# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from bones.ts.metatypes import BTAtom
from bones.lang.types import _tv
from plotnine import ggplot as _ggplot, aes as _aes, geom_point as _geom_point, geom_bar as _geom_bar, labs as _labs
from coppertop.dm.core.types import pydict

P9 = BTAtom('P9').setCoercer(_tv)

# the following seems like a lot of work to do just to get a P9 object to PP it and >> instead of plotnines +


@coppertop
def PP(p: P9) -> P9:
    fig = p._v.draw(show=True)
    return p

@coppertop
def ggplot(x) -> P9:
    return _ggplot(x) | P9

@coppertop
def aes_(lhs:P9, opts:pydict) -> P9:
    return (lhs._v + _aes(**opts)) | P9

@coppertop
def geom_bar_(lhs:P9, opts:pydict) -> P9:
    return (lhs._v + _geom_bar(**opts)) | P9

@coppertop
def geom_point_(lhs:P9, opts:pydict) -> P9:
    return (lhs._v + _geom_point(**opts)) | P9

@coppertop
def labs_(lhs:P9, opts:pydict) -> P9:
    return (lhs._v + _labs(**opts)) | P9

def aes(*args, **kwargs):
    return aes_(_, *args, kwargs)

def geom_bar(*args, **kwargs):
    return geom_bar_(_, *args, kwargs)

def geom_point(*args, **kwargs):
    return geom_point_(_, *args, kwargs)

def labs(*args, **kwargs):
    return labs_(_, *args, kwargs)