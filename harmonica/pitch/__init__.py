"""Objects and algorithms pertaining to pitch, such as chords, scales and melodies."""

from ._scales import PitchClassSet, ScaleStructure, ScaleFunc
from ._pitchset import PitchSet
from ._pitchsetshape import PitchSetShape
from .melody import PitchFunc

__all__ = [
    # _scale
    "PitchClassSet",
    "ScaleStructure",
    "ScaleFunc",
    # _chord
    "PitchSet",
    "PitchSetShape",
    # melody
    "PitchFunc",
]
