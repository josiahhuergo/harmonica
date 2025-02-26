"""Tools for modeling events distributed on a timeline, including arrangements of notes."""

from dataclasses import dataclass, field
from fractions import Fraction
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
    outport: str = 'Microsoft GS Wavetable Synth 0' 
    
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
        
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.tempo)))
        
        note_buffer: list[tuple[Fraction, int]] = []
        last_time: Fraction = Fraction()
        
        for note in self.get_notes():
            for buffer_note in note_buffer[:]:
                if buffer_note[0] <= note.onset:
                    t = _frac_to_ticks(buffer_note[0]-last_time, mid.ticks_per_beat)
                    track.append(Message('note_off', note=buffer_note[1], velocity=127, time=t))
                    last_time = buffer_note[0]
                    note_buffer.remove(buffer_note)
            
            t = _frac_to_ticks(note.onset-last_time, mid.ticks_per_beat)
            track.append(Message('note_on', note=note.pitch, velocity=127, time=t))
            last_time = note.onset
            note_buffer.append((note.onset + note.duration, note.pitch))
            
        for buffer_note in note_buffer:
            t = _frac_to_ticks(buffer_note[0]-last_time, mid.ticks_per_beat)
            track.append(Message('note_off', note=buffer_note[1], velocity=127, time=t))
            last_time = buffer_note[0]
            
        return mid
    
    def _sort(self):
        self.events.sort(key=lambda x: x.onset)
        
def _frac_to_ticks(frac: Fraction, tpb: int) -> int:
    return int(tpb * frac)
    