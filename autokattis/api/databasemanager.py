import json

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
        soup = user.get_soup_response(f'{user.get_base_url()}/ranklist/countries')
        for script in soup.find_all('script', {'id': 'country_select_data'}):
            for country in json.loads(script.text):
                _, cat, code = country['url'].replace('\\', '').split('/')
                name = country['text'].encode().decode('unicode_escape')
                if cat == 'countries': self.COUNTRIES[code] = name
        print(f'[database] Listed all {len(self.COUNTRIES)} available countries!', flush=True)

        self.AFFILIATIONS = {}
        soup = user.get_soup_response(f'{user.get_base_url()}/ranklist/affiliations')
        for script in soup.find_all('script', {'id': 'affiliation_select_data'}):
            for affiliation in json.loads(script.text):
                _, cat, code = affiliation['url'].replace('\\', '').split('/')
                name = affiliation['text'].encode().decode('unicode_escape')
                if cat == 'affiliation': self.AFFILIATIONS[code] = name
        print(f'[database] Listed all {len(self.AFFILIATIONS)} available affiliations!', flush=True)

    def get_languages(self):
        return self.LANGUAGES

    def get_countries(self):
        return self.COUNTRIES

    def get_affiliations(self):
        return self.AFFILIATIONS
