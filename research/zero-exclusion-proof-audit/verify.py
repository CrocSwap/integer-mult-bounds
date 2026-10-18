#!/usr/bin/env python3
"""Finite E8 facts used implicitly by PR1560's proof of Theorem 1 and Corollary 2, checked for EVERY pivot frame.

PR1560 (an664) proves a structural zero-exclusion criterion for a pivot frame F of the 120 doubled E8 lines.
Its proof (proof.md sections 2, 4 and 6) silently uses several facts about the lines relative to F. PR1560's own
checker establishes them only for its fixed pivot; PR1616 and PR1650 apply the theorem at hundreds of other pivots.
This file was written from proof.md's prose alone (it does not import or read PR1560's, PR1616's or PR1650's
code) and checks, for all 2025 frames F:

  E1  expansion: 2 v_i = sum_{k in F} G_ik v_k for every line i (gives identity (6) and sum_k G_ik G_jk = 2 G_ij);
  E2  pivot rows: G_fk = 2 delta_fk; every nonpivot row has G_ik in {0, +1, -1} and |T_i| = 4;
  E3  blocks: exactly 14 supports occur, each carried by exactly 8 lines, and they form a Steiner system
      S(3,4,8) on F (every triple of pivots in exactly one block);
  E4  classes: in each block the sign product prod_{k in T} eps_ik splits the 8 lines 4 + 4; lines in one class
      are mutually orthogonal, lines in opposite classes have G = +-1, and class + (F minus T) is a frame;
  E5  Hadamard: for every class C and k in T, the rows (1, s_i), i in C, satisfy H H^T = 4 I;
  E6  the 4+1 step (section 4.3): for every block, class C, distinguished k, exceptional row i0 in C and line j of
      the opposite class, the three signs s_{i0,l} s_{j,l} have product -1 and the shared diagonal formula with
      c_kl = s_{i0,l}/4 predicts w_j in {1/2, -1/2}, a value that is neither root 0 nor 1 of x^2 - x;
  E7  the class-sum dichotomy: four values in {x, 1-x} summing to 1 are all 1/4 or a permutation of (1,0,0,0)
      (exact over Q for the case analysis m = 0..4 used in section 4.3);
  E8  the gauge corollary's last step: for nonpivot i, j, sum_{k in F} eps_ik eps_jk = 2 G_ij (E1 restated on rows).

Standard library only, exact integer / Fraction arithmetic. Run from the repository root:

    python3 -I -B research/zero-exclusion-proof-audit/verify.py [--controls-only]
"""

import itertools
import sys
from fractions import Fraction

RESULTS = []


def check(tag, cond, info=''):
    RESULTS.append(tag)
    print(f"{'PASS' if cond else 'FAIL'} {tag}" + (f': {info}' if info else ''), flush=True)
    if not cond:
        print(f'FAIL_ZERO_EXCLUSION_PROOF_AUDIT: {tag}')
        sys.exit(1)


# ------------------------------------------------------------------ the model, from proof.md section 2's prose

