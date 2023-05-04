import math
import matplotlib.pyplot as plt
import pandas as pd
import re
import requests
import seaborn as sns

from bs4 import BeautifulSoup as bs
from env import USER, PASSWORD

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
        self.homepage = response.text

    def problems(self, show_solved=True, show_partial=True, show_tried=False, show_untried=False):
        '''
        Gets all Kattis problems based on some filters.
        Returns a Pandas DataFrame with these columns:
            name, fastest, shortest, total, acc, difficulty, category, link
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
                    data.append([name, fastest, shortest, total, acc, difficulty, category, link])
            params['page'] += 1
        return pd.DataFrame(
            columns=['name', 'fastest', 'shortest', 'total', 'acc', 'difficulty', 'category', 'link'],
            data=data
        )

ks = KattisSession(USER, PASSWORD)
df = ks.problems()
hist = sns.histplot(data=df, x='difficulty', hue='category', multiple='stack', binwidth=0.1)
hist.set(title=f'Solved Kattis Problems ({df.shape[0]})', xlabel='Difficulty')
plt.xticks([*range(math.floor(min(df.difficulty)), math.ceil(max(df.difficulty))+1)])
plt.show()
