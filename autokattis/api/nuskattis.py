import io
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from bs4 import BeautifulSoup as bs

from . import ABCKattis
from .enums import (
    ProblemMetadataField, ProblemStatisticsColumn, SolvedProblemsColumn, SubmissionsColumn
)
from .utils import (
    get_last_path, get_table_headers, get_table_rows, guess_id, list_to_tuple,
    remove_brackets, replace_double_dash, truncate_spaces
)

class NUSKattis(ABCKattis):
    def __init__(self, username, password=None):
        '''
        A local NUS Kattis session.
        Takes in a user (email or username).

        If the password is not given, you will be prompted for one.
        '''

        super().__init__('https://nus.kattis.com', username, password)

    @lru_cache
    def problems(self, show_solved=True):
        '''
        Gets the list of NUS Kattis problems.

        Set show_solved to True if you want to show only the problems you have solved.
        Otherwise, it will display all existing problems in NUS Kattis.

        Example:
        [
            {
                "name": "Stopwatch",
                "id": "stopwatch",
                "link": "https://nus.kattis.com/problems/stopwatch"
            },
            {
                "name": "String Multimatching",
                "id": "stringmultimatching",
                "link": "https://nus.kattis.com/problems/stringmultimatching"
            },
            {
                "name": "Beautiful Subarrays",
                "id": "subarrays",
                "link": "https://nus.kattis.com/problems/subarrays"
            }
        ]
        '''

        has_content, data = True, []
        pid_set = set()

        if show_solved:
            params = {
                'page': 0,
                'tab': 'submissions',
                'status': 'AC'
            }
            with ThreadPoolExecutor(max_workers=self.get_max_workers()) as executor:
                futures = []
                while has_content:
                    has_content = False
                    futures.clear()
                    for _ in range(self.get_max_workers()):
                        futures.append(executor.submit(self.new_get, f'{self.get_base_url()}/users/{self.get_username()}', params=params.copy()))
                        params['page'] += 1
                    for f in as_completed(futures):
                        response = f.result()
                        soup = bs(response.content, features='lxml')
                        if not soup: continue

                        table = table = soup.find('div', id='submissions-tab').find('section', class_='strip strip-item-plain').find('table', class_='table2')
                        try:                    table_content = get_table_rows(table)
                        except AttributeError:  continue

                        for row in table_content:
                            columns = row.find_all('td')
                            if columns and len(columns) >= SubmissionsColumn.CONTEST_PROBLEM_NAME:
                                has_content = True
                                pid = get_last_path(columns[SubmissionsColumn.CONTEST_PROBLEM_NAME].find_all('a')[-1].get('href')) # might have two links if it belongs to a contest, so we take the latter
                                if pid not in pid_set:
                                    pid_set.add(pid)
                                    data.append({
                                        'name': get_last_path(columns[SubmissionsColumn.CONTEST_PROBLEM_NAME].text),
                                        'id': pid,
                                        'link': f"{self.get_base_url()}/problems/{pid}"
                                    })
        else:
            # we can just take from the given dropdown list
            soup = self.get_soup_response(f'{self.get_base_url()}/users/{self.get_username()}')
            for option in soup.find_all('option')[1:]:
                pid = option.get('value').strip()
                if not pid: break
                if pid not in pid_set:
                    pid_set.add(pid)
                    data.append({
                        'name': option.text.strip(),
                        'id': pid,
                        'link': f"{self.get_base_url()}/problems/{pid}"
                    })

        return self.Result(sorted(data, key=lambda x: x['id']))

    @list_to_tuple
    @lru_cache
    def problem(self, problem_ids, download_files=False, *bc_args):
        '''
        Obtain information about one or more specific problems. The problem_ids parameter can be a string of a single problem ID, or a sequence of problem IDs.

        By default, all files, including the sample test cases, will not be downloaded within the result metadata.

        Due to security issues, you can only access a problem if it is part of a current course offering or an existing past offering.
        The function also handles the scenario if it is present in multiple course offerings.

        Example:
        [
            {
                "id": "test1",
                "text": "This problem has a C++ statistic and is included in possibly more than one course offering.",
                "cpu": "1 second",
                "memory": "1024 MB",
                "author": "Jill",
                "source": "NUS Competitive Programming",
                "files": {},
                "statistics": {
                    "C++": {
                        "fastest": {
                            "ranklist": [
                                {
                                    "rank": 1,
                                    "name": "John Doe",
                                    "username": "john-doe",
                                    "runtime": 0.01,
                                    "date": "2023-12-23 01:23:45"
                                },
                                ...
                            ],
                            "description": "The 10 fastest solutions in C++"
                        },
                        "shortest": {
                            "ranklist": [
                                {
                                    "rank": 1,
                                    "name": "Jane Doe",
                                    "username": "jane-doe",
                                    "length": 457,
                                    "date": "2023-12-23 01:23:45"
                                },
                                ...
                            ],
                            "description": "The 10 shortest solutions in C++"
                        }
                    },
                    ...
                },
                "submissions": [],
                "offerings": [
                    "https://nus.kattis.com/courses/CS2040S/CS2040S_S1_AY2425/assignments/abcdef/problems/test1",
                    ...
                ]
            },
            {
                "id": "test2",
                "text": "This problem has a file attachment and a submission by us.",
                "cpu": "1 second",
                "memory": "1024 MB",
                "author": "Jack",
                "source": "NUS CS2040",
                "files": {
                    "longwait.zip": {"sample1.in": "1 2", "sample1.ans": "100\n200"}
                },
                "statistics": {
                    ...
                },
                "submissions": [
                    {
                        "status": "Accepted (100)",
                        "runtime": "1.60 s",
                        "language": "Java",
                        "test_case_passed": 14,
                        "test_case_full": 14,
                        "link": "https://nus.kattis.com/courses/CS2040/CS2040_S1_AY2627/assignments/abcdef/submissions/999999"
                    }
                ],
                "offerings": [
                    "https://nus.kattis.com/courses/CS2040/CS2040_S1_AY2627/assignments/abcdef/problems/test2"
                ]
            }
        ]
        '''

        ret = []
        if type(problem_ids) == str: problem_ids = [problem_ids]

        for problem_id in {*problem_ids}:
            original_url = f'{self.get_base_url()}/problems/{problem_id}'
            response = self.new_get(original_url)

            if not response.ok: print(f'[problem] Ignoring {problem_id}'); continue

            soup = bs(response.content, features='lxml')
            if response.url == original_url:
                dest_urls = []
                table = soup.find('table', class_='table2')
                for row in get_table_rows(table):
                    columns = row.find_all('td')
                    for column in columns:
                        if column.find('a'): dest_urls.append(f"{self.get_base_url()}{column.find('a').get('href')}")
                soup = self.get_soup_response(dest_urls[0])
            else:
                dest_urls = [response.url]

            body = soup.find('div', class_='problembody')
            data = {'id': problem_id, 'text': body.text.strip()}

            cpu = memory = author = source = ''
            files = {}
            for div in soup.find_all('div', class_='metadata-grid'):
                for d in div.find_all('div', class_='card'):
                    div_text = [s.text.strip() for s in d.find_all('span') if s.text.strip()]
                    if div_text[0] == ProblemMetadataField.CPU_TIME_LIMIT:
                        cpu = div_text[-1].strip()
                    elif div_text[0] == ProblemMetadataField.MEMORY_LIMIT:
                        memory = div_text[-1].strip()
                    elif div_text[0] == ProblemMetadataField.SOURCE_LICENSE:
                        _, author, source, *_ = [s.text for s in d.find_all('span') if not s.find('span')]
                    elif div_text[0] == ProblemMetadataField.ATTACHMENTS or div_text[0] == ProblemMetadataField.DOWNLOADS:
                        for url, fn in [(f"{self.get_base_url()}{a.get('href')}", a.get('download') or get_last_path(a.get('href'))) for a in d.find_all('a')]:
                            if not download_files: continue
                            if url.endswith('zip'):
                                with zipfile.ZipFile(io.BytesIO(self.new_get(url).content)) as z:
                                    files[fn] = {}
                                    for inner_fn in z.namelist():
                                        with z.open(inner_fn) as inner_file: files[fn][inner_fn] = inner_file.read().decode("utf-8")
                            else:
                                files[fn] = self.new_get(url).text
            data = {
                **data,
                'cpu': cpu,
                'memory': memory,
                'author': author,
                'source': source,
                'files': files
            }

            # statistics
            # if there are multiple offerings, just take the first one because they share the same leaderboard
            data['statistics'] = {}
            soup = self.get_soup_response(f'{dest_urls[0]}/statistics')
            category_map = {option.get('value')[1:]:[option.text, option.get('data-title')] for option in soup.find_all('option')}
            for section in soup.find_all('section', class_='strip strip-item-plain'):
                table = section.find('table')
                section_id = section.get('id')
                language, description = category_map[section_id]
                data['statistics'][language] = data['statistics'].get(language, {})
                data['statistics'][language][['fastest', 'shortest']['shortest' in section_id]] = {}
                stats = data['statistics'][language][['fastest', 'shortest']['shortest' in section_id]]
                if table:
                    stats['ranklist'] = []
                    for row in get_table_rows(table):
                        columns = row.find_all('td')
                        username_a = columns[ProblemStatisticsColumn.NAME].find('a')
                        stats['ranklist'].append({
                            'rank': int(columns[ProblemStatisticsColumn.RANK].text),
                            'name': columns[ProblemStatisticsColumn.NAME].text,
                            'username': get_last_path(username_a.get('href')) if username_a else None,
                            ['runtime', 'length']['shortest' in section_id]: [float, int]['shortest' in section_id](columns[ProblemStatisticsColumn.RUNTIME_OR_LENGTH].text.split()[0]),
                            'date': columns[ProblemStatisticsColumn.DATE].text
                        })
                stats['description'] = description

            # my submissions
            data['submissions'] = []
            for dest_url in dest_urls:
                soup = self.get_soup_response(f'{dest_url}?tab=submissions')
                table = soup.find('table', id='submissions')
                if table:
                    for row in get_table_rows(table):
                        columns = row.find_all('td')
                        columns_text = [column.text.strip() for column in columns if column.text.strip()]
                        if columns_text:
                            try:
                                status, runtime, language, tc, *_ = columns_text
                                runtime = ' '.join(runtime.split())
                                test_case_passed, test_case_full = map(int, tc.split('/'))
                            except:
                                status, language, *_ = columns_text
                                runtime = test_case_passed = test_case_full = None
                            data['submissions'].append({
                                'status': status,
                                'runtime': runtime,
                                'language': language,
                                'test_case_passed': test_case_passed,
                                'test_case_full': test_case_full,
                                'link': f"{self.get_base_url()}{columns[-1].find('a').get('href')}"
                            })

            # wrap-up
            data['offerings'] = dest_urls
            ret.append(data)

        return self.Result(ret)

    @list_to_tuple
    @lru_cache
    def stats(self, languages=None, *bc_args):
        '''
        Collects the statistics of your accepted (AC) submissions based on the programming language(s) used. The languages parameter can be a string of a single language, or a sequence of languages.
        
        If there are multiple AC submissions of the same language, only the best (highest score then fastest) is considered.

        By default, all languages are included within the result. Note that the list of language(s) must be a subset of the available languages.

        Example:
        [
            {
                "id": "hello",
                "name": "Hello World!",
                "timestamp": "2021-01-01 00:00:01",
                "runtime": "0.11",
                "language": "Kotlin",
                "test_case_passed": 1,
                "test_case_full": 1,
                "link": "https://nus.kattis.com/submissions/123456"
            },
            {
                "id": "otherside",
                "name": "Other Side",
                "timestamp": "2021-01-02 00:00:02",
                "runtime": "0.12",
                "language": "Kotlin",
                "test_case_passed": 42,
                "test_case_full": 42,
                "link": "https://nus.kattis.com/submissions/234567"
            }
        ]
        '''
        if languages == None: return self.stats(languages='')

        ret = []
        if type(languages) == str: languages = [languages]

        for language in {*languages}:
            if language and language not in self.get_database().get_languages(): print(f'[stats] Cannot find {language}, language specified must be one of {sorted(self.get_database().get_languages())}'); continue

            has_content = True
            params = {
                'page': 0,
                'status': 'AC',
                'language': self.get_database().get_languages().get(language)
            }
            data = {}
            with ThreadPoolExecutor(max_workers=self.get_max_workers()) as executor:
                futures = []
                while has_content:
                    has_content = False
                    futures.clear()
                    for _ in range(self.get_max_workers()):
                        futures.append(executor.submit(self.new_get, f'{self.get_base_url()}/users/{self.get_username()}', params=params.copy()))
                        params['page'] += 1
                    for f in as_completed(futures):
                        response = f.result()
                        soup = bs(response.content, features='lxml')
                        table = soup.find('table', class_='table2 report_grid-problems_table double-rows')
                        for row in get_table_rows(table):
                            columns = row.find_all('td')
                            if [column.text.strip() for column in columns if column.text.strip()]:
                                has_content = True
                                pid = get_last_path(columns[SubmissionsColumn.CONTEST_PROBLEM_NAME].find_all('a')[-1].get('href')) # might have two links if it belongs to a contest
                                tc_pass, tc_full = map(int, columns[SubmissionsColumn.TESTCASES].text.split('/'))

                                # not converting runtime to float because some TLE solutions (with '>') can also be AC
                                new_data = {
                                    'name': get_last_path(columns[SubmissionsColumn.CONTEST_PROBLEM_NAME].text),
                                    'timestamp': columns[SubmissionsColumn.SUBMISSION_TIME].text.strip(),
                                    'runtime': ' '.join(columns[SubmissionsColumn.CPU_RUNTIME].text.split()[:-1]),
                                    'language': columns[SubmissionsColumn.PROGRAMMING_LANGUAGE].text.strip(),
                                    'test_case_passed': tc_pass,
                                    'test_case_full': tc_full,
                                    'link': f"{self.get_base_url()}/submissions/{get_last_path(columns[SubmissionsColumn.VIEW_DETAILS].find('a').get('href'))}"
                                }

                                pts_regex = re.findall(r'[\d\.]+', columns[SubmissionsColumn.STATUS].text)
                                if pts_regex: new_data['score'] = float(pts_regex[0])
                                data[pid] = new_data if pid not in data else max(
                                    data[pid], new_data,
                                    key=lambda x: (x.get('score', tc_pass/tc_full), x['test_case_passed'], -float(x['runtime'] if '>' not in x['runtime'] else 1e9))
                                )

            # wrap-up
            ret.extend({'id': k, **v} for k, v in data.items())

        return self.Result(sorted(ret, key=lambda x: x['id']))

    @lru_cache
    def courses(self):
        '''
        Lists down only the current courses offered and the courses with recently ended offerings in NUS Kattis.
        It does not list all existing courses in NUS Kattis.

        Example:
        [
            {
                "name": "Data Structures and Algorithms (Java) - CS2040",
                "url": "https://nus.kattis.com/courses/CS2040",
                "course_id": "CS2040"
            },
            {
                "name": "Competitive Programming - CS3233",
                "url": "https://nus.kattis.com/courses/CS3233",
                "course_id": "CS3233"
            }
        ]
        '''

        tables = self.get_homepage().find_all('table', class_='table2')
        if not tables: return self.Result([])
        data = []
        for table in tables:
            for row in table.find_all('tr'):
                columns = row.find_all('td')
                columns_text = [truncate_spaces(column.text.strip()) for column in columns]
                columns_url = [column.find('a') for column in columns]
                if columns_text:
                    href = columns_url[0].get('href')
                    data.append({
                        'name': columns_text[0],
                        'url': self.get_base_url() + href,
                        'course_id': get_last_path(href)
                    })
        return self.Result(sorted(data, key=lambda r: r['course_id']))

    @lru_cache
    def offerings(self, course_id):
        '''
        Lists down all offerings within a specific NUS Kattis course.

        Example:
        [
            {
                "name": "CS2040_S1_AY2425",
                "status": "teaching",
                "end_date": "2024-12-08",
                "link": "https://nus.kattis.com/courses/CS2040/CS2040_S1_AY2425"
            },
            {
                "name": "CS2040_S2_AY2324",
                "status": "registered",
                "end_date": "2024-05-06",
                "link": "https://nus.kattis.com/courses/CS2040/CS2040_S2_AY2324"
            },
            {
                "name": "CS2040_S2_AY2425",
                "status": "N/A",
                "end_date": "2025-05-03",
                "link": "https://nus.kattis.com/courses/CS2040/CS2040_S2_AY2425"
            }
        ]
        '''

        soup = self.get_soup_response(f'{self.get_base_url()}/courses/{course_id}')
        table = soup.find('table', class_='table2')
        if not table: return self.Result([])
        data = []
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            try:
                name, end_date = [truncate_spaces(column.text.strip()) for column in columns]
                link, _ = [column.find('a') for column in columns]
                name_split = name.split('\n')
                data.append({
                    'name': name_split[0], # special example: CS2040_S2_AY2324\n \n\n \xa0(teaching)
                    'status': 'N/A' if len(name_split) == 1 else name_split[-1][name_split[-1].find('(')+1:name_split[-1].find(')')],
                    'end_date': end_date.split()[1][:-1],
                    'link': self.get_base_url() + link.get('href')
                })
            except:
                pass # ignore for now
        return self.Result(sorted(data, key=lambda r: r['end_date'], reverse=True))

    @lru_cache
    def assignments(self, offering_id, course_id=None):
        '''
        Lists down all assignments within a specific NUS Kattis course offering.
        Problem IDs within a specific assignment are comma-separated, e.g. pid1,pid2,pid3

        Example:
        [
            {
                "id": "abcdef",
                "name": "Assignment 1",
                "status": "Ended",
                "link": "https://nus.kattis.com/courses/CS2040/CS2040_S1_AY2425/assignments/ghijkl",
                "problems": "magicsequence,zbrka,2048"
            },
            {
                "id": "opqrst",
                "name": "Assignment 2",
                "status": "Remaining: 7 days 12:34:56",
                "link": "https://nus.kattis.com/courses/CS2040/CS2040_S1_AY2425/assignments/uvwxyz",
                "problems": "dragonmaid,mnist2class,autori,pot,hello,zbrka,2048"
            }
        ]
        '''

        if course_id == None:
            # try to guess
            for cid in self.courses().to_df().course_id:
                if offering_id in [*self.offerings(cid).to_df().name]: course_id = cid; break
            if course_id == None:
                print('[assignments] Cannot guess course ID automatically, please provide one', flush=True)
                return self.Result([])
            print('[assignments] Guessed course ID:', course_id, flush=True)

        soup = self.get_soup_response(f'{self.get_base_url()}/courses/{course_id}/{offering_id}')
        data = []
        for div in soup.find_all('div', {'class': 'strip-row w-auto'}):
            h2 = div.find('h2')
            if h2 != None and h2.text.strip() == 'Assignments':
                toggle = False
                for asg in div.find_all('li'):
                    if asg.find('span') == None:
                        if toggle:
                            data.append({
                                'id': aid,
                                'name': name,
                                'status': status,
                                'link': link,
                                'problems': ','.join(pids)
                            })
                        name, status = truncate_spaces(asg.text.strip()).split('\n')
                        status = remove_brackets(status)
                        link = self.get_base_url() + asg.find('a').get('href')
                        aid = get_last_path(link)
                        pids = []
                        toggle = True
                    else:
                        pids.append(get_last_path(asg.find('a').get('href')))
                if toggle:
                    data.append({
                        'id': aid,
                        'name': name,
                        'status': status,
                        'link': link,
                        'problems': ','.join(pids)
                    })
        return self.Result(data)
