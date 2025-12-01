from fractions import Fraction
from typing import Self

from harmonica.pitch import PitchClassSet


class Event:
    """An event is something that occurs at a specific point in time, called the onset."""

    onset: Fraction

    def __init__(self, onset: Fraction | int | str) -> None:
        if isinstance(onset, str | int):
            self.onset = Fraction(onset)
        elif isinstance(onset, Fraction):
            self.onset = onset

    def __eq__(self, other: Self) -> bool:
        if self.onset == other.onset:
            return True
        else:
            return False

    def __repr__(self):
        return f"Event(onset={self.onset})"

    def set_onset(self, onset: Fraction) -> Self:
        self.onset = onset
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
        super().__init__(onset)
        self.pitch = pitch

        if isinstance(duration, str | int):
            self.duration = Fraction(duration)
        elif isinstance(duration, Fraction):
            self.duration = duration

        if isinstance(velocity, str | int):
            self.velocity = Fraction(velocity)
        elif isinstance(velocity, Fraction):
            self.velocity = velocity

        assert (
            self.velocity >= 0 and self.velocity <= 1
        ), "Velocity must be a number between 0 and 1."

    def __repr__(self):
        return f"Note(onset={self.onset}, pitch={self.pitch}, duration={self.duration}, velocity={self.velocity})"


class ScaleChange(Event):
    scale: PitchClassSet

    def __init__(self, onset: Fraction | int | str, scale: PitchClassSet) -> None:
        super().__init__(onset)
        self.scale = scale

    def __repr__(self):
        return f"ScaleChange(onset={self.onset}, scale={self.scale})"
