from autokattis import NUSKattis
from env import USER, PASSWORD

kt = NUSKattis(USER, PASSWORD)

print('=== TEST PROBLEMS V2 (DEFAULT) ===')
ret = kt.problems_v2()                              # problems you have solved so far
print(df:=ret.to_df())
df.to_csv('test_nus_problems_v2_default.csv', index=False)

print('=== TEST PROBLEMS V2 (ALL PROBLEMS) ===')
ret = kt.problems_v2(show_non_ac=True)              # literally all problems on Kattis
print(df:=ret.to_df())
df.to_csv('test_nus_problems_v2_all.csv', index=False)

print('=== TEST PROBLEM AUTHORS ===')
ret = kt.problem_authors()                          # list down all problem authors
print(df:=ret.to_df())
df.to_csv('test_nus_problem_authors.csv', index=False)

print('=== TEST PROBLEM SOURCES ===')
ret = kt.problem_sources()                          # list down all problem sources
print(df:=ret.to_df())
df.to_csv('test_nus_problem_sources.csv', index=False)

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

print('=== TEST ACHIEVEMENTS ===')
ret = kt.achievements()                             # do I have any?
print(df:=ret.to_df())
df.to_csv('test_nus_achievements.csv', index=False)

print('=== TEST SUGGEST ===')
ret = kt.suggest()                                  # what's the next problem for me?
print(df:=ret.to_df())
df.to_csv('test_nus_suggest.csv', index=False)

print('=== TEST RANKLIST (DEFAULT) ===')
ret = kt.ranklist()                                               # people around you
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_default.csv', index=False)

print('=== TEST RANKLIST (TOP 100) ===')
ret = kt.ranklist(top_100=True)                                   # show top 100
print(df:=ret.to_df())
df.to_csv('test_nus_ranklist_top100.csv', index=False)

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

print('=== TEST COURSES ===')
ret = kt.courses()                                      # current and recently ended courses
print(df:=ret.to_df())
df.to_csv('test_nus_courses.csv', index=False)

print('=== TEST OFFERINGS (CS3233) ===')
ret = kt.offerings('CS3233')                            # course offerings
print(df:=ret.to_df())
df.to_csv('test_nus_offerings.csv', index=False)

print('=== TEST ASSIGNMENTS (GUESS) ===')
ret = kt.assignments('CS3233_S2_AY2223')                # course assignments but course ID not provided
print(df:=ret.to_df())
df.to_csv('test_nus_assignments_guess.csv', index=False)

print('=== TEST ASSIGNMENTS (MANUAL) ===')
ret = kt.assignments('CS3233_S2_AY2223', 'CS3233')      # course assignments
print(df:=ret.to_df())
df.to_csv('test_nus_assignments_manual.csv', index=False)
