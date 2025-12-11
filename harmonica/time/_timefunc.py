from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Self, overload

from harmonica.time._event._clip import DrumClip
from harmonica.time._event._event import DrumEvent
from harmonica.utility import GMDrum, Mixed


@dataclass
class TimeFunc:
    """Time function!"""

    ## DATA ##

    pattern: list[Mixed]
    offset: Mixed = Mixed(0)

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert len(set(self.pattern)) == len(
            self.pattern
        ), "Elements of pattern must be unique."
        assert self.pattern == sorted(
            self.pattern
        ), "Elements of pattern must be in ascending order."
        assert all(
            [harmonic > 0 for harmonic in self.pattern]
        ), "Elements of pattern must be greater than 0."

    def __call__(self, n):
        return self.eval(n)

    def __add__(self, amount: Mixed):
        return self.shift(amount)

    ## TRANSFORM ##

    def shift(self, amount: Mixed) -> TimeFunc:
        """Shifts the offset of the time function."""

        return TimeFunc(self.pattern, self.offset + amount)

    def stretch(self, factor: Mixed) -> TimeFunc:
        """Scales the pattern by factor."""

        pattern = [value * factor for value in self.pattern]

        return TimeFunc(pattern, self.offset)

    def trunc(self, duration: Mixed) -> TimeFunc:
        """Truncates the pattern of the time function."""

        onsets = self.in_range(Mixed(0), Mixed(duration))
        offset = onsets[0]
        pattern = [onset - offset for onset in onsets]
        pattern = pattern[1:] + [duration]

        return TimeFunc(pattern, offset)

    def concat(self, other: TimeFunc) -> TimeFunc:
        """Concatenates another time function to create a compound pattern."""

        onsets = self.in_range(Mixed(0), Mixed(self.modulus))
        other_onsets = other.in_range(Mixed(0), Mixed(other.modulus))
        other_onsets = [onset + self.modulus for onset in other_onsets]
        onsets.extend(other_onsets)

        offset = onsets[0]
        pattern = [onset - offset for onset in onsets]
        pattern = pattern[1:] + [self.modulus + other.modulus]

        return TimeFunc(pattern, offset)

    def pad(self, pad_onset: Mixed, pad_dur: Mixed) -> TimeFunc:
        """Pads the pattern with silence."""

        onsets = self.in_range(Mixed(0), Mixed(self.modulus))
        unshifted = [onset for onset in onsets if onset < pad_onset]
        shifted = [onset + pad_dur for onset in onsets if onset >= pad_onset]
        new_onsets = unshifted + shifted

        offset = new_onsets[0]
        pattern = [onset - offset for onset in new_onsets]
        pattern = pattern[1:] + [self.modulus + pad_dur]

        return TimeFunc(pattern, offset)

    def pad_tail(self, pad_dur: Mixed) -> TimeFunc:
        """Pads the end of the pattern with silence."""

        return self.pad(self.modulus, pad_dur)

    ## ANALYZE ##

    @overload
    def eval(self, n: int) -> Mixed: ...
    @overload
    def eval(self, n: Iterable[int]) -> list[Mixed]: ...

    def eval(self, n: int | Iterable[int]) -> Mixed | list[Mixed]:
        if isinstance(n, int):
            return self._eval(n)
        if isinstance(n, Iterable):
            return [self._eval(i) for i in n]

    def _eval(self, n: int) -> Mixed:
        q = n // self.period
        r = n % self.period
        return q * self.modulus + self._rmap[r] + self.offset

    def in_range(self, lower: Mixed, upper: Mixed) -> list[Mixed]:
        """
        Returns list of all values f(x) such that lower <= f(x) < upper.
        """

        def get_bounds(f: TimeFunc, start: Mixed, stop: Mixed) -> tuple:
            lower_bound = 0
            upper_bound = 0

            x = 0

            if start <= f.eval(x):
                while True:
                    x -= 1
                    if not start <= f.eval(x):
                        lower_bound = x + 1
                        break
            else:
                while True:
                    x += 1
                    if start <= f.eval(x):
                        lower_bound = x
                        break

            x = 0

            if f.eval(x) < stop:
                while True:
                    x += 1
                    if not f.eval(x) < stop:
                        upper_bound = x - 1
                        break
            else:
                while True:
                    x += 1
                    if f.eval(x) < stop:
                        upper_bound = x
                        break

            return (lower_bound, upper_bound)

        low, high = get_bounds(self, lower, upper)

        return self.eval(range(low, high + 1))

    @property
    def modulus(self) -> Mixed:
        """Returns the modulus of the time function, representing the duration of the pattern."""

        return self.pattern[-1]

    @property
    def period(self) -> int:
        """Returns the period of the time function, which is the length of its pattern."""

        return len(self.pattern)

    @property
    def _rmap(self) -> list[Mixed]:  # residue map
        return [Mixed(0)] + self.pattern[:-1]

    ## PREVIEW ##

    def to_clip(self, duration: Mixed, drum: int = GMDrum.Claves) -> DrumClip:
        return DrumClip(
            [DrumEvent(onset, drum) for onset in self.in_range(Mixed(0), duration)]
        )
