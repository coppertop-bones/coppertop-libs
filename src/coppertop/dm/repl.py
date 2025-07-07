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


__all__ = ['ensurePath', 'printModules', 'unload', 'reload']

from importlib import reload
from bones.core.sentinels import Void


class _callFReturnX:
    def __init__(self, f2, pp, retF=lambda x:x):
        self.f2 = f2
        self.f1 = lambda x:x
        self.pp = pp
        self.retF = retF
    def __rrshift__(self, lhs):   # lhs >> self
        "ENT"
        self.f2(self.f1(lhs))
        self.f1 = lambda x: x
        return lhs
    def __call__(self, f1):
        # so can do something >> PP(repr)
        "ENT"
        self.f1 = f1
        return self
    def __lshift__(self, rhs):    # self << rhs
        "ENT"
        self.f2(self.f1(rhs))
        self.f1 = lambda x: x
        return self
    def __repr__(self):
        return self.pp


def _ensurePath(path):
    import sys
    if path not in sys.path:
        sys.path.insert(0, path)
ensurePath = _callFReturnX(_ensurePath, 'ensurePath', lambda x:Void)

def _printModules(root):
    noneNames = []
    moduleNames = []
    for k, v in sys.modules.items():
        if k.find(root) == 0:
            if v is None:
                noneNames.append(k)
            else:
                moduleNames.append(k)
    noneNames.sort()
    moduleNames.sort()
    print("****************** NONE ******************")
    for name in noneNames:
        print(name)
    print("****************** MODULES ******************")
    for name in moduleNames:
        print(name)
printModules = _callFReturnX(_printModules, 'printModules', lambda x: Void)

def _unload(module_name, leave_relative_imports_optimisation=False):
    # for description of relative imports optimisation in earlier versions of python see:
    # http://www.python.org/dev/peps/pep-0328/#relative-imports-and-indirection-entries-in-sys-modules

    l = len(module_name)
    module_names = list(sys.modules.keys())
    for name in module_names:
        if name[:l] == module_name:
            if leave_relative_imports_optimisation:
                if sys.modules[name] is not None:
                    del sys.modules[name]
            else:
                del sys.modules[name]
unload = _callFReturnX(_unload, 'unload', lambda x: Void)



if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
