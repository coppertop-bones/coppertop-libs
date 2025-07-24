# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# data structures and functions to implement the examples and exercises in Allen Downey's Think Bayes
# See also https://zenodo.org/record/1432246/files/article.pdf
#
# Using https://en.wikipedia.org/wiki/Continuous_or_discrete_variable for inspiration
# DF is a discrete function x:num->y:num where each x can be mapped to a natural number and has these subtypes
# L is a likelihood function
# PMF is a discrete random variable, i.e. a probability mass function
# CMF is a cumulative mass function
#
# DF is implemented as {fn: f64**f64[dmap], attr:txt**T[dmap]} where the attr hold attributes such as a name
#     in C or bones we might use a variable length struct

import operator, random, numpy as np, enum, scipy.stats, collections.abc

from coppertop.pipe import *
from coppertop.core import NotYetImplemented

from bones.ts.metatypes import BType
from bones.lang.types import litstruct
from bones.kernel.sym_manager import Sym

from coppertop.dm.core.aggman import both, zipAll, values, keys, select, sort, kvs, collect, interleave, dropSlots, join
from coppertop.dm.core.conv import to
from coppertop.dm.core.misc import sequence
from coppertop.dm.core.types import pylist, index, pytuple, num, dstruct, matrix, dmap, py, darray
from coppertop.dm.pp import PP


# **********************************************************************************************************************
# types and construction
# **********************************************************************************************************************

def _makeDF(cs, *args, **kwargs):
    assert len(args) == 1
    arg = args[0]
    if isinstance(arg, dict):
        for k, v in arg.items():
            assert isinstance(k, (int, float))
            assert isinstance(v, (int, float))
        return dstruct(cs, fn_=dmap(arg), **kwargs)
    elif isinstance(arg, list):
        for k, v in arg:
            if not isinstance(k, (int, float, str, Sym)): raise TypeError(f'k must be an int or float but got {k} which is a {type(k)}')
            if not isinstance(v, (int, float, str, Sym)): raise TypeError(f'v must be an int or float but got {v} which is a {type(v)}')
        return dstruct(cs, fn_=dmap(arg), **kwargs)
    elif fitsWithin(typeOf(arg), DF):
        assert len(kwargs) == 0
        answer = dstruct(cs, arg)
        answer.fn_ = dmap(answer.fn_)
        return answer
    elif fitsWithin(typeOf(arg), litstruct):
        assert len(kwargs) == 0
        # d = {k: v for k, v in arg}
        answer = dstruct(cs, arg)
        answer.fn_ = dmap(arg)
        return answer
    else:
        raise NotYetImplemented()

def _makePmf(cs, *args, **kwargs):
    answer = _makeDF(cs, *args, **kwargs)
    if answer: answer = _normaliseInPlace(answer)
    return answer | PMF

def _makeCmf(cs, *args, **kwargs):
    # OPEN: check 0 < all values <= 1 and last v == 1
    answer = _makeDF(cs, *args, **kwargs)
    return answer | CMF

DF = BType('DF: DF & dstruct in mem').setPP('DF').setConstructor(_makeDF)
DF.__doc__ = 'Discrete Function - {fn_: f64**f64[dmap]} * {...} i.e. a fn and zero or more custom fields'
DF.__module__ = __name__

PMF = BType('PMF: PMF & DF in mem').setPP('PMF').setConstructor(_makePmf)
PMF.__doc__ = 'PMF - subtype of DF whose fn_ values form a probability measure'
PMF.__module__ = __name__

L = BType('L: L & DF in mem').setPP('L').setConstructor(lambda cs, *args, **kwargs: _makeDF(cs, *args, **kwargs) | L)
L.__doc__ = 'Likelihood - subtype of DF'
L.__module__ = __name__

CMF = BType('CMF: CMF & DF in mem').setPP('CMF').setConstructor(_makeCmf)
CMF.__doc__ = 'CMF - subtype of DF whose fn_ values are a cumulative mass function'
CMF.__module__ = __name__


