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

import builtins, numpy as np

from coppertop.pipe import *
from coppertop.dm.core.types import T1, T2, pylist, N, num, matrix, darray
from coppertop.dm.core.conv import to



array_ = (N**num)&darray
matrix_ = matrix&darray



# **********************************************************************************************************************
# stats
# **********************************************************************************************************************

@coppertop
def cov(A:matrix_) -> matrix_:
    return (matrix&darray)(np.cov(A))

@coppertop
def max(x:matrix_) -> num:
    return np.max(x) >> to >> num

@coppertop
def max(x) -> num:
    return builtins.max(x) >> to >> num

@coppertop
def mean(ndOrPy) -> num:
    return np.mean(ndOrPy) >> to >> num

@coppertop
def min(x:matrix_) -> num:
    return np.min(x) >> to >> num

@coppertop
def min(x) -> num:
    return builtins.min(x) >> to >> num


# **********************************************************************************************************************
# sum - is okay as same interface as Python
# **********************************************************************************************************************

@coppertop
def std(ndOrPy) -> num:
    return np.std(ndOrPy, 0) >> to >> num

@coppertop
def std(ndOrPy, dof) -> num:
    return np.std(ndOrPy, dof) >> to >> num


# **********************************************************************************************************************
# sum - is okay as same interface as Python
# **********************************************************************************************************************

@coppertop
def sum(x) -> num:
    return builtins.sum(x) >> to >> num

@coppertop
def sum(x:(N**T1)[pylist][T2]) -> num:
    return builtins.sum(x._v) >> to >> num

@coppertop
def sum(x:(N**T1)[pylist]) -> num:
    return builtins.sum(x._v) >> to >> num


