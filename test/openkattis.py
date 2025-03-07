from autokattis import Kattis, OpenKattis
from env import USER, PASSWORD
from utils import test

kt = Kattis(USER, PASSWORD)
kt = OpenKattis(USER, PASSWORD)

test('open_01_problems_solved_fdm',                 kt.problems,                {})
test('open_02_problems_all_fdm',                    kt.problems,                {'show_tried': True, 'show_untried': True})
test('open_03_problems_ldm',                        kt.problems,                {'low_detail_mode': True})

test('open_04_plot_problems_solved_nofile',         kt.plot_problems,           {})
test('open_05_plot_problems_solved_file',           kt.plot_problems,           {'filepath': 'plot1.png'})
test('open_06_plot_problems_all_file',              kt.plot_problems,           {'filepath': 'plot2.png', 'show_tried': True, 'show_untried': True})

test('open_07_problem_single_nodownload',           kt.problem,                 {'problem_ids': '2048'})
test('open_08_problem_single_download',             kt.problem,                 {'problem_ids': '2048', 'download_files': True})
test('open_09_problem_partial_scoring',             kt.problem,                 {'problem_ids': 'golf'})
test('open_10_problem_multiple_nodownload',         kt.problem,                 {'problem_ids': ['2048', 'abinitio', 'teque']})
test('open_11_problem_multiple_download',           kt.problem,                 {'problem_ids': {'2048', 'abinitio', 'teque'}, 'download_files': True})
test('open_12_problem_invalid',                     kt.problem,                 {'problem_ids': ('@?@?', 'ABC')})

test('open_13_achievements',                        kt.achievements,            {})

test('open_14_stats_all',                           kt.stats,                   {})
test('open_15_stats_single',                        kt.stats,                   {'languages': 'C++'})
test('open_16_stats_multiple',                      kt.stats,                   {'languages': ['C++', 'Python 3']})
test('open_17_stats_invalid',                       kt.stats,                   {'languages': ('@?@?', 'ABC')})

test('open_18_suggest',                             kt.suggest,                 {})

test('open_19_user_ranklist',                       kt.user_ranklist,           {})

test('open_20_country_ranklist_top100',             kt.country_ranklist,        {})
test('open_21_country_ranklist_specific_1',         kt.country_ranklist,        {'value': 'SGP'})
test('open_22_country_ranklist_specific_2',         kt.country_ranklist,        {'value': 'Singapore'})
test('open_23_country_ranklist_specific_3',         kt.country_ranklist,        {'value': 'ISL'})

test('open_24_affiliation_ranklist_top100',         kt.affiliation_ranklist,    {})
test('open_25_affiliation_ranklist_specific_1',     kt.affiliation_ranklist,    {'value': 'nus.edu.sg'})
test('open_26_affiliation_ranklist_specific_2',     kt.affiliation_ranklist,    {'value': 'National University of Singapore'})
test('open_27_affiliation_ranklist_specific_3',     kt.affiliation_ranklist,    {'value': 'ru.is'})

test('open_28_challenge_ranklist',                  kt.challenge_ranklist,      {})

test('open_29_ranklist',                            kt.ranklist,                {})

test('open_30_problem_authors',                     kt.problem_authors,         {})

test('open_31_problem_sources',                     kt.problem_sources,         {})