@coppertop
def formatDF(df, name, keysFormat, valuesFormat, sep):
    def formatKv(kv):
        k, v = kv
        k = k if isinstance(k, (str, enum.Enum, Sym)) else format(k, keysFormat)
        v = v if isinstance(v, (str, enum.Enum, Sym)) else format(v, valuesFormat)
        return f'{k}: {v}'
    fnStrs = list(df.fn_ >> kvs) >> collect >> formatKv
    attributeStrs = list(df >> dropSlots >> ['fn_', 'cmf_'] >> kvs) >> collect >> formatKv
    return f'{name}({fnStrs >> join >> attributeStrs >> interleave >> sep})'


formatPmf = formatDF(_, 'PMF', '.3f', '.3f', ', ')
formatDf = formatDF(_, 'DF', '.3f', '.3f', ', ')
formatL = formatDF(_, 'L', '.3f', '.3f', ', ')
formatCmf = formatDF(_, 'CMF', '.3f', '.3f', ', ')

@coppertop
def PP(x:DF) -> DF:
    return PP(x, formatDf)

@coppertop
def PP(x:PMF) -> PMF:
    return PP(x, formatPmf)

@coppertop
def PP(x:L) -> L:
    return PP(x, formatL)

@coppertop
def PP(x:CMF) -> CMF:
    return PP(x, formatCmf)

@coppertop
def normalise(df:DF) -> PMF:
    return _normaliseInPlace(PMF(df)) | PMF

def _normaliseInPlace(df):
    # mutable - asssumes non-numeric values are tags and all numeric values are part of swnk
    total = 0
    for k, v in df.fn_.items():
        if isinstance(v, (float, int)):
            total += v
    factor = 1.0 / total
    for k, v in df.fn_.items():
        if isinstance(v, (float, int)):
            df.fn_[k] = v * factor
    return df

@coppertop(style=binary)
def to(xs:pylist, t:PMF, kde:scipy.stats.kde.gaussian_kde) -> PMF:
    fn = PMF()
    fn._kde = kde
    for x in xs:
        fn[x] = kde.evaluate(x)[0]
    return PMF(fn)

@coppertop(style=binary)
def to(pmf:PMF, t:CMF) -> CMF:
    answer = DF(pmf) | CMF
    running = 0.0
    df = {}
    for k, v in pmf.fn_.items():
        running += v
        df[k] = running
    answer.fn_ = df
    answer.cmf_ = np.array(list(df.items()))
    #answer._cmf[:, 1] = np.cumsum(answer._cmf[:, 1])
    return answer



# **********************************************************************************************************************
# the useful stuff
# **********************************************************************************************************************

@coppertop
def uniform(nOrXs:pylist) -> PMF:
    '''Makes a uniform PMF. xs can be sequence of values or [length]'''
    # if a single int it is a count else there must be many xs
    fn = {}
    if len(nOrXs) == 1:
        if isinstance(nOrXs[0], int):
            n = nOrXs[0]
            p = 1.0 / n
            for x in sequence(0, n-1):
                fn[float(x)] = p
            return PMF(fn)
    else:
        p = 1.0 / len(nOrXs)
        for x in nOrXs:
            fn[float(x)] = p
        return PMF(fn)

@coppertop
def mix(args:pylist) -> PMF:
    """answer a mixture pmf, each arg is (beta, pmf) or pmf"""
    t = {}
    for arg in args:
        beta, pmf = arg if isinstance(arg, (tuple, list)) else (1.0, arg)
        for x, p in pmf.fn_.items():
            t[x] = t.setdefault(x, 0) + beta * p
    return PMF(t >> sort)

@coppertop
def mean(pmf:PMF) -> num:
    fs = pmf >> keys
    ws = pmf >> values
    try:
        return num(np.average(fs, weights=ws))
    except TypeError:
        fs, ws = list([fs, ws] >> zipAll) >> select >> (lambda fv: not isinstance(fv[0], str)) >> zipAll
        return float(np.average(fs, weights=ws)) | num   # numpy floats define |

@coppertop
def gaussian_kde(data) -> scipy.stats.kde.gaussian_kde:
    return scipy.stats.gaussian_kde(data)

@coppertop(style=binary)
def sample(cmf:CMF, n:index) -> matrix[darray]:
    vals = []
    sortedCmf = cmf['_cmf']
    for _ in range(n):
        p = random.random()
        i = np.searchsorted(sortedCmf[:, 1], p, side='left')
        vals.append(sortedCmf[i, 0])
    return matrix[darray](vals)

