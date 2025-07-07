# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import builtins

from coppertop.pipe import *
from coppertop.dm.core.types import txt, pydict, dseq, dstruct, T1, btype, pytuple
from coppertop.dm.core.aggman import count, collect
from coppertop.dm.pp import PP
from coppertop.dm.core import pad, max

from coppertop.dm.examples.cluedo.core import display_table


@coppertop
def PP(t:display_table) -> display_table:
    for string in t:
        string >> PP
    return t

@coppertop(style=binary)
def hjoin(a:display_table, b:display_table) -> display_table:
    return hjoin(a, b, {})

@coppertop(style=binary)
def hjoin(a:display_table, b:display_table, options:pydict) -> display_table:
    assert (a >> count) == (b >> count)
    answer = dseq(display_table, [])
    for i in range(len(a)):
        answer.append(a[i] + options.get('sep', '') + b[i])
    return answer

@coppertop(style=binary)
def join(a:display_table, b:display_table) -> display_table:
    return dseq(display_table, a.data + b.data) >> ljust

@coppertop
def ljust(rows:display_table) -> display_table:
    return ljust(rows, {})

@coppertop
def ljust(rows:display_table, options:pydict) -> display_table:
    maxLength = rows >> collect >> count >> max
    options_ = dict(left=max((maxLength, options.get('width',0))), pad=options.get('fillchar', ' '))
    return rows >> collect >> pad(_, options_) | display_table

@coppertop(style=binary)
def add(rows:display_table, row:txt) -> display_table:
    rows.append(row)
    return rows >> ljust

@coppertop
def cardIds(cards):
    return [c.value for c in cards]

@coppertop(style=binary)
def to(args:T1, t:btype):
    return t(args)

# @coppertop(style=binary)
# def to(args:pytuple, t:pydict) -> pydict:
#     k, v = args
#     1/0

@coppertop(style=binary)
def zipBoth(a, b):
    return builtins.zip(a, b)

@coppertop(style=binary)
def bucket(t, n):
    return _bucket(t, t, n)

def _bucket(t, r, n):
    if n == 1:
        return [[r]]
    else:
        answer = []
        for numGive in range(r + 1):
            others = _bucket(t, numGive, n-1)
            for other in others:
                answer.append( [r - numGive] + other)
    return answer
