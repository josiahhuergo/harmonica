"""TODO
- Create Criterion subclasses for all criteria
- Write more search algorithms to remove computational bottlenecks
- Build out decision tree in `collect()`
- Convert algorithms into iterators / generators for lazy evaluation
"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from itertools import combinations
from typing import Generic, Optional, TypeVar

from harmonica.pitch import PitchClassSet
from harmonica.pitch._pitchfunc import PitchFunc
from harmonica.utility import powerset
from harmonica.pitch import PitchSet, PitchSetShape

type PitchSets = set[PitchSet]


class FindPitchSets:
    """Tool for finding pitch sets which meet given criteria.

    You call criteria setting methods and then return results with collect()."""

    criteria: Criteria

    def __init__(self, min_pitch: int, max_pitch: int):
        assert min_pitch < max_pitch, "Min pitch must be less than max pitch."

        self.criteria = Criteria(min_pitch, max_pitch)

    ## SETTING CRITERIA ##

    def cardinality(self, cardinality: int):
        assert cardinality > 0, "Cardinality must be more than 0."

        if (
            self.criteria.max_card.value is not None
        ):  # Only one can be used, max_cardinality or cardinality
            self.criteria.max_card.value = None
        self.criteria.cardinality.value = cardinality

        return self

    def max_cardinality(self, max_size: int):
        assert max_size > 0, "Max cardinality must be more than 0."

        if (
            self.criteria.cardinality.value is not None
        ):  # Only one can be used, max_cardinality or cardinality
            self.criteria.cardinality.value = None
        self.criteria.max_card.value = max_size

        return self

    def has_shape(self, shape: PitchSetShape):
        if (
            self.criteria.has_subshape.value is not None
        ):  # Only one can be used, has_Shape or has_subshape
            self.criteria.has_subshape.value = None
        self.criteria.has_shape.value = shape

        return self

    def has_subshape(self, subshape: PitchSetShape):
        if (
            self.criteria.has_shape.value is not None
        ):  # Only one can be used, has_Shape or has_subshape
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

        if self.criteria.has_shape.value:
            return self._transpositions()
        elif self.criteria.in_pcset.value:
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

        pitches = [
            pitch for pitch in range(min_pitch, max_pitch + 1) if pcset.contains(pitch)
        ]
        for pitch_set in powerset(pitches):
            pitch_set = PitchSet(list(pitch_set))

            if (
                self.criteria.filter(pitch_set, excludes=["in_pcset"])
                and pitch_set.pitches != []
            ):
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


T = TypeVar("T")


class Criterion(Generic[T]):
    value: Optional[T] = None

    @abstractmethod
    def filter(self, object) -> bool: ...


@dataclass
class Cardinality(Criterion[int]):
    def filter(self, object: PitchSet) -> bool:
        if object.cardinality == self.value:
            return True
        else:
            return False


@dataclass
class MinCard(Criterion[int]):
    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int

        if object.cardinality >= self.value:
            return True
        else:
            return False


@dataclass
class MaxCard(Criterion[int]):
    def filter(self, object: PitchSet) -> bool:
        assert type(self.value) == int

        if object.cardinality <= self.value:
            return True
        else:
            return False


@dataclass
class HasShape(Criterion[PitchSetShape]):
    def filter(self, object: PitchSet) -> bool:
        if object.shape == self.value:
            return True
        else:
            return False


@dataclass
class HasSubshape(Criterion[PitchSetShape]):
    def filter(self, object: PitchSet) -> bool:
        if object.shape == self:
            return True
        else:
            return False


@dataclass
class InPCSet(Criterion[PitchClassSet]):
    def filter(self, object: PitchSet) -> bool:
        assert self.value is not None

        for pitch in object:
            if not self.value.contains(pitch):
                return False

        return True


@dataclass
class Criteria:
    min_pitch: int
    max_pitch: int
    cardinality: Cardinality = field(default_factory=Cardinality)
    min_card: MinCard = field(default_factory=MinCard)
    max_card: MaxCard = field(default_factory=MaxCard)
    has_shape: HasShape = field(default_factory=HasShape)
    has_subshape: HasSubshape = field(default_factory=HasSubshape)
    in_pcset: InPCSet = field(default_factory=InPCSet)

    def get(self, excludes=None) -> dict[str, Criterion]:
        """Returns a dict containing criterion objects which have non-None values and
        aren't the pitch bounds."""
        if excludes is None:
            excludes = []
        return {
            name: criterion
            for name, criterion in vars(self).items()
            if name != "min_pitch"
            and name != "max_pitch"
            and criterion.value is not None
            and name not in excludes
        }

    def filter(self, pitch_set: PitchSet, excludes: list[str] = []) -> bool:
        """Returns True if pitch set passes criteria. Ignores criteria in excludes list."""

        return all(
            [criterion.filter(pitch_set) for criterion in self.get(excludes).values()]
        )


def find_nearby_psets_in_scale(
    source_pset: PitchSet,
    target_scale: PitchFunc,
    proximity: int,
    size_bounds: tuple[int, int],
) -> list[PitchSet]:
    """
    Returns a list of pitch sets that are in the proximity of a source pitch set
    and sit in a target scale.
    """

    target_pitches = []

    for p in source_pset:
        for tp in target_scale.in_range(p - proximity, p + proximity):
            if tp not in target_pitches:
                target_pitches.append(tp)

    proximal_psets = []

    for k in range(size_bounds[0], size_bounds[1] + 1):
        proximal_psets.extend(
            [PitchSet(list(x)) for x in combinations(target_pitches, k)]
        )

    return proximal_psets
