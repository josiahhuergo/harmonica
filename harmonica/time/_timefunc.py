from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, overload


@dataclass
class TimeFunc:
    """Time function!"""

    ## DATA ##

    pattern: list[Fraction]
    offset: Fraction = Fraction(0)

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
        self.eval(n)

    def __add__(self, amount: int):
        self.shift(amount)

    ## TRANSFORM ##

    def shift(self, amount: int):
        """Shifts the offset of the time function."""

        self.offset += amount

    ## ANALYZE ##

    @overload
    def eval(self, n: int) -> Fraction: ...
    @overload
    def eval(self, n: Iterable[int]) -> list[Fraction]: ...

    def eval(self, n: int | Iterable[int]) -> Fraction | list[Fraction]:
        if isinstance(n, int):
            return self._eval(n)
        if isinstance(n, Iterable):
            return [self._eval(i) for i in n]

    def _eval(self, n: int) -> Fraction:
        q = n // self.period
        r = n % self.period
        return q * self.modulus + self._rmap[r] + self.offset

    def in_range(self, lower: Fraction, upper: Fraction) -> list[Fraction]:
        """
        Returns list of all values f(x) such that lower <= f(x) <= upper.
        """

        def get_bounds(f: TimeFunc, start: Fraction, stop: Fraction) -> tuple:
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
                    if not f.eval(x) <= stop:
                        upper_bound = x - 1
                        break
            else:
                while True:
                    x += 1
                    if f.eval(x) <= stop:
                        upper_bound = x
                        break

            return (lower_bound, upper_bound)

        low, high = get_bounds(self, lower, upper)

        return self.eval(range(low, high + 1))

    @property
    def modulus(self) -> Fraction:
        """Returns the modulus of the time function."""

        return self.pattern[-1]

    @property
    def period(self) -> int:
        """Returns the period of the time function, which is the length of its pattern."""

        return len(self.pattern)

    @property
    def _rmap(self) -> list[Fraction]:  # residue map
        return [Fraction(0)] + self.pattern[:-1]
