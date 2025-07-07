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

from coppertop.pipe import *
from coppertop.dm.core.types import bool, matrix, darray
from coppertop.dm.core.maths import EPS

@coppertop(style=binary)
def closeTo(a, b) -> bool:
    return closeTo(a, b, EPS)

@coppertop(style=binary)
def closeTo(a, b, tol) -> bool:
    if abs(a) < tol:
        return abs(b) < tol
    else:
        return abs(a - b) / abs(a) < tol

@coppertop(style=binary)
def different(a, b) -> bool:
    return True if not fitsWithin(typeOf(a), typeOf(b)) or a != b else False

@coppertop(style=binary)
def different(a:matrix&darray, b:matrix&darray) -> bool:
    return True if not fitsWithin(typeOf(a), typeOf(b)) or bool((a != b).any()) else False

@coppertop(style=binary, dispatchEvenIfAllTypes=True)
def doesNotFitWithin(a, b) -> bool:
    return True if not fitsWithin(a, b) else False

@coppertop(style=binary, dispatchEvenIfAllTypes=True)
def equals(a, b) -> bool:
    return True if fitsWithin(typeOf(a), typeOf(b)) and a == b else False

@coppertop(style=binary, dispatchEvenIfAllTypes=True)
def equals(a:matrix&darray, b:matrix&darray) -> bool:
    return True if fitsWithin(typeOf(a), typeOf(b)) and bool((a == b).all()) else False

@coppertop(style=binary)
def ge(a, b) -> bool:
    return a >= b

@coppertop(style=binary)
def gt(a, b) -> bool:
    return a > b

@coppertop
def isEmpty(x) -> bool:
    return len(x) == 0

@coppertop(style=binary)
def le(a, b) -> bool:
    return a <= b

@coppertop(style=binary)
def lt(a, b) -> bool:
    return a < b