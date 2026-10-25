from autokattis import OpenKattis
from env import PASSWORD, USER
from utils import (
    assert_empty,
    assert_equal,
    check_problem_details,
    check_rank_records,
    check_records,
    report_failures,
    test_case,
    TEST_RESULTS,
)

kt = OpenKattis(USER, PASSWORD)
problem_names = {}

check_problem_listing = check_records(
    required_fields=('id', 'name', 'link'),
    nonempty_fields=('id', 'name', 'link'),
)
check_achievements = check_records(
    required_fields=('id', 'name', 'achievement', 'link'),
    nonempty_fields=('id', 'name', 'achievement', 'link'),
)
check_suggestions = check_records(
    required_fields=('pid', 'difficulty', 'name', 'link', 'min', 'max'),
    nonempty_fields=('pid', 'name', 'link', 'min', 'max'),
)

check_stats = check_records(
    required_fields=('id', 'name', 'language', 'link'),
    nonempty_fields=('id', 'name', 'language', 'link'),
)
check_problem_aggregates = check_records(
    required_fields=('name', 'problems', 'num_solved', 'avg_difficulty', 'avg_category', 'link'),
    nonempty_fields=('name', 'link'),
)

def check_all_problems(records):
    check_problem_listing(records=records)
    problem_names.update({problem['id']: problem['name'] for problem in records})

def check_open_problem_details(expected_ids, required_file_ids=()):
    def check(records):
        expected_names = {
            problem_id: problem_names[problem_id]
            for problem_id in expected_ids
            if problem_id in problem_names
        }
        check_problem_details(
            expected_ids=expected_ids,
            additional_fields=(),
            expected_names=expected_names or None,
            required_file_ids=required_file_ids,
        )(records=records)
    return check

def lookup_equality_result(first_test, second_test):
    return assert_equal(
        actual=TEST_RESULTS.get(first_test),
        expected=TEST_RESULTS.get(second_test),
        description='Ranklist lookups',
    )

def check_country_subdivisions(country_code, country_name, required_fields, nonempty_fields):
    def check(records):
        check_rank_records(
            required_fields=required_fields,
            nonempty_fields=nonempty_fields,
        )(records=records)
        assert all(
            record['country_code'] == country_code
            and record['country'] == country_name
            for record in records
        )
        assert any(
            record['subdivision_code'] and record['subdivision']
            for record in records
        ), 'Expected at least one ranklist entry with subdivision data'

    return check

@test_case(check=check_problem_listing)
def test_open_01_problems_solved_fdm():
    return kt.problems()

@test_case(check=check_all_problems)
def test_open_02_problems_all_fdm():
    return kt.problems(show_tried=True, show_untried=True)

@test_case(check=check_problem_listing)
def test_open_03_problems_ldm():
    return kt.problems(low_detail_mode=True)

@test_case()
def test_open_04_plot_problems_solved_nofile():
    return kt.plot_problems()

@test_case()
def test_open_05_plot_problems_solved_file():
    return kt.plot_problems(filepath='plot1.png')

@test_case()
def test_open_06_plot_problems_all_file():
    return kt.plot_problems(filepath='plot2.png', show_tried=True, show_untried=True)

@test_case(check=check_open_problem_details(expected_ids=['2048']))
def test_open_07_problem_normal_single():
    return kt.problem(problem_ids='2048')

@test_case(check=check_open_problem_details(expected_ids=('2048', 'abinitio', 'teque', 'takeonmeme', 'monkeybets', 'closestpair1', 'closestpair2')))
def test_open_08_problem_normal_multiple():
    return kt.problem(problem_ids=('2048', 'abinitio', 'teque', 'takeonmeme', 'monkeybets', 'closestpair1', 'closestpair2'))

@test_case(check=check_open_problem_details(expected_ids=['ikea']))
def test_open_09_problem_partial_single():
    return kt.problem(problem_ids='ikea')

