# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys

from coppertop.pipe import *
from coppertop.dm.core.types import txt, bool

@coppertop
def unload(module_name:txt):
    l = len(module_name)
    for name in list(sys.modules.keys()):
        if name[:l] == module_name:
            del sys.modules[name]

@coppertop
def unload(module_name:txt, leaveRelativeImportsOptimisation:bool):
    l = len(module_name)
    for name in list(sys.modules.keys()):
        if name[:l] == module_name:
            if leaveRelativeImportsOptimisation:
                if sys.modules[name] is not None:
                    del sys.modules[name]
            else:
                del sys.modules[name]
