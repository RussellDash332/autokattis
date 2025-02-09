from enum import Enum, IntEnum
# StrEnum is not supported for <3.11

class DifficultyColor(Enum):
    EASY = '#39a137'
    MEDIUM = '#ffbe00'
    HARD = '#ff411a'
    N_A = 'gray'

class SubmissionsColumn(IntEnum):
    PLAGIARISM = 0
    SUBMISSION_TIME = 1
    GROUP_TEAM_NAME = 2
    CONTEST_PROBLEM_NAME = 3
    STATUS = 4
    CPU_RUNTIME = 5
    PROGRAMMING_LANGUAGE = 6
    TESTCASES = 7
    VIEW_DETAILS = 8

class ProblemsColumn(IntEnum):
    PROBLEM_NAME = 0
    STATUS = 1
    FASTEST_RUNTIME = 2
    SHORTEST_LENGTH = 3
    N_SUBMISSIONS = 4
    N_ACC = 5
    ACC_RATIO = 6
    DIFFICULTY_CATEGORY = 7
    AVAILABLE_LANGUAGES = 8
    STATISTICS = 9

class ProblemMetadataField():
    CPU_TIME_LIMIT = 'CPU Time limit'
    MEMORY_LIMIT = 'Memory limit'
    DIFFICULTY = 'Difficulty'
    SOURCE_LICENSE = 'Source & License'
    ATTACHMENTS = 'Attachments'
    DOWNLOADS = 'Downloads'

class ProblemStatisticsColumn(IntEnum):
    RANK = 0
    NAME = 1
    RUNTIME_OR_LENGTH = 2
    LANGUAGE = 3
    DATE = 4

class SolvedProblemsColumn(IntEnum):
    NAME = 0
    CPU_RUNTIME = 1
    LENGTH = 2
    ACHIEVEMENTS = 3
    DIFFICULTY = 4
    STATISTICS = 5

class RanklistField():
    SUBDIVISION = 'Subdivision'
    AFFILIATION = 'Affiliation'
    COUNTRY = 'Country'

class UserRanklistColumn(IntEnum):
    RANK = 0
    USER = 1
    COUNTRY = 2
    AFFILIATION = 3
    SCORE = 4

class CountryRanklistColumn(IntEnum):
    RANK = 0
    COUNTRY = 1
    USERS = 2
    AFFILIATIONS = 3
    SCORE = 4

class AffiliationRanklistColumn(IntEnum):
    RANK = 0
    AFFILIATION = 1
    COUNTRY = 2
    SUBDIVISION = 3
    USERS = 4
    SCORE = 5

class SingleCountryRanklistColumn(IntEnum):
    RANK = 0
    USER = 1
    SUBDIVISION = 2
    AFFILIATION = -2
    SCORE = -1

class SingleAffiliationRanklistColumn(IntEnum):
    RANK = 0
    USER = 1
    COUNTRY = 2
    SUBDIVISION = -2
    SCORE = -1

class ChallengeRanklistColumn(IntEnum):
    RANK = 0
    USER = 1
    COUNTRY = 2
    AFFILIATION = 3
    CHALLENGE_SCORE = 4

class DefaultRanklistColumn(IntEnum):
    RANK = 0
    USER = 1
    SCORE = 2

class ProblemAuthorsColumn(IntEnum):
    AUTHOR = 0
    PROBLEMS = 1
    AVG_DIFF = 2

class ProblemSourcesColumn(IntEnum):
    SOURCE = 0
    PROBLEMS = 1
    AVG_DIFF = 2
