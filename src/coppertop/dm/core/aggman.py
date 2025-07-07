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


# manipulation of these aggregation classes:
# txt, sym, dtup, dstruct, dseq, dmap, tvframe, pylist, pydict, pytup, pyset, nd, (N**num)&darray, matrix&darray
#
#
# NOTES
# dmap is order preserving (may add a fasthash that isn't)
# decide how to handle lazy / out-of-order aggregates
# do we need merge and underride (only difference is order of keys)



import builtins, numpy as np, collections.abc

from coppertop.pipe import *
from bones import jones

from bones.core.errors import NotYetImplemented, ProgrammerError
from bones.ts.metatypes import hasT, fitsWithin
from bones.lang.types import _tv
from bones.core.sentinels import Void

from coppertop.dm.core.types import pylist, pydict, pytuple, pydict_keys, pydict_items, pydict_values, pyfunc, pyset, \
    T1, T2, T3, T4, T5, T6, txt, t, index, offset, N, dstruct, dtup, dseq, void, dmap, dframe, matrix, num, py, \
    darray


dict_keys = type({}.keys())
dict_values = type({}.values())

array_ = (N**num) & darray
matrix_ = matrix & darray


# **********************************************************************************************************************
# append
# **********************************************************************************************************************

@coppertop(style=binary)
def append(xs:pylist, x) -> pylist:
    return xs + [x]

@coppertop(style=binary)
def append(xs:pytuple, x) -> pytuple:
    return xs + (x,)

@coppertop(style=binary)
def append(xs:dseq&(N**T1), x:T1) -> dseq&(N**T1):
    xs = dseq(xs)
    xs.append(x)
    return xs


# **********************************************************************************************************************
# appendTo
# **********************************************************************************************************************

@coppertop(style=binary)
def appendTo(x, xs:pylist) -> pylist:
    return xs + [x]

@coppertop(style=binary)
def appendTo(x, xs:pytuple) -> pytuple:
    return xs + (x,)

@coppertop(style=binary)
def appendTo(x, xs:dseq&(N**T1)) -> dseq&(N**T1):
    xs = dseq(xs)
    xs.append(x)
    return xs


# **********************************************************************************************************************
# at - if the selector is N** then this means a depth access - use atAll for breadth
# **********************************************************************************************************************

@coppertop(style=binary)
def at(xs:dseq+pylist+pytuple, o:offset) -> py:
    return xs[o]

@coppertop(style=binary)
def at(xs:dseq+pylist+pytuple, i:index):
    return xs[i - 1]

@coppertop(style=binary)
def at(s:pydict+dmap, k:txt):
    return s[k]

@coppertop(style=binary)
def at(s:py, k:txt):
    return s[k]

@coppertop(style=binary)
def at(s:pydict+dmap, ks:pylist):
    for k in ks:
        s = s[k]
    return s

@coppertop(style=binary)
def at(xs:pylist+pytuple, os:pylist):
    print('A WARNING')
    answer = []
    for o in os:
        answer.append(xs[o])
    return answer

@coppertop(style=binary)
def at(xs:pylist, s1:offset, s2: offset):
    return xs[s1:s2]

@coppertop(style=binary)
def at(a:dframe, f:txt) -> (N**T1)&darray:
    return a[f]

@coppertop(style=binary)
def at(a:(N**T1)[dframe], f:txt) -> (N**N**T2)[darray]:
    # T2 is a column in  the struct T1
    return a[f]

@coppertop(style=binary)
def at(a:dframe, o:offset) -> dstruct:
    items = [(f, a[f][o]) for f in a._keys()]
    return dstruct(items)

@coppertop(style=binary)
def at(a:dframe, i:index) -> dstruct:
    items = [(f, a[f][i-1]) for f in a._keys()]
    return dstruct(items)

@coppertop(style=binary)
def at(a:(N**T1)[dframe], o:offset):  # -> T1:
    # answers a struct if o is an offset or an array if o is a name
    raise NotYetImplemented('(a, o) -> T1')

@coppertop(style=binary)
def at(a:dframe, os:pylist+pytuple) -> dframe:
    items = [(f, a[f][os]) for f in a._keys()]
    return dstruct(items)

@coppertop(style=binary)
def at(xs:(N**T1)&darray, o:t.offset) -> T1:
    return xs[o]

@coppertop(style=binary)
def at(xs:(N**T1)&darray, i:t.index) -> T1:
    return xs[i-1]

@coppertop(style=binary)
def at(xs:(N**T1)&darray, os:pylist) -> (N**T1)&darray:
    return xs[os]


# **********************************************************************************************************************
# atAll - breadth access
# **********************************************************************************************************************

@coppertop(style=binary)
def atAll(xs:pydict, os:pylist+pytuple):
    answer = []
    for o in os:
        answer.append(xs[o])
    return answer


# **********************************************************************************************************************
# atAllPut - breadth access
# **********************************************************************************************************************

@coppertop(style=ternary)
def atAllPut(xs:pydict, ks:pylist+pytuple, vs:pylist+pytuple) -> pydict:
    raise NotYetImplemented()


# **********************************************************************************************************************
# atCol
# A atCol 1
# **********************************************************************************************************************

@coppertop(style=binary)
def atCol(a: matrix & darray, o:offset) -> matrix & darray:
    return a[:, [o]]

@coppertop(style=binary)
def atCol(a: matrix & darray, i:index) -> matrix & darray:
    return a[:, [i - 1]]


# **********************************************************************************************************************
# atColPut
# A atColPut 1 (1,2,3)
# **********************************************************************************************************************

