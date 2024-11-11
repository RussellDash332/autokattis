import io
import math
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from . import ABCKattis
from .enums import (
    ChallengeRanklistColumn, CountryRanklistColumn, DefaultRanklistColumn, DifficultyColor,
    ProblemAuthorsColumn, ProblemMetadataField, ProblemSourcesColumn, ProblemStatisticsColumn,
    ProblemsColumn, RanklistField, SingleCountryRanklistColumn, SingleUniversityRanklistColumn,
    SolvedProblemsColumn, SubmissionsColumn, UniversityRanklistColumn, UserRanklistColumn
)
from .utils import (
    get_last_path, get_table_headers, get_table_rows, guess_id,
    list_to_tuple, replace_double_dash
)

class OpenKattis(ABCKattis):
    def __init__(self, username, password=None):
        '''
        A local Open Kattis session.
        Takes in a user (email or username).

        If the password is not given, you will be prompted for one.
        '''

        super().__init__('https://open.kattis.com', username, password)

    @lru_cache
    def problems(self, show_solved=True, show_partial=True, show_tried=False, show_untried=False, low_detail_mode=False):
        '''
        Gets the list of Open Kattis problems.

        Parameters:
        - low_detail_mode: True if you want only need the problem IDs and the links. Otherwise, it will contain many other details and thus will take more time. By default, this is set to False.

        The below parameters only matter if low_detail_mode is set to False:
        - show_solved: True if you want to include fully solved problems, False otherwise. By default, this is set to True.
        - show_partial: True if you want to include partially solved problems, False otherwise. By default, this is set to True.
        - show_tried: True if you want to include unsolved problems that you have attempted, False otherwise. By default, this is set to False.
        - show_untried: True if you want to include unsolved problems that you have never attempted, False otherwise. By default, this is set to False.

        Example for low detail mode:
        [
            {
                "name": "Stopwatch",
                "id": "stopwatch",
                "link": "https://open.kattis.com/problems/stopwatch"
            },
            {
                "name": "String Multimatching",
                "id": "stringmultimatching",
                "link": "https://open.kattis.com/problems/stringmultimatching"
            },
            {
                "name": "Beautiful Subarrays",
                "id": "subarrays",
                "link": "https://open.kattis.com/problems/subarrays"
            }
        ]

        Example for full detail mode:
        [
            {
                "name": "XOR Equation",
                "id": "xorequation",
                "fastest": 0.02,
                "shortest": 711,
                "total": 518,
                "acc": 152,
                "difficulty": 4.7,
                "category": "Medium",
                "link": "https://open.kattis.com/problems/xorequation"
            },
            {
                "name": "Xor Maximization",
                "id": "xormax",
                "fastest": 0.0,
                "shortest": 5,
                "total": 921,
                "acc": 258,
                "difficulty": 6.1,
                "category": "Hard",
                "link": "https://open.kattis.com/problems/xormax"
            }
        ]
        '''

        has_content, data = True, []

        if low_detail_mode:
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
        else:
            params = {
                'page': 1,
                'f_solved': ['off', 'on'][show_solved],
                'f_partial-score': ['off', 'on'][show_partial],
                'f_tried': ['off', 'on'][show_tried],
                'f_untried': ['off', 'on'][show_untried]
            }

            with ThreadPoolExecutor(max_workers=self.get_max_workers()) as executor:
                futures = []
                while has_content:
                    has_content = False
                    futures.clear()
                    for _ in range(self.get_max_workers()):
                        futures.append(executor.submit(self.new_get, f'{self.get_base_url()}/problems', params=params.copy()))
                        params['page'] += 1
                    for f in as_completed(futures):
                        soup = bs(f.result().content, features='lxml')
                        if not soup: continue

                        try:                    table = soup.find('section', class_='strip strip-item-plain').find('table', class_='table2')
                        except AttributeError:  continue # end of page (no data found)
                        try:                    table_content = get_table_rows(table)
                        except AttributeError:  continue # nothing to see

                        for row in table_content:
                            columns = row.find_all('td')
                            if columns:
                                has_content = True
                                link = f"{self.get_base_url()}{columns[ProblemsColumn.PROBLEM_NAME].find('a').get('href')}"
                                difficulty = float((re.findall('[\d\.]+', columns[ProblemsColumn.DIFFICULTY_CATEGORY].text) or [None])[-1])
                                    # [0] instead of [-1] if we want to take min instead of max
                                    # for example:
                                    # - difficulty 9.1-9.6 -> [9.1, 9.6]
                                    # - difficulty 5.0 -> [5.0]
                                try:    category = (re.findall('[A-Za-z]+', columns[ProblemsColumn.DIFFICULTY_CATEGORY].text) or ['N/A'])[0]
                                except: category = 'N/A'
                                data.append({
                                    'name': columns[ProblemsColumn.PROBLEM_NAME].text.strip(),
                                    'id': get_last_path(link),
                                    'fastest': replace_double_dash(columns[ProblemsColumn.FASTEST_RUNTIME].text, float('inf')),
                                    'shortest': replace_double_dash(columns[ProblemsColumn.SHORTEST_LENGTH].text, -1),
                                    'total': int(columns[ProblemsColumn.N_SUBMISSIONS].text),
                                    'acc': int(columns[ProblemsColumn.N_ACC].text),
                                    'difficulty': difficulty,
                                    'category': category,
                                    'link': link
                                })
        return self.Result(sorted(data, key=lambda x: x['id']))

    @lru_cache
    def plot_problems(self, filepath=None, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Plots the histogram of Kattis problems by difficulty points to a specified filepath, if any.

        By default, this function plots all solved and partially solved problems without saving it to any file.
        '''
        enum_to_title = lambda c: c.name.replace('_', '/').title()

        df = pd.DataFrame(self.problems(show_solved, show_partial, show_tried, show_untried))
        categories = set(df.category)

        hue_order = [enum_to_title(c) for c in [DifficultyColor.N_A, DifficultyColor.HARD, DifficultyColor.MEDIUM, DifficultyColor.EASY] if enum_to_title(c) in categories]
        palette = {enum_to_title(c):c.value for c in [DifficultyColor.EASY, DifficultyColor.MEDIUM, DifficultyColor.HARD, DifficultyColor.N_A] if enum_to_title(c) in categories}

        diff_lo = math.floor(min([d for d in df.difficulty if d], default=0))
        diff_hi = math.ceil(max([d for d in df.difficulty if d], default=0))

        plt.clf()
        hist = sns.histplot(data=df, x='difficulty', hue='category', multiple='stack', bins=[i/10 for i in range(10*diff_lo, 10*diff_hi+1)], hue_order=hue_order, palette=palette)
        hist.set(title=f'Solved Kattis Problems by {self.get_username()} ({df.shape[0]})', xlabel='Difficulty')
        plt.legend(title='Category', loc='upper right', labels=hue_order[::-1])
        plt.xticks([*range(diff_lo, diff_hi+1)])

        if filepath != None: plt.savefig(filepath), print(f'[plot_problems] Saved to {filepath}')

        plt.show()

    @list_to_tuple
    @lru_cache
    def problem(self, problem_ids, download_files=False, *bc_args):
        '''
        Obtain information about one or more specific problems. The problem_ids parameter can be a string of a single problem ID, or a sequence of problem IDs.

        By default, all files, including the sample test cases, will not be downloaded within the result metadata.

        Example:
        [
            {
                "id": "satisfaction",
                "text": "...",
                "cpu": "45 seconds",
                "memory": "1024 MB",
                "difficulty": 9.4,
                "category": "Hard",
                "author": "",
                "source": "2013 University of Chicago Invitational Programming Contest",
                "files": {
                    "satisfaction.zip": {
                        "sample.in": "...",
                        "sample.ans": "..."
                    }
                },
                "statistics": {
                    "Python 3": {
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
                "submissions": [
                    {
                        "status": "Time Limit Exceeded",
                        "runtime": "> 45.00 s",
                        "language": "C++",
                        "test_case_passed": 0,
                        "test_case_full": 4,
                        "link": "https://open.kattis.com/submissions/123456"
                    }
                ]
            }
        ]
        '''

        ret = []
        if type(problem_ids) == str: problem_ids = [problem_ids]

        for problem_id in {*problem_ids}:
            response = self.new_get(f'{self.get_base_url()}/problems/{problem_id}')

            if not response.ok: print(f'[problem] Ignoring {problem_id}'); continue

            soup = bs(response.content, features='lxml')
            body = soup.find('div', class_='problembody')
            data = {'id': problem_id, 'text': body.text.strip()}

            cpu = memory = author = source = ''
            difficulty, category, files = None, 'N/A', {}
            for div in soup.find_all('div', class_='metadata-grid'):
                for d in div.find_all('div', class_='card'):
                    div_text = [s.text.strip() for s in d.find_all('span') if s.text.strip()]
                    if div_text[0] == ProblemMetadataField.CPU_TIME_LIMIT:
                        cpu = div_text[-1].strip()
                    elif div_text[0] == ProblemMetadataField.MEMORY_LIMIT:
                        memory = div_text[-1].strip()
                    elif len(div_text) > 1 and div_text[1] == ProblemMetadataField.DIFFICULTY:
                        difficulty = float((re.findall('[\d\.]+', columns[ProblemsColumn.DIFFICULTY_CATEGORY].text) or [None])[-1])
                                    # [0] instead of [-1] if we want to take min instead of max
                                    # for example:
                                    # - difficulty 9.1-9.6 -> [9.1, 9.6]
                                    # - difficulty 5.0 -> [5.0]
                        category = div_text[2].strip() if len(div_text) > 2 else 'N/A'
                    elif div_text[0] == ProblemMetadataField.SOURCE_LICENSE:
                        text_links = [(s.text.strip(), [a.get('href').strip('/') for a in s.find_all('a')]) for s in d.find_all('span') if s.text.strip()]
                        for text, links in text_links:
                            if any(link.startswith('problem-authors') for link in links): author = text
                            if any(link.startswith('problem-sources') for link in links): source = text
                    elif div_text[0] == ProblemMetadataField.ATTACHMENTS or div_text[0] == ProblemMetadataField.DOWNLOADS:
                        if not download_files: continue
                        for url, fn in [(f"{self.get_base_url()}{a.get('href')}", a.get('download') or get_last_path(a.get('href'))) for a in d.find_all('a')]:
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
                'difficulty': difficulty,
                'category': category,
                'author': author,
                'source': source,
                'files': files
            }

            # statistics
            data['statistics'] = {}
            soup = self.get_soup_response(f'{self.get_base_url()}/problems/{problem_id}/statistics')
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
            soup = self.get_soup_response(f'{self.get_base_url()}/problems/{problem_id}?tab=submissions')
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
            ret.append(data)

        return self.Result(ret)

    @lru_cache
    def achievements(self):
        '''
        Lists down all your Kattis achievements. Flex it!

        Example:
        [
            {
                "name": "Zyxab",
                "id": "zyxab",
                "runtime": 0.01,
                "length": 10,
                "achievement": "Within 100% of shortest",
                "difficulty": 2.6,
                "category": "Easy",
                "link": "https://open.kattis.com/problems/zyxab"
            },
            ...
        ]
        '''

        has_content, params, data = True, {'page': 1}, []

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
                    table = soup.find('table', class_='table2')
                    for row in get_table_rows(table):
                        columns = row.find_all('td')
                        if [column.text.strip() for column in columns if column.text.strip()]:
                            if columns[SolvedProblemsColumn.NAME].find('a') == None: continue
                            has_content = True
                            link = f"{self.get_base_url()}{columns[SolvedProblemsColumn.NAME].find('a').get('href')}"
                            achievement = ', '.join(sorted(set(sp.text.strip() for sp in columns[SolvedProblemsColumn.ACHIEVEMENTS].find_all('span') if len(sp.find_all('span')) == 1)))
                            if not achievement: continue
                            try:        difficulty = float(re.findall('[\d\.]+', columns[SolvedProblemsColumn.DIFFICULTY].text)[-1])
                            except:     difficulty = None
                            try:        category = re.findall('[A-Za-z]+', columns[SolvedProblemsColumn.DIFFICULTY].text)[0]
                            except:     category = 'N/A'
                            data.append({
                                'name': columns[SolvedProblemsColumn.NAME].text,
                                'id': get_last_path(link),
                                'runtime': replace_double_dash(columns[SolvedProblemsColumn.CPU_RUNTIME].text, float('inf')),
                                'length': replace_double_dash(columns[SolvedProblemsColumn.LENGTH].text, -1),
                                'achievement': achievement,
                                'difficulty': difficulty,
                                'category': category,
                                'link': link
                            })
        return self.Result(sorted(data, key=lambda x: x['id']))

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
                "link": "https://open.kattis.com/submissions/123456"
            },
            {
                "id": "otherside",
                "name": "Other Side",
                "timestamp": "2021-01-02 00:00:02",
                "runtime": "0.12",
                "language": "Kotlin",
                "test_case_passed": 42,
                "test_case_full": 42,
                "link": "https://open.kattis.com/submissions/234567"
            }
        ]
        '''
        if languages == None: return self.stats('')

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
    def suggest(self):
        '''
        Retrieves suggested problems based on what you have solved so far.

        Example:
        [
            {
                "pid": "composedrhythms",
                "difficulty": "Trivial",
                "name": "Composed Rhythms",
                "link": "https://open.kattis.com/problems/composedrhythms",
                "min": 1.4,
                "max": 1.4
            },
            {
                "pid": "tolvuihlutir",
                "difficulty": "Easy",
                "name": "Tölvuíhlutir",
                "link": "https://open.kattis.com/problems/tolvuihlutir",
                "min": 1.8,
                "max": 6.1
            }
        ]
        '''

        soup = self.get_homepage()
        try:    table = soup.find_all('table', class_='table2 report_grid-problems_table')[0]
        except: return self.Result([])
    
        data = []
        for row in get_table_rows(table):
            header = row.find('th')
            if header: difficulty = header.text
            column = row.find('td')
            pid = get_last_path(column.find('a').get('href'))
            link = f'{self.get_base_url()}/problems/{pid}'
            name, pt = column.text.strip().split('\n')
            pt = pt.strip(' pt')
            data.append({
                'pid': pid, 'difficulty': difficulty, 'name': name, 'link': link,
                'min': float(pt.split('-')[0]), 'max': float(pt.split('-')[-1]),
            })
        return self.Result(data)

    @lru_cache
    def user_ranklist(self):
        '''
        Retrieves the top 100 user ranklist.

        Example:
        [
            {
                "rank": 1,
                "name": "Jack",
                "username": "jackdoe",
                "points": 12345.6,
                "country_code": "USA",
                "country": "United States",
                "university_code": "nus.edu.sg",
                "university": "National University of Singapore"
            },
            ...,
            {
                "rank": 100,
                "name": "Jill",
                "username": "jill-doe",
                "points": 1.2,
                "country_code": "SGP",
                "country": "Singapore",
                "university_code": "mit.edu",
                "university": "Massachusetts Institute of Technology"
            }
        ]
        '''

        data = []
        soup = self.get_soup_response(f'{self.get_base_url()}/ranklist')
        try:        table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users') or 1/0
        except:     return self.Result([])
        
        headers = get_table_headers(table)
        for row in get_table_rows(table):
            columns = row.find_all('td')
            if len(columns) == 1: break # stop at ellipsis if any

            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]

            name_urls = columns_url[UserRanklistColumn.USER]

            country = columns_text[UserRanklistColumn.COUNTRY]
            country_urls = columns_url[UserRanklistColumn.COUNTRY]
            country_code = get_last_path(country_urls[0].get('href')) if country_urls else None

            university = columns_text[UserRanklistColumn.UNIVERSITY]
            university_urls = columns_url[UserRanklistColumn.UNIVERSITY]
            university_code = get_last_path(university_urls[0].get('href')) if university_urls else None

            data.append({
                'rank': int(columns_text[UserRanklistColumn.RANK]) if columns_text[UserRanklistColumn.RANK].isdigit() else None,
                'name': columns_text[UserRanklistColumn.USER],
                'username': get_last_path(name_urls[0].get('href')),
                'points': float(columns_text[UserRanklistColumn.SCORE]),
                'country_code': country_code if country else None,
                'country': country or None,
                'university_code': university_code if university else None,
                'university': university or None
            })
        return self.Result(data)

    @lru_cache
    def country_ranklist(self, value=''):
        '''
        Retrieves the top 100 country ranklist if the value paramater is not set, otherwise a specific country's top 50.

        Example for top 100:
        [
            {
                "rank": 1,
                "country": "United States",
                "country_code": "USA",
                "users": 12345,
                "universities": 2345,
                "points": 1234.5
            },
            ...,
            {
                "rank": 100,
                "country": "Singapore",
                "country_code": "SGP",
                "users": 1,
                "universities": 1,
                "points": 1.2
            }
        ]

        Example for specific country top 50:
        [
            {
                "rank": 1,
                "name": "Jack Doe",
                "username": "jack-doe",
                "points": 12345.6,
                "country_code": "SGP",
                "country": "Singapore",
                "subdivision_code": None,
                "subdivision": None,
                "university_code": "nus.edu.sg",
                "university": "National University of Singapore"
            },
            ...,
            {
                "rank": 50,
                "name": "Jill",
                "username": "jilldoe",
                "points": 1.2,
                "country_code": "SGP",
                "country": "Singapore",
                "subdivision_code": "PI",
                "subdivision": "Punggol Imaginary",
                "university_code": None,
                "university": None
            }
        ]
        '''

        data = []
        if value == '':
            # display top 100 countries
            soup = self.get_soup_response(f'{self.get_base_url()}/ranklist/countries')
            try:        table = soup.find('table', class_='table2 report_grid-problems_table') or 1/0
            except:     return self.Result([])

            headers = get_table_headers(table)
            for row in get_table_rows(table):
                columns = row.find_all('td')
                if len(columns) == 1: break # stop at ellipsis if any

                columns_text = [column.text.strip() for column in columns]
                columns_url = [column.find_all('a') for column in columns]

                data.append({
                    'rank': int(columns_text[CountryRanklistColumn.RANK]),
                    'country': columns_text[CountryRanklistColumn.COUNTRY],
                    'country_code': get_last_path(columns_url[CountryRanklistColumn.COUNTRY][0].get('href')),
                    'users': int(columns_text[CountryRanklistColumn.USERS]),
                    'universities': int(columns_text[CountryRanklistColumn.UNIVERSITIES]),
                    'points': float(columns_text[CountryRanklistColumn.SCORE]),
                })
        else:
            # display a specific country
            country_code = guess_id(value, self.get_database().get_countries())
            soup = self.get_soup_response(f'{self.get_base_url()}/countries/{country_code}')
            try:        table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users') or 1/0
            except:     return self.Result([])

            headers = get_table_headers(table)
            for row in get_table_rows(table):
                columns = row.find_all('td')
                if len(columns) == 1: break # stop at ellipsis if any

                columns_text = [column.text.strip() for column in columns]
                columns_url = [column.find_all('a') for column in columns]

                if RanklistField.SUBDIVISION in headers:
                    subdivision = columns_text[SingleCountryRanklistColumn.SUBDIVISION]
                    subdivision_urls = columns_url[SingleCountryRanklistColumn.SUBDIVISION]
                    subdivision_code = get_last_path(subdivision_urls[0].get('href')) if subdivision_urls else None
                else:
                    subdivision = None

                if RanklistField.UNIVERSITY in headers:
                    university = columns_text[SingleCountryRanklistColumn.UNIVERSITY]
                    university_urls = columns_url[SingleCountryRanklistColumn.UNIVERSITY]
                    university_code = get_last_path(university_urls[0].get('href')) if university_urls else None
                else:
                    university = None

                data.append({
                    'rank': int(columns_text[SingleCountryRanklistColumn.RANK]),
                    'name': columns_text[SingleCountryRanklistColumn.USER],
                    'username': get_last_path(columns_url[SingleCountryRanklistColumn.USER][0].get('href')),
                    'points': float(columns_text[SingleCountryRanklistColumn.SCORE]),
                    'country_code': country_code,
                    'country': self.get_database().get_countries()[country_code],
                    'subdivision_code': subdivision_code if subdivision else None,
                    'subdivision': subdivision or None,
                    'university_code': university_code if university else None,
                    'university': university or None
                })
        return self.Result(data)

    @lru_cache
    def university_ranklist(self, value=''):
        '''
        Retrieves the top 100 university ranklist if the value paramater is not set, otherwise a specific university's top 50.

        Example for top 100:
        [
            {
                "rank": 1,
                "university": "National University of Singapore",
                "university_code": "nus.edu.sg",
                "country": "Singapore",
                "country_code": "SGP",
                "subdivision": None,
                "users": 5000,
                "points": 10000.1
            },
            ...,
            {
                "rank": 100,
                "university": "Not NUS",
                "university_code": "not.nus",
                "country": "Antartica",
                "country_code": "ATC",
                "subdivision": "Unknown",
                "users": 123,
                "points": 1.2
            }
        ]

        Example for specific university top 50:
        [
            {
                "rank": 1,
                "name": "Jack",
                "username": "jackdoe",
                "points": 12345.6,
                "country_code": "IDN",
                "country": "Indonesia",
                "subdivision_code": "JK",
                "subdivision": "DKI Jakarta",
                "university_code": "binus.ac.id",
                "university": "Binus University"
            },
            ...,
            {
                "rank": 50,
                "name": "Jill Doe",
                "username": "jill-doe",
                "points": 1.2,
                "country_code": "IDN",
                "country": "Indonesia",
                "subdivision_code": None,
                "subdivision": None,
                "university_code": "binus.ac.id",
                "university": "Binus University"
            }
        ]
        '''

        data = []
        if value == '':
            # display top 100 universities
            soup = self.get_soup_response(f'{self.get_base_url()}/ranklist/universities')
            try:        table = soup.find('table', class_='table2 report_grid-problems_table') or 1/0
            except:     return self.Result([])

            headers = get_table_headers(table)
            for row in get_table_rows(table):
                columns = row.find_all('td')
                if len(columns) == 1: break # stop at ellipsis if any

                columns_text = [column.text.strip() for column in columns]
                columns_url = [column.find_all('a') for column in columns]

                data.append({
                    'rank': int(columns_text[UniversityRanklistColumn.RANK]),
                    'university': columns_text[UniversityRanklistColumn.UNIVERSITY],
                    'university_code': get_last_path(columns_url[UniversityRanklistColumn.UNIVERSITY][0].get('href')),
                    'country': columns_text[UniversityRanklistColumn.COUNTRY],
                    'country_code': get_last_path(columns_url[UniversityRanklistColumn.COUNTRY][0].get('href')),
                    'subdivision': columns_text[UniversityRanklistColumn.SUBDIVISION] or None,
                    'users': int(columns_text[UniversityRanklistColumn.USERS]),
                    'points': float(columns_text[UniversityRanklistColumn.SCORE]),
                })
        else:
            # display a specific university
            university_code = guess_id(value, self.get_database().get_universities())
            soup = self.get_soup_response(f'{self.get_base_url()}/universities/{university_code}')
            table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
            if not table: return self.Result([])

            headers = get_table_headers(table)
            for row in get_table_rows(table):
                columns = row.find_all('td')
                if len(columns) == 1: break # stop at ellipsis if any

                columns_text = [column.text.strip() for column in columns]
                columns_url = [column.find_all('a') for column in columns]

                if RanklistField.COUNTRY in headers:
                    country = columns_text[SingleUniversityRanklistColumn.COUNTRY]
                    country_urls = columns_url[SingleUniversityRanklistColumn.COUNTRY]
                    country_code = get_last_path(country_urls[0].get('href')) if country_urls else None
                else:
                    country = None

                if RanklistField.SUBDIVISION in headers:
                    subdivision = columns_text[SingleUniversityRanklistColumn.SUBDIVISION]
                    subdivision_urls = columns_url[SingleUniversityRanklistColumn.SUBDIVISION]
                    subdivision_code = get_last_path(subdivision_urls[0].get('href')) if subdivision_urls else None
                else:
                    subdivision = None

                data.append({
                    'rank': int(columns_text[SingleUniversityRanklistColumn.RANK]),
                    'name': columns_text[SingleUniversityRanklistColumn.USER],
                    'username': get_last_path(columns_url[SingleUniversityRanklistColumn.USER][0].get('href')),
                    'points': float(columns_text[SingleUniversityRanklistColumn.SCORE]),
                    'country_code': country_code if country else None,
                    'country': country or None,
                    'subdivision_code': subdivision_code if subdivision else None,
                    'subdivision': subdivision or None,
                    'university_code': university_code,
                    'university': self.get_database().get_universities()[university_code]
                })
        return self.Result(data)

    @lru_cache
    def challenge_ranklist(self):
        '''
        Retrieves the top 100 challenge ranklist.

        Example:
        [
            {
                "rank": 1,
                "name": "Jack",
                "username": "jackdoe",
                "score": 12345.6,
                "country_code": "USA",
                "country": "United States",
                "university_code": "nus.edu.sg",
                "university": "National University of Singapore"
            },
            ...,
            {
                "rank": 100,
                "name": "Jill",
                "username": "jill-doe",
                "score": 1.2,
                "country_code": "SGP",
                "country": "Singapore",
                "university_code": "mit.edu",
                "university": "Massachusetts Institute of Technology"
            }
        ]
        '''

        data = []
        soup = self.get_soup_response(f'{self.get_base_url()}/ranklist/challenge')
        try:        table = soup.find('table', class_='table2 report_grid-problems_table') or 1/0
        except:     return self.Result([])

        headers = get_table_headers(table)
        for row in get_table_rows(table):
            columns = row.find_all('td')
            if len(columns) == 1: break # stop at ellipsis if any

            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]

            name_urls = columns_url[ChallengeRanklistColumn.USER]

            country = columns_text[ChallengeRanklistColumn.COUNTRY]
            country_urls = columns_url[ChallengeRanklistColumn.COUNTRY]
            country_code = get_last_path(country_urls[0].get('href')) if country_urls else None

            university = columns_text[ChallengeRanklistColumn.UNIVERSITY]
            university_urls = columns_url[ChallengeRanklistColumn.UNIVERSITY]
            university_code = get_last_path(university_urls[0].get('href')) if university_urls else None

            data.append({
                'rank': int(columns_text[ChallengeRanklistColumn.RANK]) if columns_text[ChallengeRanklistColumn.RANK].isdigit() else None,
                'name': columns_text[ChallengeRanklistColumn.USER],
                'username': get_last_path(name_urls[0].get('href')),
                'score': float(columns_text[ChallengeRanklistColumn.CHALLENGE_SCORE]),
                'country_code': country_code if country else None,
                'country': country or None,
                'university_code': university_code if university else None,
                'university': university or None
            })
        return self.Result(data)

    @lru_cache
    def ranklist(self, *bc_args):
        '''
        Retrieves the ranklist of users near your position.

        Example:
        [
            {
                "rank": 103,
                "name": "Jack",
                "points": 12345.6,
                "country": "United States",
                "university": "National University of Singapore"
                "username": "jackdoe",
                "country_code": "USA",
                "university_code": "nus.edu.sg"
            },
            ...,
            {
                "rank": 110,
                "name": "Jill",
                "points": 9000.1,
                "country": "Singapore",
                "university": None,
                "username": "jill-doe",
                "country_code": "SGP"
            }
        ]
        '''

        data = []
        soup = self.get_homepage()
        try:        table = soup.find_all('table', class_='table2 report_grid-problems_table')[1] or 1/0
        except:     return self.Result([])

        for row in get_table_rows(table):
            columns = row.find_all('td')
            columns_text = [column.text.strip() for column in columns]

            new_data = {
                'rank': int(columns_text[DefaultRanklistColumn.RANK]) if columns_text[DefaultRanklistColumn.RANK].isdigit() else None,
                'name': columns_text[DefaultRanklistColumn.USER],
                'points': float(re.findall(r'[\d\.]+', columns_text[DefaultRanklistColumn.SCORE])[0]),
                'country': None,
                'university': None
            }

            for urlsplit, title in [(column.get('href').split('/'), column.get('title')) for column in columns[DefaultRanklistColumn.USER].find_all('a')]:
                assert sum(x in urlsplit for x in ['users', 'universities', 'countries']) == 1, 'Only one field should be present'
                if 'users' in urlsplit:
                    new_data['username'] = urlsplit[-1]
                elif 'universities' in urlsplit:
                    new_data['university_code'] = urlsplit[-1]
                    new_data['university'] = title
                elif 'countries' in urlsplit:
                    new_data['country_code'] = urlsplit[-1]
                    new_data['country'] = title
            data.append(new_data)
        return self.Result(data)

    @lru_cache
    def problem_authors(self):
        '''
        Lists down all problem authors.

        Example:
        [
            {
                "name": "Lorem Ipsum",
                "problems": 6,
                "avg_difficulty": 1.3,
                "avg_category": "Easy",
                "link": "https://open.kattis.com/problem-authors/Lorem%20Ipsum"
            },
            {
                "name": "Jack Julius Jill",
                "problems": 12,
                "avg_difficulty": 5.3,
                "avg_category": "Medium",
                "link": "https://open.kattis.com/problem-authors/Jack%20Julius%Jill"
            }
        ]
        '''

        response = self.new_get(f'{self.get_base_url()}/problem-authors')
        try:        soup = bs(response.content, features='lxml')
        except:     return self.Result([])

        table = soup.find('table', class_='table2')
        if not table: return self.Result([])

        data = []
        for row in get_table_rows(table):
            columns = row.find_all('td')
            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]

            try:        difficulty = float(re.findall('[\d\.]+', columns_text[ProblemAuthorsColumn.AVG_DIFF])[-1])
            except:     difficulty = None

            data.append({
                'name': columns_text[ProblemAuthorsColumn.AUTHOR].strip(),
                'problems': int(columns_text[ProblemAuthorsColumn.PROBLEMS]),
                'avg_difficulty': difficulty,
                'avg_category': (re.findall('[A-Za-z]+', columns_text[ProblemAuthorsColumn.AVG_DIFF]) or ['N/A'])[0],
                'link': f'{self.get_base_url()}{columns_url[ProblemAuthorsColumn.AUTHOR][0].get("href")}'
            })
        return self.Result(data)

    @lru_cache
    def problem_sources(self):
        '''
        Lists down all problem sources.

        Example:
        [
            {
                "name": "Lorem Ipsum Contest",
                "problems": 6,
                "avg_difficulty": 1.3,
                "avg_category": "Easy",
                "link": "https://open.kattis.com/problem-sources/Lorem%20Ipsum%20Contest"
            },
            {
                "name": "Jack Julius Jill Cup",
                "problems": 12,
                "avg_difficulty": 5.3,
                "avg_category": "Medium",
                "link": "https://open.kattis.com/problem-authors/Jack%20Julius%Jill%20Cup"
            }
        ]
        '''

        response = self.new_get(f'{self.get_base_url()}/problem-sources')
        try:        soup = bs(response.content, features='lxml')
        except:     return self.Result([])

        table = soup.find('table', class_='table2')
        if not table: return self.Result([])

        data = []
        for row in get_table_rows(table):
            columns = row.find_all('td')
            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]

            try:        difficulty = float(re.findall('[\d\.]+', columns_text[ProblemSourcesColumn.AVG_DIFF])[-1])
            except:     difficulty = None

            data.append({
                'name': columns_text[ProblemSourcesColumn.SOURCE].strip(),
                'problems': int(columns_text[ProblemSourcesColumn.PROBLEMS]),
                'avg_difficulty': difficulty,
                'avg_category': (re.findall('[A-Za-z]+', columns_text[ProblemSourcesColumn.AVG_DIFF]) or ['N/A'])[0],
                'link': f'{self.get_base_url()}{columns_url[ProblemSourcesColumn.SOURCE][0].get("href")}'
            })
        return self.Result(data)
