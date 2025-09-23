# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *

import logging as _logging, io

from coppertop.dm.core.types import txt
from bones.ts.metatypes import BTUnion
from types import FunctionType

DEBUG = _logging.DEBUG
INFO = _logging.INFO

tHandlers = BTUnion(_logging.StreamHandler, _logging.FileHandler)

@coppertop
def _debug(logger:_logging.Logger, msg:txt) -> txt:
    logger._debug(msg)
    return msg

@coppertop
def _info(logger:_logging.Logger, msg:txt) -> txt:
    logger._info(msg)
    return msg

@coppertop
def getLogger(name:txt) -> _logging.Logger:
    logger = _logging.getLogger(name)
    if not hasattr(logger, '_debug'):
        logger._debug = logger.debug
        logger.debug = _debug(logger, _)
    if not hasattr(logger, '_info'):
        logger._info = logger.info
        logger.info = _info(logger, _)
    if not hasattr(logger, 'setFfn'): logger.setFfn = setFfn(logger, _)
    if not hasattr(logger, '_setLevel'):
        logger._setLevel = logger.setLevel
        logger.setLevel = setLevel(logger, _)
    logger.setLevel(_logging.INFO)
    return logger

@coppertop
def getLogger(handler:tHandlers) -> _logging.Logger:
    return handler._logger

@coppertop(style=binary)
def setDtFmt(handler:tHandlers, datefmt:txt) -> tHandlers:
    current = handler.formatter
    if current is None:
        formatter = _logging.Formatter(datefmt=datefmt)
    else:
        fmt = current._fmt
        formatter = _logging.Formatter(fmt=fmt, datefmt=datefmt)
    handler.setFormatter(formatter)
    return handler

@coppertop(style=binary)
def setFfn(logger:_logging.Logger, ffn:txt) -> _logging.Handler:
    handler = _logging.FileHandler(ffn)
    handler.setFmt = setFmt(handler, _)
    handler.setDtFmt = setDtFmt(handler, _)
    logger.addHandler(handler)
    handler._logger = logger
    return handler

@coppertop(style=binary)
def setFfn(logger:_logging.Logger, ffn) -> _logging.Handler:
    # ipykernel.iostream.OutStream, io.TextIOWrapper
    handler = _logging.StreamHandler(ffn)
    handler.setFmt = setFmt(handler, _)
    handler.setDtFmt = setDtFmt(handler, _)
    logger.addHandler(handler)
    handler._logger = logger
    return handler

@coppertop(style=binary)
def setFmt(handler:tHandlers, fmt:txt) -> tHandlers:
    current = handler.formatter
    if current is None:
        formatter = _logging.Formatter(fmt=fmt)
    else:
        datefmt = current.datefmt
        formatter = _logging.Formatter(fmt=fmt, datefmt=datefmt)
    handler.setFormatter(formatter)
    return handler

@coppertop(style=binary)
def setLevel(logger:_logging.Logger, level) -> _logging.Logger:
    logger._setLevel(level)
    return logger
