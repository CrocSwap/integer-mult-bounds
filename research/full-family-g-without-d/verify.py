#!/usr/bin/env python3
"""(G) does not imply (D) even for the family of ALL live frames: an exact counterexample on an 8-line deletion of
P112 (a P104 live set), for PR1560's frame-incidence criterion as implemented in PR1650.

Standard library only, exact integer/rational arithmetic. Self-contained: the E8 line model, frame enumeration
and the four conditions (D), (G), (W), nonempty blocks follow PR1650's `verify.py` (session 9, head d960f8a2),
re-typed here so this file does not depend on an unmerged package. Run from the repository root:

    python3 -I -B research/full-family-g-without-d/verify.py

Checks, for each fixture (deleted set X, pivot frame F), with the family of all 784 live frames of P112 \\ X:
  1. F is a live frame; nonempty blocks, (W) and (G) hold;
  2. (D) fails: on I_k for one pivot k, the incidence matrix has exact rational rank |I_k| - 8 < |I_k| - 7
     (Fraction elimination), while the seven vectors h_kl are independent and lie in its kernel;
  3. each fixture carries a sparse integer kernel vector x (entries +-1 on eight lines) with every live
     frame's row orthogonal to x and rank [h; x] = 8, which certifies the rank drop without elimination;
  4. control: restoring any one of the eight deleted lines makes the same pivot pass all four conditions
     (mod-p rank lower bound plus the h_kl kernel upper bound, as in PR1650);
  5. controls: a mutated certificate is rejected; the pivot-alone sub-family fails (G);
  6. each certificate is explained: every one of the 2025 E8 frames meets two orthogonal 12-line D4 subsystems
     Da, Db equally (fixture 1: the coordinate halves), and x is the difference of their live indicator vectors.
"""

import itertools
import sys
from fractions import Fraction

PRIME = 1000003


def check(tag, cond, info=''):
    print(f"{'PASS' if cond else 'FAIL'} {tag}" + (f': {info}' if info else ''), flush=True)
    if not cond:
        print(f'FAIL_FULL_FAMILY_G_WITHOUT_D: {tag}')
        sys.exit(1)


# ---------------------------------------------------------------- E8 model (doubled coordinates, norm 8)

def lines_e8():
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for sj in (2, -2):
            v = [0] * 8
            v[i], v[j] = 2, sj
            out.add(tuple(v))
    for s in itertools.product((1, -1), repeat=7):
        v = (1,) + s
        if v.count(-1) % 2 == 0:
            out.add(v)
    return sorted(out)


# Line IDs are positions in this sorted list; they agree with PR1560's and PR1650's IDs.
LINES = lines_e8()
NL = len(LINES)
IDX = {v: n for n, v in enumerate(LINES)}


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
FRAME0 = (0, 1, 6, 11, 20, 29, 106, 119)
P112 = [i for i in range(NL) if i not in FRAME0]


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


def frames_inside(live):
    live = sorted(live)
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(tuple(cur))
            return
        for n, j in enumerate(cand):
            grow(cur + [j], [k for k in cand[n + 1:] if G[j][k] == 0])

    grow([], live)
    return out


FRAMES = frames_inside(range(NL))

# ---------------------------------------------------------------- fixtures (found by deletion walks, see README)

# split = (Da, Db): two disjoint 12-line D4 subsystems, each containing 4 FRAME0 lines. Fixture 1's are the
# coordinate halves (Da on coordinates 0-3, Db on 4-7); fixture 2's were found as an image of those under the
# FRAME0 stabiliser (search/mech.py); verify.py checks only the properties it uses.
# The certificate is x = 1 on the live lines of Da, -1 on the live lines of Db.
FIXTURES = [
    dict(X=(3, 4, 8, 9, 107, 108, 117, 118), F=(19, 25, 37, 47, 67, 82, 94, 115), k=2,
         split=((20, 29, 30, 31, 40, 41, 106, 107, 108, 117, 118, 119), tuple(range(12))),
         cert={30: 1, 31: 1, 40: 1, 41: 1, 2: -1, 5: -1, 7: -1, 10: -1}),
    dict(X=(13, 18, 22, 27, 34, 35, 36, 37), F=(17, 25, 38, 52, 61, 75, 98, 116), k=7,
         split=((0, 1, 34, 35, 36, 37, 106, 111, 112, 113, 114, 119), (6, 11, 12, 13, 18, 19, 20, 21, 22, 27, 28, 29)),
         cert={111: 1, 112: 1, 113: 1, 114: 1, 12: -1, 19: -1, 21: -1, 28: -1}),
]



