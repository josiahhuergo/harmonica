from typing import Any

from harmonica._chord import PitchSet

class FindPitchSets:
    """Object with a dict of strings which specify what criteria to use
    when generating a list of pitch sets.
    
    You tack criteria onto the dict by calling methods like `max_size(4)`. 
    Then you call `collect()` to get the resulting list."""

    criteria: dict[str, Any]

    def collect(self) -> list[PitchSet]:
        return []
    
    