# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# see https://kotlinlang.org/docs/sequences.html#sequence
# see https://kotlinlang.org/docs/sequences.html#construct


from coppertop.pipe import *
from bones.ts.metatypes import BTUnion
from bones.core.errors import NotYetImplemented
from coppertop.dm.core.types import pylist
from coppertop.dm.examples.ranges.agents import MapFR, UntilFR, ChunkUsingSubRangeGeneratorFR, ChunkUsingFR, \
    EMPTY, IInputRange, IRandomAccessInfinite, TakeFR
from coppertop.dm.core.types import pytuple


@coppertop
def rChain(rs):
    raise NotYetImplemented()

@coppertop(style=binary)
def rChunkUsing(r, f):
    return ChunkUsingFR(r, f)

@coppertop(style=binary)
def rChunkUsingSubRangeGeneratorFR(r, f):
    return ChunkUsingSubRangeGeneratorFR(r, f)

@coppertop
def rDrop(r, n):
    raise NotYetImplemented()

@coppertop
def rDropBack(r, n):
    raise NotYetImplemented()

@coppertop
def rFilter(r, f):
    raise NotYetImplemented()

@coppertop
def rFind(r, value):
    while not r.empty:
        if r.front == value:
            break
        r.popFront()
    return r

@coppertop
def rFnAdapterEager(f):
    answer = []
    i = 0
    while (x := f(i)) != EMPTY:
        answer.append(x)
        i += 1
    return answer

@coppertop
def rFront(r):
    return r.front

@coppertop(style=binary)
def rMap(x, y):
    return MapFR(x, y)

@coppertop
def rMaterialise(r):
    return _materialise(r)

def _materialise(r):
    answer = list()
    while not r.empty:
        e = r.front
        if isinstance(e, IInputRange) and not isinstance(e, IRandomAccessInfinite):
            answer.append(_materialise(e))
            if not r.empty:  # the sub range may exhaust this range
                r.popFront()
        else:
            answer.append(e)
            r.popFront()
    return answer

@coppertop(style=binary)
def rPushAllTo(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return outR

@coppertop(style=binary)
def rPut(r, x):
    return r.put(x)

@coppertop
def rInject(r, seed, f):
    raise NotYetImplemented()

@coppertop(style=binary)
def rTake(r, n):
    return TakeFR(r, n)

@coppertop(style=binary)
def rTakeBack(r, n):
    raise NotYetImplemented()

@coppertop(style=binary)
def rUntil(x, y):
    return UntilFR(x, y)

@coppertop
def rZip(r):
    raise NotYetImplemented()




@coppertop
def popFront(r):
    r.popFront()
    return r

@coppertop
def popBack(r):
    r.popBack()
    return r

@coppertop
def rReplaceWith(haystack, needle, replacement):
    return haystack >> rMap >> (lambda e: replacement if e == needle else e)



# **********************************************************************************************************************
# buffer
# **********************************************************************************************************************

@coppertop
def buffer(iter) -> pytuple:
    return tuple(iter)

