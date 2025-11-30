"""Miscellaneous functions that are helpful throughout the library."""

from enum import IntEnum
import math
from itertools import chain, combinations
from typing import Iterable

__all__ = [
    "pitch_key",
    "int_to_note",
    "int_to_pitch_class",
    "rotate",
    "brightness_of_tone",
    "diff",
    "cycle_diff",
    "cumsum",
    "cycle_cumsum",
    "matrix_transpose",
    "repeating_subseq",
    "flatten_list",
    "smallest_multiple",
    "quantize",
    "is_cyclically_ordered",
    "factors",
    "print_iter",
    "powerset",
    "GM",
    "GMDrum",
]


class GM(IntEnum):
    # Piano
    AcousticGrandPiano = 0
    BrightAcousticPiano = 1
    ElectricGrandPiano = 2
    HonkyTonkPiano = 3
    ElectricPiano1 = 4
    ElectricPiano2 = 5
    Harpsichord = 6
    Clavinet = 7

    # Chromatic Percussion
    Celesta = 8
    Glockenspiel = 9
    MusicBox = 10
    Vibraphone = 11
    Marimba = 12
    Xylophone = 13
    TubularBells = 14
    Dulcimer = 15

    # Organ
    DrawbarOrgan = 16
    PercussiveOrgan = 17
    RockOrgan = 18
    ChurchOrgan = 19
    ReedOrgan = 20
    Accordion = 21
    Harmonica = 22
    TangoAccordion = 23

    # Guitar
    AcousticGuitarNylon = 24
    AcousticGuitarSteel = 25
    ElectricGuitarJazz = 26
    ElectricGuitarClean = 27
    ElectricGuitarMuted = 28
    OverdrivenGuitar = 29
    DistortionGuitar = 30
    GuitarHarmonics = 31

    # Bass
    AcousticBass = 32
    ElectricBassFinger = 33
    ElectricBassPick = 34
    FretlessBass = 35
    SlapBass1 = 36
    SlapBass2 = 37
    SynthBass1 = 38
    SynthBass2 = 39

    # Strings
    Violin = 40
    Viola = 41
    Cello = 42
    Contrabass = 43
    TremoloStrings = 44
    PizzicatoStrings = 45
    OrchestralHarp = 46
    Timpani = 47

    # Ensemble
    StringEnsemble1 = 48
    StringEnsemble2 = 49
    SynthStrings1 = 50
    SynthStrings2 = 51
    ChoirAahs = 52
    VoiceOohs = 53
    SynthVoice = 54
    OrchestraHit = 55

    # Brass
    Trumpet = 56
    Trombone = 57
    Tuba = 58
    MutedTrumpet = 59
    FrenchHorn = 60
    BrassSection = 61
    SynthBrass1 = 62
    SynthBrass2 = 63

    # Reed
    SopranoSax = 64
    AltoSax = 65
    TenorSax = 66
    BaritoneSax = 67
    Oboe = 68
    EnglishHorn = 69
    Bassoon = 70
    Clarinet = 71

    # Pipe
    Piccolo = 72
    Flute = 73
    Recorder = 74
    PanFlute = 75
    BlownBottle = 76
    Shakuhachi = 77
    Whistle = 78
    Ocarina = 79

    # Synth Lead
    Lead1Square = 80
    Lead2Sawtooth = 81
    Lead3Calliope = 82
    Lead4Chiff = 83
    Lead5Charang = 84
    Lead6Voice = 85
    Lead7Fifths = 86
    Lead8BassLead = 87

    # Synth Pad
    Pad1NewAge = 88
    Pad2Warm = 89
    Pad3Polysynth = 90
    Pad4Choir = 91
    Pad5Bowed = 92
    Pad6Metallic = 93
    Pad7Halo = 94
    Pad8Sweep = 95

    # Synth Effects
    FX1Rain = 96
    FX2Soundtrack = 97
    FX3Crystal = 98
    FX4Atmosphere = 99
    FX5Brightness = 100
    FX6Goblins = 101
    FX7Echoes = 102
    FX8SciFi = 103

    # Ethnic
    Sitar = 104
    Banjo = 105
    Shamisen = 106
    Koto = 107
    Kalimba = 108
    Bagpipe = 109
    Fiddle = 110
    Shanai = 111

    # Percussive
    TinkleBell = 112
    Agogo = 113
    SteelDrums = 114
    Woodblock = 115
    TaikoDrum = 116
    MelodicTom = 117
    SynthDrum = 118
    ReverseCymbal = 119

    # Sound Effects
    GuitarFretNoise = 120
    BreathNoise = 121
    Seashore = 122
    BirdTweet = 123
    TelephoneRing = 124
    Helicopter = 125
    Applause = 126
    Gunshot = 127


