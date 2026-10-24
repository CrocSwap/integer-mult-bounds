#!/usr/bin/env python3
"""A design-frame word: triangular scalar programs around the required diagonal.

The controller word is one factorisation of the required diagonal,

    M = A . D . B          (A, B scalar programs, D the monomial letters)

and the base already prices A and B as its left/right scalar programs.  Nothing forces A and
B to be the controller's choice.  This receipt takes the other extreme:

    M_new = T . D . T^-1        with T unit lower triangular (a pure shear cascade),

which has two properties the controller word lacks:

  * every row of M_new is supported on the diagonal monomials of roles <= i, so the realised
    row frames are prefixes -- the design convention -- natively, not after any gauge;
  * the diagonal is unchanged, so the required outputs and denominators are the same, and the
    paid jobs D are the same.

Both A -> T and B -> T^-1 are scalar programs, i.e. shears, which the native word already
contains as `scalar` operations.  The receipt checks, per p: retained-stage discipline, that
`factor` succeeds, the diagonal equals the controller's required diagonal, and the realised
row frames equal the design frames.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def matmul(X, Y):
    n = len(X)
    return [[sum(X[i][k]*Y[k][j] for k in range(n) if X[i][k] and Y[k][j]) for j in range(n)]
            for i in range(n)]

def matinv(X):
    n = len(X)
    M = [row[:] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(X)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c])
        M[c], M[p] = M[p], M[c]
        f = M[c][c]
        M[c] = [x/f for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                g = M[r][c]
                M[r] = [a - g*b for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]

def main():
    mod = load('c4940_design', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    out = {'status': 'DESIGN_WORD_PROBE', 'cases': {}}
    for p, pat in ((3, 'IT'), (4, 'IIT'), (5, 'IITT')):
        thick = frozenset(range(1, 2*p, 2))
        co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
        th = mod.thin(co, thick)
        base = C.factor(th)
        need(base is not None, 'the controller factorises at p=%d' % p)
        D_list = base['diagonal']                      # the required diagonal, per role
        n = len(D_list)

        # T: unit lower triangular with generic shears
        T = [[Q(1) if i >= j else Q(0) for j in range(n)] for i in range(n)]
        Ti = matinv(T)

        keys = sorted(set(D_list))
        coeffs = {}
        for key in keys:
            E = [[Q(int(D_list[i] == key and i == j)) for j in range(n)] for i in range(n)]
            coeffs[key] = matmul(matmul(T, E), Ti)
        coeffs = {k: v for k, v in coeffs.items() if any(any(r) for r in v)}

        # retained-stage discipline
        bad = [k for k in coeffs if any(bit and (s not in thick) for s, bit in enumerate(k[1:]))]
        need(not bad, 'every coefficient of the new word uses only retained stages at p=%d' % p)

        # realised row frames
        rows = {i: set() for i in range(n)}
        for key, m in coeffs.items():
            sel = {s for s, bit in enumerate(key[1:]) if bit}
            for i in range(n):
                if any(m[i][j] for j in range(n)): rows[i] |= sel
        sizes = Counter(len(rows[i]) for i in range(n))
        full = frozenset(range(2*p+1)); outs = [full, full]
        for i, ch in enumerate(pat, 1):
            outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
        des = [sorted(s & thick) for s in outs]
        des_sizes = Counter(len(s) for s in des)
        frames = [sorted(rows[i]) for i in range(n)]

        # factor must succeed and reproduce the diagonal
        r2 = C.factor(coeffs)
        diag2 = None if r2 is None else sorted(Counter(sum(t[1:]) for t in r2['diagonal']).items())
        want = sorted(Counter(sum(t[1:]) for t in D_list).items())
        out['cases']['p%d_%s' % (p, pat)] = {
            'realised_frames': frames, 'designed_frames': des,
            'frame_match': frames == des,
            'realised_sizes': dict(sorted(sizes.items())),
            'designed_sizes': dict(sorted(des_sizes.items())),
            'factorises': r2 is not None, 'diagonal_required': want, 'diagonal_actual': diag2,
            'diagonal_match': diag2 == want}
        print('p=%d %-4s frames %s' % (p, pat, [len(f) for f in frames]))
        print('        designed %s   frame_match %s   factorises %s   diagonal %s == %s : %s'
              % ([len(f) for f in des], frames == des, r2 is not None, diag2, want, diag2 == want))

    ok = all(v['frame_match'] and v['factorises'] and v['diagonal_match'] for v in out['cases'].values())
    out['status'] = 'PASS_DESIGN_WORD' if ok else 'FINDING_DESIGN_WORD_FAILS'
    out['rule'] = 'T unit lower triangular; M_new = T D T^-1; D the controller diagonal'
    (HERE/'P19_DESIGNWORD.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
