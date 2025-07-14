# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2021 David Briant. All rights reserved.
#                               Contact the copyright holder for licensing terms.
#
# **********************************************************************************************************************

# Python implementation of https://wiki.dlang.org/Component_programming_with_ranges
#
# We want print this calendar to stdout, with three months horizontally and each week ending on a Sunday:
#
#        January              February                March
#         1  2  3  4  5                  1  2                  1  2
#   6  7  8  9 10 11 12   3  4  5  6  7  8  9   3  4  5  6  7  8  9
#  13 14 15 16 17 18 19  10 11 12 13 14 15 16  10 11 12 13 14 15 16
#  20 21 22 23 24 25 26  17 18 19 20 21 22 23  17 18 19 20 21 22 23
#  27 28 29 30 31        24 25 26 27 28        24 25 26 27 28 29 30
#                                              31
#
#         April                  May                  June
#      1  2  3  4  5  6            1  2  3  4                     1
#   7  8  9 10 11 12 13   5  6  7  8  9 10 11   2  3  4  5  6  7  8
#  14 15 16 17 18 19 20  12 13 14 15 16 17 18   9 10 11 12 13 14 15
#  21 22 23 24 25 26 27  19 20 21 22 23 24 25  16 17 18 19 20 21 22
#  28 29 30              26 27 28 29 30 31     23 24 25 26 27 28 29
#                                              30
#
#         July                 August               September
#      1  2  3  4  5  6               1  2  3   1  2  3  4  5  6  7
#   7  8  9 10 11 12 13   4  5  6  7  8  9 10   8  9 10 11 12 13 14
#  14 15 16 17 18 19 20  11 12 13 14 15 16 17  15 16 17 18 19 20 21
#  21 22 23 24 25 26 27  18 19 20 21 22 23 24  22 23 24 25 26 27 28
#  28 29 30 31           25 26 27 28 29 30 31  29 30
#
#        October              November              December
#         1  2  3  4  5                  1  2   1  2  3  4  5  6  7
#   6  7  8  9 10 11 12   3  4  5  6  7  8  9   8  9 10 11 12 13 14
#  13 14 15 16 17 18 19  10 11 12 13 14 15 16  15 16 17 18 19 20 21
#  20 21 22 23 24 25 26  17 18 19 20 21 22 23  22 23 24 25 26 27 28
#  27 28 29 30 31        24 25 26 27 28 29 30  29 30 31
#
#
# First we define "chunking" as breaking something up into smaller parts and "aggregating" as assembling smaller parts
# together, and borrow from https://www.informit.com/articles/printerfriendly/1407357.
#
# Can this all be done in one pass? No, but we can save checkpoints and resume, i.e. by using forward ranges rather
# than a simple input range. This should effectively add up to exactly two passes over the dates in the year, one for
# chunking, which can yield a checkpoint to be consumed by the second pass, which formats the dates into a calendar
# lines. If the year was an array of dates stored in memory then we would be jumping around the array accessing each
# partial week sequentially. For the purpose of this example we pretend creating dates is expensive to compute but cheap
# to cache (not an unrealistic assumption for many situations).
#
# The game might be to say the costs of computation, storing the computation and changing storage size is high, the
# cost of ranges is low and the value of printing each line of the calendar is high and the sooner the better.
#
# We will cache the results of the date computation in a ring buffer, so that we can iterate over the results, and
# can we even drop some dates as we go? E.g. once we have finished the first week we can drop the dates of the first
# month but not the second and third months. Also, we can start printing the first line once we know all three months.
# So our maximum computation buffer should be 2 whole months and 1 week.
#
# The parts are:
#   1) input range to compute on demand and store all the dates in a year into a ring buffer
#   2) forward ranges to chunk dates by whole months
#   3) forward ranges to chunk months by month lines, e.g. ending on a Sunday
#   4) formatting of each month line, e.g. right and left padding for line with less than 7 days
#   5) aggregator to collect 3 calendar line ranges and emit them as a single string interleaved with a separator
#   6) line formatter that produces a line of titles, a spacer, then each calendar line in the quarter
#   7) quarter formatter that consumes a quarter, emits a blank line if needed, and repeats until done
#
# Effectively we are setting up a non-trivial processing pipeline with inputs, outputs and a lot of mutation
#
# Our goal here is to make it as immutable as possible, ideally in a way that we can reason about the code and step
# through it.
#
# Design notes:
# - no functions that can directly mutate a range, e.g. no popFront, no put
# - inspection functions e.g. rFront, rEmpty, count
# - stdout is affected by parts 5), 6) and 7) - should we compose them and pass the result up the stack, or should we
#   construct them with a sink that writes to stdout?


# OPEN: can to take a construction function?
# week >> rEach >> dateAsDayString >> rMaterialise
# week >> rEach >> dateAsDayString >> to >> pylist

# rEach creates a MapFR
# @coppertop(style=binary)
# def to(r:MapFR+FR, y:pylist):   << problem with the dispatch here since metric is currently average distance

