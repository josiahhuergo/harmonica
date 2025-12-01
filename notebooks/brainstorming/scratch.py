from harmonica.pitch._scales import PitchClassSet
from harmonica.time._event._clip import ScaleChangeClip
from harmonica.time._event._event import ScaleChange


scale_changes = ScaleChangeClip(
    [
        ScaleChange(onset, scale)
        for onset, scale in [
            (0, PitchClassSet([0, 2, 4, 5, 7], 12)),
            (2, PitchClassSet([0, 2, 3, 6, 9, 10], 12)),
            (5, PitchClassSet([1, 2, 4, 5, 7, 8], 12)),
            (7, PitchClassSet([2, 4, 5, 7, 10], 12)),
        ]
    ]
)
