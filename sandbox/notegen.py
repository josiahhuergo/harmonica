from fractions import Fraction
from itertools import cycle
from harmonica.chord import PitchSet
from harmonica.melody import PitchFunc
from harmonica.timeline import Note, Timeline


def block_chords(
    chord_seq: list[PitchSet],
    dur_seq: list[Fraction],
    length: int,
    strum: Fraction = Fraction(0),
) -> list[Note]:
    """Generates a stream of block chords as notes.

    chord_seq: A sequence of pitch sets.

    dur_seq: A sequence of time deltas between successive pitch sets.

    strum: Offsets each note by a certain amount, creating a strumming or broken chord type effect.
    Negative values strum top-down instead of down-up.

    length: The number of chords populated into the output."""

    notes: list[Note] = []
    chords = cycle(chord_seq)
    durs = cycle(dur_seq)
    onset = Fraction(0)

    while length > 0:
        chord = next(chords)
        dur = next(durs)

        strum_onset = onset
        strum_dur = dur
        for pitch in chord:
            notes.append(Note(onset=strum_onset, pitch=pitch, duration=strum_dur))
            strum_dur -= strum
            strum_onset += strum

        onset += dur
        length -= 1

    return notes


def melodic_line(
    pitch_seq: list[int], dur_seq: list[Fraction], length: int
) -> list[Note]:
    """Generates a stream of pitches as notes.

    pitch_seq: A sequence of pitches.

    dur_seq: A sequence of time deltas between notes.

    length: The number of notes to produce."""

    notes = []

    pitches = cycle(pitch_seq)
    durs = cycle(dur_seq)
    onset = Fraction(0)

    while length > 0:
        dur = next(durs)
        notes.append(Note(onset=onset, pitch=next(pitches), duration=dur))
        onset += dur
        length -= 1

    return notes


def arpeggiate():
    pass


psets = [
    pset + 60
    for pset in [
        PitchSet([0, 3, 7, 10]),
        PitchSet([2, 5, 10]),
        PitchSet([3, 7, 10, 14]),
        PitchSet([14, 15, 17, 26]),
    ]
]

chords = block_chords(
    chord_seq=psets,
    dur_seq=[Fraction("5/2"), Fraction("3/2")],
    strum=Fraction("1/4"),
    length=20,
)

melody = melodic_line(
    pitch_seq=[
        p + 84 for p in [3, 2, 0, -5, -7, -9, -10, -14, -12, -10, -14, -17, 3, 5, 2, -2]
    ],
    dur_seq=[Fraction(x) for x in ["1/4"]],
    length=128,
)

timeline = Timeline()

for note in chords:
    timeline.add_event(note)

for note in melody:
    timeline.add_event(note)

# timeline.write_and_open_midi()

scale = PitchFunc([2, 3, 7], 58)
pfunc = PitchFunc([1, -1, 3, 1, 5, 2, 6, 4, 7, 5, 9, 5, 8, 4, 6, 3, 5, 2, 4, 5])

pitches = [scale(pfunc(i)) for i in range(-20, 20)]
chord_p = [scale(i) for i in range(-5, 16)]

funcmel = melodic_line(
    pitch_seq=pitches, dur_seq=[Fraction("1/8")], length=len(pitches)
)

chrds = block_chords(
    chord_seq=[PitchSet(chord_p)],
    dur_seq=[Fraction(16)],
    length=1,
    strum=Fraction("1/2"),
)

# for note in funcmel:
#     timeline.add_event(note)

# for note in chrds:
#     timeline.add_event(note)

timeline.write_and_open_midi()
