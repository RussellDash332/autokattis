from collections import Counter
from getpass import getpass
import re

class LoginManager:
    def __init__(self, user):
        self.user = user

    def login(self, username, password, method):
        if method == 'email':
            # Prompt if not given
            if password == None: password = getpass('Enter password: ')

            # Get CSRF token
            response = self.user.new_get(f'{self.user.get_base_url()}/login/email')
            regex_result = re.findall(r'value="(\d+)"', response.text)
            assert len(regex_result) == 1, f'[login] Regex found several possible CSRF tokens, {regex_result}'

            # Get EduSite cookie + homepage
            data = {
                'csrf_token': regex_result[0],
                'user': username,
                'password': password
            }
            response = self.user.new_post(f'{self.user.get_base_url()}/login/email', data=data)
            assert response.url.startswith(self.user.get_base_url()), '[login] Cannot login to Kattis'

            # Reassign username and wrap-up
            self.user.load_homepage()
            names = []
            for a in self.user.get_homepage().find_all('a'):
                href = a.get('href')
                if href:
                    paths = href.split('/')
                    if len(paths) > 2 and paths[1] == 'users': names.append(paths[2])
            ctr = Counter(names)
            assert ctr, '[login] There are issues when logging in to Kattis, please check your username again'
            max_freq = max(ctr.values())
            candidate_usernames = [name for name in ctr if ctr[name] == max_freq]
            print(f'[login] Candidate username(s): {candidate_usernames}', flush=True)
            print(f'[login] Successfully logged in to Kattis as {candidate_usernames[0]}!', flush=True)
            return candidate_usernames[0]
        else:
            # TODO: google? linkedin? github?
            raise NotImplementedError