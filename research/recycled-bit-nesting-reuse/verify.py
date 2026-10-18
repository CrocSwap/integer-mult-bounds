#!/usr/bin/env python3
"""Bounded differential check of the fraction-free null_exact kernel used by recycled-bit-integration/verify.py.

thakrarsagar, with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.

Checks (seconds, stdlib only):
  1. null_exact_ff(A, k) == PR97 linalg.null_exact(A, k) (list equality of integer rows) on structured edge
     cases and a deterministic random family: empty input, k = 0/1, zero rows, rank-deficient stacks,
     0/1 and +-1 entries, and entries up to 2^80;
  2. the installed fast prim equals frames147.prim on integer rows; non-integer or ragged input falls back
     to the original functions (same output, same exception);
  3. install_null_kernel patches linalg, check_lifted and frames147 in place, and VERIFY_NULL=audit catches a
     kernel whose output differs from the reference;
  4. negative controls: a sign-flipped kernel row and a non-primitive row differ from the reference; with the
     fast kernel installed, check_moves reports a non-nested move and the nondegeneracy predicate rejects a
     degenerate frame; the certificate pins the current verify.py bytes, not the base bytes.
This is a finite differential test plus a structural argument (see README); the full-input equality audit and
the full `--all` replay are recorded in README, not re-run here.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
PR97 = ROOT / 'references/partial-gauge/pr97'
os.environ.pop('VERIFY_NULL', None)
sys.path.insert(0, str(ROOT / 'research/bit-reuse-147'))
sys.path.insert(0, str(ROOT / 'research/recycled-bit-integration'))
import verify as V                      # research/recycled-bit-integration/verify.py (main() is not run)
assert Path(V.__file__).resolve() == ROOT / 'research/recycled-bit-integration/verify.py', V.__file__
import frames147
REF_PRIM = frames147.prim
sys.path.insert(0, str(PR97))
import linalg
import check_lifted
REF_NULL = linalg.null_exact
BASE_VERIFY_SHA = 'a5508f429d0ff6d441d9d07f6d1f9a83ce2335eb59b2041abbc65327b6a4a0b9'


def cases(seed=20261015, count=3000):
    yield from [([], 0), ([], 1), ([], 4), ([[0]], 1), ([[7]], 1), ([[0, 0, 0]], 3), ([[0, 0], [0, 0]], 2),
                ([[1, 2, 3]], 3), ([[-2, 4, -6], [1, -2, 3]], 3), ([[0, 3, 0, -6], [0, 0, 0, 0]], 4),
                ([[1, 0], [0, 1], [1, 1]], 2), ([[2**90, -3], [5, 2**70]], 2)]
    rng = random.Random(seed)
    for _ in range(count):
        k = rng.randint(1, 30); m = rng.randint(0, 35)
        lo, hi = rng.choice([(0, 1), (-1, 1), (-3, 3), (-10**6, 10**6), (-2**80, 2**80)])
        dens = rng.choice([0.1, 0.3, 0.6, 1.0])
        A = [[rng.randint(lo, hi) if rng.random() < dens else 0 for _ in range(k)] for _ in range(m)]
        if m > 2 and rng.random() < 0.4:
            for _ in range(rng.randint(1, 5)):
                u, v = rng.sample(range(m), 2); cu, cv = rng.randint(-5, 5), rng.randint(-5, 5)
                A.append([cu * x + cv * y for x, y in zip(A[u], A[v])])
            rng.shuffle(A)
        yield A, k


def main():
    n = nonempty = 0
    for A, k in cases():
        out = V.null_exact_ff(A, k)
        assert out == REF_NULL(A, k), ('kernel mismatch', A, k)
        assert all(type(x) is int for r in out for x in r)
        n += 1; nonempty += bool(out)
    print('PASS null_exact_ff == linalg.null_exact on %d matrices (%d with a nonzero kernel)' % (n, nonempty))

    assert V.install_null_kernel(PR97, 'fast') == 'fast'
    fast_null, fast_prim = linalg.null_exact, frames147.prim
    assert check_lifted.null_exact is fast_null and fast_null is not REF_NULL and fast_prim is not REF_PRIM
    rng = random.Random(7); m = 0
    for _ in range(20000):
        r = [rng.randint(-60, 60) * rng.randint(0, 1) for _ in range(rng.randint(0, 25))]
        assert fast_prim(r) == REF_PRIM(r) and all(type(x) is int for x in fast_prim(r)); m += 1
    frac = [[Fraction(1, 2), Fraction(-3, 4), 0]]
    assert fast_null(frac, 3) == REF_NULL(frac, 3) and fast_prim(frac[0]) == REF_PRIM(frac[0])
    for bad in ([[1, 2]], 3), ([[1, 2, 3, 4]], 3):
        errs = []
        for f in (fast_null, REF_NULL):
            try: errs.append(('ok', f(*bad)))
            except Exception as e: errs.append(type(e).__name__)
        assert errs[0] == errs[1], ('ragged fallback', bad, errs)
    print('PASS installed fast prim on %d rows; Fraction and ragged input fall back to the reference' % m)

    # negative controls on the kernel
    A = [[1, 2, 3, 4], [2, 0, 1, 1]]
    flipped = [[-x for x in r] for r in V.null_exact_ff(A, 4)]
    scaled = [[2 * x for x in r] for r in V.null_exact_ff(A, 4)]
    assert flipped != REF_NULL(A, 4) and scaled != REF_NULL(A, 4)
    assert V.install_null_kernel(PR97, 'audit') == 'audit'
    assert linalg.null_exact(A, 4) == REF_NULL(A, 4)
    saved = V.null_exact_ff
    V.null_exact_ff = lambda A, k: [[-x for x in r] for r in saved(A, k)]
    try:
        linalg.null_exact(A, 4)
        raise SystemExit('FAIL audit mode accepted a sign-flipped kernel')
    except AssertionError as e:
        assert 'null_exact kernel mismatch' in str(e.args[0])
    finally:
        V.null_exact_ff = saved
    print('PASS controls: sign-flipped and non-primitive kernel rows differ; VERIFY_NULL=audit rejects a wrong kernel')

    # predicates with the fast kernel installed (synthetic frames; Exact.__init__ is not run)
    V.install_null_kernel(PR97, 'fast')
    E = object.__new__(frames147.Exact)
    E.h = h = 23; E.null_exact = linalg.null_exact; E.rank_mod = linalg.rank_mod; E.Q31 = linalg.Q31
    E.full = [[int(i == j) for j in range(h)] for i in range(h)]; E._null = {}
    e = lambda i: [int(j == i) for j in range(h)]
    E._basis = {('x', 'small'): [[1, 1] + [0] * 21],
                ('x', 'big'): [e(0), e(1), [0, 0, 1, 1, -2] + [0] * 18],
                ('x', 'degenerate'): [[1] * 9 + [0] * 14]}
    assert V.check_moves(E, [('r', ('x', 'small'), ('x', 'big'))]) == []
    assert V.check_moves(E, [('r', ('x', 'big'), ('x', 'small'))]) == [('r', ('x', 'big'), ('x', 'small'))]
    assert E.null(('x', 'big')) == REF_NULL(E._basis[('x', 'big')], h)
    assert E.nondegenerate(('x', 'small')) and not E.nondegenerate(('x', 'degenerate'))
    bad = V.check_moves(E, [('r', ('x', 'small'), ('x', 'big')), ('r', ('x', 'degenerate'), ('x', 'big'))],
                        nondegenerate=True)
    assert bad == [('r', ('x', 'degenerate'), ('x', 'big'))], bad
    print('PASS controls: non-nested move reported, degenerate frame rejected (fast kernel installed)')

    cert = json.loads((ROOT / 'research/recycled-bit-integration/certificate.json').read_text())
    pin = cert['source_sha256']['research/recycled-bit-integration/verify.py']
    now = sha256((ROOT / 'research/recycled-bit-integration/verify.py').read_bytes()).hexdigest()
    assert pin == now != BASE_VERIFY_SHA and V.sources()['research/recycled-bit-integration/verify.py'] == pin
    print('PASS certificate pins the current verify.py (%s...), not the base bytes (%s...)' % (pin[:12], BASE_VERIFY_SHA[:12]))
    print('PASS_RECYCLED_BIT_NULL_KERNEL')


if __name__ == '__main__':
    main()
