from .api.openkattis import OpenKattis
from .api.nuskattis import NUSKattis
from .api.utils import set_verbose, suppress_warnings

Kattis = OpenKattis # backwards compatibility :)
suppress_warnings()
