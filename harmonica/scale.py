"""Objects and algorithms pertaining to scales."""

from __future__ import annotations
from multimethod import multimethod
from dataclasses import dataclass
from itertools import combinations
import math

from harmonica.util import cumsum, cycle_cumsum, cycle_diff, repeating_subseq, rotate

@dataclass
class PitchClassSet:
    """A set of pitch classes used to represent a scale, without respect to a root.
    
    `{0,2,4,5,7,9,11} mod 12`, or `PClassSet([0,2,4,5,7,9,11], 12)`, represents the pitches mapped to
    by C major, D dorian, E phrygian, etc."""
    
    ## DATA ##

    pitch_classes: list[int]
    modulus: int

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert self.modulus > 0, "Modulus must be a positive integer."
        assert self.pitch_classes == list(
            sorted(self.pitch_classes)
        ), "Pitch classes must be in order."
        assert len(self.pitch_classes) == len(set(self.pitch_classes)), "Pitch classes must be unique."
        assert all(
            [0 <= pitch < self.modulus for pitch in self.pitch_classes]
        ), "Pitch classes must be between 0 and modulus - 1."
    
    def __getitem__(self, item: int | slice) -> int | list[int]:
        if isinstance(item, int):
            return self.pitch_classes[item]
        if isinstance(item, slice):
            return self.pitch_classes[item.start:item.stop:item.step]
    
    def __add__(self, other: int) -> PitchClassSet:
        return self.transposed(other)
    
    def a() -> int:
        return True
    
    def __sub__(self, other: int) -> PitchClassSet:
        return self.transposed(-other)
    
    ## TRANSFORMATION ##

    def transpose(self, amount: int):
        """Transposes the pitch classes in the set using modular arithmetic."""

        self.pitch_classes = [(pc + amount) % self.modulus for pc in self.pitch_classes]
        self.pitch_classes.sort()
    
    def transposed(self, amount: int) -> PitchClassSet:
        """Returns a transposed pitch class set."""

        pitch_classes = [(pc + amount) % self.modulus for pc in self.pitch_classes]
        pitch_classes.sort()

        return PitchClassSet(pitch_classes, self.modulus)
    
    def normalize(self, pitch_class: int):
        """Transposes the pitch classes in the set so 0 is present."""

        assert pitch_class in self.pitch_classes

        self.transpose(-pitch_class)

    def normalized(self, pitch_class: int) -> PitchClassSet:
        """Returns a normalized pitchset."""

        assert pitch_class in self.pitch_classes

        return self.transposed(-pitch_class)

    ## ANALYSIS ##

    @property
    def interval_network(self) -> list[list]:

        # RESEARCH FURTHER

        domain = list(combinations(self.pitch_classes, 2))
        rang = [harmonic_interval_class(i[0], i[1], self.modulus) for i in domain]

        return [[]] #list(zip(domain, rang))

    @property
    def interval_vector(self) -> list[int]:

        # RESEARCH FURTHER

        ic_vector = [0] * (self.modulus // 2)
        for scalar_iclass in self.interval_network:
            if scalar_iclass[1] != 0:
                ic_vector[scalar_iclass[1] - 1] += 1
        return [2] #tuple(ic_vector)
    
    def scale_function(self, root: int) -> ScaleFunc:
        """Returns a scale function that maps to the same pitches as this pitch class set.
        
        For example, if we have a pitch class set representing D major (and its modes) 
        `{1,2,4,6,7,9,11} mod 12` and we specify 6 as the root then this will return 
        `[1,3,5,7,8,10,12] + 6`."""
        
        return ScaleFunc(self.normalized(root)[1:] + [self.modulus], min(self.pitch_classes))
    
    @property
    def size(self) -> int:
        """The number of pitch classes in the set."""

        return len(self.pitch_classes)
    
    @property
    def shape(self, start_index: int = 0) -> ScaleShape:
        """The intervallic shape of the pitch class set, by default starting
        from the lowest pitch class in the set."""

        intervals = cycle_diff(self.pitch_classes, self.modulus, start_index)

        return ScaleShape(intervals)

@dataclass
class PCSetWithRoot(PitchClassSet):
    """A pitch class set with one pitch class specified as the root.
    
    `{0,2,4,5,7,9,11} mod 12 root 4`, or `RootedPCSet([0,2,4,5,7,9,11], 12, 4)` 
    would represent the same set of pitch classes as C major, D dorian, E phrygian, etc.,
    but the root specifies that it represents E phrygian in particular."""

    ## DATA ##

    root: int

    ## MAGIC METHODS ##

    def __post_init__(self):
        super().__post_init__()
        assert self.root in self.pitch_classes, 'Root must be in pitch class set.'
    
    ## TRANSFORM ##

    def rotate_mode_relative(self, amount: int):
        """Shifts the root of the pitch class set, accessing a relative mode.
        
        `{0,2,4,5,7,9,11} mod 12 root 4` rotated this way by 2 would shift the
        root up to the pitch class 2 spaces clockwise from the current root. 
        This would yield `{0,2,4,5,7,9,11} mod 12 root 7`, because 7 is 2 spaces
        clockwise from 4 in this pitch class set."""

        i = (self.pitch_classes.index(self.root) + amount) % self.size
        self.root = self.pitch_classes[i]
    
    def rotate_mode_parallel(self, amount: int):
        """Rotates the shape of the pitch class set around the root.
        
        `{0,2,4,5,7,9,11} mod 12 root 4` rotated this way by 2 would take the
        shape, `[1,2,2,2,1,2,2]`, and rotate it by 2 to yield the shape of mixolydian,
        `[2,2,1,2,2,1,2]`, which stamped onto pitch class 4 yields 
        `{1,3,4,6,8,9,11} mod 12 root 4`."""

        shape = self.shape
        shape.rotate(amount)
        new_pcset = shape.stamp_to_rooted_pcset(self.root)
        self.pitch_classes = new_pcset.pitch_classes

    def transpose(self, amount: int):
        """Transposes the pitch class set."""

        self.pitch_classes = [(pc + amount) % self.modulus for pc in self.pitch_classes]
        self.pitch_classes.sort()
        self.root = (self.root + amount) % self.modulus
    
    ## ANALYZE ##

    @property
    def shape(self) -> ScaleShape:
        """The intervallic shape of the pitch class set, starting from the root."""

        intervals = cycle_diff(self.pitch_classes, self.modulus, self.pitch_classes.index(self.root))

        return ScaleShape(intervals)

@dataclass
class ScaleShape:
    """A sequence of intervals that describes the circular intervallic shape of a pitch class set."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert all(
            [0 < interval for interval in self.intervals]
        ), "Intervals in pitch class set shape must be positive."
    
    def __getitem__(self, item: int) -> int | list[int]:
        return self.intervals[item]
    
    ## TRANSFORM ##
    
    def rotate(self, amount: int):
        """Rotates the intervals in the scale shape."""

        self.intervals = rotate(self.intervals, amount)

    ## GENERATE ##

    def stamp_to_pcset(self, starting_pitch: int) -> PitchClassSet:
        """Creates a pitch class set by "stamping" this scale shape onto pitch class 
        space at the pitch class `starting_pitch`."""

        return PitchClassSet(cycle_cumsum(self.intervals, starting_pitch), self.modulus)

    def stamp_to_rooted_pcset(self, starting_pitch: int) -> PCSetWithRoot:
        """Creates a rooted pitch class set by "stamping" this scale shape onto pitch class 
        space at the pitch class `starting_pitch`."""

        return PCSetWithRoot(cycle_cumsum(self.intervals, starting_pitch), self.modulus, starting_pitch % self.modulus)
    
    def stamp_to_scale_func(self, transposition: int) -> ScaleFunc:
        """Creates a scale function whose pattern is constructed from this shape."""
        
        return ScaleFunc(cumsum(self.intervals)[1:], transposition)

    ## ANALYZE ##
    
    def count_transpositions(self) -> int:
        """Counts the number of unique transpositions that this scale would have
        when stamped."""

        return sum(repeating_subseq(self.intervals))
    
    def count_modes(self) -> int:
        """Counts the number of distinct modes that this scale would have when
        stamped."""

        return len(repeating_subseq(self.intervals))
    
    @property
    def size(self) -> int:
        """Returns the number of intervals in the shape."""

        return len(self.intervals)
    
    @property
    def modulus(self) -> int:
        """Returns the modulus of the scale shape."""

        return sum(self.intervals)

@dataclass 
class ScaleFunc:
    """A scale function is a pattern of pitches along with a transposition
    which models a scale key, such as C major or Gb mixolydian. 

    Here is the scale function for C major: `[2,4,5,7,9,11,12] + 0`
    
    This function maps to the same set of pitches as the pitch class set
    `{0,2,4,5,7,9,11} mod 12`.

    `cmajor = ScaleFunc([2,4,5,7,9,11,12], 0)`

    Then you would access pitches in the scale by calling it:

    `cmajor(4) == 7  # True`

    Args:
        pattern (list[int]): The scaling pattern, which determines how inputs are scaled.
        transposition (int): The amount by which the output is offset. 
    """

    ## DATA ##

    pattern: list[int]
    transposition: int = 0

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert len(set(self.pattern)) == len(self.pattern), 'Elements of pattern must be unique.'
        assert self.pattern == sorted(self.pattern), 'Elements of pattern must be in ascending order.'
        assert all([harmonic > 0 for harmonic in self.pattern]), 'Elements of pattern must be greater than 0.'
    
    def __call__(self, n: int) -> int:
        return self.eval(n)
    
    def __add__(self, amount: int):
        self.transpose(amount)

    ## TRANSFORM ##
    
    def transpose(self, amount: int):
        """Shifts the transposition of the scale function."""

        self.transposition += amount

    def rotate_mode_parallel(self, amount: int):
        """Rotates to a parallel mode, retaining the current transposition."""

        sub = self._rmap[amount % self.size]
        new_pattern = [
            (pitch_class - sub) % self.modulus for pitch_class in self._rmap
        ]
        new_pattern.sort()
        self.pattern = new_pattern[1:] + [self.modulus]
    
    def rotate_mode_relative(self, amount: int):
        """Rotates to a relative mode, changing the transposition."""

        self.transposition += (self(amount) - self.transposition)
        self.rotate_mode_parallel(amount)
    
    def eval_rot(self, n: int) -> int:
        """Evaluates the scale function and then rotates to the relative mode
        that's centered on the evaluated pitch."""

        eval = self.eval(n)
        self.rotate_mode_relative(n)

        return eval

    ## GENERATE ##
    
    def compose(self, other: ScaleFunc) -> ScaleFunc:
        """Composes this scale function with another."""

        # RESEARCH FURTHER

        new_t = other(self(0))
        new_period = (self.size * other.size) / math.gcd(self.modulus, other.modulus)

        return ScaleFunc(
            pattern = list(other(self(i)) - new_t for i in range(1, int(new_period) + 1)),
            transposition = new_t
        )
    
    def to_pcset(self) -> PitchClassSet:
        """Returns the pitch class set corresponding to this scale function."""

        return self.shape.stamp_to_pcset(self.transposition)
    
    ## ANALYZE ##

    def eval(self, n: int) -> int:
        """Evaluates the function with input n.
        
        The object itself can be called like a function, yielding this evaluation.
        ```
        >>> scale = ScaleFunc([2,3,5,7,9,10,12],2)
        >>> scale(6)
        12  
        ```"""

        r = n % len(self.pattern)
        q = int((n - r)) / self.size

        # Returns quotient * modulus + remainder + transposition
        return int(q * self.modulus + self._rmap[r]) + self.transposition
    
    def count_transpositions(self) -> int:
        """Counts the number of unique transpositions of this scale function."""

        return self.shape.count_transpositions()
    
    def count_modes(self) -> int:
        """Counts the number of distinct modes of the shape of this scale function."""

        return self.shape.count_modes()
    
    def maps_to_pitch(self, pitch: int) -> bool:
        """Returns true if this scale function has an input that maps to `pitch`."""

        r = (pitch - self.transposition) % self.modulus

        return True if r in self._rmap else False
    
    def index(self, pitch: int) -> bool:
        """Returns the index that maps to `pitch` in this scale function.
        
        Example, the input that produces the pitch 25 from the scale function 
        `[2,4,5,7,9,11,12] + 4` is 12."""

        assert self.maps_to_pitch(pitch), "Scale function must map to pitch."
        r = (pitch - self.transposition) % self.modulus

        return self._rmap.index(r) + (((pitch - self.transposition) // self.modulus) * self.size)
    
    @property
    def modulus(self) -> int:
        """Returns the modulus of the scale function."""

        return self.pattern[-1]

    @property
    def size(self) -> int:
        """Returns the size of the scaling pattern."""

        return len(self.pattern)
    
    @property
    def shape(self) -> ScaleShape:
        return ScaleShape(cycle_diff(self._rmap, self.modulus, 0))

    @property
    def _rmap(self) -> tuple[int, ...]:  # residue map
        return [0] + self.pattern[:-1]

def normalize_interval(interval: int, mod: int) -> int:
    # converts a member of an interval class to its smallest representative.
    # example: 5 and 7 are of the same interval class. if 5 was present, it'd stay
    # the same. but if 7 was present, it'd become 5.

    # RESEARCH FURTHER

    return interval if interval < mod - interval else mod - interval

def melodic_interval_class(pclass1: int, pclass2: int, modulus: int) -> int:
    """Returns the melodic interval class between one pitch class and another."""

    # RESEARCH FURTHER

    return (pclass2 - pclass1) % modulus

def harmonic_interval_class(pclass1: int, pclass2: int, modulus: int) -> int:
    """Returns the harmonic interval class between two pitch classes."""

    # RESEARCH FURTHER

    return normalize_interval(melodic_interval_class(pclass1, pclass2, modulus), modulus)