@coppertop(style=binary)
def sample(kde:scipy.stats.kde.gaussian_kde, n:index) -> matrix[darray]:
    return kde.resample(n).flatten()

@coppertop(style=binary, name='*')
def pmfMul(lhs:DF, rhs:DF) -> DF:
    # lhs kvs both {(x.k, x.v*(y.v)} (rhs kvs) normalise <:pmf>
    return DF(
        lhs.fn_ >> both >> (lambda kLhs, vLhs, kRhs, vRhs: (kLhs, vLhs * vRhs)) >> rhs.fn_
    )

@coppertop(style=binary)
def rvAdd(lhs:PMF, rhs:PMF) -> PMF:
    return _rvOp(lhs, rhs, operator.add)

@coppertop(style=binary)
def rvSub(lhs:PMF, rhs:PMF) -> PMF:
    return _rvOp(lhs, rhs, operator.sub)

@coppertop(style=binary)
def rvMul(lhs:PMF, rhs:PMF) -> PMF:
    return _rvOp(lhs, rhs, operator.mul)

@coppertop(style=binary)
def rvDiv(lhs:PMF, rhs:PMF) -> PMF:
    return _rvOp(lhs, rhs, operator.truediv)

@coppertop(style=binary)
def rvMax(lhs:PMF, rhs:PMF) -> PMF:
    return _rvOp(lhs, rhs, max)

def _rvOp(lhs, rhs, op):
    xps = {}
    for x1, p1 in lhs.fn_.items():
        for x2, p2 in rhs.fn_.items():
            x = op(x1, x2)
            xps[x] = xps.setdefault(x, 0.0) + p1 * p2
    return PMF(
        sorted(
            xps.items(),
            key=lambda xp: xp[0]
        )
    )

@coppertop
def toXsPs(pmf:PMF) -> pytuple:
    return tuple(zip(*pmf.fn_.items()))

@coppertop(style=unary)
def quantile(pmf:PMF, x:num):
    total = 0
    for k, v in pmf.fn_.items():
        total += v
        if total >= x:
            return k

@coppertop(style=unary)
def quantile(cmf:CMF, x:num):
    for k, v in cmf.fn_.items():
        if v >= x:
            return k


# **********************************************************************************************************************
# plotting functions
# **********************************************************************************************************************

@coppertop
def toSteps(s:PMF) -> pytuple:
    return _asSteps(s >> keys, s >> values)

@coppertop
def toSteps(s:PMF, kwargs) -> pytuple:
    return _asSteps(s >> keys, s >> values, **kwargs)

def _asSteps(xs:pylist, ys:pylist, align='center', width=None):
    #xMin, xMax = min(xs), max(xs)
    if width is None:
        width = np.diff(list(xs)).min()
    points = []
    lastx = np.nan
    lasty = np.nan
    for x, y in [xs, ys] >> zipAll:
        if (x - lastx) > 1e-5:
            points.append((lastx, 0))
            points.append((x, 0))
        if not np.isnan(lasty):
            points.append((x, lasty))
        points.append((x, y))
        points.append((x + width, y))
        lastx = x + width
        lasty = y
    points.append((lastx, lasty))
    pxs, pys = points >> zipAll
    if align == 'center':
        pxs = np.array(pxs) - width / 2.0
    elif align == 'right':
        pxs = np.array(pxs) - width
    return pxs, np.array(pys)


# **********************************************************************************************************************
# aggman functions
# **********************************************************************************************************************

@coppertop
def keys(a:DF) -> collections.abc.KeysView:
    return a.fn_.keys()

@coppertop
def values(a:DF) -> collections.abc.ValuesView:
    return a.fn_.values()

@coppertop(style=binary)
def at(df:DF, k:py):
    return df.fn_[k]

@coppertop(style=ternary)
def atOr(df:DF, k:py, default:py):
    return df.fn_.get(k, default)

# @coppertop(style=binary)
# def merge(a:DF[T1], b:dstruct&T2, tByT) -> DF[T1]:
#     answer = dstruct(tByT[T1], a)
#     answer._update(b.items())
#     return answer
