# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# Python imports
import itertools, collections, numpy as np

# bones imports
from coppertop.utils import Missing, Null



# step 1 serialisation framework with object link handling

Handle = collections.namedtuple('Handle', ['name', 'id'])


class SuitCase:

    # NB: this is a bit silly to have a class with two separate modes, but I liked the name SuitCase so overloaded it

    __slots__ = [
        '_packersByName', '_handleByObject', '_contentsByHandle', '_handleSeed',
        '_unpackersByName', '_objectByHandle', '_objectByName', '_handleByName'
    ]


    # PACKING MODE
    
    @staticmethod
    def forPacking(packersByName):
        suitcase = SuitCase()
        suitcase._packersByName = packersByName
        suitcase._handleByObject = {Missing: Handle('Missing', 1), Null: Handle('Null', 2)}
        suitcase._contentsByHandle = {}
        suitcase._handleSeed = itertools.count(3)
        return suitcase

    def pack(self, closure):
        for obj in closure:
            self._handleByObject.setdefault(obj, None)
        for obj in closure:
            handle = self.handleFor(obj)
            self._contentsByHandle[handle] = self._packersByName[handle.name](obj, self)
        return self

    def handleFor(self, obj) -> Handle:
        # answer the handle for obj, creating one if necessary
        if (handle := self._handleByObject.get(obj, Missing)) is Missing:
            # not in closure
            return self._handleByObject[Missing]
        elif handle is None:
            # has no handle yet so create one
            self._handleByObject[obj] = handle = Handle(type(obj).__name__, next(self._handleSeed))
        return handle

    def set(self, name, obj):
        self._contentsByHandle[name] = self.handleFor(obj)
        return self

    @property
    def contents(self):
        return self._contentsByHandle


    # UNPACKING MODE
    
    @staticmethod
    def forUnpacking(unpackersByName):
        suitcase = SuitCase()
        suitcase._objectByHandle = {Handle('Missing', 1): Missing, Handle('Null', 2): Null}
        suitcase._unpackersByName = unpackersByName
        suitcase._handleByName = {}
        return suitcase

    def objectFor(self, handle):
        return self._objectByHandle[handle]

    def handle(self, name):
        return self._handleByName[name]

    def create(self, contents):
        names = []
        for handleOrName, contentOrHandle in contents.items():
            if not isinstance(handleOrName, str):
                create, _ = self._unpackersByName[handleOrName.name]
                obj = self._objectByHandle[handleOrName] = create(contentOrHandle)
            else:
                names.append(handleOrName)
        for name in names:
            self._handleByName[name] = contents[name]
        return self

    def relink(self, contents):
        for handleOrName, contentOrHandle in contents.items():
            if not isinstance(handleOrName, str):
                _, relink = self._unpackersByName[handleOrName.name]
                relink(self._objectByHandle[handleOrName], contentOrHandle, self)
        return self

    def unpack(self, contents):
        self.create(contents)
        self.relink(contents)
        return self

    def replace(self, handle, obj):
        self._objectByHandle[handle] = obj
        return self

    @property
    def closure(self):
        answer = dict(self._objectByHandle)
        answer.pop(Handle('Missing', 1))
        answer.pop(Handle('Null', 2))
        return list(answer.values())

    def get(self, name):
        return self._objectByHandle.get(self._handleByName.get(name, Missing), Missing)


# step 2 serialisation functions to and from BLIP (Binary Language Independent Payload) format
# this would handle a standard set of basic types - str, int, float, list, dict, np.ndarray, dataframes, etc that have
# common representations in the target languages and ideally in a zero-copy way

def toBlip(contents):
    return contents

def fromBlip(raw):
    return raw


# example class and step 1 serialisation methods

class Person:
    __slots__ = ['mf', 'name', 'father', 'mother', 'ageByChild', 'ageAtDeath']

    def __init__(self, mf, name, fatherAndAge, motherAndAge, ageAtDeath):
        self.mf = mf
        self.name = name
        if fatherAndAge is Missing or fatherAndAge is Null:
            self.father = fatherAndAge
        else:
            self.father, age = fatherAndAge
            self.father.ageByChild[self] = age
        if motherAndAge is Missing or motherAndAge is Null:
            self.mother = motherAndAge
        else:
            self.mother, age = motherAndAge
            self.mother.ageByChild[self] = age
        self.ageByChild = {}
        self.ageAtDeath = ageAtDeath

    def __repr__(self):
        fathersName = self.father.name if self.father else str(self.father)
        mothersName = self.mother.name if self.mother else str(self.mother)
        return f'{self.name}({self.mf}, {fathersName}, {mothersName}, {self.ageAtDeath})'


    # these serialisation methods for Person could equally be exogenous, albeit friendly, free functions

    def pack(self, suitcase):
        # serialise as a dictionary
        content = {}
        content['mf'] = self.mf
        content['name'] = self.name
        content['mother'] = suitcase.handleFor(self.mother)
        content['father'] = suitcase.handleFor(self.father)
        content['ageAtDeath'] = self.ageAtDeath
        content['ageByChild'] = ageByChild = dict()
        for child, age in self.ageByChild.items():
            ageByChild[suitcase.handleFor(child)] = age
        return content

    @staticmethod
    def create(content):
        inst = Person(content['mf'], content['name'], Missing, Missing, content['ageAtDeath'])
        return inst

    def relink(self, content, suitcase):
        if self.mother is Missing: self.mother = suitcase.objectFor(content['mother'])
        if self.father is Missing: self.father = suitcase.objectFor(content['father'])
        # splicing here is a bit more complicated so is left as an exercise...
        for handle, age in content['ageByChild'].items():
            self.ageByChild[suitcase.objectFor(handle)] = age
        return self


