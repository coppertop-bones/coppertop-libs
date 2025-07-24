# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.core import ProgrammerError, UnhappyWomble, Missing, Void

from coppertop.dm.core.types import void, pylist, pydict, dstruct
import coppertop.dm.pmf
from coppertop.dm.pp import PP
from coppertop.dm.core import collect, keys, join, drop, do, select, count, without, combinations, atPut, to, \
    joinAll, asideDo, soleElement, minus, countIf, intersects

from coppertop.dm.examples.cluedo.core import people, weapons, rooms, Card, TBI, cluedo_helper, YES, NO, MAYBE, HasOne, \
    cluedo_pad, cell
from coppertop.dm.examples.cluedo.utils import zipBoth, to



# we track all possible card locations (state is YES, NO or MAYBE) for the following:
#  - the hand of the player (whose pad this is),
#  - the hand to be inferred TBI,
#  - the hand of each opponent
# we track suggestions and responses as lists in each hand (i.e. without aggregating them)


# the probability of a card being in the TBI or a player's hand is 1 - bayes update? not really however there is an
# increase probability of a card being in the hand of a player who has to show a card in response to a suggestion




@coppertop(style=binary)
def figureKnown(helper:cluedo_helper, events) -> cluedo_helper:
    # extract everything known from events


    _.pad = helper.pad
    helper.pad = Missing   # pass ownership of pad to _
    handId = helper.handId
    _.handIds = helper.sizeByHandId >> keys

    _.iSuggest = 0
    turnId = Missing
    off = ord('a') - 1

    hId, pe, we, ro = Missing, Missing, Missing, Missing

    for ev in helper.hand >> collect >> (lambda c: [handId, c]) >> join >> events:

        if isinstance(ev, list) and len(ev) == 4:
            hId, pe, we, ro = ev            # the current suggestion state
            _.iSuggest += 1;  turnId = chr(_.iSuggest + off)
            _.pad[pe][hId].suggestions.append(turnId)
            _.pad[we][hId].suggestions.append(turnId)
            _.pad[ro][hId].suggestions.append(turnId)

        elif ev >> typeOf == HasOne:
            _.pad[pe][ev.handId].haveOnes.append(turnId)
            _.pad[we][ev.handId].haveOnes.append(turnId)
            _.pad[ro][ev.handId].haveOnes.append(turnId)

        # if a card location is known to be YES in one handId it must be NO in all other handIds
        elif isinstance(ev, list) and len(ev) == 2:
            hId, c = ev
            ensureDefinitely(c, hId, YES)
            _.handIds >> drop >> hId >> do >> ensureDefinitely(c, _, NO)        # mark other hands as definite NOs
            if pe and we and ro:
                # record the response to a suggestion
                _.pad[pe][hId].haveOnes.append(turnId)
                _.pad[we][hId].haveOnes.append(turnId)
                _.pad[ro][hId].haveOnes.append(turnId)

        elif isinstance(ev, int) and type(ev) is not Card:
            # a tag to create a pad - ignore for now
            continue

        # the player indicated they don't have a match with the suggestion - thus we know three NOs
        else:
            hId = ev
            (pe, we, ro) >> do >> ensureDefinitely(_, hId, NO)

    helper.turnId = turnId
    del _.iSuggest

    hId, pe, we, ro = Missing, Missing, Missing, Missing


    # run the inference rules

    _.changed = True
    while _.changed:
        _.changed = False

        # check each handId to see if the YES count equals the hand size - if so mark any MAYBEs as NO
        # should we do the reverse rule?
        _.allYesCardsNotInTBI = []
        for hId in _.handIds:
            # two outputs - the count (which we use to determine if a hand is fully known) and which hand a known card is in
            yesCount = 0
            for c in _.pad >> keys:
                if _.pad[c][hId].state == YES:
                    yesCount += 1
                    if hId != TBI:
                        _.allYesCardsNotInTBI.append(c)
            if yesCount == helper.sizeByHandId[hId]:
                _.pad >> keys >> do >> ensureDefinitely(_, hId, NO)
            elif yesCount > helper.sizeByHandId[hId]:
                raise UnhappyWomble()

        # for each card check if all hands but one have NO - in which case the remaining one must be a YES
        for c in _.pad >> keys:
            noHands = _.handIds >> select >> (lambda hId: _.pad[c][hId].state == NO)
            remaining = set(_.handIds) >> minus >> noHands
            if remaining >> count == 1:
                remaining >> soleElement >> ensureDefinitely(c, _, YES)

        # for each group in the TBI hand, check:
        #   - for a single YES - if found, others must be NO
        #   - if all but one are NO - if so, the remaining one is a YES
        (people, weapons, rooms) >> do >> checkAndUpdateTbiHand

        # for each group if we know the location of all but one card (inspectable from hIdByYesCard) then we can
        # infer that the remaining card must be in TBI hand
        x = (people, weapons, rooms) >> collect >> (lambda group: set(group) >> minus >> _.allYesCardsNotInTBI)
        x = x  \
            >> select >> (lambda remaining: remaining >> count == 1)  \
            >> collect >> soleElement  \
            >> asideDo >> (lambda cInferredInTBI:
                cInferredInTBI >> collect >> ensureDefinitely(_, TBI, YES)
            )  \
            >> asideDo >> (lambda cInferredInTBI:
                cInferredInTBI >> collect >> (lambda c:
                    _.handIds >> collect >> ensureDefinitely(c, _, NO)
               )
            )

        del _.allYesCardsNotInTBI

    helper.pad = _.pad
    del _.pad
    del _.handIds
    del _.changed
    return helper


