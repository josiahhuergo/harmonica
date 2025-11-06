"""Objects and algorithms for modelling time."""

from ._event import *
from ._timefunc import *

__all__ = [
    # event
    "Event",
    "Note",
    "ScaleChange",
    "Clip",
    "NoteClip",
    # note_gen
    "block_chords",
    "mono_line",
    # scale_gen
    "scale_changes",
    # timefunc
    "TimeFunc",
]
