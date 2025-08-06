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

import abc, numpy as np, typing
from collections import UserList, UserDict
from coppertop.pipe import fitsWithin, typeOf
from coppertop.utils import context, Missing, Void, NotYetImplemented, PathNotTested, ProgrammerError

from bones.ts.metatypes import BType, extractConstructors
from bones.ts.core import Constructors


__all__ = [
    '_tvdate', '_tvtime', '_tvdatetime',
    '_tvtuple', '_tvstruct',
    '_tvseq', '_tvmap', '_tvarray',
]


# the tv structs implement common simple and container classes. As well as the expected public API they also implement
# _t and _v so appear as boxes.



# **********************************************************************************************************************
# simple types
# **********************************************************************************************************************

class _tvdate: pass
class _tvtime: pass
class _tvdatetime: pass



# **********************************************************************************************************************
# product types (each element has a specific known type)
# **********************************************************************************************************************

class _tvtuple(list):
    # we need to be able to assign into a slot so a Python list rather than a Python tuple (which is immutable)
    __slots__ = ['_t']

    def __new__(cls, *args_, **kwargs_):
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) != 1: raise NotYetImplemented()
            constr = constrs[0]
            if len(args) == 2:
                t, v = args
                instance = super().__new__(cls, v)
                instance._t = t
                instance._init(v)
                return instance
            raise SyntaxError()
        else:
            raise NotYetImplemented()

    def _init(self, v):
        super().__init__(v)

    def __init__(self, *args_, **kwargs_):
        pass

    def __getattribute__(self, f):
        if f in ('append', 'extend', 'insert', 'remove', 'pop', 'clear', 'sort', 'reverse'):
            raise AttributeError(f'{f} is Missing')
        else:
            return super().__getattribute__(f)

    def __repr__(self):
        # OPEN: shorten type PP to first 2 types
        strs = (f"{str(e)}" for e in self)
        rep = f'{self._t}({", ".join(strs)})'
        return rep

    @property
    def _v(self):
        return self