class GMDrum(IntEnum):
    """General MIDI Drum Kit (Channel 10)"""

    AcousticBassDrum = 35
    BassDrum1 = 36
    SideStick = 37
    AcousticSnare = 38
    HandClap = 39
    ElectricSnare = 40
    LowFloorTom = 41
    ClosedHiHat = 42
    HighFloorTom = 43
    PedalHiHat = 44
    LowTom = 45
    OpenHiHat = 46
    LowMidTom = 47
    HiMidTom = 48
    CrashCymbal1 = 49
    HighTom = 50
    RideCymbal1 = 51
    ChineseCymbal = 52
    RideBell = 53
    Tambourine = 54
    SplashCymbal = 55
    Cowbell = 56
    CrashCymbal2 = 57
    Vibraslap = 58
    RideCymbal2 = 59
    HiBongo = 60
    LowBongo = 61
    MuteHiConga = 62
    OpenHiConga = 63
    LowConga = 64
    HighTimbale = 65
    LowTimbale = 66
    HighAgogo = 67
    LowAgogo = 68
    Cabasa = 69
    Maracas = 70
    ShortWhistle = 71
    LongWhistle = 72
    ShortGuiro = 73
    LongGuiro = 74
    Claves = 75
    HiWoodBlock = 76
    LowWoodBlock = 77
    MuteCuica = 78
    OpenCuica = 79
    MuteTriangle = 80
    OpenTriangle = 81


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
    11: "B",
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

    return lst[n % len(lst) :] + lst[: n % len(lst)]


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
        11: 5,
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

    return [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]


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

    for window_size in range(1, len(seq) + 1):
        # Store first element as the "ref window".
        ref_window = seq[0:window_size]
        # It starts with window size one, and then it starts at position one.
        for position in range(0, len(seq) - window_size, window_size):
            window = seq[position : position + window_size]
            # "Is this window equal to the ref window?"
            if window == ref_window:
                continue  # If yes, then carry on.
            else:  # If no, then continue to the next window size.
                break
        else:
            return window

    return seq


def flatten_list(lst: list) -> list:
    """Takes a nested list and flattens into a simple 1-dimensional list."""

    if not lst:
        return lst
    if isinstance(lst[0], list):
        return flatten_list(lst[0]) + flatten_list(lst[1:])

    return lst[:1] + flatten_list(lst[1:])


def smallest_multiple(n: int, m: int) -> int:
    """Returns the smallest multiple of n greater than m."""

    return n * ((m // n) + 1)


def quantize(n: int, q: int) -> int:
    return q * math.floor(n / q + 1 / 2)


def is_cyclically_ordered(a: int, b: int, c: int, m: int) -> bool:
    return 0 <= (b - a) % m <= (c - a) % m


def factors(n: int) -> list[int]:
    """Returns the factors of n."""

    return list(i for i in range(1, n + 1) if n % i == 0)


def print_iter(lis: Iterable):
    """Prints an iterable row by row."""

    for e in lis:
        print(e)


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
