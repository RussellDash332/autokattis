from autokattis import NUSKattis
from env import USER, PASSWORD

kt = NUSKattis(USER, PASSWORD)

print('=== TEST PROBLEMS (DEFAULT) ===')
ret = kt.problems()                                 # problems you have solved so far
print(df:=ret.to_df())
df.to_csv('test_nus_problems_default.csv', index=False)

print('=== TEST PROBLEMS (NO PARTIAL) ===')
ret = kt.problems(show_partial=False)               # exclude partial submissions
print(df:=ret.to_df())
df.to_csv('test_nus_problems_no_partial.csv', index=False)

print('=== TEST PROBLEMS (ALL PROBLEMS) ===')
ret = kt.problems(*[True]*4)                        # literally all problems on Kattis
print(df:=ret.to_df())
df.to_csv('test_nus_problems_all.csv', index=False)

print('=== TEST LIST UNSOLVED ===')
ret = kt.list_unsolved()                            # let's grind!
print(df:=ret.to_df())
df.to_csv('test_nus_list_unsolved.csv', index=False)

print('=== TEST PLOT PROBLEMS (DEFAULT) ===')
ret = kt.plot_problems()                            # plot the points distribution
print('Done!')

print('=== TEST PLOT PROBLEMS (TO FILEPATH) ===')
ret = kt.plot_problems(filepath='plot.png')         # save to a filepath
print('Done!')

print('=== TEST PLOT PROBLEMS (NO PARTIAL) ===')
ret = kt.plot_problems(show_partial=False)          # plot fully solved submissions
print('Done!')

print('=== TEST PROBLEM (SINGLE) ===')
ret = kt.problem('2048')                            # fetch info about a problem
print(df:=ret.to_df())
df.to_csv('test_nus_problem_single.csv', index=False)

print('=== TEST PROBLEM (MULTIPLE) ===')
ret = kt.problem('2048', 'abinitio', 'dasort')      # fetch multiple in one
print(df:=ret.to_df())
df.to_csv('test_nus_problem_multiple.csv', index=False)

print('=== TEST STATS (DEFAULT, ALL) ===')
ret = kt.stats()                                    # your best submission for each problem
print(df:=ret.to_df())
df.to_csv('test_nus_stats_default_all.csv', index=False)

print('=== TEST STATS (SINGLE) ===')
ret = kt.stats('Java')                              # all your Java submissions
print(df:=ret.to_df())
df.to_csv('test_nus_stats_single.csv', index=False)

print('=== TEST STATS (MULTIPLE) ===')
ret = kt.stats('Python3', 'Cpp')                    # multiple languages
print(df:=ret.to_df())
df.to_csv('test_nus_stats_multiple.csv', index=False)

print('=== TEST SUGGEST ===')
ret = kt.suggest()                                  # what's the next problem for me?
print(df:=ret.to_df())
df.to_csv('test_nus_suggest.csv', index=False)

print('=== TEST RANKLIST (DEFAULT) ===')
ret = kt.ranklist()                                               # people around you
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_default.csv', index=False)

print('=== TEST RANKLIST (COUNTRY) ===')
ret = kt.ranklist(country='Singapore')                            # country leaderboard
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_country_name.csv', index=False)

print('=== TEST RANKLIST (ALPHA-3) ===')
ret = kt.ranklist(country='SGP')                                  # use alpha-3 code instead
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_country_alpha3.csv', index=False)

print('=== TEST RANKLIST (UNIVERSITY) ===')
ret = kt.ranklist(university='National University of Singapore')  # university leaderboard
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_university_name.csv', index=False)

print('=== TEST RANKLIST (DOMAIN) ===')
ret = kt.ranklist(university='nus.edu.sg')                        # use university domain instead
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_university_domain.csv', index=False)
