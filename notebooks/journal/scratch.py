from math import floor

from harmonica.utility._mixed import Mixed


def truncate(subdivs, res, new_dur_in_beats: Mixed):
    """Truncates the subdivision tree to a new duration (in beats)."""

    new_dur_in_beats = floor(new_dur_in_beats / res) * res

    new_dur_units = int(new_dur_in_beats / res)

    new_subdiv_tree = []

    for subdiv in subdivs:
        new_subdiv = []

        for i in subdiv:
            new_sum = sum(new_subdiv + [i])
            if new_sum > new_dur_units:
                diff = new_sum - new_dur_units
                if i - diff > 0:
                    new_subdiv.append(i - diff)
                break
            else:
                new_subdiv.append(i)

        new_subdiv_tree.append(new_subdiv)

    return new_subdiv_tree


tree = [[6, 4], [3, 3, 2, 2], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
print(truncate(tree, Mixed("1/4"), Mixed("7/3")))
