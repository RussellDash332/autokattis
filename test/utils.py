import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TEST_NAMES = set()
def test(title, fn, kwargs, csv=True):
    assert title not in TEST_NAMES
    TEST_NAMES.add(title)

    print(f'[{bcolors.OKBLUE}RUN{bcolors.ENDC}] {fn.__qualname__}:{title}')
    start = time.perf_counter()
    try:
        ret = fn(**kwargs)
        print(df:=ret.to_df())
        if csv: df.to_csv(f'{title}.csv', index=False)
        print(f'Time taken: {round(time.perf_counter()-start, 4)}s')
        print(f'[{bcolors.OKGREEN}OK{bcolors.ENDC}] {fn.__qualname__}:{title}')
    except Exception as e:
        print(f'{type(e).__name__}: {e}')
        print(f'Time taken: {round(time.perf_counter()-start, 4)}s')
        print(f'[{bcolors.FAIL}FAIL{bcolors.ENDC}] {fn.__qualname__}:{title}')