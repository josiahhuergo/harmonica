from harmonica.time import Clip, TimeFunc
from harmonica.utility import GMDrum, Mixed

clip_len = Mixed(128)

f = TimeFunc([Mixed(x) for x in ["3/4", "1 1/2", 2]])
g = f.stretch(Mixed("3/4")).trunc(Mixed(4))
h = f.stretch(Mixed("1 1/2")).trunc(Mixed(4))
f = f.trunc(Mixed(4))
t = TimeFunc([Mixed(1)])
c = t.trunc(Mixed(4)).pad_tail(Mixed(4)).shift(Mixed(4))
k = TimeFunc(
    [Mixed(x) for x in ["1/3", "2/3", "1 1/3", "1 2/3", 2, 32]], offset=Mixed("18 1/2")
)
j = TimeFunc([Mixed(x) for x in ["1/4", "3/4", "2 1/2", "3 1/2", 4]])

Clip(
    [
        f.to_clip(clip_len, drum=GMDrum.HiWoodBlock),
        g.to_clip(clip_len, drum=GMDrum.Claves),
        h.to_clip(clip_len, drum=GMDrum.AcousticBassDrum),
        t.to_clip(clip_len, drum=GMDrum.PedalHiHat),
        c.to_clip(clip_len, drum=GMDrum.HandClap),
        k.to_clip(clip_len, drum=GMDrum.LowMidTom),
        j.to_clip(clip_len, drum=GMDrum.ShortGuiro),
    ]
).preview(tempo=100)