class _tvstruct:
    __slots__ = ['_pub', '_pvt']

    def __init__(self, *args_, **kwargs_):
        super().__init__()
        super().__setattr__('_pvt', {})
        super().__setattr__('_pub', {})
        super().__getattribute__('_pvt')['_t'] = type(self)
        super().__getattribute__('_pvt')['_v'] = self

        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            constr = constrs[0]
            if len(args) == 0:
                # _tvstruct(), _tvstruct(**kwargs)
                if constr:
                    super().__getattribute__('_pvt')['_t'] = constr
                if kwargs:
                    super().__getattribute__('_pub').update(kwargs)
            elif len(args) == 1:
                # _tvstruct(_tvstruct), _tvstruct(dictEtc)
                arg1 = args[0]
                if isinstance(arg1, _tvstruct):
                    # _tvstruct(_tvstruct)
                    super().__getattribute__('_pvt')['_t'] = arg1._t
                    super().__getattribute__('_pub').update(arg1._pub)
                elif isinstance(arg1, (dict, list, tuple, zip)):
                    # _tvstruct(dictEtc)
                    super().__getattribute__('_pub').update(arg1)
                    if constr:
                        super().__getattribute__('_pvt')['_t'] = constr
                else:
                    # _tvstruct(t), _tvstruct(t, **kwargs)
                    super().__getattribute__('_pvt')['_t'] = arg1
                    if kwargs:
                        # _tvstruct(t, **kwargs)
                        super().__getattribute__('_pub').update(kwargs)
            elif len(args) == 2:
                # _tvstruct(t, _tvstruct), _tvstruct(t, dictEtc)
                arg1, arg2 = args
                if kwargs:
                    # this needs sorting but I don't have time right now
                    # came up for `PMF(Brown=30, Yellow=20, Red=20, Green=10, Orange=10, Tan=10)`
                    # having two types (PMF and then _tvstruct do the construction so args is (_tvstruct, PMF)
                    super().__getattribute__('_pvt')['_t'] = arg2
                    super().__getattribute__('_pub').update(kwargs)
                    # raise TypeError('No kwargs allowed when 2 args are provided')
                    return None
                super().__getattribute__('_pvt')['_t'] = arg1
                if isinstance(arg2, _tvstruct):
                    # _tvstruct(t, _tvstruct)
                    super().__getattribute__('_pub').update(arg2._pub)
                else:
                    # _tvstruct(t, dictEtc)
                    super().__getattribute__('_pub').update(arg2)
            else:
                raise TypeError(
                    '_tvstruct(...) must be of form _tvstruct(), _tvstruct(**kwargs), _tvstruct(_tvstruct), _tvstruct(dictEtc), ' +
                    '_tvstruct(t), _tvstruct(t, **kwargs), _tvstruct(t, _tvstruct), _tvstruct(t, dictEtc), '
                )
        else:
            if len(args) == 1:
                # _tvstruct(_tvstruct)
                arg1 = args[0]
                if isinstance(arg1, _tvstruct):
                    # _tvstruct(_tvstruct)
                    super().__getattribute__('_pvt')['_t'] = arg1._t
                    super().__getattribute__('_pub').update(arg1._pub)
                else:
                    raise ProgrammerError()
            else:
                raise ProgrammerError()

    def __asT__(self, t):
        super().__getattribute__('_pvt')['_t'] = t
        return self

    def __copy__(self):
        return _tvstruct(self)

    def __getattribute__(self, f):
        if f[0:2] == '__':
            try:
                answer = super().__getattribute__(f)
            except AttributeError as e:
                answer = super().__getattribute__('_pvt').get(f, Missing)
            if answer is Missing:
                if f in ('__class__', '__len__', '__members__', '__getstate__'):
                    # don't change behaviour
                    raise AttributeError()
            return answer

        if f[0:1] == "_":
            if f == '_pvt': return super().__getattribute__('_pvt')
            if f == '_pub': return super().__getattribute__('_pub')
            if f == '_asT': return super().__getattribute__('__asT__')
            if f == '_t': return super().__getattribute__('_pvt')['_t']
            if f == '_v': return super().__getattribute__('_pvt')['_v']
            # if f == '_asT': return super().__getattribute__('_asT')
            if f == '_keys': return super().__getattribute__('_pub').keys
            if f == '_kvs': return super().__getattribute__('_pub').items
            if f == '_values': return super().__getattribute__('_pub').values
            if f == '_update': return super().__getattribute__('_pub').update
            if f == '_get': return super().__getattribute__('_pub').get
            if f == '_pop': return super().__getattribute__('_pub').pop
            # if names have been added e.g. by self['_10y'] allow access as long as not double entered
            pub = super().__getattribute__('_pub').get(f, Missing)
            pvt = super().__getattribute__('_pvt').get(f, Missing)
            if pub is Missing: return pvt
            if pvt is Missing: return pub
            raise AttributeError(f'public and private entries exist for {f}')
        # print(f)
        # I think we can get away without doing the following
        # if f == 'items':
        #     # for pycharm :(   - pycharm knows we are a subclass of dict so is inspecting us via items
        #     # longer term we may return a BTStruct instead of struct in response to __class__
        #     return {}.items
        v = super().__getattribute__('_pub').get(f, Missing)
        if v is Missing:
            raise AttributeError(f'{f} is Missing')
        else:
            return v

    def __setattr__(self, f, v):
        if f[0:1] == "_":
            if f == '_t_': return super().__getattribute__('_pvt').__setitem__('_t', v)
            # if f in ('_t', '_v', '_pvt', '_pub'): raise AttributeError(f"Can't set {f} on _tvstruct")
            if f in ('_pvt', '_pub'): raise AttributeError(f"Can't set {f} on _tvstruct")
            return super().__getattribute__('_pvt').__setitem__(f, v)
        return super().__getattribute__('_pub').__setitem__(f, v)

    def __getitem__(self, fOrFs):
        if isinstance(fOrFs, (list, tuple)):
            kvs = {f: self[f] for f in fOrFs}
            return _tvstruct(self._t, kvs)
        else:
            _pub = super().__getattribute__('_pub')
            return _pub.__getitem__(fOrFs)

    def __setitem__(self, f, v):
        if isinstance(f, str):
            if f[0:1] == "_":
                if f in ('_pvt', '_pub', '_keys', '_kvs', '_values', '_update', '_get'):
                    raise AttributeError(f'name {f} is reserved for use by _tvstruct')
                # if f in super().__getattribute__('_pvt'):
                #     raise AttributeError(f'name {f} is already in pvt use')
        super().__getattribute__('_pub').__setitem__(f, v)

    def __delitem__(self, fOrFs):
        if isinstance(fOrFs, (list, tuple)):
            for f in fOrFs:
                super().__getattribute__('_pub').__delitem__(f)
        else:
            super().__getattribute__('_pub').__delitem__(fOrFs)

    def __contains__(self, f):
        return super().__getattribute__('_pub').__contains__(f)

    def __call__(self, **kwargs):
        # OPEN: do we neeed this?
        _pub = super().__getattribute__('_pub')
        for f, v in kwargs.items():
            _pub.__setitem__(f, v)
        return self

    def __dir__(self) -> typing.Iterable[str]:
        # return super().__getattribute__('_pub').keys()
        return [k for k in super().__getattribute__('_pub').keys() if isinstance(k, str)]

    def __repr__(self):
        _pub = super().__getattribute__('_pub')
        _t = super().__getattribute__('_pvt')['_t']
        itemStrings = (f"{str(k)}={repr(v)}" for k, v in _pub.items())

        if type(_t) is abc.ABCMeta or _t is _tvstruct:
            name = _t.__name__
        else:
            name = str(self._t)
        rep = f'{name}({", ".join(itemStrings)})'
        return rep

    def __len__(self):
        return len(super().__getattribute__('_pub'))

    def __eq__(self, rhs):  # self == rhs
        if isinstance(rhs, dict):
            raise NotYetImplemented()
        elif isinstance(rhs, _tvstruct):
            return self._kvs() == rhs._kvs()
        else:
            return False

    def __iter__(self):
        # iter on public name value pairs
        return iter(super().__getattribute__('_pub').items())



