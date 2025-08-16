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
from coppertop.pipe import _btypeByClass
from coppertop.utils import NotYetImplemented, ImpossiblePathError
from bones.ts.metatypes import BType, extractConstructors
from coppertop.dm.core.types import pylist, pytuple, pydict_keys, pydict_values, pyset, txt, t, offset, matrix, darray, \
    pydict, index, polarframe, polarseries


_btypeByClass[pl.DataFrame] = polarframe
_btypeByClass[pl.Series] = polarseries

# def _conPolarframe(f:pl.DataFrame) -> polarframe:
#     """
#     Coerce a polars DataFrame to a polarframe.
#     """
#     def __new__(cls, *args_, **kwargs_):
#         constrs, args, kwargs = extractConstructors(args_, kwargs_)
#         if constrs:
#             if len(constrs) != 1: raise NotYetImplemented()
#             constr = constrs[0]
#             raise NotYetImplemented()
#         else:
#             raise ImpossiblePathError()
#
#
#     return polarframe(f)


# **********************************************************************************************************************
# aj
# **********************************************************************************************************************

@coppertop(style=binary)
def aj(f1:polarframe, f2:polarframe, k:txt, direction:txt):
    return f1.join_asof(f2, on=k, strategy='backward' if direction == 'prior' else 'forward')

@coppertop(style=binary)
def aj(f1:polarframe, f2:polarframe, k1:txt, k2:txt, direction:txt):
    return f1.join_asof(f2, left_on=k1, right_on=k2, strategy='backward' if direction == 'prior' else 'forward')


# **********************************************************************************************************************
# asc
# **********************************************************************************************************************

@coppertop(style=unary)
def asc(f:polarframe) -> polarframe:
    return f.sort(by=f >> colNames >> at >> 0)


# **********************************************************************************************************************
# at
# **********************************************************************************************************************

@coppertop(style=binary)
def at(df:polarframe, k:txt):
    return df.get_column(k)

@coppertop(style=binary)
def at(df:polarframe, o:offset) -> pydict:
    return df.row(o, named=True)

@coppertop(style=binary)
def at(df:polarframe, i:index) -> pydict:
    return df.row(i - 1, named=True)

@coppertop(style=binary)
def at(s:polarseries, o:offset):
    return s[o]

@coppertop(style=binary)
def at(s:polarseries, i:index):
    return s[i - 1]


# **********************************************************************************************************************
# colNames
# **********************************************************************************************************************

@coppertop
def colNames(df:polarframe) -> pylist:
    return df.columns


# **********************************************************************************************************************
# conv
# **********************************************************************************************************************

@coppertop
def conv(f:polarframe, conversions:pydict) -> polarframe:
    for n, conversion in conversions.items():
        f = f.with_columns(conversion(pl.col(n)))
    return f


# **********************************************************************************************************************
# diffRows
# **********************************************************************************************************************

@coppertop
def diffRows(f: polarframe) -> polarframe:
    """
    Returns a DataFrame containing the differences between consecutive rows.
    """
    numericCols = f.select(pl.selectors.numeric())
    for n, c in zip(numericCols.columns, numericCols):
        f = f.with_columns(pl.col(n).diff(1))
    return f


# **********************************************************************************************************************
# drop
# **********************************************************************************************************************

@coppertop(style=binary)
def drop(f: polarframe, n: t.count) -> polarframe:
    if n >= 0:
        return f[n:]
    else:
        return f[:n]

@coppertop(style=binary)
def drop(f: polarframe, k:txt) -> polarframe:
    return f.drop(k)

@coppertop(style=binary)
def drop(f: polarframe, ks:pylist) -> polarframe:
    # OPEN: distinguish between a list of ints and a list of txt
    return f.drop(ks)


# **********************************************************************************************************************
# first
# **********************************************************************************************************************

@coppertop
def first(f: polarseries):
    return f[0]

@coppertop
def first(f: polarframe) -> polarframe:
    return f[:1]


# **********************************************************************************************************************
# firstLast
# **********************************************************************************************************************

@coppertop
def firstLast(f: polarframe) -> polarframe:
    return f[[1, -1]]

@coppertop
def firstLast(f: polarseries) -> polarseries:
    return f[[1, -1]]


# **********************************************************************************************************************
# last
# **********************************************************************************************************************

@coppertop
def last(f: polarframe) -> polarframe:
    return f[-1:]

@coppertop
def last(f: polarseries):
    return f[-1]


# **********************************************************************************************************************
# lj
# **********************************************************************************************************************

