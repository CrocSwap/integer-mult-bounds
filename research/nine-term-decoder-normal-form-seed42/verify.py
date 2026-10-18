#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nine-term complex E8 decoders: exact normal form, census facts and constructions (no new kappa).

Standard library only, exact integer / F2 / rational arithmetic.  Run from the repository root:

    python3 -I -B research/nine-term-decoder-normal-form-seed42/verify.py [--out FILE.json]

Sections (each prints PASS/FAIL lines; exit status 1 on any FAIL):
  A  model: 120 lines, rank-9 label pairing, code weights
  B  spanning census: all 511 codeword supports span R^8 (=> every nonzero normal has full label span
     on P120); all 130305 pairwise support intersections; U1 = 56, U2 = 84
  C  Theorem A / Corollary B / Corollary C on explicit exact decoders (P112 and P120), the PR1180-shaped
     outside-code example, a two-sided m=9 control (inexact) and an exact two-sided m=10 example
  D  Lemma D (merging parallel column normals) on explicit instances
  E  Proposition F (ratio classes, pairwise hyperplane) on every frame of section F
  F  weight frames of maximal subsystems (A8, A7+A1, A2+E6, A3+D5) and frame+root decoders: exact
     identities on all live pairs, P120 cost formula, recorded costs
  G  negative controls
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e8lab as E  # noqa: E402

FAILS, LOG, CERT = [], [], {}


def check(tag, cond, info=''):
    line = ('PASS ' if cond else 'FAIL ') + tag + (' | ' + info if info else '')
    print(line, flush=True)
    LOG.append(line)
    if not cond:
        FAILS.append(tag)


# ============================================================================ A. model
def section_a():
    check('A1 120 lines', E.N == 120)
    check('A2 label pairing F2 rank 9', E.f2_rank(E.M) == 9)
    check('A3 pairing rows distinct', len(set(E.M)) == 120)
    basis, words = E.code_words()
    wt = Counter(E.popcount(w) for w in words)
    check('A4 code weights {56:255, 64:255, 120:1}', dict(wt) == {56: 255, 64: 255, 120: 1}, str(dict(wt)))
    CERT['code_weights'] = dict(wt)
    return words


# ============================================================================ B. spanning census
def section_b(words, full_pairs=True):
    ranks = Counter(E.line_rank(w) for w in words)
    check('B1 every nonzero codeword support spans R^8', dict(ranks) == {8: 511}, str(dict(ranks)))
    # consequence: for every nonzero normal b (real or complex), C(b) on P120 has label span 9
    # (dim V_X <= 8 iff X misses some support; C(b) misses supp(w) iff supp(w) lies in b-perp).
    U1 = min(E.popcount(w) for w in words)
    check('B2 U1 = 56 (largest set of label span <= 8 has 64 lines)', U1 == 56)
    cnt, U2, sizes = Counter(), 120, Counter()
    if full_pairs:
        for a in range(len(words)):
            wa = words[a]
            for b in range(a + 1, len(words)):
                inter = wa & words[b]
                r = E.line_rank(inter)
                cnt[r] += 1
                if r < 8:
                    sizes[(E.popcount(inter), r)] += 1
                U2 = min(U2, E.popcount(wa | words[b]))
        check('B3 pairwise intersections: 130305 pairs, rank census {8:91050, 7:35640, 6:3360, 0:255}',
              dict(cnt) == {8: 91050, 7: 35640, 6: 3360, 0: 255}, str(dict(cnt)))
        check('B4 deficient intersections have (size, rank) in {(0,0),(28,7),(32,7),(36,6)}',
              set(sizes) == {(0, 0), (28, 7), (32, 7), (36, 6)}, str(dict(sizes)))
        check('B5 U2 = 84 (largest set of label span <= 7 has 36 lines)', U2 == 84)
        CERT['pairwise_intersection_rank_census'] = {str(k): v for k, v in sorted(cnt.items())}
        CERT['deficient_intersection_size_rank'] = {f'{s},{r}': v for (s, r), v in sorted(sizes.items())}
    CERT['U1'], CERT['U2'] = U1, U2 if full_pairs else None