@coppertop
def checkAndUpdateTbiHand(group) -> void:
    # check the given group in the TBI hand for definite YES and definite NO
    yesCards = group >> select >> (lambda c: _.pad[c][TBI].state == YES)        # could merge these so loops only once
    noCount = group >> countIf >> (lambda c: _.pad[c][TBI].state == NO)
    if yesCards:
        if yesCards >> count > 1: raise UnhappyWomble()
        group >> without >> yesCards >> do >> ensureDefinitely(_, TBI, NO)
    elif noCount == count(group) - 1:
        group >> do >> ensureDefinitely(_, TBI, YES)
    return Void


# for a function to match it must ensure ignore ctx inputs and outputs are met too
# it's not going to be super trivial to add however the improvement in readabilty will be worth it?
@coppertop #(ctx=S(pad)) or could make a kwarg? ctx:S(pad=cluedo_pad)
def ensureDefinitely(c, hId, knownState) -> void: # * ctx(changed=bool, pad=cluedo_pad):
    if _.pad[c][hId].state == MAYBE:
        _.pad[c][hId].state = knownState        # <--- immutable update in the style of deep mutable update :)
        _.changed = True
    return Void




@coppertop(style=binary)
def processResponses(helper:cluedo_helper, events:pylist) -> cluedo_helper:
    # we can figure a prior from the responses where a player shows another player a held card
    _.pad = helper.pad
    _.trackerByHandId = helper.trackerByHandId
    helper.pad = Missing
    helper.trackerByHandId = Missing

    for hId in helper.otherHandIds:
        ys, ns, ms = _.pad >> yesNoMaybesFor(_, hId)
        # (ys, ns, ms) >> collect >> count >> PP
        numUnknowns = helper.sizeByHandId[hId] - (ys >> count) #>> PP
        _.trackerByHandId[hId].combs = ms >> combinations >> numUnknowns
        _.trackerByHandId[hId].ys = ys
        _.trackerByHandId[hId].ns = ns
        _.trackerByHandId[hId].ms = ms
        # _.trackerByHandId[hId >> PP].combs >> count >> PP

    for ev in events:
        if isinstance(ev, list) and len(ev) == 4:
            player, pe, we, ro = ev
            suggestion = (pe, we, ro)
        elif ev >> typeOf == HasOne:
            respondant = ev.handId
            ys = _.trackerByHandId[respondant].ys
            ms = _.trackerByHandId[respondant].ms
            ns = _.trackerByHandId[respondant].ns
            if _.trackerByHandId[respondant].ys.intersection(suggestion):
                f'We know {respondant} has {_.trackerByHandId[respondant].ys.intersection(suggestion)}' >> PP
                #suggestion intersects with a card we know the respondant has so no additional information
                pass
            else:
                possibleCards = _.trackerByHandId[respondant].ms.intersection(suggestion)
                if len(possibleCards) == 1:
                    # We've determined a player definitely has a certain card. This means this information needs
                    # adding to the knowns and the previous inference up to this point needs redoing
                    # for the moment print the data and throw an error so the user can add it to the events list
                    f'{respondant} has {possibleCards}' >> PP
                    1 / 0
                else:
                    # we are left with 2 or 3 possible cards the player has so filter the hand combinations
                    newCombs = _.trackerByHandId[respondant].combs \
                        >> select >> (lambda comb: comb >> intersects >> possibleCards)
                    f'{respondant}: {_.trackerByHandId[respondant].combs >> count} -> {newCombs >> count}' >> PP
                    _.trackerByHandId[respondant].combs = newCombs

    # as a temporary stop gap let's put the prob into the score - later we'll do the prior and update the PP code
    for hId in helper.otherHandIds:
        combs = _.trackerByHandId[hId].combs
        nCombs = combs >> count
        # for c in _.pad >> keys:
        #     p = 0
        #     for comb in combs:
        #         if c in combs:
        #             p += _.trackerByHandId[hId].posterior[comb]
        #     _.pad[c][hId].prior = p
        # _.trackerByHandId[hId].prior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict
        _.trackerByHandId[hId].posterior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict

    helper.pad = _.pad
    helper.trackerByHandId = _.trackerByHandId
    del _.pad
    del _.trackerByHandId
    return helper


