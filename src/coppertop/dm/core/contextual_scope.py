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

from coppertop._scopes import _ContextualScopeManager, _MutableContextualScope, _CoWScope, ANON_NAME
from coppertop.pipe import *
from bones.core.errors import NotYetImplemented, CPTBError
from bones.core.sentinels import Missing
from coppertop.dm.core.types import txt


@coppertop
def push(underscore:_ContextualScopeManager):
    # create an anonymous scope and push it - cannot be switched only popped
    child = _MutableContextualScope(underscore, underscore._current)
    underscore._current = child
    return child


@coppertop
def pushCow(underscore:_ContextualScopeManager):
    raise NotYetImplemented()


@coppertop
def pop(underscore:_ContextualScopeManager):
    if underscore._current._name is Missing:
        raise CPTBError("Cannot pop a named context - use switch instead")
    underscore._current = underscore._current._parent
    return underscore._current


@coppertop(style=binary)
def new(underscore:_ContextualScopeManager, name:txt):
    # return a child scope that inherits from the current one without pushing it
    if (current := underscore._namedScopes.get(name, Missing)) is Missing:    # numpy overides pythons truth function in an odd way
        current = underscore._current = _MutableContextualScope(underscore._current._manager, underscore._current, name)
    return current


@coppertop(style=binary)
def newCow(underscore:_ContextualScopeManager, name:txt):
    # return a child cow scope that inherits from the current one without pushing it
    raise NotYetImplemented()


@coppertop(style=binary)
def switch(underscore:_ContextualScopeManager, contextualScopeOrName):
    if underscore._current._name is Missing:
        raise CPTBError("Cannot switch from an anonymous context - use pop instead")
    if isinstance(contextualScopeOrName, _MutableContextualScope):
        underscore._current = contextualScopeOrName
        return contextualScopeOrName
    else:
        underscore._current = underscore._namedScopes[contextualScopeOrName]
        return underscore._current


@coppertop
def root(underscore:_ContextualScopeManager):
    root = underscore._parent
    while root is not (root := root._parent): pass
    return root


@coppertop
def name(underscore:_ContextualScopeManager):
    current = underscore._current
    for k, v in underscore._namedScopes.items():
        if v is current:
            return k
    return ANON_NAME


@coppertop
def names(underscore:_ContextualScopeManager):
    return list(underscore._namedScopes.keys())
