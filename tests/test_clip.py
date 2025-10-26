from fractions import Fraction
from harmonica.time import Event, Clip


class TestClip:
    def test_get_events(self):
        clip = Clip(
            [
                Event(Fraction(0)),
                Event(Fraction("1/2")),
                Clip(
                    [
                        Event(Fraction("1/4")),
                        Event(Fraction("4/5")),
                        Event(Fraction("16/11")),
                    ]
                ),
                Event(12),
                Clip(
                    [
                        Event(Fraction(4)),
                        Event(Fraction("22/19")),
                        Event(Fraction(6)),
                        Event(Fraction(22)),
                        Event(Fraction(55)),
                        Event(Fraction(66)),
                    ],
                    onset="5/3",
                ),
            ]
        )
        flat_clip = Clip(
            [
                Event(onset=Fraction(0)),
                Event(onset=Fraction("1 / 4")),
                Event(onset=Fraction("1 / 2")),
                Event(onset=Fraction("4 / 5")),
                Event(onset=Fraction("22 / 19")),
                Event(onset=Fraction("16 / 11")),
                Event(onset=Fraction(4)),
                Event(onset=Fraction(6)),
                Event(onset=Fraction(12)),
                Event(onset=Fraction(22)),
                Event(onset=Fraction(55)),
                Event(onset=Fraction(66)),
            ]
        )

        assert clip.get_flattened_events() == flat_clip.get_flattened_events()
