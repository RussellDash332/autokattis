from autokattis import Kattis, OpenKattis
from env import USER, PASSWORD
from utils import test

kt = Kattis(USER, PASSWORD)
kt = OpenKattis(USER, PASSWORD)

test('open_problems_solved_fdm',               kt.problems,               {})
test('open_problems_solved_ldm',               kt.problems,               {'low_detail_mode': True})
test('open_problems_all_fdm',                  kt.problems,               {'show_tried': True, 'show_untried': True})
test('open_problems_all_ldm',                  kt.problems,               {'show_tried': True, 'show_untried': True, 'low_detail_mode': True})

test('open_plot_problems_solved_nofile',       kt.plot_problems,          {})
test('open_plot_problems_solved_file',         kt.plot_problems,          {'filepath': 'plot1.png'})
test('open_plot_problems_all_file',            kt.plot_problems,          {'filepath': 'plot2.png', 'show_tried': True, 'show_untried': True})

test('open_problem_single_nodownload',         kt.problem,                {'problem_ids': '2048'})
test('open_problem_single_download',           kt.problem,                {'problem_ids': '2048', 'download_files': True})
test('open_problem_partial_scoring',           kt.problem,                {'problem_ids': 'golf'})
test('open_problem_multiple_nodownload',       kt.problem,                {'problem_ids': ['2048', 'abinitio', 'teque']})
test('open_problem_multiple_download',         kt.problem,                {'problem_ids': {'2048', 'abinitio', 'teque'}, 'download_files': True})
test('open_problem_invalid',                   kt.problem,                {'problem_ids': ('@?@?', 'ABC')})

test('open_achievements',                      kt.achievements,           {})

test('open_stats_all',                         kt.stats,                  {})
test('open_stats_single',                      kt.stats,                  {'languages': 'C++'})
test('open_stats_multiple',                    kt.stats,                  {'languages': ['C++', 'Python 3']})
test('open_stats_invalid',                     kt.stats,                  {'languages': ('@?@?', 'ABC')})

test('open_suggest',                           kt.suggest,                {})

test('open_user_ranklist',                     kt.user_ranklist,          {})

test('open_country_ranklist_top100',           kt.country_ranklist,       {})
test('open_country_ranklist_specific_1',       kt.country_ranklist,       {'value': 'SGP'})
test('open_country_ranklist_specific_2',       kt.country_ranklist,       {'value': 'Singapore'})
test('open_country_ranklist_specific_3',       kt.country_ranklist,       {'value': 'ISL'})

test('open_affiliation_ranklist_top100',       kt.affiliation_ranklist,   {})
test('open_affiliation_ranklist_specific_1',   kt.affiliation_ranklist,   {'value': 'nus.edu.sg'})
test('open_affiliation_ranklist_specific_2',   kt.affiliation_ranklist,   {'value': 'National University of Singapore'})
test('open_affiliation_ranklist_specific_3',   kt.affiliation_ranklist,   {'value': 'ru.is'})

test('open_challenge_ranklist',                kt.challenge_ranklist,     {})

test('open_ranklist',                          kt.ranklist,               {})

test('open_problem_authors',                   kt.problem_authors,        {})

test('open_problem_sources',                   kt.problem_sources,        {})
