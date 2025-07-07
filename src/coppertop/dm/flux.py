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
from bones.core.errors import NotYetImplemented
from coppertop.dm.core.types import pylist, T1, N, dseq



# **********************************************************************************************************************
# add
# **********************************************************************************************************************

@coppertop(style=binary)
def add(xs:pylist, x) -> pylist:
    return xs + [x]         # this is immutable

@coppertop(style=binary)
def add(xs:(N**T1)[dseq], x:T1) -> (N**T1)[dseq]:
    xs = dseq(xs)
    xs.append(x)
    return xs


# **********************************************************************************************************************
# append
# **********************************************************************************************************************

@coppertop(style=binary)
def append(xs:pylist, x) -> pylist:
    return xs + [x]         # this is immutable


# **********************************************************************************************************************
# appendTo
# **********************************************************************************************************************

@coppertop(style=binary)
def appendTo(x, xs:pylist) -> pylist:
    return xs + [x]         # this is immutable


# **********************************************************************************************************************
# drop
# **********************************************************************************************************************

# @coppertop(style=binary)
# def drop(xs:(N**T1)[pylist], ks:(N**T2)[pylist]) -> (N**T1)[pylist]:
#     answer = []
#     for x in xs:
#         if x not in ks:
#             answer.append(x)
#     return answer


# **********************************************************************************************************************
# prepend
# **********************************************************************************************************************

@coppertop(style=binary)
def prepend(xs:pylist, x) -> pylist:
    return [x] + xs         # this is immutable


# **********************************************************************************************************************
# prependTo
# **********************************************************************************************************************

@coppertop(style=binary)
def prependTo(x, xs:pylist) -> pylist:
    return [x] + xs         # this is immutable


# **********************************************************************************************************************
# postAdd
# **********************************************************************************************************************

@coppertop(style=ternary)
def postAdd(c, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# postAddCol
# **********************************************************************************************************************

@coppertop(style=ternary)
def postAddCol(c, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# postAddRow
# **********************************************************************************************************************

@coppertop(style=ternary)
def postAddRow(c, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# preAdd
# **********************************************************************************************************************

@coppertop(style=ternary)
def preAdd(c, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# preAddCol
# **********************************************************************************************************************

@coppertop(style=ternary)
def preAddCol(c, i, v):
    raise NotYetImplemented()


# **********************************************************************************************************************
# preAddRow
# **********************************************************************************************************************

@coppertop(style=ternary)
def preAddRow(c, i, v):
    raise NotYetImplemented()


