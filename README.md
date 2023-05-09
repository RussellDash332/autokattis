# autokattis

Kattis scraper, updated as of May 2023 after the major UI/UX change.

## Setup

1. Run `pip install -r requirements.txt` to install the Python packages required.
1. Create a new file called `env.py` and add these two lines.

    ```python
    USER = <username>
    PASSWORD = <password>
    ```

    where `<username>` is your Kattis username/email and `<password>` is your Kattis account password. Both should be provided as **Python strings**. See `env.py.example` for example.
1. Run `python main.py`.

## Use Cases

### Login

Construct a `KattisSession` object that takes in the username and the password.

```py
kt = KattisSession('username', 'password')
```

### Problem-specific

```py
kt.problems() # problems you have solved so far
kt.problems(show_partial=False) # exclude partial submissions
kt.problems(*[True]*4) # literally all problems on Kattis

kt.plot_problems() # plot the points distribution
kt.plot_problems(filepath='plot.png') # save to a filepath
kt.plot_problems(show_partial=False) # plot fully solved submissions

kt.problem('2048') # fetch info about a problem
kt.problem('2048', 'abinitio', 'dasort') # fetch multiple in one
```

### User-specific

```py
kt.stats() # your best submission for each problem
kt.stats('Java') # all your Java submissions
kt.stats('Python3', 'Cpp') # multiple languages

kt.suggest() # what's the next problem for me?
```

### Ranklist

```py
kt.ranklist() # people around you
kt.ranklist(country='Singapore') # country leaderboard
kt.ranklist(country='SGP') # use alpha-3 code instead
kt.ranklist(university='National University of Singapore') # university leaderboard
kt.ranklist(university='nus.edu.sg') # use university domain instead
```

## Useful References

- Old UI Kattis API wrapper: https://github.com/terror/kattis-api

    > Most of the work in `autokattis` is heavily inspired and motivated by this repository.

- Kattis official CLI tool: https://github.com/Kattis/kattis-cli

    > Since Kattis has provided an official tool to automate submissions, there won't be such feature in `autokattis`.

## Contributing

asdf