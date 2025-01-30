"""Objects and algorithms pertaining to harmonic changes and progressions."""

from dataclasses import dataclass

from harmonica.chord import PitchSet

__all__ = ["PitchSetSeq"]

@dataclass
class PitchSetSeq:
    """A sequence of pitch sets, representing a succession of chord voicings."""

    ## DATA ##

    pitch_sets: list[PitchSet]

    ## MAGIC METHODS ##

    def __len__(self) -> int:
        return len(self.pitch_sets)

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
        
        size = self.pitch_sets[0].size

        if all([x.size == size for x in self.pitch_sets]):
            return True
        else:
            return False
    
    @property
    def len(self) -> int:
        """Returns the length of the sequence of pitch sets."""

        return len(self.pitch_sets)