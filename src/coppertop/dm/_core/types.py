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


# a collection of usual types that aren't essential to the bones language
# in bones types can have constructors associated with them - so we have some classes embedded in the types module
# more for convenience and ease of understanding the module structure rather than anything deeper

import builtins, numpy as np
from coppertop.pipe import *
from coppertop.utils import Missing, ProgrammerError, NotYetImplemented, ImpossiblePathError
from bones.ts.metatypes import BTAtom, BType, weaken, extractConstructors
from bones.lang.types import *
import bones.lang.types
from coppertop.dm._core.structs import _tvtuple, _tvstruct, _tvarray, _tvseq, _tvmap
from bones.ts.core import Constructors


__all__ = bones.lang.types.__all__


inty = BTAtom('inty')

i8 = BTAtom('i8')
u8 = BTAtom('u8')
i16 = BTAtom('i16')
u16 = BTAtom('u16')
i32 = BTAtom('i32')
u32 = BTAtom('u32')
i64 = BTAtom('i64')
u64 = BTAtom('u64')
f32 = BTAtom('f32')
f64 = BTAtom('f64')

__all__ += [
    'i8', 'u8', 'i16', 'u16', 'i32', 'u32', 'i64', 'u64', 'f32', 'f64',
]



# litbool is parsed in the SM to a storage format of a python bool and on assignment is notionally weakened to a
# bool - in reality we just equate bool and python bool
def _makeBool(t, v):
    return builtins.bool(v)
bool = BTAtom('bool', space=mem).setCoercer(_makeBool).setConstructor(_makeBool)
__all__ += ['bool']



# **********************************************************************************************************************
# classes for the underlying storage of floats - for num _t is hard-coded to avoid boxing
# **********************************************************************************************************************

class num_(float):
    # unboxed float
    def __new__(cls, *args_, **kwargs_):
        if not args_: raise SyntaxError(f'Needs arguments, got {args_}')
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) == 1:
                t = constrs[0]
                if len(args) != 1: raise SyntaxError(f'{t}(...) expected 1 argument, got {args}')
                if not fitsWithin(t, num): raise TypeError(f'Expected a type derived from num, got {t}')
                return super(cls, cls).__new__(cls, args[0])
            else:
                raise NotYetImplemented()
        else:
            if len(args) == 2:
                t, v = args
                # OPEN: do some type checking here
                instance = super(cls, cls).__new__(cls, v)
                return instance
            else:
                raise SyntaxError(f'| {args[0]} 1 argument, got {len(args)}')
    @property
    def _t(self):
        return num
    def _v(self):
        return self
    def __repr__(self):
        return f'{super().__repr__()}'
num = BType('num: num & f64 in mem').setCoercer(num_).setConstructor(num_)
__all__ += ['num']


class tvfloat_(float):
    # a boxed float
    def __new__(cls, *args_, **kwargs_):
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) != 1: raise NotYetImplemented()
            constr = constrs[0]
            t, v = args
            instance = super(cls, cls).__new__(cls, v)
            instance._t_ = t
            return instance
        else:
            raise NotYetImplemented()
    @property
    def _v(self):
        return super().__new__(float, self)
    @property
    def _t(self):
        return self._t_
    def __repr__(self):
        return f'{self._t}{super().__repr__()}'
    def _asT(self, t):
        self._t_ = t
        return self
tvfloat = BType('tvfloat: tvfloat & f64 in mem').setConstructor(tvfloat_).setCoercer(tvfloat_)
__all__ += ['tvfloat']



# **********************************************************************************************************************
# classes for the underlying storage of integers - for index, count and offset _t is hard-coded to avoid boxing
# **********************************************************************************************************************

class ptr_(int):
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return ptr
    @property
    def _v(self):
        return self
    def __repr__(self):
        return f'*{self:012x}'          # could add hidden flag later on
ptr = BType('ptr: atom in ptr').setCoercer(ptr_)
__all__ += ['ptr']


indexy = BType('indexy: indexy & inty in mem')
__all__ += ['indexy']


# hack in Python so can do N**txt
N = BTAtom('N')
for i in range(1, 10):
    t = BTAtom(f'N{i}')
    locals()[t.name] = t
