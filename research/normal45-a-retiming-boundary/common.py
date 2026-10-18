# SPDX-License-Identifier: Apache-2.0
"""Scalar row transport and cleanup, Tekalign with substantial OpenAI Codex assistance."""
import copy
from fractions import Fraction as Q
import preload_move as pm

FULL = pm.basis([1 << i for i in range(9)])
PROFILE = {'1': 2434, '2': 632, '3': 286, '4': 104, '5': 26, '8': 8}
OBJECTS = ((57, 94, 3866, 1852, 2164), (57, 62, 3865, 1852, 2010),
           (92, 63, 3859, 1857, 2010), (92, 61, 3860, 1857, 2164))


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def scalar_pull(row, gate):
    out = dict(row)
    if gate[0] == 'add':
        t, s, a, b = gate[1:5]
        out[s] = out.get(s, Q(0)) + out.get(t, Q(0)) * Q(a, b)
    elif gate[0] == 'scale':
        t, a, b = gate[1:4]
        out[t] = out.get(t, Q(0)) * Q(a, b)
    else:
        raise ValueError('transport interval must be scalar')
    return {s: a for s, a in out.items() if a}


def retime(word, original, cut, row, order):
    target = word['A'][original][1]
    require(set(order) == set(row) and len(order) == len(row), 'complete source permutation')
    require(target not in row, 'no self shear')
    child = copy.deepcopy(word)
    del child['A'][original]
    child['A'][cut:cut] = [['add', target, r, row[r].numerator, row[r].denominator, []]
                         for r in order]
    return child


def cleanup(word):
    child = copy.deepcopy(word)
    child['A'] = child['A'][child['prelude_events']:]
    return pm.derive_cleanup(child, set(map(int, child['helper_final'])))