# ---------------------------------------------------------------- ranks

def rank_fraction(rows):
    """Exact rank over Q by Fraction Gaussian elimination."""
    basis = []  # (pivot column, row)
    for r in rows:
        v = [Fraction(x) for x in r]
        for c, b in basis:
            if v[c]:
                a = v[c]
                v = [x - a * y for x, y in zip(v, b)]
        c = next((j for j, x in enumerate(v) if x), None)
        if c is not None:
            v = [x / v[c] for x in v]
            basis.append((c, v))
    return len(basis)


def rank_mod(rows):
    """Rank modulo PRIME (a lower bound on the rank over Q)."""
    basis = {}
    for row in rows:
        v = [x % PRIME for x in row]
        for j in sorted(basis):
            if v[j]:
                a, w = v[j], basis[j]
                v = [(x - a * y) % PRIME for x, y in zip(v, w)]
        j = next((j for j, x in enumerate(v) if x), None)
        if j is not None:
            inv = pow(v[j], -1, PRIME)
            basis[j] = [x * inv % PRIME for x in v]
    return len(basis)


# ---------------------------------------------------------------- PR1560's four conditions at one pivot

def setup(X, F, frames=None):
    dead = set(FRAME0) | set(X)
    live_frames = [Fr for Fr in FRAMES if not dead & set(Fr)] if frames is None else frames
    non = [i for i in P112 if i not in dead and i not in F]
    odd = {i: tuple(n for n in range(8) if G[i][F[n]]) for i in non}
    return live_frames, non, odd


def blocks_w(F, non, odd):
    """(nonempty-blocks ok, W ok). Block of i = its odd pivot 4-set; class = parity of negative signs on it."""
    blocks = {}
    for i in non:
        t = odd[i]
        assert len(t) == 4
        blocks.setdefault(t, [0, 0])[sum(G[i][F[n]] < 0 for n in t) % 2] += 1
    cov = set()
    for t, (c0, c1) in blocks.items():
        if (c0 == 4 and c1) or (c1 == 4 and c0):
            cov.update(itertools.combinations(t, 2))
    return len(blocks) == 14, len(cov) == 28


def condition_g(non, odd, live_frames):
    """For each pivot pair kl: the graph on I_kl (i, j joined when a live frame meets I_kl in exactly {i, j})
    is connected."""
    traces = {frozenset(Fr) & frozenset(non) for Fr in live_frames}
    for p in itertools.combinations(range(8), 2):
        I = {i for i in non if p[0] in odd[i] and p[1] in odd[i]}
        par = {i: i for i in I}

        def find(a):
            while par[a] != a:
                a = par[a]
            return a

        for s in traces:
            e = s & I
            if len(e) == 2:
                a, b = sorted(e)
                par[find(a)] = find(b)
        if len({find(i) for i in I}) != 1:
            return False
    return True


def incidence(F, k, non, live_frames):
    I = [i for i in non if G[i][F[k]]]
    rows = sorted({tuple(1 if i in Fr else 0 for i in I) for Fr in live_frames})
    h = [[G[i][F[k]] * G[i][F[l]] for i in I] for l in range(8) if l != k]
    return I, rows, h


def kernel_ok(rows, vecs):
    return all(sum(a * b for a, b in zip(r, v)) == 0 for r in rows for v in vecs)


def condition_d_modp(F, non, live_frames):
    """PR1650's (D) test: h_kl independent and in the kernel, incidence rank mod p reaches |I_k| - 7."""
    for k in range(8):
        I, rows, h = incidence(F, k, non, live_frames)
        if rank_mod(h) != 7 or not kernel_ok(rows, h) or rank_mod(rows) != len(I) - 7:
            return False
    return True


