"""Objects and algorithms pertaining to velocity / volume."""

from dataclasses import dataclass
from itertools import accumulate
from math import floor

from harmonica.utility._mixed import Mixed


@dataclass
class VelocityFunc:
    duration: int
    resolution: Mixed
    subdivisions: list[list[int]]
    velocities: list[Mixed]
    offset: Mixed

    def __post_init__(self):
        assert (
            self.duration % self.resolution == 0
        ), "Duration must be a multiple of resolution."

        assert (
            self.offset % self.resolution == 0
        ), "Offset must be a multiple of resolution."

        assert all(
            [sum(parts) == self.duration for parts in self.subdivisions]
        ), "Sum of parts in each subdivision level must be equal to duration."

        assert all(
            [0 <= velocity <= 1 for velocity in self.velocities]
        ), "Velocities must be between 0 and 1."

    def evaluate(self, t: Mixed) -> Mixed:
        """Take an onset time t and return a velocity value.
        Naive algorithm that assumes t is a multiple of resolution."""

        # assert (
        #     t % self.resolution == 0
        # ), "Evaluated time t must be a multiple of resolution."

        # For now, I will just round t down to a multiple of resolution.
        t = floor(t / self.resolution) * self.resolution

        remainder = (t + self.offset) % self.dur_in_beats

        for i, subdiv_level in enumerate(self._subdiv_onsets()):
            for onset_numerator in subdiv_level:
                if (onset_numerator * self.resolution) == remainder:
                    return self.velocities[i]

        return Mixed()

    def _subdiv_onsets(self) -> list[list[int]]:
        """Transform partitions into onsets that can be compared against while evaluating."""

        subdivs = [[0] + list(accumulate(subdiv[:-1])) for subdiv in self.subdivisions]

        result = [subdivs[0]]

        for i, subdiv in enumerate(subdivs[1:]):
            result.append([onset for onset in subdiv if onset not in subdivs[i]])

        return result

    @property
    def dur_in_beats(self) -> Mixed:
        return Mixed(self.duration) * self.resolution
