# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys         
# sys._TRACE_IMPORTS = True
if getattr(sys, '_TRACE_IMPORTS', False): print(__name__)


from coppertop.pipe import *
from bones.ts.metatypes import BTStruct, BType
from coppertop.dm.core.types import T1, T2, tvfloat, pyfunc
from coppertop.dm.finance.types import ccy, fx
from coppertop.dm.testing import check, raises, equals


# <:fx:fx_&{{domestic:_ccy&T1,_ccy&T2}}>
#
# <:GBP:_ccy&"GBP">
# <:USD:_ccy&"USD">
#
# <:GBPUSD:fx(GBP,USD)>
#
# <:ccy:_ccy&num>
#
# <:rat:()

GBP = BType('GBP: GBP & ccy & tvfloat').setCoercer(tvfloat)
USD = BType('USD: USD & ccy & tvfloat').setCoercer(tvfloat)
tvccy = ccy & tvfloat

GBPUSD = fx[BTStruct(domestic=GBP, foreign=USD)].nameAs('GBPUSD')[tvfloat].setCoercer(tvfloat)
fxT1T2 = fx[BTStruct(domestic=tvccy[T1], foreign=tvccy[T2])] & tvfloat


@coppertop(style=binary)
def addccy(a:tvccy[T1], b:tvccy[T1]) -> tvccy[T1]:
    return (a + b) | a._t

@coppertop(style=binary)
def addccy_(a, b) -> pyfunc:
    return lambda : (addccy(a, b))

@coppertop(style=binary)
def mul(dom:tvccy[T1], fx:fxT1T2, tByT) -> tvccy[T2]:
    assert dom._t == tvccy[tByT[T1]]
    return (dom * fx) | tvccy[tByT[T2]]

@coppertop(style=binary)
def mul(dom:tvccy[T2], fx:fxT1T2, tByT) -> tvccy[T1]:
    assert dom._t == tvccy[tByT[T2]]
    return (dom / fx) | tvccy[tByT[T1]]


def testFx():
    fits1, tByT1, distance1 = fitsWithin(GBP, tvccy[T1])
    fits2, tByT2, distance2 = fitsWithin(GBPUSD, fxT1T2)

    (100|GBP) >> mul >> (1.3|GBPUSD) >> addccy >> (20|USD) >> check >> equals >> (150|USD)
    (130|USD) >> mul >> (1.3|GBPUSD) >> check >> equals >> (100|GBP)

    (100|GBP) >> addccy_ >> (100|USD) >> check >> raises >> TypeError

    assert (100|GBP) >> addccy >> (100|GBP) == (200|GBP)




def main():
    testFx()


if __name__ == '__main__':
    main()
    print('pass')
