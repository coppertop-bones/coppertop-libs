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


import numpy as np, datetime, builtins
from _strptime import _strptime

from coppertop.pipe import *
from coppertop.utils import NotYetImplemented
from bones.ts.metatypes import BType
from coppertop.dm.core.datetime import toCTimeFormat
from coppertop.dm.core.types import dframe, dmap, txt, pylist, pydict, T, T1, T2, N, pytuple, pydict_keys, pydict_values, \
    date, index, num, npfloat, dtup, dseq, matrix, t, darray, btype, py, matrix


array_ = (N**num)&darray

_defaultDateFmt = toCTimeFormat('YYYY.MM.DD')


# **********************************************************************************************************************
# to
# **********************************************************************************************************************

def _toHelper(x:T1, t:btype + py, tByT) -> pydict:
    tByT = dict(tByT)
    tByT[T2] = t
    return tByT

@coppertop(style=binary, typeHelper=_toHelper)
def to(x:T1, t:py, tByT) -> T2:
    if tByT[T1] == tByT[T2]:
        return x
    elif isinstance(t, BType):
        return t(x)
    else:
        try:
            return t(x)
        except Exception as ex:
            raise TypeError(f'Catch all can\'t convert {repr(x)} to {repr(t)} - {ex}')

@coppertop(style=binary, typeHelper=_toHelper)
def to(x:T1, t:btype, tByT) -> T2:
    if tByT[T1] == tByT[T2]:
        return x
    elif isinstance(t, BType):
        return t(x)
    else:
        try:
            return t(x)
        except Exception as ex:
            raise TypeError(f'Catch all can\'t convert {repr(x)} to {repr(t)} - {ex}')

@coppertop(style=binary)
def to(x:dmap, t:pydict) -> pydict:
    return dict(x.items())

@coppertop(style=binary)
def to(x:T, t:pydict) -> pydict:
    return dict(x)

@coppertop(style=binary)
def to(x:txt, t:date, f:txt) -> date:
    return parseDate(x, toCTimeFormat(f))

@coppertop(style=binary)
def to(x:txt, t:date) -> date:
    return parseDate(x, _defaultDateFmt)

@coppertop(style=binary)
def to(x:date, t:txt) -> txt:
    return x.strftime(_defaultDateFmt)

@coppertop(style=binary)
def to(d:date, t_:t.count) -> t.count:
    return d.toordinal() | t.count

@coppertop(style=binary)
def to(greg:t.count+index, t:date) -> date:
    return datetime.date.fromordinal(greg)

@coppertop(style=binary)
# def to(x:pylist, t:matrix) -> matrix:
def to(x:pylist, t:matrix) -> matrix:
    return matrix(x)

@coppertop(style=binary)
def to(x:matrix, t:array_) -> array_:
    return array_(x.reshape(max(x.shape)))

@coppertop(style=binary)
def to(x:pylist, t:np.ndarray) -> np.ndarray:
    return np.array(x)

@coppertop(style=binary)
def to(x:array_, t:np.ndarray) -> np.ndarray:
    return np.array(x)

def parseNum(x:txt) -> num:
    try:
        return float(x)
    except:
        return np.nan

@coppertop
def parseDate(x:txt, cFormat:txt) -> date:
    # rework to be more efficient in bulk by parsing format separately from x or handle x as an array / range
    dt, micro, _ = _strptime(x, cFormat)
    return datetime.date(dt[0], dt[1], dt[2])

@coppertop(style=binary)
def to(xs:pylist, t:array_) -> array_:
    return array_([parseNum(x) for x in xs])

@coppertop(style=binary)
def to(xs:pylist, t:(N**date)&darray, f:txt) -> (N**date)&darray:
    cFormat = toCTimeFormat(f)
    return darray((N**date)&darray, [parseDate(x, cFormat) for x in xs])

@coppertop
def toRow(xs:pylist) -> matrix:
    if len(xs) == 0: raise ValueError("can't create an empty matrix")
    if isinstance(xs[0], str):
        raise NotYetImplemented()
    raise NotYetImplemented()
    cFormat = toCTimeFormat(f)
    return darray((N**date)&darray, [parseDate(x, cFormat) for x in xs])

@coppertop
def toCol(xs:pylist) -> matrix:
    if len(xs) == 0: raise ValueError("can't create an empty matrix")
    if isinstance(xs[0], str):
        return darray(matrix, [parseNum(x) for x in xs]).reshape(len(xs), 1)
    return darray(matrix, xs).reshape(len(xs), 1)

@coppertop(style = binary)
def withKeys(vs, ks) -> pydict:
    return dict(builtins.zip(ks, vs))

@coppertop(style = binary)
def withValues(ks, vs) -> pydict:
    return dict(builtins.zip(ks, vs))
