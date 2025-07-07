# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import datetime

from coppertop.pipe import *
from coppertop.dm.core import keys_, first, kvs, drop
from coppertop.dm.examples.cluedo.core import *
from coppertop.dm.examples.cluedo.core import one
from coppertop.dm.examples.cluedo.simple import createHelper, figureKnown, processResponses, processSuggestions1, \
    processSuggestions2
from coppertop.dm.examples.cluedo.reports import PP, rep1, rep2

__all__ = ['game1_data', 'game2_data', 'game3_data', 'game4_data', 'game5_data', 'game6_data', 'game7_data']


game1_data = (
        {Sc: [Ha, Co, Sc], Pe: 3, Pl: 3, Gr: 3, Mu: 3, Or: 3},
        [
            [Or, Bi],
            [Or, Mu],
            [Mu, Re],
            [Pl, Ca],
        ],
        [
            [Gr, Pe, Ro, Bi], Mu, Or - one,
            [Mu, Mu, Ro, Li], Or - one,
            [Or, Gr, Ca, Ba], Sc, Pe - one,
            [Sc, Or, Da, Ki], Pe, [Pl, Da],
            [Pe, Mu, Re, Co], Pl, Gr, Mu - one,
            [Pl, Sc, Wr, Ba], Gr, Mu, Or, [Sc, Sc],

            [Gr, Pl, Le, Di], Mu - one,
            [Mu, Pe, Ro, Li], Or, Sc, Pe - one,
            [Or, Pl, Le, Di], Sc, Pe - one,
            [Sc, Pe, Wr, Ba], [Pe, Pe],
            [Pe, Or, Da, Ki], Pl - one,
            [Pl, Pl, Re, Ki], Gr, Mu - one,

            [Gr, Sc, Wr, Ha], Mu, Or, [Sc, Sc],
            [Mu, Gr, Le, St], Or, Sc, Pe - one,
            [Or, Mu, Ca, St], Sc, Pe, Pl - one,
            [Sc, Or, Sc, St], Pe, Pl, [Gr, St],
            [Pe, Or, Ro, Di], Pl - one,
            [Pl, Pl, Wr, St], Gr - one,

            [Gr, Pl, Wr, Ha], Mu, Or, [Sc, Ha],
            [Mu, Pl, Re, Li], Or, Sc, Pe, Pl, Gr,
        ]
    )


game2_data = (
        {Pl: [Gr, Ro, Lo], Gr: 3, Mu: 3, Or: 3, Sc: 3, Pe: 3},
        [
            [Sc, Pl],
            [Pe, Ha],
            [Sc, Sc],
            [Or, Mu],
        ],
        [
            [Pl, Mu, Da, Di], Gr, [Mu, Di],
            [Gr, Gr, Da, Li], Mu, Or, Sc, Pe, [Pl, Gr],
            [Mu, Pl, Da, Lo], Or, Sc - one,
            [Or, Sc, Da, Ha], Sc - one,
            [Sc, Or, Da, Ha], Pe - one,
            [Pe, Or, Ca, Ba], Pl, Gr - one,

            [Pl, Or, Ca, Lo], [Gr, Or],
            [Gr, Pe, Ca, Bi], Mu, Or, Sc, Pe - one,
            [Mu, Sc, Da, Ha], Or, Sc - one,
            [Or, Pl, Da, Ha], Sc - one,
            [Sc, Or, Da, Di], Pe, Pl, Gr - one,
            [Pe, Mu, Da, Bi], Pl, Gr, Mu, Or - one,

            [Pl, Gr, Ro, Li], [Gr, Li],  # We won?
        ]
    )


game3_data = (
        {Pl: [St, Li, Di, Wr, Sc], Gr: 5, Or: 4, Pe: 4},
        [
            [Or, Ro],
        ],
        [
            [Gr, Mu, Da, Bi], Or - one,
            [Or, Gr, Re, Ba], Pe - one,
            [Pe, Gr, Wr, Ki], [Pl, Wr],
            [Pl, Gr, Da, Ba], [Gr, Gr],

            [Gr, Pe, Le, Bi], Or, Pe - one,
            # Or misses a go
            [Pe, Sc, Da, Li], [Pl, Sc],
            [Pl, Pe, Le, Bi], Gr, Or, [Pe, Pe],

            [Gr, Gr, Ro, Li], Or - one,
            [Or, Pl, Wr, Di], Pe, [Pl, Wr],
            [Pe, Pl, Le, Bi], Pl, Gr, Or,
        ]
    )


