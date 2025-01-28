"""Objects and algorithms pertaining to chords."""

from __future__ import annotations
from dataclasses import dataclass

from harmonica.scale import PitchClassSet
from harmonica.util import cumsum, diff


@dataclass
class PitchSet:
    """A set of pitches used to represent a specific voicing of a chord."""

    ## DATA ##

    pitches: list[int]

    ## MAGIC METHODS ##

    def __post_init__(self):
        assert self.pitches == list(sorted(set(self.pitches))), "Pitches in pitch set must be unique."
        assert self.pitches == list(sorted(self.pitches)), "Pitches in pitch set must be sorted."

        self.pitches = list(set(self.pitches)) # Remove duplicates
        self.pitches.sort() # Sort pitches

    def __getitem__(self, item: int) -> int:
        return self.pitches[item]
    
    def __add__(self, amount: int) -> PitchSet:
        pset = PitchSet(self.pitches)
        pset.transpose(amount)

        return pset
    
    def __sub__(self, amount: int):
        pset = pset = PitchSet(self.pitches)
        pset.transpose(-amount)

        return pset
    
    def __mod__(self, modulus: int) -> PitchClassSet:
        return self.classify(modulus)

    ## TRANSFORM ##

    def transpose(self, amount: int):
        """Transposes the pitch set by `amount` semitones."""

        for i in range(len(self.pitches)):
            self.pitches[i] += amount
    
    def normalize(self):
        """Transposes the pitch set so the lowest pitch is 0."""

        self.transpose(-min(self.pitches))

    def harmonize(self, target_pitch: int, target_pitch_index: int):
        """Transposes the pitch set so the pitch at `index` is equal to `pitch`."""

        self.pitches = [
            pitch + (target_pitch - self.pitches[target_pitch_index]) for pitch in self.pitches
        ]

    ## GENERATE ##

    def classify(self, modulus: int) -> PitchClassSet:
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
    def interval_network(self) -> list[list[int]]:
        """Returns a list of lists representing intervals between pairs of pitches 
        in the pitch set, grouped together by level of adjacency.

        The first list is of intervals between adjacent pitches, which is
        equal to the shape of the pitch set. The second list is of intervals
        between pairs of pitches that are two spaces apart, etc. 

        The sole element in the last list, the interval between the first and
        last pitch, is equivalent to the span of the pitch set.
        
        Example: `{-4,1,8,10}` has the following interval network:
        ```
        [ [5,7,2], [12,9], [14] ]
        ```"""

        # RESEARCH FURTHER (Should probably just return a dict between tuples of pitches & intervals)

        network = []

        for adjacency in range(1, self.size):
            entry = []

            for pos in range(self.size - adjacency):
                entry.append(self.pitches[pos + adjacency] - self.pitches[pos])

            network.append(entry)
        
        return network


    
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

    def invert_around_voice(modulus: int, voice: int):
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


