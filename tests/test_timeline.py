from fractions import Fraction
from harmonica.timeline import Event, Note, Timeline

class TestTimeline:
    def test_get_notes(self):
        tl = Timeline()
        tl.add_event(Event(onset=Fraction()))
        tl.add_event(Note(onset=Fraction(2,3), pitch=60, duration=Fraction(1)))
        tl.add_event(Note(onset=Fraction(2), pitch=64, duration=Fraction(1)))
        
        notes = [
            Note(Fraction(2,3), 60, Fraction(1)),
            Note(Fraction(2), 64, Fraction(1))
        ]
        
        print(tl.get_notes())
        
        assert tl.get_notes() == notes

