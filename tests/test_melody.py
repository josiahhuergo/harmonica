from harmonica.melody import Polyphony, PitchSeqShape, PitchSeq

class TestPitchSeq:
    def test_contour(self):
        pseq = PitchSeq([0,2,4,7,-2,0])
        shape = PitchSeqShape([2,2,3,-9,2])
        assert pseq.shape == shape

    def test_transpose(self):
        pseq = PitchSeq([0,2,4,7,-2,0])
        tr = PitchSeq([2,4,6,9,0,2])
        pseq.transpose(2)
        assert pseq == tr

    def test_add(self):
        pseq = PitchSeq([0,2,4,7,-2,0])
        tr = PitchSeq([2,4,6,9,0,2])
        assert pseq + 2 == tr

    def test_normalize(self):
        pseq = PitchSeq([-6,2,4,7,3])
        norm = PitchSeq([0,8,10,13,9])
        pseq.normalize()
        assert pseq == norm
    
    def test_stamp(self):
        shape = PitchSeqShape([2,-3,1,0,6])
        pseq = PitchSeq([5,7,4,5,5,11])
        assert shape.stamp(5) == pseq

class TestPSeqSet:
    def test_all_lengths_equal(self):
        pseqset_a = Polyphony([
            PitchSeq([0,2,6,4,8]),
            PitchSeq([1,6,0,4,7,3]),
            PitchSeq([0,-6,-2,7])
        ])
        pseqset_b = Polyphony([
            PitchSeq([0,2,6,4,8]),
            PitchSeq([1,6,0,4,7]),
            PitchSeq([0,-6,-2,7,1])
        ])
        assert pseqset_a.all_lengths_equal() is False and pseqset_b.all_lengths_equal() is True

    def test_transpose(self):
        pseqset = Polyphony([
            PitchSeq([0,2,6,4,8]),
            PitchSeq([1,6,0,4,7,3]),
            PitchSeq([0,-6,-2,7])
        ])
        transposed = Polyphony([
            PitchSeq([1,3,7,5,9]),
            PitchSeq([2,7,1,5,8,4]),
            PitchSeq([1,-5,-1,8])
        ])
        pseqset.transpose(1)
        assert pseqset == transposed