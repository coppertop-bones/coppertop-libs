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
from coppertop.dm.core.types import litint, litnum, num, count as tCount, err, T, T1, T2, index, txt, btype, pytype
from bones.core.errors import NotYetImplemented
from bones.ts.metatypes import BType, BTUnion



# **********************************************************************************************************************
# addition
# **********************************************************************************************************************

@coppertop(style=binary, name='+')
def _add(a:index, b:index) -> index:
    return a + b

@coppertop(style=binary, name='+')
def _add(a:num, b:num) -> num:
    return a + b

@coppertop(style=binary, name='+')
def _add(a:litint, b:litint) -> litint:
    return a + b

@coppertop(style=binary, name='+')
def _add(a:litnum, b:litnum) -> litnum:
    return a + b

@coppertop(style=binary, name='+')
def _add(a:tCount, b:tCount) -> tCount:
    return a + b

# @coppertop(style=binary, name='+')
# def add_(a:err&T1, b:T2) -> err&T1:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='+')
# def add_(a:T1, b:err&T2) -> err&T2:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='+')
# def add_(a:err&T1, b:err&T1) -> err&T1:
#     raise NotYetImplemented()


# **********************************************************************************************************************
# subtraction
# **********************************************************************************************************************

@coppertop(style=binary, name='-')
def sub(a:index, b:index) -> index:
    return a - b

@coppertop(style=binary, name='-')
def _sub(a:num, b:num) -> num:
    return a - b

@coppertop(style=binary, name='-')
def _sub(a:litint, b:litint) -> litint:
    return a - b

@coppertop(style=binary, name='-')
def _sub(a:litnum, b:litnum) -> litnum:
    return a - b

@coppertop(style=binary, name='-')
def _sub(a:tCount, b:tCount) -> tCount:
    return a - b

@coppertop(style=binary, name='-')
def _sub(a:err&T1, b:T2) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='-')
def _sub(a:T1, b:err&T2) -> err&T2:
    raise NotYetImplemented()

@coppertop(style=binary, name='-')
def _sub(a:err&T1, b:err&T1) -> err&T1:
    raise NotYetImplemented()


# **********************************************************************************************************************
# multiplication
# **********************************************************************************************************************

@coppertop(style=binary, name='*')
def _mul(a:num, b:num) -> num:
    return a * b

@coppertop(style=binary, name='*')
def _mul(a:litint, b:litint) -> litint:
    return a * b

@coppertop(style=binary, name='*')
def _mul(a:litnum, b:litnum) -> litnum:
    return a * b

@coppertop(style=binary, name='*')
def _mul(a:err&T1, b:T2) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='*')
def _mul(a:T1, b:err&T2) -> err&T2:
    raise NotYetImplemented()

@coppertop(style=binary, name='*')
def _mul(a:err&T1, b:err&T1) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='*')
def _mul(a:index, b:index) -> index:
    return a * b


# **********************************************************************************************************************
# division
# **********************************************************************************************************************

@coppertop(style=binary, name='/')
def _div(a:num, b:num) -> num:
    return a / b

# @coppertop(style=binary, name='/')
# def _div(a:err&T1, b:T2) -> err&T1:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='/')
# def _div(a:T1, b:err&T2) -> err&T2:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='/')
# def _div(a:err&T1, b:err&T1) -> err&T1:
#     raise NotYetImplemented()


# **********************************************************************************************************************
# equals
# **********************************************************************************************************************

@coppertop(style=binary, name='==')
def _eq(a:num, b:num) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:index, b:index) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:txt, b:txt) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:bool, b:bool) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:litint, b:litint) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:litnum, b:litnum) -> bool:
    return a == b

@coppertop(style=binary, name='==')
def _eq(a:btype+pytype, b:btype+pytype) -> bool:
    return a == b


# **********************************************************************************************************************
# less than
# **********************************************************************************************************************

@coppertop(style=binary, name='<')
def lt(a:num, b:num) -> bool:
    return a < b


# **********************************************************************************************************************
# less than or equal
# **********************************************************************************************************************

@coppertop(style=binary, name='<=')
def le(a:btype, b:btype) -> bool:
    return fitsWithin(a, b)

