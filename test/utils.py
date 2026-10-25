import math
import time
import traceback
import warnings
from functools import wraps

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TEST_NAMES = set()
FAILURES = []
TEST_RESULTS = {}

def assert_records(records, required_fields, nonempty_fields=()):
    assert records, 'Expected at least one record; the result was empty'

    for index, record in enumerate(records):
        assert isinstance(record, dict), f'Record {index} must be a dictionary, got {type(record).__name__}'
        missing = set(required_fields) - record.keys()
        assert not missing, f'Record {index} is missing required fields: {sorted(missing)}'

        for field in nonempty_fields:
            value = record[field]
            assert value is not None and value != '' and value != [] and value != {}, (
                f'Record {index} must have a non-empty {field!r}; got {value!r}'
            )

def check_records(required_fields, nonempty_fields=()):
    return lambda records: assert_records(
        records=records,
        required_fields=required_fields,
        nonempty_fields=nonempty_fields,
    )

def assert_rank_value(rank):
    assert rank is None or (type(rank) is int and rank > 0), (
        f'Rank must be None for a hidden profile or a positive integer; got {rank!r}'
    )

def assert_rank_records(records, required_fields, nonempty_fields=()):
    assert_records(
        records=records,
        required_fields=required_fields,
        nonempty_fields=nonempty_fields,
    )
    for record in records:
        assert_rank_value(rank=record['rank'])

def check_rank_records(required_fields, nonempty_fields=()):
    return lambda records: assert_rank_records(
        records=records,
        required_fields=required_fields,
        nonempty_fields=nonempty_fields,
    )

