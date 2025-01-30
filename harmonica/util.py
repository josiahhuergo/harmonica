"""Miscellanious functions that are helpful throughout the library."""

import math
from itertools import chain, combinations

__all__ = ["pitch_key", "int_to_note", "int_to_pitch_class", "rotate", 
           "brightness_of_tone", "diff", "cycle_diff", "cumsum", "cycle_cumsum", 
           "matrix_transpose", "repeating_subseq", "flatten_list", "smallest_multiple", 
           "quantize", "is_cyclically_ordered", "factors", "print_list", "powerset"]

pitch_key = {
    0: "C",
    1: "Db",
    2: "D",
    3: "Eb",
    4: "E",
    5: "F",
    6: "Gb",
    7: "G",
    8: "Ab",
    9: "A",
    10: "Bb",
    11: "B"
}

def int_to_note(pitch_int: int) -> str:
    """Returns the letter name and octave of a pitch integer, such as 61 -> C#4."""

    octave = math.floor(pitch_int / 12) - 1

    return pitch_key[pitch_int % 12] + str(octave)

def int_to_pitch_class(pitch_int: int) -> str:
    """Returns the letter name of a pitch integer, such as 61 -> C#4."""

    return pitch_key[pitch_int % 12]

def rotate(lst: list, n: int) -> list:
    """Returns a rotated list."""

    return lst[n % len(lst):] + lst[:n % len(lst)]

def brightness_of_tone(tone: int) -> int:
    brightness_map = {
        0: 0,
        1: -5,
        2: 2,
        3: -3,
        4: 4,
        5: -1,
        6: 6,
        7: 1,
        8: -4,
        9: 3,
        10: -2,
        11: 5
    }

    return brightness_map[tone]

# def cluster(b: list, x: int) -> list:
#     # Returns a list describing the size of the clusters of number x in list b
#     # That is to say, it counts the number of adjacent occurrences of the number x in list b
#     # For example, in [2, 1, 1, 4], there are 2 adjacent occurrences of the number 1.
#     # (What is this even for?)

#     outp = [0]
#     for i in range(len(b)):
#         if b[i] == x:
#             outp[-1] += 1
#         else:
#             outp += [0]

#     return [i for i in outp[1:-1] + [outp[0] + outp[-1]] if i != 0]

def diff(seq: list[int]) -> list[int]:
    """Diffs a sequence of numbers."""

    return [seq[i+1] - seq[i] for i in range(len(seq)-1)]

def cycle_diff(cycle: list[int], mod: int, start_index: int) -> list[int]:
    """Diffs a circular permutation of numbers using modular arithmetic.
    
    Args:
        start_index (int): Index of number to start cycle diff on."""
    
    # Assumes cycle is sorted, non-negative, and less than mod.
    cdiff = diff(cycle) + [cycle[0] + mod - cycle[-1]]

    return rotate(cdiff, start_index)

def cumsum(seq: list[int], start: int = 0) -> list[int]:
    """Gives the cumulative sum of a sequence (opposite of diff)."""

    cs = [start]
    for num in seq:
        cs += [cs[-1] + num]

    return cs

def cycle_cumsum(cycle: list[int], start: int) -> list[int]:
    """Cumulatively sums a circular permutation of numbers using modular arithmetic. 
    The sum of the cycle is taken as the modulus."""

    mod = sum(cycle)
    start = start % mod
    cs = [start]
    for num in cycle[:-1]:
        cs += [(cs[-1] + num) % mod]
    cs.sort()

    return cs

def matrix_transpose(list_of_lists: list[list]) -> list[list]:
    """Transposes a tuple of tuples, in the matrix sense."""

    return list(map(list, zip(*list_of_lists)))

def repeating_subseq(seq: list) -> list:
    """If there's a repeating sequence inside of the list, it will be returned.
    Otherwise, it will return the original list."""

    ref_window = []
    window = []

    for window_size in range(1,len(seq)+1):
        # Store first element as the "ref window".
        ref_window = seq[0:window_size]
        # It starts with window size one, and then it starts at position one.
        for position in range(0,len(seq)-window_size,window_size):
            window = seq[position:position+window_size]
            # "Is this window equal to the ref window?"
            if window == ref_window: 
                continue  # If yes, then carry on.
            else: # If no, then continue to the next window size.
                break
        else:
            return window
        
    return seq

def flatten_list(lst: list) -> list:
    """Takes a nested list and flattens into a simple 1-dimensional list."""

    if lst == []:
        return lst
    if isinstance(lst[0], list):
        return flatten_list(lst[0]) + flatten_list(lst[1:])
    
    return lst[:1] + flatten_list(lst[1:])

def smallest_multiple(n: int, m: int) -> int:
    """Returns the smallest multiple of n greater than m."""

    return n * ((m // n) + 1)

def quantize(n: int, q: int) -> int:
    return q * math.floor(n/q + 1/2)

def is_cyclically_ordered(a: int, b: int, c: int, m: int) -> bool:
    return 0 <= (b - a) % m <= (c - a) % m

def factors(n: int) -> list[int]:
    """Returns the factors of n."""

    return list(i for i in range(1,n+1) if n % i == 0)

def print_list(lis: list):
    """Prints a list row by row."""

    for e in lis:
        print(e)

def powerset(n: list) -> list[list]:
    """Returns the powerset of the list n."""

    s = list(n)

    return list(list(x) for x in
            list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))))