@test_case(check=check_open_problem_details(expected_ids=('ikea', 'laviner', 'lavinerhard', 'lavinersuperhard')))
def test_open_10_problem_partial_multiple():
    return kt.problem(problem_ids=('ikea', 'laviner', 'lavinerhard', 'lavinersuperhard'))

@test_case(check=check_open_problem_details(expected_ids=['guess']))
def test_open_11_problem_interactive_single():
    return kt.problem(problem_ids='guess')

@test_case(check=check_open_problem_details(expected_ids=('guess', 'mysystem', 'uuu', 'harmoniousscarf')))
def test_open_12_problem_interactive_multiple():
    return kt.problem(problem_ids=('guess', 'mysystem', 'uuu', 'harmoniousscarf'))

@test_case(check=check_open_problem_details(expected_ids=['dialhomedevice'], required_file_ids=('dialhomedevice',)))
def test_open_13_problem_attachments_single():
    return kt.problem(problem_ids='dialhomedevice', download_files=True)

@test_case(check=check_open_problem_details(expected_ids=('dialhomedevice', 'darkride'), required_file_ids=('dialhomedevice', 'darkride')))
def test_open_14_problem_attachments_multiple():
    return kt.problem(problem_ids=('dialhomedevice', 'darkride'), download_files=True)

@test_case(check=assert_empty)
def test_open_15_problem_invalid():
    return kt.problem(problem_ids=('@?@?',))

@test_case(check=check_achievements)
def test_open_16_achievements():
    return kt.achievements()

@test_case(check=check_suggestions)
def test_open_17_suggest():
    return kt.suggest()

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points'), nonempty_fields=('name', 'username', 'points')))
def test_open_18_user_ranklist():
    return kt.user_ranklist()

@test_case(check=check_rank_records(required_fields=('rank', 'country', 'country_code', 'users', 'affiliations', 'points'), nonempty_fields=('country', 'country_code', 'users', 'affiliations', 'points')))
def test_open_19_country_ranklist_top100():
    return kt.country_ranklist()

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country'), nonempty_fields=('name', 'username', 'points')))
def test_open_20_country_ranklist_1():
    return kt.country_ranklist(value='SGP')

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country'), nonempty_fields=('name', 'username', 'points')))
def test_open_21_country_ranklist_2():
    return kt.country_ranklist(value='Singapore')

@test_case()
def test_open_22_country_ranklist_3():
    return lookup_equality_result(
        first_test='test_open_20_country_ranklist_1',
        second_test='test_open_21_country_ranklist_2',
    )

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country'), nonempty_fields=('name', 'username', 'points')))
def test_open_23_country_ranklist_4():
    return kt.country_ranklist(value='ISL')

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country'), nonempty_fields=('name', 'username', 'points')))
def test_open_24_country_ranklist_5():
    return kt.country_ranklist(value='Iceland')

@test_case()
def test_open_25_country_ranklist_6():
    return lookup_equality_result(
        first_test='test_open_23_country_ranklist_4',
        second_test='test_open_24_country_ranklist_5',
    )

