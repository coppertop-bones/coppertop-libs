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
from coppertop.core import NotYetImplemented
from coppertop.dm.core.types import pylist
from coppertop.dm.examples.ranges import nodes
from coppertop.dm.core.types import pytuple


@coppertop
def rChain(rs):
    return nodes.Chain(rs)

@coppertop(style=binary)
def rChunkUsing(r, f):
    return nodes.EmitWhilesUsing(r, f)

@coppertop(style=binary)
def rChunkUsingSubRangeGeneratorFR(r, f):
    return nodes.ChunkUsingSubRangeGenerator(r, f)

@coppertop
def rDrop(r, n):
    raise NotYetImplemented()

@coppertop
def rDropBack(r, n):
    raise NotYetImplemented()

@coppertop(style=binary)
def rExhaustInto(inR, outR):
    while not inR.empty:
        e = inR.front
        if isinstance(e, nodes.IIdxInf):
            raise TypeError('Infinite range encountered')
        elif isinstance(e, nodes.Simple):
            rExhaustInto(e, outR)
            if not inR.empty:  # the sub range may exhaust this range
                inR.popFront()
        else:
            outR.put(e)
            inR.popFront()
    return outR

@coppertop(style=binary)
def rExhaustInto(inR, outR, depth):
    assert depth == 1  # OPEN: implement depth > 1
    while not inR.empty:
        e = inR.front
        outR.put(e)
        inR.popFront()
    return outR

@coppertop(style=binary)
def rFilter(r, fn):
    return nodes.FilterUsing(r, fn)

@coppertop
def rFnAdapterEager(f):
    answer = []
    i = 0
    while (x := f(i)) != nodes.EMPTY:
        answer.append(x)
        i += 1
    return answer

@coppertop
def rFront(r):
    return r.front

@coppertop
def rInject(r, seed, f):
    raise NotYetImplemented()

@coppertop(style=binary)
def rMap(x, y):
    return nodes.Map(x, y)

@coppertop
def rMaterialise(r):
    return _materialise(r)

def _materialise(r):
    answer = list()
    while not r.empty:
        e = r.front
        if isinstance(e, nodes.Simple) and not isinstance(e, nodes.IIdxInf):
            answer.append(_materialise(e))
            if not r.empty:  # the sub range may exhaust this range
                r.popFront()
        else:
            answer.append(e)
            r.popFront()
    return answer

@coppertop(style=binary)
def rPut(r, x):
    return r.put(x)

@coppertop
def rReplaceWith(haystack, needle, replacement):
    return haystack >> rMap >> (lambda e: replacement if e == needle else e)

@coppertop
def rSeek(r, value):
    while not r.empty:
        if r.front == value:
            break
        r.popFront()
    return r

@coppertop(style=binary)
def rTake(r, n):
    return nodes.Take(r, n)

@coppertop(style=binary)
def rTakeBack(r, n):
    raise NotYetImplemented()

@coppertop
def rTarget(sink:nodes.ListSink):
    return sink.list

@coppertop
def rTarget(sink:nodes.LastSink):
    return sink.last

@coppertop(style=ternary)
def rUntil(r, fn, v):
    return nodes.Until(r, fn, v)

@coppertop(style=ternary)
def rWhile(r, fn, v):
    return nodes.While(r, fn, v)

@coppertop
def rZipRagged(ror):
    return nodes.ZipRagged(ror)