game4_data = (
        {Pl: [Lo, Wr, Pe, Mu, Gr], Gr: 5, Or: 4, Pe: 4},
        [
            [Or, Ro],
        ],
        [
            [Gr, Pl, Da, Di], Or, Pe - one,
            [Or, Mu, Le, Bi], Pe - one,
            [Pe, Mu, Wr, Ba], [Pl, Mu],
            [Pl, Sc, Da, Di], Gr, [Or, Sc],

            [Gr, Pe, Le, Ba], Or, Pe - one,
            [Or, Gr, Ro, Li], Pe, [Pl, Gr],
            [Pe, Gr, Da, Ki], [Pl, Gr],
            [Pl, Pl, Da, Di], Gr, Or, [Pe, Pl],

            [Gr, Or, Re, St], Or - one,
            [Or, Mu, Wr, St], Pe, [Pl, Mu],
            [Pe, Or, Da, Di], Pl, Gr, Or,
        ]
    )


game5_data = (
        {Pl: [Ki, Di, Le, Da, Ca], Gr: 5, Or: 4, Pe: 4},
        [
            [Or, Ro],
        ],
        [
            [Pl, Gr, Re, Ba], [Gr, Ba],
            [Gr, Mu, Re, Ki], Or - one,
            [Or, Or, Ro, Lo], Pe - one,
            [Pe, Gr, Da, Co], [Pl, Da],

            [Pl, Or, Wr, Co], Gr, Or, [Pe, Or],
            [Gr, Sc, Ca, Ki], Or, Pe, [Pl, Ca],
            [Or, Pe, Ro, Ba], Pe, Pl, Gr - one,
            [Pe, Mu, Re, Co], Pl, Gr, Or - one,

            [Pl, Sc, Wr, Bi], [Gr, Bi],  # Sc, Wr, Co
            [Gr, Sc, Le, Ba], Or, Pe, [Pl, Le],
            [Or, Pe, Re, Co], Pe, Pl, Gr,  # Or won
        ]
    )


game6_data = (
        {Pl: [Ba, Pl, Pe, Mu], Gr: 4, Mu: 4, Or: 3, Pe: 3},
        [
            [Or, Wr],
            [Mu, Ha],
            [Or, Sc],
        ],
        [
            [Pe, Sc, Ro, Ki], Pl, Gr - one,
            [Pl, Mu, Re, St], Gr, [Mu, Re],
            [Gr, Gr, Ca, Ba], Mu, Or, Pe, [Pl, Ba],
            [Mu, Pe, Wr, Li], Or - one,
            [Or, Or, Da, Di], Pl, Gr - one,

            [Pe, Pe, Le, Bi], [Pl, Pe],
            [Pl, Gr, Ca, Li], Gr, Mu, Or, [Pe, Li],
            [Gr, Sc, Ca, Bi], Mu, Or - one,
            [Mu, Sc, Ca, Bi], Or - one,
            [Or, Gr, Ca, Ha], Pl, Gr, Mu - one,

            [Pe, Gr, Ca, Li], Pl, Gr, Or,
            [Pl, Pe, Ca, St], Gr, Mu, Or, [Pe, St],
            [Gr, Gr, Ro, Bi], Mu, Or, Pe, Pl,  # Gr won
        ]
    )


