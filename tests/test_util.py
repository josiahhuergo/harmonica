from harmonica.util import *

def test_rotate():
    lst = [0,4,6,9,2]
    rotated = [6,9,2,0,4]
    assert rotate(lst, 2) == rotated

def test_diff():
    lst = [0,4,8,22,11]
    d = [4,4,14,-11]
    assert diff(lst) == d

def test_cumsum():
    lst = [3,2,7,5]
    start = 3
    cumsummed = [3,6,8,15,20]
    assert cumsum(lst, start) == cumsummed

def test_matrix_transpose():
    lst = [
        [0,2,3],
        [1,5,7],
        [9,3,6]
    ]
    trans = [
        [0,1,9],
        [2,5,3],
        [3,7,6]
    ]
    assert matrix_transpose(lst) == trans

def test_repeating_subseq():
    seq = [1,2,3,1,2,7,1,2,3,1,2,7,1,2,3]
    subseq = [1,2,3,1,2,7]
    assert repeating_subseq(seq) == subseq

def test_flatten_list():
    lst = [
        [1,4,2],
        [
            6,
            [1,7]
        ],
        7
    ]
    flat = [1,4,2,6,1,7,7]
    assert flatten_list(lst) == flat

def test_cycle_diff():
    lst = [1,4,6,8,10]
    mod = 12
    start_index = 2
    cdiff = [2,2,3,3,2]
    assert cycle_diff(lst,mod,start_index) == cdiff

def test_cycle_cumsum():
    shape = [2,2,3,2]
    start = 3
    cs = [1,3,5,7]
    assert cycle_cumsum(shape, start) == cs