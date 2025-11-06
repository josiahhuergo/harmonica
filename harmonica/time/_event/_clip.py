from __future__ import annotations
from fractions import Fraction
import os
from pathlib import Path
import subprocess
from typing import Generic, Iterable, Self, TypeVar, Union

from ._event import Event, Note, ScaleChange

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo


E = TypeVar("E", bound="Event")


class Clip(Generic[E], Event):
    """A clip is an event that contains other events."""

    events: list[E | Clip[E]]

    def __init__(
        self, events: list[E | Clip[E]], onset: Fraction = Fraction(0)
    ) -> None:
        super().__init__(onset)
        self.events = events

    def __iter__(self) -> Iterable[E | Clip[E]]:
        return iter(self.events)

    def __next__(self) -> E | Clip[E]:
        return next(self)

    def __repr__(self):
        return f"Clip(onset={self.onset}, events={self.events})"

    def get_flattened_events(self) -> list[E]:
        """Returns a flattened list of all events in this clip and any other clips
        it contains."""

        events: list[E] = []

        for event in self.events:
            if isinstance(event, Clip):
                flattened_clip_events = event.get_flattened_events()
                for clip_event in flattened_clip_events:
                    clip_event.onset += event.onset
                events.extend(flattened_clip_events)
            else:
                events.append(event)

        return sorted(events, key=lambda event: event.onset)

    def add_event(self, event: E | Clip[E]):
        self.events.append(event)

    def add_events(self, events: list[E | Clip[E]]):
        self.events.extend(events)

    def write_midi(self, filename: str = "temp", tempo: int = 120):
        """Writes the notes in the timeline to a MIDI file. Without any arguments,
        this creates a file called temp.mid by default."""

        mid: MidiFile = self._create_midifile(tempo=tempo)
        Path("output").mkdir(exist_ok=True)
        mid.save(f"output/{filename}.mid")

    def write_and_open_midi(self, filename: str = "temp", tempo: int = 120):
        self.write_midi(filename, tempo=tempo)
        subprocess.run(["taskkill", "/f", "/im", "domino.exe"], capture_output=True)
        os.startfile(str(Path.cwd()) + "/output/" + filename + ".mid")

    def _create_midifile(self, tempo: int = 120) -> MidiFile:
        """Creates a MidiFile object and populates it with messages corresponding to
        the tracks in our Timeline object."""

        mid = MidiFile()

        # Tempo track
        mid.tracks.append(MidiTrack())

        # Set tempo
        mid.tracks[0].append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo)))

        for i, child in enumerate(self.events):
            if type(child) is not NoteClip:
                continue

            if i > 15:
                continue

            track = []
            mid.tracks.append(MidiTrack())

            mid.tracks[-1].append(
                Message(
                    "program_change",
                    program=child.program,
                    channel=i,
                    time=_frac_to_ticks(Fraction(4), mid.ticks_per_beat),
                )
            )

            for note in child.get_notes():
                onset_ticks = _frac_to_ticks(
                    note.onset + child.onset, mid.ticks_per_beat
                )
                duration_ticks = _frac_to_ticks(note.duration, mid.ticks_per_beat)
                offset_ticks = onset_ticks + duration_ticks

                # Note on event
                track.append(
                    (
                        onset_ticks,
                        "note_on",
                        note.pitch,
                        int(max(min(127, note.velocity * 127), 0)),
                    )
                )
                # Note off event
                track.append((offset_ticks, "note_off", note.pitch, 0))

            # Sort by time, with note_off before note_on at same tick
            track.sort(key=lambda x: (x[0], x[1] == "note_on"))

            # Convert to delta-time messages
            last_time = 0
            for abs_time, msg_type, pitch, velocity in track:
                delta = abs_time - last_time
                mid.tracks[-1].append(
                    Message(
                        msg_type, channel=i, note=pitch, velocity=velocity, time=delta
                    )
                )
                last_time = abs_time

        return mid


class NoteClip(Clip[Note]):
    program: int

    def __init__(
        self,
        events: list[Note | Clip[Note]],
        onset: Fraction = Fraction(0),
        program: int = 0,
    ) -> None:
        super().__init__(events, onset)
        self.program = program

    def get_notes(self) -> list[Note]:
        return Clip[Note].get_flattened_events(self)

    def set_program(self, program: int) -> Self:
        self.program = program
        return self


class ScaleChangeClip(Clip[ScaleChange]):
    def __init__(
        self,
        events: list[ScaleChange | Clip[ScaleChange]],
        onset: Fraction = Fraction(0),
    ) -> None:
        super().__init__(events, onset)

    # def get_scale_at_time(self, t: Fraction) -> PitchClassSet:
    #     pass


def _frac_to_ticks(frac: Fraction, tpb: int) -> int:
    return int(tpb * frac)
