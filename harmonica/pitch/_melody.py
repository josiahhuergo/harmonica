"""Objects and algorithms pertaining to melodies."""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from harmonica.utility import cumsum, diff

__all__ = ["PitchSeq", "PitchSeqShape", "PCSequence", "PitchSeqSet"]


@dataclass
class PitchSeq:
    """A sequence of pitches used to represent a melody."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __getitem__(self, item: int) -> int:
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

    ## GENERATE ##

    def classify(self, modulus: int) -> PCSequence:
        """Converts the pitch sequence into a pitch class sequence."""

        assert modulus > 0, "Modulus must be positive."

        return PCSequence([pitch % modulus for pitch in self.pitches], modulus)

    ## PREVIEW ##

    def preview(self, bass: Optional[int] = None, duration: Fraction = Fraction(1)):
        """Previews the pitch sequence."""

        from harmonica.time import NoteClip, Clip, Note
        from fractions import Fraction

        onset = Fraction(0)
        transpose = 0
        if bass:
            transpose = bass - self[0]

        note_clip = NoteClip([])

        for pitch in self:
            note_clip.add_event(
                Note(pitch=pitch + transpose, duration=duration, onset=onset)
            )
            onset += duration

        Clip([note_clip]).preview()


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

        assert self.modulus > 0, "Modulus must be positive."

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
class PitchSeqSet:
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
