# autokattis

Updated Kattis API wrapper as of May 2023 after the major UI/UX change.

## Setup

Simply install it as a Python package.

```sh
$ pip install autokattis
```

## Use Cases

### Login

Construct a `Kattis` object that takes in the username and the password.

```py
from autokattis import Kattis
kt = Kattis('username', 'password')
kt = Kattis('username') # which will then prompts you for the password
```

where `'username'` is your Kattis username/email and `'password'` is your Kattis account password. **Both should be provided as Python strings.**

Similarly if you want to login to the NUS version of Kattis.

```py
from autokattis import NUSKattis
kt = NUSKattis('username', 'password')
kt = NUSKattis('username')
```

### Problem-specific

```py
kt.problems()                               # problems you have solved so far
kt.problems(show_partial=False)             # exclude partial submissions
kt.problems(*[True]*4)                      # literally all problems on Kattis

kt.list_unsolved()                          # let's grind!

kt.plot_problems()                          # plot the points distribution
kt.plot_problems(filepath='plot.png')       # save to a filepath
kt.plot_problems(show_partial=False)        # plot fully solved submissions

kt.problem('2048')                          # fetch info about a problem
kt.problem('2048', 'abinitio', 'dasort')    # fetch multiple in one

kt.problem_authors()                        # list down all problem authors
kt.problem_sources()                        # list down all problem sources
```

### User-specific

```py
kt.stats()                  # your best submission for each problem
kt.stats('Java')            # all your Java submissions
kt.stats('Python3', 'Cpp')  # multiple languages

kt.achievements()           # do I have any?
kt.suggest()                # what's the next problem for me?
```

### Ranklist

```py
kt.ranklist()                                               # people around you
kt.ranklist(country='Singapore')                            # country leaderboard
kt.ranklist(country='SGP')                                  # use alpha-3 code instead
kt.ranklist(university='National University of Singapore')  # university leaderboard
kt.ranklist(university='nus.edu.sg')                        # use university domain instead
```

### NUS-specific

```py
kt.courses()                                    # current and recently ended courses
kt.offerings('CS3233')                          # course offerings
kt.assignments('CS3233_S2_AY2223')              # course assignments but course ID not provided
kt.assignments('CS3233_S2_AY2223', 'CS3233')    # course assignments
```

### Convert to DataFrame

As simple as this!

```py
kt.problems().to_df()
kt.ranklist().to_df()
```

## Useful References

- Old UI Kattis API wrapper: https://github.com/terror/kattis-api

    > Most of the work in `autokattis` is heavily inspired and motivated by this repository.

- Kattis official CLI tool: https://github.com/Kattis/kattis-cli

    > Since Kattis has provided an official tool to automate submissions, there won't be such feature in `autokattis`.

## Contributing

asdf