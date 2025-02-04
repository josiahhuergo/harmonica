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

from harmonica.scale import PitchClassSet
from harmonica.utility import powerset
from harmonica._chord import PitchSet, PitchSetShape

type PitchSets = list[PitchSet]

class FindPitchSets:
    """Tool for finding pitch sets which meet given criteria.
    
    You call criteria setting methods and then return results with collect()."""

    criteria: PSetCriteria

    def __init__(self, min_pitch: int, max_pitch: int):
        assert min_pitch < max_pitch, "Min pitch must be less than max pitch."

        self.criteria = PSetCriteria(min_pitch, max_pitch)
        
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

    ## COLLECTING RESULTS ##

    def collect(self) -> PitchSets:
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

        results: PitchSets = []
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch
        criteria: list[Criterion] = list(self.criteria.get().values())

        for pitch_set in powerset(range(min_pitch, max_pitch)):
            pitch_set = PitchSet(list(pitch_set)) 
            
            if all([criterion.filter(pitch_set) for criterion in criteria]):
                results.append(pitch_set)

        return results
    
    def _pcset_search(self) -> PitchSets:
        """Iterate through powerset of range of pitches inside of a pitch class set
        and filter through elements using all present criteria."""

        assert self.criteria.in_pcset.value is not None

        results: PitchSets = []
        pcset: PitchClassSet = self.criteria.in_pcset.value
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch
        criteria: list[Criterion] = list(
            criterion for criterion in self.criteria.get().values()
        )

        pitches = [pitch for pitch in range(min_pitch, max_pitch + 1) if pcset.contains(pitch)]
        for pitch_set in powerset(pitches):
            pitch_set = PitchSet(list(pitch_set))

            if all([criterion.filter(pitch_set) for criterion in criteria]):
                results.append(pitch_set)

        return results
    
    def _transpositions(self) -> PitchSets:
        """Called when has_shape is present, transposes a pitch set stamped at 
        min_pitch until it's highest pitch exceeds max_pitch"""

        assert self.criteria.has_shape.value is not None

        results: PitchSets = []
        shape: PitchSetShape = self.criteria.has_shape.value
        min_pitch: int = self.criteria.min_pitch
        max_pitch: int = self.criteria.max_pitch

        transpositions = (max_pitch - min_pitch) - shape.span + 1

        if transpositions < 1:
            return results

        pitch_set: PitchSet = shape.stamp(min_pitch)

        for transposition in range(transpositions):
            results.append(pitch_set + transposition)

        return results

class PSetCriteria:
    min_pitch: int
    max_pitch: int
    is_size: PSetIsSize
    max_size: PSetMaxSize 
    has_shape: PSetHasShape 
    has_subshape: PSetHasSubshape 
    in_pcset: PSetInPCSet

    def __init__(self, min_pitch: int, max_pitch: int):
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.is_size = PSetIsSize()
        self.max_size = PSetMaxSize()
        self.has_shape = PSetHasShape()
        self.has_subshape = PSetHasSubshape()
        self.in_pcset = PSetInPCSet()

    def get(self, exclude: list[str] = []) -> dict[str, Criterion]:
        """Returns a list of the criterion objects which have non-None values."""
        return {
            name:criterion for name, criterion in vars(self).items()
            if name != "min_pitch" 
            and name != "max_pitch" 
            and criterion.value is not None 
            and name not in exclude
        }

class Criterion: 
    value: Optional[Any]

    @abstractmethod
    def filter(self, object) -> bool: ...

@dataclass
class PSetIsSize(Criterion):
    value: Optional[int] = None

    def filter(self, object: PitchSet) -> bool:
        if object.size == self.value:
            return True
        else:
            return False

@dataclass
class PSetMaxSize(Criterion):
    value: Optional[int] = None

    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int

        if object.size <= self.value:
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

