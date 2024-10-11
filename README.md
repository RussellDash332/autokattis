# autokattis

Updated Kattis API wrapper as of May 2023 after the major UI/UX change.

## Setup

Simply install it as a Python package.

```sh
$ pip install autokattis
```

## Use Cases

For now, this package supports `OpenKattis` and `NUSKattis`.

### Login

Construct an `OpenKattis` object that takes in the username and the password.

```py
from autokattis import OpenKattis
kt = OpenKattis('username', 'password')
kt = OpenKattis('username') # which will then prompt you for the password
```

where `'username'` is your Kattis username/email and `'password'` is your Kattis account password. **Both should be provided as Python strings.**

Similarly if you want to login to NUS Kattis.

```py
from autokattis import NUSKattis
kt = NUSKattis('username', 'password')
kt = NUSKattis('username')
```

### OpenKattis

> Due to backwards compatibility, you can still use `Kattis` as a shorthand form of `OpenKattis`.

#### Problem-specific

```py
kt.problems()                               # problems you have solved so far
kt.problems(show_partial=False)             # exclude partial submissions
kt.problems(low_detail_mode=False)          # include more data for each problem
kt.problems(*[True]*4)                      # show literally all problems on Open Kattis

kt.plot_problems()                          # plot the points distribution
kt.plot_problems(filepath='plot.png')       # save to a filepath
kt.plot_problems(show_partial=False)        # plot fully solved submissions

kt.problem('2048')                          # fetch info about a problem
kt.problem(['2048', 'abinitio', 'dasort'])  # fetch multiple in one
kt.problem({'2048', 'abinitio', 'dasort'})  # tuples or sets also allowed
kt.problem('2048', download_files=True)     # download files too

kt.stats()                                  # your best submission for each problem
kt.stats('Java')                            # all your Java submissions
kt.stats(('Python3', 'Cpp'))                # multiple languages

kt.suggest()                                # what's the next problem for me?
kt.achievements()                           # do I have any?
kt.problem_authors()                        # list down all problem authors
kt.problem_sources()                        # list down all problem sources
```

#### Ranklist

```py
kt.ranklist()                                                           # people around you

kt.user_ranklist()                                                      # top 100 users in general ladder
kt.challenge_ranklist()                                                 # top 100 users in challenge ladder

kt.country_ranklist()                                                   # top 100 countries
kt.country_ranklist('Singapore')                                        # specific country
kt.country_ranklist('SGP')                                              # use country code instead

kt.university_ranklist()                                                # top 100 universities
kt.university_ranklist(university='National University of Singapore')   # specific university
kt.university_ranklist(university='nus.edu.sg')                         # use university domain instead
```

### NUSKattis

#### Problem-specific

```py
kt.problems()                               # problems you have solved so far, only supports low detail mode
kt.problems(show_solved=False)              # show literally all problems on NUS Kattis

kt.problem('2048')                          # fetch info about a problem
kt.problem(['2048', 'abinitio', 'dasort'])  # fetch multiple in one
kt.problem({'2048', 'abinitio', 'dasort'})  # tuples or sets also allowed
kt.problem('2048', download_files=True)     # download files too

kt.stats()                                  # your best submission for each problem
kt.stats('Java')                            # all your Java submissions
kt.stats(('Python3', 'Cpp'))                # multiple languages
```

#### Course-specific

```py
kt.courses()                                    # current and recently ended courses
kt.offerings('CS3233')                          # course offerings
kt.assignments('CS3233_S2_AY2223')              # offering assignments but course ID not provided
kt.assignments('CS3233_S2_AY2223', 'CS3233')    # offering assignments
```

### Convert to DataFrame

As simple as adding `.to_df()`!

```py
kt.problems().to_df()
kt.ranklist().to_df()
```

### Other Scenarios

Some scenarios you can perform when using `autokattis`:
1. Mapping problem ID with its difficulty
    ```py
    okt = OpenKattis(...)
    df = okt.problems().to_df()
    diff_map = dict(zip(df.id, df.difficulty))
    ```
1. Find the number of questions on every assignment on an NUS course offering
    ```py
    nkt = NUSKattis(...)
    df = nkt.assignments('CS3233_S2_AY2324').to_df()
    df['n_problems'] = df['problems'].apply(lambda x: len(x.split(',')))
    df[['name', 'n_problems']]
    ```
1. Find the average difficulty of every assignment on an NUS course offering
    ```py
    diff_map = ... # see scenario 1

    nkt = NUSKattis(...)
    avg_2dp = lambda x: round(sum(y:=[v for v in x if v != None])/max(len(y), 1), 2)
    df = nkt.assignments('CS3233_S2_AY2324').to_df()
    df['avg_diff'] = df['problems'].apply(lambda x: avg_2dp(map(diff_map.get, x.split(','))))
    df[['name', 'avg_diff']]
    ```
1. Group top 100 users by country
    ```py
    okt = OpenKattis(...)
    okt.user_ranklist().to_df().groupby('country').size()
    ```

### More Information

The docstrings might be a great help if you want to know more about the JSON return values!

```py
from autokattis import OpenKattis
help(OpenKattis)
```

## Testing

The `test` directory is provided within this repository. You are free to test `autokattis` with these anytime.

```sh
>>> python test/openkattis.py
...
>>> python test/nuskattis.py
...
```

## Useful References

- Old UI Kattis API wrapper: https://github.com/terror/kattis-api

    > Most of the work in `autokattis` is heavily inspired and motivated by this repository.

- Kattis official CLI tool: https://github.com/Kattis/kattis-cli

    > Since Kattis has provided an official tool to automate submissions, there won't be such feature in `autokattis`.

## Contributing

Feel free to suggest anything or add on some implementation by simply creating a pull request!