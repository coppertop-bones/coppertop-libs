# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import builtins

from coppertop.pipe import *
from bones.lang.types import _tv
from coppertop.dm.core.types import num, index, txt, bool, litint, litnum, littxt, T1, T2, N, t


true = _tv(bool, True)
false = _tv(bool, False)

@coppertop(name='id')
def _id(x:T1) -> T1:
    return x

@coppertop(style=ternary, name='ifTrue:ifFalse:')
def _ifTrueIfFalse(cond:bool, x:T1, y:T2) -> T1 + T2:
    if cond:
        return x
    else:
        return y

@coppertop(name='collect:')
def _collect(xs, f):
    return [f(x) for x in xs]

@coppertop(style=binary)
def join(a:txt, b:txt) -> txt:
    return a + b

@coppertop
def count(a:txt) -> t.count:
    return len(a) | t.count

@coppertop
def toTxt(a:litint) -> txt:
    return str(a) | txt

@coppertop
def toTxt(a:littxt) -> txt:
    return a | txt

@coppertop
def toIndex(a:litint) -> index:
    return a | index

@coppertop
def PP(x):
    print(x)
    return x

@coppertop
def PP(x:txt) -> txt:
    print(x)
    return x

@coppertop
def PP(x:num) -> num:
    print(x)
    return x

@coppertop
def PP(x:index) -> index:
    print(x)
    return x

@coppertop(style=binary)
def arrayJoin(a:N**T1, b:N**T1) -> N**T1:
    return a + b