@coppertop(style=binary)
def processSuggestions1(helper:cluedo_helper, events:pylist, like:pydict) -> cluedo_helper:
    _.pad = helper.pad
    _.trackerByHandId = helper.trackerByHandId
    helper.pad = Missing
    helper.trackerByHandId = Missing

    for ev in events:
        if isinstance(ev, list) and len(ev) == 4:
            player, pe, we, ro = ev
            if player != helper.handId:
                suggestion = set([pe, we, ro])
                combs = _.trackerByHandId[player].combs
                for comb in combs:
                    overlap = suggestion.intersection(comb)
                    _.trackerByHandId[player].posterior[comb] = \
                        _.trackerByHandId[player].posterior[comb] * like[len(overlap)] #>> PP

    # divide by P(data)
    for hId in helper.otherHandIds:
        sum = 0
        for comb in _.trackerByHandId[hId].combs:
            sum += _.trackerByHandId[hId].posterior[comb]
        sum >> PP
        for comb in _.trackerByHandId[hId].combs:
            p = _.trackerByHandId[hId].posterior[comb] / sum
            _.trackerByHandId[hId].posterior[comb] = p
            # _.trackerByHandId[hId].posterior[comb] >> PP
        # _.trackerByHandId[hId].posterior >> PPPost

    # as a temporary stop gap let's put the prob into the score - later we'll do the prior and update the PP code
    for hId in helper.otherHandIds:
        combs = _.trackerByHandId[hId].combs
        nCombs = combs >> count
        for c in _.pad >> keys:
            p = 0
            for comb in combs:
                if c in comb:
                    p += _.trackerByHandId[hId].posterior[comb]
            _.pad[c][hId].posterior = p #>> PP
        # _.trackerByHandId[hId].prior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict
        # _.trackerByHandId[hId].posterior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict

    helper.pad = _.pad
    helper.trackerByHandId = _.trackerByHandId
    del _.pad
    del _.trackerByHandId

    return helper


