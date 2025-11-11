from __future__ import annotations
from dataclasses import dataclass, field
import math
from typing import Iterable, overload


@dataclass
class PitchFunc:
    """A pitch function is a pattern of pitches along with a transposition
    which models an infinite sequence of pitches."""

    ## DATA ##

    pattern: list[int]
    transposition: int = field(default=0)

    @overload
    def __call__(self, n: int) -> int: ...
    @overload
    def __call__(self, n: Iterable[int]) -> list[int]: ...

    def __call__(self, n: int | Iterable[int]) -> None | int | list[int]:
        if isinstance(n, int):
            return self.eval(n)
        elif isinstance(n, Iterable):
            return self.eval(n)
        return None

    def __add__(self, amount: int):
        self.transpose(amount)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Shifts the transposition of the pitch function."""

        self.transposition += amount

    ## GENERATE ##

    def compose(self, other: PitchFunc) -> PitchFunc:
        """Composes this pitch function with another."""

        transposition = self.eval(other.eval(0))
        size = self.period * other.period // math.gcd(self.period, other.modulus)
        pattern = [
            chroma - transposition
            for chroma in self.eval(other.eval(range(1, size + 1)))
        ]

        return PitchFunc(pattern, transposition)

    ## ANALYZE ##

    @overload
    def eval(self, n: int) -> int: ...
    @overload
    def eval(self, n: Iterable[int]) -> list[int]: ...

    def eval(self, n: int | Iterable[int]) -> None | list[int] | int:
        """Evaluates the pitch function.

        The object itself can be called like a function, yielding this evaluation.

        >>> func = PitchFunc([2,3,5,7,9,10,12],2)
        >>> func(6)
        12

        You can also evaluate a list of integers:

        >>> func([1,3,4,6])
        [4,7,9,12]
        """

        if isinstance(n, int):
            return self._eval(n)
        if isinstance(n, Iterable):
            return [self._eval(i) for i in n]
        return None

    def _eval(self, n: int) -> int:
        r = n % len(self.pattern)
        q = int((n - r)) / self.period

        # Returns quotient * modulus + remainder + transposition
        return int(q * self.modulus + self._rmap[r]) + self.transposition

    def in_range(self, lower: int, upper: int) -> list[int]:
        """
        Returns list of all values f(x) such that lower <= f(x) <= upper.
        """

        def get_bounds(f: PitchFunc, start: int, stop: int) -> tuple:
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
    def modulus(self) -> int:
        """Returns the modulus of the pitch function."""

        return self.pattern[-1]

    @property
    def period(self) -> int:
        """Returns the size of the pattern."""

        return len(self.pattern)

    @property
    def _rmap(self) -> list[int]:  # residue map
        return [0] + self.pattern[:-1]
