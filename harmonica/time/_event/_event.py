from typing import Self

from harmonica.pitch import PitchClassSet
from harmonica.utility import GMDrum, Mixed, Time


class Event:
    """An event is something that occurs at a specific point in time, called the onset."""

    onset: Mixed

    def __init__(self, onset: Time) -> None:
        self.onset = Mixed(onset)

    def __eq__(self, other: Self) -> bool:
        if self.onset == other.onset:
            return True
        else:
            return False

    def __repr__(self):
        return f"Event(onset={self.onset})"

    def set_onset(self, onset: Time) -> Self:
        self.onset = Mixed(onset)
        return self


class Note(Event):
    pitch: int
    duration: Mixed
    velocity: Mixed

    def __init__(
        self,
        pitch: int,
        onset: Time,
        duration: Time,
        velocity: Time = 1,
    ):
        duration = Mixed(duration)
        velocity = Mixed(velocity)

        assert (
            velocity >= 0 and velocity <= 1
        ), "Velocity must be a number between 0 and 1."

        super().__init__(onset)
        self.pitch = pitch
        self.duration = duration
        self.velocity = velocity

    def __repr__(self):
        return f"Note(onset={self.onset}, pitch={self.pitch}, duration={self.duration}, velocity={self.velocity})"


class DrumEvent(Event):
    drum: int
    velocity: Mixed

    def __init__(
        self,
        onset: Time,
        drum: int = GMDrum.LowWoodBlock,
        velocity: Time = Mixed(1),
    ) -> None:
        super().__init__(onset)
        self.drum = drum
        self.velocity = Mixed(velocity)

    def __repr__(self):
        return f"DrumEvent(onset={self.onset}, drum={GMDrum(self.drum).name}, velocity={self.velocity})"


class ScaleChange(Event):
    scale: PitchClassSet

    def __init__(self, onset: Time, scale: PitchClassSet) -> None:
        super().__init__(onset)
        self.scale = scale

    def __repr__(self):
        return f"ScaleChange(onset={self.onset}, scale={self.scale})"