# **********************************************************************************************************************
# exponential types (elements are of same type) - _tvseq, _tvmap, _tvarray
# **********************************************************************************************************************

class _tvseq(UserList):
    __slots__ = ['_t', 'data']

    def __init__(self, *args_, **kwargs_):
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) != 1: raise NotYetImplemented()
            constr = constrs[0]
            if len(args) == 1:
                arg = args[0]
                if isinstance(arg, _tvseq):
                    # dseq(dseq)
                    super().__init__(arg._v)
                    self._t = arg._t
                elif isinstance(arg, BType):
                    # dseq(<BType>)
                    super().__init__()
                    self._t = arg
                else:
                    raise TypeError("Can't create dseq without type information")
            elif len(args) == 2:
                # dseq(t, iterable)
                arg1, arg2 = args
                super().__init__(arg2)
                self._t = arg1
            elif len(args) == 3:
                # dseq(dseq, t, iterable)
                arg1, arg2, arg3 = args
                assert isinstance(arg1, Constructors)
                super().__init__(arg3)
                self._t = arg2
            else:
                raise TypeError("Invalid arguments to _tvseq constructor")
        else:
            if len(args) == 2:
                t, v = args
                super().__init__(v)
                self._t = t
            else:
                raise NotYetImplemented()

    @property
    def _v(self):
        return self.data

    def _asT(self, t):
        self._t = t
        return self

    def __repr__(self):
        itemStrings = (f"{str(e)}" for e in self.data)
        t = self._t
        if type(t) is abc.ABCMeta or t is _tvseq:
            name = self._t.__name__
        else:
            name = str(self._t)
        rep = f'{name}({", ".join(itemStrings)})'
        return rep

    def __eq__(self, other):
        if isinstance(other, _tvseq):
            return self._t == other._t and self.data == other.data
        else:
            return False

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self._t, self.data[i])
        else:
            return self.data[i]



class _tvmap(UserDict):
    __slots__ = ['_t', 'data']

    def __new__(cls, *args_, **kwargs):
        constr, args = (args_[0][0], args_[1:]) if args_ and isinstance(args_[0], Constructors) else (Missing, args_)
        if len(args) == 0:
            if kwargs:
                # xxx(a=1, b=2)
                instance = super().__new__(cls)
                instance.data = {}
                instance._t = constr  # maybe use TBI in the future
                instance.update(kwargs)
                # raise PathNotTested()
                return instance
            else:
                # xxx()
                instance = super().__new__(cls)
                instance.data = {}
                instance._t = constr  # maybe use TBI in the future
                return instance
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, tuple):
                if len(arg) == 2:
                    ks, vs = arg
                    instance = super().__new__(cls)
                    instance.data = dict(zip(ks, vs))
                    instance._t = constr
                    return instance
                else:
                    raise NotYetImplemented()
            elif isinstance(arg, (dict, list)):
                # xxx(dict) or xxx(list of key value pairs)
                instance = super().__new__(cls)
                instance.data = dict(arg)
                instance._t = constr
                return instance
            elif isinstance(arg, (_tvmap, _tvstruct)):
                # xxx(_tvmap) or xxx(_tvstruct)
                instance = super().__new__(cls)
                instance.data = dict(arg)
                instance._t = constr
                return instance
            elif isinstance(arg, zip):
                instance = super().__new__(cls)
                instance.data = dict(arg)
                instance._t = constr
                return instance
            elif kwargs:
                if isinstance(arg, BType):
                    # assume arg can be used as a dictionary
                    instance = super().__new__(cls)
                    instance.data = {}
                    instance._t = constr  # maybe use TBI in the future
                    instance.update(arg)
                    return instance
                else:
                    # xxx(t, **kwargs)
                    raise PathNotTested()
                    instance = super().__new__(cls)
                    instance.data = {}
                    instance._t = arg
                    return instance
            elif isinstance(arg, BType):
                # xxx(t, a=1, b=2)
                instance = super().__new__(cls)
                instance.data = {}
                instance._t = arg
                instance.update(kwargs)
                return instance
            else:
                raise NotYetImplemented(f'one arg of type {typeOf(arg)}')
        elif len(args) == 2:
            arg1, arg2 = args
            if not kwargs:
                if isinstance(arg1, BType):
                    # assume arg2 can be used to construct a dictionary
                    instance = super().__new__(cls)
                    instance.data = {}
                    instance._t = arg1
                    instance.update(arg2)
                    raise PathNotTested()
                    return instance
                else:
                    raise PathNotTested()
                    raise SyntaxError("do a better error message")
            else:
                raise NotYetImplemented("getting bored!")
        else:
            # too many args
            raise PathNotTested()
            raise SyntaxError("too many args")


    def __init__(self, *args, **kwargs):
        pass  # we handle construction in __new__

    @property
    def _v(self):
        return self.data

    def _asT(self, t):
        self._t = t
        return self

    def __repr__(self):
        superRepr = super().__repr__()
        rep = f'{self._t}({superRepr})'
        return rep



