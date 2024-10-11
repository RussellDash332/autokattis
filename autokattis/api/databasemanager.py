import re

class DatabaseManager:
    def __init__(self, user):
        self.user = user

        self.LANGUAGES = {}
        soup = self.user.get_soup_response(f'{user.get_base_url()}/users/{user.get_username()}')
        for option in soup.find('select', {'name': 'language'}).find_all('option'):
            val = option.get('value').strip()
            name = option.text.strip()
            if val and name: self.LANGUAGES[val] = name
        for val, name in [*self.LANGUAGES.items()]:
            self.LANGUAGES[name] = self.LANGUAGES[val] = val
        print('[database] Listed all available languages!', flush=True)

        self.COUNTRIES = {}
        self.UNIVERSITIES = {}
        soup = user.get_soup_response(f'{user.get_base_url()}/ranklist')
        for script in soup.find_all('script'):
            for name, code in re.findall('text: "([^"]*)",url: "([^"]*)"', script.text):
                _, cat, code = code.replace('\\', '').split('/')
                name = name.encode().decode('unicode_escape')
                if cat == 'countries': self.COUNTRIES[code] = name
                elif cat == 'universities': self.UNIVERSITIES[code] = name
        print('[database] Listed all available countries!', flush=True)
        print('[database] Listed all available universities!', flush=True)

    def get_languages(self):
        return self.LANGUAGES

    def get_countries(self):
        return self.COUNTRIES

    def get_universities(self):
        return self.UNIVERSITIES
