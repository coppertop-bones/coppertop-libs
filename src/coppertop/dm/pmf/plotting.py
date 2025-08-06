# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************


import pandas as pd, numpy as np, plotnine

from coppertop.pipe import *

from coppertop.dm.core.types import pylist, pydict, pytuple, pandaframe
from coppertop.dm.core.aggman import withKeys, zipAll, keys, values
from coppertop.dm.pmf.core import PMF, CMF, values, keys
from coppertop.dm.pandaframe import to


# **********************************************************************************************************************
# plotting functions
# **********************************************************************************************************************

@coppertop
def toSteps(s:PMF) -> pytuple:
    return _asSteps(s >> keys, s >> values)

@coppertop
def toSteps(s:PMF, kwargs) -> pytuple:
    return _asSteps(s >> keys, s >> values, **kwargs)

def _asSteps(xs:pylist, ys:pylist, align='center', width=None):
    #xMin, xMax = min(xs), max(xs)
    if width is None:
        width = np.diff(list(xs)).min()
    points = []
    lastx = np.nan
    lasty = np.nan
    for x, y in [xs, ys] >> zipAll:
        if (x - lastx) > 1e-5:
            points.append((lastx, 0))
            points.append((x, 0))
        if not np.isnan(lasty):
            points.append((x, lasty))
        points.append((x, y))
        points.append((x + width, y))
        lastx = x + width
        lasty = y
    points.append((lastx, lasty))
    pxs, pys = points >> zipAll
    if align == 'center':
        pxs = np.array(pxs) - width / 2.0
    elif align == 'right':
        pxs = np.array(pxs) - width
    return pxs, np.array(pys)

@coppertop
def geom_prob(mf:PMF + CMF, kwargs:pydict):
    return plotnine.geom_line(mf >> toSteps >> withKeys >> ('x', 'y') >> to >> pandaframe, plotnine.aes(x="x", y="y"), **kwargs)