# remove the >> operators from numpy.ndarray so can use >> piping

class _nd(np.ndarray):
    def __rrshift__(self, arg):
        return NotImplemented
    def __rshift__(self, arg):
        return NotImplemented


# naming - array or tensor?
# see https://en.wikipedia.org/wiki/Tensor
# https://medium.com/@quantumsteinke/whats-the-difference-between-a-matrix-and-a-tensor-4505fbdc576c

# an array is not a tensor - see Dan Fleisch - https://www.youtube.com/watch?v=f5liqUk0ZTw&t=447s
# I understand a tensor to be a n dimensional matrix of coefficients with each coefficient corresponding to m vectors in and

# tensors are combination of components and basis vectors

# a scalar is a tensor of rank 0 - size is 1 x 1 x 1 etc

# a vector is a tensor of rank 1 - size is rank x dimensions,
# e.g for 3 dimensions
# [Ax,           (0,0,1)
#  Ab,           (0,1,0)
#  Ac]           (1,0,0)

# a matrix is a tensor of rank 2 - size is n x n for n dimensions
# e.g. for 2 dimensions
# [Axx, Axy;           (0,1)&(0,1), (0,1)&(1,0)
#  Ayx, Ayy]           (1,0)&(0,1), (1,0)&(1,0)

# a tensor is therefore not a data structure but a data structure with a context

class _tvarray(_nd):

    def __new__(cls, *args_, **kwargs_):
        constrs, args, kwargs = extractConstructors(args_, kwargs_)
        if constrs:
            if len(constrs) != 1: raise NotYetImplemented()
            constr = constrs[0]
            if len(args) == 0:
                # we have a null tuple
                raise NotYetImplemented()
            elif len(args) == 1:
                if t:
                    instance = np.asarray(args[0], **kwargs).view(cls)
                    instance._t_ = t
                else:
                    raise SyntaxError()
            elif len(args) == 2:
                arg1, arg2 = args
                if isinstance(arg1, BType):
                    # darray(t, iterable)
                    try:
                        instance = np.asarray(arg2, **kwargs).view(cls)
                        instance._t_ = arg1
                    except Exception as ex:
                        print(f'{arg1}    {arg2} {ex}')
                        raise ex
                else:
                    raise SyntaxError()
            else:
                raise SyntaxError()
            return instance
        else:
            raise NotYetImplemented()

    def __array_finalize__(self, instance):
        # see - https://numpy.org/doc/stable/user/basics.subclassing.html
        if instance is None: return
        self._t_ = getattr(instance, '_t_', _tvarray)

    @property
    def _v(self):
        return self

    @property
    def _t(self):
        return self._t_

    def _asT(self, t):
        self._t_ = t
        return self

    def __or__(self, arg):  # so doesn't get in the way of arg | type
        return NotImplemented

    def __ror__(self, arg):  # disabled so don't get confusing error messages for type | arg (we want a doesNotUnderstand)
        return NotImplemented

    def __repr__(self):
        if type(self._t) is type:
            typename = self._t.__name__
        else:
            typename = str(self._t)
        return f'{self._t}({np.array2string(self)})'
