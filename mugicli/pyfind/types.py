from collections import namedtuple
from dataclasses import dataclass
from collections.abc import Callable

import re
try:
    from openpyxl.utils import column_index_from_string
except ImportError:
    pass

FloatRange = namedtuple('FloatRange', ['v1', 'v2'])

AddressRange = namedtuple('AddressRange', ['r1', 'c1', 'r2', 'c2'])

def parse_address_range(s):
    ms = [re.match('^([a-z]+)([0-9]+)$', ss, re.IGNORECASE) for ss in s.split(':')]
    if None in ms:
        return None
    rc = [(int(m.group(2)), column_index_from_string(m.group(1))) for m in ms]
    if len(rc) == 1:
        r1, c1 = rc[0]
        r2, c2 = rc[0]
    else:
        [r1, c1], [r2, c2] = rc
    return AddressRange(r1, c1, r2, c2)

def parse_int(s):
    try:
        return int(s)
    except ValueError:
        pass

def parse_float(s):
    try:
        return float(s)
    except ValueError:
        pass

def parse_float_range(s):
    ss = s.split('..')
    if len(ss) != 2:
        return
    try:
        v1 = float(ss[0])
        v2 = float(ss[1])
        return FloatRange(v1, v2)
    except ValueError:
        pass

@dataclass
class ExtraArgs:
    maxdepth: int
    first: int

Pred = Callable[[str, str, bool], bool]

Exec = Callable[[str, str, str, bool], None]