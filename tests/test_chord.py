import pytest
from harmonica.chord import PitchSet, PitchSetShape
from harmonica.scale import PitchClassSet

class TestPitchSet:
    def test_size(self):
        assert PitchSet([0,4,7,9,11]).cardinality == 5

    def test_span(self):
        assert PitchSet([-9,-6,1,9,14]).span == 23
    
    def test_transpose(self):
        pset = PitchSet([0,4,7,10])
        pset.transpose(4)
        assert pset.pitches == [4,8,11,14]
    
    def test_add(self):
        pset = PitchSet([0,4,7,10])
        pset2 = pset + 4
        assert pset2.pitches == [4,8,11,14]

    def test_eq(self):
        assert PitchSet([0,4,7]) == PitchSet([0,4,7])

    def test_sub(self):
        pset = PitchSet([4,8,11,14])
        pset2 = pset - 4
        assert pset2.pitches == [0,4,7,10]
    
    def test_normalize(self):
        pset = PitchSet([4,8,11,22])
        pset.normalize()
        assert pset.pitches == [0,4,7,18]
    
    def test_shape(self):
        pset = PitchSet([0,4,7,11])
        shape = PitchSetShape([4,3,4])
        assert pset.shape == shape
    
    def test_classify(self):
        pset = PitchSet([0,2,4,9,11,16])
        mod = 8
        pcset = PitchClassSet([0,1,2,3,4], mod)
        assert pset.classify(mod) == pcset
    
    def test_harmonize(self):
        pset = PitchSet([0,2,6,9,12,19,24])
        tp = 4
        tpi = 3
        pset_harm = PitchSet([-5,-3,1,4,7,14,19])
        pset.harmonize(tp, tpi)
        assert pset == pset_harm
    
    def test_interval_spectrum(self):
        pset = PitchSet([0,4,7,14])
        spectrum = [
            [4,3,7],
            [7,10],
            [14]
        ]
        assert pset.interval_spectrum == spectrum
    
    def test_invert(self):
        pset = PitchSet([4,6,9,13])
        amount = 3
        inverted = PitchSet([13,16,18,21])
        pset.invert(amount)
        assert pset == inverted

class TestPitchSetShape:
    def test_init_neg(self):
        with pytest.raises(AssertionError):
            shape = PitchSetShape([7,7,-2,7])
    
    def test_getitem(self):
        shape = PitchSetShape([7,7,2,7])
        assert shape[2] == 2
    
    def test_eq(self):
        assert PitchSetShape([2,2,21]) == PitchSetShape([2,2,21])
    
    def test_stamp(self):
        shape = PitchSetShape([5,2,6])
        assert shape.stamp(2) == PitchSet([2,7,9,15])
    
    def test_span(self):
        shape = PitchSetShape([2,4,6])
        assert shape.span == 12

class TestFindPitchSets:
    def test_brute_force(self):
        brute = PitchSet.find(
                            60,65
                        ).cardinality(
                            3
                        ).collect()
        
        results = set(
            PitchSet(x) for x in [
                [60,61,62], [60,61,63], [60,61,64], [60,61,65],
                [60,62,63], [60,62,64], [60,62,65], 
                [60,63,64], [60,63,65],
                [60,64,65],
                [61,62,63], [61,62,64], [61,62,65],
                [61,63,64], [61,63,65],
                [61,64,65],
                [62,63,64], [62,63,65],
                [62,64,65],
                [63,64,65]
            ]
        )

        assert brute == results

    def test_pcset_search(self):
        in_pcset = PitchSet.find(
                                60,66
                            ).in_pcset(
                                PitchClassSet([0,2,4,5,7,9,10], 12)
                            ).collect()

        results = set(
            PitchSet(x) for x in [
                [60], [62], [64], [65],
                [60, 62], [60, 64], [60, 65], [62, 64], [62, 65], [64, 65],
                [60, 62, 64], [60, 62, 65], [60, 64, 65], [62, 64, 65],
                [60, 62, 64, 65]
            ]
        )

        assert in_pcset == results

    def test_transpositions(self):
        has_shape = PitchSet.find(
                                60,66
                            ).has_shape(
                                PitchSetShape([2,1])
                            ).collect()
        
        results = set(
            PitchSet(x) for x in [
                [60,62,63], [61,63,64], [62,64,65], [63,65,66]
            ]
        )

        assert has_shape == results