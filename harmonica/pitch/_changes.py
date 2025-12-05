"""Objects and algorithms pertaining to harmonic changes and progressions."""

from dataclasses import dataclass
from typing import Optional

from harmonica.utility import Mixed, Time

from ._pitchset import PitchSet

__all__ = ["PitchSetSeq"]


@dataclass
class PitchSetSeq:
    """A sequence of pitch sets, representing a succession of chord voicings."""

    ## DATA ##

    pitch_sets: list[PitchSet]

    ## MAGIC METHODS ##

    def __len__(self) -> int:
        return len(self.pitch_sets)

    def __getitem__(self, item: int) -> PitchSet:
        return self.pitch_sets[item]

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes all the pitch sets in the sequence."""

        for pitch_set in self.pitch_sets:
            pitch_set.transpose(amount)

    ## ANALYZE ##

    def all_sizes_equal(self) -> bool:
        """Returns true if all pitch sets in the set are of the same length."""

        if len(self.pitch_sets) == 0:
            return True

        cardinality = self.pitch_sets[0].cardinality

        if all([x.cardinality == cardinality for x in self.pitch_sets]):
            return True
        else:
            return False

    @property
    def len(self) -> int:
        """Returns the length of the sequence of pitch sets."""

        return len(self.pitch_sets)

    ## PREVIEW ##

    def preview(self, bass: Optional[int] = None, duration: Time = 2, program: int = 0):
        """Previews the pitch set sequence."""

        from harmonica.time import NoteClip, Clip, Note

        duration = Mixed(duration)

        transpose = 0
        if bass:
            transpose = bass - self[0][0]

        note_clip = NoteClip([]).set_program(program)
        onset = Mixed(0)

        for pitch_set in self:
            for pitch in pitch_set:
                note_clip.add_event(
                    Note(pitch=pitch + transpose, onset=onset, duration=duration)
                )
            onset += duration

        Clip([note_clip]).preview()