@coppertop(style=binary)
def lj(f1:polarframe, f2:polarframe, k:txt):
    return f1.join(f2, on=k, how='left')

@coppertop(style=binary)
def lj(f1:polarframe, f2:polarframe, k1:txt, k2:txt):
    return f1.join(f2, left_on=k1, right_on=k2, how='left')


# **********************************************************************************************************************
# numCols
# **********************************************************************************************************************

@coppertop
def numCols(df:polarframe) -> t.count:
    return len(df.columns) | t.count


# **********************************************************************************************************************
# numRows
# **********************************************************************************************************************

@coppertop
def numRows(df:polarframe) -> t.count:
    return len(df) | t.count


# **********************************************************************************************************************
# read - move to coppertop.dm.polars.csv
# **********************************************************************************************************************

@coppertop
def read(path:txt) -> polarframe:
    return pl.read_csv(path, try_parse_dates=True)


# **********************************************************************************************************************
# rename
# **********************************************************************************************************************

@coppertop
def rename(f:polarframe, newByOld:pydict) -> polarframe:
    return f.rename(newByOld)

@coppertop
def rename(f:polarframe, old:pylist+pytuple+pydict_keys+pydict_values, new:pylist+pytuple+pydict_keys+pydict_values) -> polarframe:
    oldNew = dict(builtins.zip(old, new))
    return f.rename(oldNew)

@coppertop
def rename(f:polarframe, old:txt, new:txt) -> polarframe:
    oldNew = {old:new}
    return f.rename(oldNew)


# **********************************************************************************************************************
# schema
# **********************************************************************************************************************

@coppertop
def schema(df:polarframe) -> pl.Schema:
    return df.schema


# **********************************************************************************************************************
# shape
# **********************************************************************************************************************

@coppertop
def shape(df:polarframe) -> pytuple:
    return df.shape #(len(df) | t.count, len(df.columns) | t.count)


# **********************************************************************************************************************
# take
# **********************************************************************************************************************

@coppertop(style=binary)
def take(f: polarframe, n: t.count) -> polarframe:
    if n >= 0:
        return f[:n]
    else:
        return f[n:]

@coppertop(style=binary)
def take(f: polarframe, ks: pylist+pyset) -> polarframe:
    return f.select(ks)

@coppertop(style=binary)
def take(f: polarframe, k: txt) -> polarframe:
    return f.select(k)


# **********************************************************************************************************************
# takePanel
# **********************************************************************************************************************

@coppertop
def takePanel(f: polarframe) -> matrix:
    return (matrix)(f.to_numpy())


# **********************************************************************************************************************
# to
# **********************************************************************************************************************

@coppertop(style=binary)
def to(col: pl.Expr, t:pl.DataTypeClass) -> pl.Expr:
    """
    Answers a polars Expr to cast to the given type.
    See https://docs.pola.rs/api/python/dev/reference/expressions/api/polars.Expr.cast.html#polars.Expr.cast
    """
    return col.cast(t)

@coppertop(style=binary)
def to(col: pl.Expr, t, format: txt) -> pl.Expr:
    """
    Answers a polars Expr to cast to the given type using the format.
    See https://docs.pola.rs/api/python/dev/reference/expressions/api/polars.Expr.cast.html#polars.Expr.cast
    """
    if t == pl.Date:
        return col.str.to_date(format=format)
    elif t == pl.Datetime:
        return col.str.to_datetime(format=format)
    elif t == pl.Time:
        return col.str.to_time(format=format)
    else:
        raise TypeError(f"Got a {t} for t but only support pl.Date, pl.Datetime, and pl.Time.")

@coppertop(style=binary)
def to(d:pydict, t:polarframe):
    return pl.DataFrame(d)


# **********************************************************************************************************************
# toPolars
# **********************************************************************************************************************

@coppertop
def toPolars(d:pydict):
    return pl.DataFrame(d)


# **********************************************************************************************************************
# where
# **********************************************************************************************************************

@coppertop(style=binary)
def where(f:polarframe, pred:pl.Expr) -> polarframe:
    return f.filter(pred)

@coppertop(style=binary)
def where(f:polarframe, fn) -> polarframe:
    return f.filter([fn(d) for d in f.to_dicts()])


# **********************************************************************************************************************
# xasc
# **********************************************************************************************************************

@coppertop(style=binary)
def xasc(f:polarframe, ks:pylist+pytuple) -> polarframe:
    return f.sort(by=ks)

@coppertop(style=binary)
def xasc(f:polarframe, k:txt) -> polarframe:
    return f.sort(by=k)

