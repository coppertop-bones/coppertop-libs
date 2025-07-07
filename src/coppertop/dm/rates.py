# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import builtins, polars as pl
from coppertop.pipe import *
from bones.core.errors import NotYetImplemented, ProgrammerError
from bones.core.sentinels import Missing
from coppertop.dm.core.types import pylist, pytuple, pydict_keys, pydict_values, pyset, txt, t, offset, date, num
from coppertop.dm.core.datetime import addMonths

import math

ACT365Q = 1
ACT365 = 2
ACT360 = 3
_30360 = 4


@coppertop(style=nullary)
def tau(d1, d2, dct):
    if dct == ACT365Q:
        return (d2 - d1).days / 365.25
    elif dct == ACT365:
        return (d2 - d1).days / 365.0
    elif dct == ACT360:
        return (d2 - d1).days / 360.0
    else:
        raise ProgrammerError()


@coppertop
def df(cc:num, tau:num) -> num:
    return math.exp(-cc * tau)


@coppertop
def cc(df:num, tau:num) -> num:
    return math.log(df) / -tau


class Curve:
    def __init__(self):
        self.d1 = []
        self.d2 = []
        self.rates = Missing
        self.cumdf = Missing


@coppertop
def df(curve:Curve, o:offset, d:date) -> num:
    return curve.cumdf[o] * df(curve.rates[o], (d - curve.d1[o]) / 365.25)


@coppertop
def startEnds(todayDate, tenorInMonths, freqInMonths):
    answer = []
    start = todayDate
    for o in range(int(tenorInMonths / freqInMonths)):
        end = todayDate >> addMonths >> (o + 1) * freqInMonths
        answer.append((start, end))
        start = end
    return answer

