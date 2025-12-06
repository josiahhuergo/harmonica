from dataclasses import dataclass
from typing import TYPE_CHECKING

from harmonica.utility import cumsum

if TYPE_CHECKING:
    from harmonica.pitch import PitchSet


@dataclass
class PitchSetShape:
    """A sequence of positive intervals that describes the intervallic shape of a pitch set."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert not any(
            [interval <= 0 for interval in self.intervals]
        ), "Intervals in pitch set shape must be greater than 0."

    def __getitem__(self, item: int) -> int:
        # Access pitch set shape like a list for convenience.
        return self.intervals[item]

    ## GENERATE ##

    def stamp(self, lowest_pitch: int) -> "PitchSet":
        """Constructs a pitch set using the shape of intervals."""

        from harmonica.pitch import PitchSet

        return PitchSet(cumsum(self.intervals, lowest_pitch))

    ## ANALYZE

    @property
    def span(self) -> int:
        """How many semitones the shape spans."""

        return sum(self.intervals)

    ## PREVIEW ##

    def preview(self, bass: int = 60):
        """Previews the pitch set shape."""

        self.stamp(bass).preview()
