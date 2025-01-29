from harmonica.melody import Polyphony, PitchContour, PitchSequence

class TestPitchSeq:
    def test_contour(self):
        pseq = PitchSequence([0,2,4,7,-2,0])
        contour = PitchContour([2,2,3,-9,2])
        assert pseq.contour == contour

    def test_transpose(self):
        pseq = PitchSequence([0,2,4,7,-2,0])
        tr = PitchSequence([2,4,6,9,0,2])
        pseq.transpose(2)
        assert pseq == tr

    def test_add(self):
        pseq = PitchSequence([0,2,4,7,-2,0])
        tr = PitchSequence([2,4,6,9,0,2])
        assert pseq + 2 == tr

    def test_normalize(self):
        pseq = PitchSequence([-6,2,4,7,3])
        norm = PitchSequence([0,8,10,13,9])
        pseq.normalize()
        assert pseq == norm
    
    def test_stamp(self):
        contour = PitchContour([2,-3,1,0,6])
        pseq = PitchSequence([5,7,4,5,5,11])
        assert contour.stamp(5) == pseq

class TestPSeqSet:
    def test_all_lengths_equal(self):
        pseqset_a = Polyphony([
            PitchSequence([0,2,6,4,8]),
            PitchSequence([1,6,0,4,7,3]),
            PitchSequence([0,-6,-2,7])
        ])
        pseqset_b = Polyphony([
            PitchSequence([0,2,6,4,8]),
            PitchSequence([1,6,0,4,7]),
            PitchSequence([0,-6,-2,7,1])
        ])
        assert pseqset_a.all_lengths_equal() is False and pseqset_b.all_lengths_equal() is True

    def test_transpose(self):
        pseqset = Polyphony([
            PitchSequence([0,2,6,4,8]),
            PitchSequence([1,6,0,4,7,3]),
            PitchSequence([0,-6,-2,7])
        ])
        transposed = Polyphony([
            PitchSequence([1,3,7,5,9]),
            PitchSequence([2,7,1,5,8,4]),
            PitchSequence([1,-5,-1,8])
        ])
        pseqset.transpose(1)
        assert pseqset == transposed