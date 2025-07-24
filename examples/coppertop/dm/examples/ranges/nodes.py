# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from __future__ import annotations

import sys

if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from coppertop.pipe import *
from coppertop.core import Null, Missing
from coppertop.dm.core import to
from coppertop.dm.core.types import pylist, bool, index, T, T1, T2

if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - imports done')


if not hasattr(sys, '_EMPTY'):
    class _EMPTY:
        def __bool__(self):
            return False
        def __repr__(self):
            # for pretty display in pycharm debugger
            return 'EMPTY'
    sys._EMPTY = _EMPTY()
EMPTY = sys._EMPTY


class IRange: pass


# **********************************************************************************************************************
# Interfaces
# **********************************************************************************************************************

class Simple(IRange):
    # a range that implements empty, front, and popFront

    @property
    def empty(self) -> bool:
        raise NotImplementedError()
    @property
    def front(self):
        raise NotImplementedError()
    def popFront(self):
        raise NotImplementedError()
    def moveFront(self):
        raise NotImplementedError()

    # assignable
    @front.setter
    def front(self, value):
        raise NotImplementedError()

    def __iter__(self):
        return self
    def __next__(self):
        if self.empty: raise StopIteration
        answer = self.front
        self.popFront()
        return answer


class Snappable(Simple):
    # an input range that implements checkpoint in addition to empty, front and popFront
    def snap(self):
        raise NotImplementedError()


class IFwdBwd(Snappable):
    @property
    def back(self):
        raise NotImplementedError()
    def moveBack(self):
        raise NotImplementedError()
    def popBack(self):
        raise NotImplementedError()

    # assignable
    @back.setter
    def back(self, value):
        raise NotImplementedError()


class IIdxFinite(IFwdBwd):
    def moveAt(self, i: int):
        raise NotImplementedError()
    def __getitem__(self, i: index+slice):
        raise NotImplementedError()
    @property
    def length(self) -> index:
        raise NotImplementedError()

    # assignable
    def __setitem__(self, i: int, value):
        raise NotImplementedError()


class IIdxInf(Snappable):
    def moveAt(self, i: int):
        raise NotImplementedError()

    def __getitem__(self, i: int):
        """Answers an element"""
        raise NotImplementedError()


class ISink(IRange):
    # a range that implements put
    def put(self, value):
        """Answers void"""
        raise NotImplementedError()



# **********************************************************************************************************************
# Range implementations
# **********************************************************************************************************************

class EmitWhilesUsing(Snappable):
    # consumes the Snappable range r and emits a While with a snap or r whenever the function changes value
    __slots__ = ['_r', '_fn', '_current']
    def __init__(self, r, fn:T1^T2):
        assert isinstance(r, Snappable)
        self._r = r
        self._fn = fn
        self._current = None if self._r.empty else self._fn(self._r.front)
    @property
    def empty(self):
        return self._r.empty
    @property
    def front(self):
        assert not self._r.empty
        return While(self._r.snap(), self._fn, self._current)
    def popFront(self):
        assert not self._r.empty
        while not self._r.empty and self._fn(self._r.front) == self._current:
            self._r.popFront()
        if not self._r.empty:
            self._current = self._fn(self._r.front)
    def snap(self):
        return EmitWhilesUsing(self._r.snap(), self._fn)
    def __repr__(self):
        return 'EmitWhilesUsing(%s,%s)' % (self._r, self._current)


class Chain(Simple):
    def __init__(self, listOfRanges):
        self.rOfR = listOfRanges >> to >> SrcFromSeq
        if self.rOfR.empty:
            self.curR = None
        else:
            self.curR = self.rOfR.front
            self.rOfR.popFront()
    @property
    def empty(self):
        if self.curR is None: return True
        while self.curR.empty and not self.rOfR.empty:
            self.curR = self.rOfR.front
            self.rOfR.popFront()
        return self.curR.empty
    @property
    def front(self):
        assert not self.curR.empty
        return self.curR.front
    def popFront(self):
        if not self.curR.empty:
            self.curR.popFront()


class ChunkUsingSubRangeGenerator(Snappable):
    def __init__(self, r, fn):
        self._r = r
        self._fn = fn
        self._current = None if self._r.empty else self._fn(self._r)
    @property
    def empty(self):
        return self._r.empty
    @property
    def front(self):
        assert not self._r.empty
        return self._current
    def popFront(self):
        self._current = None if self._r.empty else self._fn(self._r)
    def snap(self) -> Snappable:
        new = ChunkUsingSubRangeGenerator(self._r.snap(), self._fn)
        new._current = None if self._current is None else self._current.snap()
        return new


class FilterUsing(Snappable):
    # consumes the Snappable range r and emits values where fn(front) is True
    __slots__ = ['_r', '_fn']
    def __init__(self, r, fn:T^bool):
        assert isinstance(r, Snappable)
        self._r = r
        self._fn = fn
        while not self._r.empty and not self._fn(self._r.front):
            self._r.popFront()
    @property
    def empty(self):
        return self._r.empty
    @property
    def front(self):
        assert not self._r.empty
        return self._r.front
    def popFront(self):
        self._r.popFront()
        while not self._r.empty and not self._fn(self._r.front):
            self._r.popFront()
    def snap(self):
        return FilterUsing(self._r.snap(), self._fn)
    def __repr__(self):
        return 'FilterUsing(%s)' % (self._r)


