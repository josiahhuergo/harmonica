"""Objects and algorithms pertaining to melodies."""

from __future__ import annotations
from dataclasses import dataclass

from harmonica.util import cumsum, diff

@dataclass
class PitchSequence:
    """A sequence of pitches used to represent a melody."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __getitem__(self, item: int) -> int | list[int]:
        return self.pitches[item]
    
    def __len__(self) -> int:
        return len(self.pitches)
    
    def __add__(self, amount: int) -> PitchSequence:
        return PitchSequence([pitch + amount for pitch in self.pitches])
    
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
    def contour(self) -> PitchContour:
        """Returns the melodic contour of the pitch sequence."""

        return PitchContour(diff(self.pitches))

@dataclass
class PitchContour:
    """A sequence of intervals used to represent a melodic contour."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __getitem__(self, item: int) -> int:
        return self.intervals[item]
    
    def __len__(self) -> int:
        return len(self.pitches)
    
    ## GENERATE ##

    def stamp(self, starting_pitch: int) -> PitchSequence:
        """Produces a pitch sequence by "stamping" the contour at a given pitch."""

        return PitchSequence(cumsum(self.intervals, starting_pitch))
    
    ## ANALYZE ##

    @property
    def length(self) -> int:
        """Returns the length of the melodic shape."""

        return len(self.intervals)
    
@dataclass
class MelodicFunc:
    """A melodic function is a pattern of pitches along with a transposition
    which models a melodic pattern."""

    ## DATA ##

    pattern: list[int]
    transposition: int
    
    # RESEARCH FURTHER

@dataclass 
class PCSequence:
    """A sequence of pitch classes used to represent a whole class of pitch sequences."""

    ## DATA ##

    pitch_classes : list[int]
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

    pitch_sequences: list[PitchSequence]

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