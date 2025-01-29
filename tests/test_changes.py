from harmonica.changes import PitchSetSeq
from harmonica.chord import PitchSet

class TestPitchSetSeq:
    def test_transpose(self):
        psetseq = PitchSetSeq([
            PitchSet([0,2,6,8]),
            PitchSet([1,6,7]),
            PitchSet([-6,-2,7])
        ])
        transposed = PitchSetSeq([
            PitchSet([1,3,7,9]),
            PitchSet([2,7,8]),
            PitchSet([-5,-1,8])
        ])
        psetseq.transpose(1)
        assert psetseq == transposed

    def test_all_sizes_equal(self):
        psetseq_a = PitchSetSeq([
            PitchSet([0,2,6,8]),
            PitchSet([1,6,7]),
            PitchSet([-6,-2,7])
        ])
        psetseq_b = PitchSetSeq([
            PitchSet([1,3,7,9]),
            PitchSet([2,7,8,16]),
            PitchSet([-5,-1,8,9])
        ])
        assert psetseq_a.all_sizes_equal() is False and psetseq_b.all_sizes_equal() is True