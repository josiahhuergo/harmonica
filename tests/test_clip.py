from harmonica.time import Event, Clip
from harmonica.utility._mixed import Mixed


class TestClip:
    def test_get_events(self):
        clip = Clip(
            [
                Event(Mixed(0)),
                Event(Mixed("1/2")),
                Clip(
                    [
                        Event(Mixed("1/4")),
                        Event(Mixed("4/5")),
                        Event(Mixed("16/11")),
                    ]
                ),
                Event(Mixed(12)),
                Clip(
                    [
                        Event(Mixed(4)),
                        Event(Mixed("22/19")),
                        Event(Mixed(6)),
                        Event(Mixed(22)),
                        Event(Mixed(55)),
                        Event(Mixed(66)),
                    ],
                    onset=Mixed("5/3"),
                ),
            ]
        )
        flat_clip = Clip(
            [
                Event(onset=Mixed(0)),
                Event(onset=Mixed("1 / 4")),
                Event(onset=Mixed("1 / 2")),
                Event(onset=Mixed("4 / 5")),
                Event(onset=Mixed("22 / 19")),
                Event(onset=Mixed("16 / 11")),
                Event(onset=Mixed(4)),
                Event(onset=Mixed(6)),
                Event(onset=Mixed(12)),
                Event(onset=Mixed(22)),
                Event(onset=Mixed(55)),
                Event(onset=Mixed(66)),
            ]
        )

        assert clip.get_flattened_events() == flat_clip.get_flattened_events()
