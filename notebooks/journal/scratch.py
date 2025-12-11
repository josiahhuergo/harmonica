from itertools import chain, product, islice
from more_itertools import powerset
from typing import Iterator

from harmonica.pitch._pitchset import PitchSet
from harmonica.pitch._scales import PitchClassSet


def list_voicings_in_range(
    pcset: PitchClassSet, lower_bound: int, upper_bound: int
) -> Iterator[PitchSet]:
    """Yields all pitch sets that can be derived from a pitch class set in a range of pitches,
    assuming each pitch class appears at least once in each pitch set."""

    # List out each occurrence of each pitch class within bounds
    in_bounds_pitches_for_each_pc = (
        (p for p in range(lower_bound, upper_bound + 1) if p % pcset.modulus == pc)
        for pc in pcset.pitch_classes
    )

    for pitches in product(
        *(
            islice(powerset(in_bound_pitches), 1, None)
            for in_bound_pitches in in_bounds_pitches_for_each_pc
        )
    ):
        yield PitchSet(list(chain(*pitches)))


print(list(list_voicings_in_range(PitchClassSet([0, 4, 7], 12), 21, 108)))
