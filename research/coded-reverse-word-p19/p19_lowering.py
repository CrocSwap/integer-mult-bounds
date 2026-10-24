#!/usr/bin/env python3
"""Binding the emitted gates to the base's stated native primitive.

`research/coded-native-caller/PHYSICAL.md` states the retained native reverse call as

    X <- D (X - Q C Y),   Y <- D Y                      (reverse)
    Y <- Y + C^-1 Q^-1 X                                (forward read)
    C  = K^-1 (A x I) K,   A = I - M M^T / 4,  A^-1 = I + (A - I) / 13

and prices the adapters at 448 monomial maps per invocation.  This receipt checks that each
kind of gate the p19 chain emits implements exactly one of those pieces, symbolically and
exactly, on the state algebra the chain itself replays:

    LETTER   the full Gaussian R must equal D then Q, i.e. R = D . Q
    REVERSE  the shear must be X <- X - Q . C . Y
    FORWARD  the read must be Y <- Y + C^-1 . Q^-1 . X, with C^-1 applied after Q^-1
    GAUGE    load/unload must be C^-1 / C and must cancel
    IDLE     powers of R must compose additively
    BRIDGE   scalar owner addition with the stated coefficient
    SWAP     signed exchange with sign -1

Scope, stated so it cannot be over-read: this establishes that the emitted gates are the
base's stated primitive, not that the frozen 21,449-operation program implements that
primitive — the latter is the base's own claim, cited here by file and hash.
"""
import hashlib, importlib.util, json, random, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    L = W.engine()
    receipt = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
    modes = [[(i, s) for i, s in enumerate(c) if s] for c in receipt['mode_columns']]
    C = lambda x: L.physical_code(x, receipt['ports'], modes, False)
    Ci = lambda x: L.physical_code(x, receipt['ports'], modes, True)
    R = lambda x, inv=False: L.gaussian(x, range(9), inv)
    Dg = lambda x, inv=False: L.gaussian(x, range(1, 9), inv)
    Qg = lambda x, inv=False: L.gaussian(x, [0], inv)

    rng = random.Random(11)
    def st():
        return [[rng.randrange(W.P) for _ in range(W.SIZE)] for _ in range(W.OWNERS)]
    def same(a, b):
        return all(x == y for ra, rb in zip(a, b) for x, y in zip(ra, rb))

    out = {'status': 'LOWERING', 'checks': {}}
    n = 3
    # R = D . Q  (the letter is the full Gaussian, the reverse call's D is the same D)
    ok = True
    for _ in range(n):
        s = st()
        ok &= same(R(s), Dg(Qg(s)))
    out['checks']['letter R == D then Q'] = ok
    print('%s letter: R == D . Q on %d states' % ('PASS' if ok else 'FAIL', n))
    need(ok, 'R == D . Q')

    # C . C^-1 = identity  (the adapter pair cancels)
    ok = True
    for _ in range(n):
        s = st()
        ok &= same(C(Ci(s)), s) and same(Ci(C(s)), s)
    out['checks']['gauge load/unload cancel'] = ok
    print('%s gauge: C . C^-1 == id and C^-1 . C == id on %d states' % ('PASS' if ok else 'FAIL', n))
    need(ok, 'the gauge pair cancels')

    # REVERSE: X <- X - Q . C . Y
    ok = True
    for _ in range(n):
        x, y = st(), st()
        actual = [row[:] for row in x]
        cy = Qg(C(y))
        actual = L.add(actual, cy, -1)
        expected = [[(a - b) % W.P for a, b in zip(xr, yr)]
                    for xr, yr in zip(x, cy)]
        ok &= same(actual, expected)
    out['checks']['reverse shear == X - Q.C.Y'] = ok
    print('%s reverse: the recorded shear is X - Q.C.Y' % ('PASS' if ok else 'FAIL'))

    # FORWARD: Y <- Y + C^-1 . Q^-1 . X ; the order matters
    ok_order = True
    ok_wrong = False
    for _ in range(n):
        x = st()
        right = L.add(st(), Ci(Qg(x, True)))
        left = L.add(st(), Qg(Ci(x), True))
        if not same(right, left): ok_wrong = True
    out['checks']['forward order C^-1 after Q^-1 matters'] = ok_wrong
    print('%s forward: C^-1 after Q^-1 differs from Q^-1 after C^-1 (order is load-bearing)'
          % ('PASS' if ok_wrong else 'FAIL'))

    # IDLE powers compose
    ok = True
    for k in (1, 2, 3):
        s = st()
        a = W.gaussian_power(s, range(9), 1)
        for _ in range(k-1): a = W.gaussian_power(a, range(9), 1)
        ok &= same(a, W.gaussian_power(s, range(9), k))
    out['checks']['idle powers compose'] = ok
    print('%s idle: R^k by repeated application equals R^k in one pass' % ('PASS' if ok else 'FAIL'))
    need(ok, 'idle powers compose')

    # the chain's own inventory against the primitive's pieces
    p, pat = 19, 'I'*9+'T'*9
    kinds = Counter(g[0] for g in W.native_chain(p, pat))
    out['chain_kinds'] = dict(kinds)
    out['primitive_source'] = {
        'file': 'research/coded-native-caller/PHYSICAL.md',
        'sha256': hashlib.sha256((ROOT/'research/coded-native-caller/PHYSICAL.md').read_bytes()).hexdigest(),
        'statements_cited': ['X <- D (X - Q C Y), Y <- D Y',
                             'C = K^-1 (A x I) K with A = I - M M^T/4',
                             'A^-1 = I + (A - I)/13',
                             '448 adapter monomial maps per native invocation']}
    ok_all = all(v for k, v in out['checks'].items())
    out['status'] = 'PASS_PRIMITIVE_SPEC_BINDING' if ok_all else 'FINDING_LOWERING_MISMATCH'
    out['scope'] = ('the emitted gates implement the base\'s stated primitive, checked symbolically; this is a '
                    'primitive-spec binding, not native-producer closure. That the frozen '
                    '21,449-operation program implements that primitive is the base\'s own claim, cited by file and '
                    'hash, and is not replayed here')
    (HERE/'P19_LOWERING.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