@test_case(check=check_country_subdivisions(country_code='IDN', country_name='Indonesia', required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'subdivision_code', 'subdivision', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_26_country_ranklist_7():
    return kt.country_ranklist(value='IDN')

@test_case(check=check_country_subdivisions(country_code='IDN', country_name='Indonesia', required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'subdivision_code', 'subdivision', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_27_country_ranklist_8():
    return kt.country_ranklist(value='Indonesia')

@test_case()
def test_open_28_country_ranklist_9():
    return lookup_equality_result(
        first_test='test_open_26_country_ranklist_7',
        second_test='test_open_27_country_ranklist_8',
    )

@test_case(check=check_rank_records(required_fields=('rank', 'affiliation', 'affiliation_code', 'country', 'country_code', 'subdivision', 'users', 'points'), nonempty_fields=('affiliation', 'affiliation_code', 'users', 'points')))
def test_open_29_affiliation_ranklist_top100():
    return kt.affiliation_ranklist()

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_30_affiliation_ranklist_1():
    return kt.affiliation_ranklist(value='nus.edu.sg')

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_31_affiliation_ranklist_2():
    return kt.affiliation_ranklist(value='National University of Singapore')

@test_case()
def test_open_32_affiliation_ranklist_3():
    return lookup_equality_result(
        first_test='test_open_30_affiliation_ranklist_1',
        second_test='test_open_31_affiliation_ranklist_2',
    )

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_33_affiliation_ranklist_4():
    return kt.affiliation_ranklist(value='ru.is')

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'points', 'country_code', 'country', 'affiliation_code', 'affiliation'), nonempty_fields=('name', 'username', 'points')))
def test_open_34_affiliation_ranklist_5():
    return kt.affiliation_ranklist(value='Reykjavík University')

@test_case()
def test_open_35_affiliation_ranklist_6():
    return lookup_equality_result(
        first_test='test_open_33_affiliation_ranklist_4',
        second_test='test_open_34_affiliation_ranklist_5',
    )

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'username', 'score'), nonempty_fields=('name', 'username', 'score')))
def test_open_36_challenge_ranklist():
    return kt.challenge_ranklist()

@test_case(check=check_rank_records(required_fields=('rank', 'name', 'points', 'country', 'affiliation', 'username'), nonempty_fields=('name', 'username', 'points')))
def test_open_37_ranklist():
    return kt.ranklist()

@test_case(check=check_problem_aggregates)
def test_open_38_problem_authors():
    return kt.problem_authors()

@test_case(check=check_problem_aggregates)
def test_open_39_problem_sources():
    return kt.problem_sources()

@test_case(check=check_stats)
def test_open_40_stats_single():
    return kt.stats(languages='Bash')

@test_case(check=check_stats)
def test_open_41_stats_multiple():
    return kt.stats(languages=['C++', 'Bash'])

@test_case(check=assert_empty)
def test_open_42_stats_invalid():
    return kt.stats(languages=('@?@?', 'ABC'))

@test_case(check=check_stats)
def test_open_43_stats_all():
    return kt.stats() # might take a while since it's every submission of yours, ever

tests = [
    test_open_01_problems_solved_fdm,
    test_open_02_problems_all_fdm,
    test_open_03_problems_ldm,
    test_open_04_plot_problems_solved_nofile,
    test_open_05_plot_problems_solved_file,
    test_open_06_plot_problems_all_file,
    test_open_07_problem_normal_single,
    test_open_08_problem_normal_multiple,
    test_open_09_problem_partial_single,
    test_open_10_problem_partial_multiple,
    test_open_11_problem_interactive_single,
    test_open_12_problem_interactive_multiple,
    test_open_13_problem_attachments_single,
    test_open_14_problem_attachments_multiple,
    test_open_15_problem_invalid,
    test_open_16_achievements,
    test_open_17_suggest,
    test_open_18_user_ranklist,
    test_open_19_country_ranklist_top100,
    test_open_20_country_ranklist_1,
    test_open_21_country_ranklist_2,
    test_open_22_country_ranklist_3,
    test_open_23_country_ranklist_4,
    test_open_24_country_ranklist_5,
    test_open_25_country_ranklist_6,
    test_open_26_country_ranklist_7,
    test_open_27_country_ranklist_8,
    test_open_28_country_ranklist_9,
    test_open_29_affiliation_ranklist_top100,
    test_open_30_affiliation_ranklist_1,
    test_open_31_affiliation_ranklist_2,
    test_open_32_affiliation_ranklist_3,
    test_open_33_affiliation_ranklist_4,
    test_open_34_affiliation_ranklist_5,
    test_open_35_affiliation_ranklist_6,
    test_open_36_challenge_ranklist,
    test_open_37_ranklist,
    test_open_38_problem_authors,
    test_open_39_problem_sources,
    test_open_40_stats_single,
    test_open_41_stats_multiple,
    test_open_42_stats_invalid,
    test_open_43_stats_all,
]

for test_function in tests:
    test_function()

report_failures()