game7_data = (
        {Pl: [St, Di, Co, Ca], Gr: 4, Mu: 4, Or: 3, Pe: 3},
        [
            [Pe, Ha],
            [Pe, Or],
            [Mu, Wr],
        ],
        [
            [Pl, Gr, Da, Ha], [Gr, Gr],
            [Gr, Mu, Wr, Ha], Mu - one,
            [Mu, Sc, Ro, Lo], Or, Pe, Pl, Gr - one,
            [Or, Pl, Re, Li], Pe - one,
            [Pe, Gr, Ca, St], [Pl, Ca],

            [Pl, Sc, Ro, Li], [Gr, Ro],
            [Gr, Or, Da, St], Mu, Or, Pe - one,
            [Mu, Sc, Ca, Ha], Or, Pe - one,
            [Or, Gr, Wr, Li], Pe, Pl, Gr - one,

            [Pe, Pe, Re, Ki], Pl, Gr - one,
            [Pl, Sc, Wr, Bi], [Gr, Sc],
            [Gr, Mu, Le, Li], Mu - one,
            [Mu, Sc, Da, Bi], Or, Pe, Pl, Gr - one,
            [Or, Mu, Da, Bi], Pe, Pl, Gr, Mu,  # Or won
        ]
    )


game8_data = (
    {Pl: [Ki, Ha, Co, Da, Pe], Gr: 5, Or: 4, Pe: 4},
    [
    ],
    [
        [Pe, Pl, Ro, Ki], [Pl, Ki],
        [Pl, Pl, Ro, Ba], [Gr, Pl],
        [Gr, Pe, Re, Li], Or, Pe - one,
        # Or low roll

        [Pe, Or, Ro, Co], [Pl, Co],
        [Pl, Or, Ro, Bi], [Gr, Or],
        # Gr low roll
        [Or, Pe, Le, Ba], Pe, [Pl, Pe],

        # [Pe, Mu, Le, Ba], Pl, Gr, Or,
    ]
)


game9_data = (
    # 3 Dec 2022
    {Pl: [St, Ba, Wr, Da, Sc], Gr: 5, Or: 4, Pe: 4},
    [
    ],
    [
        [Gr, Gr, Re, Ki], Or, Pe, Pl,
        [Or, Gr, Re, Ba], Pe, [Pl, Ba],
        [Pe, Gr, Re, Di], Pl, Gr, Or,
        [Pl, Sc, Da, Li], Gr, [Or, Li],

        [Gr, Pe, Re, Lo], Or, Pe, Pl,
        [Or, Gr, Re, Li], Pe, Pl, Gr,
        [Pe, Or, Re, Lo], Pl, Gr, Or,
        [Pl, Sc, Wr, Ha], Gr, Or, [Pe, Ha],
    ]
)


game10_data = (
    {Pl: [Da, Ca, Sc, Pe], Gr: 4, Mu: 4, Or: 3, Pe: 3},
    [
        [Pe, Ha],
        [Pe, Or],
        [Mu, Wr],
    ],
    [  # 0,
        [Pe, Mu, Le, Ki], Pl, Gr, Mu, Or - one, 1,      # Le% or Ki
        [Pl, Pe, Da, Ki], Gr, Mu, [Or, Ki],
        [Gr, Sc, Ca, Ba], Mu, Or, Pe, [Pl, Ca], 3,
        [Mu, Or, Ro, Di], Or - one, 4,                  # Or%, Ro%
        [Or, Mu, Le, Di], Pe, Pl, Gr, Mu - one, 5,      # Di

        [Pe, Sc, Ca, St], [Pl, Ca], 6,
        [Pl, Mu, Le, Ba], [Gr, Ba], 7,
        [Gr, Mu, Le, Ki], [Or, Ki], 8,                  # Le%, Ki
        [Mu, Mu, Re, St], Or, Pe - one, 9,
        [Or, Mu, Ro, Ha], Pe - one, 10,                 # Ha

        [Pe, Mu, Le, Li], Gr - one, 11,                 # Li
        [Pl, Sc, Da, Co], Gr, [Mu, Co], 12,
        [Gr, Or, Le, Bi], Mu, Or - one, 13,             # Or%, Le%, Bi%
        [Mu, Pl, Le, Bi], Or - one, 14,                 # Le%, Bi%
        [Or, Mu, Ro, Bi], Pe, Pl, Gr, Mu, 15,

        [Pe, Mu, Re, St], Pl, Gr, Mu, Or, 16,
        [Pl, Sc, Le, Bi], Gr, Mu, [Or, Bi], 17,
    ]

)


