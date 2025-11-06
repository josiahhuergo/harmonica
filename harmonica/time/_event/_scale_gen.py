from fractions import Fraction
from itertools import cycle
from harmonica.pitch import PitchClassSet
from ._clip import Clip, ScaleChangeClip
from ._event import ScaleChange


def scale_changes(
    change_seq: list[PitchClassSet],
    delta_seq: list[Fraction],
    clip_dur: Fraction,
) -> ScaleChangeClip:
    change_events: list[ScaleChange | Clip[ScaleChange]] = []

    changes = cycle(change_seq)
    deltas = cycle(delta_seq)
    onset = Fraction(0)

    while onset < clip_dur:
        scale = next(changes)
        change_events.append(ScaleChange(onset, scale))
        onset += next(deltas)

    return ScaleChangeClip(change_events)
