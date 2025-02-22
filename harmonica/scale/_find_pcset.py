from __future__ import annotations

from harmonica.scale import PitchClassSet

class FindPCSets:
    """Object with a dict of strings which specify what criteria to use
    when generating a list of pitch class sets.
    
    You tack criteria onto the dict by calling methods like `max_size(4)`. 
    Then you call `collect()` to get the resulting list."""

    criteria: PitchClassSet

    


    
