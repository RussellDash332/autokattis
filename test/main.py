import pandas as pd

from autokattis import Kattis
from env import USER, PASSWORD

kt = Kattis(USER, PASSWORD)

for ret in [
    kt.problems(),                              # problems you have solved so far
    kt.problems(show_partial=False),            # exclude partial submissions
    kt.problems(*[True]*4),                     # literally all problems on Kattis
    kt.list_unsolved()                          # let's grind!

    kt.plot_problems(),                         # plot the points distribution
    kt.plot_problems(filepath='plot.png'),      # save to a filepath
    kt.plot_problems(show_partial=False),       # plot fully solved submissions

    kt.problem('2048'),                         # fetch info about a problem
    kt.problem('2048', 'abinitio', 'dasort'),   # fetch multiple in one

    kt.stats(),                 # your best submission for each problem
    kt.stats('Java'),           # all your Java submissions
    kt.stats('Python3', 'Cpp'), # multiple languages

    kt.suggest(),               # what's the next problem for me?

    kt.ranklist(),                                              # people around you
    kt.ranklist(country='Singapore'),                           # country leaderboard
    kt.ranklist(country='SGP'),                                 # use alpha-3 code instead
    kt.ranklist(university='National University of Singapore'), # university leaderboard
    kt.ranklist(university='nus.edu.sg')                        # use university domain instead
]:
    if ret:
        print(pd.DataFrame(ret))
