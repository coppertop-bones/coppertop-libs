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


import builtins, numpy as np, types

from coppertop.pipe import *
from coppertop.utils import NotYetImplemented, Missing
from coppertop.utils.types import dict_keys, dict_values, dict_items
from bones.ts.metatypes import BTAtom as _BTAtom
from coppertop.dm.core.aggman import inject
from bones.lang.types import _tv
from coppertop.dm.core.types import T, pylist, txt, pydict, pyfunc, T1, T2, py


_SBT = _BTAtom('ShouldBeTyped')      # temporary type to allow"  'DE000762534' >> box | tISIN - i.e. make the box then type it


@coppertop
def _t(x):
    return x._t

@coppertop
def _v(x):
    return x._v

@coppertop(style=binary)
def asideDo(x:T1, fn:T1^T2) -> T1:
    fn(x)
    return x

@coppertop(style=binary)
def asideDo(x:py, fn:pyfunc) -> py:
    fn(x)
    return x

@coppertop
def box(v) -> _SBT:
    return _tv(_SBT, v)

@coppertop
def box(v, t:T) -> T:
    return _tv(t, v)

@coppertop
def compose(x, fs):
    return fs >> inject(_, x, _) >> (lambda x, f: f(x))


# **********************************************************************************************************************
# gather
# **********************************************************************************************************************

@coppertop
def gather(x:types.FunctionType) -> pyfunc:
    return x()

@coppertop
def gather(x:dict_keys) -> pylist:
    return list(x)

@coppertop
def gather(x:dict_values) -> pylist:
    return list(x)

@coppertop
def gather(x:dict_items) -> pylist:
    return list(x)


@coppertop(style=binary)
def getAttr(x, name):
    return getattr(x, name)

@coppertop
def not_(b):
    return False if b else True

@coppertop
def Not(b):
    return False if b else True

@coppertop
def pyeval_(src:txt):
    return lambda : eval(src)

@coppertop
def pyeval_(src:txt, ctx:pydict):
    return lambda : eval(src, ctx)

repr = coppertop(dispatchEvenIfAllTypes=True)(builtins.repr)


# **********************************************************************************************************************
# sequence
# **********************************************************************************************************************

@coppertop(style=nullary)
def sequence(p1, p2):
    first , last = p1, p2
    return list(range(first, last+1, 1))

@coppertop(style=nullary)
def sequence(p1, p2, n, sigmas):
    mu, sigma = p1, p2
    low = mu - sigmas * sigma
    high = mu + sigmas * sigma
    return sequence(low, high, n=n)

@coppertop(style=nullary)
def sequence(p1, p2, n):
    first , last = p1, p2
    return list(np.linspace(first, last, n))

@coppertop(style=nullary)
def sequenceStep(p1, p2, step):
    first , last = p1, p2
    return list(np.arange(first, last + step, step))

@coppertop(style=nullary)
def sequence(first, last, kwargs:pydict):
    if not kwargs:
        return list(range(first, last+1, 1))
    if (step := kwargs.get('step', Missing)):
        return list(np.arange(first, last + step, step))
    else:
        raise NotYetImplemented(f'sequence({first}, {last}, {kwargs})')

@coppertop
def unpack(f:pyfunc) -> pyfunc:
    return lambda args: f(*args)

@coppertop(style=ternary)
def withCtx(arg1, ctx:pydict, fn):
    with context(ctx):
        return arg1 >> fn

