from fractions import Fraction

import mido

from harmonica.timeline import Note, Timeline


chords = [[0, 4, 7, 11], [-3, 0, 4, 7]]

chords = [[pitch + 60 for pitch in chord] for chord in chords]

# [[60, 64, 67, 71], [57, 60, 64, 67]]


def broken_chord(chord: list[int], spread: Fraction, duration: Fraction) -> list[Note]:
    """Takes a pitch set and turns it into a broken chord. It is arpeggiated upwards,
    and notes are all sustained for `duration` long."""

    notes = []
    onset = Fraction(0)

    for pitch in chord:
        note = Note(onset=onset, pitch=pitch, duration=duration)
        notes.append(note)
        duration -= spread
        onset += spread

    return notes


bc = broken_chord(chords[0], Fraction("1/2"), Fraction(4))
timeline = Timeline(bc)
# timeline.play_midi()
