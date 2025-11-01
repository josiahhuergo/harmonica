from fractions import Fraction
from itertools import cycle
from typing import Optional

from harmonica.pitch import PitchSet
from ._event import Note
from ._clip import NoteClip


def block_chords(
    pset_seq: list[PitchSet],
    delta_seq: list[Fraction],
    vel_seq: list[Fraction],
    clip_dur: Fraction,
    strum: Fraction = Fraction(0),
    trim_end: bool = False,
    note_len: Optional[Fraction] = None,
) -> NoteClip:
    """
    Generates a stream of block chords as notes.

    pset_seq: A sequence of pitch sets.

    delta_seq: A sequence of time deltas between successive pitch sets.

    clip_dur: Duration of generated clip.

    strum: Offsets each note by a certain amount, creating a strumming or broken chord type effect.
    Negative values strum top-down instead of down-up.

    trim_end: If this is true, the tails of any notes that extend past the clip duration are trimmed.

    note_len: A fixed length for each note. If None, then the note lengths are legato - meaning
    notes will be sustained until the next chord begins.
    """

    assert all([delta >= 0 for delta in delta_seq]), "Deltas must be positive values."
    assert clip_dur >= 0, "Clip duration must be positive."

    notes: list[Note] = []

    chords = cycle(pset_seq)
    deltas = cycle(delta_seq)
    vels = cycle(vel_seq)

    onset = Fraction(0)

    if not note_len:
        while True:
            if onset >= clip_dur:
                return NoteClip(notes)

            chord = next(chords)
            delta = next(deltas)
            vel = next(vels)

            strum_onset = onset
            strum_dur = delta

            for pitch in chord:
                dur = strum_dur
                if trim_end:
                    dur = min(dur, clip_dur - strum_onset)
                if strum_dur > 0:
                    notes.append(
                        Note(
                            onset=strum_onset,
                            pitch=pitch,
                            duration=dur,
                            velocity=vel,
                        )
                    )
                    strum_dur -= strum
                    strum_onset += strum
                else:
                    break

            onset += delta
    else:
        while True:
            if onset >= clip_dur:
                return NoteClip(notes)

            chord = next(chords)
            delta = next(deltas)
            vel = next(vels)

            strum_onset = onset

            for pitch in chord:
                dur = note_len
                if trim_end:
                    dur = min(dur, clip_dur - strum_onset)
                if strum_onset - onset >= delta:
                    break
                notes.append(
                    Note(
                        onset=strum_onset,
                        pitch=pitch,
                        duration=dur,
                        velocity=vel,
                    )
                )
                strum_onset += strum

            onset += delta


def mono_line(
    pitch_seq: list[int],
    delta_seq: list[Fraction],
    vel_seq: list[Fraction],
    clip_dur: Fraction,
    trim_end: bool = False,
    note_len: Optional[Fraction] = None,
) -> NoteClip:
    """Generates a stream of pitches as notes.

    pitch_seq: A sequence of pitches.

    delta_seq: A sequence of time deltas between notes.

    clip_dur: Duration of generated clip.

    note_len: A fixed length for each note. If None, then the note lengths are legato - meaning
    notes will be sustained until the next note begins."""

    assert all([delta >= 0 for delta in delta_seq]), "Deltas must be positive values."
    assert clip_dur >= 0, "Clip duration must be positive."

    notes = []

    pitches = cycle(pitch_seq)
    deltas = cycle(delta_seq)
    vels = cycle(vel_seq)
    onset = Fraction(0)

    while True:
        if onset >= clip_dur:
            return NoteClip(notes)

        delta = next(deltas)
        vel = next(vels)
        p = next(pitches)

        dur = note_len if note_len else delta

        if trim_end:
            dur = min(dur, clip_dur - onset)

        notes.append(Note(onset=onset, pitch=p, duration=dur, velocity=vel))

        onset += delta
