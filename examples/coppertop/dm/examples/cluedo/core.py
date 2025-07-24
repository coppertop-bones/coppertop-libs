# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from enum import IntEnum

from coppertop.core import Missing
from bones.ts.metatypes import BType
import coppertop.dm.core.types
from coppertop.dm.examples.cluedo.cards import *


__all__ = [
    'TBI',
    'Gr', 'Mu', 'Or', 'Pe', 'Pl', 'Sc',
    'Ca', 'Da', 'Le', 'Re', 'Ro', 'Wr',
    'Ki', 'Ba', 'Co', 'Bi', 'Li', 'St', 'Ha', 'Lo', 'Di',
    'people', 'weapons', 'rooms',
    'Card',
    'one',
]


NS_TO_S = 1 / 1_000_000_000


card = BType('card: atom')
handId = BType('handId: atom')
possibleHand = BType('possibleHand: possibleHand & (N ** card)')
event = BType('event: atom')
turnId = BType('turnId: atom')

suggestion = BType('''suggestion: suggestion & 
    {
        player: handId,
        who: card,
        weapon: card,
        room: card
    } & event in mem
''')

noneOf = BType('''noneOf: noneOf & 
    {
        player: handId,
        who: card,
        weapon: card,
        room: card
    } & event in mem
''')

oneOf = BType('''oneOf: oneOf & 
    {
        player: handId,
        who: card,
        weapon: card,
        room: card
    } & event in mem
''')

showsOne = BType('''showsOne: showsOne & 
    {
        player: handId,
        what: card
    } & event in mem
''')

ndmap = BType('ndmap: atom')

handTracker = BType('''
    handTracker: 
        {
            ys: N ** card,
            ns: N ** card,
            ms: N ** card,
            combs: N ** possibleHand,
            suggestions: N ** (N ** card),
            prior: (N ** txt) ** num,
            posterior: (N ** txt) ** num
        } & dstruct in mem
''')

cell = BType('''
    cell: 
        {
            state: txt,                 // 'X', '-', '?' for yes, no, maybe
            suggestions: N**turnId,
            haveOnes: N**turnId,
            prior: num,
            posterior: num
        } & dstruct in mem
''')

cluedo_pad = BType('cluedo_pad: cluedo_pad & (card ** (handId ** cell)) & dmap in mem')

cluedo_helper = BType('''
    cluedo_helper: 
        {
            handid: handId, 
            hand: N ** card,
            sizeByHandId: handId ** count,
            pad: cluedo_pad,                            // a grid of cells
            trackerByHandId: handId ** handTracker,     // a tracker for each handId
            otherHandIds: N ** handId,
            turnId: turnId
        }  & dstruct in mem
''')

display_table = BType('display_table: display_table & (N ** txt) & dseq in mem')      # a seq of txt


YES = 'X'
NO = '-'
MAYBE = '?'


class HasOne:
    def __init__(self, handId=Missing):
        self.handId = handId

    def __rsub__(self, handId):  # handId / has
        assert self.handId == Missing, 'Already noted a handId'
        return HasOne(handId)

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.handId == self.handId

one = HasOne()