__all__ += ['N', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9']


# litint is parsed in the SM to a storage format of a python int and on assignment is notionally weakened to an
# index - in reality we just equate num and python float
class index_(int):
    # 1 based
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return index
    def _v(self):
        return self
    def __repr__(self):
        return f'i{super().__repr__()}'
index = BType('index: index & indexy in indexy').setCoercer(index_)
__all__ += ['index']


class count_(int):
    # tv representing counts, natural numbers starting at 0
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    # def __add__(self, other):
    #     return NotImplemented
    # def __sub__(self, other):
    #     return NotImplemented
    # def __mul__(self, other):
    #     return NotImplemented
    # def __div__(self, other):
    #     return NotImplemented
    @property
    def _t(self):
        return count
    @property
    def _v(self):
        return self
    def __repr__(self):
        return f'{super().__repr__()}'
count = BType('count: atom in mem').setCoercer(count_)
__all__ += ['count']


class offset_(int):
    # (0 based)
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return offset
    def _v(self):
        return self
    def __repr__(self):
        return f'{super().__repr__()}'
offset = BType('offset: offset & indexy in indexy').setCoercer(offset_)
__all__ += ['offset']


class tvint_(int):
    def __new__(cls, t, v, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, v)
        instance._t = t
        return instance
    @property
    def _v(self):
        return self #super().__new__(int, self)
    def __repr__(self):
        return f'{self._t}{super().__repr__()}'
    def _asT(self, t):
        self._t = t
        return self
tvint = BType('tvint: tvint & inty in mem').setConstructor(tvint_)
__all__ += ['tvint']



# **********************************************************************************************************************
# class for the underlying storage of text - as with index, count and offset _t is hard-coded to avoid boxing
# **********************************************************************************************************************

class _tvstr(builtins.str):
    def __new__(cls, *args_, **kwargs_):
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) != 1: raise NotYetImplemented()
            constr = constrs[0]
            if len(args) == 0:
                raise NotYetImplemented()
            elif len(args) == 1:
                instance = super(cls, cls).__new__(cls, args[0])
                if constr != txt:
                    instance._t_ = constr
                return instance
            else:
                raise SyntaxError(f'Expected 1 argument, got {len(args)}')
        else:
            raise ImpossiblePathError()
    @property
    def _t(self):
        return getattr(self, '_t_', txt)  # default to txt if not set
    @property
    def _v(self):
        return self
    def __repr__(self):
        return f'txt({super().__repr__()})'
    def _asT(self, t):
        self._t_ = t
        return self

def _coerceToTxt(t, v):
    if isinstance(v, _tvstr):
        return v.asT(t)
    elif isinstance(v, str):
        return txt(v)._asT(t)
    # elif isinstance(v, bytes):
    #     return txt_(t, v.decode('utf-8'))
    else:
        raise TypeError(f'Cannot coerce {v} of type {type(v)} to txt')

txt = BType('txt: atom in mem').setConstructor(_tvstr).setCoercer(_coerceToTxt)
__all__ += ['txt']



# **********************************************************************************************************************
# classes for the underlying storage of dates
# **********************************************************************************************************************

# litdate is parsed in the SM to a storage format of a python datetime.date and on assignment is notionally weakened
# to a date - in reality we just equate rub date and python datetime.date
date = BType('date: atom in mem')

__all__ += ['date']



# **********************************************************************************************************************
# types for dealing with python - not needed in a non-python implementation
# **********************************************************************************************************************


def coercer(t, v):
    tV = typeOf(v)
    try:
        fits = fitsWithin(typeOf(v), t)
    except Exception as ex:
        fits = (tV == t)
    if fits or t == py:
        return v
    else:
        raise TypeError(f'Cannot type {type(v)} to {t} - {v}')


py = BType('py: atom in mem').setCoercer(coercer)


pylist = BType('pylist: pylist & py in mem').setCoercer(coercer)
@coppertop
def _const_pylist(t:Constructors, x) -> pylist:
    return list(x)
pylist.setConstructor(_const_pylist)

pytuple = BType('pytuple: pytuple & py in mem').setCoercer(coercer)

