"""Construct rank-two residual words in the original binary symplectic space.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained rank-one kernel is by Nick Petalas, after Krzysztof Wojt.
"""
from pathlib import Path
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parent


def load_kernel():
    for row in json.loads((ROOT / 'ORIGINS.json').read_text()):
        data = (ROOT / row['local']).read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('retained source hash mismatch')
    return runpy.run_path(str(ROOT / 'inputs/rank_one.py'))


K = load_kernel()
require = K['require']
pairing = K['pairing']
turn = K['turn']
apply_word = K['apply_word']
combine = K['linear_combination']
eliminate = K['elimination']
residual = K['residual']


def rank(rows):
    return len(eliminate(tuple(rows))[0])


def anisotropic(rows):
    """Find a nonzero quadratic value on a basis vector or a pair sum."""
    r = len(rows)
    for c in tuple(1 << i for i in range(r)) + tuple(
            (1 << i) | (1 << j) for i in range(r) for j in range(i)):
        if (combine(rows, c) & c).bit_count() & 1:
            return c
    return None


def complete(n, source, image):
    """Return an attaining word or an interval of width one.

    A nonzero gap is not a proved optimum. The API rejects residual rank > 2.
    """
    K['validate'](n, source, image)
    basis, lifts, rows = residual(n, source, image)
    r, q = len(basis), rank(rows)
    require(q <= 2, 'residual rank exceeds two')
    lower = 2 * r - q
    escape = None
    pivot = anisotropic(rows)
    if q == 0:
        word = tuple(reversed(K['upper_correction'](n, source, image)))
        case = 'zero'
    elif q == 1:
        word = K['complete'](n, source, image)
        case = 'rank_one'
    elif pivot is not None:
        a = combine(basis, pivot)
        reduced = tuple(turn(y, a, n) for y in image)
        db, _, rb = residual(n, source, reduced)
        require(len(db) == r - 1 and rank(rb) == 1, 'pivot rank identity')
        word = K['complete'](n, source, reduced) + (a,)
        case = 'rank_two_nonalternating'
    else:
        delta = tuple(x ^ y for x, y in zip(source, image))
        fixed = tuple(combine(source, c) for c in eliminate(delta)[1])
        space = fixed + basis
        dimension = rank(space)
        radical = eliminate(rows)[1]
        for c in radical:
            v = combine(lifts, c)
            if rank(space + (v,)) > dimension:
                escape = v
                break
        i = next(i for i, row in enumerate(rows) if row)
        p, u = basis[i], lifts[i]
        constraints = tuple((x, 0) for x in space) + ((u, 1),)
        if escape is not None:
            constraints += ((escape, 1),)
        a = K['solve_pairings'](n, constraints)
        axes = (a, a ^ p)
        require(all(axes) and pairing(*axes, n) == 0, 'invalid correction pair')
        reduced = tuple(apply_word(y, axes, n) for y in image)
        db, _, rb = residual(n, source, reduced)
        expected_q = 2 if escape is not None else 1
        require(len(db) == r - 1 and rank(rb) == expected_q
                and anisotropic(rb) is not None, 'alternating reduction identity')
        tail = complete(n, source, reduced)
        require(tail['lower'] == tail['upper'], 'reduced optimum is not exact')
        word = tuple(tail['word']) + tuple(reversed(axes))
        case = 'rank_two_alternating_escape' if escape is not None else 'rank_two_alternating_closed'
        if r == 2:
            lower += 1
    upper = len(word)
    require(lower <= upper <= 2 * r, 'invalid completion bounds')
    require(tuple(apply_word(x, word, n) for x in source) == image,
            'word does not realize the partial map')
    return {'word': list(word), 'displacement_rank': r, 'residual_rank': q,
            'lower': lower, 'upper': upper, 'case': case, 'escape_lift': escape}
