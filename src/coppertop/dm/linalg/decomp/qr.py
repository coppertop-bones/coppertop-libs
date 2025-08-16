# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import scipy.linalg, numpy as np

from coppertop.pipe import *
from coppertop.dm.core.types import matrix, T, darray
from coppertop.dm.linalg.types import orth, right, QR
import coppertop.dm.linalg.orient


@coppertop
def qr(A:matrix) -> QR:
    Q, R = np.linalg.qr(A)            # via householder?
    q = matrix(Q) | +orth
    r = matrix(R) | +right
    return QR(q, r)


@coppertop(style=binary)
def solve(qr:QR, b:matrix[T]) -> matrix:
    """Returns the solution x of Ax = b given a QR decomposition of A"""
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_triangular.html
    return scipy.linalg.solve_triangular(qr.r, qr.T @ b, lower=False).view(darray) | matrix

