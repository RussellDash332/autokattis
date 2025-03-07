from autokattis import NUSKattis
from env import USER, PASSWORD
from utils import test

kt = NUSKattis(USER, PASSWORD)

test('nus_01_problems_solved',                  kt.problems,        {})
test('nus_02_problems_all',                     kt.problems,        {'show_solved': False})

test('nus_03_problem_single_nodownload',        kt.problem,         {'problem_ids': 'magicsequence'})
test('nus_04_problem_single_download',          kt.problem,         {'problem_ids': 'magicsequence', 'download_files': True})
test('nus_05_problem_multiple_nodownload',      kt.problem,         {'problem_ids': ['magicsequence', 'racinggame', 'rationalsequence3']})
test('nus_06_problem_multiple_download',        kt.problem,         {'problem_ids': {'magicsequence', 'racinggame', 'rationalsequence3'}, 'download_files': True})
test('nus_07_problem_invalid',                  kt.problem,         {'problem_ids': ('@?@?', 'ABC', 'finalexam')})

test('nus_08_stats_all',                        kt.stats,           {})
test('nus_09_stats_single',                     kt.stats,           {'languages': 'C++'})
test('nus_10_stats_multiple',                   kt.stats,           {'languages': ['C++', 'Python 3']})
test('nus_11_stats_invalid',                    kt.stats,           {'languages': ('@?@?', 'ABC')})

test('nus_12_courses',                          kt.courses,         {})

test('nus_13_offerings_valid_1',                kt.offerings,       {'course_id': 'CS2040'})
test('nus_14_offerings_valid_2',                kt.offerings,       {'course_id': 'CS3233'})
test('nus_15_offerings_invalid',                kt.offerings,       {'course_id': 'idk'})

test('nus_16_assignments_courseid_guessed_1',   kt.assignments,     {'offering_id': 'CS2040_S1_AY2425'})
test('nus_17_assignments_courseid_guessed_2',   kt.assignments,     {'offering_id': 'CS3233_S2_AY2425'})
test('nus_18_assignments_courseid_given',       kt.assignments,     {'offering_id': 'CS3233_S2_AY2223', 'course_id': 'CS3233'})
test('nus_19_assignments_unknown_courseid',     kt.assignments,     {'offering_id': 'xyz'})
test('nus_20_assignments_unknown_offeringid',   kt.assignments,     {'offering_id': 'xyz', 'course_id': 'CS3233'})
