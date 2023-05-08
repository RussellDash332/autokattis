import math
import matplotlib.pyplot as plt
import pandas as pd
import re
import requests
import seaborn as sns
import warnings

from bs4 import BeautifulSoup as bs
from database import LANGUAGES, COUNTRIES, UNIVERSITIES
from env import USER, PASSWORD
from thefuzz import fuzz

warnings.warn = lambda *args, **kwargs: None # suppress warnings

def guess_id(guess, data):
    if guess in data: return guess
    reverse_mapping = {v:k for k,v in data.items()}
    if guess in reverse_mapping: return reverse_mapping[guess]

    # Use fuzzy search
    candidates = {**data, **reverse_mapping}
    best = max(candidates, key=lambda c: (fuzz.ratio(guess, c), fuzz.partial_ratio(guess, c)))
    if best in data: return best
    elif best in reverse_mapping: return reverse_mapping[best]
    raise Exception(f'Invalid ID provided! ({guess})')

class KattisSession(requests.Session):
    def __init__(self, user, password):
        '''
        A local Kattis session.
        Takes in a user (email or username) and a password.
        '''

        super().__init__()
        self.user, self.password = user, password
        
        # Get CSRF token
        response = self.get('https://open.kattis.com/login/email')
        regex_result = re.findall(r'value="(\d+)"', response.text)
        assert len(regex_result) == 1, f'Regex found several possible CSRF tokens, {regex_result}'
        self.csrf_token = regex_result[0]

        # Get EduSite cookie + homepage
        data = {
            'csrf_token': self.csrf_token,
            'user': self.user,
            'password': self.password
        }
        response = self.post('https://open.kattis.com/login/email', data=data)
        assert response.ok, 'Cannot login to Kattis'
        print('Logged in to Kattis!', flush=True)

        self.homepage = response.text
        regex_result = re.findall(r'/users/([^/]+)/settings', self.homepage)
        assert len(regex_result) == 1, f'Regex found several possible usernames, {regex_result}'
        self.user = regex_result[0]

    def problems(self, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Gets all Kattis problems based on some filters.
        Returns a JSON-like structure with these fields:
            name, fastest, shortest, total, acc, difficulty, category, link

        Default: all solved and partially solved problems.
        '''

        has_content = True
        params = {
            'page': 0,
            'show_solved': ['off', 'on'][show_solved],
            'show_partial': ['off', 'on'][show_partial],
            'show_tried': ['off', 'on'][show_tried],
            'show_untried': ['off', 'on'][show_untried]
        }
        data = []
        while has_content:
            has_content = False
            response = self.get('https://open.kattis.com/problems', params=params)
            soup = bs(response.content, features='lxml')
            table = soup.find('table', class_='table2')
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    has_content = True
                    link = f"https://open.kattis.com{columns[0].find('a').get('href')}"
                    name = columns[0].text
                    fastest = float(columns[2].text)
                    shortest = int(columns[3].text)
                    total = int(columns[4].text)
                    acc = int(columns[5].text)
                    difficulty = float(re.findall('[\d\.]+', columns[7].text)[-1])
                        # [0] instead of [-1] if we want to take min instead of max
                        # for example:
                        # - difficulty 9.1-9.6 -> [9.1, 9.6]
                        # - difficulty 5.0 -> [5.0]
                    category = re.findall('[A-Za-z]+', columns[7].text)[0]
                    data.append({
                        'name': name,
                        'fastest': fastest,
                        'shortest': shortest,
                        'total': total,
                        'acc': acc,
                        'difficulty': difficulty,
                        'category': category,
                        'link': link
                    })
            params['page'] += 1
        return data

    def plot_problems(self, filepath=None, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Plots the histogram of Kattis problems to a specified filepath.

        Default: plots all solved and partially solved problems without saving it to any file.
        '''

        df = pd.DataFrame(self.problems(show_solved, show_partial, show_tried, show_untried))
        hist = sns.histplot(data=df, x='difficulty', hue='category', multiple='stack', binwidth=0.1)
        hist.set(title=f'Solved Kattis Problems ({df.shape[0]})', xlabel='Difficulty')
        plt.xticks([*range(math.floor(min(df.difficulty)), math.ceil(max(df.difficulty))+1)])
        plt.show()
        if filepath != None:
            plt.savefig(filepath)
            print(f'Saved to {filepath}')

    def problem(self, problem_id, *problem_ids):
        '''
        Obtain information about one or more specific problems.
        Returns a JSON-like structure of the problem body text and their metadata.
        '''

        response = self.get(f'https://open.kattis.com/problems/{problem_id}')

        if not response.ok:
            print(f'Ignoring {problem_id}')
            return []

        soup = bs(response.content, features='lxml')
        body = soup.find('div', class_='problembody')
        data = {'id': problem_id, 'text': body.text.strip(), 'metadata': {}}
        meta = data['metadata']
        for div in soup.find_all('div', class_='metadata_list-item'):
            div = div.text.strip().split('\n')
            if div[0] == 'CPU Time limit':
                meta['cpu'] = div[-1].strip()
            elif div[0] == 'Memory limit':
                meta['memory'] = div[-1].strip()
            elif div[0] == 'Difficulty':
                meta['difficulty'] = float(re.findall('[\d\.]+', div[-1])[-1])
                meta['category'] = re.findall('[A-Za-z]+', div[-1])[0]
            elif div[0] == 'Author':
                meta['author'] = div[-1].strip()
            elif div[0] == 'Source':
                meta['source'] = div[-1].strip()
        ret = [data]
        for pid in set(problem_ids) - {problem_id}:
            prob = self.problem(pid)
            if prob: ret.append(prob[0])
        return ret

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
        while has_content:
            has_content = False
            response = self.get(f'https://open.kattis.com/users/{self.user}', params=params)
            soup = bs(response.content, features='lxml')
            table = soup.find('table', class_='table2 report_grid-problems_table double-rows')
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                columns_text = [column.text for column in columns if column.text]
                if columns_text:
                    has_content = True
                    link = f"https://open.kattis.com/submissions/{columns[-1].find('a').get('href').split('/')[-1]}"
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
                            key=lambda x: (x.get('score'), x['test_case_passed'], -float(x['runtime'] if '>' not in x['runtime'] else 1e9))
                        )
            params['page'] += 1
        ret = [{'id': k, **v} for k, v in data.items()]
        for lang in set(languages) - {language}:
            ret.extend(self.stats(lang))
        return ret

    def suggest(self):
        '''
        Retrieves suggested problems based on what you have solved so far.
        Returns a JSON-like structure containing the suggested problems points and its difficulty.
        '''

        soup = bs(self.homepage, features='lxml')
        table = soup.find_all('table', class_='table2 report_grid-problems_table')[0]
        data = []
        for row in table.tbody.find_all('tr'):
            header = row.find('th')
            if header:
                difficulty = header.text
            column = row.find('td')
            pid = column.find('a').get('href').split('/')[-1]
            link = f'https://open.kattis.com/problems/{pid}'
            name, pt = column.text.strip().split('\n')
            pt = pt.strip(' pt')
            data.append({
                'pid': pid, 'difficulty': difficulty, 'name': name, 'link': link,
                'min': float(pt.split('-')[0]), 'max': float(pt.split('-')[-1]),
            })
        return data

    def ranklist(self, country=None, university=None):
        '''
        Retrieves the current ranklist.
        Country or university can be specified, but not both.

        Default: ranklist of people around you.
        '''

        assert country == None or university == None, 'Both of country and university cannot be given at the same time!'

        if country == university == None:
            soup = bs(self.homepage, features='lxml')
            table = soup.find_all('table', class_='table2 report_grid-problems_table')[1]
            data = []
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                rank, name, pts, *_ = [column.text.strip() for column in columns]
                rank = int(rank)
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
                        new_data['university'] = {'code': urlsplit[-1], 'name': title}
                    elif 'countries' in urlsplit:
                        new_data['country'] = {'code': urlsplit[-1], 'name': title}
                data.append(new_data)
        elif country != None:
            country_code = guess_id(country, COUNTRIES)
            response = self.get(f'https://open.kattis.com/countries/{country_code}')
            soup = bs(response.content, features='lxml')
            table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
            if not table: return []
            data = []
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
                    'country': {'code': country_code, 'name': COUNTRIES[country_code]},
                    'subdivision': {'code': subdivision_code, 'name': subdivision} if subdivision else None,
                    'university': {'code': university_code, 'name': university} if university else None
                })
        else:
            university_code = guess_id(university, UNIVERSITIES)
            response = self.get(f'https://open.kattis.com/universities/{university_code}')
            soup = bs(response.content, features='lxml')
            table = soup.find('table', class_='table2 report_grid-problems_table', id='top_users')
            if not table: return []
            data = []
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
                    'university': {'code': university_code, 'name': country_code},
                    'country': {'code': country_code, 'name': country} if country else None,
                    'subdivision': {'code': subdivision_code, 'name': subdivision} if subdivision else None
                })
        return data

if __name__ == '__main__':
    ks = KattisSession(USER, PASSWORD)
