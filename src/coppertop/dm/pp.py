# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from copy import copy as _copy
import numpy as np
from enum import Enum

from collections import namedtuple
from coppertop.pipe import *
from coppertop.utils import Missing
from coppertop.dm.core.aggman import collect, interleave, kvs
from coppertop.dm.core.types import txt, pyfunc, T

__all__ = []

list_iter = type(iter([]))


@coppertop
def formatStruct(s, name, keysFormat, valuesFormat, sep):
    def formatKv(kv):
        k, v = kv
        k = k if isinstance(k, (str, Enum)) else format(k, keysFormat)
        v = v if isinstance(v, (str, Enum)) else format(v, valuesFormat)
        return f'{k}: {v}'
    return f'{name}({list(s >> kvs) >> collect >> formatKv >> interleave >> sep})'
    # return f'{name}({s >> kvs >> collect >> formatKv >> join >> sep})'

@coppertop(dispatchEvenIfAllTypes=True)
def PP(x):
    return context.PP(x)

@coppertop(dispatchEvenIfAllTypes=True)
def NB(x):
    return context.NB(x)

@coppertop(dispatchEvenIfAllTypes=True)
def EE(x):
    return context.EE(x)

@coppertop
def PP(x, f:pyfunc + (T^T)):
    f(x) >> PP
    return x

@coppertop
def PPS(lines):
    for line in lines:
        line >> PP
    return lines

@coppertop
def PP(x, fmt:txt):
    x >> format(_, fmt) >> PP
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def RR(x):
    print(repr(x))
    return x

@coppertop
def RR(x, f:pyfunc):
    print(repr(f(x)))
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def SS(x):
    print(str(x))
    return x

@coppertop
def SS(x, f:pyfunc):
    print(str(f(x)))
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def DD(x):
    print(dir(x))
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def JJ(x):
    print('                                                                                                                                                                                                                                                                                      ', end='\r')
    print(x, end='\r')
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def HH(x):
    if hasattr(x, '_doc') and x._doc:
        print(x._doc)
    elif hasattr(x, '_t'):
        help(x._t)
    else:
        help(x)
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def TT(x):
    print(typeOf(x))
    return x

@coppertop(dispatchEvenIfAllTypes=True)
def TTV(x):
    '''Verbosely prints the type to stdout'''
    with context(showFullType=True):
        print(typeOf(x))
    return x

@coppertop
def LL(x):
    if isinstance(x, list_iter):
        x = list(_copy(x)) # if it's an iterator it's state will be changed by len - so make a copy
    if isinstance(x, np.ndarray):
        print(x.shape)
    else:
        print(len(x))
    return x

Titles = namedtuple('Titles', ['title', 'subTitles'])  # aka heading def

@coppertop
def formatAsTable(listOfRows):
    return _formatAsTable(listOfRows)

@coppertop
def formatAsTable(listOfRows, headingDefs):
    return _formatAsTable(listOfRows, headingDefs)

@coppertop
def formatAsTable(listOfRows, headingDefs, title):
    return _formatAsTable(listOfRows, headingDefs, title)

def _formatAsTable(listOfRows, headingDefs=Missing, title=Missing):
    # for moment only handle one level of grouping
    columnTitles = _Collector()
    i = 0
    groupTitles = _Collector()
    hasGroupTitles = False
    for headingDef in headingDefs:
        if isinstance(headingDef, str):
            groupTitles << (i, i, '')
            columnTitles << headingDef
            i += 1
        elif not headingDef:
            groupTitles << (i, i, '')
            columnTitles << ''
            i += 1
        else:
            groupTitles << (i, i + len(headingDef.subTitles) - 1, headingDef.title)
            columnTitles += headingDef.subTitles
            i += len(headingDef.subTitles)
            hasGroupTitles = True
    allRows = ([columnTitles] if headingDefs else []) + [list(row) for row in listOfRows]
    widths = [1] * len(allRows[0])
    for row in allRows:
        for j, cell in enumerate(row):
            row[j] = str(row[j])
            widths[j] = widths[j] if widths[j] >= len(row[j]) else len(row[j])
    cellsWidth = sum(widths) + 2 * len(widths)
    lines = []
    if title is not Missing:
        titleLine = '- ' + title + ' -' if title else ''
        LHWidth = int((cellsWidth - len(titleLine)) / 2)
        RHWidth = (cellsWidth - len(titleLine)) - LHWidth
        titleLine = ('-' * LHWidth) + titleLine + ('-' * RHWidth)
        lines.append(titleLine)
    if groupTitles:
        line = ''
        for i1, i2, groupTitle in groupTitles:
            width = sum([widths[i] for i in range(i1, i2 + 1)])
            width += 2 * (i2 - i1)
            line += (' %' + str(width) + 's|') % groupTitle[:width]
        lines.append(line)
    for i, row in enumerate(allRows):
        line = ''
        for j, cell in enumerate(row):
            line += (' %' + str(widths[j]) + 's|') % cell
        lines.append(line)
        if i == 0 and headingDefs:
            line = ''
            for width in widths:
                line += '-' * (width + 1) + '|'
            lines.append(line)
    return lines

class _Collector(list):
    def __lshift__(self, other):  # self << other
        self.append(other)
        return self

