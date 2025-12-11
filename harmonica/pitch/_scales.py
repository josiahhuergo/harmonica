from __future__ import annotations
from itertools import combinations
from typing import Iterable, Optional, overload
from dataclasses import dataclass, field
import math

from harmonica.utility import (
    cumsum,
    cycle_cumsum,
    cycle_diff,
    repeating_subseq,
    rotate,
)


@dataclass
class PitchClassSet:
    """A set of pitch classes used to represent a scale, without respect to a root.

    `{0,2,4,5,7,9,11} mod 12`, or `PitchClassSet([0,2,4,5,7,9,11], 12)`, represents the pitches mapped to
    by C major, D dorian, E phrygian, etc."""

    ## DATA ##

    pitch_classes: list[int]
    modulus: int
    root: Optional[int] = field(default=None)

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert self.modulus > 0, "Modulus must be a positive integer."
        assert self.pitch_classes == list(
            sorted(self.pitch_classes)
        ), "Pitch classes must be in order."
        assert len(self.pitch_classes) == len(
            set(self.pitch_classes)
        ), "Pitch classes must be unique."
        assert all(
            [0 <= pitch < self.modulus for pitch in self.pitch_classes]
        ), "Pitch classes must be between 0 and modulus - 1."
        if self.root is not None:
            assert self.root in self.pitch_classes, "Root must be in pitch class set."

    def __getitem__(self, item: int | slice) -> int | list[int]:
        if isinstance(item, int):
            return self.pitch_classes[item]
        if isinstance(item, slice):
            return self.pitch_classes[item.start : item.stop : item.step]

    def __add__(self, other: int) -> PitchClassSet:
        return self.transposed(other)

    def __sub__(self, other: int) -> PitchClassSet:
        return self.transposed(-other)

    ## TRANSFORMATION ##

    def select(self, selector: PitchClassSet) -> PitchClassSet:
        """Uses another pitch class set as a selector to return a subset."""

        assert (
            selector.modulus == self.cardinality
        ), "Modulus of selector set must be equal to cardinality of pitch class set it's selecting."
        assert selector.root is not None, "Selector set must have a root."
        assert self.root is not None, "Pitch class set must have a root."

        root_index = self.index(self.root)

        pitch_classes = sorted(
            [
                self.pitch_classes[(index + root_index) % self.cardinality]
                for index in selector.pitch_classes
            ]
        )

        root = self.pitch_classes[(root_index + selector.root) % self.cardinality]

        return PitchClassSet(pitch_classes, self.modulus, root)

    def rotate_mode_relative(self, amount: int):
        """Shifts the root of the pitch class set, accessing a relative mode.

        `{0,2,4,5,7,9,11} mod 12 root 4` rotated this way by 2 would shift the
        root up to the pitch class 2 spaces clockwise from the current root.
        This would yield `{0,2,4,5,7,9,11} mod 12 root 7`, because 7 is 2 spaces
        clockwise from 4 in this pitch class set."""

        if self.root is None:
            return

        i = (self.pitch_classes.index(self.root) + amount) % self.cardinality
        self.root = self.pitch_classes[i]

    def rotate_mode_parallel(self, amount: int):
        """Rotates the structure of the pitch class set around the root.

        `{0,2,4,5,7,9,11} mod 12 root 4` rotated this way by 2 would take the
        structure, `[1,2,2,2,1,2,2]`, and rotate it by 2 to yield the structure of
        mixolydian, `[2,2,1,2,2,1,2]`, which stamped onto pitch class 4 yields
        `{1,3,4,6,8,9,11} mod 12 root 4`."""

        if self.root is None:
            return

        structure = self.structure
        structure.rotate(amount)
        new_pcset = structure.stamp_to_pcset_with_root(self.root)
        self.pitch_classes = new_pcset.pitch_classes

    def transpose(self, amount: int):
        """Transposes the pitch classes in the set using modular arithmetic."""

        self.pitch_classes = [(pc + amount) % self.modulus for pc in self.pitch_classes]
        self.pitch_classes.sort()
        if self.root is not None:
            self.root = (self.root + amount) % self.modulus

    def transposed(self, amount: int) -> PitchClassSet:
        """Returns a transposed pitch class set."""

        pitch_classes = [(pc + amount) % self.modulus for pc in self.pitch_classes]
        pitch_classes.sort()
        if self.root is not None:
            root = (self.root + amount) % self.modulus

        return PitchClassSet(pitch_classes, self.modulus, root)

    def normalize(self, pitch_class: int):
        """Transposes the pitch classes in the set so 0 is present."""

        assert pitch_class in self.pitch_classes

        self.transpose(-pitch_class)

    def normalized(self, pitch_class: int) -> PitchClassSet:
        """Returns a normalized pitchset."""

        assert pitch_class in self.pitch_classes

        return self.transposed(-pitch_class)

    ## ANALYSIS ##

    def index(self, pitch_class: int) -> int:
        """Returns the index of a pitch class."""

        assert pitch_class in self.pitch_classes, "Pitch class must be in set."

        return self.pitch_classes.index(pitch_class)

    def scale_function(self, root: int) -> ScaleFunc:
        """Returns a scale function that maps to the same pitches as this pitch class set.

        For example, if we have a pitch class set representing D major (and its modes)
        `{1,2,4,6,7,9,11} mod 12` and we specify 6 as the root then this will return
        `[1,3,5,7,8,10,12] + 6`."""

        return ScaleFunc(
            self.normalized(root).pitch_classes[1:] + [self.modulus],
            min(self.pitch_classes),
        )

    def contains(self, pitch: int) -> bool:
        """Returns true if a pitch belongs to a pitch class in the set."""

        return True if pitch % self.modulus in self.pitch_classes else False

    @property
    def interval_spectrum(self) -> list[list[int]]:
        """Returns a list of lists describing all the intervals present
        in the scale that don't exceed the octave. The first list is of
        intervals between adjacent pitches, then between pitches two spaces
        apart, etc.

        >>> PitchClassSet([0,2,4,5,7,9,11], 12).interval_spectrum
        [
            [2,2,1,2,2,2,1],
            [4,3,3,4,4,3,3],
            [5,5,5,6,5,5,5],
            [7,7,7,7,7,7,6],
            [9,9,8,9,8,8,9]
            [11,10,10,11,10,10,10]
        ]"""

        if self.cardinality <= 1:
            return []

        spectrum: list[list[int]] = []

        for jump in range(1, self.cardinality):
            diff: list[int] = []
            for pos in range(self.cardinality):
                index = (pos + jump) % self.cardinality
                interval = self.pitch_classes[index] - self.pitch_classes[pos]
                diff.append(interval % self.modulus)
            spectrum.append(diff)

        return spectrum

    @property
    def interval_vector(self) -> tuple[int, ...]:
        """Returns the interval vector of the pitch class set.

        Counts the occurrence of each interval class present between pairs of pitch
        classes in the set. There are `floor(m/2)` interval classes in a pitch class
        set with a modulus of `m`."""

        iclass_count: int = math.floor(self.modulus / 2)
        vector: list[int] = [0] * iclass_count

        iclasses = [
            harmonic_interval_class(pair[0], pair[1], self.modulus)
            for pair in list(combinations(self.pitch_classes, 2))
        ]

        for iclass in iclasses:
            vector[iclass - 1] += 1

        return tuple(vector)

    @property
    def cardinality(self) -> int:
        """The number of pitch classes in the set."""

        return len(self.pitch_classes)

    @property
    def structure(self) -> ScaleStructure:
        """Returns the intervallic structure of the pitch class set, by default starting
        from the lowest pitch class in the set."""

        index = 0

        if self.root is not None:
            index = self.pitch_classes.index(self.root)

        intervals = cycle_diff(self.pitch_classes, self.modulus, index)

        return ScaleStructure(intervals)

    @property
    def prime(self) -> PitchClassSet:
        """Returns the prime subscale of the pitch class set, which has an aperiodic
        structure."""

        root = self.pitch_classes[0]

        if self.root is not None:
            root_index = self.pitch_classes.index(self.root)
            prime_len = self.structure.prime.size
            root = self.pitch_classes[root_index % prime_len]

        return self.structure.prime.stamp_to_pcset(root)