pydict = BType('pydict: pydict & py in mem').setCoercer(coercer)
def _pydictCons(*args_, **kwargs_) -> pydict:
    constrs, args, kwargs = extractConstructors(args_, kwargs_)
    if constrs:
        if len(constrs) != 1: raise NotYetImplemented()
        constr = constrs[0]
        if len(args) == 0:
            return dict()
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, tuple):     # a pair of ks and values
                if len(arg) == 2:
                    ks, vs = arg
                    assert len(ks) == len(vs), f'Keys and values must be the same length, got {len(ks)} and {len(vs)}'
                    return dict(zip(ks, vs))
                else:
                    raise NotYetImplemented()
            return dict(arg)
        elif len(args) == 2:
            ks, vs = args[0]
            return dict(zip(ks, vs))
        else:
            raise NotYetImplemented()
        return dict(args[0])
    else:
        raise ImpossiblePathError()
pydict.setConstructor(_pydictCons)

pyset = BType('pyset: pyset & py in mem').setCoercer(coercer)
npfloat = BType('npfloat: npfloat & py in mem').setCoercer(coercer)
pydict_keys = BType('pydict_keys: pydict_keys & py in mem').setCoercer(coercer)
pydict_values = BType('pydict_values: pydict_values & py in mem').setCoercer(coercer)
pydict_items = BType('pydict_items: pydict_items & py in mem').setCoercer(coercer)
pyfunc = BType('pyfunc: pyfunc & py in mem').setCoercer(coercer)

pyint = BType('pyint: pyint & py in mem')


txt = BType('txt: atom in mem').setConstructor(_tvstr).setCoercer(_coerceToTxt)


__all__ += [
    'py', 'pyint', 'pylist', 'pytuple', 'pydict', 'pyset', 'npfloat', 'pydict_keys', 'pydict_values', 'pydict_items', 'pyfunc',
    'matrix', 'vec'
]



# **********************************************************************************************************************
# other
# **********************************************************************************************************************

err = BTAtom('err')             # an error code of some sort
missing = BTAtom('missing')     # something that isn't there and should be there

sys._Missing._t = missing
sys._ERR._t = err


__all__ += [
    'err', 'missing', 'null', 'void',
]


# **********************************************************************************************************************
# vec and matrix
# **********************************************************************************************************************

def create1DTvArray(*args_, **kwargs):
    constr, args = (args_[0][0], args_[1:]) if args_ and isinstance(args_[0], Constructors) else (Missing, args_)
    if len(args) == 1:
        t, x = constr, args[0]
    else:
        t, x = args
    answer = darray(t, x)
    ndims = len(answer.shape)
    if ndims == 0:
        answer.shape = (1, )
    elif ndims == 2:
        if answer.shape[0] == 1:
            answer.shape = answer.shape[1]
        elif answer.shape[1] == 1:
            answer.shape = answer.shape[0]
        else:
            raise TypeError(f'Can\' coerce shape {answer.shape} to 1D')
    elif ndims > 2:
        raise TypeError('x has more than 2 dimensions')
    return answer | t

def _consMatrix(*args_, **kwargs_):
    constrs, args, kwargs = extractConstructors(args_, kwargs_)
    if len(args) == 0:
        raise SyntaxError('Matrix constructor must have at least one argument')
    elif len(args) == 1:
        arg = args[0]
        if isinstance(arg, (list, tuple)) and arg:
            if isinstance(arg[0], (list, tuple)):
                # arg is a list of lists
                return darray(*args_, **kwargs_)
            else:
                # matrix( [1,4] ) into a 1x2 matrix
                return darray(constrs, list(args), **kwargs)
        else:
            return darray(constrs, arg, **kwargs)
    else:
        # for convenience let's make matrix([1,4],[2,5],[3,6]) into a 3x2 matrix
        return darray(constrs, list(args), **kwargs)

    # answer = darray(t, x)
    # ndims = len(answer.shape)
    # if ndims == 0:
    #     answer.shape = (1, 1)
    # elif ndims == 1:
    #     answer.shape = (answer.shape[0], 1)
    # elif ndims > 2:
    #     raise TypeError('x has more than 2 dimensions')
    # return answer | t


