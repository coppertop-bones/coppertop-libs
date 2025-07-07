# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from enum import IntEnum

__all__ = [
    'TBI',
    'Gr', 'Mu', 'Or', 'Pe', 'Pl', 'Sc',
    'Ca', 'Da', 'Le', 'Re', 'Ro', 'Wr',
    'Ki', 'Ba', 'Co', 'Bi', 'Li', 'St', 'Ha', 'Lo', 'Di',
    'people', 'weapons', 'rooms',
    'Card',
]

ppLongNames = [
    'TBI',
    'Green', 'Mustard', 'Orchid', 'Peacock', 'Plum', 'Scarlet',
    'Candlestick', 'Dagger', 'Lead Pipe', 'Revolver', 'Rope', 'Wrench',
    'Ballroom', 'Billiard Room', 'Conservatory', 'Dining Room', 'Hall', 'Kitchen', 'Library', 'Lounge', 'Study'
]

ppShortNames = [
    'TBI',
    'Gr', 'Mu', 'Or', 'Pe', 'Pl', 'Sc',
    'Ca', 'Da', 'Le', 'Re', 'Ro', 'Wr',
    'Ba', 'Bi', 'Co', 'Di', 'Ha', 'Ki', 'Li', 'Lo', 'St'
]

class Card(IntEnum):
    TBI = 0

    Gr = 1
    Mu = 2
    Or = 3
    Pe = 4
    Pl = 5
    Sc = 6

    Ca = 7
    Da = 8
    Le = 9
    Re = 10
    Ro = 11
    Wr = 12

    Ba = 13
    Bi = 14
    Co = 15
    Di = 16
    Ha = 17
    Ki = 18
    Li = 19
    Lo = 20
    St = 21

    def __str__(self):
        return ppLongNames[self]

    def __repr__(self):
        return ppShortNames[self]


TBI = Card.TBI

Gr = Card.Gr
Mu = Card.Mu
Or = Card.Or
Pe = Card.Pe
Pl = Card.Pl
Sc = Card.Sc

Ca = Card.Ca
Da = Card.Da
Le = Card.Le
Re = Card.Re
Ro = Card.Ro
Wr = Card.Wr

Ba = Card.Ba
Bi = Card.Bi
Co = Card.Co
Di = Card.Di
Ha = Card.Ha
Ki = Card.Ki
Li = Card.Li
Lo = Card.Lo
St = Card.St

people = [Gr, Mu, Or, Pe, Pl, Sc]
weapons = [Ca, Da, Le, Re, Ro, Wr]
rooms = [Ba, Bi, Co, Di, Ha, Ki, Li, Lo, St]