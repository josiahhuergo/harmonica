from typing import Iterator

from more_itertools import powerset
from harmonica.pitch._scales import PitchClassSet


__all__ = ["find_pcset_supersets"]


def find_pcset_supersets(pitch_class_set: PitchClassSet) -> Iterator[PitchClassSet]:
    complement = set(range(pitch_class_set.modulus)) - set(
        pitch_class_set.pitch_classes
    )
    pcset_powerset = powerset(complement)

    for other_pitch_classes in pcset_powerset:
        yield PitchClassSet(
            pitch_classes=sorted(
                pitch_class_set.pitch_classes + list(other_pitch_classes)
            ),
            modulus=pitch_class_set.modulus,
        )