game11_data = (
    {Pl: [Or, Ca, Ha, Ki, St], Gr: 5, Or: 4, Pe: 4},
    [
    ],
    [
        [Pl, Gr, Da, Ba], [Gr, Da],
        [Gr, Pe, Le, Ki], Or, Pe - one,
        [Or, Sc, Ca, Ki], Pe, [Pl, Ca],
        [Pe, Or, Re, St], [Pl, Or],

        [Pl, Sc, Le, Co], Gr, Or, [Pe, Le],
        [Gr, Sc, Da, Ba], Or - one,
        [Or, Sc, Ro, Li], Pe - one,
        [Pe, Sc, Re, Li], Pl, Gr - one,

        [Pl, Sc, Wr, Ki], Gr, Or, Pe,
        [Gr, Sc, Wr, Ki], Or, Pe, [Pl, Ki],
        [Or, Sc, Wr, St], Pe, [Pl, Ki],
        [Pe, Pe, Wr, Ha], [Pl, Ha],

        [Pl, Or, Ca, Di], Gr, [Or, Di],
        [Gr, Sc, Wr, Lo], Or, Pe, Pl,  # Gr won - I gave away Scarlet and Wrench?
    ]
)


game12_data = (
    {Pl: [Wr, Le, Ca, Sc, Or], Gr: 5, Or: 4, Pe: 4},
    [
    ],
    [
        [Gr, Or, Ro, Ba], Or - one,
        [Or, Or, Le, Di], Pe, [Pl, Le],
        [Pe, Gr, Ro, Bi], Pl, Gr - one,
        [Pl, Gr, Ro, Ba], Gr, [Or, Ro],
        [Or, Ro],
        [Gr, Bi],

        [Gr, Pl, Wr, Co], Or, Pe, [Pl, Wr],
        [Or, Gr, Re, Ha], Pe, Pl, Gr - one,
        [Pe, Pl, Wr, Co], [Pl, Wr],
        [Pl, Pl, Pl, Co], [Gr, Pl],

        [Gr, Gr, Re, Di], Or-one,
        [Or, Gr, Re, Li], Pe, Pl, Gr-one,
        [Pe, Pl, Ro, Lo], Pl, Gr-one,
        [Gr, Ha],
        [Or, Di],
        [Gr, Li],
        [Pl, Gr, Re, Co], Gr, Or, Pe

    ]
)



games = {
    1: game1_data,
    2: game2_data,
    3: game3_data,
    4: game4_data,
    5: game5_data,
    6: game6_data,
    7: game7_data,
    8: game8_data,
    9: game9_data,
    10: game10_data,
    11: game11_data,
    12: game12_data,
}


# gameXX_data = (
#     {Pl: [XX, XX], Gr: 5, Or: 4, Pe: 4},
#     [
#     ],
#     [
#     ]
# )


def play(data):
    deal, preevents, events = data
    Pl, hand = deal >> kvs >> first
    otherHandSizesById = deal >> drop >> Pl

    like = {0: 100, 1: 10, 2: 5, 3: 0}

    helper = createHelper(Pl, hand, otherHandSizesById)
    helper = helper >> figureKnown >> preevents + events
    helper = helper >> processResponses >> events
    # helper = helper >> processSuggestions1(_, _, like) >> events
    helper = helper >> processSuggestions2(_, _, like) >> events
    helper >> rep2 >> PP



def main():
    t1 = datetime.datetime.now()
    play(game4_data)
    t2 = datetime.datetime.now()
    f'\n{(t2 - t1).microseconds / 1000}ms' >> PP

    # import coppertop._singletons
    # f'{int(coppertop._singletons._numNotCopied / (coppertop._singletons._numNotCopied + coppertop._singletons._numCopies)*100)}%' >> PP

    # totalCombs =
    #     num(people) - num(my people) - num(TBI people)
    #     * num(weapons) - num(my weapons) - num(TBI weapons)
    #     * num(rooms) - num(my rooms) - num(TBI rooms)
    #     * perms (remaining cards, num other players)

if __name__ == '__main__':
    main()