def main():
    check('model', NL == 120 and len(FRAMES) == 2025 and is_frame(FRAME0), f'{NL} lines, {len(FRAMES)} frames')
    for n, fx in enumerate(FIXTURES, 1):
        X, F, k = fx['X'], fx['F'], fx['k']
        tag = f'fixture{n}'
        check(f'{tag}.pivot', is_frame(F) and not set(F) & (set(X) | set(FRAME0)) and len(set(X)) == 8
              and set(X) <= set(P112), f'X={X} F={F}')
        live_frames, non, odd = setup(X, F)
        nb, w = blocks_w(F, non, odd)
        check(f'{tag}.premises', nb and w and condition_g(non, odd, live_frames),
              f'{len(live_frames)} live frames (all of them); nonempty blocks, (W), (G) hold')
        bad = []
        for kk in range(8):
            I, rows, h = incidence(F, kk, non, live_frames)
            check(f'{tag}.h{kk}', rank_fraction(h) == 7 and kernel_ok(rows, h))
            r = rank_fraction(rows)
            if r != len(I) - 7:
                bad.append((kk, len(I), r))
        check(f'{tag}.D-fails', [b[0] for b in bad] == [k] and bad[0][2] == bad[0][1] - 8,
              f'exact rank over Q on I_{k}: {bad[0][2]} = |I_k| - 8 with |I_k| = {bad[0][1]}; other k pass')
        I, rows, h = incidence(F, k, non, live_frames)
        x = [fx['cert'].get(i, 0) for i in I]
        check(f'{tag}.certificate', set(fx['cert']) <= set(I) and kernel_ok(rows, [x]) and rank_fraction(h + [x]) == 8,
              f'integer kernel vector {fx["cert"]} is orthogonal to every live frame and outside span(h)')
        # Why: every E8 frame meets Da and Db in equally many lines; FRAME0 and X leave 4 live lines in each, all
        # odd to F[k], so x = 1_(Da live) - 1_(Db live) is orthogonal to every live frame's trace on I_k.
        Da, Db = (set(d) for d in fx['split'])
        dead = set(X) | set(FRAME0)
        check(f'{tag}.balanced-d4', len(Da) == len(Db) == 12 and not Da & Db
              and len(Da & set(FRAME0)) == len(Db & set(FRAME0)) == 4
              and all(G[a][b] in (0, 1, -1) for a in Da for b in Da if a != b) and all(G[a][b] == 0 for a in Da for b in Db)
              and all(len(Da & set(Fr)) == len(Db & set(Fr)) for Fr in FRAMES)
              and fx['cert'] == {**{i: 1 for i in Da - dead}, **{i: -1 for i in Db - dead}},
              f'Da, Db orthogonal 12-line systems; all 2025 frames meet them equally; certificate = 1 on Da live '
              f'{sorted(Da - dead)}, -1 on Db live {sorted(Db - dead)}')
        if n == 1:
            check(f'{tag}.coordinate-halves', Da == {i for i, v in enumerate(LINES) if not any(v[4:])}
                  and Db == {i for i, v in enumerate(LINES) if not any(v[:4])})
        y = list(x)
        y[I.index(next(iter(fx['cert'])))] *= -1
        check(f'{tag}.control.mutated-certificate', not kernel_ok(rows, [y]))
        for x in X:
            Y = tuple(i for i in X if i != x)
            lf, nn, oo = setup(Y, F)
            nb, w = blocks_w(F, nn, oo)
            ok = nb and w and condition_g(nn, oo, lf) and condition_d_modp(F, nn, lf)
            check(f'{tag}.control.restore-{x}', ok, f'{len(lf)} live frames; all four conditions pass')
        lf, nn, oo = setup(X, F, frames=[F])
        check(f'{tag}.control.pivot-alone-fails-G', not condition_g(nn, oo, lf))
    print('PASS_FULL_FAMILY_G_WITHOUT_D fixtures=2: (W), nonempty blocks and (G) on the full live family do not '
          'imply (D) (exact), and restoring any one deleted line makes the same pivot pass')


if __name__ == '__main__':
    if sys.flags.optimize:
        sys.exit('refusing to run with -O')
    main()
