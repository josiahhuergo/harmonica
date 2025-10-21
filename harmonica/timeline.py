"""Tools for modeling events distributed on a timeline, including arrangements of notes."""

from copy import deepcopy
from dataclasses import dataclass, field
from fractions import Fraction
import os
import subprocess
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo


@dataclass
class Event:
    """An event is anything that occurs at a specific moment in time.

    Its onset is represented as a fraction. The unit of time is **beats**.

    A beat is an abstract unit of time which can be converted to seconds
    given a tempo (in beats per minute)."""

    onset: Fraction


@dataclass
class Note(Event):
    """A note event has a pitch and duration."""

    pitch: int
    duration: Fraction


@dataclass
class Timeline:
    """Arrangement of events ordered by onset time."""

    events: list[Event] = field(default_factory=list)
    tempo: int = field(default=120)
    outport: str = "Microsoft GS Wavetable Synth 0"

    def __post_init__(self):
        self.events.sort(key=lambda e: e.onset)

    def add_event(self, event: Event):
        """Adds an event to the timeline."""

        self.events.append(event)
        self._sort()

    def add_note(self, onset: Fraction, pitch: int, duration: Fraction):
        """Adds a note to the timeline."""

        self.add_event(Note(onset, pitch, duration))

    def get_notes(self) -> list[Note]:
        """Returns a list of all the notes on the timeline."""

        return [event for event in self.events if isinstance(event, Note)]

    def write_midi(self, filename: str = "temp"):
        """Writes the notes in the timeline to a MIDI file. Without any arguments,
        this creates a file called temp.mid by default."""

        mid: MidiFile = self._create_midi()
        mid.save(filename + ".mid")

    def write_and_open_midi(self, filename: str = "temp"):
        self.write_midi(filename)
        subprocess.run(["taskkill", "/f", "/im", "domino.exe"], capture_output=True)
        os.startfile("C:/Users/Siahbug/Documents/harmonica/" + filename + ".mid")

    def play_midi(self):
        """Play notes in realtime."""

        mid: MidiFile = self._create_midi()

        with mido.open_output(self.outport) as port:
            for msg in mid.play():
                port.send(msg)

    def set_midi_port(self, port: str):
        """Sets the name of the port that MIDI messages will be sent to."""

        self.outport = port

    def _create_midi(self) -> MidiFile:
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Set tempo
        track.append(MetaMessage("set_tempo", tempo=bpm2tempo(self.tempo)))

        # Collect all MIDI events with absolute timing
        events = []

        for note in self.get_notes():
            onset_ticks = _frac_to_ticks(note.onset, mid.ticks_per_beat)
            duration_ticks = _frac_to_ticks(note.duration, mid.ticks_per_beat)
            offset_ticks = onset_ticks + duration_ticks

            # Note on event
            events.append((onset_ticks, "note_on", note.pitch, 127))
            # Note off event
            events.append((offset_ticks, "note_off", note.pitch, 0))

        # Sort by time, with note_off before note_on at same tick
        events.sort(key=lambda x: (x[0], x[1] == "note_on"))

        # Convert to delta-time messages
        last_time = 0
        for abs_time, msg_type, pitch, velocity in events:
            delta = abs_time - last_time
            track.append(Message(msg_type, note=pitch, velocity=velocity, time=delta))
            last_time = abs_time

        return mid

    def _sort(self):
        self.events.sort(key=lambda x: x.onset)


def _frac_to_ticks(frac: Fraction, tpb: int) -> int:
    return int(tpb * frac)
