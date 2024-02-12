import io
import math
import matplotlib.pyplot as plt
import pandas as pd
import re
import requests
import seaborn as sns
import warnings
import zipfile

from bs4 import BeautifulSoup as bs
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from getpass import getpass

from ..database import LANGUAGES, COUNTRIES, UNIVERSITIES
from ..utils import guess_id

warnings.warn = lambda *args, **kwargs: None # suppress warnings
truncate = lambda text: text if (new_text:=text.replace('  ', ' ')) == text else truncate(new_text)

class Kattis(requests.Session):

    BASE_URL = 'https://open.kattis.com'
    MAX_WORKERS = 6

    def new_get(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return self.new_get(*args, **kwargs)
    
    def new_post(self, *args, **kwargs):
        try:
            return self.post(*args, **kwargs)
        except:
            return self.new_post(*args, **kwargs)

    class Result(list):
        def __init__(self, data):
            super().__init__(data)
            self.to_df = lambda: pd.DataFrame(data)

    def get_base_url(self):
        return self.BASE_URL

    def set_base_url(self, url):
        self.BASE_URL = url

    def get_homepage(self):
        return self.homepage

    def set_homepage(self, hp):
        self.homepage = hp

    def __init__(self, user, password=None):
        '''
        A local Kattis session.
        Takes in a user (email or username) and a password.
        '''

        super().__init__()
        if password == None: password = getpass('Enter password: ')
        self.user, self.password = user, password
        
        # Get CSRF token
        response = self.new_get(f'{self.BASE_URL}/login/email')
        regex_result = re.findall(r'value="(\d+)"', response.text)
        assert len(regex_result) == 1, f'Regex found several possible CSRF tokens, {regex_result}'
        self.csrf_token = regex_result[0]

        # Get EduSite cookie + homepage
        data = {
            'csrf_token': self.csrf_token,
            'user': self.user,
            'password': self.password
        }
        response = self.new_post(f'{self.BASE_URL}/login/email', data=data)
        assert response.url.startswith(self.BASE_URL), 'Cannot login to Kattis'

        self.homepage = bs(response.content, features='lxml')
        names = []
        for a in self.homepage.find_all('a'):
            href = a.get('href')
            if href:
                paths = href.split('/')
                if len(paths) > 2 and paths[1] == 'users':
                    names.append(paths[2])
        ctr = Counter(names)
        assert ctr, 'There are issues when logging in to Kattis, please check your username again'
        max_freq = max(ctr.values())
        candidate_usernames = [name for name in ctr if ctr[name] == max_freq]
        print(f'Candidate username(s): {candidate_usernames}', flush=True)
        self.user = candidate_usernames[0]
        print('Successfully logged in to Kattis!', flush=True)

    @lru_cache
    def problems(self, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Gets all Kattis problems based on some filters.
        Returns a JSON-like structure with these fields:
            name, id, fastest, shortest, total, acc, difficulty, category, link

        Default: all solved and partially solved problems.
        '''

        has_content = True
        params = {
            'page': 1,
            'f_solved': ['off', 'on'][show_solved],
            'f_partial-score': ['off', 'on'][show_partial],
            'f_tried': ['off', 'on'][show_tried],
            'f_untried': ['off', 'on'][show_untried]
        }
        data = []

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            while has_content:
                has_content = False
                futures.clear()
                for _ in range(self.MAX_WORKERS):
                    futures.append(executor.submit(self.new_get, f'{self.BASE_URL}/problems', params=params.copy()))
                    params['page'] += 1
                for f in as_completed(futures):
                    response = f.result()
                    soup = bs(response.content, features='lxml')
                    if not soup: continue
                    table = soup.find('section', class_='strip strip-item-plain').find('table', class_='table2')
                    try:
                        table_content = table.tbody.find_all('tr')
                    except AttributeError:
                        continue
                    for row in table_content:
                        columns = row.find_all('td')
                        if columns:
                            has_content = True
                            link = f"{self.BASE_URL}{columns[0].find('a').get('href')}"
                            name = columns[0].text
                            fastest = float(columns[2].text.replace('--', 'inf'))
                            shortest = int(float(columns[3].text.replace('--', '-1')))
                            total = int(columns[4].text)
                            acc = int(columns[5].text)
                            try:
                                difficulty = float(re.findall('[\d\.]+', columns[7].text)[-1])
                                    # [0] instead of [-1] if we want to take min instead of max
                                    # for example:
                                    # - difficulty 9.1-9.6 -> [9.1, 9.6]
                                    # - difficulty 5.0 -> [5.0]
                            except:
                                difficulty = None
                            if len(columns) == 10:
                                try:
                                    category = re.findall('[A-Za-z]+', columns[7].text)[0]
                                except:
                                    category = 'N/A'
                            else:
                                category = 'N/A'
                            data.append({
                                'name': name,
                                'id': link.split('/')[-1],
                                'fastest': fastest,
                                'shortest': shortest,
                                'total': total,
                                'acc': acc,
                                'difficulty': difficulty,
                                'category': category,
                                'link': link
                            })
        return self.Result(sorted(data, key=lambda x: x['id']))

    @lru_cache
    def problems_v2(self, show_non_ac=False):
        '''
        Gets all accepted Kattis problems. Note that this is entirely different than the `problems`
            method due to possible gateway issues from the initial version.
        Returns a simpler JSON-like structure with these fields:
            name, id, link

        Default: all solved and partially solved problems.
        '''

        has_content = True
        params = {
            'page': 0,
            'tab': 'submissions',
            'status': 'AC'
        }

        data = []
        pid_set = set()

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            while has_content:
                has_content = False
                futures.clear()
                for _ in range(self.MAX_WORKERS):
                    futures.append(executor.submit(self.new_get, f'{self.BASE_URL}/users/{self.user}', params=params.copy()))
                    params['page'] += 1
                for f in as_completed(futures):
                    response = f.result()
                    soup = bs(response.content, features='lxml')
                    if not soup: continue
                    table = table = soup.find('div', id='submissions-tab').find('section', class_='strip strip-item-plain').find('table', class_='table2')
                    try:
                        table_content = table.tbody.find_all('tr')
                    except AttributeError:
                        continue
                    for row in table_content:
                        columns = row.find_all('td')
                        if columns and len(columns) > 2:
                            has_content = True
                            pid = columns[2].find_all('a')[-1].get('href').split('/')[-1] # might have two links if it belongs to a contest
                            if pid not in pid_set:
                                link = f"{self.BASE_URL}/problems/{pid}"
                                name = columns[2].text.split('/')[-1].strip()
                                pid_set.add(pid)
                                data.append({
                                    'name': name,
                                    'id': pid,
                                    'link': link
                                })

        if show_non_ac:
            # we can just use the latest soup and take the dropdown
            for option in soup.find_all('option')[1:]:
                pid = option.get('value').strip()
                if not pid: break
                if pid not in pid_set:
                    pid_set.add(pid)
                    data.append({
                        'name': option.text.strip(),
                        'id': pid,
                        'link': f"{self.BASE_URL}/problems/{pid}"
                    })

        return self.Result(sorted(data, key=lambda x: x['id']))

    @lru_cache
    def plot_problems(self, filepath=None, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Plots the histogram of Kattis problems to a specified filepath.

        Default: plots all solved and partially solved problems without saving it to any file.
        '''

        df = pd.DataFrame(self.problems(show_solved, show_partial, show_tried, show_untried))
        categories = set(df.category)
        hue_order = [c for c in ['Easy', 'Medium', 'Hard', 'N/A'][::-1] if c in categories]
        palette = {'Easy': '#39a137', 'Medium': '#ffbe00', 'Hard': '#ff411a', 'N/A': 'gray'}
        for c in [*palette]:
            if c not in categories: del palette[c]
        diff_lo = math.floor(min([d for d in df.difficulty if d], default=0))
        diff_hi = math.ceil(max([d for d in df.difficulty if d], default=0))
        hist = sns.histplot(data=df, x='difficulty', hue='category', multiple='stack', bins=[i/10 for i in range(10*diff_lo, 10*diff_hi+1)], hue_order=hue_order, palette=palette)
        hist.set(title=f'Solved Kattis Problems by {self.user} ({df.shape[0]})', xlabel='Difficulty')
        plt.legend(title='Category', loc='upper right', labels=hue_order[::-1])
        plt.xticks([*range(diff_lo, diff_hi+1)])
        if filepath != None:
            plt.savefig(filepath)
            print(f'Saved to {filepath}')
        plt.show()

    @lru_cache
    def list_unsolved(self, show_partial=True):
        '''
        Quick shortcut for all Kattis grinders to list all unsolved questions.

        Default: includes partially solved questions.
        '''
        return self.problems(show_solved=False, show_partial=show_partial, show_tried=True, show_untried=True)

    @lru_cache
    def problem(self, problem_id, *problem_ids):
        '''
        Obtain information about one or more specific problems.
        Returns a JSON-like structure of the problem body text and their metadata.
        '''

        response = self.get(f'{self.BASE_URL}/problems/{problem_id}')

        if not response.ok:
            print(f'Ignoring {problem_id}')
            return []

        soup = bs(response.content, features='lxml')
        body = soup.find('div', class_='problembody')
        data = {'id': problem_id, 'text': body.text.strip()}

        cpu = memory = author = source = ''
        difficulty = None
        category = 'N/A'
        files = {}
        for div in soup.find_all('div', class_='metadata-grid'):
            for d in div.find_all('div', class_='card'):
                div_text = [s.text.strip() for s in d.find_all('span') if s.text.strip()]
                if div_text[0] == 'CPU Time limit':
                    cpu = div_text[-1].strip()
                elif div_text[0] == 'Memory limit':
                    memory = div_text[-1].strip()
                elif len(div_text) > 1 and div_text[1] == 'Difficulty':
                    try:
                        difficulty = float(div_text[0])
                    except:
                        difficulty = None
                    try:
                        category = div_text[2].strip()
                    except:
                        category = 'N/A'
                elif div_text[0] == 'Source & License':
                    text_links = [(s.text.strip(), [a.get('href').strip('/') for a in s.find_all('a')]) for s in d.find_all('span') if s.text.strip()]
                    for text, links in text_links:
                        if any(link.startswith('problem-authors') for link in links): author = text
                        if any(link.startswith('problem-sources') for link in links): source = text
                elif div_text[0] == 'Attachments' or div_text[0] == 'Downloads':
                    for url, fn in [(f"{self.BASE_URL}{a.get('href')}", a.get('download') or a.get('href').split('/')[-1]) for a in d.find_all('a')]:
                        if url.endswith('zip'):
                            with zipfile.ZipFile(io.BytesIO(self.get(url).content)) as z:
                                files[fn] = {}
                                for inner_fn in z.namelist():
                                    with z.open(inner_fn) as inner_file:
                                        files[fn][inner_fn] = inner_file.read().decode("utf-8")
                        else:
                            files[fn] = self.get(url).text
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
        response = self.get(f'{self.BASE_URL}/problems/{problem_id}/statistics')
        data['statistics'] = {}
        soup = bs(response.content, features='lxml')
        category_map = {}
        for option in soup.find_all('option'):
            category_map[option.get('value')] = [option.text, option.get('data-title')]
        for section in soup.find_all('section', class_='strip strip-item-plain'):
            table = section.find('table', class_='table2 report_grid-problems_table')
            section_id = section.get('id')
            language, description = category_map[section_id]
            data['statistics'][language] = data['statistics'].get(language, {})
            data['statistics'][language][['fastest', 'shortest']['shortest' in section_id]] = {}
            stats = data['statistics'][language][['fastest', 'shortest']['shortest' in section_id]]
            if table:
                stats['ranklist'] = []
                for row in table.tbody.find_all('tr'):
                    columns = row.find_all('td')
                    rank, name, runtime_or_length, date, _ = [column.text for column in columns]
                    rank = int(rank)
                    runtime_or_length = [float, int]['shortest' in section_id](runtime_or_length.split()[0])
                    username_a = columns[1].find('a')
                    if username_a:
                        username = username_a.get('href').split('/')[-1]
                    else:
                        username = None
                    stats['ranklist'].append({
                        'rank': rank,
                        'name': name,
                        'username': username,
                        ['runtime', 'length']['shortest' in section_id]: runtime_or_length,
                        'date': date
                    })
            stats['description'] = description

        # my submissions
        response = self.get(f'{self.BASE_URL}/problems/{problem_id}?tab=submissions')
        data['submissions'] = []
        soup = bs(response.content, features='lxml')
        table = soup.find('table', id='submissions')
        if table:
            for row in table.tbody.find_all('tr'):
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
                    link = f"{self.BASE_URL}{columns[-1].find('a').get('href')}"
                    data['submissions'].append({
                        'status': status,
                        'runtime': runtime,
                        'language': language,
                        'test_case_passed': test_case_passed,
                        'test_case_full': test_case_full,
                        'link': link
                    })

        ret = [data]
        for pid in set(problem_ids) - {problem_id}:
            prob = self.problem(pid)
            if prob: ret.append(prob[0])
        return self.Result(ret)

    @lru_cache
    def achievements(self, verbose=False):
        '''
        Lists down all your Kattis achievements. Flex it!
        The parameter verbose adjusts whether you only want to include the problems
            with at least one achievement or not.

        Default: includes only solved questions with at least one achievement.
        '''

        has_content = True
        params = {'page': 1}
        data = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            while has_content:
                has_content = False
                futures.clear()
                for _ in range(self.MAX_WORKERS):
                    futures.append(executor.submit(self.get, f'{self.BASE_URL}/users/{self.user}', params=params.copy()))
                    params['page'] += 1
                for f in as_completed(futures):
                    response = f.result()
                    soup = bs(response.content, features='lxml')
                    table = soup.find('table', class_='table2')
                    for row in table.tbody.find_all('tr'):
                        columns = row.find_all('td')
                        columns_text = [column.text for column in columns if column.text]
                        if columns_text:
                            if columns[0].find('a') == None: continue
                            has_content = True
                            link = f"{self.BASE_URL}{columns[0].find('a').get('href')}"
                            name = columns[0].text
                            runtime = float(columns[1].text.replace('--', 'inf'))
                            length = int(float(columns[2].text.replace('--', '-1')))
                            if len(columns) == 3:
                                if not verbose: continue
                                achievement = ''
                                difficulty = None
                                category = 'N/A'
                            elif len(columns) == 4:
                                if not verbose: continue
                                achievement = ''
                                try:
                                    difficulty = float(re.findall('[\d\.]+', columns[3].text)[-1])
                                except:
                                    difficulty = None
                                try:
                                    category = re.findall('[A-Za-z]+', columns[3].text)[0]
                                except:
                                    category = 'N/A'
                            else:
                                achievement = ', '.join(sorted(set(sp.text.strip() for sp in columns[3].find_all('span') if len(sp.find_all('span')) == 1)))
                                if not achievement: continue
                                try:
                                    difficulty = float(re.findall('[\d\.]+', columns[4].text)[-1])
                                except:
                                    difficulty = None
                                try:
                                    category = re.findall('[A-Za-z]+', columns[4].text)[0]
                                except:
                                    category = 'N/A'
                            data.append({
                                'name': name,
                                'id': link.split('/')[-1],
                                'runtime': runtime,
                                'length': length,
                                'achievement': achievement,
                                'difficulty': difficulty,
                                'category': category,
                                'link': link
                            })
        return self.Result(sorted(data, key=lambda x: x['id']))

    @lru_cache
    def stats(self, language='', *languages):
        '''
        Collects the statistics of your accepted (AC) submissions based on the programming language(s) used.
        Returns a JSON-like structure that contains fields such as:
            the submission time, problem name, number of test cases (and partial score), and its CPU runtime.
        If there are multiple AC submissions of the same language, only the best (highest score then fastest) is considered.

        Default: all languages.
        '''

        for lang in (language, *languages):
            if lang != '':
                assert lang in LANGUAGES, f'Cannot find {lang}, language specified must be one of {LANGUAGES}'

        has_content = True
        params = {
            'page': 0,
            'status': 'AC',
            'language': language
        }
        data = {}
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            while has_content:
                has_content = False
                futures.clear()
                for _ in range(self.MAX_WORKERS):
                    futures.append(executor.submit(self.get, f'{self.BASE_URL}/users/{self.user}', params=params.copy()))
                    params['page'] += 1
                for f in as_completed(futures):
                    response = f.result()
                    soup = bs(response.content, features='lxml')
                    table = soup.find('table', class_='table2 report_grid-problems_table double-rows')
                    for row in table.tbody.find_all('tr'):
                        columns = row.find_all('td')
                        columns_text = [column.text.strip() for column in columns if column.text.strip()]
                        if columns_text:
                            has_content = True
                            link = f"{self.BASE_URL}/submissions/{columns[-1].find('a').get('href').split('/')[-1]}"
                            ts = columns_text[0]
                            pid = columns[2].find_all('a')[-1].get('href').split('/')[-1] # use find_all as a workaround for contest links
                            name = columns_text[1].split(' / ')[-1]
                            runtime = ' '.join(columns_text[3].split()[:-1]) # not converting to float because some TLE solutions (with '>') can also be AC
                            language = columns_text[4]
                            tc_pass, tc_full = map(int, columns_text[5].split('/'))
                            new_data = {
                                'name': name,
                                'timestamp': ts,
                                'runtime': runtime,
                                'language': language,
                                'test_case_passed': tc_pass,
                                'test_case_full': tc_full,
                                'link': link
                            }
                            pts_regex = re.findall(r'[\d\.]+', columns_text[2])
                            if pts_regex:
                                new_data['score'] = float(pts_regex[0])
                            if pid not in data:
                                data[pid] = new_data
                            else:
                                data[pid] = max(
                                    data[pid], new_data,
                                    key=lambda x: (x.get('score', tc_pass/tc_full), x['test_case_passed'], -float(x['runtime'] if '>' not in x['runtime'] else 1e9))
                                )
        ret = [{'id': k, **v} for k, v in data.items()]
        for lang in set(languages) - {language}:
            ret.extend(self.stats(lang))
        return self.Result(sorted(ret, key=lambda x: x['id']))

    @lru_cache
    def suggest(self):
        '''
        Retrieves suggested problems based on what you have solved so far.
        Returns a JSON-like structure containing the suggested problems points and its difficulty.
        '''

        soup = self.get_homepage()
        try:
            table = soup.find_all('table', class_='table2 report_grid-problems_table')[0]
        except:
            return self.Result([])
        data = []
        for row in table.tbody.find_all('tr'):
            header = row.find('th')
            if header:
                difficulty = header.text
            column = row.find('td')
            pid = column.find('a').get('href').split('/')[-1]
            link = f'{self.BASE_URL}/problems/{pid}'
            name, pt = column.text.strip().split('\n')
            pt = pt.strip(' pt')
            data.append({
                'pid': pid, 'difficulty': difficulty, 'name': name, 'link': link,
                'min': float(pt.split('-')[0]), 'max': float(pt.split('-')[-1]),
            })
        return self.Result(data)

    @lru_cache
    def ranklist(self, top_100=False, country=None, university=None):
        '''
        Retrieves the current ranklist.
        Query for top 100 takes precedence over query for country or university.
        Otherwise, country or university can be specified, but not both.

        Default: ranklist of people around you.
        '''

        data = []
        if top_100:
            response = self.get(f'{self.BASE_URL}/ranklist')
            soup = bs(response.content, features='lxml')
            try:
                table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
            except:
                return self.Result([])
            if not table:
                return self.Result([])
            headers = [re.findall(r'[A-Za-z]+', h.text)[0] for h in table.find_all('th')]
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                columns_text = [column.text.strip() for column in columns]
                columns_url = [column.find_all('a') for column in columns]

                rank = int(columns_text[0])
                name = columns_text[1]
                pts = float(columns_text[-1])
                name_urls = columns_url[1]
                username = name_urls[0].get('href').split('/')[-1] # guaranteed to exist

                if 'Subdivision' in headers:
                    subdivision = columns_text[2]
                    subdivision_urls = columns_url[2]
                    subdivision_code = subdivision_urls[0].get('href').split('/')[-1] if subdivision_urls else None
                else:
                    subdivision = None

                if 'University' in headers:
                    university = columns_text[-2]
                    university_urls = columns_url[-2]
                    university_code = university_urls[0].get('href').split('/')[-1] if university_urls else None
                else:
                    university = None

                data.append({
                    'rank': rank,
                    'name': name,
                    'username': username,
                    'points': pts,
                    'country_code': country_code if country else None,
                    'country': country,
                    'subdivision_code': subdivision_code if subdivision else None,
                    'subdivision': subdivision if subdivision else None,
                    'university_code': university_code if university else None,
                    'university': university if university else None
                })
        else:
            assert country == None or university == None, 'Both of country and university cannot be given at the same time!'

            if country == university == None:
                soup = self.get_homepage()
                try:
                    table = soup.find_all('table', class_='table2 report_grid-problems_table')[1]
                except:
                    return self.Result([])
                if not table:
                    return self.Result([])
                for row in table.tbody.find_all('tr'):
                    columns = row.find_all('td')
                    rank, name, pts, *_ = [column.text.strip() for column in columns]
                    rank = int(rank) if rank.isdigit() else None
                    pts = float(re.findall(r'[\d\.]+', pts)[0])
                    findall = columns[1].find_all('a')

                    new_data = {
                        'rank': rank,
                        'name': name,
                        'points': pts,
                        'country': None,
                        'university': None
                    }

                    for urlsplit, title in [(column.get('href').split('/'), column.get('title')) for column in findall]:
                        assert sum(x in urlsplit for x in ['users', 'universities', 'countries']) == 1, 'Only one field should be present'
                        if 'users' in urlsplit:
                            new_data['username'] = urlsplit[-1] # guaranteed to exist
                        elif 'universities' in urlsplit:
                            new_data['university_code'] = urlsplit[-1]
                            new_data['university'] = title
                        elif 'countries' in urlsplit:
                            new_data['country_code'] = urlsplit[-1]
                            new_data['country'] = title
                    data.append(new_data)
            elif country != None:
                country_code = guess_id(country, COUNTRIES)
                response = self.get(f'{self.BASE_URL}/countries/{country_code}')
                soup = bs(response.content, features='lxml')
                try:
                    table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
                except:
                    return self.Result([])
                if not table:
                    return self.Result([])
                headers = [re.findall(r'[A-Za-z]+', h.text)[0] for h in table.find_all('th')]
                for row in table.tbody.find_all('tr'):
                    columns = row.find_all('td')
                    columns_text = [column.text.strip() for column in columns]
                    columns_url = [column.find_all('a') for column in columns]

                    rank = int(columns_text[0])
                    name = columns_text[1]
                    pts = float(columns_text[-1])
                    name_urls = columns_url[1]
                    username = name_urls[0].get('href').split('/')[-1] # guaranteed to exist

                    if 'Subdivision' in headers:
                        subdivision = columns_text[2]
                        subdivision_urls = columns_url[2]
                        subdivision_code = subdivision_urls[0].get('href').split('/')[-1] if subdivision_urls else None
                    else:
                        subdivision = None

                    if 'University' in headers:
                        university = columns_text[-2]
                        university_urls = columns_url[-2]
                        university_code = university_urls[0].get('href').split('/')[-1] if university_urls else None
                    else:
                        university = None

                    data.append({
                        'rank': rank,
                        'name': name,
                        'username': username,
                        'points': pts,
                        'country_code': country_code,
                        'country': COUNTRIES[country_code],
                        'subdivision_code': subdivision_code if subdivision else None,
                        'subdivision': subdivision if subdivision else None,
                        'university_code': university_code if university else None,
                        'university': university if university else None
                    })
            else:
                university_code = guess_id(university, UNIVERSITIES)
                response = self.get(f'{self.BASE_URL}/universities/{university_code}')
                soup = bs(response.content, features='lxml')
                table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
                if not table:
                    return self.Result([])
                headers = [re.findall(r'[A-Za-z]+', h.text)[0] for h in table.find_all('th')]
                for row in table.tbody.find_all('tr'):
                    columns = row.find_all('td')
                    columns_text = [column.text.strip() for column in columns]
                    columns_url = [column.find_all('a') for column in columns]

                    rank = int(columns_text[0])
                    name = columns_text[1]
                    pts = float(columns_text[-1])
                    name_urls = columns_url[1]
                    username = name_urls[0].get('href').split('/')[-1] # guaranteed to exist

                    if 'Country' in headers:
                        country = columns_text[2]
                        country_urls = columns_url[2]
                        country_code = country_urls[0].get('href').split('/')[-1] if country_urls else None
                    else:
                        country = None

                    if 'Subdivision' in headers:
                        subdivision = columns_text[-2]
                        subdivision_urls = columns_url[-2]
                        subdivision_code = subdivision_urls[0].get('href').split('/')[-1] if subdivision_urls else None
                    else:
                        subdivision = None

                    data.append({
                        'rank': rank,
                        'name': name,
                        'username': username,
                        'points': pts,
                        'country_code': country_code if country else None,
                        'country': country if country else None,
                        'subdivision_code': subdivision_code if subdivision else None,
                        'subdivision': subdivision if subdivision else None,
                        'university_code': university_code,
                        'university': UNIVERSITIES[university_code]
                    })
        return self.Result(data)

    @lru_cache
    def problem_authors(self):
        '''
        Lists down all problem authors alongside with the number of problems one has
            authored as well as the average difficulty.
        '''

        response = self.get(f'{self.BASE_URL}/problem-authors')
        try:
            soup = bs(response.content, features='lxml')
        except:
            return self.Result([])
        table = soup.find('table', class_='table2')
        if not table:
            return self.Result([])
        data = []
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]
            name = columns_text[0].strip()
            link = f'{self.BASE_URL}{columns_url[0][0].get("href")}'
            num_problems = int(columns_text[1])
            try:
                difficulty = float(re.findall('[\d\.]+', columns_text[2])[-1])
            except:
                difficulty = None
            try:
                category = re.findall('[A-Za-z]+', columns_text[2])[0]
            except:
                category = 'N/A'
            data.append({
                'name': name,
                'problems': num_problems,
                'avg_difficulty': difficulty,
                'avg_category': category,
                'link': link
            })
        return self.Result(data)
    
    @lru_cache
    def problem_sources(self):
        '''
        Lists down all problem sources alongside with the number of problems one comes from
            as well as the average difficulty.
        '''

        response = self.get(f'{self.BASE_URL}/problem-sources')
        try:
            soup = bs(response.content, features='lxml')
        except:
            return self.Result([])
        table = soup.find('table', class_='table2')
        if not table:
            return self.Result([])
        data = []
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            columns_text = [column.text.strip() for column in columns]
            columns_url = [column.find_all('a') for column in columns]
            name = columns_text[0].strip()
            link = f'{self.BASE_URL}{columns_url[0][0].get("href")}'
            num_problems = int(columns_text[1])
            try:
                difficulty = float(re.findall('[\d\.]+', columns_text[2])[-1])
            except:
                difficulty = None
            try:
                category = re.findall('[A-Za-z]+', columns_text[2])[0]
            except:
                category = 'N/A'
            data.append({
                'name': name,
                'problems': num_problems,
                'avg_difficulty': difficulty,
                'avg_category': category,
                'link': link
            })
        return self.Result(data)

class NUSKattis(Kattis):
    def __init__(self, user, password=None):
        print('Logging in to NUS Kattis...', flush=True)
        self.set_base_url('https://nus.kattis.com')
        super().__init__(user, password)
        response = self.get(self.get_base_url())
        self.set_homepage(bs(response.content, features='lxml'))

    @lru_cache
    def courses(self):
        '''
        Lists down only the current courses offered and the courses with recently ended offerings in NUS Kattis.
        It does not list all existing courses in NUS Kattis.
        '''

        tables = self.get_homepage().find_all('table', class_='table2')
        if not tables:
            return self.Result([])
        data = []
        for table in tables:
            for row in table.find_all('tr'):
                columns = row.find_all('td')
                columns_text = [truncate(column.text.strip()) for column in columns]
                columns_url = [column.find('a') for column in columns]
                if columns_text:
                    href = columns_url[0].get('href')
                    data.append({
                        'name': columns_text[0],
                        'url': self.get_base_url() + href,
                        'course_id': href.split('/')[-1]
                    })
        return self.Result(sorted(data, key=lambda r: r['course_id']))

    @lru_cache
    def offerings(self, course_id):
        '''
        Lists down all offerings within a specific NUS Kattis course.
        '''

        response = self.get(f'{self.get_base_url()}/courses/{course_id}')
        soup = bs(response.content, features='lxml')
        table = soup.find('table', class_='table2')
        if not table:
            return self.Result([])
        data = []
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            try:
                name, end_date = [truncate(column.text.strip()) for column in columns]
                link, _ = [column.find('a') for column in columns]
                data.append({
                    'name': name,
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
        '''

        if course_id == None:
            # try to guess
            for cid in self.courses().to_df().course_id:
                if offering_id in [*self.offerings(cid).to_df().name]:
                    course_id = cid
                    break
            assert course_id != None, 'Cannot guess course ID automatically, please provide one'
            print('Guessed course ID:', course_id, flush=True)
        response = self.get(f'{self.get_base_url()}/courses/{course_id}/{offering_id}')
        soup = bs(response.content, features='lxml')
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
                        name, status = truncate(asg.text.strip()).split('\n')
                        status = status.replace('(', '').replace(')', '').strip()
                        link = self.get_base_url() + asg.find('a').get('href')
                        aid = link.split('/')[-1]
                        pids = []
                        toggle = True
                    else:
                        pids.append(asg.find('a').get('href').split('/')[-1])
                if toggle:
                    data.append({
                        'id': aid,
                        'name': name,
                        'status': status,
                        'link': link,
                        'problems': ','.join(pids)
                    })
        return self.Result(data)