# but in this example we want to sink to stdout not create a list. In general we have inputs, outputs and control
# Python hides all the control by doing what is necessary to get the next result however out 3 month process is a
# breadth first access not a depth first access, so we can't use my naive rMaterialise to test at that level
#
# @coppertop
# def rMaterialise(r):
#     return _materialise(r)
#
# def _materialise(r):
#     answer = list()
#     while not r.empty:
#         e = r.front
#         if isinstance(e, IInputRange) and not isinstance(e, IRandomAccessInfinite):
#             answer.append(_materialise(e))
#             if not r.empty:  # the sub range may exhaust this range
#                 r.popFront()
#         else:
#             answer.append(e)
#             r.popFront()
#     return answer


import datetime, pytest
skip = pytest.mark.skip

from bones.core.sentinels import Null
from coppertop.pipe import *
from bones.ts.metatypes import BTUnion
from coppertop.dm.core import count, joinAll, collect, interleave, pad, strip, to, day, weekday, weekdayName, \
    monthLongName, addDays, toCTimeFormat, parseDate
from coppertop.dm.core.misc import not_
from coppertop.dm.core.types import date, txt, pylist
from coppertop.dm.testing import check, equals
from coppertop.dm.pp import PP
from coppertop.dm.wip import wrapInList

from coppertop.dm.examples.ranges.agents import IForwardRange, ListOR, RaggedZipIR, FnAdapterFR, ChainFR, \
    IndexableFR
from coppertop.dm.examples.ranges.utils import rChunkUsingSubRangeGeneratorFR, rChunkFROnChangeOf, rGetIRIter, \
    rPushAllTo, EMPTY, rEach, rUntil, rReplaceWith, rMaterialise, rFront, rTake


YYYY_MM_DD = 'YYYY.MM.DD' >> toCTimeFormat




@coppertop
def rDatesInYear(year):
     return _ithDateInYear(year, _) >> to >> FnAdapterFR

@coppertop
def _ithDateInYear(year, i):
    ithDate = datetime.date(year, 1, 1) >> addDays >> i
    return EMPTY if ithDate.year != year else ithDate



@coppertop
def rMonthChunks(datesR):
    return datesR >> rChunkFROnChangeOf(_, lambda x: x.month)

@coppertop
def _untilWeekdayName(datesR, wdayName):
    return datesR >> rUntil >> (lambda d: d >> weekday >> weekdayName == wdayName)

@coppertop
def weekChunks(r):
    return r >> rChunkUsingSubRangeGeneratorFR(_, _untilWeekdayName(_, 'Sun'))

@coppertop
def dateAsDayString(d):
    return d >> day >> to >> txt >> pad(_, dict(right=3))


class WeekStringsFR(IForwardRange):
    def __init__(self, rOfWeeks):
        self.rOfWeeks = rOfWeeks

    @property
    def empty(self):
        return self.rOfWeeks.empty

    @property
    def front(self):
        # this exhausts the front week range
        week = self.rOfWeeks.front
        startDay = week.front >> weekday
        preBlanks = ['   '] * startDay
        dayStrings = week >> rEach >> dateAsDayString >> rMaterialise
        postBlanks = ['   '] * (7 - ((dayStrings >> count) + startDay))
        return (preBlanks + dayStrings + postBlanks) >> joinAll

    def popFront(self):
        self.rOfWeeks.popFront()

    def save(self):
        # TODO delete once we've debugged the underlying save issue
        return WeekStringsFR(self.rOfWeeks.save())

@coppertop
def monthTitle(month, width):
    return month >> monthLongName >> pad(_, dict(center=width))

@coppertop
def monthLines(monthDays):
    return [
        monthDays.front.month >> monthTitle(_, 21) >> wrapInList >> to >> IndexableFR,
        monthDays >> weekChunks >> to >> WeekStringsFR
    ] >> to >> ChainFR

@coppertop
def monthStringsToCalendarRow(strings, blank, sep):
    return strings >> rReplaceWith(_, Null, blank) >> rMaterialise >> interleave >> sep

def pasteBlocks(rOfMonthChunk):
    return rOfMonthChunk >> to >> RaggedZipIR >> rEach >> monthStringsToCalendarRow(" "*21, " ")

@coppertop
def _ithDateBetween(start, end, i):
    ithDate = start >> addDays >> i
    return EMPTY if ithDate > end else ithDate

@coppertop(style=binary)
def datesBetween(start:date, end:date):
     return _ithDateBetween(start, end, _) >> to >> FnAdapterFR



def test_allDaysInYear():
    actual = []
    o = 2020 >> rDatesInYear >> rPushAllTo >> ListOR(actual)
    actual[0] >> check >> equals >> datetime.date(2020, 1, 1)
    actual[-1] >> check >> equals >> datetime.date(2020, 12, 31)
    a = [e for e in 2020 >> rDatesInYear >> rGetIRIter]
    b = a >> count
    b \
        >> check \
        >> equals >> 366


