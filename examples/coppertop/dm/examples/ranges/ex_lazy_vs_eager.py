# **********************************************************************************************************************
#
#                             Copyright (c) 2020-2021 David Briant. All rights reserved.
#                               Contact the copyright holder for licensing terms.
#
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.dm.core import collect, to
from coppertop.dm.testing import check, equals
from coppertop.dm.examples.ranges.agents import FnAdapterFR
from coppertop.dm.examples.ranges.utils import EMPTY, rFnAdapterEager, rEach, rMaterialise
from coppertop.dm.core.datetime import addDays, day, toCTimeFormat
from coppertop.dm.core.conv import parseDate

YYYY_MM_DD = 'YYYY.MM.DD' >> toCTimeFormat

@coppertop
def _ithDateBetween2(start, end, i):
    ithDate = start >> addDays >> i
    return EMPTY if ithDate > end else ithDate

@coppertop(style=binary)
def datesBetween2(start, end):
     return _ithDateBetween2(start, end, _) >> to >> FnAdapterFR

@coppertop(style=binary)
def datesBetweenEager2(start, end):
     return _ithDateBetween2(start, end, _) >> rFnAdapterEager


def test_datesBetween_lazy():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetween2 >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
    >> rEach >> day \
    >> rMaterialise >> check >> equals >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

def test_datesBetween_eager():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetweenEager2 >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
    >> collect >> day \
    >> check >> equals >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

def main():
    test_datesBetween_lazy()
    test_datesBetween_eager()

if __name__ == '__main__':
    main()
    print('pass')

