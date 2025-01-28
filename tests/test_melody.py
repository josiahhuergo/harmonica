from harmonica.melody import PitchContour, PitchSequence

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