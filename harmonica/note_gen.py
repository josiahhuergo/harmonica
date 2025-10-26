from fractions import Fraction
from itertools import cycle

from harmonica.chord import PitchSet
from harmonica.time import NoteClip, Note


def block_chords(
    chord_seq: list[PitchSet],
    dur_seq: list[Fraction],
    vel_seq: list[Fraction],
    length: int,
    strum: Fraction = Fraction(0),
) -> NoteClip:
    """Generates a stream of block chords as notes.

    chord_seq: A sequence of pitch sets.

    dur_seq: A sequence of time deltas between successive pitch sets.

    strum: Offsets each note by a certain amount, creating a strumming or broken chord type effect.
    Negative values strum top-down instead of down-up.

    length: The number of chords populated into the output."""

    notes: list[Note] = []
    chords = cycle(chord_seq)
    durs = cycle(dur_seq)
    vels = cycle(vel_seq)
    onset = Fraction(0)

    while length > 0:
        chord = next(chords)
        dur = next(durs)

        strum_onset = onset
        strum_dur = dur
        for pitch in chord:
            vel = next(vels)
            notes.append(
                Note(onset=strum_onset, pitch=pitch, duration=strum_dur, velocity=vel)
            )
            strum_dur -= strum
            strum_onset += strum

        onset += dur
        length -= 1

    return NoteClip(notes)


def melodic_line(
    pitch_seq: list[int], dur_seq: list[Fraction], vel_seq: list[Fraction], length: int
) -> NoteClip:
    """Generates a stream of pitches as notes.

    pitch_seq: A sequence of pitches.

    dur_seq: A sequence of time deltas between notes.

    length: The number of notes to produce."""

    notes = []

    pitches = cycle(pitch_seq)
    durs = cycle(dur_seq)
    vels = cycle(vel_seq)
    onset = Fraction(0)

    while length > 0:
        dur = next(durs)
        vel = next(vels)
        p = next(pitches)
        notes.append(Note(onset=onset, pitch=p, duration=dur, velocity=vel))
        onset += dur
        length -= 1

    return NoteClip(notes)
