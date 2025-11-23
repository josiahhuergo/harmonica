from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import ceil
from typing import TYPE_CHECKING, Optional

from harmonica.pitch import PitchClassSet
from harmonica.utility import diff

if TYPE_CHECKING:
    from harmonica.pitch import PitchSetShape
    from harmonica.time import NoteClip


@dataclass
class PitchSet:
    """A set of pitches used to represent a specific voicing of a chord."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert self.pitches == list(
            sorted(set(self.pitches))
        ), "Pitches in pitch set must be unique."
        assert self.pitches == list(
            sorted(self.pitches)
        ), "Pitches in pitch set must be sorted."

    def __getitem__(self, item: int) -> int:
        return self.pitches[item]

    def __iter__(self):
        return iter(self.pitches)

    def __add__(self, amount: int) -> PitchSet:
        return self.get_transposed(amount)

    def __len__(self) -> int:
        return len(self.pitches)

    def __sub__(self, amount: int) -> PitchSet:
        pset = PitchSet(self.pitches)
        pset.transpose(-amount)

        return pset

    def __mod__(self, modulus: int) -> PitchClassSet:
        return self.classify(modulus)

    def __hash__(self):
        return hash(tuple(pitch for pitch in self.pitches))

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes the pitch set."""

        for i in range(len(self.pitches)):
            self.pitches[i] += amount

        return self

    def get_transposed(self, amount: int) -> PitchSet:
        """Returns a transposed pitch set."""

        return PitchSet([pitch + amount for pitch in self.pitches])

    def normalize(self):
        """Transposes the pitch set so the lowest pitch is 0."""

        self.transpose(-min(self.pitches))

        return self

    def get_normalized(self) -> PitchSet:
        """Returns a normalized pitch set."""

        return PitchSet([pitch - min(self.pitches) for pitch in self.pitches])

    def harmonize(self, target_pitch: int, target_pitch_index: int):
        """Transposes the pitch set so the pitch at `target_pitch_index` is equal to `target_pitch`."""

        self.pitches = [
            pitch + (target_pitch - self.pitches[target_pitch_index])
            for pitch in self.pitches
        ]

        return self

    def get_harmonized(self, target_pitch: int, target_pitch_index: int):
        """Returns transposed pitch set. Immutable variant of `harmonize()`."""

    def invert(self, amount: int, modulus: int = 12):
        """Treats the pitch set as a chord-scale with respect to a given modulus - 12 by default -
        and inverts the chord by a certain amount. This has the effect of moving the pitch set
        up or down in register."""

        new_mod = modulus * ceil(self.span / modulus)
        pcset = self.classify(new_mod)
        func = pcset.scale_function(min(pcset.pitch_classes))
        self.pitches = [func(func.index(pitch) + amount) for pitch in self.pitches]

        return self

    ## GENERATE ##

    def classify(self, modulus: int = 12) -> PitchClassSet:
        """Yields the pitch class set corresponding to this pitch set with respect to a given modulus."""

        pcset = [pitch % modulus for pitch in self.pitches]
        pcset = list(set(pcset))
        pcset.sort()

        return PitchClassSet(pcset, modulus)

    ## ANALYZE ##

    @property
    def shape(self) -> PitchSetShape:
        """The sequence of intervals between adjacent pitches in the set."""

        from harmonica.pitch import PitchSetShape

        return PitchSetShape(diff(self.pitches))

    @property
    def cardinality(self) -> int:
        """The number of pitches in the set."""

        return len(self.pitches)

    @property
    def span(self) -> int:
        """The difference between the highest and lowest pitches in the set."""

        return max(self.pitches) - min(self.pitches)

    @property
    def interval_spectrum(self) -> list[list[int]]:
        """Returns a list of lists that describes intervals between notes that
        are one space apart, then two spaces apart, etc.

        >>> PitchSet([0,4,7,14]).interval_spectrum
        [[4,3,7], [7,10], [14]]]

        This accounts for every interval present in the pitch set."""

        if self.cardinality <= 1:
            return []

        spectrum: list[list[int]] = []

        for jump in range(1, self.cardinality):
            diffs: list[int] = []
            for pos in range(self.cardinality - jump):
                diffs.append(self.pitches[pos + jump] - self.pitches[pos])
            spectrum.append(diffs)

        return spectrum

    ## PREVIEW ##

    def to_clip(
        self, onset: Fraction = Fraction(0), duration: Fraction = Fraction(8)
    ) -> NoteClip:
        """Creates a note clip from the pitch set."""

        from harmonica.time import NoteClip, Note

        note_clip = NoteClip([])

        for pitch in self:
            note_clip.add_event(Note(pitch=pitch, duration=duration, onset=Fraction(0)))

        note_clip.set_onset(onset)

        return note_clip

    def preview(self, bass: Optional[int] = None):
        """Previews the pitch set."""

        from harmonica.time import NoteClip, Clip, Note

        duration = Fraction(8)
        transpose = 0
        if bass:
            transpose = bass - self[0]

        note_clip = NoteClip([])

        for pitch in self:
            note_clip.add_event(
                Note(pitch=pitch + transpose, duration=duration, onset=Fraction(0))
            )

        Clip([note_clip]).preview()
