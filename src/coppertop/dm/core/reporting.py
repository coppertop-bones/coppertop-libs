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

from coppertop.utils import NotYetImplemented
from coppertop.pipe import *
from bones.ts.metatypes import BType, extractConstructors

from coppertop.dm.core.types import dseq, matrix, txt, pyint, num



# display_table is a seq of txt (each one must be the same length)
def _consDisplayTable(*args_, **kwargs_):
    constrs, args, kwargs = extractConstructors(args_, kwargs_)
    if len(constrs) == 0:
        raise NotYetImplemented()
    else:
        t = constrs[0]
        if len(args) == 0:
            return dseq(constrs, *args, **kwargs)
        elif len(args) == 1:
            if len(args[0]) == 0:
                raise ValueError('Can\'t create empty display table - no rows provided')
            rows = args[0]
            l = len(rows[0])
            for i, r in enumerate(rows):
                if len(r) != l:
                    raise ValueError(f'Row @ offset {i} does not have same length as first row')
            return dseq(constrs, *args, **kwargs)
        else:
            raise NotYetImplemented()

display_table = BType('display_table: display_table & (N ** txt) & dseq in mem').setConstructor(_consDisplayTable)


@coppertop(style=binary)
def join(A:display_table, B:display_table) -> display_table:
    if (nA := len(A)) == (nB := len(B)):
        return display_table([a + b for a, b in zip(A, B)])
    else:
        # center vertically
        if nA > nB:
            numRows = int((nA - nB) / 2)
            i, iA, iB = 0, 0, 0
            padding = ' ' * len(B[0])
            answer = display_table([''] * nA)
            for j in range(numRows):
                answer[i] = A[iA] + padding
                i += 1
                iA += 1
            for j in range(nB):
                answer[i] = A[iA] + B[iB]
                i += 1
                iA += 1
                iB += 1
            for j in range(nA - numRows - nB):
                answer[i] = A[iA] + padding
                i += 1
                iA += 1
            return answer
        else:
            numRows = int((nB - nA) / 2)
            i, iA, iB = 0, 0, 0
            padding = ' ' * len(A[0])
            answer = display_table([''] * nB)
            for j in range(numRows):
                answer[i] = padding + B[iB]
                i += 1
                iB += 1
            for j in range(nA):
                answer[i] = A[iA] + B[iB]
                i += 1
                iA += 1
                iB += 1
            for j in range(nB - numRows - nA):
                answer[i] = padding + B[iB]
                i += 1
                iB += 1
            return answer


@coppertop(style=binary)
def to(x:matrix, t:display_table) -> display_table:
    strs = str(x).split('\n')
    l = max(map(len, strs))
    return display_table([s.ljust(l) for s in strs])


@coppertop
def PP(x:display_table) -> display_table:
    for r in x:
        print(r)
    return display_table(x)

@coppertop
def TR(x:txt) -> display_table:
    return display_table([x])

@coppertop
def TR(x:pyint + num) -> display_table:
    return display_table([str(x)])

@coppertop
def TR(x:matrix) -> display_table:
    return x >> to >> display_table