def assert_problem_details(
    records,
    expected_ids,
    additional_fields=(),
    expected_names=None,
    require_files=False,
    required_file_ids=(),
):
    required_fields = (
        'id',
        'text',
        'files',
        'statistics',
        'submissions',
        *additional_fields,
    )
    assert_records(
        records=records,
        required_fields=required_fields,
        nonempty_fields=('id', 'text'),
    )
    actual_ids = [record['id'] for record in records]
    expected_ids = sorted(set(expected_ids))
    assert actual_ids == expected_ids, (
        f'Problem ID mismatch: missing={sorted(set(expected_ids) - set(actual_ids))}, '
        f'unexpected={sorted(set(actual_ids) - set(expected_ids))}, '
        f'expected_order={expected_ids}, actual_order={actual_ids}'
    )

    for record in records:
        assert isinstance(record['text'], str), f"Problem {record['id']!r} text must be a string"
        assert isinstance(record['files'], dict), f"Problem {record['id']!r} files must be a dictionary"
        if require_files or record['id'] in required_file_ids:
            assert record['files'], f"Problem {record['id']!r} was expected to have downloaded attachments, but files is empty"
        assert isinstance(record['statistics'], dict), f"Problem {record['id']!r} statistics must be a dictionary"
        assert isinstance(record['submissions'], list), f"Problem {record['id']!r} submissions must be a list"

        if expected_names is not None:
            assert record.get('name') == expected_names[record['id']], (
                f"Problem {record['id']!r} name mismatch: expected {expected_names[record['id']]!r}, got {record.get('name')!r}"
            )
        if 'name' in record:
            assert isinstance(record['name'], str) and record['name'], f"Problem {record['id']!r} name must be a non-empty string"

        for field in ('cpu', 'memory', 'author', 'source', 'category'):
            if field in record:
                assert isinstance(record[field], str), f'{field} must be a string'

        if 'difficulty' in record:
            assert record['difficulty'] is None or (
                type(record['difficulty']) is float
                and math.isfinite(record['difficulty'])
            ), f"Problem {record['id']!r} difficulty must be None or a finite float; got {record['difficulty']!r}"

        if 'breakpoints' in record:
            assert isinstance(record['breakpoints'], list), f"Problem {record['id']!r} breakpoints must be a list"
            for breakpoint in record['breakpoints']:
                assert set(breakpoint) == {
                    'breakpoint',
                    'difficulty',
                    'tooltip_text',
                    'difficulty_category',
                }, f"Problem {record['id']!r} breakpoint has unexpected fields: {sorted(breakpoint)}"
                assert type(breakpoint['breakpoint']) is float, f"Breakpoint value must be a float; got {breakpoint['breakpoint']!r}"
                assert math.isfinite(breakpoint['breakpoint']) and breakpoint['breakpoint'] >= 0, f"Breakpoint value must be finite and non-negative; got {breakpoint['breakpoint']!r}"
                assert type(breakpoint['difficulty']) in (int, float), f"Breakpoint difficulty must be numeric; got {breakpoint['difficulty']!r}"
                assert math.isfinite(breakpoint['difficulty']), f"Breakpoint difficulty must be finite; got {breakpoint['difficulty']!r}"
                assert isinstance(breakpoint['tooltip_text'], str), f"Breakpoint tooltip_text must be a string; got {type(breakpoint['tooltip_text']).__name__}"
                assert breakpoint['tooltip_text'], 'Breakpoint tooltip_text must not be empty'
                assert isinstance(breakpoint['difficulty_category'], str), f"Breakpoint difficulty_category must be a string; got {type(breakpoint['difficulty_category']).__name__}"
                assert breakpoint['difficulty_category'], 'Breakpoint difficulty_category must not be empty'

        for field in additional_fields:
            if field == 'offerings':
                assert isinstance(record[field], list), f"Problem {record['id']!r} offerings must be a list"
                assert record[field], f"Problem {record['id']!r} must have at least one offering URL"
                assert all(
                    isinstance(offer, str) and offer.startswith('https://')
                    for offer in record[field]
                ), f"Problem {record['id']!r} offerings must all be HTTPS URLs; got {record[field]!r}"

        for language, statistics in record['statistics'].items():
            assert isinstance(language, str) and language, f"Problem {record['id']!r} statistics language key must be a non-empty string; got {language!r}"
            assert isinstance(statistics, dict), f"Problem {record['id']!r} statistics for {language!r} must be a dictionary"
            assert set(statistics) <= {'fastest', 'shortest', 'score'}, (
                f"Problem {record['id']!r} statistics for {language!r} have unsupported metric keys: "
                f'{sorted(statistics)}'
            )

            for kind, details in statistics.items():
                assert kind in ('fastest', 'shortest', 'score'), f"Problem {record['id']!r} has unsupported statistics kind {kind!r}"
                assert isinstance(details, dict), f"Problem {record['id']!r} {kind} statistics for {language!r} must be a dictionary"
                assert set(details) <= {'description', 'ranklist'}, f"Problem {record['id']!r} {kind} statistics have unsupported fields: {sorted(details)}"
                assert isinstance(details.get('description'), str), f"Problem {record['id']!r} {kind} statistics description must be a string"
                assert details['description'], f"Problem {record['id']!r} {kind} statistics description must not be empty"
                if 'ranklist' not in details:
                    continue
                assert isinstance(details['ranklist'], list), f"Problem {record['id']!r} {kind} statistics ranklist must be a list when present"

                metric = {
                    'fastest': 'runtime',
                    'shortest': 'length',
                    'score': 'score',
                }[kind]
                for entry in details['ranklist']:
                    assert set(entry) == {'rank', 'name', 'username', metric, 'date'}, f"Problem {record['id']!r} {language!r} {kind} entry must contain rank/name/username/{metric}/date; got {sorted(entry)}"
                    assert_rank_value(rank=entry['rank'])
                    assert isinstance(entry['name'], str) and entry['name'].strip(), f"Problem {record['id']!r} {language!r} {kind} entry name must be a non-empty string; got {entry['name']!r}"
                    assert entry['name'] == entry['name'].strip(), (
                        f"Problem {record['id']!r} {language!r} {kind} entry name must be trimmed; "
                        f'{entry["name"]!r}'
                    )
                    assert entry['username'] is None or isinstance(
                        entry['username'], str
                    ), f"Problem {record['id']!r} {language!r} {kind} username must be None or a string; got {entry['username']!r}"
                    assert isinstance(entry['date'], str) and entry['date'], f"Problem {record['id']!r} {language!r} {kind} entry date must be a non-empty string; got {entry['date']!r}"

                    value = entry[metric]
                    if kind in ('fastest', 'score'):
                        assert type(value) is float, f"Problem {record['id']!r} {language!r} {kind} {metric} must be a float; got {value!r}"
                        assert math.isfinite(value) and value >= 0, f"Problem {record['id']!r} {language!r} {kind} {metric} must be finite and non-negative; got {value!r}"
                    else:
                        assert type(value) is int and value > 0, f"Problem {record['id']!r} {language!r} {kind} {metric} must be a positive integer; got {value!r}"

        if record['submissions']:
            for submission in record['submissions']:
                assert set(submission) == {
                    'status',
                    'runtime',
                    'language',
                    'test_case_passed',
                    'test_case_full',
                    'link',
                }, f"Problem {record['id']!r} submission has unexpected fields: {sorted(submission)}"
                assert isinstance(submission['status'], str), f"Problem {record['id']!r} submission status must be a string"
                assert submission['status'], f"Problem {record['id']!r} submission status must not be empty"
                assert submission['runtime'] is None or isinstance(
                    submission['runtime'], str
                ), f"Problem {record['id']!r} submission runtime must be None or a string; got {submission['runtime']!r}"
                assert isinstance(submission['language'], str), f"Problem {record['id']!r} submission language must be a string"
                assert submission['language'], f"Problem {record['id']!r} submission language must not be empty"
                assert submission['link'].startswith('https://'), f"Problem {record['id']!r} submission link must be an HTTPS URL; got {submission['link']!r}"

                passed = submission['test_case_passed']
                full = submission['test_case_full']
                assert passed is None or type(passed) is int, f"Problem {record['id']!r} submission test_case_passed must be None or an integer; got {passed!r}"
                assert full is None or type(full) is int, f"Problem {record['id']!r} submission test_case_full must be None or an integer; got {full!r}"
                assert (passed is None) == (full is None), f"Problem {record['id']!r} submission test case counts must either both be present or both be None; got passed={passed!r}, full={full!r}"
                if passed is not None:
                    assert 0 <= passed <= full, f"Problem {record['id']!r} submission passed test cases must be between 0 and the full count; got passed={passed}, full={full}"

        assert record['statistics'], f"Problem {record['id']!r} must include statistics; got an empty mapping"
        for filename, contents in record['files'].items():
            assert isinstance(filename, str) and filename, f"Problem {record['id']!r} attachment filename must be a non-empty string; got {filename!r}"
            assert isinstance(contents, (str, dict)), f"Problem {record['id']!r} attachment {filename!r} content must be a string or dictionary; got {type(contents).__name__}"
            if isinstance(contents, dict):
                assert contents, f"Problem {record['id']!r} attachment {filename!r} must contain at least one file"
                assert all(
                    isinstance(path, str) and isinstance(text, str)
                    for path, text in contents.items()
                ), f"Problem {record['id']!r} attachment {filename!r} entries must map string paths to string contents"
            else:
                assert contents, f"Problem {record['id']!r} attachment {filename!r} content must not be empty"