# ============================================================================ frames and representations
class Frame:
    """Nine column normals b_0..b_8 (doubled coordinates, rational) spanning R^8 with one dependency z."""

    def __init__(self, name, vecs):
        self.name = name
        self.F = [tuple(Q(x) for x in v) for v in vecs]
        if len(self.F) != 9 or E.q_rank([list(v) for v in self.F]) != 8:
            raise ValueError('a frame needs nine vectors spanning R^8')
        for drop in range(9):
            basis = [self.F[k] for k in range(9) if k != drop]
            if E.q_rank([list(v) for v in basis]) == 8:
                break
        self.drop = drop
        cols = [list(c) for c in zip(*basis)]  # 8x8, columns = basis vectors
        self.inv = E.q_inv(cols)
        zb = self._solve(self.F[drop])
        self.z = self._lift(zb, Q(-1))
        if any(sum(self.z[k] * self.F[k][c] for k in range(9)) != 0 for c in range(8)):
            raise ValueError('dependency check failed')
        self.S = [k for k in range(9) if self.z[k] != 0]

    def _solve(self, v):
        return [sum(self.inv[r][c] * v[c] for c in range(8)) for r in range(8)]

    def _lift(self, c8, at_drop):
        out, j = [], 0
        for k in range(9):
            if k == self.drop:
                out.append(at_drop)
            else:
                out.append(c8[j])
                j += 1
        return out

    def base(self, i):
        """One coefficient vector c with sum_k c_k b_k = 2 r_i."""
        return self._lift(self._solve([2 * Q(x) for x in E.LINES[i]]), Q(0))

    def options(self, i):
        """All supports of c0 + t z: critical t (one per ratio class) and one generic t."""
        c0 = self.base(i)
        ts = sorted({-c0[k] / self.z[k] for k in self.S})
        generic = (ts[-1] + 1) if ts else Q(1)
        out = []
        for t in ts + [generic]:
            c = [c0[k] + t * self.z[k] for k in range(9)]
            out.append((t, c))
        return out

    def sparsest(self, i):
        return min(self.options(i), key=lambda tc: (sum(1 for x in tc[1] if x != 0), tc[0]))[1]


def T_entry(j, b):
    return sum(Q(a) * x for a, x in zip(E.LINES[j], b)) / 4  # <r_j, b> in true units


def exact_on_pairs(rows, F, live):
    """D T^T = 2 G on all live pairs, where T_jk = <r_j, b_k>."""
    idx = list(E.bits(live))
    Tm = {j: [T_entry(j, b) for b in F] for j in idx}
    for i in idx:
        d = rows[i]
        for j in idx:
            if sum(x * y for x, y in zip(d, Tm[j])) != 2 * E.G[i][j]:
                return False, (i, j)
    return True, len(idx) ** 2


def decoder_cost(rows, F, live):
    X = [0] * len(F)
    for i in E.bits(live):
        for k, x in enumerate(rows[i]):
            if x != 0:
                X[k] |= 1 << i
    Y = [E.support(b, live) for b in F]
    per = [E.pairing_rank(X[k], Y[k]) for k in range(len(F))]
    return per, X, Y


def coordinate_frame():
    F0 = []
    for i in range(E.N):
        if all(E.G[i][j] == 0 for j in F0):
            F0.append(i)
        if len(F0) == 8:
            return F0


# ============================================================================ C. normal form
def decompose(D, T, live):
    """Theorem A decomposition D = R A' + N1, T = R B' + N2 with R^T N = 0 (exact)."""
    idx = list(E.bits(live))
    R = [[Q(x) for x in E.LINES[i]] for i in idx]
    Rt = E.transpose(R)
    G0inv = E.q_inv(E.matmul(Rt, R))
    P = E.matmul(G0inv, Rt)  # 8 x L left inverse
    A = E.matmul(P, D)
    B = E.matmul(P, T)
    N1 = [[d - r for d, r in zip(drow, rrow)] for drow, rrow in zip(D, E.matmul(R, A))]
    N2 = [[d - r for d, r in zip(drow, rrow)] for drow, rrow in zip(T, E.matmul(R, B))]
    return R, A, B, N1, N2


def is_zero(Mx):
    return all(x == 0 for row in Mx for x in row)


