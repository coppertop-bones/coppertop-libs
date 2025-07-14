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
from bones.core.sentinels import Null
from coppertop.dm.core import to
from coppertop.dm.core.types import pylist, bool, index

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

class IInputRange(IRange):
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

    # python iterator interface - so we can use ranges in list comprehensions and for loops!!! ugh
    # this is convenient but possibly too convenient and it may muddy things hence the ugly name
    @property
    def _getIRIter(self):
        return IInputRange._Iter(self)

    class _Iter:
        def __init__(self, r):
            self.r = r
        def __iter__(self):
            return self
        def __next__(self):
            if self.r.empty: raise StopIteration
            answer = self.r.front
            self.r.popFront()
            return answer


class IForwardRange(IInputRange):
    # an input range that implements save in addition to empty, front and popFront
    def save(self):
        raise NotImplementedError()


class IBidirectionalRange(IForwardRange):
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


class IRandomAccessFinite(IBidirectionalRange):
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


class IRandomAccessInfinite(IForwardRange):
    def moveAt(self, i: int):
        raise NotImplementedError()

    def __getitem__(self, i: int):
        """Answers an element"""
        raise NotImplementedError()


class IOutputRange(IRange):
    # a range that implements put
    def put(self, value):
        """Answers void"""
        raise NotImplementedError()



# **********************************************************************************************************************
# Range implementations
# **********************************************************************************************************************

class ChunkFROnChangeOf(IForwardRange):
    # chunks the input range on change of a function applied to the front element
    def __init__(self, r, fn):
        assert isinstance(r, IForwardRange)
        self.r = r
        self.fn = fn
        self.lastF = None if self.r.empty else self.fn(self.r.front)
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        assert not self.r.empty
        return ChunkFR(self.r, self.fn, self.lastF)
    def popFront(self):
        assert not self.r.empty
        while not self.r.empty and self.fn(self.r.front) == self.lastF:
            self.r.popFront()
        if not self.r.empty:
            self.lastF = self.fn(self.r.front)
    def save(self):
        return ChunkFROnChangeOf(self.r.save(), self.fn)
    def __repr__(self):
        return 'ChunkFROnChangeOf(%s,%s)' % (self.r, self.curF)


class ChunkFR(IForwardRange):
    # a chunk of a forward range that is defined by a function applied to the front element
    def __init__(self, r, f, curF):
        self.r = r
        self.f = f
        self.curF = curF
    @property
    def empty(self):
        return self.r.empty or self.curF != self.f(self.r.front)
    @property
    def front(self):
        return self.r.front
    def popFront(self):
        assert not self.r.empty
        self.r.popFront()
    def save(self):
        return ChunkFR(self.r.save(), self.f, self.curF)
    def __repr__(self):
        return 'ChunkFR(%s)' % self.curF


class ChainFR(IForwardRange):
    def __init__(self, listOfRanges):
        self.rOfR = listOfRanges >> to >> IndexableFR
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


class ChunkUsingSubRangeGeneratorFR(IForwardRange):
    def __init__(self, r, f):
        self.r = r
        self.f = f
        self.curSR = None if self.r.empty else self.f(self.r)
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        assert not self.r.empty
        return self.curSR
    def popFront(self):
        self.curSR = None if self.r.empty else self.f(self.r)
    def save(self) -> IForwardRange:
        new = ChunkUsingSubRangeGeneratorFR(self.r.save(), self.f)
        new.curSR = None if self.curSR is None else self.curSR.save()
        return new


class FileLineIR(IInputRange):
    def __init__(self, f, stripNL=False):
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


class FnAdapterFR(IForwardRange):
    # adapts a unary function (that takes a position index) into a forward range
    def __init__(self, f):
        self.f = f
        self.i = 0
        self.current = self.f(self.i)

    @property
    def empty(self):
        return self.current == EMPTY

    @property
    def front(self):
        return self.current

    def popFront(self):
        self.i += 1
        if not self.empty:
            self.current = self.f(self.i)

    def save(self):
        new = FnAdapterFR(self.f)
        new.i = self.i
        new.current = new.f(new.i)
        return new

    def repr(self):
        return 'FnAdapterFR(%s)[%s]' % (self.f, self.i)


class IndexableFR(IForwardRange):
    def __init__(self, indexable):
        self.indexable = indexable
        self.i = 0
    @property
    def empty(self):
        return self.i >= len(self.indexable)
    @property
    def front(self):
        return self.indexable[self.i]
    def popFront(self):
        self.i += 1
    def save(self):
        new = IndexableFR(self.indexable.__class__(self.indexable))
        new.i = self.i
        return new


class ListOR(IOutputRange):
    def __init__(self, list):
        self.list = list
    def put(self, value):
        self.list.append(value)


class MapFR(IForwardRange):
    def __init__(self, r, fn):
        if isinstance(r, IInputRange):
            self.r = r
        else:
            self.r = IndexableFR(r)
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
    def save(self):
        return MapFR(self.r.save(), self.f)


class RaggedZipIR(IInputRange):
    """As RZip but input ranges do not need to be of same length, shorter ranges are post padded with Null"""
    def __init__(self, ror):
        self.ror = ror
        ror = ror.save()
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
        ror = self.ror.save()
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
        ror = self.ror.save()
        self.allEmpty = True
        while not ror.empty:
            subrange = ror.front
            if not subrange.empty:
                subrange.popFront()
                if not subrange.empty:
                    self.allEmpty = False
            ror.popFront()


class TakeFR(IForwardRange):
    def __init__(self, r, n):
        if not isinstance(r, IForwardRange):
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
    def save(self):
        return TakeFR(self.r.save(), self.n)
    def __repr__(self):
        return 'TakeFR(%s,%s)' % (self.r, self.n)


class UntilFR(IForwardRange):
    def __init__(self, r, f):
        if not isinstance(r, IForwardRange):
            raise TypeError(str(r))
        self.r = r
        self.f = f
        self.hasFound = False
    @property
    def empty(self):
        return self.r.empty or self.hasFound
    @property
    def front(self):
        assert not self.r.empty
        return self.r.front
    def popFront(self):
        assert not self.empty
        self.hasFound = self.f(self.r.front)
        self.r.popFront()
    def save(self):
        return UntilFR(self.r.save(), self.f)
    def __repr__(self):
        return 'UntilFR(%s,%s)' % (self.r, self.f)

