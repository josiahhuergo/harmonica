from harmonica._scale import PitchClassSet, ScaleFunc, ScaleStructure, PCSetWithRoot

class TestPitchClassSet:
    def test_transpose(self):
        scale = PitchClassSet([0,2,4,5,7,9,11], 12)
        tr = PitchClassSet([0,2,3,5,7,8,10], 12)
        scale.transpose(3)
        assert scale == tr
    
    def test_structure(self):
        scale = PitchClassSet([0,2,4,5,7,9,11], 12)
        structure = ScaleStructure([2,2,1,2,2,2,1])
        assert scale.structure == structure

    def test_normalize(self):
        normalized = PitchClassSet([0,3,4,6,8,15,23,1831], 2843)
        scale = PitchClassSet([3,6,7,9,11,18,26,1834], 2843)
        scale.normalize(3)
        assert scale == normalized

    def test_neq(self):
        assert PitchClassSet([1,2,4],6) != PitchClassSet([0,2,4],8)

    def test_eq(self):
        assert PitchClassSet([0,2,4],12) == PitchClassSet([0,2,4],12)
    
    def test_scale_function(self):
        scale = PitchClassSet([2,4,5,8,9,11], 12)
        func = ScaleFunc([2,3,6,7,9,12], 2)
        assert scale.scale_function(2) == func

    def test_contains_pitch(self):
        scale = PitchClassSet([2,4,5,7,10], modulus=11)
        assert scale.contains(21) is True and scale.contains(20) is False
    
    def test_interval_spectrum(self):
        scale = PitchClassSet([0,2,4,5,7,9,11], 12)
        spectrum = [
            [2,2,1,2,2,2,1],
            [4,3,3,4,4,3,3],
            [5,5,5,6,5,5,5],
            [7,7,7,7,7,7,6],
            [9,9,8,9,9,8,8],
            [11,10,10,11,10,10,10]
        ]
        assert scale.interval_spectrum == spectrum

    def test_interval_vector(self):
        scale = PitchClassSet([0,2,5,7,9,11], 12)
        assert scale.interval_vector == (1,4,3,2,4,1)
        

class TestPCSetWithRoot:
    def test_structure(self):
        scale = PCSetWithRoot([0,2,4,5,7,9,11], 12, 4)
        structure = ScaleStructure([1,2,2,2,1,2,2])
        assert scale.structure == structure

    def test_transpose(self):
        scale = PCSetWithRoot([0,2,4,5,7,9,11], 12, 4)
        scale_tr = PCSetWithRoot([0,1,3,5,6,8,10], 12, 5)
        scale.transpose(1)
        assert scale == scale_tr
    
    def test_rotate_mode_relative(self):
        scale = PCSetWithRoot([0,2,4,5,7,9,11], 12, 4)
        rot = PCSetWithRoot([0,2,4,5,7,9,11], 12, 9)
        scale.rotate_mode_relative(3)
        assert scale == rot
    
    def test_rotate_mode_parallel(self):
        scale = PCSetWithRoot([0,2,4,5,7,9,11], 12, 4)
        rot = PCSetWithRoot([1,2,4,6,8,9,11], 12, 4)
        scale.rotate_mode_parallel(2)
        assert scale == rot

class TestScaleStructure:
    def test_stamp_to_rooted_pcset(self):
        structure = ScaleStructure([3,3,4,2])
        root = 4
        rootpcset = PCSetWithRoot([2,4,7,10], structure.modulus, root)
        assert structure.stamp_to_pcset_with_root(root) == rootpcset
    
    def test_stamp_to_scale_func(self):
        structure = ScaleStructure([2,2,3,2,2,1])
        trans = 4
        func = ScaleFunc([2,4,7,9,11,12],4)
        assert structure.stamp_to_scale_func(trans) == func

class TestScaleFunc:
    def test_rotate_mode_relative(self):
        scale = ScaleFunc([2,4,5,7,9,10,12],2)
        amount = 2
        # {0,2,4,6,7,9,11} mod 12 root 2
        rot = ScaleFunc([1,3,5,6,8,10,12], 6)
        scale.rotate_mode_relative(amount)
        assert scale == rot
    
    def test_rotate_mode_parallel(self):
        scale = ScaleFunc([2,4,5,7,9,10,12],2)
        amount = 2
        # {0,2,4,6,7,9,11} mod 12 root 2
        rot = ScaleFunc([1,3,5,6,8,10,12], 2)
        scale.rotate_mode_parallel(amount)
        assert scale == rot
    
    def test_structure(self):
        scale = ScaleFunc([2,4,5,7,9,11,12],4)
        structure = ScaleStructure([2,2,1,2,2,2,1])
        assert scale.structure == structure

    def test_maps_to_pitch(self):
        scale = ScaleFunc([2,4,5,7,9,11,12], 4)
        pitch = 17
        assert scale.maps_to_pitch(pitch) == False

    def test_index_of_pitch(self):
        scale = ScaleFunc([2,4,5,7,9,11,12], 4)
        pitch = 25
        assert scale.index(pitch) == 12
    
    def test_to_pcset(self):
        scale = ScaleFunc([2,4,5,7,9,11,12], 4)
        pcset = PitchClassSet([1,3,4,6,8,9,11], 12)
        assert scale.to_pcset() == pcset
    
    def test_eval_rot(self):
        scale = ScaleFunc([2,4,5,7], 3)
        pitch = scale.eval_rot(3)
        rot = ScaleFunc([2,4,6,7], 8)
        assert pitch == 8 and scale == rot

    def test_eval_list(self):
        scale = ScaleFunc([2,4,5], 4)
        evals = [6,9,13]
        assert scale([1,3,5]) == evals

    def test_composition(self):
        scale1 = ScaleFunc([2,4,5,7,9,11,12], 2)
        scale2 = ScaleFunc([2], 1)
        comp = ScaleFunc([3,7,10,14,17,21,24], 4)
        
        assert scale1.compose(scale2) == comp