class Map(Snappable):
    def __init__(self, r, fn):
        if isinstance(r, Simple):
            self.r = r
        else:
            self.r = SrcFromSeq(r)
        if not callable(fn):
            raise TypeError("RMAP.__init__ fn should be a function but got a %s" % type(fn))
        self.f = fn
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        return self.f(self.r.front)
    def popFront(self):
        self.r.popFront()
    def snap(self):
        return Map(self.r.snap(), self.f)


class FileLines(Simple):
    def __init__(self, f):
        self.f = f
        self.line = self.f.readline()
    @property
    def empty(self):
        return self.line == ''
    @property
    def front(self):
        return self.line
    def popFront(self):
        self.line = self.f.readline()


class LastSink(ISink):
    def __init__(self):
        self.last = Missing
    def put(self, value):
        self.last = value


class ListSink(ISink):
    def __init__(self, list=Missing):
        self.list = [] if list is Missing else list
    def put(self, value):
        self.list.append(value)


class SrcFromSeq(Snappable):
    __slots = ['_seq', '_i']
    def __init__(self, seq):
        self._seq = seq
        self._i = 0
    @property
    def empty(self):
        return self._i >= len(self._seq)
    @property
    def front(self):
        return self._seq[self._i]
    def popFront(self):
        self._i += 1
    def snap(self):
        new = SrcFromSeq(self._seq)
        new._i = self._i
        return new


class SrcUsing(Snappable):
    # adapts a unary function (that takes a position index) into a Snappable range
    __slots__ = ['_fn', '_i', '_current']
    def __init__(self, fn):
        self._fn = fn
        self._i = 0
        self._current = self._fn(self._i)

    @property
    def empty(self):
        return self._current == EMPTY

    @property
    def front(self):
        return self._current

    def popFront(self):
        self._i += 1
        if not self.empty:
            self._current = self._fn(self._i)

    def snap(self):
        new = SrcUsing(self._fn)
        new._i = self._i
        new._current = new._fn(new._i)
        return new

    def repr(self):
        return f'SrcUsing({self._fn})[{self._i}]'


class Take(Snappable):
    def __init__(self, r, n):
        if not isinstance(r, Snappable):
            raise TypeError(str(r))
        self.r = r
        self.n = n
    @property
    def empty(self):
        return self.r.empty or self.n <= 0
    @property
    def front(self):
        assert not self.r.empty
        return self.r.front
    def popFront(self):
        assert not self.empty
        self.r.popFront()
        self.n -= 1
    def snap(self):
        return Take(self.r.snap(), self.n)
    def __repr__(self):
        return 'Take(%s,%s)' % (self.r, self.n)


class Until(Snappable):
    # consumes the Snappable range r until fn(front) == v
    __slots__ = ['_r', '_fn', '_v', '_hasFound']
    def __init__(self, r, fn, v):
        if not isinstance(r, Snappable):
            raise TypeError(str(r))
        self._r = r
        self._fn = fn
        self._v = v
        self._hasFound = False
    @property
    def empty(self):
        return self._r.empty or self._hasFound
    @property
    def front(self):
        assert not self._r.empty
        return self._r.front
    def popFront(self):
        assert not self.empty
        self._hasFound = self._fn(self._r.front) == self._v
        self._r.popFront()
    def snap(self):
        return Until(self._r.snap(), self._fn, self._v)
    def __repr__(self):
        return 'Until(%s,%s)' % (self._r, self._v)


class While(Snappable):
    # consumes the Snappable range r while fn(front) == v
    __slots__ = ['_r', '_fn', '_v']
    def __init__(self, r, fn:T1^T2, v):
        assert isinstance(r, Snappable)
        self._r = r
        self._fn = fn
        self._v = v
    @property
    def empty(self):
        return self._r.empty or self._fn(self._r.front) != self._v
    @property
    def front(self):
        assert not self.empty
        return self._r.front
    def popFront(self):
        assert not self.empty
        self._r.popFront()
    def snap(self):
        return While(self._r.snap(), self._fn, self._v)
    def __repr__(self):
        return 'While(%s)' % self._v


class ZipRagged(Simple):
    """As RZip but input ranges do not need to be of same length, shorter ranges are post padded with Null"""
    def __init__(self, ror):
        self.ror = ror
        ror = ror.snap()
        self.allEmpty = True
        while not ror.empty:
            if not ror.front.empty:
                self.allEmpty = False
                break
    @property
    def empty(self):
        return self.allEmpty
    @property
    def front(self) -> pylist:
        parts = []
        ror = self.ror.snap()
        while not ror.empty:
            subrange = ror.front
            if subrange.empty:
                parts.append(Null)
            else:
                parts.append(subrange.front)
            if not subrange.empty:
                subrange.popFront()
            # ror.popFront()
        return parts
    def popFront(self):
        ror = self.ror.snap()
        self.allEmpty = True
        while not ror.empty:
            subrange = ror.front
            if not subrange.empty:
                subrange.popFront()
                if not subrange.empty:
                    self.allEmpty = False
            ror.popFront()

