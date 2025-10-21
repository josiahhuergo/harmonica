"""Objects and algorithms pertaining to melodies."""

from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import Iterable, overload

from harmonica.timeline import Note, Timeline
from harmonica.utility import cumsum, diff

__all__ = ["PitchSeq", "PitchSeqShape", "PitchFunc", "PCSequence", "Polyphony"]


@dataclass
class PitchSeq:
    """A sequence of pitches used to represent a melody."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __getitem__(self, item: int) -> int | list[int]:
        return self.pitches[item]

    def __len__(self) -> int:
        return len(self.pitches)

    def __add__(self, amount: int) -> PitchSeq:
        return PitchSeq([pitch + amount for pitch in self.pitches])

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes the pitch sequence."""

        self.pitches = [pitch + amount for pitch in self.pitches]

    def normalize(self):
        """Transposes the pitch sequence so the lowest pitch is 0."""

        self.transpose(-min(self.pitches))

    ## ANALYZE ##

    @property
    def length(self) -> int:
        """Returns the length of the pitch sequence."""

        return len(self.pitches)

    @property
    def shape(self) -> PitchSeqShape:
        """Returns the sequence of intervals between successive pitches in the sequence."""

        return PitchSeqShape(diff(self.pitches))

    ## LISTEN ##

    def play(
        self, dur: Fraction = Fraction(1), bpm: int = 120, hang: Fraction = Fraction()
    ):
        """Plays the pitch sequence real time as MIDI.

        Each note will be `dur` long, which is 1 beat by default.

        There is an optional `hang` argument, which specifies how long the last note rings out.
        """

        tl = Timeline()
        tl.tempo = bpm

        for i in range(self.length - 1):
            tl.add_note(dur * i, self.pitches[i], dur)

        tl.add_note(dur * (self.length - 1), self.pitches[-1], dur + hang)

        tl.play_midi()


@dataclass
class PitchSeqShape:
    """A sequence of intervals used to describe the difference between successive
    pitches in a pitch sequence."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __getitem__(self, item: int) -> int:
        return self.intervals[item]

    def __len__(self) -> int:
        return len(self.intervals)

    ## GENERATE ##

    def stamp(self, starting_pitch: int) -> PitchSeq:
        """Produces a pitch sequence by "stamping" the shape at a given pitch."""

        return PitchSeq(cumsum(self.intervals, starting_pitch))

    ## ANALYZE ##

    @property
    def length(self) -> int:
        """Returns the length of the interval sequence."""

        return len(self.intervals)


@dataclass
class PitchFunc:
    """A pitch function is a pattern of pitches along with a transposition
    which models an infinite sequence of pitches."""

    ## DATA ##

    pattern: list[int]
    transposition: int = field(default=0)

    @overload
    def __call__(self, n: int) -> int: ...
    @overload
    def __call__(self, n: Iterable[int]) -> list[int]: ...

    def __call__(self, n):
        if isinstance(n, int):
            return self.eval(n)
        if isinstance(n, Iterable):
            return self.eval(n)

    def __add__(self, amount: int):
        self.transpose(amount)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Shifts the transposition of the scale function."""

        self.transposition += amount

    def eval_rot(self, n: int) -> int:
        """Evaluates the scale function and then rotates to the relative mode
        that's centered on the evaluated pitch."""

        eval = self.eval(n)
        self.rotate_mode_relative(n)

        return eval

    ## GENERATE ##

    def compose(self, other: PitchFunc) -> PitchFunc:
        """Composes this scale function with another."""

        transposition = self.eval(other.eval(0))
        size = self.size * other.size // math.gcd(self.size, other.modulus)
        pattern = [
            chroma - transposition
            for chroma in self.eval(other.eval(range(1, size + 1)))
        ]

        return PitchFunc(pattern, transposition)

    ## ANALYZE ##

    @overload
    def eval(self, n: int) -> int: ...
    @overload
    def eval(self, n: Iterable[int]) -> list[int]: ...

    def eval(self, n: int | Iterable[int]) -> int | list[int]:
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

    def _eval(self, n: int) -> int:
        r = n % len(self.pattern)
        q = int((n - r)) / self.size

        # Returns quotient * modulus + remainder + transposition
        return int(q * self.modulus + self._rmap[r]) + self.transposition

    @property
    def modulus(self) -> int:
        """Returns the modulus of the scale function."""

        return self.pattern[-1]

    @property
    def size(self) -> int:
        """Returns the size of the scaling pattern."""

        return len(self.pattern)

    @property
    def _rmap(self) -> list[int]:  # residue map
        return [0] + self.pattern[:-1]


@dataclass
class PCSequence:
    """A sequence of pitch classes used to represent a whole class of pitch sequences."""

    ## DATA ##

    pitch_classes: list[int]
    modulus: int

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert all(
            [0 <= pitch_class < self.modulus for pitch_class in self.pitch_classes]
        ), "Pitch classes must be between 0 and modulus - 1."

    def __getitem__(self, item: int) -> int:
        return self.pitch_classes[item]

    def __len__(self) -> int:
        return len(self.pitch_classes)

    ## ANALYZE ##

    @property
    def length(self) -> int:
        """Returns the length of the pitch class sequence."""

        return len(self.pitch_classes)


@dataclass
class Polyphony:
    """A set of pitch sequences, representing a polyphony of voices."""

    ## DATA ##

    pitch_sequences: list[PitchSeq]

    ## MAGIC METHODS ##

    def __len__(self) -> int:
        return len(self.pitch_sequences)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes all the pitch sequences in the set."""

        for pitch_sequence in self.pitch_sequences:
            pitch_sequence.transpose(amount)

    ## ANALYZE ##

    def all_lengths_equal(self) -> bool:
        """Returns true if all pitch sequences in the set are of the same length."""

        if len(self.pitch_sequences) == 0:
            return True

        length = self.pitch_sequences[0].length

        if all([x.length == length for x in self.pitch_sequences]):
            return True
        else:
            return False

    @property
    def size(self) -> int:
        """Returns the size of the set of pitch sequences."""

        return len(self.pitch_sequences)
