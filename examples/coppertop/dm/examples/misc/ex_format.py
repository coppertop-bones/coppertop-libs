# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#                               Contact the copyright holder for licensing terms.
#
# **********************************************************************************************************************

from coppertop.pipe import _
from coppertop.dm.wip import stdout
from coppertop.dm.core import format



stdout \
    << (2 >> format(_, '{a:.{0}%}', dict(a=2))) << '\n' \
    << ((10, 2, 123.456) >> format(_, '{2:{0}.{1}f} - {a:.1%}', dict(a=2))) << '\n' \
    << (dict(a=2) >> format(_, '{a:.1%}')) << '\n'