def test_datesBetween():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetween >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
        >> rEach >> day \
        >> rMaterialise \
        >> check >> equals >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


def test_chunkingIntoMonths():
    2020 >> rDatesInYear \
        >> rMonthChunks \
        >> rMaterialise \
        >> count \
        >> check >> equals >> 12


def test_checkNumberOfDaysInEachMonth():
    2020 >> rDatesInYear \
        >> rMonthChunks \
        >> rMaterialise \
        >> collect >> count \
        >> check >> equals >> [31,29,31,30,31,30,31,31,30,31,30,31]


def test__untilWeekdayName():
    r = 2020 >> rDatesInYear
    dates = [d for d in r >> _untilWeekdayName(_, 'Sun') >> rGetIRIter]
    dates[-1] >> check >> equals >> datetime.date(2020, 1, 5)   # the sunday
    r >> rFront >> check >> equals >> datetime.date(2020, 1, 6) # the monday


def test_WeekChunks():
    datesR = '2020.01.16' >> parseDate(_, YYYY_MM_DD) >> datesBetween >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD))
    weeksR = rChunkUsingSubRangeGeneratorFR(datesR, _untilWeekdayName(_, 'Sun'))
    actual = []
    while not weeksR.empty:
        weekR = weeksR >> rFront
        actual.append([d >> day for d in weekR >> rGetIRIter])
        weeksR.popFront()
    actual >> check >> equals >> [[16, 17, 18, 19], [20, 21, 22, 23, 24, 25, 26], [27, 28, 29]]


def test_WeekStrings():
    expectedJan2020 = [
        '        1  2  3  4  5',
        '  6  7  8  9 10 11 12',
        ' 13 14 15 16 17 18 19',
        ' 20 21 22 23 24 25 26',
        ' 27 28 29 30 31      ',
    ]
    weekStringsR = (
        2020 >> rDatesInYear
        >> rMonthChunks
        >> rFront
        >> weekChunks
        >> to >> WeekStringsFR
    )
    weekStringsR2 = weekStringsR.save()
    [ws for ws in weekStringsR >> rGetIRIter] >> check >> equals >> expectedJan2020

    actual = [ws for ws in weekStringsR2 >> rGetIRIter]
    if actual >> equals >> expectedJan2020 >> not_:
        "fix WeekStringsFR.save()" >> PP


def test_MonthTitle():
    1 >> monthTitle(_, 21) >> wrapInList >> to >> IndexableFR \
        >> rEach >> strip >> rMaterialise \
        >> check >> equals >> ['January']


def test_oneMonthsOutput():
    [
        1 >> monthTitle(_, 21) >> wrapInList >> to >> IndexableFR,
        2020 >> rDatesInYear
            >> rMonthChunks
            >> rFront
            >> weekChunks
            >> to >> WeekStringsFR
    ] >> to >> ChainFR \
        >> rMaterialise >> check >> equals >> Jan2020TitleAndDateLines

    # equivalently
    check(
        rMaterialise(monthLines(rFront(rMonthChunks(rDatesInYear(2020))))),
        equals,
        Jan2020TitleAndDateLines
    )


@skip
def test_firstQuarter():
    r = (2020 >> rDatesInYear \
        >> rMonthChunks \
        >> rTake >> 3 \
        >> to >> RaggedZipIR >> rEach >> monthStringsToCalendarRow(_, " "*21, " ")
    )
    x = r >> rMaterialise
    x >> check >> equals >> Q1_2013TitleAndDateLines



Jan2020DateLines = [
    '        1  2  3  4  5',
    '  6  7  8  9 10 11 12',
    ' 13 14 15 16 17 18 19',
    ' 20 21 22 23 24 25 26',
    ' 27 28 29 30 31      ',
]

Jan2020TitleAndDateLines = ['       January       '] + Jan2020DateLines

Q1_2013TitleAndDateLines = [
    "       January              February                March        ",
    "        1  2  3  4  5                  1  2                  1  2",
    "  6  7  8  9 10 11 12   3  4  5  6  7  8  9   3  4  5  6  7  8  9",
    " 13 14 15 16 17 18 19  10 11 12 13 14 15 16  10 11 12 13 14 15 16",
    " 20 21 22 23 24 25 26  17 18 19 20 21 22 23  17 18 19 20 21 22 23",
    " 27 28 29 30 31        24 25 26 27 28        24 25 26 27 28 29 30",
    "                                             31                  "
]



def main():
    test_allDaysInYear()
    test_datesBetween()
    test_chunkingIntoMonths()
    test_checkNumberOfDaysInEachMonth()
    test__untilWeekdayName()
    test_WeekChunks()
    test_WeekStrings()
    test_MonthTitle()
    test_oneMonthsOutput()
    test_firstQuarter()


if __name__ == '__main__':
    main()
    print('pass')