@coppertop(style=binary)
def processSuggestions2(helper:cluedo_helper, events:pylist, like:pydict) -> cluedo_helper:
    _.pad = helper.pad
    _.trackerByHandId = helper.trackerByHandId
    helper.pad = Missing
    helper.trackerByHandId = Missing

    for ev in events:
        if isinstance(ev, list) and len(ev) == 4:
            player, pe, we, ro = ev
            if player != helper.handId:
                suggestion = set([pe, we, ro])
                _.trackerByHandId[player].suggestions.append(suggestion)
                combs = _.trackerByHandId[player].combs
                for comb in combs:
                    overlap = suggestion.intersection(comb)
                    _.trackerByHandId[player].posterior[comb] = \
                        _.trackerByHandId[player].posterior[comb] * like[len(overlap)] #>> PP

    # divide by P(data)
    for hId in helper.otherHandIds:
        sum = 0
        for comb in _.trackerByHandId[hId].combs:
            sum += _.trackerByHandId[hId].posterior[comb]
        sum >> PP
        for comb in _.trackerByHandId[hId].combs:
            p = _.trackerByHandId[hId].posterior[comb] / sum
            _.trackerByHandId[hId].posterior[comb] = p
            # _.trackerByHandId[hId].posterior[comb] >> PP
        # _.trackerByHandId[hId].posterior >> PPPost

    # as a temporary stop gap let's put the prob into the score - later we'll do the prior and update the PP code
    for hId in helper.otherHandIds:
        combs = _.trackerByHandId[hId].combs
        nCombs = combs >> count
        for c in _.pad >> keys:
            p = 0
            for comb in combs:
                if c in comb:
                    p += _.trackerByHandId[hId].posterior[comb]
            _.pad[c][hId].posterior = p #>> PP
        # _.trackerByHandId[hId].prior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict
        # _.trackerByHandId[hId].posterior = combs >> zipBoth >> ([1] * nCombs) >> to >> pydict

    helper.pad = _.pad
    helper.trackerByHandId = _.trackerByHandId
    del _.pad
    del _.trackerByHandId

    return helper


@coppertop
def PPPost(pByComb):
    for k, v in pByComb.items():
        f'{k} -> {v}' >> PP

@coppertop
def yesNoMaybesFor(pad, hId):
    ys, ns, ms = set(), set(), set()
    for c in pad >> keys:
        s = pad[c][hId]
        if s.state == YES:
            ys.add(c)
        elif s.state == NO:
            ns.add(c)
        elif s.state == MAYBE:
            ms.add(c)
        else:
            raise ProgrammerError()
    return ys, ns, ms


@coppertop
def createHelper(handId:Card, hand:pylist, otherHandSizesById:pydict) -> cluedo_helper:

    sizeByHandId = {TBI:3} \
        >> atPut >> handId >> (hand >> count) \
        >> join >> otherHandSizesById

    handsToTrack = sizeByHandId >> keys

    # SHOULDDO replace these with struct creation
    @coppertop
    def newPadCell(c, hId):
        return dstruct(cell, state=MAYBE, suggestions=[], haveOnes=[], prior=0, posterior=0)

    def newHandTracker(hId):
        return dstruct(ys=Missing, ns=Missing, ms=Missing, combs=Missing, prior=Missing, suggestions=[])

    @coppertop
    def newRow(c, hIds):
        return hIds >> zipBoth >> (hIds >> collect >> newPadCell(c, _)) >> to >> pydict

    cards = (people, weapons, rooms) >> joinAll
    pad = cards >> zipBoth >> (cards >> collect >> newRow(_, handsToTrack)) >> to >> cluedo_pad
    # in bones we should certainly be able to tell the difference between a list of tuples and a tuple of lists (i.e. a
    # product of exponentials and a exponential of products) even if we can't in python very easily

    otherHandIds = otherHandSizesById >> keys
    trackerByHandId = otherHandIds >> zipBoth >> (otherHandIds >> collect >> newHandTracker) >> to >> pydict

    return dstruct(
        handId=handId,
        hand=hand,
        sizeByHandId=sizeByHandId,
        pad=pad,
        trackerByHandId=trackerByHandId,
        otherHandIds=otherHandIds,
    ) | cluedo_helper


cluedo_helper.setConstructor(createHelper)