def theorem_a_checks(tag, D, T, live, expect_one_sided=True):
    R, A, B, N1, N2 = decompose(D, T, live)
    Rt = E.transpose(R)
    m = len(D[0])
    ABt = E.matmul(A, E.transpose(B))
    # doubled coordinates: R R^T = 4 G, so D T^T = 2G = R R^T / 2 gives A' B'^T = I/2
    check(f'{tag} A\'B\'^T = I/2 (doubled coordinates)',
          all(ABt[r][c] == (Q(1, 2) if r == c else 0) for r in range(8) for c in range(8)))
    check(f'{tag} R^T N1 = 0 and R^T N2 = 0', is_zero(E.matmul(Rt, N1)) and is_zero(E.matmul(Rt, N2)))
    check(f'{tag} N1 B\'^T = 0, A\' N2^T = 0, N1 N2^T = 0',
          is_zero(E.matmul(N1, E.transpose(B))) and is_zero(E.matmul(A, E.transpose(N2)))
          and is_zero(E.matmul(N1, E.transpose(N2))))
    zs = E.q_nullspace(B, m)
    ys = E.q_nullspace(A, m)
    check(f'{tag} dim ker B\' = dim ker A\' = m-8 = {m - 8}', len(zs) == len(ys) == m - 8)
    pair = [[sum(a * b for a, b in zip(y, z)) for z in zs] for y in ys]
    check(f'{tag} ker A\' x ker B\' dot pairing nondegenerate', E.q_rank(pair) == m - 8)
    n1z, n2z = is_zero(N1), is_zero(N2)
    if m == 9 and expect_one_sided:
        check(f'{tag} Corollary B: at most one factor leaves the root code', n1z or n2z,
              f'N1 zero={n1z}, N2 zero={n2z}')
    return n1z, n2z


