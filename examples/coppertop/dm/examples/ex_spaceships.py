# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from bones.ts.metatypes import BType
from bones.core.sentinels import Null

from coppertop.dm.core.types import txt, null
from coppertop.dm.testing import check, equals
from coppertop.dm.pp import PP


# Inspired by the wikipedia article on multi-dispatch - https://en.wikipedia.org/wiki/Multiple_dispatch
# Hopefully this is even more readable than Julia

asteroid = BType('asteroid: asteroid & txt in mem')
ship = BType('ship: ship & txt in mem')
event = BType('event: event & txt in mem')


@coppertop
def collide(a:asteroid, b:asteroid) -> event:
    return f'{a} split {b} (collide<:asteroid,asteroid:>)' | event

@coppertop
def collide(a:ship, b:asteroid) -> event:
    return f'{a} tried to ram {b} (collide<:ship,asteroid:>)' | event

@coppertop
def collide(a:asteroid, b:ship) -> event:
    return f'{a} destroyed {b} (collide<:asteroid,ship:>)' | event

@coppertop
def collide(a:ship, b:ship) -> null:
    return Null
#    return f'{a} bounced {b} (collide<:ship,ship:>)' >> to >> event

@coppertop
def process(e:event) -> txt:
    return e

@coppertop
def process(e:null) -> txt:
    return 'nothing happened'

# @coppertop
# def process(e:event+null) -> txt:
#     return 'nothing happened' if typeOf(e) == null else e


borg = BType('borg: borg & ship in mem')

@coppertop
def collide(a:borg, b:ship) -> event:
    return f'{a} subsumes {b} (collide<:borg,ship:>)' | event

@coppertop
def collide(a:borg, b:borg) -> event:
    return f'{a} merges with {b} (collide<:borg,borg:>)' | event



def testCollide():
    ship1 = 'ship1' | ship
    ship2 = 'ship2' | ship
    ast1 = 'big asteroid' | asteroid
    ast2 = 'small asteroid' | asteroid
    b = 'borg' | borg
    b2 = 'the borg' | borg

    ship1 >> collide(_, ship2) >> process >> PP
    ship1 >> collide(_, ast1) >> process >> PP
    ship2 >> collide(ast2, _) >> process >> PP
    ast1 >> collide(_, ast2) >> process >> PP
    b >> collide(_, ship2) >> process >> PP
    b >> collide(_, ast1) >> process >> PP
    b >> collide(ast2, _) >> process >> PP
    ship1 >> collide(_, b) >> process >> PP
    b >> collide(_, b2) >> process >> PP

    ship1 >> collide(_, ship2) >> process >> check >> equals >> 'nothing happened'
    # 'ship1 tried to ram big asteroid (collide<:ship,asteroid:>)'
    # 'small asteroid destroyed ship2 (collide<:asteroid,ship:>)'
    # 'big asteroid split small asteroid (collide<:asteroid,asteroid:>)'


def main():
    testCollide()


if __name__ == '__main__':
    testCollide()
    print('pass')