def doubled_lines():
    """Doubled E8 roots (squared length 8) with first nonzero coordinate positive, sorted lexicographically."""
    out = set()
    for a, b in itertools.combinations(range(8), 2):
        for sa in (2, -2):
            for sb in (2, -2):
                v = [0] * 8
                v[a], v[b] = sa, sb
                out.add(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            out.add(signs)
    return sorted(v for v in out if next(x for x in v if x) > 0)


V = doubled_lines()
N = len(V)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


GRAM = [[dot(V[i], V[j]) for j in range(N)] for i in range(N)]
G = [[g // 4 for g in row] for row in GRAM]


def all_frames():
    """Every 8-clique of the orthogonality graph, by increasing-ID recursion (each visited once)."""
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(tuple(cur))
            return
        for n, j in enumerate(cand):
            grow(cur + [j], [k for k in cand[n + 1:] if G[j][k] == 0])

    grow([], list(range(N)))
    return out


def facts_at(F, frameset):
    """Check E1-E6 and E8 at pivot frame F. Returns a count tuple, or a string naming the first failure."""
    # E1 (and E8): the expansion of every line in the orthogonal basis F.
    for i in range(N):
        for c in range(8):
            if 2 * V[i][c] != sum(G[i][k] * V[k][c] for k in F):
                return f'E1 line {i}'
    # E2: pivot rows and nonpivot supports.
    supp = {}
    for i in range(N):
        row = [G[i][k] for k in F]
        if i in F:
            if row != [2 if k == i else 0 for k in F]:
                return f'E2 pivot {i}'
            continue
        if any(g not in (0, 1, -1) for g in row):
            return f'E2 values {i}'
        T = tuple(n for n in range(8) if row[n])
        if len(T) != 4:
            return f'E2 support {i}'
        supp.setdefault(T, []).append(i)
    # E3: 14 blocks of 8 lines, a Steiner system S(3,4,8).
    if len(supp) != 14 or any(len(v) != 8 for v in supp.values()):
        return 'E3 blocks'
    for tri in itertools.combinations(range(8), 3):
        if sum(set(tri) <= set(T) for T in supp) != 1:
            return f'E3 triple {tri}'
    n_e6 = 0
    for T, lines in supp.items():
        eps = {i: {k: G[i][F[k]] for k in T} for i in lines}
        prod = {i: eps[i][T[0]] * eps[i][T[1]] * eps[i][T[2]] * eps[i][T[3]] for i in lines}
        classes = [[i for i in lines if prod[i] == 1], [i for i in lines if prod[i] == -1]]
        # E4: 4 + 4, orthogonal inside a class, G = +-1 across, class + (F minus T) is a frame.
        if sorted(map(len, classes)) != [4, 4]:
            return f'E4 sizes {T}'
        for C in classes:
            if any(G[a][b] for a, b in itertools.combinations(C, 2)):
                return f'E4 orthogonal {T}'
            if tuple(sorted(C + [F[n] for n in range(8) if n not in T])) not in frameset:
                return f'E4 frame {T}'
        if any(abs(G[a][b]) != 1 for a in classes[0] for b in classes[1]):
            return f'E4 across {T}'
        for C, D in (classes, classes[::-1]):
            for k in T:
                rest = [l for l in T if l != k]
                s = {i: [eps[i][k] * eps[i][l] for l in rest] for i in lines}
                # E5: Hadamard rows (1, s_i) for i in C.
                H = [[1] + s[i] for i in C]
                if any(dot(H[a], H[b]) != (4 if a == b else 0) for a in range(4) for b in range(4)):
                    return f'E5 {T} {k}'
                # E6: exceptional row i0 and opposite-class line j.
                for i0 in C:
                    c = [Fraction(x, 4) for x in s[i0]]
                    # the coefficients are the unique solution of the shared formula with w = e_{i0} on C
                    for i in C:
                        w = Fraction(1, 4) + sum(cl * x for cl, x in zip(c, s[i]))
                        if w != (1 if i == i0 else 0):
                            return f'E6 solve {T} {k} {i0}'
                    for j in D:
                        p = s[i0][0] * s[j][0] * s[i0][1] * s[j][1] * s[i0][2] * s[j][2]
                        w = Fraction(1, 4) + sum(cl * x for cl, x in zip(c, s[j]))
                        if p != -1 or w not in (Fraction(1, 2), Fraction(-1, 2)) or w * w - w == 0:
                            return f'E6 {T} {k} {i0} {j}'
                        n_e6 += 1
    # E8: the identity used for nonpivot pairs in Corollary 2.
    non = [i for i in range(N) if i not in F]
    for i, j in itertools.combinations(non, 2):
        if sum(G[i][k] * G[j][k] for k in F) != 2 * G[i][j]:
            return f'E8 {i} {j}'
    return (len(supp), n_e6)


def dichotomy():
    """E7: solve m x + (4 - m)(1 - x) = 1 for m = 0..4, where m counts the values equal to x (a root of
    x^2 - x + q) and the rest equal 1 - x. Returns the set of possible sorted 4-tuples of values."""
    out = set()
    for m in range(5):
        # (2m - 4) x = 1 - (4 - m)
        a, b = 2 * m - 4, 1 - (4 - m)
        if a == 0:
            if b == 0:
                return None  # would leave x free: not the case
            continue
        x = Fraction(b, a)
        out.add(tuple(sorted([x] * m + [1 - x] * (4 - m))))
    return out


def main():
    controls_only = '--controls-only' in sys.argv[1:]
    check('model.lines', N == 120 and len(V) == len(set(V)) and all(dot(v, v) == 8 for v in V),
          '120 doubled lines of squared length 8')
    check('model.gram', all(GRAM[i][j] % 4 == 0 for i in range(N) for j in range(N))
          and {G[i][j] for i in range(N) for j in range(N) if i != j} == {-1, 0, 1}, 'G = <v_i, v_j>/4 in {0, +-1} off the diagonal')
    frames = all_frames()
    frameset = set(frames)
    F0 = (0, 1, 6, 11, 20, 29, 106, 119)
    F1560 = (2, 5, 8, 9, 30, 41, 108, 117)
    check('model.frames', len(frames) == 2025 and F0 in frameset and F1560 in frameset,
          "2025 frames; PR1560's FRAME0 and pivot F are frames under these IDs")
    sols = dichotomy()
    check('E7.dichotomy', sols == {(Fraction(1, 4),) * 4, (0, 0, 0, 1)},
          'four values in {x, 1-x} with sum 1: all 1/4, or {1, 0, 0, 0} up to order')

    # Negative controls: each fact must be falsifiable by the check that is meant to catch it. The third entry is
    # an illustration (an arithmetic identity), not a rejection control.
    bad = list(frames[0])
    bad[0] = next(i for i in range(N) if i not in bad and G[i][bad[1]] == 0)  # not a frame any more
    check('control.non-frame-pivot', isinstance(facts_at(tuple(bad), frameset), str),
          'replacing one pivot breaks the expansion / support facts')
    r = facts_at(F1560, frameset - {tuple(sorted([22, 27, 34, 37] + [8, 9, 108, 117]))})
    check('control.missing-class-frame', isinstance(r, str) and r.startswith('E4 frame'),
          'removing a class-completion frame from the frame list is detected: ' + str(r))
    check('illustration.same-class-witness', all(
        Fraction(1, 4) + sum(Fraction(a * b, 4) for a, b in zip(s0, s0)) == 1
        for s0 in itertools.product((1, -1), repeat=3)),
        'a same-class "witness" (j = i0) reproduces w = 1, so the opposite parity of j is what forces 1/2 or -1/2')
    if controls_only:
        print('PASS_ZERO_EXCLUSION_PROOF_AUDIT_CONTROLS_ONLY')
        return

    total_e6 = 0
    for n, F in enumerate(frames):
        res = facts_at(F, frameset)
        if isinstance(res, str):
            check('facts.all-frames', False, f'frame {n} {F}: {res}')
        total_e6 += res[1]
    check('facts.all-frames', True,
          f'E1-E6 and E8 hold at all {len(frames)} pivot frames; {total_e6} exceptional 4+1 configurations checked')
    print('PASS_ZERO_EXCLUSION_PROOF_AUDIT')


if __name__ == '__main__':
    main()
