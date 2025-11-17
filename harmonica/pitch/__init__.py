"""Objects and algorithms pertaining to pitch, such as chords, scales and melodies."""

from ._scales import PitchClassSet, ScaleStructure, ScaleFunc
from ._pitchset import PitchSet
from ._pitchsetshape import PitchSetShape
from ._pitchfunc import PitchFunc
from ._changes import PitchSetSeq
from ._melody import PitchSeq, PitchSeqShape, PCSequence, PitchSeqSet

__all__ = [
    # _scale
    "PitchClassSet",
    "ScaleStructure",
    "ScaleFunc",
    # _chord
    "PitchSet",
    "PitchSetShape",
    # _pitchfunc
    "PitchFunc",
    # _changes
    "PitchSetSeq",
    # _melody
    "PitchSeq",
    "PitchSeqShape",
    "PCSequence",
    "PitchSeqSet",
]
