from autokattis import NUSKattis
from env import USER, PASSWORD
from utils import test

kt = NUSKattis(USER, PASSWORD)

test('nus_problems_solved',                 kt.problems,        {})
test('nus_problems_all',                    kt.problems,        {'show_solved': False})

test('nus_problem_single_nodownload',       kt.problem,         {'problem_ids': 'magicsequence'})
test('nus_problem_single_download',         kt.problem,         {'problem_ids': 'magicsequence', 'download_files': True})
test('nus_problem_multiple_nodownload',     kt.problem,         {'problem_ids': ['magicsequence', 'racinggame', 'rationalsequence3']})
test('nus_problem_multiple_download',       kt.problem,         {'problem_ids': {'magicsequence', 'racinggame', 'rationalsequence3'}, 'download_files': True})
test('nus_problem_invalid',                 kt.problem,         {'problem_ids': ('@?@?', 'ABC', 'finalexam')})

test('nus_stats_all',                       kt.stats,           {})
test('nus_stats_single',                    kt.stats,           {'languages': 'C++'})
test('nus_stats_multiple',                  kt.stats,           {'languages': ['C++', 'Python 3']})
test('nus_stats_invalid',                   kt.stats,           {'languages': ('@?@?', 'ABC')})

test('nus_courses',                         kt.courses,         {})

test('nus_offerings_valid_1',               kt.courses,         {'course_id': 'CS2040'})
test('nus_offerings_valid_2',               kt.courses,         {'course_id': 'CS3233'})
test('nus_offerings_invalid',               kt.courses,         {'course_id': 'idk'})

test('nus_assignments_courseid_guessed',    kt.assignments,     {'offering_id': 'CS3233_S2_AY2223'})
test('nus_assignments_courseid_given',      kt.assignments,     {'offering_id': 'CS3233_S2_AY2223', 'course_id': 'CS3233'})
