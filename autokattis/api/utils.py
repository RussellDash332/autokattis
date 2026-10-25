from functools import wraps
import re
import warnings

from thefuzz import fuzz

VERBOSE = True

def set_verbose(verbose):
    global VERBOSE
    VERBOSE = bool(verbose)

def log(*args, **kwargs):
    if VERBOSE: print(*args, **kwargs)

def to_int(value):
    if value is None: return None
    try:
        value = str(value).replace(',', '').strip()
        return None if value in ('', '-', '--') else int(value)
    except (TypeError, ValueError):
        return None

def to_float(value):
    if value is None: return None
    try:
        value = str(value).replace(',', '').strip()
        return None if value in ('', '-', '--') else float(value)
    except (TypeError, ValueError):
        return None

def parse_interval(value, index=-1):
    # Use index=0 instead of index=-1 to select the minimum instead of the maximum.
    # For example:
    # - difficulty 9.1-9.6 -> [9.1, 9.6]
    # - difficulty 5.0 -> [5.0]
    matches = re.findall(r'[\d,.]+', str(value)) if value is not None else []
    values = [parsed for match in matches if (parsed := to_float(match)) is not None]
    return values[index] if values and -len(values) <= index < len(values) else None

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

def normalize_whitespace(text):
    return ' '.join(text.split())

def remove_brackets(text):
    return text.replace('(', '').replace(')', '').strip()

def get_last_path(link):
    return link.split('/')[-1].strip()

def suppress_warnings():
    warnings.warn = lambda *args, **kwargs: None

def get_table_headers(table):
    return [re.findall(r'[A-Za-z]+', h.text)[0] for h in table.find_all('th')]

def get_table_rows(table):
    try: return table.tbody.find_all('tr')
    except: return []

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