@coppertop(style=ternary)
def atColPut(m, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atIfNone
# map at: `fred ifNone: missing
# **********************************************************************************************************************

@coppertop(style=ternary)
def atIfNone(m, k, default):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atIfNonePut
# map at: `fred ifNonePut: default
# **********************************************************************************************************************

@coppertop(style=ternary)
def atIfNonePut(m, k, default):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atPut
# **********************************************************************************************************************

@coppertop(style=ternary)
def atPut(s:dstruct, name:txt, value) -> dstruct:
    s = dstruct(s)
    s[name] = value
    return s

@coppertop(style=ternary)
def atPut(m:(T1**T2)[dstruct][T3], ks:(N**T1)[pylist], v:T2) -> (T1**T2)[dstruct][T3]:
    for k in ks._v:
        m[k] = v
    return m

@coppertop(style=ternary)
def atPut(a:dframe, o:offset, row:dstruct) -> dframe:
    raise NotYetImplemented()

@coppertop(style=ternary)
def atPut(a:dframe, f:txt, col:(N**T1)[darray]) -> dframe:
    a[f] = col
    return a

@coppertop(style=ternary)
def atPut(m:pydict, k:T1, v:T2) -> pydict:
    m = dict(m)
    m[k] = v
    return m

@coppertop(style=ternary)
def atPut(m:dmap, k, v) -> dmap:
    raise NotYetImplemented()
    m[k] = v
    return m

@coppertop(style=ternary)
def atPut(xs:pylist, iOrIs, yOrYs) -> pylist:
    # immutable??
    # xs = list(xs)
    if isinstance(iOrIs, (list, tuple)):
        for fromI, toI in enumerate(iOrIs):
            xs[toI] = yOrYs[fromI]
    else:
        xs[iOrIs] = yOrYs
    return xs


# **********************************************************************************************************************
# atRemain
# **********************************************************************************************************************

@coppertop(style=binary)
def atRemain(m, o:offset):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atRow
# **********************************************************************************************************************

@coppertop(style=binary)
def atRow(m, o:offset):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atRowPut
# **********************************************************************************************************************

@coppertop(style=ternary)
def atRowPut(m, o:offset, row):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atSlice
# (1,2,3)(0:1) == (1)   // in bones:
# (`a,`b,`c) 1 == `a    // in bones
# so we don't want to reuse at
# **********************************************************************************************************************

@coppertop(style=binary)
def atSlice(m, s):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atSlicePut
# **********************************************************************************************************************

@coppertop(style=binary)
def atSlicePut(m, s, y):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atSlices
# **********************************************************************************************************************

@coppertop(style=binary)
def atSlices(m, ss):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atSlicesPut
# **********************************************************************************************************************

@coppertop(style=binary)
def atSlicesPut(m, ss, y):
    raise NotYetImplemented()


# **********************************************************************************************************************
# atSlot
# **********************************************************************************************************************

@coppertop(style=binary)
def atSlot(s: dstruct, k: txt):
    return s[k]


# **********************************************************************************************************************
# atSlotPut
# **********************************************************************************************************************

@coppertop(style=ternary)
def atSlotPut(s:dstruct, name:txt, value) -> dstruct:
    s = dstruct(s)
    s[name] = value
    return s


# **********************************************************************************************************************
# both
# **********************************************************************************************************************

@coppertop(style=ternary)
def both(a:pylist+pydict_items, f:pyfunc, b:pylist+pydict_items) -> pylist:
    return [f(x, y) for (x, y) in builtins.zip(a, b)]

@coppertop(style=ternary)
def both(a:pydict, f:pyfunc, b:pydict) -> pylist:
    answer = []
    for (ak, av), (bk, bv) in zip((a.items(), b.items())):
        answer.append(f(ak, av, bk, bv))
    return answer

@coppertop(style=ternary)
def both(a:dmap, f:pyfunc, b:dmap) -> pylist:
    answer = []
    for (ak, av), (bk, bv) in zip(a.items(), b.items()):
        answer.append(f(ak, av, bk, bv))
    return answer

@coppertop(style=ternary)
def both(a:(T1 ** T2)[dstruct], fn, b:(T1 ** T2)[dstruct]) -> pylist:
    return a._kvs()  \
        >> both  \
        >> (lambda aFV, bFV: fn(aFV[0], aFV[1], bFV[0], bFV[1]))  \
        >> b._kvs()

@coppertop(style=ternary)
def both(a:dstruct, fn, b:dstruct) -> pylist:
    return a._kvs()  \
        >> both  \
        >> (lambda aFV, bFV: fn(aFV[0], aFV[1], bFV[0], bFV[1]))  \
        >> b._kvs()

@coppertop(style=ternary)
def both(a:(T1 ** T2)[dstruct][T3], fn, b:(T1 ** T2)[dstruct][T3]) -> pylist:
    return a._kvs()  \
        >> both  \
        >> (lambda aFV, bFV: fn(aFV[0], aFV[1], bFV[0], bFV[1]))  \
        >> b._kvs()

@coppertop(style=ternary)
def both(a:dstruct[T1], fn, b:dstruct[T2]) -> pylist:
    return a._kvs()  \
        >> both  \
        >> (lambda aFV, bFV: fn(aFV[0], aFV[1], bFV[0], bFV[1]))  \
        >> b._kvs()

@coppertop(style=ternary)
def both(a:(T1 ** T2)[dstruct][T3], fn:pyfunc, b:(T4 ** T5)[dstruct][T6]) -> pylist:
    return a._kvs()  \
        >> both  \
        >> (lambda aFV, bFV: fn(aFV[0], aFV[1], bFV[0], bFV[1]))  \
        >> b._kvs()

@coppertop(style=ternary)
def both(a: matrix&darray, f, b:matrix&darray) -> matrix&darray:
    with np.nditer([a, b, None]) as it:
        for x, y, z in it:
            z[...] = f(x,y)
        return it.operands[2].view(matrix&darray)


# **********************************************************************************************************************
# centerCols
# **********************************************************************************************************************

@coppertop
def centerCols(panel:matrix&darray) -> matrix&darray:
    return panel - np.mean(panel, 0).reshape((1, panel.shape[1]))


# **********************************************************************************************************************
# collect
# **********************************************************************************************************************

@coppertop(style=binary)
def collect(xs, f) -> pylist:
    return [f(x) for x in xs]

@coppertop(style=binary)
def collect(xs:pylist+pydict_keys+pydict_values+pytuple, f) -> pylist:
    return [f(x) for x in xs]

@coppertop(style=binary)
def collect(xs:pyset, f) -> pyset:
    return set([f(x) for x in xs])

@coppertop(style=binary)
def collect(a:dmap, fn2) -> dmap:
    answer = dmap()
    for f, v in a._kvs():
        answer[f] = fn2(f, v)
    return answer

@coppertop(style=binary)
def collect(a:dframe, fn1):
    inputsAndOutput = [x for x in a._values()] + [None]
    with np.nditer(inputsAndOutput) as it:
        for vars in it:
            vars[-1][...] = fn1(*vars[:-1])
        return it.operands[len(inputsAndOutput) - 1].view(dtup)

@coppertop(style=binary)
def collect(xs: pydict_items, f) -> pylist:
    return [f(k, v) for k, v in xs]

def _collectHelper(xs:(N**T1)[dseq], f:T1^T2, tByT) -> dict:
    t1 = tByT[T1]
    if isinstance(f, (jones._pfn)):
        if f.num_tbc != 1: raise Exception()
        tArgs = [typeOf(arg) for arg in f.args]
        tArgs[f.o_tbc[0]] = t1
        tArgs = tuple(tArgs)
    else:
        tArgs = (t1,)
    fn, tByT_f, hasValue = f.d.getOverload(len(tArgs)).selectFunction(*tArgs)
    t2 = fn.tRet
    if hasT(t2):
        raise NotYetImplemented()
    answer = dict(tByT)
    answer[T2] = t2
    return answer

@coppertop(style=binary, typeHelper=_collectHelper)
def collect(xs:(N**T1)[dseq], f:T1^T2, tByT) -> (N**T2)[dseq]:
    fxs = [f(x) for x in xs]
    return dseq((N**tByT[T2])[dseq], fxs)

@coppertop(style=binary, typeHelper=_collectHelper)
def collect(xs:(N**T1)[dseq][T3], f:T1^T2, tByT) -> (N**T2)[dseq][T3]:
    fxs = [f(x) for x in xs]
    return dseq((N**tByT[T2])[dseq, tByT[T3]], fxs)


# **********************************************************************************************************************
# collectV
# **********************************************************************************************************************

@coppertop(style=binary)
def collectV(a:dmap, fn1) -> pylist:
    answer = list()
    for v in a._values():
        answer.append(fn1(v))
    return answer


# **********************************************************************************************************************
# count
# **********************************************************************************************************************

@coppertop
def count(x:dstruct) -> t.count:
    return len(x._keys()) | t.count

@coppertop
def count(x) -> t.count:
    return len(x) | t.count

@coppertop
def count(x:txt+pylist+pytuple+pyset+pydict_keys+pydict_values) -> t.count:
    return len(x) | t.count

@coppertop
def count(m:matrix&darray) -> t.count:
    nr, nc = m.shape
    return nr | t.count

@coppertop
def count(a:array_) -> t.count:
    assert a.ndim == 1
    return a.shape[0] | t.count


# **********************************************************************************************************************
# countIf
# **********************************************************************************************************************

@coppertop(style=binary)
def countIf(xs:pylist+pytuple+pyset+pydict_keys+pydict_values, fn:pyfunc) -> t.count:
    c = 0
    for x in xs:
        c += fn(x)
    return c | t.count


# **********************************************************************************************************************
# diff
# **********************************************************************************************************************

@coppertop
def diff(a:array_):
    assert a.ndim == 1
    return np.diff(a)


# **********************************************************************************************************************
# diffCols
# **********************************************************************************************************************

@coppertop
def diffCols(p:matrix):
    return np.diff(p,axis=1)


# **********************************************************************************************************************
# diffRows
# **********************************************************************************************************************

@coppertop
def diffRows(p:matrix):
    return np.diff(p,axis=0)


# **********************************************************************************************************************
# distinct
# **********************************************************************************************************************

@coppertop
def distinct(x:pylist) -> pyset:
    return set(x)


# **********************************************************************************************************************
# do
# **********************************************************************************************************************

@coppertop(style=binary)
def do(xs:pylist+pydict_keys+pydict_values+pytuple, f) -> void:
    [f(x) for x in xs]
    return Void


# **********************************************************************************************************************
# drop - drops elements from a N**T2 or a T1**T2
#        three cases of overload 1) drop count, 2) drop N/T1 or Ns/T1s 3) drop T2 or T2s
#        this becomes ambiguous when T1 == T2 and in python we have to peek into the args :(, in bones we don't :)
#        we could distinguish by having dropV as a companion - something to think about
# **********************************************************************************************************************

@coppertop(style=binary)
def drop(xs:(N**T1)[pylist], ks:(N**T2)[pylist]) -> (N**T1)[pylist]:
    raise ProgrammerError("Don't need to box pylist now we have dseq")
    # answer = []
    # for x in xs._v:
    #     if x not in ks._v:
    #         answer.append(x)
    # return _tv(xs._t, answer)

@coppertop(style=binary)
def drop(xs:(N**T1)[dseq][T2], n:t.count, tByT) -> (N**T1)[dseq][T2]:
    if n >= 0:
        return xs[n:]
    else:
        raise xs[:n]

@coppertop(style=binary)
def drop(xs: (N ** T1)[dseq], n: t.count, tByT) -> (N ** T1)[dseq]:
    if n >= 0:
        return xs[n:]
    else:
        raise xs[:n]

@coppertop(style=binary)
def drop(xs:pylist+pydict_keys, ks:pylist) -> pylist:
    answer = []
    if isinstance(ks[0], (builtins.str, txt)):
        for x in xs:
            if x not in ks:
                answer.append(x)
    elif isinstance(ks[0], int):
        for o, e in enumerate(xs):
            if o not in ks:
                answer.append(e)
    else:
        raise NotYetImplemented()
    return answer

@coppertop(style=binary)
def drop(xs:pylist, n) -> pylist:    #(N**T1(im), count)-> N**T1(im)
    if n > 0:
        return xs[n:]
    else:
        raise NotYetImplemented('drop(xs:pylist, n:count) -> pylist')

@coppertop(style=binary)
def drop(xs:pylist, n:t.count) -> pylist:    #(N**T1(im), count)-> N**T1(im)
    if n > 0:
        return xs[n:]
    else:
        raise NotYetImplemented('drop(xs:pylist, n:count) -> pylist')

@coppertop(style=binary)
def drop(xs:pytuple, n:t.count) -> pytuple:    #(N**T1(im), count)-> N**T1(im)
    if n > 0:
        return xs[n:]
    else:
        raise NotYetImplemented('drop(xs:txt, n:count) -> txt')

@coppertop(style=binary)
def drop(xs:pytuple, n) -> pytuple:    #(N**T1(im), py)-> N**T1(im)
    if n > 0:
        return xs[n:]
    else:
        raise NotYetImplemented('drop(xs:txt, n:count) -> txt')

@coppertop(style=binary)
def drop(xs:pydict_keys+pydict_values, n:t.count) -> pylist:    #(N**T1(im), count)-> N**T1(im)
    if n > 0:
        return list(xs)[n:]
    else:
        raise NotYetImplemented('drop(xs:txt, n:count) -> txt')

@coppertop(style=binary)
def drop(xs:txt, n:t.count) -> txt:     #(N**T1(txt), count)-> N**T1(txt)
    if n > 0:
        return xs[n:]
    else:
        raise NotYetImplemented('drop(xs:txt, n:count) -> txt')

@coppertop(style=binary)
def drop(xs:pylist, ss:pytuple) -> pylist:
    s1, s2 = ss
    if s1 is Ellipsis:
        if s2 is Ellipsis:
            return []
        else:
            return xs[s2:]
    else:
        if s2 is Ellipsis:
            return xs[:s1]
        else:
            raise NotYetImplemented()

@coppertop(style=binary)
def drop(d:pydict, ks: pylist) -> pydict:
    return {k:k for k, v in d.items() if k not in ks}

@coppertop(style=binary)
def drop(d:pydict, k) -> pydict:
    answer = dict(d)
    del answer[k]
    return answer

@coppertop(style=binary)
def drop(d:pydict, k:txt) -> pydict:
    return {k2:d[k2] for k2 in d.keys() if k2 != k}

@coppertop(style=binary)
def drop(s:dmap, keys:pylist) -> dmap:
    # keys may be a list[str] or list[int]
    answer = dmap(s)
    if not keys: return answer
    if type(keys[0]) is builtins.str:
        for k in keys:
            del answer[k]
    elif type(keys[0]) is int:
        raise NotImplementedError()
    else:
        raise TypeError(f'Unhandled type list[{str(type(keys[0]))}]')
    return answer

@coppertop(style=binary)
def drop(s:dmap, name:txt) -> dmap:
    answer = dmap(s)
    del answer[name]
    return answer

@coppertop(style=binary)
def drop(f:dframe, k:txt) -> dframe:
    return dframe({k_:f[k_] for k_ in f >> keys >> drop >> k})

@coppertop(style=binary)
def drop(f:dframe, n:t.count) -> dframe:
    if n >= 0:
        return dframe({k:f[k][n:] for k in f._keys()})
    else:
        firstCol = None
        for firstCol in f._values():
            break
        s1 = firstCol.shape[0] - n
        return dframe({k:f[k][s1:] for k in f._keys()})

@coppertop(style=binary)
def drop(f:dframe, isOrKs:pylist) -> dframe:
    if not isOrKs:
        return f
    elif isinstance(isOrKs[0], str):
        # sequence( of strings
        ks = [k for k in f._keys() if k not in isOrKs]
        return dframe({k:f[k] for k in ks})
    elif isinstance(isOrKs[0], int):
        raise NotYetImplemented()
    else:
        raise TypeError()

@coppertop(style=binary)
def drop(f:dframe, ss:pytuple) -> dframe:
    raise NotYetImplemented()

@coppertop(style=binary)
def drop(xs:(N**T1)&darray, c:t.count) -> (N**T1)&darray:
    return xs[c:]


# **********************************************************************************************************************
# dropCol
# A dropCol 1
# **********************************************************************************************************************

@coppertop(style=binary)
def dropCol(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# dropColRemain
# A dropColRemain 1
# **********************************************************************************************************************

@coppertop(style=binary)
def dropColRemain(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# dropCols
# **********************************************************************************************************************

@coppertop(style=binary)
def dropCols(m:matrix&darray, n:t.count):
    return m[:,n:]


# **********************************************************************************************************************
# dropRow
# A dropRow 1
# **********************************************************************************************************************

@coppertop(style=binary)
def dropRow(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# dropRemain
# A dropRemain 1
# **********************************************************************************************************************

@coppertop(style=binary)
def dropRemain(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# dropRowRemain
# A dropRowRemain 1
# **********************************************************************************************************************

@coppertop(style=binary)
def dropRowRemain(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# dropRows
# **********************************************************************************************************************

@coppertop(style=binary)
def dropRows(m:matrix&darray, n:t.count):
    if n >= 0:
        return m[n:,:]
    else:
        raise NotYetImplemented()


# **********************************************************************************************************************
# dropSlot
# **********************************************************************************************************************

@coppertop(style=binary)
def dropSlot(s:dstruct, name:txt) -> dstruct:
    answer = dstruct(s)
    answer._pop(name, None)
    return answer


# **********************************************************************************************************************
# dropSlots
# **********************************************************************************************************************

@coppertop(style=binary)
def dropSlots(s:dstruct, names:pylist) -> dstruct:
    answer = dstruct(s)
    for name in names:
        answer._pop(name, None)
    return answer


# **********************************************************************************************************************
# eachCol_
# TODO use sequence instead
# **********************************************************************************************************************

@coppertop
def eachCol_(m: matrix & darray) -> pylist:
    answer = []
    nr, nc = m.shape
    for i in range(nc):
        answer.append(m[:,[i]])
    return answer


# **********************************************************************************************************************
# eachRow_
# TODO use sequence instead
# **********************************************************************************************************************

@coppertop
def eachRow_(m: matrix & darray) -> pylist:
    answer = []
    nr, nc = m.shape
    for i in range(nc):
        answer.append(m[[i],:])
    return answer


# **********************************************************************************************************************
# first
# **********************************************************************************************************************

@coppertop
def first(a:array_) -> num:
    return float(a[0])

@coppertop
def first(a:dframe) -> dframe:
    # answers first row
    raise NotYetImplemented()

@coppertop
def first(x:pylist+pytuple):
    return x[0]

@coppertop
def first(xs:pydict_values+pydict_keys+pydict_items + collections.abc.ValuesView+collections.abc.KeysView+collections.abc.ItemsView):
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    for x in xs:
        return x

@coppertop
def first(f:dframe) -> dframe:
    return dframe({k:f[k][[0]] for k in f._keys()})


# **********************************************************************************************************************
# firstLast
# **********************************************************************************************************************

@coppertop
def firstLast(a:dframe) -> dframe:
    # answers first row
    raise NotYetImplemented()

@coppertop
def firstLast(x:pylist+pytuple) -> pytuple:
    return x[0], x[-1]

@coppertop
def firstLast(x:(N**T1)&darray) -> (N**T1)&darray:
    return x[[0,-1]]


# **********************************************************************************************************************
# hjoin
# A hjoin B
# **********************************************************************************************************************

@coppertop(style=binary)
def hjoin(a:darray&matrix, b:darray&matrix) -> darray&matrix:
    aShape = a.shape; bShape = b.shape
    if aShape[0] != bShape[0]: raise ValueError('A and B are different heights!')
    return (darray&matrix)(np.append(a, b, axis=1))


# **********************************************************************************************************************
# hjoinAll
# A hjoinAll
# **********************************************************************************************************************

@coppertop
def hjoinAll(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# icollect
# **********************************************************************************************************************

@coppertop(style=binary)
def icollect(xs:pylist, f2) -> pylist:
    return [f2(i, x) for (i, x) in enumerate(xs)]


# **********************************************************************************************************************
# indexOf
# **********************************************************************************************************************

@coppertop
def indexOf(xs, x):
    raise NotYetImplemented()


# **********************************************************************************************************************
# indexesOf
# **********************************************************************************************************************

@coppertop
def indexesOf(xs, x):
    answer = []
    for i, e in enumerate(xs):
        if x == e:
            answer.append(i)
    return answer


# **********************************************************************************************************************
# inject
# **********************************************************************************************************************

@coppertop(style=binary)
def inject(xs:pylist, seed, f2):
    prior = seed
    for x in xs:
        prior = f2(prior, x)
    return prior

@coppertop(style=binary)
def inject(s:dmap, seed, f3):
    prior = seed
    for f, v in s._kvs():
        prior = f3(prior, f, v)
    return prior


# **********************************************************************************************************************
# interleave
# **********************************************************************************************************************

@coppertop(style=binary)
def interleave(xs:pylist+pytuple, b) -> pylist:
    answer = xs[0]
    for x in xs[1:]:
        answer = answer >> join >> b >> join >> x
    return answer

@coppertop(style=binary)
def interleave(a:(N**T1)[dseq], b: T1) -> (N**T1)[dseq]:
    raise NotYetImplemented()

@coppertop(style=binary)
def interleave(a:(N**T1)[dseq], b: (N**T1)[dseq]) -> (N**T1)[dseq]:
    raise NotYetImplemented()

@coppertop(style=binary)
def interleave(xs:N**txt, sep:txt) -> txt:
    # ['hello', 'world'] >> joinAll(_,' ')
    return sep.join(xs)

@coppertop(style=binary)
def interleave(xs:pylist+pytuple, sep:txt) -> txt:
    return sep.join(xs)


# **********************************************************************************************************************
# intersects
# **********************************************************************************************************************

@coppertop(style=binary)
def intersects(a, b):
    if not isinstance(a, (list, tuple, set, dict_keys, dict_values)):
        if not isinstance(b, (list, tuple, set, dict_keys, dict_values)):
            return a == b
        else:
            return a in b
    else:
        if not isinstance(b, (list, tuple, set, dict_keys, dict_values)):
            return b in a
        else:
            for e in a:
                if e in b:
                    return True
            return False


# **********************************************************************************************************************
# join
# **********************************************************************************************************************

@coppertop(style=binary)
def join(xs:pylist, ys:pylist) -> pylist:
    return xs + ys

@coppertop(style=binary)
def join(s1:txt, s2:txt) -> txt:
    return s1 + s2

@coppertop(style=binary)
def join(s1:txt[T1], s2:txt[T1], tByT) -> txt[T1]:
    return s1 + s2

@coppertop(style=binary)
def join(d1:pydict, d2:pydict) -> pydict:
    answer = dict(d1)
    for k, v in d2.items():
        if k in answer:
            raise KeyError(f'{k} already exists in d1 - use underride or override to merge (rather than join) two pydicts')
        answer[k] = v
    return answer

@coppertop(style=binary)
def join(xs:pylist, ys:pydict_keys) -> pylist:
    return xs + list(ys)

@coppertop(style=binary)
def join(xs:(N**T1)[dseq], ys:(N**T1)[dseq], tByT) -> (N**T1)[dseq]:
    return dseq((N**(tByT[T1]))[dseq], xs.data + ys.data)


# **********************************************************************************************************************
# joinAll
# **********************************************************************************************************************

@coppertop
def joinAll(xs:N**txt) -> txt:
    return ''.join(xs)

@coppertop
def joinAll(xs:N**txt, sep:txt) -> txt:
    return sep.join(xs)

@coppertop
def joinAll(xs:pylist+pytuple) -> txt + ((N**T1)[dseq]) + pylist + pytuple:
    # could be a list of strings or a list of (N**T1) & dseq
    # answer a string if no elements
    if not xs:
        return ''
    typeOfFirst = typeOf(xs[0])
    if fitsWithin(typeOfFirst, txt):
        return ''.join(xs)
    elif fitsWithin(typeOfFirst, (N**T1)[dseq]):
        elements = []
        for x in xs:
            # could check the type of each list using metatypes.fitsWithin
            elements.extend(x.data)
        return dseq(xs[0]._t, elements)
    elif fitsWithin(typeOfFirst, pylist):
        answer = []
        for e in xs:
            answer += e
        return answer
    elif fitsWithin(typeOfFirst, pytuple):
        answer = ()
        for e in xs:
            answer += e
        return answer


# **********************************************************************************************************************
# keys
# **********************************************************************************************************************

@coppertop
def keys(d:pydict) -> pylist:     # (T1**T2)&map -> (N**T1)&pylist
    return list(d.keys())

@coppertop
def keys(m:dmap) -> pylist:
    return list(m.keys())

@coppertop
def keys(x: dmap[T1]) -> pylist:
    return list(x.keys())

@coppertop
def keys(x:(T1**T2)[dmap][T3]) -> (N**T1)[pylist]:
    return _tv(
        (N**x._t.parent.parent.indexType)[pylist],
        list(x._keys())
    )

@coppertop
def keys(f:dframe) -> pylist:
    return list(f._keys())

@coppertop
def keys(s:(dstruct & T1)+dstruct) -> list: #(N**txt)[pydict_keys]: needs a _tvmap_keys!!!
    return list(s._keys())


# **********************************************************************************************************************
# keys_
# **********************************************************************************************************************

@coppertop
def keys_(d:pydict) -> pydict_keys:     # (T2**T1)(map) -> (N**T1)(iter)
    return d.keys()

@coppertop
def keys_(s:dmap) -> pydict_keys:
    return s._keys()


# **********************************************************************************************************************
# kvs
# **********************************************************************************************************************

@coppertop
def kvs(x:dmap) -> collections.abc.ItemsView:
    return x.items()

@coppertop
def kvs(x:dmap[T1], tByT) -> collections.abc.ItemsView:
    return x.items()

@coppertop
def kvs(x:dstruct) -> pydict_items:
    return x._v._kvs()

@coppertop
def kvs(x:dstruct[T1], tByT) -> pydict_items:
    return x._v._kvs()

@coppertop
def kvs(x:(T1**T2)[dstruct][T3], tByT) -> pydict_items:
    return x._v._kvs()

@coppertop
def kvs(x:(T1**T2)[dstruct]) -> pydict_items:
    return x._v._kvs()

@coppertop
def kvs(x:pydict) -> pydict_items:
    return x.items()


# **********************************************************************************************************************
# last
# **********************************************************************************************************************

@coppertop
def last(f:dframe) -> dframe:
    return dframe({k:f[k][[-1]] for k in f._keys()})

@coppertop
def last(x:pylist+pytuple):
    return x[-1]


# **********************************************************************************************************************
# merge - answers all of A and all of B raising an error if any keys are in common - see also underride and override
# **********************************************************************************************************************

@coppertop(style=binary)
def merge(a:pydict, b:pydict) -> pydict:
    answer = dict(a)
    for k, v in b.items():
        if k in answer:
            raise RuntimeError(f"{k} is already in a")
        else:
            answer[k] = v
    return answer

@coppertop(style=binary)
def merge(a:pydict, b:dstruct) -> pydict:
    answer = dict(a)
    for k, v in b._kvs():
        if k in answer:
            raise RuntimeError(f"{k} is already in a")
        else:
            answer[k] = v
    return answer

@coppertop(style=binary)
def merge(a:dmap, b:dmap) -> dmap:
    answer = dmap(a)
    for k, v in b._kvs():
        if k in answer:
            raise RuntimeError(f"{k} is already in a")
        else:
            answer[k] = v
    return answer

@coppertop(style=binary)
def merge(a:dstruct, b:dstruct) -> dstruct:
    answer = dstruct(a)
    for k, v in b._kvs():
        if k in answer:
            raise RuntimeError(f"{k} is already in a")
        else:
            answer[k] = v
    return answer

@coppertop(style=binary)
def merge(a:dstruct, b:pydict) -> dstruct:
    answer = dstruct(a)
    for k, v in b.keys():
        if k in answer:
            raise RuntimeError(f"{k} is already in a")
        else:
            answer[k] = v
    return answer


# **********************************************************************************************************************
# minus
# **********************************************************************************************************************

@coppertop(style=binary)
def minus(a:pyset, b:pyset+pylist+pydict_keys+pydict_values) -> pyset:
    return a.difference(b)

@coppertop(style=binary)
def minus(a:pylist+pytuple, b:pyset+pylist+pydict_keys+pydict_values) -> pyset:
    return set(a).difference(b)


# **********************************************************************************************************************
# numCols
# **********************************************************************************************************************

@coppertop
def numCols(f: dframe) -> t.count:
    return len(f._keys())

@coppertop
def numCols(x:matrix&darray) -> t.count:
    return x.shape[1] | t.count

@coppertop
def numCols(x:np.ndarray) -> t.count:
    return x.shape[1] | t.count


# **********************************************************************************************************************
# numRows
# **********************************************************************************************************************

@coppertop
def numRows(f: dframe) -> t.count:
    firstCol = None
    for firstCol in f._values():
        break
    return firstCol.shape[0]

@coppertop
def numRows(x:matrix&darray) -> t.count:
    return x.shape[0] | t.count

@coppertop
def numRows(x:np.ndarray) -> t.count:
    return x.shape[0] | t.count


# **********************************************************************************************************************
# override - for each in A replace with the one in B if it exists
# **********************************************************************************************************************

@coppertop(style=binary)
def override(a:dstruct, b:dstruct) -> dstruct:
    answer = dstruct(a)
    for k, v in b._kvs():
        if k in answer:
            answer[k] = v
        # answer._setdefault(k, v)      # this doesn't respect insertion order!!
    return answer


# **********************************************************************************************************************
# prepend
# **********************************************************************************************************************

@coppertop(style=binary)
def prepend(xs:pylist, x) -> pylist:
    return [x] + xs

@coppertop(style=binary)
def prepend(xs:pytuple, x) -> pytuple:
    return (x,) + xs

@coppertop(style=binary)
def prepend(xs:(N**T1)&dseq, x:T1) -> (N**T1)&dseq:
    xs = dseq(xs)
    xs.insert(0, x)
    return xs


# **********************************************************************************************************************
# prependTo
# **********************************************************************************************************************

@coppertop(style=binary)
def prependTo(x, xs:pylist) -> pylist:
    return [x] + xs

@coppertop(style=binary)
def prependTo(x, xs:pytuple) -> pytuple:
    return (x,) + xs

@coppertop(style=binary)
def prependTo(x:T1, xs:(N**T1)&dseq) -> (N**T1)&dseq:
    xs = dseq(xs)
    xs.insert(0, x)
    return xs


# **********************************************************************************************************************
# rename
# **********************************************************************************************************************

@coppertop(style=ternary)
def rename(d:pydict, old, new):
    d = dict(d)
    d[new] = d.pop(old)
    return d

@coppertop(style=ternary)
def rename(d:dmap, old, new):
    d = dmap(d)
    d[new] = d._pop(old)
    return d


# **********************************************************************************************************************
# replace
# **********************************************************************************************************************

@coppertop(style=ternary)
def replace(d:dmap, f:txt, new):
    d = dmap(d)
    d[f] = new
    return d

@coppertop(style=ternary)
def replace(d:pydict, f:txt, new):
    d = dict(d)
    d[f] = new
    return d


# **********************************************************************************************************************
# scalarProduct aka innerProduct, dotProduct - scalarProduct is selected here as it conveys return type
# **********************************************************************************************************************

@coppertop(style=binary)
def scalarProduct(A:matrix&darray, B:matrix&darray) -> num:
    return float(np.dot(A, B))


# **********************************************************************************************************************
# select - https://en.wikipedia.org/wiki/Filter_(higher-order_function)
# **********************************************************************************************************************

@coppertop(style=binary)
def select(d:pydict, f2) -> pydict:
    filteredKVs = []
    for k, v in d.items():
        if f2(k, v): filteredKVs.append((k,v))
    return dict(filteredKVs)

@coppertop(style=binary)
def select(d:dmap, f2) -> dmap:
    filteredKVs = []
    for k, v in d._kvs():
        if f2(k, v): filteredKVs.append((k,v))
    return dmap(filteredKVs)

@coppertop(style=binary)
def select(pm:dstruct, f2) -> dstruct:
    filteredKVs = []
    for k, v in pm._kvs():
        if f2(k, v): filteredKVs.append((k,v))
    return dstruct(pm._t, filteredKVs)

@coppertop(style=binary)
def select(pm:(T1**T2)[dstruct], f2) -> (T1**T2)[dstruct]:
    filteredKVs = []
    for k, v in pm._kvs():
        if f2(k, v): filteredKVs.append((k,v))
    return dstruct(pm._t, filteredKVs)

@coppertop(style=binary)
def select(pm:(T1**T2)[dstruct][T3], f2) -> (T1**T2)[dstruct][T3]:
    filteredKVs = []
    for k, v in pm._v._kvs():
        if f2(k, v): filteredKVs.append((k,v))
    return dstruct(pm._t, filteredKVs)

@coppertop(style=binary)
def select(xs:pylist+pydict_keys+pydict_values, f) -> pylist:
    return [x for x in xs if f(x)]

@coppertop(style=binary)
def select(xs:pytuple, f) -> pytuple:
    return tuple(x for x in xs if f(x))

@coppertop(style=binary)
def select(a:dframe, fn1) -> dframe:
    fs = a._keys()
    cols = [c for c in a._values()] #a >> values >> std.collect >> partial(lambda c: c)
    # collate the offsets that fn1 answers true
    os = []
    for o in range(cols[0].shape[0]):
        r = dstruct(builtins.zip(fs, [c[o] for c in cols]))
        if fn1(r): os.append(o)
    # create new cols from the old cols and the offsets
    newCols = [c[os] for c in cols]
    return dframe(builtins.zip(fs, newCols))

@coppertop(style=binary)
def select(z:builtins.zip, f:pyfunc):
    answer = []
    for e in z:
        if f(*e): answer.append(e)
    return answer


# **********************************************************************************************************************
# setOrder - reorders the keyed collection a with the keys in ks - keeping the order of any missing at the end
# **********************************************************************************************************************

@coppertop(style=binary)
def setOrder(a, ks):
    raise NotYetImplemented()


# **********************************************************************************************************************
# shape
# **********************************************************************************************************************

@coppertop
def shape(x:matrix&darray) -> pytuple:
    return x.shape

@coppertop
def shape(f:dframe) -> pytuple:
    firstCol = None
    for firstCol in f._values():
        break
    return (firstCol.shape[0], len(f._keys()))


# **********************************************************************************************************************
# shift
# **********************************************************************************************************************

@coppertop(style=binary)
def shift(m:array_, n:t.count) -> array_:
    if n == 0:
        return m
    elif n > 0:
        answer = np.roll(m, n)
        answer[0:n] = 0
        return answer
    else:
        raise NotYetImplemented()


# **********************************************************************************************************************
# shuffleColsInPlace   - shuffleCol???
# **********************************************************************************************************************

@coppertop
def shuffleColsInPlace(panel:matrix&darray) -> matrix&darray:
    for i in range(panel >> numCols):
        ix = np.arange(panel >> numRows)
        np.random.shuffle(ix)      # destructive
        panel[:,i] = panel[:,i][ix]
    return panel


# **********************************************************************************************************************
# soleElement
# **********************************************************************************************************************

@coppertop
def soleElement(a:pyset):
    # https://stackoverflow.com/questions/1619514/how-to-extract-the-member-from-single-member-set-in-python
    answer, = a
    return answer


# **********************************************************************************************************************
# sort
# **********************************************************************************************************************

@coppertop
def sort(x:pydict) -> pydict:
    return dict(sorted(x.items(), key=None, reverse=False))

@coppertop
def sort(x:dstruct) -> dstruct:
    return dstruct(sorted(x._kvs(), key=None, reverse=False))

@coppertop
def sort(x:dmap) -> dmap:
    return dmap(sorted(x._kvs(), key=None, reverse=False))

@coppertop
def sort(x:pylist+pyset) -> pylist:
    return sorted(x, key=None, reverse=False)


# **********************************************************************************************************************
# sortRev
# **********************************************************************************************************************

@coppertop
def sortRev(x:pylist+pyset) -> pylist:
    return sorted(x, key=None, reverse=True)

@coppertop
def sortRev(x:pydict) -> pydict:
    return dict(sorted(x.items(), key=None, reverse=True))

@coppertop
def sortRev(x:dmap) -> dmap:
    raise NotYetImplemented()

@coppertop
def sortRev(x:dstruct) -> dstruct:
    raise NotYetImplemented()


# **********************************************************************************************************************
# sortRevUsing
# **********************************************************************************************************************

@coppertop(style=binary)
def sortRevUsing(x:pylist+pyset, key:pyfunc) -> pylist:
    return sorted(x, key=key, reverse=True)

@coppertop(style=binary)
def sortRevUsing(x:pydict, key:pyfunc) -> pydict:
    return dict(sorted(x.items(), key=key, reverse=True))


# **********************************************************************************************************************
# sortUsing
# **********************************************************************************************************************

@coppertop(style=binary)
def sortUsing(x:pylist+pyset, key:pyfunc) -> pylist:
    return sorted(x, key=key, reverse=False)

@coppertop(style=binary)
def sortUsing(x:pydict, key:pyfunc) -> pydict:
    return dict(sorted(x.items(), key=key, reverse=False))

@coppertop(style=binary)
def sortUsing(soa, f):
    raise NotYetImplemented()


# **********************************************************************************************************************
# split - splits collection a at all the points in b
# [1, 2, 3] >> split >> 1 == [[1], [2], [3]]
# [1, 2, 3] >> split >> 0 == [[], [1], [2, 3]]
# **********************************************************************************************************************

@coppertop(style=binary)
def split(a, b):
    raise NotYetImplemented()


# **********************************************************************************************************************
# splitCol - splits matrix a at all the points in b
# **********************************************************************************************************************

@coppertop(style=binary)
def splitCol(a, b):
    raise NotYetImplemented()


# **********************************************************************************************************************
# splitOn - splits collection a at every point value v is found
# "fred.joe" >> splitOn >> '.' == ['fred', 'joe']  (the '.' is implicit)
# **********************************************************************************************************************

@coppertop(style=binary)
def splitOn(a, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# splitRow - splits matrix a at all the points in b
# **********************************************************************************************************************

@coppertop(style=binary)
def splitRow(a, b):
    raise NotYetImplemented()


# **********************************************************************************************************************
# subsetOf
# **********************************************************************************************************************

@coppertop(style=binary)
def subsetOf(a, b):
    if not isinstance(a, (list, set, tuple, dict_keys, dict_values)):
        if not isinstance(b, (list, set, tuple, dict_keys, dict_values)):
            # 1, 1
            return a == b
        else:
            # 1, 1+
            return a in b
    else:
        if not isinstance(b, (list, set, tuple, dict_keys, dict_values)):
            # 1+, 1
            return False
        else:
            # 1+, 1+
            for e in a:
                if e not in b:
                    return False
            return True


# **********************************************************************************************************************
# T
# **********************************************************************************************************************

@coppertop
def T(A:matrix&darray) -> matrix&darray:
    return A.T


# **********************************************************************************************************************
# take - for type analysis / issues see drop
# **********************************************************************************************************************

@coppertop(style=binary)
def take(a:dframe, k:txt) -> dframe:
    return dframe({k:a[k]})

@coppertop(style=binary)
def take(a:dframe, isOrKs:pylist) -> dframe:
    if not isOrKs:
        return dframe
    elif isinstance(isOrKs[0], (builtins.str, str)):
        return dframe({k:a[k] for k in isOrKs})
    elif isinstance(isOrKs[0], int):
        raise NotYetImplemented()
    else:
        raise TypeError()

@coppertop(style=binary)
def take(a:dframe, ss:pytuple) -> dframe:
    raise NotYetImplemented()

@coppertop(style=binary)
def take(a:dframe, i:t.count) -> dframe:
    if i >= 0:
        return dframe({k:a[k][0:i] for k in a._keys()})
    else:
        return dframe({k:a[k][i:] for k in a._keys()})

@coppertop(style=binary)
def take(a:dframe, isOrKs:pylist) -> dframe:
    if not isOrKs:
        return dframe()
    elif isinstance(isOrKs[0], (str, txt)):
        # sequence( of strings
        return dframe({k:a[k] for k in isOrKs})
    elif isinstance(isOrKs[0], (int, offset)):
        # sequence( of offets
        return dframe({k:at(a[k], isOrKs) for k in a._keys()})
    else:
        raise TypeError()

@coppertop(style=binary)
def take(a:dframe, ss:slice) -> dframe:
    return dframe({k:a[k][ss] for k in a._keys()})

@coppertop(style=binary)
def take(d:pydict, ks:pylist) -> pydict:
    return {k:d[k] for k in ks}

@coppertop(style=binary)
def take(d:pydict, k:txt) -> pydict:
    return {k:d[k]}

@coppertop(style=binary)
def take(d:dstruct, k:txt) -> dstruct:
    return d[k]

@coppertop(style=binary)
def take(xs:pylist, c:t.count) -> pylist:
    if c >= 0:
        return xs[0:c]
    else:
        return xs[c:]

@coppertop(style=binary)
def take(xs:pylist, c) -> pylist:
    if c >= 0:
        return xs[0:c]
    else:
        return xs[c:]

@coppertop(style=binary)
def take(xs:pylist, os:pylist) -> pylist:
    return [xs[o] for o in os]

@coppertop(style=binary)
def take(xs:pylist, ss:pytuple) -> pylist:
    s1, s2 = ss
    if s1 is Ellipsis:
        if s2 is Ellipsis:
            return xs
        else:
            return xs[:s2]
    else:
        if s2 is Ellipsis:
            return xs[s1:]
        else:
            return xs[s1:s2]

@coppertop(style=binary)
def take(xs:(N**T1)&darray, c:t.count) -> (N**T1)&darray:
    if c >= 0:
        return xs[:c]
    else:
        return xs[c:]


# **********************************************************************************************************************
# takeCol
# A takeCol 1
# **********************************************************************************************************************

@coppertop(style=binary)
def takeCol(m:matrix&darray, i:offset):
    return m[:,[i]]


# **********************************************************************************************************************
# takeColRemain
# A takeColRemain 1
# **********************************************************************************************************************

@coppertop(style=binary)
def takeColRemain(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# takeCols
# **********************************************************************************************************************

@coppertop(style=binary)
def takeCols(m:matrix&darray, n:t.count) -> matrix&darray:
    if n >= 0:
        return m[:,0:n]
    else:
        raise NotYetImplemented()


# **********************************************************************************************************************
# takeDiag
# **********************************************************************************************************************

@coppertop
def takeDiag(m: matrix & darray) -> array_:
    return np.diag(m) | array_


# **********************************************************************************************************************
# takeDrop
# **********************************************************************************************************************

@coppertop(style=binary)
def takeDrop(f:dframe, n:t.count):
    t, r = dframe(), dframe()
    for k, v in f._kvs():
        t[k] = v[:n]
        r[k] = v[n:]
    return t, r


# **********************************************************************************************************************
# takeDropUsing
# **********************************************************************************************************************

@coppertop(style=binary)
def takeDropUsing(xs:pytuple, f1):
    selected = []
    rejected = []
    for x in xs:
        if f1(x):
            selected.append(x)
        else:
            rejected.append(x)
    return tuple(selected), tuple(rejected)


# **********************************************************************************************************************
# takePanel
# **********************************************************************************************************************

@coppertop
def takePanel(f:dframe) -> matrix&darray:
    return (matrix&darray)(np.hstack(f >> values))


# **********************************************************************************************************************
# takeRow
# A takeRow 1
# **********************************************************************************************************************

@coppertop(style=binary)
def takeRow(m, i):
    raise NotYetImplemented()


# **********************************************************************************************************************
# takeRowRemain
# A takeRowRemain 1
# **********************************************************************************************************************

@coppertop(style=binary)
def takeRowRemain(X:matrix&darray, i:offset) -> pytuple:
    remain = np.delete(X, i, axis=0)
    take = X[[i],:]
    return take, remain


# **********************************************************************************************************************
# takeRows
# **********************************************************************************************************************

@coppertop(style=binary)
def takeRows(m:matrix&darray, n:t.count) -> matrix&darray:
    if n >= 0:
        return m[:n, :]
    else:
        return m[n:, :]


# **********************************************************************************************************************
# toDiag
# **********************************************************************************************************************

@coppertop
def toDiag(m: array_) -> matrix & darray:
    return (matrix & darray)(np.diag(m))


# **********************************************************************************************************************
# underride
# **********************************************************************************************************************

@coppertop(style=binary)
def underride(a:dstruct, b:dstruct) -> dstruct:
    answer = dstruct(a)
    for k, v in b._kvs():
        if k not in answer:
            answer[k] = v
        # answer._setdefault(k, v)      # this doesn't respect insertion order!!
    return answer

@coppertop(style=binary)
def underride(a:dstruct, b:pydict) -> dstruct:
    answer = dstruct(a)
    for k, v in b.items():
        if k not in answer:
            answer[k] = v
        # answer._setdefault(k, v)      # this doesn't respect insertion order!!
    return answer

@coppertop(style=binary)
def underride(a:pydict, b:pydict) -> pydict:
    answer = dict(a)
    for k, v in b.items():
        if k not in answer:
            answer[k] = v
        # answer._setdefault(k, v)      # this doesn't respect insertion order!!
    return answer


# **********************************************************************************************************************
# values
# **********************************************************************************************************************

@coppertop
def values(x:(T1**T2)[dstruct][T3]) -> (N**T2)[pylist]:
    return _tv(
        (N**x._t.parent.parent.mappedType)[pylist],
        list(x._values())
    )

@coppertop
def values(x:pydict) -> pytuple:
    return tuple(x.values())

@coppertop
def values_(x:pydict) -> pydict_values:
    return x.values()

@coppertop
def values(x:dmap) -> pytuple:
    return tuple(x.values())

@coppertop
def values_(x:dmap[T1]) -> pydict_values:
    return x.values()

@coppertop
def values(a:dframe) -> pytuple:
    return tuple(a._values())

@coppertop
def values_(a:dframe) -> pydict_values:
    return a._values()


# **********************************************************************************************************************
# [1,2,3,4] without [2,3] == [1,4]
# without as python can't easily distinguish drop(N**T1, N**N) from drop(N**T1, N**T1) :(
# **********************************************************************************************************************

@coppertop(style=binary)
def without(xs:pylist+pytuple+pyset, elements:pylist+pytuple+pyset) -> pylist:
    answer = []
    for x in xs:
        if x not in elements:
            answer.append(x)
    return answer

@coppertop(style=binary)
def without(xs:pylist+pytuple+pyset, x) -> pylist:
    answer = []
    for e in xs:
        if e != x:
            answer.append(e)
    return answer

@coppertop(style=binary)
def without(xs:(N**T1)[dseq], x:T1, tByT) -> (N**T1)[dseq]:
    answer = dseq((N**tByT[T1])[dseq])
    for e in xs:
        if e != x:
            answer.append(e)
    return answer


# **********************************************************************************************************************
# XTX - OPEN: move to linalg
# **********************************************************************************************************************

@coppertop
def XTX(x:matrix&darray) -> matrix&darray:
    return x.T @ x


# **********************************************************************************************************************
# XXT
# **********************************************************************************************************************

@coppertop
def XXT(x:matrix&darray) -> matrix&darray:
    return x @ x.T


# **********************************************************************************************************************
# zipAll - can't be same name as Python as different interface, i.e. does not take *args
# **********************************************************************************************************************

@coppertop
def zipAll(x:pylist+pytuple+pydict_keys+pydict_values+pydict_items+py):
    return builtins.zip(*x)
