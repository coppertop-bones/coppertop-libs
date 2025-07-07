# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import time, numpy as np

from coppertop.pipe import *
from bones.core.sentinels import Missing
from coppertop.dm.core.structs import darray
from coppertop.dm.core.types import N, Nn, Nm, num, matrix, count, bool, N1, missing, T1, T2
from coppertop.dm.linalg.types import colvec, Cholesky, QR, SVD
from coppertop.dm.linalg.core import solve


class StopSearch(RuntimeError): pass


array_ = (N**num)[darray]
matrix_ = matrix[darray]



@coppertop(style=nullary)
def search(
            fTarget     : Nn**N1**num,
            xInitial    : Nm**N1**num,
            fFn         : (Nm**N1**num) ^ (Nn**N1**num),
            JFn         : (Nm**N1**num) ^ (Nn**Nm**num),
            WDecomp     : Cholesky+QR+SVD,
            CQPDecompFn : matrix ^ (Cholesky+QR+SVD),
            tol         : Nn**N1**num,
            maxEvals            : count = 50,
            maxJacobians        : count = 10,
            maxBeforeRestart    : count = 12,
            evaluateAndCheckFn  : (T1^T2) + missing = Missing,
            J                   : (Nn**Nm**num) + Missing = Missing,
            requireJ            : bool = False
        ):
    """Answers a tuple (x, nfFnEvals, nJFnEvals) such that (fFn(x) - fTarget) <= tol, and sTWs is minimised,
    where s is the step, i.e. xk+1 = xk + s

    fFn(x) is the unscaled constraint function that returns a column vector of size N
    x is a column vector of size M starting at xInitial
    JFn(x) returns the Jacobian (N x M) of the unscaled fFn evaluated at argument x
    tol is the tolerance vector (size N)
    maxEvals is the maximum number of fFn evaluations we allow (calls for bumped Jacobian calculation do not count)
    maxJacobians is the maximum number of JFn evaluations we allow
    """

    _.fRemain = maxEvals
    _.fTime = 0.0
    _.jRemain = maxJacobians
    _.jTime = 0.0
    _.fRemainBeforeRestart = maxBeforeRestart

    scales = 1.0 / tol

    # use a closure here rather than a partial - can check later if partial is fast enough
    def scaledfFn(x):
        """Calculates a scaled f(x) and does some housekeeping"""
        t1 = time.clock()
        if _.fRemain == 0: raise StopSearch("Exhausted function evaluations")
        _.fRemain = _.fRemain - 1
        _.fRemainBeforeRestart = _.fRemainBeforeRestart - 1
        result = (fFn(x) - fTarget) * scales
        t2 = time.clock()
        _.fTime = _.fTime + (t2-t1)
        return result

    def scaledJFn(x):
        """Calculates a scaled J(x) and does some housekeeping"""
        t1 = time.clock()
        if _.jRemain == 0: raise StopSearch("Exhausted Jacobian evaluations")
        _.jRemain = _.jRemain - 1
        J = JFn(x)
        for iCol in range(J.shape[1]):
            J[:,iCol] = J[:,iCol] * scales
        t2 = time.clock()
        _.jTime = _.jTime + (t2-t1)
        return J

    if evaluateAndCheckFn is Missing: evaluateAndCheckFn = evalfAndCheck


    x = xInitial
    f = scaledfFn(x)

    # check to see if already in tolerance
    if np.max(f * f) <= 1.0:
        J = scaledJFn(x) if (requireJ and not J) else None
        return x + 0.0, maxEvals - _.fRemain, maxJacobians - _.jRemain, J, _.fTime, _.jTime

    J = scaledJFn(x) if J is Missing else J
    JIsExact = True

    try:
        while True:
            xGuess = x + QPStep(f, J, WDecomp, CQPDecompFn)
            xNew, fNew, inTol, tookStep, restart = evaluateAndCheckFn(xGuess, x, f, scaledfFn)
            if inTol:
                # if we are inTol then we must have taken a step so use xNew in this block
                J = scaledJFn(x) if requireJ and not J else None
                return xNew, maxEvals - _.fRemain, maxJacobians - _.jRemain, J, _.fTime, _.jTime
            assert restart or tookStep, "checkFn must return either restart==True or tookStep==True"
            if JIsExact and not tookStep: raise StopSearch("Unable to progress")
            if _.fRemainBeforeRestart <= 0 and _.jRemain > 0: restart = True
            if restart:
                J = scaledJFn(xNew)
                _.fRemainBeforeRestart = maxBeforeRestart
                JIsExact = True
            else:
                J = J + BroydenUpdate(x, f, xNew, fNew, J)
                JIsExact = False
            if tookStep:
                x = xNew
                f = fNew
    except StopSearch:
        return xNew, maxEvals - _.fRemain, maxJacobians - _.jRemain, None, _.fTime, _.jTime


def QPStep(f:colvec, J:matrix, WDecomp:Cholesky+QR+SVD, CQPDecompFn:matrix^(Cholesky+QR+SVD)) -> colvec:
    """Returns the QP step - see p104, 'Derivatives Algorithms - Volume 1: Bones' by Tom Hyer"""
    WInvJT = WDecomp >> solve >> J.T
    JWInvJT = J @ WInvJT
    JWInvJTInvf = CQPDecompFn(JWInvJT) >> solve >> f
    return -(WInvJT @ JWInvJTInvf) | colvec


def BroydenUpdate(xOld, fOld, xNew, fNew, J):
    """Answer the Broyden updated Jacobian - see chap 8, p170, 'Numerical Methods for Unconstrained Optimisation and Nonlinear Equations' by Dennis & Schnabel"""
    sc = xOld - xNew
    sc.shape = (len(sc), 1)
    scTsc = (sc @ sc.T)[0, 0]
    if scTsc < 0.000000000001: return J          # no move - should we flag an error?
    yc = fOld - fNew
    yc.shape = (len(yc), 1)
    return ((yc - (J @ sc)) @ sc.T) / scTsc


def bumpedJacobian(x, fFn, bumpSizes):
    """Utility to return the Jacobian formed by a one-sided bump of the parameter space"""
    fx = fFn(x)
    J = np.zeros((len(fx), len(x)), np.float64)
    for i in range(len(x)):
        x[i] += bumpSizes[i]
        fBumped = fFn(x)
        J[:, i] = (fBumped - fx) / bumpSizes[i]
        x[i] -= bumpSizes[i]
    return J


def addSelfWeight(W, weight, i):
    W[i, i] += weight


def addPairWeight(W, weight, i, j):
    #(xi - xj)^2
    W[i, i] += weight
    W[i, j] -= weight
    W[j, i] -= weight
    W[j, j] += weight


def evalfAndCheck(xGuess, xOld, fOld, fFn):
    """Answers xNew, fNew, inTol, tookStep, restart"""

    fN = fFn(xGuess)
    fN2 = fN ** 2
    # is np.min(fN2) > 1.0 correct? shouldn't it be np.max(fN2) < 1.0
    if np.min(fN2) > 1.0: return _evalResult(xGuess, fN, inTol=True)                  # within tolerance so escape

    fC = fN - fOld
    fCTfC = np.sum(fC ** 2)
    if fCTfC < 0.00001: return _evalResult(xOld, fOld, tookStep=False, restart=True)  # no change so restart

    return _evalResult(xGuess, fN, tookStep=True, restart=False)


def _evalResult(xNew, fNew, inTol=False, tookStep=False, restart=False):
    return (xNew, fNew, inTol, tookStep, restart)

