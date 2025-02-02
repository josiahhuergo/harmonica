"""TODO
- Create Criterion subclasses for all criteria
- Build out decision tree in `collect()`
- Convert algorithms into iterators / generators for lazy evaluation
"""

from __future__ import annotations
from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Any

from harmonica._scale import PitchClassSet
from harmonica.utility import powerset
from harmonica._chord import PitchSet, PitchSetShape

type PitchSets = list[PitchSet]

class FindPitchSets:
    """Tool for finding pitch sets which meet given criteria.
    
    You call criteria setting methods and then return results with collect()."""

    min_pitch: int
    max_pitch: int
    criteria: PSetCriteria

    def __init__(self, min_pitch: int, max_pitch: int):
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.criteria = PSetCriteria()

    ## COLLECTING RESULTS ##

    def collect(self) -> PitchSets:
        if self.criteria.has_shape is not None:
            return self._transpositions()
        else:
            return self._brute_force()
        
    ## SETTING CRITERIA ##
        
    def is_size(self, size: int):
        assert size > 0, "Size must be more than 0."

        if self.criteria.max_size.value is not None:    # Only one can be used, max_size or is_size
            self.criteria.max_size.value = None
        self.criteria.is_size.value = size

        return self

    def max_size(self, max_size: int):
        assert max_size > 0, "Max size must be more than 0."

        if self.criteria.is_size.value is not None:     # Only one can be used, max_size or is_size
            self.criteria.is_size.value = None
        self.criteria.max_size.value = max_size

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
    
    ## SEARCH ALGORITHMS ##
    
    def _brute_force(self) -> PitchSets:
        results: PitchSets = []

        # Iterate through powerset of range, and then assert that criterion.filter(pset)
        # is true for all criteria in self.criteria.get()
        for pitch_set in powerset(range(self.min_pitch, self.max_pitch)):
            pset = PitchSet(list(pitch_set))
            if all([criterion.filter(pset) for criterion in self.criteria.get()]):
                results.append(pset)

        return results
    
    def _transpositions(self) -> PitchSets:
        # Called when has_shape is present, transposes a pitch set stamped at 
        # min_pitch until it's highest pitch exceeds max_pitch.
        
        results: PitchSets = []

        return results

class PSetCriteria:
    is_size: PSetIsSize
    max_size: PSetMaxSize 
    has_shape: PSetHasShape 
    has_subshape: PSetHasSubshape 
    in_pcset: PSetInPCSet 

    def __init__(self):
        self.is_size = PSetIsSize()
        self.max_size = PSetMaxSize()
        self.has_shape = PSetHasShape()
        self.has_subshape = PSetHasSubshape()
        self.in_pcset = PSetInPCSet()

    def get(self) -> list[Criterion]:
        """Returns a list of the criterion objects which have non-None values."""
        return [criterion for criterion in vars(self).values() if criterion.value != None]

class Criterion: 
    value: Any

    @abstractmethod
    def filter(self, object) -> bool: ...

@dataclass
class PSetIsSize(Criterion):
    value: int | None = None

    def filter(self, object: PitchSet) -> bool:
        if object.size == self.value:
            return True
        else:
            return False

@dataclass
class PSetMaxSize(Criterion):
    value: int | None = None

    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int
        if object.size <= self.value:
            return True
        else:
            return False

@dataclass
class PSetHasShape(Criterion):
    value: PitchSetShape | None = None

    def filter(self, object: PitchSet) -> bool:
        if object.shape == self.value:
            return True
        else:
            return False

@dataclass
class PSetHasSubshape(Criterion):
    value: PitchSetShape | None = None

    def filter(self, object: PitchSet) -> bool:
        return True  # WRITE THIS

@dataclass
class PSetInPCSet(Criterion):
    value: PitchClassSet | None = None

    def filter(self, object: PitchSet) -> bool:
        #
        return True  # WRITE THIS

