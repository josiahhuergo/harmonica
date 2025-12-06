from typing import Self

from harmonica.pitch import PitchClassSet
from harmonica.utility import GMDrum, Mixed


class Event:
    """An event is something that occurs at a specific point in time, called the onset."""

    onset: Mixed

    def __init__(self, onset: Mixed) -> None:
        self.onset = onset

    def __eq__(self, other: Self) -> bool:
        if self.onset == other.onset:
            return True
        else:
            return False

    def __repr__(self):
        return f"Event(onset={self.onset})"

    def set_onset(self, onset: Mixed) -> Self:
        self.onset = onset
        return self


class Note(Event):
    pitch: int
    duration: Mixed
    velocity: Mixed

    def __init__(
        self,
        pitch: int,
        onset: Mixed,
        duration: Mixed,
        velocity: Mixed = Mixed(1),
    ):
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
        onset: Mixed,
        drum: int = GMDrum.LowWoodBlock,
        velocity: Mixed = Mixed(1),
    ) -> None:
        super().__init__(onset)
        self.drum = drum
        self.velocity = velocity

    def __repr__(self):
        return f"DrumEvent(onset={self.onset}, drum={GMDrum(self.drum).name}, velocity={self.velocity})"


class ScaleChange(Event):
    scale: PitchClassSet

    def __init__(self, onset: Mixed, scale: PitchClassSet) -> None:
        super().__init__(onset)
        self.scale = scale

    def __repr__(self):
        return f"ScaleChange(onset={self.onset}, scale={self.scale})"
