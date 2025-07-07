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

import csv

from coppertop.pipe import *
from bones.core.sentinels import Missing
from coppertop.dm.core.types import dframe, txt, pydict, dtup


# **********************************************************************************************************************
# read
# **********************************************************************************************************************

@coppertop
def read(pfn:txt, renames:pydict, conversions:pydict) -> dframe:
    with open(pfn, mode='r') as f:
        r = csv.DictReader(f)
        d = {}
        for name in r.fieldnames:
            d[name] = list()
        for cells in r:
            for k, v in cells.items():
                d[k].append(v)
        a = dframe()
        for k in d.keys():
            newk = renames.get(k, k)
            fn = conversions.get(newk, lambda l: dtup(l, Missing))     ## we could insist the conversions return dtup s
            a[newk] = fn(d[k])
    return a

@coppertop
def read(pfn:txt, renames:pydict, conversions:pydict, cachePath) -> dframe:
    with open(pfn, mode='r') as f:
        r = csv.DictReader(f)
        d = {}
        for name in r.fieldnames:
            d[name] = list()
        for cells in r:
            for k, v in cells.items():
                d[k].append(v)
        a = dframe()
        for k in d.keys():
            newk = renames.get(k, k)
            fn = conversions.get(newk, lambda l: dtup(l, Missing))     ## we could insist the conversions return dtup s
            a[newk] = fn(d[k])
    return a
