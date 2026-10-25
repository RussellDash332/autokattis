from autokattis import NUSKattis
from env import PASSWORD, USER
from utils import (
    assert_empty,
    check_problem_details,
    check_records,
    report_failures,
    test_case,
)

kt = NUSKattis(USER, PASSWORD)

check_problem_listing = check_records(
    required_fields=('id', 'name', 'link'),
    nonempty_fields=('id', 'name', 'link'),
)

def check_single_problem(problem_id):
    def check(records):
        if records:
            check_nus_problem_records(records=records, expected_ids=[problem_id])
            assert [record['id'] for record in records] == [problem_id], (
                f'Expected problem result for {problem_id!r}, got {[record["id"] for record in records]!r}'
            )
    return check

def check_empty_problem_data(record):
    required_fields = ('id', 'name', 'text', 'cpu', 'memory', 'author', 'source', 'files', 'statistics', 'submissions', 'offerings')
    check_records(required_fields=required_fields, nonempty_fields=('id',))(records=[record])
    assert record['text'] == '', f"Unavailable problem {record['id']!r} text must be empty"
    for field in ('cpu', 'memory', 'author', 'source'):
        assert record[field] == '', f"Unavailable problem {record['id']!r} {field} must be empty"
    assert record['files'] == {}, f"Unavailable problem {record['id']!r} files must be empty"
    assert record['statistics'] == {}, f"Unavailable problem {record['id']!r} statistics must be empty"
    assert record['submissions'] == [], f"Unavailable problem {record['id']!r} submissions must be empty"
    assert isinstance(record['offerings'], list), f"Unavailable problem {record['id']!r} offerings must be a list"
    assert all(isinstance(offer, str) and offer.startswith('https://') for offer in record['offerings']), f"Unavailable problem {record['id']!r} offerings must contain HTTPS URLs"

def check_nus_problem_records(records, expected_ids):
    returned_ids = [record['id'] for record in records]
    assert len(returned_ids) == len(set(returned_ids)), 'Problem result contains duplicate IDs'
    assert set(returned_ids) <= set(expected_ids), f'Unexpected problem IDs: {sorted(set(returned_ids) - set(expected_ids))}'
    empty_data_records = [record for record in records if record.get('text') == '']
    for record in empty_data_records:
        check_empty_problem_data(record=record)
    available_records = [record for record in records if record.get('text') != '']
    if available_records:
        check_problem_details(
            expected_ids=[record['id'] for record in available_records],
            additional_fields=('offerings',),
        )(records=available_records)

def check_all_problems(records):
    check_problem_listing(records=records)

def check_multiple_problems(expected_ids):
    def check(records):
        check_nus_problem_records(records=records, expected_ids=expected_ids)
    return check

check_courses = check_records(
    required_fields=('name', 'url', 'course_id'),
    nonempty_fields=('name', 'url', 'course_id'),
)
check_offerings = check_records(
    required_fields=('name', 'status', 'end_date', 'link'),
    nonempty_fields=('name', 'status', 'end_date', 'link'),
)

assignment_fields = ('id', 'name', 'status', 'link', 'problems')
assignment_nonempty = ('id', 'name', 'link')
check_assignments = check_records(
    required_fields=assignment_fields,
    nonempty_fields=assignment_nonempty,
)

stats_fields = ('id', 'name', 'language', 'link')
check_stats = check_records(
    required_fields=stats_fields,
    nonempty_fields=stats_fields,
)

@test_case(check=check_problem_listing)
def test_nus_01_problems_solved():
    return kt.problems()

@test_case(check=check_all_problems)
def test_nus_02_problems_all():
    return kt.problems(show_solved=False)

@test_case(check=check_single_problem(problem_id='magicsequence'))
def test_nus_03_problem_single_1_nodownload():
    return kt.problem(problem_ids='magicsequence')

@test_case(check=check_single_problem(problem_id='magicsequence'))
def test_nus_04_problem_single_1_download():
    return kt.problem(problem_ids='magicsequence', download_files=True)

@test_case(check=check_single_problem(problem_id='racinggame'))
def test_nus_05_problem_single_2_nodownload():
    return kt.problem(problem_ids='racinggame')