def section_c(rng):
    F0 = coordinate_frame()
    P112 = E.FULL
    for i in F0:
        P112 &= ~(1 << i)
    out = {}
    # C1: coordinate frame + one extra root column normal, random rational t per line (Corollary C form)
    extra = next(i for i in range(E.N) if i not in F0 and sum(1 for f in F0 if E.G[i][f]) == 4)
    fr = Frame('coord+root', [E.LINES[f] for f in F0] + [E.LINES[extra]])
    for lname, live in (('P120', E.FULL), ('P112', P112)):
        rows = {}
        for i in E.bits(live):
            c0 = fr.base(i)
            t = Q(rng.randint(-7, 7), rng.randint(1, 5))
            rows[i] = [c0[k] + t * fr.z[k] for k in range(9)]
        ok, info = exact_on_pairs(rows, fr.F, live)
        check(f'C1 {lname}: random one-sided 9-term decoder (frame+root, random t_i) is exact', ok, str(info))
        idx = list(E.bits(live))
        D = [rows[i] for i in idx]
        T = [[T_entry(j, b) for b in fr.F] for j in idx]
        n1z, n2z = theorem_a_checks(f'C1 {lname}', D, T, live)
        check(f'C1 {lname}: row factor leaves the root code, column factor does not', (not n1z) and n2z)
        per, X, Y = decoder_cost(rows, fr.F, live)
        out[f'C1_{lname}_random_cost'] = sum(per)
    # C2: PR1180-shaped outside-code identity on P112: (R0+e)R0^T + sum_{j>=1} Rj Rj^T + (-e)R0^T
    idx = list(E.bits(P112))
    ell = idx[0]
    # columns R_j = <r_i, f_j> (true units) for the coordinate frame lines f_j; an orthogonal frame of
    # norm-2 roots has sum_j f_j f_j^T = 2I, so sum_j R_j R_j^T = 2G
    cols = [[Q(E.dot(E.LINES[i], E.LINES[f]), 4) for i in idx] for f in F0]
    D = [[cols[j][a] + (Q(1) if (j == 0 and idx[a] == ell) else 0) for j in range(8)]
         + [Q(-1) if idx[a] == ell else Q(0)] for a in range(len(idx))]
    T = [[cols[j][a] for j in range(8)] + [cols[0][a]] for a in range(len(idx))]
    DT = E.matmul(D, E.transpose(T))
    ok = all(DT[a][b] == 2 * E.G[idx[a]][idx[b]] for a in range(len(idx)) for b in range(len(idx)))
    check('C2 PR1180-shaped outside-code nine-term identity exact on all 12544 P112 pairs', ok)
    n1z, n2z = theorem_a_checks('C2', D, T, P112)
    check('C2 its outside-code part sits in D only', (not n1z) and n2z)
    # C3: control -- two-sided junk at m = 9 is never exact
    rows = {i: fr.sparsest(i) for i in E.bits(E.FULL)}
    idx = list(E.bits(E.FULL))
    D = [rows[i] for i in idx]
    T = [[T_entry(j, b) for b in fr.F] for j in idx]
    R, A, B, N1, N2 = decompose(D, T, E.FULL)
    z = E.q_nullspace(B, 9)[0]
    y = E.q_nullspace(A, 9)[0]
    zy = sum(a * b for a, b in zip(z, y))
    check('C3 z.y != 0 at m = 9', zy != 0, str(zy))
    # a vector n in ker R^T: n = e_l - R (R^T R)^-1 R^T e_l
    Rt = E.transpose(R)
    G0inv = E.q_inv(E.matmul(Rt, R))

    def kernel_vec(a):
        e = [[Q(int(b == a))] for b in range(len(idx))]
        proj = E.matmul(R, E.matmul(G0inv, E.matmul(Rt, e)))
        return [e[b][0] - proj[b][0] for b in range(len(idx))]
    nvec, mvec = kernel_vec(3), kernel_vec(17)
    D2 = [[D[a][k] + nvec[a] * z[k] for k in range(9)] for a in range(len(idx))]
    T2 = [[T[a][k] + mvec[a] * y[k] for k in range(9)] for a in range(len(idx))]
    D1ok = all(sum(x * w for x, w in zip(D2[a], T[b])) == 2 * E.G[idx[a]][idx[b]]
               for a in range(0, 120, 7) for b in range(0, 120, 5))
    check('C3 one-sided junk n z^T alone keeps exactness (sampled pairs)', D1ok)
    bad = sum(1 for a in range(len(idx)) for b in range(len(idx))
              if sum(x * w for x, w in zip(D2[a], T2[b])) != 2 * E.G[idx[a]][idx[b]])
    check('C3 control: two-sided junk (n z^T, m y^T) at m = 9 is inexact', bad > 0, f'{bad} wrong entries')
    # C4: m = 10 admits exact two-sided junk (z1 . y = 0 possible)
    b9 = next(i for i in range(E.N) if i not in F0 and i != extra and sum(1 for f in F0 if E.G[i][f]) == 4)
    F10 = [tuple(Q(x) for x in E.LINES[f]) for f in F0] + [tuple(Q(x) for x in E.LINES[extra]),
                                                            tuple(Q(x) for x in E.LINES[b9])]
    D10 = [fr.sparsest(i) + [Q(0)] for i in idx]
    T10 = [[T_entry(j, b) for b in F10] for j in idx]
    R, A, B, N1, N2 = decompose(D10, T10, E.FULL)
    zs = E.q_nullspace(B, 10)
    ys = E.q_nullspace(A, 10)
    # choose z in ker B' and y in ker A' with z.y = 0
    z = zs[0]
    a0 = sum(p * q for p, q in zip(ys[0], z))
    a1 = sum(p * q for p, q in zip(ys[1], z))
    y = [a1 * p - a0 * q for p, q in zip(ys[0], ys[1])]
    check('C4 m = 10: found z in ker B\', y in ker A\' with z.y = 0, y != 0',
          sum(p * q for p, q in zip(z, y)) == 0 and any(y))
    D3 = [[D10[a][k] + nvec[a] * z[k] for k in range(10)] for a in range(len(idx))]
    T3 = [[T10[a][k] + mvec[a] * y[k] for k in range(10)] for a in range(len(idx))]
    DT = E.matmul(D3, E.transpose(T3))
    ok = all(DT[a][b] == 2 * E.G[idx[a]][idx[b]] for a in range(len(idx)) for b in range(len(idx)))
    check('C4 m = 10 decoder with junk on both factors is exact on all 14400 pairs', ok)
    n1z, n2z = theorem_a_checks('C4', D3, T3, E.FULL, expect_one_sided=False)
    check('C4 both factors leave the root code (Corollary B is specific to m = 9)', (not n1z) and (not n2z))
    CERT['section_C'] = out


