# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import numpy as np

from coppertop.pipe import *
from coppertop.dm.core.types import matrix, N, num, darray, index
from coppertop.dm.core import to
import coppertop.dm.linalg.orient
from coppertop.dm.core.text_report import display_table, PP as PP2


array_ = (N**num)[darray]


# NB a 1x1 matrix is assumed to be a scalar, e.g. https://®®en.wikipedia.org/wiki/Dot_product#Algebraic_definition

@coppertop
def col(A:matrix, i:index) -> matrix:
    return A[:,i-1:i]

@coppertop
def cols(A:matrix, i1:index, i2:index) -> matrix:
    return A[:,i1-1:i2]

@coppertop
def inv(A:matrix) -> matrix:
    return matrix(np.linalg.inv(A))

@coppertop(style=binary)
def madd(A:matrix, B:matrix) -> matrix:
    return A + B

@coppertop(style=binary)
def mmul(A:matrix, B:matrix) -> matrix:
    return A @ B

@coppertop
def PP(x:matrix) -> matrix:
    TR(x) >> PP2
    return x

@coppertop
def row(A:matrix, i:index) -> matrix:
    return A[i-1:i, :]

@coppertop
def rows(A:matrix, i1:index, i2:index) -> matrix:
    return A[i1-1:i2, :]

@coppertop(style=binary)
def to(x:matrix, t:display_table) -> display_table:
    strs = str(x).split('\n')
    l = max(map(len, strs))
    return display_table([s.ljust(l) for s in strs])

@coppertop
def TR(x:matrix) -> display_table:
    return x >> to >> display_table
