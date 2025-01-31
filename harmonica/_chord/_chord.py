from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from math import ceil

from harmonica._scale import PitchClassSet
from _utility import cumsum, diff


@dataclass
class PitchSet:
    """A set of pitches used to represent a specific voicing of a chord."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert self.pitches == list(sorted(set(self.pitches))), "Pitches in pitch set must be unique."
        assert self.pitches == list(sorted(self.pitches)), "Pitches in pitch set must be sorted."

    def __getitem__(self, item: int) -> int:
        return self.pitches[item]
    
    def __add__(self, amount: int) -> PitchSet:
        pset = PitchSet(self.pitches)
        pset.transpose(amount)

        return pset
    
    def __sub__(self, amount: int) -> PitchSet:
        pset = pset = PitchSet(self.pitches)
        pset.transpose(-amount)

        return pset
    
    def __mod__(self, modulus: int) -> PitchClassSet:
        return self.classify(modulus)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes the pitch set."""

        for i in range(len(self.pitches)):
            self.pitches[i] += amount
    
    def transposed(self, amount: int) -> PitchSet:
        """Returns a transposed pitch set."""
        
        return PitchSet([pitch + amount for pitch in self.pitches])
    
    def normalize(self):
        """Transposes the pitch set so the lowest pitch is 0."""

        self.transpose(-min(self.pitches))
    
    def normalized(self) -> PitchSet:
        """Returns a normalized pitch set."""

        return PitchSet([pitch - min(self.pitches) for pitch in self.pitches])

    def harmonize(self, target_pitch: int, target_pitch_index: int):
        """Transposes the pitch set so the pitch at `index` is equal to `pitch`."""

        self.pitches = [
            pitch + (target_pitch - self.pitches[target_pitch_index]) for pitch in self.pitches
        ]
    
    def invert(self, amount: int, modulus: int = 12):
        """Treats the pitch set as a chord-scale with respect to a given modulus - 12 by default - 
        and inverts the chord by a certain amount. This has the effect of moving the pitch set 
        up or down in register."""

        new_mod = modulus * ceil(self.span / modulus)
        pcset = self.classify(new_mod)
        func = pcset.scale_function(min(pcset.pitch_classes))
        self.pitches = [func(func.index(pitch) + amount) for pitch in self.pitches]      

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

        return PitchSetShape(diff(self.pitches))

    @property
    def size(self) -> int:
        """The number of pitches in the set."""

        return len(self.pitches)
    
    @property
    def span(self) -> int:
        """The difference between the highest and lowest pitches in the set."""

        return max(self.pitches) - min(self.pitches)
    
    @property
    def interval_network(self) -> dict:
        """Returns a dict that maps pairs of pitches to the intervals between them. 
        This accounts for every interval present in the pitch set."""

        return { pair : pair[1] - pair[0] for pair in combinations(self.pitches, 2)}

@dataclass
class PitchSetShape:
    """A sequence of positive intervals that describes the intervallic shape of a pitch set."""

    ## DATA ##

    intervals: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert not any(
            [interval <= 0 for interval in self.intervals]
        ), 'Intervals in pitch set shape must be greater than 0.'

    def __getitem__(self, item: int) -> int:
        # Access pitch set shape like a list for convenience.
        return self.intervals[item]
    
    ## TRANSFORM ##

    def invert_around_voice(self, modulus: int, voice: int):
        """Inverts a chord with respect to a modulus, fixed around a voice."""

        # RESEARCH FURTHER

        pass

    ## GENERATE ##

    def stamp(self, lowest_pitch: int) -> PitchSet:
        """Constructs a pitch set using the shape of intervals."""

        return PitchSet(cumsum(self.intervals, lowest_pitch))
    
    ## ANALYZE
    
    @property
    def span(self) -> int:
        """How many semitones the shape spans."""

        return sum(self.intervals)

