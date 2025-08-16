# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import scipy.linalg

from coppertop.pipe import *
from coppertop.dm.core.types import matrix, T, darray
from coppertop.dm.linalg.types import right, upper, lower, left
import coppertop.dm.linalg.orient


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_triangular.html

@coppertop(style=binary)
def solve(U:(upper&matrix)+(right&matrix), b:matrix[T]) -> matrix:
    """Returns the solution x of Ux = b where U is upper triangular"""
    return scipy.linalg.solve_triangular(U, b, lower=False).view(darray) | matrix


@coppertop(style=binary)
def solve(L:(lower&matrix)+(left&matrix), b:matrix[T]) -> matrix:
    """Returns the solution x of Lx = b where L is lower triangular"""
    return scipy.linalg.solve_triangular(L, b, lower=True).view(darray) | matrix
