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

import builtins, numpy as np, math

from bones.core.errors import NotYetImplemented
from coppertop.pipe import *
from coppertop.dm.core.types import T1, pylist, N, num, matrix, t, pyset, pytuple, T, darray
from coppertop.dm.core.aggman import count

import itertools, scipy



EPS = 7.105427357601E-15      # i.e. double precision

array_ = (N**num)&darray
matrix_ = matrix&darray



# **********************************************************************************************************************
# permutations (arrangements) and combinations
# perms and combs are such useful variable names so use fuller name in fn
# **********************************************************************************************************************

@coppertop(style=binary)
def permutations(xs, k):
    return tuple(itertools.permutations(xs, k))

@coppertop(style=binary)
def nPermutations(n, k):
    return math.perm(n, k)

@coppertop(style=binary)
def permutationsR(xs, k):
    return tuple(itertools.product(*([xs]*k)))

@coppertop(style=binary)
def nPermutationsR(n, k):
    return n ** k

@coppertop(style=binary)
def combinations(xs, k):
    return tuple(itertools.combinations(xs, k))

@coppertop(style=binary)
def nCombinations(n, k):
    return math.comb(n, k)

@coppertop(style=binary)
def combinationsR(xs, k):
    return tuple(itertools.combinations_with_replacement(xs, k))

@coppertop(style=binary)
def nCombinationsR(n, k):
    return scipy.special.comb(n, k, exact=True)

@coppertop
def nPartitions(sizes:pylist) -> t.count:
    num = 1
    n = sum(sizes)
    for k in sizes:
        num *= n >> nCombinations >> k
        n -= k
    return num | t.count

@coppertop(style=binary)
def allPartitionsInto(xs:pylist, sizes:pylist+pytuple) -> pylist: #N**N**T:
    if sum(sizes) != xs >> count: raise ValueError(f'sum(sizes) != count(xs), {sum(sizes)} != {xs >> count}')
    return _partitions(xs, sizes)

@coppertop(style=binary)
def allPartitionsInto(xs, sizes:pylist+pytuple) -> pylist: #N**N**T:
    if sum(sizes) != xs >> count: raise ValueError(f'sum(sizes) != count(xs), {sum(sizes)} != {xs >> count}')
    return _partitions(list(xs), sizes)

def _partitions(xs:N**T, sizes:N**t.count) -> pylist: #N**N**T:
    if sizes:
        answer = []
        for comb, rest in _combRest(xs, sizes[0]):
            for e in _partitions(rest, sizes[1:]):
                answer.append(comb + e)
        return answer
    else:
        return [[]]

def _combRest(xs:N**T1, m:t.count) -> pylist: #N**( (N**T1)*(N**T1) ):
    '''answer [m items chosen from n items, the rest]'''
    if m == 0:
        return [([], xs)]
    elif m == len(xs):
        return [(xs, [])]
    else:
        firstOne, remainder = xs[0:1], xs[1:]
        firstPart = [ (firstOne + x, y) for x, y in _combRest(remainder, m - 1)]
        secondPart = [ (x, firstOne + y) for x, y in _combRest(remainder, m)]
        return firstPart + secondPart

# %%timeit
# x = list(range(13)) >> allPartitionsInto >> [5,4,4]
# 115 ms ± 3.49 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)


# **********************************************************************************************************************
# comparison
# **********************************************************************************************************************

@coppertop
def within(x, a, b):
    # answers true if x is in the closed interval [a, b]
    return (a <= x) and (x <= b)


# **********************************************************************************************************************
# functions
# **********************************************************************************************************************

@coppertop
def log(v:array_) -> array_:
    return np.log(v)

@coppertop
def sqrt(x):
    return np.sqrt(x)   # answers a nan rather than throwing

@coppertop
def product(x:pylist+pyset+pytuple) -> num + t.count:
    return math.product(x)


# **********************************************************************************************************************
# rounding
# **********************************************************************************************************************

@coppertop
def roundDown(x):
    # i.e. [roundDown(-2.9), roundDown(2.9,0)] == [-3, 2]
    return math.floor(x)

@coppertop
def roundUp(x):
    # i.e. [roundUp(-2.9), roundUp(2.9,0)] == [-2, 3]
    return math.ceil(x)

@coppertop
def roundHalfToZero(x):
    # i.e. [round(-2.5,0), round(2.5,0)] == [-2.0, 2.0]
    return round(x)

@coppertop
def roundHalfFromZero(x):
    raise NotYetImplemented()

@coppertop
def roundHalfToNeg(x):
    raise NotYetImplemented()

@coppertop
def roundHalfToPos(x):
    raise NotYetImplemented()

@coppertop
def round(xs:matrix&darray, figs:t.count) -> matrix&darray:
    return (matrix&darray)(np.round(xs, figs))

@coppertop
def round(xs:array_, figs:t.count) -> array_:
    return (array_)(np.round(xs, figs))