# ============================================================================ D. merging lemma
def section_d(rng):
    F0 = coordinate_frame()
    # b_8 parallel to b_0: dependency support |S| = 2
    vecs = [E.LINES[f] for f in F0] + [tuple(2 * x for x in E.LINES[F0[0]])]
    fr = Frame('parallel', vecs)
    check('D1 dependency support of a parallel pair is {0, 8}', fr.S == [0, 8], str(fr.S))
    worst = None
    for trial in range(40):
        rows = {}
        for i in E.bits(E.FULL):
            c0 = fr.base(i)
            t = Q(rng.randint(-5, 5), rng.randint(1, 3))
            rows[i] = [c0[k] + t * fr.z[k] for k in range(9)]
        per, X, Y = decoder_cost(rows, fr.F, E.FULL)
        # merge: column 8 = 2 * column 0  -> single term with row c_0 + 2 c_8
        merged = {i: [rows[i][0] + 2 * rows[i][8]] + rows[i][1:8] for i in rows}
        mper, _, _ = decoder_cost(merged, fr.F[:8], E.FULL)
        ok, _ = exact_on_pairs(merged, fr.F[:8], E.FULL) if trial == 0 else (True, 0)
        if trial == 0:
            check('D2 merged eight-term decoder is exact on all 14400 pairs', ok)
        d = sum(per) - sum(mper)
        worst = d if worst is None else min(worst, d)
    check('D3 merging never increases cost (40 random one-sided decoders)', worst >= 0, f'min saving {worst}')


# ============================================================================ E/F. frames
def build_frames():
    frames = {}
    frames['A8 weights'] = E.an_weights(E.simple_chain(8))
    a1 = E.ROOTS240[0]
    frames['A7 weights + A1 root'] = E.an_weights(E.simple_chain(7, orth_to=(a1,))) + [a1]
    ch2 = E.simple_chain(2)
    frames['A2 weights + E6 root basis'] = E.an_weights(ch2) + E.root_basis_orthogonal_to(ch2, 6)
    ch3 = E.simple_chain(3)
    frames['A3 weights + D5 root basis'] = E.an_weights(ch3) + E.root_basis_orthogonal_to(ch3, 5)
    F0 = coordinate_frame()
    extra = next(i for i in range(E.N) if i not in F0 and sum(1 for f in F0 if E.G[i][f]) == 4)
    frames['coordinate frame + root'] = [E.LINES[f] for f in F0] + [E.LINES[extra]]
    return {k: Frame(k, v) for k, v in frames.items()}


def section_e(frames):
    for name, fr in frames.items():
        # ratio-class vectors v_kk' = z_k' a_k - z_k a_k' where a_k = coefficient functional of base rep
        # computed by the identity c0_k(i) = <a_k, 2 r_i>: test nonvanishing via lines
        nonzero = True
        hyper = True
        for k, kk in combinations(fr.S, 2):
            vals = []
            for i in range(E.N):
                c0 = fr.base(i)
                vals.append(fr.z[kk] * c0[k] - fr.z[k] * c0[kk])  # = <v_kk', 2 r_i>
            if all(v == 0 for v in vals):
                nonzero = False
            # lines with an option avoiding both k and kk have <v, r_i> = 0
            for i in range(E.N):
                for t, c in fr.options(i):
                    if c[k] == 0 and c[kk] == 0 and vals[i] != 0:
                        hyper = False
        check(f'E1 {name}: v_kk\' != 0 for all {len(fr.S) * (len(fr.S) - 1) // 2} masked pairs', nonzero)
        check(f'E2 {name}: a line avoiding two masked terms is orthogonal to v_kk\'', hyper)
        # each option's avoided masked set is one ratio class
        ok = True
        for i in range(E.N):
            c0 = fr.base(i)
            for t, c in fr.options(i):
                av = {k for k in fr.S if c[k] == 0}
                if av != {k for k in fr.S if c0[k] / fr.z[k] == -t}:
                    ok = False
        check(f'E3 {name}: every option avoids exactly one ratio class of masked terms', ok)


