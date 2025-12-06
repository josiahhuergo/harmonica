from __future__ import annotations
import os
from pathlib import Path
import subprocess
from typing import Generic, Iterable, Self, Sequence, TypeVar

from harmonica.pitch import PitchClassSet
from harmonica.utility import Mixed

from ._event import DrumEvent, Event, Note, ScaleChange

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo


E = TypeVar("E", bound="Event")


class Clip(Generic[E], Event):
    """A clip is an event that contains other events."""

    events: list[E | Self]

    def __init__(
        self, events: Sequence[E | Self] = [], onset: Mixed = Mixed(0)
    ) -> None:
        super().__init__(onset)
        self.events = list(events)

    def __iter__(self) -> Iterable[E | Clip[E]]:
        return iter(self.events)

    def __next__(self) -> E | Self:
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

    def get_note_clips(self) -> list[NoteClip]:
        """Returns a list of the note clips inside of this clip."""
        note_clips: list[NoteClip] = []

        for event in self.events:
            if type(event) is NoteClip:
                note_clips.append(event)

        return note_clips

    def get_onsets(self) -> list[Mixed]:
        """Returns a list of onset times."""

        return sorted(set([event.onset for event in self.events]))

    def add_event(self, event: E | Self):
        self.events.append(event)

    def add_events(self, events: list[E | Self]):
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

    def preview(self, tempo: int = 120):
        """Listen back to the contents of the clip."""

        self.write_and_open_midi(tempo=tempo)

    def _create_midifile(self, tempo: int = 120) -> MidiFile:
        """Creates a MidiFile object and populates it with messages corresponding to
        the tracks in our Timeline object."""

        mid = MidiFile()

        # Tempo track
        mid.tracks.append(MidiTrack())

        # Set tempo
        mid.tracks[0].append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo)))

        # If there are any drum clips present, create a drum track at index 1 and combine the clips
        if any([type(event) is DrumClip for event in self.events]):
            mid.tracks.append(MidiTrack())

            DUR = 40  # Give all drum hits a constant gate value

            track = []

            # I need to combine the drum tracks.

            drum_clip = DrumClip()

            for event in self.events:
                if type(event) is DrumClip:
                    drum_clip.add_event(event)

            for event in drum_clip.get_drum_events():
                if event.drum < 0 or event.drum > 127:
                    # Ignore out of bounds values
                    continue

                onset_ticks = _frac_to_ticks(event.onset, mid.ticks_per_beat)
                offset_ticks = onset_ticks + DUR

                # Note on event
                track.append(
                    (onset_ticks, "note_on", event.drum, int(event.velocity * 127))
                )
                # Note off event
                track.append((offset_ticks, "note_off", event.drum, 0))

                track.sort(key=lambda x: (x[0], x[1] == "note_on"))

            # Convert to delta-time messages
            last_time = 0
            for abs_time, msg_type, pitch, velocity in track:
                delta = abs_time - last_time
                mid.tracks[-1].append(
                    Message(
                        msg_type,
                        channel=9,
                        note=pitch,
                        velocity=velocity,
                        time=delta,
                    )
                )
                last_time = abs_time

        # Add all note clips
        for i, child in enumerate(self.events):
            if type(child) is not NoteClip:
                continue

            if i >= 9:  # Channel index 9 is reserved for the drum track, so we skip
                i += 1

            if i > 15:
                # There are only 16 channels, 0 through 15, so we ignore anything higher
                continue

            track = []
            mid.tracks.append(MidiTrack())

            mid.tracks[-1].append(
                Message(
                    "program_change",
                    program=child.program,
                    channel=i,
                    time=_frac_to_ticks(Mixed(0), mid.ticks_per_beat),
                )
            )

            for note in child.get_notes():
                if note.pitch < 0 or note.pitch > 127:
                    # Ignore out of bounds values
                    continue

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
        events: Sequence[Note | Self] = [],
        onset: Mixed = Mixed(0),
        program: int = 0,
    ) -> None:
        super().__init__(events, onset)
        self.program = program

    def get_notes(self) -> list[Note]:
        return Clip[Note].get_flattened_events(self)

    def set_program(self, program: int) -> Self:
        self.program = program
        return self

    def preview(self, tempo: int = 120):
        Clip([self]).preview(tempo)


class DrumClip(Clip[DrumEvent]):
    def __init__(
        self, events: Sequence[DrumEvent | Self] = [], onset: Mixed = Mixed(0)
    ) -> None:
        super().__init__(events, onset)

    def get_drum_events(self) -> list[DrumEvent]:
        return Clip[DrumEvent].get_flattened_events(self)

    def preview(self, tempo: int = 120):
        Clip([self]).preview(tempo)


class ScaleChangeClip(Clip[ScaleChange]):
    def __init__(
        self,
        events: Sequence[ScaleChange | Self] = [],
        onset: Mixed = Mixed(0),
    ) -> None:
        super().__init__(events, onset)

    def get_scales(self) -> list[ScaleChange]:
        return Clip[ScaleChange].get_flattened_events(self)

    def get_scale_at_time(self, t: Mixed) -> PitchClassSet:
        for i, scale_change in enumerate(self.get_scales()):
            if scale_change.onset > t:
                return self.get_scales()[i - 1].scale

        return self.get_scales()[-1].scale


def _frac_to_ticks(frac: Mixed, tpb: int) -> int:
    return int(tpb * frac)