def check_problem_details(
    expected_ids,
    additional_fields=(),
    expected_names=None,
    required_file_ids=(),
):
    return lambda records: assert_problem_details(
        records=records,
        expected_ids=expected_ids,
        additional_fields=additional_fields,
        expected_names=expected_names,
        required_file_ids=required_file_ids,
    )

def assert_empty(records):
    assert records == [], f'Expected no records for this invalid or unavailable lookup, got {records!r}'

def assert_problem_name(records, problem_id, expected_name):
    matches = [record for record in records if record.get('id') == problem_id]
    assert len(matches) == 1, f'Expected exactly one listing for problem {problem_id!r}, found {len(matches)}'
    assert matches[0].get('name') == expected_name, (
        f"Problem {problem_id!r} listing name mismatch: expected {expected_name!r}, got {matches[0].get('name')!r}"
    )

def assert_equal(actual, expected, description):
    assert actual is not None and expected is not None, (
        f'{description}: cannot compare results because at least one test returned None after failing'
    )
    assert actual == expected, f'{description}: results differ; actual={actual!r}, expected={expected!r}'
    return actual

def _record_failure(title, error, caught_warnings):
    FAILURES.append({
        'title': title,
        'error': error,
        'traceback': traceback.extract_tb(error.__traceback__),
        'warnings': [
            f'{warning.filename}:{warning.lineno}: '
            f'{warning.category.__name__}: {warning.message}'
            for warning in caught_warnings
        ],
    })

def report_failures():
    if not FAILURES:
        print('All tests passed.')
        return

    print(f'\n{len(FAILURES)} test(s) failed:')
    for failure in FAILURES:
        error = failure['error']
        print(f"\n[{bcolors.FAIL}{failure['title']}{bcolors.ENDC}] {type(error).__name__}: {error}")
        for frame in failure['traceback']:
            print(f'  {frame.filename}:{frame.lineno} in {frame.name}')
            if frame.line:
                print(f'    {frame.line.strip()}')
        if failure['warnings']:
            print('  Warnings:')
            for warning in failure['warnings']:
                print(f'    {warning}')
    raise SystemExit(1)

def test_case(check=None, csv=True):
    def decorate(fn):
        @wraps(fn)
        def run():
            result = test(fn=fn, csv=csv, check=check)
            TEST_RESULTS[fn.__name__] = result
            return result
        return run
    return decorate

def test(fn, csv=True, check=None):
    title = fn.__name__[5:] if fn.__name__.startswith('test_') else fn.__name__
    assert title not in TEST_NAMES, f'Test title {title!r} is duplicated; each registered test must have a unique title'
    TEST_NAMES.add(title)

    print(f'[{bcolors.OKBLUE}RUN{bcolors.ENDC}] {fn.__qualname__}')
    start = time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter('always')
            ret = fn()
            if check:
                check(records=ret)
            if ret is not None:
                df = ret.to_df()
                formatters = {
                    'text': lambda value: value if len(value) <= 20 else f'{value[:17]}...',
                    'files': lambda value: value if len(value:=str(value)) <= 20 else f'{value[:17]}...',
                    'statistics': lambda value: value if len(value:=str(value)) <= 30 else f'{value[:27]}...',
                    'submissions': lambda value: value if len(value:=str(value)) <= 30 else f'{value[:27]}...',
                    'problems': lambda value: value if len(value:=str(value)) <= 50 else f'{value[:47]}...',
                }
                print(df.to_string(max_rows=10, max_colwidth=200, line_width=200, formatters=formatters))
                if csv:
                    df.to_csv(f'{title}.csv', index=False)
        print(f'Time taken: {round(time.perf_counter() - start, 4)}s')
        print(f'[{bcolors.OKGREEN}OK{bcolors.ENDC}] {fn.__qualname__}')
        return ret
    except Exception as error:
        _record_failure(
            title=title,
            error=error,
            caught_warnings=caught_warnings,
        )
        print(f'{type(error).__name__}: {error}')
        print(f'Time taken: {round(time.perf_counter() - start, 4)}s')
        print(f'[{bcolors.FAIL}FAIL{bcolors.ENDC}] {fn.__qualname__}')
        return None
