from fractions import Fraction
from typing import Self

from harmonica.pitch import PitchClassSet
from harmonica.utility import GMDrum


class Event:
    """An event is something that occurs at a specific point in time, called the onset."""

    onset: Fraction

    def __init__(self, onset: Fraction | int | str) -> None:
        self.onset = Fraction(onset)

    def __eq__(self, other: Self) -> bool:
        if self.onset == other.onset:
            return True
        else:
            return False

    def __repr__(self):
        return f"Event(onset={self.onset})"

    def set_onset(self, onset: Fraction | int | str) -> Self:
        self.onset = Fraction(onset)
        return self


class Note(Event):
    pitch: int
    duration: Fraction
    velocity: Fraction

    def __init__(
        self,
        pitch: int,
        onset: Fraction | str | int,
        duration: Fraction | str | int,
        velocity: Fraction | str | int = 1,
    ):
        assert (
            self.velocity >= 0 and self.velocity <= 1
        ), "Velocity must be a number between 0 and 1."

        super().__init__(onset)
        self.pitch = pitch
        self.duration = Fraction(duration)
        self.velocity = Fraction(velocity)

    def __repr__(self):
        return f"Note(onset={self.onset}, pitch={self.pitch}, duration={self.duration}, velocity={self.velocity})"


class DrumEvent(Event):
    drum: int
    velocity: Fraction

    def __init__(
        self,
        onset: Fraction | int | str,
        drum: int = GMDrum.LowWoodBlock,
        velocity: Fraction | int | str = Fraction(1),
    ) -> None:
        super().__init__(onset)
        self.drum = drum
        self.velocity = Fraction(velocity)

    def __repr__(self):
        return f"DrumEvent(onset={self.onset}, drum={GMDrum(self.drum).name}, velocity={self.velocity})"


class ScaleChange(Event):
    scale: PitchClassSet

    def __init__(self, onset: Fraction | int | str, scale: PitchClassSet) -> None:
        super().__init__(onset)
        self.scale = scale

    def __repr__(self):
        return f"ScaleChange(onset={self.onset}, scale={self.scale})"
