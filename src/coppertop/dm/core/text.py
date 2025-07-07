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
from bones.core.sentinels import Missing
from coppertop.dm.core.types import pylist, pytuple, pydict, txt, index, bool



@coppertop(style=binary)
def endsWith(s1:txt, s2:txt) -> bool:
    return s1.endswith(s2)

# see https://realpython.com/python-formatted-output/ and https://www.python.org/dev/peps/pep-3101/
@coppertop
def format(arg, f:txt) -> txt:
    return f.format(arg)

@coppertop
def format(arg, f:txt, kwargs:pydict) -> txt:
    return f.format(arg, **kwargs)

@coppertop
def format(args:pylist+pytuple, f:txt, kwargs:pydict) -> txt:
    return f.format(*args, **kwargs)

@coppertop
def format(kwargs:pydict, f:txt) -> txt:
    return f.format(**kwargs)

@coppertop
def pad(s:txt, options:pydict):
    left = options.get('left', Missing)
    right = options.get('right', Missing)
    center = options.get('center', Missing)
    pad = options.get('pad', ' ')
    if right is not Missing:
        return s.rjust(right, pad)
    if center is not Missing:
        return s.center(center, pad)
    return s.ljust(left, pad)

@coppertop(style=ternary)
def replace(haystack:txt, needle:txt, alt:txt) -> txt:
    return haystack.replace(needle, alt)

@coppertop(style=binary)
def splitOn(s, sep):
    return s.split(sep)

@coppertop(style=binary)
def splitOn(s, sep, maxsplit):
    return s.split(sep, maxsplit)

@coppertop(style=binary)
def startsWith(s1:txt, s2:txt) -> bool:
    return s1.startswith(s2)

@coppertop
def strip(s):
    return s.strip()

@coppertop
def strip(s, chars):
    return s.strip(chars)