darray = BType('darray: darray & py in mem').setConstructor(_tvarray)
vec = BType('vec: vec & (N**num) & darray in mem')      #jones.BTypeError: There are exclusion conflicts within (num, darray)
# vec = BType('vec: vec & darray in mem')
# matrix = BType('matrix: matrix & N**N**num')
matrix = BType('matrix: matrix & (N**N**num) & darray in mem').setConstructor(_consMatrix)          # jones.BTypeError: There are exclusion conflicts within (num, darray)
# matrix = BType('matrix: matrix & darray in mem').setConstructor(_consMatrix)


# BType('(N**num) & darray in mem').setConstructor(create1DTvArray)
# BType('vec & darray in mem').setConstructor(create1DTvArray)
# BType('matrix & darray in mem').setConstructor(create2DTvArray)


# could make +, -, / and * be type aware by having index, offset, count, etc being familial as well as orthogonal

class thing: pass
t = thing()     # t for types in anticipation of BType namespacing and import coppertop.bones_types as t
t.count = count
t.index = index
t.offset = offset



@coppertop
def sequence_(n):
    return range(n)
offset.sequence_ = sequence_


def createDFrame(*args_, **kwargs_):
    constrs, args, kwargs = extractConstructors(args_, kwargs_)
    if len(args) == 0:
        return _tvstruct(constrs, **kwargs)
    elif len(args) == 1:
        t = args[0]
        assert t.keys() == kwargs.keys()
        return _tvstruct(constrs[0] & t, **kwargs)
    else:
        raise ProgrammerError()

def _coerceToDseq(t, v):
    return dseq(t, v)

dtup = BType('dtup: dtup & py in mem').setConstructor(_tvtuple)
dstruct = BType('dstruct: dstruct & py in py').setConstructor(_tvstruct)
dseq = BType('dseq: dseq & py in py').setConstructor(_tvseq).setCoercer(_coerceToDseq)  # & N**T
dmap = BType('dmap: dmap & py in py').setConstructor(_tvmap)                            # & T1**T2
dframe = BType('dframe: dframe & frame & py in mem').setConstructor(createDFrame)       # & N**BTStruct(...)


# in python we need a super type for dynamic programming
# in bones we wouldn't as we would know the structures type
#
# we have more than one implementation for the struct - with a common functional interface
# so full type is struct&dstruct&BTStruct(....)
# then
# def join(struct[T1], struct[T2]) -> struct[T1 and T2] + err:
#
# adhoc(BTStruct(fred=pyint), fred=1)
# " " ~ " "
#
# class fred:
#     def __


pyndarray = BType('pyndarray: pyndarray & py in mem')


__all__ += [
    'dtup', 'dstruct', 'dseq', 'dmap', 'dframe', 'darray', 'pyndarray'
]

__all__ += [
    'pytype', 'btype'
]


# **********************************************************************************************************************
# frames
# **********************************************************************************************************************

polarframe = BType('polarframe: polarframe & py in mem')
polarseries = BType('polarseries: polarseries & py in mem')
pandaframe = BType('pandaframe: pandaframe & py in mem')


__all__ += [
    'polarframe', 'polarseries', 'pandaframe'
]


# **********************************************************************************************************************
# add mappings of classes to types
# **********************************************************************************************************************

def _init():
    # easiest way to keep namespace a little cleaner
    import datetime, types
    from coppertop.pipe import _btypeByClass
    from coppertop.utils.types import dict_keys, dict_items, dict_values

    weaken(litint, (offset, num, count, index))
    weaken(pyint, (offset, num, count, index))
    weaken(litnum, (num,))
    weaken(type(None), (null, void))
    weaken(littxt, (txt,))

    _btypeByClass.update({
        builtins.int: pyint,
        builtins.str: txt,
        datetime.date: date,
        builtins.float: num,
        builtins.bool: bool,
        builtins.tuple: pytuple,
        builtins.list: pylist,
        builtins.dict: pydict,
        builtins.set: pyset,
        dict_keys: pydict_keys,
        dict_items: pydict_items,
        dict_values: pydict_values,
        types.FunctionType: pyfunc,
        np.ndarray: pyndarray,
    })



_init()




if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