packers = {'Person': (Person.pack)}
unpackers = {'Person': (Person.create, Person.relink)}


# closure generators

def allDescendentsOf(person, closure):
    closure.update(person.ageByChild)
    for child, age in person.ageByChild.items():
        allDescendentsOf(child, closure)
    return closure

def allAncestorsOf(person, closure):
    if person.father: closure[person.father] = None
    if person.mother: closure[person.mother] = None
    if person.father: allAncestorsOf(person.father, closure)
    if person.mother: allAncestorsOf(person.mother, closure)
    return closure


# test data - Genesis 1-9

motherNature = Person('f', 'Mother Nature', Null, Null, np.nan)

adam = Person('m', 'Adam', (motherNature, np.nan), (motherNature, np.nan), 930)
eve = Person('f', 'Eve', (motherNature, np.nan), (motherNature, np.nan), np.nan)
cain = Person('m', 'Cain', (adam, np.nan), (eve, np.nan), np.nan)
able = Person('m', 'Able', (adam, np.nan), (eve, np.nan), np.nan)

cainswife = Person('f', 'Cains Wife', Null, Null, np.nan)
enoch = Person('m', 'Enoch', (cain, np.nan), (cainswife, np.nan), np.nan)
irad = Person('m', 'Irad', (enoch, np.nan), Null, np.nan)
mehujael = Person('m', 'Mehujael', (irad, np.nan), Null, np.nan)
methushael = Person('m', 'Methushael', (mehujael, np.nan), Null, np.nan)
lamech = Person('m', 'Lamech', (methushael, np.nan), Null, np.nan)

adah = Person('f', 'Adah', Null, Null, np.nan)
jabal = Person('m', 'Jabal', (lamech, np.nan), (adah, np.nan), np.nan)
jubal = Person('m', 'Jubal', (lamech, np.nan), (adah, np.nan), np.nan)

zillah = Person('f', 'Zillah', Null, Null, np.nan)
tubalCain = Person('m', 'Tubal-Cain', (lamech, np.nan), (zillah, np.nan), np.nan)
naamah = Person('f', 'Naamah', (lamech, np.nan), (zillah, np.nan), np.nan)

seth = Person('m', 'Seth', (adam, 130), (eve, np.nan), 912)
enosh = Person('m', 'Enosh', (seth, 105), Null, 905)
kenan = Person('m', 'Kenan', (enosh, 90), Null, 910)
mahalalel = Person('m', 'Mahalalel', (kenan, 70), Null, 895)
jared = Person('m', 'Jared', (kenan, 65), Null, 962)
enoch = Person('m', 'Enoch', (jared, 162), Null, 365)
methuselah = Person('m', 'Methuselah', (enoch, 162), Null, 969)
lamech = Person('m', 'Lamech', (methuselah, 187), Null, 700)
noah = Person('m', 'Noah', (methuselah, 187), Null, 950)
shem = Person('m', 'Shem', (noah, 500), Null, np.nan)
ham = Person('m', 'Ham', (noah, 500), Null, np.nan)
japheth = Person('m', 'Japheth', (noah, 500), Null, np.nan)
canaan = Person('m', 'Canaan', (ham, np.nan), Null, np.nan)



# test 1 - descendents of mother nature

humanRaceClosure1 = list(allDescendentsOf(motherNature, dict()).keys())
suitcase1 = SuitCase.forPacking(packers).pack(humanRaceClosure1)
serialised = toBlip(suitcase1.contents)

contents = fromBlip(serialised)
suitcase2 = SuitCase.forUnpacking(unpackers).unpack(contents)
humanRaceClosure2 = suitcase2.closure

print(humanRaceClosure1)
print(humanRaceClosure2)

print([id(x) for x in humanRaceClosure1])
print([id(x) for x in humanRaceClosure2])



# test 2 - kenan plus ancestors less mother nature

closure1 = allAncestorsOf(kenan, dict())
closure1.pop(motherNature)
closure1 = list(closure1.keys())
suitcase1 = SuitCase.forPacking(packers).pack(closure1).pack([kenan]).set('kenan', kenan).set('eve', eve)
serialised = toBlip(suitcase1.contents)

contents = fromBlip(serialised)
suitcase2 = SuitCase.forUnpacking(unpackers).create(contents)
# at this point if we replace objects in the closure with other objects then we can effectively splice a serialised
# closure into an existing network - let's replace Eve with Naamah with the consequence that Seth has a new mother
suitcase2.replace(suitcase2.handle('eve'), naamah)
suitcase2 = suitcase2.relink(contents)
closure2 = suitcase2.closure

print(closure1)
print(closure2)

print([id(x) for x in closure1])
print([id(x) for x in closure2])

# NOTE: Adam parents are Missing from closure2, but Enosh's mother is Null, and now Seth's mother is Naamah!!
# [Enosh(m, Seth, Null, 905), Seth(m, Adam, Eve, 912), Adam(m, Mother Nature, Mother Nature, 930), Eve(f, Mother Nature, Mother Nature, nan)]
# [Enosh(m, Seth, Null, 905), Seth(m, Adam, Naamah, 912), Adam(m, Missing, Missing, 930), Naamah(f, Lamech, Zillah, nan), Kenan(m, Enosh, Null, 910)]
# [4927432368, 4927432288, 4927430848, 4927430768]
# [4927435408, 4927435488, 4927435568, 4927432208, 4927435728]

print(suitcase2.get('kenan'))
print(suitcase2.get('ham'))
