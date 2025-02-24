from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

from harmonica.utility import cumsum

if TYPE_CHECKING:
    from harmonica.chord import PitchSet

@dataclass
class PitchSetShape:
    """A sequence of positive intervals that describes the intervallic shape of a pitch set."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert not any(
            [interval <= 0 for interval in self.intervals]
        ), 'Intervals in pitch set shape must be greater than 0.'

    def __getitem__(self, item: int) -> int:
        # Access pitch set shape like a list for convenience.
        return self.intervals[item]

    ## GENERATE ##

    def stamp(self, lowest_pitch: int) -> 'PitchSet':
        """Constructs a pitch set using the shape of intervals."""
        
        from harmonica.chord import PitchSet

        return PitchSet(cumsum(self.intervals, lowest_pitch))
    
    ## ANALYZE
    
    @property
    def span(self) -> int:
        """How many semitones the shape spans."""

        return sum(self.intervals)

    ## LISTEN ##
    
    def play(self, dur: Fraction = Fraction(6), pitch: int = 60):
        """Plays the pitch set shape real time as MIDI. 
        To do so, the shape is stamped at `ref_pitch` and then played."""
        
        self.stamp(pitch).play(dur)