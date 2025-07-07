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

import builtins, polars as pl
from coppertop.pipe import *
from coppertop.dm.core.types import pylist, pytuple, pydict_keys, pydict_values, pyset, txt, t, offset, matrix, darray



# **********************************************************************************************************************
# aj
# **********************************************************************************************************************

@coppertop(style=binary)
def aj(f1:pl.DataFrame, f2:pl.DataFrame, k:txt, direction:txt):
    return f1.join_asof(f2, on=k, strategy='backward' if direction == 'prior' else 'forward')

@coppertop(style=binary)
def aj(f1:pl.DataFrame, f2:pl.DataFrame, k1:txt, k2:txt, direction:txt):
    return f1.join_asof(f2, left_on=k1, right_on=k2, strategy='backward' if direction == 'prior' else 'forward')


# **********************************************************************************************************************
# asc
# **********************************************************************************************************************

@coppertop(style=unary)
def asc(f:pl.DataFrame) -> pl.DataFrame:
    return f.sort(by=f >> keys >> at >> 0)


# **********************************************************************************************************************
# at
# **********************************************************************************************************************

@coppertop(style=binary)
def at(df:pl.DataFrame, k:txt):
    return df.get_column(k)

@coppertop(style=binary)
def at(df:pl.DataFrame, o:offset):
    return df.row(o)


# **********************************************************************************************************************
# drop
# **********************************************************************************************************************

@coppertop(style=binary)
def drop(f: pl.DataFrame, n: t.count) -> pl.DataFrame:
    if n >= 0:
        return f[n:]
    else:
        return f[:n]

@coppertop(style=binary)
def drop(f: pl.DataFrame, k:txt) -> pl.DataFrame:
    return f.drop(k)

@coppertop(style=binary)
def drop(f: pl.DataFrame, k:txt) -> pl.DataFrame:
    return f.drop(k)

@coppertop(style=binary)
def drop(f: pl.DataFrame, ks:pylist) -> pl.DataFrame:
    return f.drop(ks)


# **********************************************************************************************************************
# first
# **********************************************************************************************************************

@coppertop
def first(f: pl.Series):
    return f[0]

@coppertop
def first(f: pl.DataFrame) -> pl.DataFrame:
    return f[:1]


# **********************************************************************************************************************
# firstLast
# **********************************************************************************************************************

@coppertop
def firstLast(f: pl.DataFrame) -> pl.DataFrame:
    return f[[1, -1]]


# **********************************************************************************************************************
# keys
# **********************************************************************************************************************

@coppertop
def keys(df:pl.DataFrame) -> pylist:
    return df.columns


# **********************************************************************************************************************
# last
# **********************************************************************************************************************

@coppertop
def last(f: pl.DataFrame) -> pl.DataFrame:
    return f[-1:]

@coppertop
def last(f: pl.Series):
    return f[-1]


# **********************************************************************************************************************
# lj
# **********************************************************************************************************************

@coppertop(style=binary)
def lj(f1:pl.DataFrame, f2:pl.DataFrame, k:txt):
    return f1.join(f2, on=k, how='left')

@coppertop(style=binary)
def lj(f1:pl.DataFrame, f2:pl.DataFrame, k1:txt, k2:txt):
    return f1.join(f2, left_on=k1, right_on=k2, how='left')


# **********************************************************************************************************************
# numCols
# **********************************************************************************************************************

@coppertop
def numCols(df:pl.DataFrame) -> t.count:
    return len(df.columns) | t.count


# **********************************************************************************************************************
# numRows
# **********************************************************************************************************************

@coppertop
def numRows(df:pl.DataFrame) -> t.count:
    return len(df) | t.count


# **********************************************************************************************************************
# read - move to coppertop.dm.polars.csv
# **********************************************************************************************************************

@coppertop
def read(path:txt) -> pl.DataFrame:
    return pl.read_csv(path, parse_dates=True)


# **********************************************************************************************************************
# rename
# **********************************************************************************************************************

@coppertop(style=ternary)
def rename(f:pl.DataFrame, old:pylist+pytuple+pydict_keys+pydict_values, new:pylist+pytuple+pydict_keys+pydict_values) -> pl.DataFrame:
    oldNew = dict(builtins.zip(old, new))
    return f.rename(oldNew)

@coppertop(style=ternary)
def rename(f:pl.DataFrame, old:txt, new:txt) -> pl.DataFrame:
    oldNew = {old:new}
    return f.rename(oldNew)


# **********************************************************************************************************************
# shape
# **********************************************************************************************************************

@coppertop
def shape(df:pl.DataFrame) -> pytuple:
    return df.shape #(len(df) | t.count, len(df.columns) | t.count)


# **********************************************************************************************************************
# take
# **********************************************************************************************************************

@coppertop(style=binary)
def take(f: pl.DataFrame, n: t.count) -> pl.DataFrame:
    if n >= 0:
        return f[:n]
    else:
        return f[n:]

@coppertop(style=binary)
def take(f: pl.DataFrame, ks: pylist+pyset) -> pl.DataFrame:
    return f.select(ks)

@coppertop(style=binary)
def take(f: pl.DataFrame, k: txt) -> pl.DataFrame:
    return f.select(k)


# **********************************************************************************************************************
# takePanel
# **********************************************************************************************************************

@coppertop
def takePanel(f: pl.DataFrame) -> matrix&darray:
    return (matrix&darray)(f.to_numpy())


# **********************************************************************************************************************
# where
# **********************************************************************************************************************

@coppertop(style=binary)
def where(f:pl.DataFrame, pred:pl.Expr) -> pl.DataFrame:
    return f.filter(pred)


# **********************************************************************************************************************
# xasc
# **********************************************************************************************************************

@coppertop(style=binary)
def xasc(f:pl.DataFrame, ks:pylist+pytuple) -> pl.DataFrame:
    return f.sort(by=ks)

@coppertop(style=binary)
def xasc(f:pl.DataFrame, k:txt) -> pl.DataFrame:
    return f.sort(by=k)

