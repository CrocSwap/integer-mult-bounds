"""Exact controls for the clean-ancilla register note.

The scalar, Laurent and group-algebra primitives are imported unchanged from
the merged dirty-auxiliary package (PR #1882).  This module changes only the
acceptance predicate: with clean (zero-initialized, zero-restored) auxiliary
registers, only the data columns of the endpoint are constrained.

Column-vector convention: D_N([A]) = I + ([A]-1) x y^T maps v to
v + ([A]-1) x (y^T v), so column k of the product is the image of input k.

Only the Python standard library is used.
"""

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random

DIRTY = Path(__file__).resolve().parent.parent / 'bit-dirty-auxiliary-registers' / 'controls.py'
_spec = spec_from_file_location('dirty_aux_controls', DIRTY)
dirty = module_from_spec(_spec)  # merged PR #1882, imported unchanged
_spec.loader.exec_module(dirty)

projectors = dirty.projectors
cube_options = dirty.cube_options
symbolic_product = dirty.symbolic_product
formal_product = dirty.formal_product
diagonal_endpoint = dirty.diagonal_endpoint
frames_with_relation = dirty.frames_with_relation
parse_terminal = dirty.parse_terminal
rank_q = dirty.rank_q
add = dirty.add
outer = dirty.outer
_reduce = dirty._reduce


def clean_endpoint(state, W):
    """Data frames if every data column k < W equals [C_k] e_k, else None."""
    n = len(state)
    out = []
    for k in range(W):
        for i in range(n):
            if i != k and state[i][k]:
                return None
        if len(state[k][k]) != 1:
            return None
        key = next(iter(state[k][k]))
        out.append([list(key[0:3]), list(key[3:6]), list(key[6:9])])
    return out


def symbolic_terminals_clean(state, r, W):
    """Clean-ancilla class representatives of the data targets, or None."""
    n = len(state)
    reps = []
    for k in range(W):
        for i in range(n):
            acc = {}
            for key in state[i][k]:
                red = _reduce(key, r)
                acc[red] = acc.get(red, []) + [key]
            odd = [keys for keys in acc.values() if len(keys) % 2]
            if i != k and odd:
                return None
            if i == k:
                if len(odd) != 1:
                    return None
                key = odd[0][0]
                members = [key] if r is None else [
                    tuple(x + c * y for x, y in zip(key, r)) for c in (-1, 0, 1)]
                masks = [sum(b << q for q, b in enumerate(m)) for m in members
                         if all(b in (0, 1) for b in m)]
                reps.append(min(masks))
    return reps


def realize_terminals(lines, n, W, count, seed=7, require_clean_only=False):
    """Realize clean engine terminals with exact rational frames.

    For each selected terminal, the formal group-algebra product of random
    frames with exactly the stated relation lattice must satisfy the clean
    predicate, its data frames must equal the reported class sums, and some
    data target must have rank at most two.  With ``require_clean_only`` the
    same product must also fail the dirty (full diagonal) predicate, which
    shows that the relaxation is used physically.
    """
    rng = random.Random(seed)
    P = projectors(n)
    checked = 0
    for line in lines:
        flag, word, r, reps = parse_terminal(line)
        if r is not None and sum(1 for v in r if v) > 4:
            continue
        mats = [P[p] for p in word]
        frames = frames_with_relation(len(word), r, rng)
        state = formal_product(mats, frames)
        if require_clean_only and diagonal_endpoint(state) is not None:
            continue
        end = clean_endpoint(state, W)
        assert end is not None, line
        assert len(reps) == W, line
        for w, rep in enumerate(reps):
            expected = add(*[frames[j] for j in range(len(word)) if rep >> j & 1]) \
                if rep else [[Fraction(0)] * 3 for _ in range(3)]
            assert end[w] == expected, line
        assert flag == 0 and any(rank_q(end[w]) <= 2 for w in range(W)), line
        checked += 1
        if checked == count:
            break
    return checked


def compare_symbolic(lines, n, W, s, words):
    """Compare clean engine terminals with the symbolic implementation."""
    P = projectors(n)
    options = cube_options(s)
    by_word = {}
    for line in lines:
        flag, word, r, reps = parse_terminal(line)
        by_word.setdefault(tuple(word), set()).add((r, tuple(reps)))
    for word in words:
        state = symbolic_product([P[p] for p in word])
        found = set()
        for r in options:
            reps = symbolic_terminals_clean(state, r, W)
            if reps is not None:
                found.add((r, tuple(reps)))
        assert found == by_word.get(tuple(word), set()), word
    return len(words)


def clean_only_control(seed=20261014):
    """Two calls that are correct only because the auxiliary starts at zero.

    Registers (x0, x1, a).  Call 1 reads x0 + a and writes x0 (frame A).
    Call 2 reads a and writes x0 and a (frame B).  With a = 0 the second call
    sees zero, so the data columns are [A] e_0 and e_1; the auxiliary column
    is not diagonal.  The clean predicate accepts, the dirty one rejects.
    """
    rng = random.Random(seed)
    P = projectors(3)

    def proj(x, y):
        return tuple(tuple(x[i] * y[k] for k in range(3)) for i in range(3))
    first, second = proj((1, 0, 0), (1, 0, 1)), proj((1, 0, 1), (0, 0, 1))
    assert first in P and second in P
    A = outer(dirty.random_vector(rng), dirty.random_vector(rng))
    B = outer(dirty.random_vector(rng), dirty.random_vector(rng))
    state = formal_product([first, second], [A, B])
    zero = [[Fraction(0)] * 3 for _ in range(3)]
    assert diagonal_endpoint(state) is None
    assert clean_endpoint(state, 2) == [A, zero]
    # writing the result into the auxiliary instead is rejected by both
    leak = formal_product([proj((0, 0, 1), (1, 0, 1))], [A])
    assert clean_endpoint(leak, 2) is None
    return True