@test_case(check=check_single_problem(problem_id='racinggame'))
def test_nus_06_problem_single_2_download():
    return kt.problem(problem_ids='racinggame', download_files=True)

@test_case(check=check_single_problem(problem_id='hwei'))
def test_nus_07_problem_single_3_nodownload():
    return kt.problem(problem_ids='hwei')

@test_case(check=check_single_problem(problem_id='hwei'))
def test_nus_08_problem_single_3_download():
    return kt.problem(problem_ids='hwei', download_files=True)

@test_case(check=check_multiple_problems(expected_ids=('magicsequence', 'racinggame', 'hwei', 'amazing', 'bots')))
def test_nus_09_problem_multiple_nodownload():
    return kt.problem(problem_ids=['magicsequence', 'racinggame', 'hwei', 'amazing', 'bots'])

@test_case(check=check_multiple_problems(expected_ids=('magicsequence', 'racinggame', 'hwei', 'amazing', 'bots')))
def test_nus_10_problem_multiple_download():
    return kt.problem(problem_ids={'magicsequence', 'racinggame', 'hwei', 'amazing', 'bots'}, download_files=True)

@test_case(check=assert_empty)
def test_nus_11_problem_invalid():
    return kt.problem(problem_ids=('@?@?',))

@test_case(check=check_courses)
def test_nus_12_courses():
    return kt.courses()

@test_case(check=check_offerings)
def test_nus_13_offerings_valid_1():
    return kt.offerings(course_id='CS2040')

@test_case(check=check_offerings)
def test_nus_14_offerings_valid_2():
    return kt.offerings(course_id='CS3233')

@test_case(check=assert_empty)
def test_nus_15_offerings_invalid():
    return kt.offerings(course_id='idk')

@test_case(check=check_assignments)
def test_nus_16_assignments_courseid_guessed_1():
    return kt.assignments(offering_id='CS2040_S1_AY2425')

@test_case(check=check_assignments)
def test_nus_17_assignments_courseid_guessed_2():
    return kt.assignments(offering_id='CS3233_S2_AY2425')

@test_case(check=check_assignments)
def test_nus_18_assignments_courseid_given():
    return kt.assignments(offering_id='CS3233_S2_AY2223', course_id='CS3233')

@test_case(check=assert_empty)
def test_nus_19_assignments_unknown_courseid():
    return kt.assignments(offering_id='xyz')

@test_case(check=assert_empty)
def test_nus_20_assignments_unknown_offeringid():
    return kt.assignments(offering_id='xyz', course_id='CS3233')

@test_case(check=check_stats)
def test_nus_21_stats_single():
    return kt.stats(languages='C++')

@test_case(check=check_stats)
def test_nus_22_stats_multiple():
    return kt.stats(languages=['C++', 'Python 3'])

@test_case(check=assert_empty)
def test_nus_23_stats_invalid():
    return kt.stats(languages=('@?@?', 'ABC'))

@test_case(check=check_stats)
def test_nus_24_stats_all():
    return kt.stats()

tests = [
    test_nus_01_problems_solved,
    test_nus_02_problems_all,
    test_nus_03_problem_single_1_nodownload,
    test_nus_04_problem_single_1_download,
    test_nus_05_problem_single_2_nodownload,
    test_nus_06_problem_single_2_download,
    test_nus_07_problem_single_3_nodownload,
    test_nus_08_problem_single_3_download,
    test_nus_09_problem_multiple_nodownload,
    test_nus_10_problem_multiple_download,
    test_nus_11_problem_invalid,
    test_nus_12_courses,
    test_nus_13_offerings_valid_1,
    test_nus_14_offerings_valid_2,
    test_nus_15_offerings_invalid,
    test_nus_16_assignments_courseid_guessed_1,
    test_nus_17_assignments_courseid_guessed_2,
    test_nus_18_assignments_courseid_given,
    test_nus_19_assignments_unknown_courseid,
    test_nus_20_assignments_unknown_offeringid,
    test_nus_21_stats_single,
    test_nus_22_stats_multiple,
    test_nus_23_stats_invalid,
    test_nus_24_stats_all
]

for test_function in tests:
    test_function()

report_failures()
