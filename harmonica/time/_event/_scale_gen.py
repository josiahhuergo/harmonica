from itertools import cycle
from harmonica.pitch import PitchClassSet
from harmonica.utility import Mixed
from ._clip import ScaleChangeClip
from ._event import ScaleChange


def scale_changes(
    change_seq: list[PitchClassSet],
    delta_seq: list[Mixed],
    clip_dur: Mixed,
) -> ScaleChangeClip:
    change_events = []

    changes = cycle(change_seq)
    deltas = cycle(delta_seq)
    onset = Mixed(0)

    while onset < clip_dur:
        scale = next(changes)
        change_events.append(ScaleChange(onset, scale))
        onset += next(deltas)

    return ScaleChangeClip(change_events)
