# **********************************************************************************************************************
#
#                             Copyright (c) 2020-2021 David Briant. All rights reserved.
#                               Contact the copyright holder for licensing terms.
#
# **********************************************************************************************************************

# see - https://en.wikipedia.org/wiki/Jackson_structured_programming
# this file show four ways to implement the problem of counting repeated lines in a file - two are translations from
# the wikipedia article and the remaining two take the "traditional" program and transform it into range style code

import os
from coppertop.pipe import *
from coppertop.dm.examples.ranges import nodes
from coppertop.dm.examples.ranges.utils import rPut, rExhaustInto, rTarget
from coppertop.dm.core.misc import getAttr
from coppertop.dm.testing import check, equals



home = os.path.dirname(os.path.abspath(__file__))
filename = "/linesForCounting.txt"
expected = [
    ('aaa\n', 2),
    ('bb\n', 1),
    ('aaa\n', 1),
    ('bb\n', 3),
    ('aaa\n', 1)
]


def countLinesTrad(f):
    answer = []

    count = 0
    firstLineOfGroup = ''
    line = f.readline()
    while line != '':
        if firstLineOfGroup == '' or line != firstLineOfGroup:
            if firstLineOfGroup != '':
                answer.append((firstLineOfGroup, count))
            count = 0
            firstLineOfGroup = line
        count += 1
        line = f.readline()

    if (firstLineOfGroup != ''):
        answer.append((firstLineOfGroup, count))

    return answer



def countLinesRanges1(f):
    r = nodes.FileLines(f)
    out = nodes.ListSink()

    count = 0
    firstLineOfGroup = ''
    while not r.empty:
        if firstLineOfGroup == '' or r.front != firstLineOfGroup:
            if firstLineOfGroup != '':
                out >> rPut >> (firstLineOfGroup, count)
            count = 0
            firstLineOfGroup = r.front
        count += 1
        r.popFront()

    if firstLineOfGroup != '':
        out >> rPut >> (firstLineOfGroup, count)

    return out.list



def countLinesRanges2(f):
    out = nodes.ListSink()
    r = nodes.FileLines(f)
    while not r.empty:
        count = r >> countEquals(_, firstLineOfGroup := r.front)
        out >> rPut >> (firstLineOfGroup, count)
    return out.list


@coppertop
def countEquals(r, value):
    count = 0
    while not r.empty and r.front == value:
        count += 1
        r.popFront()
    return count



def countLinesRanges3(f):
    return nodes.FileLines(f) >> rRepititionCounts >> rExhaustInto >> nodes.ListSink([]) >> rTarget


@coppertop
def rRepititionCounts(r):
    return RepititionCountIR(r)

class RepititionCountIR(nodes.Simple):
    def __init__(self, r):
        self.r = r
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        firstInGroup = self.r.front
        count = 0
        while not self.r.empty and self.r.front ==firstInGroup:
            count += 1
            self.r.popFront()
        return firstInGroup, count
    def popFront(self):
        pass



# "Jackson criticises the traditional version, claiming that it hides the relationships which exist between the
# input lines, compromising the program's understandability and maintainability by, for example, forcing the use
# of a special case for the first line and forcing another special case for a final output operation."

def countLinesJsp(f):
    answer = []

    line = f.readline()
    while line != '':
        count = 0
        firstLineOfGroup = line

        while line != '' and line == firstLineOfGroup:
            count += 1
            line = f.readline()
        answer.append((firstLineOfGroup, count))

    return answer



def main():
    with open(home + filename) as f:
        actual = countLinesJsp(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesTrad(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges1(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges2(f)
    actual >> check >> equals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges3(f)
    actual >> check >> equals >> expected


if __name__ == '__main__':
    main()
    print('pass')

