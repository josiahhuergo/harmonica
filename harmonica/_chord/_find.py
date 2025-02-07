"""TODO
- Create Criterion subclasses for all criteria
- Write more search algorithms to remove computational bottlenecks
- Build out decision tree in `collect()`
- Convert algorithms into iterators / generators for lazy evaluation
"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from harmonica._scale import PitchClassSet
from harmonica.utility import powerset
from harmonica._chord import PitchSet, PitchSetShape

type PitchSets = set[PitchSet]

class FindPitchSets:
    """Tool for finding pitch sets which meet given criteria.
    
    You call criteria setting methods and then return results with collect()."""

    criteria: PSetCriteria

    def __init__(self, min_pitch: int, max_pitch: int):
        assert min_pitch < max_pitch, "Min pitch must be less than max pitch."

        self.criteria = PSetCriteria(min_pitch, max_pitch)
        
    ## SETTING CRITERIA ##

    def cardinality(self, cardinality: int):
        assert cardinality > 0, "Cardinality must be more than 0."

        if self.criteria.max_card.value is not None:    # Only one can be used, max_cardinality or cardinality
            self.criteria.max_card.value = None
        self.criteria.cardinality.value = cardinality

        return self

    def max_cardinality(self, max_size: int):
        assert max_size > 0, "Max cardinality must be more than 0."

        if self.criteria.cardinality.value is not None:     # Only one can be used, max_cardinality or cardinality
            self.criteria.cardinality.value = None
        self.criteria.max_card.value = max_size

        return self

    def has_shape(self, shape: PitchSetShape):
        if self.criteria.has_subshape.value is not None:    # Only one can be used, has_Shape or has_subshape
            self.criteria.has_subshape.value = None
        self.criteria.has_shape.value = shape

        return self

    def has_subshape(self, subshape: PitchSetShape):
        if self.criteria.has_shape.value is not None:   # Only one can be used, has_Shape or has_subshape
            self.criteria.has_shape.value = None
        self.criteria.has_subshape.value = subshape

        return self

    def in_pcset(self, pcset: PitchClassSet):
        self.criteria.in_pcset.value = pcset

        return self

    ## COLLECTING RESULTS ##

    def collect(self) -> PitchSets:
        """Deploys the best algorithms given the current criteria settings
        and returns a set of pitch sets."""

        if self.criteria.has_shape.value is not None:
            return self._transpositions()
        elif self.criteria.in_pcset.value is not None:
            return self._pcset_search()
        else:
            return self._brute_force()
    
    ## SEARCH ALGORITHMS ##
    
    def _brute_force(self) -> PitchSets:
        """Iterate through powerset of range, and then assert that criterion.filter(pset)
        is true for all criteria."""

        results: PitchSets = set()
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch

        for pitch_set in powerset(range(min_pitch, max_pitch + 1)):
            pitch_set = PitchSet(list(pitch_set)) 
            
            if self.criteria.filter(pitch_set):
                results.add(pitch_set)

        return results
    
    def _pcset_search(self) -> PitchSets:
        """Iterate through powerset of range of pitches inside of a pitch class set
        and filter through elements using all present criteria."""

        assert self.criteria.in_pcset.value is not None

        results: PitchSets = set()
        pcset: PitchClassSet = self.criteria.in_pcset.value
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch

        pitches = [pitch for pitch in range(min_pitch, max_pitch + 1) if pcset.contains(pitch)]
        for pitch_set in powerset(pitches):
            pitch_set = PitchSet(list(pitch_set))

            if self.criteria.filter(pitch_set, excludes=["in_pcset"]) and pitch_set.pitches != []:
                results.add(pitch_set)

        return results
    
    def _transpositions(self) -> PitchSets:
        """Called when has_shape is present, transposes a pitch set stamped at 
        min_pitch until it's highest pitch exceeds max_pitch."""

        assert self.criteria.has_shape.value is not None

        results: PitchSets = set()
        shape: PitchSetShape = self.criteria.has_shape.value
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch

        transpositions = (max_pitch - min_pitch) - shape.span + 1

        if transpositions < 1:
            return results

        pitch_set: PitchSet = shape.stamp(min_pitch)

        for transposition in range(transpositions):
            if self.criteria.filter(pitch_set + transposition, excludes=["has_shape"]):
                results.add(pitch_set + transposition)

        return results

class PSetCriteria:
    min_pitch: int
    max_pitch: int
    cardinality: PSetCardinality
    min_card: PSetMinCard
    max_card: PSetMaxCard 
    has_shape: PSetHasShape 
    has_subshape: PSetHasSubshape 
    in_pcset: PSetInPCSet

    def __init__(self, min_pitch: int, max_pitch: int):
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.cardinality = PSetCardinality()
        self.min_card = PSetMinCard()
        self.max_card = PSetMaxCard()
        self.has_shape = PSetHasShape()
        self.has_subshape = PSetHasSubshape()
        self.in_pcset = PSetInPCSet()

    def get(self, excludes: list[str] = []) -> dict[str, Criterion]:
        """Returns a dict containing criterion objects which have non-None values and
        aren't the pitch bounds."""
        return {
            name:criterion for name, criterion in vars(self).items()
            if name != "min_pitch" 
            and name != "max_pitch" 
            and criterion.value is not None 
            and name not in excludes
        }
    
    def filter(self, pitch_set: PitchSet, excludes: list[str] = []) -> bool:
        """Returns True if pitch set passes criteria. Ignores criteria in excludes list."""

        return all([
            criterion.filter(pitch_set) for criterion in self.get(excludes).values()
        ])

class Criterion: 
    value: Optional[Any]

    @abstractmethod
    def filter(self, object) -> bool: ...

@dataclass
class PSetCardinality(Criterion):
    value: Optional[int] = None

    def filter(self, object: PitchSet) -> bool:
        if object.cardinality == self.value:
            return True
        else:
            return False

@dataclass
class PSetMinCard(Criterion):
    value: Optional[int] = None

    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int

        if object.cardinality >= self.value:
            return True
        else:
            return False

@dataclass
class PSetMaxCard(Criterion):
    value: Optional[int] = None

    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int

        if object.cardinality <= self.value:
            return True
        else:
            return False

@dataclass
class PSetHasShape(Criterion):
    value: Optional[PitchSetShape] = None

    def filter(self, object: PitchSet) -> bool:
        if object.shape == self.value:
            return True
        else:
            return False

@dataclass
class PSetHasSubshape(Criterion):
    value: Optional[PitchSetShape] = None

    def filter(self, object: PitchSet) -> bool:
        return True  # WRITE THIS

@dataclass
class PSetInPCSet(Criterion):
    value: Optional[PitchClassSet] = None

    def filter(self, object: PitchSet) -> bool:
        assert self.value is not None

        for pitch in object:
            if not self.value.contains(pitch):
                return False
        
        return True 