@dataclass
class ScaleStructure:
    """A sequence of intervals that describes the circular intervallic
    structure of a pitch class set."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert all(
            [0 < interval for interval in self.intervals]
        ), "Intervals in scale structure must be positive."

    def __getitem__(self, item: int | slice) -> None | int | list[int]:
        if isinstance(item, int):
            return self.intervals[item]
        if isinstance(item, slice):
            return self.intervals[item.start : item.stop : item.step]
        return None

    ## TRANSFORM ##

    def rotate(self, amount: int):
        """Rotates the intervals in the structure."""

        self.intervals = rotate(self.intervals, amount)

    ## GENERATE ##

    def stamp_to_pcset(self, starting_pitch: int) -> PitchClassSet:
        """Creates a pitch class set by "stamping" this scale structure onto pitch class
        space at the pitch class `starting_pitch`."""

        return PitchClassSet(cycle_cumsum(self.intervals, starting_pitch), self.modulus)

    def stamp_to_pcset_with_root(self, starting_pitch: int) -> PitchClassSet:
        """Creates a rooted pitch class set by "stamping" this scale structure onto pitch class
        space at the pitch class `starting_pitch`."""

        return PitchClassSet(
            cycle_cumsum(self.intervals, starting_pitch),
            self.modulus,
            starting_pitch % self.modulus,
        )

    def stamp_to_scale_func(self, transposition: int) -> ScaleFunc:
        """Creates a scale function whose pattern is constructed from this structure."""

        return ScaleFunc(cumsum(self.intervals)[1:], transposition)

    ## ANALYZE ##

    def count_transpositions(self) -> int:
        """Counts the number of unique transpositions that a scale with this
        structure would have."""

        return sum(repeating_subseq(self.intervals))

    def count_modes(self) -> int:
        """Counts the number of distinct modes that a scale with this structure
        would have."""

        return len(repeating_subseq(self.intervals))

    @property
    def prime(self) -> ScaleStructure:
        """Returns the structure of the prime subscale. For example, if the structure
        is [2,1,2,1,2,1,2,1], then its prime is [2,1]."""

        return ScaleStructure(repeating_subseq(self.intervals))

    @property
    def size(self) -> int:
        """Returns the number of intervals in the structure."""

        return len(self.intervals)

    @property
    def modulus(self) -> int:
        """Returns the modulus of a scale with this structure."""

        return sum(self.intervals)


@dataclass
class ScaleFunc:
    """A scale function is a pattern of coefficients along with a transposition
    which models a scale, such as C major or Gb mixolydian.

    Here is the scale function for C major: `[2,4,5,7,9,11,12] + 0`

    This function maps to the same set of pitches as the pitch class set
    `{0,2,4,5,7,9,11} mod 12`.

    `cmajor = ScaleFunc([2,4,5,7,9,11,12], 0)`

    Then you would access pitches in the scale by calling it with an index:

    `cmajor(4) == 7  # True`

    Evaluating the function at 0 will always yield the transposition of the function.

    Args:
        pattern (list[int]): The coefficient pattern, which determines how the input is scaled.
        transposition (int): The amount by which the output is offset.
    """

    ## DATA ##

    pattern: list[int]
    transposition: int = 0

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert len(set(self.pattern)) == len(
            self.pattern
        ), "Elements of pattern must be unique."
        assert self.pattern == sorted(
            self.pattern
        ), "Elements of pattern must be in ascending order."
        assert all(
            [harmonic > 0 for harmonic in self.pattern]
        ), "Elements of pattern must be greater than 0."

    @overload
    def __call__(self, n: int) -> int: ...

    @overload
    def __call__(self, n: Iterable[int]) -> list[int]: ...

    def __call__(self, n):
        return self.eval(n)

    def __add__(self, amount: int):
        self.transpose(amount)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Shifts the transposition of the scale function."""

        self.transposition += amount

    def rotate_mode_parallel(self, amount: int):
        """Rotates to a parallel mode, retaining the current transposition."""

        sub = self._rmap[amount % self.cardinality]
        new_pattern = [(pitch_class - sub) % self.modulus for pitch_class in self._rmap]
        new_pattern.sort()
        self.pattern = new_pattern[1:] + [self.modulus]

    def rotate_mode_relative(self, amount: int):
        """Rotates to a relative mode, changing the transposition."""

        self.transposition += self.eval(amount) - self.transposition
        self.rotate_mode_parallel(amount)

    def eval_rot(self, n: int) -> int:
        """Evaluates the scale function and then rotates to the relative mode
        that's centered on the evaluated pitch."""

        eval_result = self.eval(n)
        self.rotate_mode_relative(n)

        return eval_result

    ## GENERATE ##

    def compose(self, other: ScaleFunc) -> ScaleFunc:
        """Composes this scale function with another."""

        transposition = self.eval(other.eval(0))
        cardinality = (
            self.cardinality
            * other.cardinality
            // math.gcd(self.cardinality, other.modulus)
        )
        pattern = [
            chroma - transposition
            for chroma in self.eval(other.eval(range(1, cardinality + 1)))
        ]

        return ScaleFunc(pattern, transposition)

    def to_pcset(self) -> PitchClassSet:
        """Returns the pitch class set corresponding to this scale function."""

        return self.structure.stamp_to_pcset(self.transposition)

    ## ANALYZE ##

    @overload
    def eval(self, n: int) -> int: ...

    @overload
    def eval(self, n: Iterable[int]) -> list[int]: ...

    def eval(self, n: int | Iterable[int]) -> None | list[int] | int:
        """Evaluates the scale function.

        The object itself can be called like a function, yielding this evaluation.

        >>> scale = ScaleFunc([2,3,5,7,9,10,12],2)
        >>> scale(6)
        12

        You can also evaluate a list of integers:

        >>> scale([1,3,4,6])
        [4,7,9,12]
        """

        if isinstance(n, int):
            return self._eval(n)
        if isinstance(n, Iterable):
            return [self._eval(i) for i in n]
        return None

    def _eval(self, n: int) -> int:
        r = n % len(self.pattern)
        q = int((n - r)) / self.cardinality

        # Returns quotient * modulus + remainder + transposition
        return int(q * self.modulus + self._rmap[r]) + self.transposition

    def count_transpositions(self) -> int:
        """Counts the number of unique transpositions of this scale function."""

        return self.structure.count_transpositions()

    def count_modes(self) -> int:
        """Counts the number of distinct modes of this scale function."""

        return self.structure.count_modes()

    def maps_to_pitch(self, pitch: int) -> bool:
        """Returns true if this scale function has an input that maps to `pitch`."""

        r = (pitch - self.transposition) % self.modulus

        return True if r in self._rmap else False

    @overload
    def index(self, pitch: int) -> int: ...

    @overload
    def index(self, pitch: list[int]) -> list[int]: ...

    def index(self, pitch: int | list[int]) -> None | list[int] | int:
        """Returns the index that maps to `pitch` in this scale function.

        Example, the input that produces the pitch 25 from the scale function
        `[2,4,5,7,9,11,12] + 4` is 12.

        You can also check the indexes of a list of integers."""

        if isinstance(pitch, int):
            return self._index(pitch)
        if isinstance(pitch, list):
            return [self._index(p) for p in pitch]
        return None

    def _index(self, pitch: int) -> int:
        assert self.maps_to_pitch(pitch), "Scale function must map to pitch."
        r = (pitch - self.transposition) % self.modulus

        return self._rmap.index(r) + (
            ((pitch - self.transposition) // self.modulus) * self.cardinality
        )

    @property
    def modulus(self) -> int:
        """Returns the modulus of the scale function."""

        return self.pattern[-1]

    @property
    def cardinality(self) -> int:
        """Returns the length of the function's coefficient pattern."""

        return len(self.pattern)

    @property
    def structure(self) -> ScaleStructure:
        """Returns the structure of the corresponding scale."""

        return ScaleStructure(cycle_diff(self._rmap, self.modulus, 0))

    @property
    def _rmap(self) -> list[int]:  # residue map
        return [0] + self.pattern[:-1]


def normalize_interval(interval: int, mod: int) -> int:
    """Converts a member of an interval class to its smallest representative."""

    return interval if interval < mod - interval else mod - interval


def melodic_interval_class(pclass1: int, pclass2: int, modulus: int) -> int:
    """Returns the melodic interval class between one pitch class and another."""

    return (pclass2 - pclass1) % modulus


def harmonic_interval_class(pclass1: int, pclass2: int, modulus: int) -> int:
    """Returns the harmonic interval class between two pitch classes."""

    return normalize_interval(
        melodic_interval_class(pclass1, pclass2, modulus), modulus
    )