def section_f(frames):
    res = {}
    for name, fr in frames.items():
        rows = {i: fr.sparsest(i) for i in range(E.N)}
        ok, info = exact_on_pairs(rows, fr.F, E.FULL)
        check(f'F1 {name}: sparsest-representation 9-term decoder exact on all 14400 pairs', ok, str(info))
        per, X, Y = decoder_cost(rows, fr.F, E.FULL)
        ydims = [E.label_dim(y) for y in Y]
        xdims = [E.label_dim(x) for x in X]
        check(f'F2 {name}: P120 cost formula rho_k = dim V_Xk (all column supports span 9)',
              all(d == 9 for d in ydims) and per == xdims)
        spars = Counter(sum(1 for x in rows[i] if x != 0) for i in range(E.N))
        res[name] = {'masked_terms': len(fr.S), 'P120_term_costs': per, 'P120_cost': sum(per),
                     'row_support_sizes': [E.popcount(x) for x in X], 'sparsity': dict(sorted(spars.items()))}
        print(f'      {name}: |S|={len(fr.S)} cost={sum(per)} per-term={per} |X|={res[name]["row_support_sizes"]}')
    a8 = res['A8 weights']
    check('F3 A8 frame: every line is 2- or 3-sparse (36 + 84)', a8['sparsity'] == {2: 36, 3: 84})
    check('F4 A8 frame: every row support has 36 = 120 - U2 lines, yet label span 9; cost 81',
          a8['row_support_sizes'] == [36] * 9 and a8['P120_cost'] == 81)
    check('F5 no frame of section F beats the eight-term P120 floor 72',
          min(r['P120_cost'] for r in res.values()) >= 72, str({k: v['P120_cost'] for k, v in res.items()}))
    CERT['frames'] = res


# ============================================================================ G. controls
def section_g(frames, rng):
    fr = frames['A8 weights']
    rows = {i: fr.sparsest(i) for i in range(E.N)}
    bad = dict(rows)
    i0 = 5
    k0 = next(k for k in range(9) if bad[i0][k] != 0)
    bad[i0] = list(bad[i0])
    bad[i0][k0] += Q(1, 3)
    ok, _ = exact_on_pairs(bad, fr.F, E.FULL)
    check('G1 control: perturbing one coefficient breaks exactness', not ok)
    bad = dict(rows)
    bad[i0] = [x if k != k0 else Q(0) for k, x in enumerate(rows[i0])]
    ok, _ = exact_on_pairs(bad, fr.F, E.FULL)
    check('G2 control: deleting one support entry breaks exactness', not ok)
    try:
        Frame('rank7', [E.LINES[0]] * 9)
        check('G3 control: a rank-deficient frame is rejected', False)
    except ValueError:
        check('G3 control: a rank-deficient frame is rejected', True)
    flipped = list(E.M)
    flipped[0] ^= 1 << 7
    saved = E.M[:]
    E.M[:] = flipped
    r = E.f2_rank(E.M)
    E.M[:] = saved
    check('G4 control: a flipped label entry changes the pairing rank away from 9', r != 9, str(r))
    check('G5 control: label_dim of a single line is 1, of C(root) is 9',
          E.label_dim(1) == 1 and E.label_dim(E.support(E.LINES[0])) == 9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', help='write the JSON certificate here')
    ap.add_argument('--quick', action='store_true', help='skip the 130305-pair census (section B3-B5)')
    args = ap.parse_args()
    rng = random.Random(42)
    print('== A model'); words = section_a()
    print('== B spanning census'); section_b(words, full_pairs=not args.quick)
    print('== C normal form'); section_c(rng)
    print('== D merging'); section_d(rng)
    frames = build_frames()
    print('== E ratio classes'); section_e(frames)
    print('== F frames'); section_f(frames)
    print('== G controls'); section_g(frames, rng)
    CERT['log'] = LOG
    CERT['fails'] = FAILS
    if args.out:
        Path(args.out).write_text(json.dumps(CERT, indent=1, sort_keys=True) + '\n')
    npass = sum(1 for l in LOG if l.startswith('PASS'))
    if FAILS:
        print(f'FAIL_NINE_TERM_NORMAL_FORM_S42 failures={len(FAILS)}: {FAILS}')
        sys.exit(1)
    pairs = 'skipped' if args.quick else '130305'
    print(f'PASS_NINE_TERM_NORMAL_FORM_S42 checks={npass} pairs={pairs} frames={len(frames)} '
          f'A8_cost={CERT["frames"]["A8 weights"]["P120_cost"]}')


if __name__ == '__main__':
    main()
