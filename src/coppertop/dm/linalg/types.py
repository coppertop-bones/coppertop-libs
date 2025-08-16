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
from bones.ts.metatypes import BTAtom, BType
from coppertop.dm.core.types import matrix, N, num, pytuple, dstruct, darray


# NB a 1x1 matrix is assumed to be a scalar, e.g. https://®®en.wikipedia.org/wiki/Dot_product#Algebraic_definition


I = BTAtom('I')
square = BTAtom('square')
right = BTAtom('right')
left = BTAtom('left')
upper = BTAtom('upper')
lower = BTAtom('lower')
orth = BTAtom('orth')
diag = BTAtom('diag')
tri = BTAtom('tri')
cov = BTAtom('cov')
colvec = BTAtom('colvec')
rowvec = BTAtom('rowvec')

Cholesky = BTAtom('Cholesky')


matrix = matrix
array_ = (N**num) & darray


QR = BType('QR: QR & {qT:matrix, r:matrix&right} in mem')
@coppertop(style=nullary)
def _makeQR(ts, q:matrix, r:matrix):
    return dstruct(QR&dstruct, q=q, r=r)
@coppertop(style=nullary)
def _makeQR(ts, qr:pytuple):
    return dstruct(QR&dstruct, q=matrix(qr[0]), r=matrix(qr[1]))
QR.setConstructor(_makeQR)


# SVD = BType('SVD: SVD & {u:matrix, s:N**num, vt:matrix} & dstruct in mem')
SVD = BType('SVD: SVD & {u:matrix, s:N**num, vt:matrix} in mem')
@coppertop(style=nullary)
def _makeSVD(ts, u:matrix, s:array_, vT:matrix) -> SVD:
    return dstruct(SVD, u=u, s=s, vT=vT)
SVD.setConstructor(_makeSVD)
