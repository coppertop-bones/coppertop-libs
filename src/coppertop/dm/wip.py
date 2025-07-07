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

import os, os.path, json, itertools, builtins, numpy as np, polars as pl

from io import TextIOWrapper
from coppertop.pipe import *
from coppertop.dm.core.types import txt, pylist, dframe, dmap, pytuple, pyfunc, dtup, pydict, t as bt
from coppertop.dm.core.text import strip
from coppertop.dm.core.aggman import collect
from bones.core.errors import NotYetImplemented
from bones.core.sentinels import Missing
from coppertop.dm.core.conv import to



class OStreamWrapper:
    def __init__(self, sGetter):
        self._sGetter = sGetter
    def __lshift__(self, other):
        # self << other
        self._sGetter().write(other)      # done as a function call so it plays nicely with HookStdOutErrToLines
        return self

stdout = OStreamWrapper(lambda : sys.stdout)
stderr = OStreamWrapper(lambda : sys.stderr)



# **********************************************************************************************************************
# chunkBy
# **********************************************************************************************************************

@coppertop
def chunkBy(a:dframe, keys):
    "answers a range of range of row"
    raise NotYetImplemented()


# **********************************************************************************************************************
# chunkUsing
# **********************************************************************************************************************

@coppertop(style=binary)
def chunkUsing(iter, fn2):
    answer = []
    i0 = 0
    for i1, (a, b) in enumerate(_pairwise(iter)):
        if not fn2(a, b):
            answer += [iter[i0:i1+1]]
            i0 = i1 + 1
    answer += [iter[i0:]]
    return answer
def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b, strict=True)


@coppertop(style=binary)
def joinPath(a, b):
    return os.path.join(a, *(b if isinstance(b, (list, tuple)) else [b]))

@coppertop
def readlines(f:TextIOWrapper) -> pylist:
    return f.readlines()

@coppertop
def linesOf(pfn:txt):
    with open(pfn) as f:
        return f >> readlines >> collect >> strip(_,'\\n')

@coppertop(style=binary)
def copyTo(src, dest):
    raise NotImplementedError()

@coppertop
def readJson(pfn:txt):
    with open(pfn) as f:
        return json.load(f)

@coppertop
def readJson(f:TextIOWrapper):
    return json.load(f)

@coppertop(style=binary)
def ksJoinVs(ks, vs) -> dmap:
    return zip(ks, vs, strict=True) >> to >> dmap
dmap.ksJoinVs = ksJoinVs

@coppertop(style=binary)
def ksJoinVs(ks, vs) -> pydict:
    return zip(ks, vs, strict=True) >> to >> pydict
pydict.ksJoinVs = ksJoinVs


def sequence(p1, p2, n=Missing, step=Missing, sigmas=Missing):
    requiredType = bt.count
    if step is not Missing and n is not Missing:
        raise TypeError('Must only specify either n or step')
    if step is Missing and n is Missing:
        first , last = p1, p2
        return [e | requiredType for e in range(first, last+1, 1)]
    elif n is not Missing and sigmas is not Missing:
        mu, sigma = p1, p2
        low = mu - sigmas * sigma
        high = mu + sigmas * sigma
        first, last = high, low
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is not Missing and sigmas is Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is Missing and step is not Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.arange(first, last + step, step)]
    else:
        raise NotImplementedError('Unhandled case')
bt.count.sequence = sequence

def sequence(p1, p2, n=Missing, step=Missing, sigmas=Missing):
    requiredType = bt.offset
    if step is not Missing and n is not Missing:
        raise TypeError('Must only specify either n or step')
    if step is Missing and n is Missing:
        first , last = p1, p2
        return [e | requiredType for e in range(first, last+1, 1)]
    elif n is not Missing and sigmas is not Missing:
        mu, sigma = p1, p2
        low = mu - sigmas * sigma
        high = mu + sigmas * sigma
        first, last = high, low
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is not Missing and sigmas is Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is Missing and step is not Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.arange(first, last + step, step)]
    else:
        raise NotImplementedError('Unhandled case')
bt.offset.sequence = sequence
@coppertop
def sequence_(n:bt.count):
    return range(n)
bt.offset.sequence_ = sequence_

def sequence(p1, p2, n=Missing, step=Missing, sigmas=Missing):
    requiredType = bt.index
    if step is not Missing and n is not Missing:
        raise TypeError('Must only specify either n or step')
    if step is Missing and n is Missing:
        first , last = p1, p2
        return [e | requiredType for e in range(first, last+1, 1)]
    elif n is not Missing and sigmas is not Missing:
        mu, sigma = p1, p2
        low = mu - sigmas * sigma
        high = mu + sigmas * sigma
        first, last = high, low
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is not Missing and sigmas is Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.linspace(first, last, n)]
    elif n is Missing and step is not Missing:
        first, last = p1, p2
        return [e | requiredType for e in np.arange(first, last + step, step)]
    else:
        raise NotImplementedError('Unhandled case')
bt.index.sequence = sequence

@coppertop(style=binary)
def takeUntil(iter, fn):
    items = []
    if isinstance(iter, dict):
        for k, v in iter.items():
            if fn(k, v):
                break
            else:
                items.append([k,v])
        return dict(items)
    else:
        raise NotYetImplemented()

@coppertop
def replaceAll(xs, old, new):
    assert isinstance(xs, pytuple)
    return (new if x == old else x for x in xs)

@coppertop
def fromto(x, s1):
    return x[s1:None]

@coppertop
def fromto(x, s1, s2):
    return x[s1:s2]

@coppertop(style=binary)
def where(s:dmap, bools) -> dmap:
    assert isinstance(s, dmap)
    answer = dmap(s)
    for f, v in s._kvs():
        answer[f] = v[bools].view(dtup)
    return answer

@coppertop
def wrapInList(x):
    l = list()
    l.append(x)
    return l

@coppertop(style=binary)
def eachAsArgs(listOfArgs, f):
    """eachAsArgs(f, listOfArgs)
    Answers [f(*args) for args in listOfArgs]"""
    return [f(*args) for args in listOfArgs]

@coppertop(style=binary)
def subset(a:dmap, f2:pyfunc) -> pytuple:
    A, B = dmap(), dmap()
    for k, v in a._kvs():
        if f2(k, v):
            A[k] = v
        else:
            B[k] = v
    return A, B
