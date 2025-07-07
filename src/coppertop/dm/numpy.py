# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# don't really want to encourage raw ndarrays as they don't have the typing we'd like, but here's some helpers for
# when I'm being lazy

import sys

if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import numpy as np
from coppertop.pipe import *
from coppertop.dm.core.types import t, pytuple



# **********************************************************************************************************************
# count
# **********************************************************************************************************************

@coppertop
def count(x:np.ndarray) -> t.count:
    assert x.ndim == 1
    return x.shape[0] | t.count


# **********************************************************************************************************************
# diff
# **********************************************************************************************************************

@coppertop
def diff(a:np.ndarray, axis):
    return np.diff(a, axis=axis)

@coppertop
def diff(a:np.ndarray):
    return np.diff(a)


# **********************************************************************************************************************
# shape
# **********************************************************************************************************************

@coppertop
def shape(a:np.ndarray) -> pytuple:
    return a.shape


# **********************************************************************************************************************
# sum
# **********************************************************************************************************************

@coppertop
def sum(x: np.ndarray):
    return np.sum(x)


# **********************************************************************************************************************
# take
# **********************************************************************************************************************

@coppertop(style=binary)
def take(x: np.ndarray, n: t.count) -> np.ndarray:
    if n > 0:
        return x[:n]
    else:
        return x[n:]


# **********************************************************************************************************************
# takeRows
# **********************************************************************************************************************

@coppertop(style=binary)
def takeRows(x: np.ndarray, n: t.count) -> np.ndarray:
    if n > 0:
        return x[:n, :]
    else:
        return x[n:, :]
