from functools import wraps
import re
import warnings

from thefuzz import fuzz

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

def truncate_spaces(text):
    return text if (new_text:=text.replace('  ', ' ')) == text else truncate_spaces(new_text)

def replace_double_dash(text, new):
    return type(new)(text.replace('--', str(new)).strip())

def remove_brackets(text):
    return text.replace('(', '').replace(')', '').strip()

def get_last_path(link):
    return link.split('/')[-1].strip()

def suppress_warnings():
    warnings.warn = lambda *args, **kwargs: None

def get_table_headers(table):
    return [re.findall(r'[A-Za-z]+', h.text)[0] for h in table.find_all('th')]

def get_table_rows(table):
    return table.tbody.find_all('tr')

def list_to_tuple(fn):
    @wraps(fn)
    def helper(slf, *args, **kwargs):
        if args:
            return fn(slf, tuple(args[0]), *args[1:], **kwargs) if type(args[0]) in (list, dict, set) else fn(slf, *args, **kwargs)
        elif 'problem_ids' in kwargs:
            val = kwargs['problem_ids']
            del kwargs['problem_ids']
            return fn(slf, problem_ids=tuple(val), *args, **kwargs) if type(val) in (list, dict, set) else fn(slf, problem_ids=val, *args, **kwargs)
        elif 'languages' in kwargs:
            val = kwargs['languages']
            del kwargs['languages']
            return fn(slf, languages=tuple(val), *args, **kwargs) if type(val) in (list, dict, set) else fn(slf, languages=val, *args, **kwargs)
        else:
            return fn(slf, **kwargs)
    return helper
