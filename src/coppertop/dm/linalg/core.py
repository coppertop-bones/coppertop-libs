# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import scipy.linalg, numpy as np, numpy.linalg

from coppertop.pipe import *
from coppertop.dm.core.types import matrix, N, num, T, darray
from coppertop.dm.linalg.types import orth, right, upper, lower, Cholesky, QR, SVD, left
import coppertop.dm.linalg.orient


array_ = (N**num)[darray]
matrix_ = matrix[darray]


# NB a 1x1 matrix is assumed to be a scalar, e.g. https://®®en.wikipedia.org/wiki/Dot_product#Algebraic_definition


@coppertop
def inv(A:matrix_) -> matrix_:
    return np.linalg.inv(A)

@coppertop
def qr(A:matrix_) -> QR:
    Q, R = np.linalg.qr(A)            # via householder?
    q = matrix_(Q) | +orth
    r = matrix_(R) | +right
    return QR(q, r)

@coppertop
def cholesky(A:matrix_) -> matrix_&Cholesky:
    # use np since in scipy.linalg.cho_factor "The returned matrix also contains random data in the entries not
    # used by the Cholesky decomposition. If you need to zero these entries, use the function cholesky instead."
    return matrix_(np.linalg.cholesky(A)) | +Cholesky

@coppertop
def svd(A:matrix_) -> SVD:
    u, s, vT = np.linalg.svd(A)
    return SVD(matrix_(u), array_(s), matrix_(vT))



# https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_triangular.html

@coppertop(style=binary)
def solve(U:(upper&matrix_)+(right&matrix_), b:matrix_[T]) -> matrix_:
    """Returns the solution x of Ux = b where U is upper triangular"""
    return scipy.linalg.solve_triangular(U, b, lower=False).view(darray) | matrix_


@coppertop(style=binary)
def solve(L:(lower&matrix_)+(left&matrix_), b:matrix_[T]) -> matrix_:
    """Returns the solution x of Lx = b where U is lower triangular"""
    return scipy.linalg.solve_triangular(L, b, lower=True).view(darray) | matrix_


@coppertop(style=binary)
def solve(c:Cholesky&matrix, b:matrix_[T]) -> matrix_:
    """Returns the solution x of Ax = b given the Cholesky decomposition of A"""
    return matrix_(scipy.linalg.cho_solve(c, b))


@coppertop(style=binary)
def solve(qr:QR, b:matrix_[T]) -> matrix_:
    """Returns the solution x of Ax = b given a QR decomposition of A"""
    return scipy.linalg.solve_triangular(qr.r, qr.T @ b, lower=False).view(darray) | matrix_


@coppertop(style=binary)
def solve(svd:SVD, b:matrix_[T]) -> matrix_:
    """Returns the solution x of Ax = b given the SVD of A"""
    raise NotYetImplemented()


@coppertop
def pca(panel:matrix&darray):
    res = svd(panel)
    vor, e, sfv, thetas, sorts = coppertop.dm.linalg.orient.orientEigenvectors(res.vT.T, res.s)
    return vor, res.s

