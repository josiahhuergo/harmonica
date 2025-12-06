from fractions import Fraction
from typing import Any, Optional, Self, Sequence, overload


class Mixed(Fraction):
    """A Fraction subclass that supports mixed fraction notation."""

    @overload
    def __new__(cls, value: int = 0, denominator: Optional[int] = None) -> Self: ...

    @overload
    def __new__(cls, value: float) -> Self: ...

    @overload
    def __new__(cls, value: str) -> Self: ...

    @overload
    def __new__(cls, value: Fraction) -> Self: ...

    def __new__(
        cls, value: int | float | str | Fraction = 0, denominator: Optional[int] = None
    ) -> Self:
        """
        Create a mixed fraction from various inputs:
        - Mixed("16 7/16") - from mixed fraction string
        - Mixed("7/16") - from simple fraction string
        - Mixed(5) - from integer
        - Mixed(3.5) - from float
        - Mixed(3, 4) - from numerator and denominator
        """
        if isinstance(value, str):
            # Parse mixed fraction string like "16 7/16" or simple fraction "7/16"
            value = value.strip()
            if " " in value:
                # Mixed fraction format
                whole_part, frac_part = value.split(" ", 1)
                whole = int(whole_part)
                frac = Fraction(frac_part)

                # Convert to improper fraction
                if whole < 0:
                    converted = Fraction(whole) - frac
                else:
                    converted = Fraction(whole) + frac

                # Use parent class with the converted fraction's numerator and denominator
                return super().__new__(cls, converted.numerator, converted.denominator)
            else:
                # Regular fraction string - convert first
                converted = Fraction(value)
                return super().__new__(cls, converted.numerator, converted.denominator)
        elif isinstance(value, Fraction):
            # Convert Fraction to MixedFraction
            return super().__new__(cls, value.numerator, value.denominator)
        elif isinstance(value, float):
            # Convert float to Fraction first
            converted = Fraction(value)
            return super().__new__(cls, converted.numerator, converted.denominator)

        # Use parent class to create the fraction (int or int with denominator)
        return super().__new__(cls, value, denominator)

    # Arithmetic operations that return MixedFraction
    def _make_mixed(self, result):
        """Convert a Fraction result to MixedFraction."""
        if isinstance(result, Fraction):
            return type(self)(result.numerator, result.denominator)
        # For operations that return int or float, return as-is
        return result

    def __add__(self, other):
        result = super().__add__(other)
        return self._make_mixed(result)

    def __radd__(self, other):
        result = super().__radd__(other)
        return self._make_mixed(result)

    def __sub__(self, other):
        result = super().__sub__(other)
        return self._make_mixed(result)

    def __rsub__(self, other):
        result = super().__rsub__(other)
        return self._make_mixed(result)

    def __mul__(self, other):
        result = super().__mul__(other)
        return self._make_mixed(result)

    def __rmul__(self, other):
        result = super().__rmul__(other)
        return self._make_mixed(result)

    def __truediv__(self, other):
        result = super().__truediv__(other)
        return self._make_mixed(result)

    def __rtruediv__(self, other):
        result = super().__rtruediv__(other)
        return self._make_mixed(result)

    def __floordiv__(self, other):
        result = super().__floordiv__(other)
        return self._make_mixed(result)

    def __rfloordiv__(self, other):
        result = super().__rfloordiv__(other)
        return self._make_mixed(result)

    def __mod__(self, other):
        result = super().__mod__(other)
        return self._make_mixed(result)

    def __rmod__(self, other):
        result = super().__rmod__(other)
        return self._make_mixed(result)

    def __pow__(self, other):
        result = super().__pow__(other)
        return self._make_mixed(result)

    def __rpow__(self, other):
        result = super().__rpow__(other)
        return self._make_mixed(result)

    def __neg__(self):
        result = super().__neg__()
        return self._make_mixed(result)

    def __pos__(self):
        result = super().__pos__()
        return self._make_mixed(result)

    def __abs__(self):
        result = super().__abs__()
        return self._make_mixed(result)

    def __str__(self):
        """Return string representation as mixed fraction."""
        if abs(self.numerator) < abs(self.denominator):
            # Proper fraction, return as-is
            return f"{self.numerator}/{self.denominator}"

        # Convert to mixed fraction
        whole = self.numerator // self.denominator
        remainder = abs(self.numerator % self.denominator)

        if remainder == 0:
            # Whole number
            return str(whole)
        else:
            # Mixed fraction
            return f"{whole} {remainder}/{self.denominator}"

    def __repr__(self):
        """Return representation showing the class."""
        return f"Mixed('{str(self)}')"
