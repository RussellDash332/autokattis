import re
import requests

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
        self.homepage = response.text
        print(response.status_code)

ks = KattisSession(USER, PASSWORD)