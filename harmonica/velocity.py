from __future__ import annotations
from dataclasses import dataclass
from itertools import cycle
from math import floor

from harmonica.utility._mixed import Mixed
from harmonica.utility._utility import rotate


@dataclass
class VelocityFunc:
    """A cyclic pattern of velocities that can be used to impose
    a rhythmic stress pattern over a clip."""

    pattern: list[int]
    resolution: Mixed

    def __post_init__(self):
        assert all(
            [velocity_index >= 0 for velocity_index in self.pattern]
        ), "Numbers in pattern must be positive."

        assert self.resolution > 0, "Time resolution must be positive."

    def __call__(self, t: Mixed, velocities: list[Mixed]):
        self.evaluate(t, velocities)

    ## TRANSFORM ##

    def shift(self, amount: int) -> VelocityFunc:
        """Rotates the pattern of the velocity function."""

        return VelocityFunc(rotate(self.pattern, amount), self.resolution)

    def stretch(self, factor: Mixed) -> VelocityFunc:
        """Scales the time resolution."""

        return VelocityFunc(self.pattern, self.resolution * factor)

    def stretch_to_res(self, new_res: Mixed) -> VelocityFunc:
        """Sets a new time resolution."""

        return VelocityFunc(self.pattern, new_res)

    def stretch_to_dur(self, new_dur_in_beats: Mixed) -> VelocityFunc:
        """Adjusts the time resolution to fit the pattern to a specific duration (in beats)."""

        return self.stretch(new_dur_in_beats / self.dur_in_units)

    def truncate(self, new_dur_in_beats: Mixed) -> VelocityFunc:
        """Truncates the velocity pattern to a new duration (in beats)."""

        new_dur_units = int(new_dur_in_beats / self.resolution)

        new_pattern = []

        pattern_cycle = cycle(self.pattern)

        for _ in range(new_dur_units):
            new_pattern.append(next(pattern_cycle))

        return VelocityFunc(new_pattern, self.resolution)

    def concat(self, other: VelocityFunc) -> VelocityFunc:
        """Concatenate this pattern with another, retaining the current time resolution."""

        return VelocityFunc(self.pattern + other.pattern, self.resolution)

    ## ANALYZE ##

    def evaluate(self, t: Mixed, velocities: list[Mixed]) -> Mixed:
        """Returns a velocity value corresponding to an onset time `t`."""

        assert (
            len(velocities) == max(self.pattern) + 1
        ), "Velocities list must contain enough values for pattern to map to."

        # Quantize t to time resolution
        t_units = floor(t / self.resolution)

        index = self.pattern[t_units % self.dur_in_units]

        return velocities[index]

    @property
    def dur_in_units(self) -> int:
        return len(self.pattern)

    @property
    def dur_in_beats(self) -> Mixed:
        return self.resolution * self.dur_in_units

    @property
    def subdivision_depth(self) -> int:
        return max(self.pattern) - min(self.pattern)
