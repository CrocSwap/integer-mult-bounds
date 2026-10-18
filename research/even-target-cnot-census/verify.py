#!/usr/bin/env python3
"""Even (order-3) diagonal targets in the formal F2[GL_2(F2)] register model.

Scoped check for research/even-target-cnot-census.  Standard library only.

Model (README.md section 1):  G = GL_2(F_2) = <a,b | a^2 = b^2 = (ab)^3 = 1>,
c = ab (order 3).  Registers r, target T = [c] I_r in M_r(F2[G]).
A paid call is C(g,N) = I + ([g]+1) N with g in {a,b} and N = v phi any
binary rank-one idempotent (phi(v) = 1).  Free scalar GL_r(F2) mixing is
free; the sign-quotient invariant (L1'/L2') forces any word hitting T to
have even length with mixing U = I and sum_i N_i = 0.

All exclusion meets run in the entrywise natural image (2-dimensional
representation of S_3), a homomorphic image of M_r(F2[G]):  an empty meet
there excludes the formal word as well.  Every accepted word is verified
exactly in M_r(F2[G]) by engine B (formal coefficients).

Engines:
  A  packed natural image, rank-1 fast updates (exclusion meets).
  B  formal coefficients in M_r(F2[G]) (independent small-ball cross-check
     and exact acceptance of every attaining word).

The written free-layer system (README section 3) is asserted as a screening
filter on the attaining words only; it is NOT a necessary condition (the
r=1 word b a b a is a target word it rejects) and NOT sufficient (r=2 word
a b on one projector passes and is not a target).  README section 3 states
the corrected scope.  Final line starts with PASS_EVEN_TARGET_CNOT_CENSUS.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from array import array
from bisect import bisect_left
from pathlib import Path

# ---------------------------------------------------------------------------
# G = GL_2(F_2): 2x2 binary matrices packed row-major in bits 0..3.
# bit0 = (0,0), bit1 = (0,1), bit2 = (1,0), bit3 = (1,1).
# ---------------------------------------------------------------------------

def mmul(u: int, v: int) -> int:
    a00, a01 = u & 1, (u >> 1) & 1
    a10, a11 = (u >> 2) & 1, (u >> 3) & 1
    b00, b01 = v & 1, (v >> 1) & 1
    b10, b11 = (v >> 2) & 1, (v >> 3) & 1
    return (
        (a00 & b00) ^ (a01 & b10)
        | (((a00 & b01) ^ (a01 & b11)) << 1)
        | (((a10 & b00) ^ (a11 & b10)) << 2)
        | (((a10 & b01) ^ (a11 & b11)) << 3)
    )


MAT_A = 0b1011  # [[1,1],[0,1]]
MAT_B = 0b1101  # [[1,0],[1,1]]
MAT_C = mmul(MAT_A, MAT_B)  # [[0,1],[1,1]], order 3
MAT_S = mmul(MAT_C, MAT_A)  # [[0,1],[1,0]]
MAT_I = 0b1001  # [[1,0],[0,1]]

GROUP = sorted({MAT_I, MAT_A, MAT_B, MAT_S, MAT_C, mmul(MAT_B, MAT_A)})
assert len(GROUP) == 6
GIDX = {m: i for i, m in enumerate(GROUP)}
E_IDX, A_IDX, B_IDX, C_IDX = GIDX[MAT_I], GIDX[MAT_A], GIDX[MAT_B], GIDX[MAT_C]
S_IDX = GIDX[MAT_S]
GTAB = [[GIDX[mmul(GROUP[i], GROUP[j])] for j in range(6)] for i in range(6)]
GINV = [next(j for j in range(6) if GTAB[i][j] == E_IDX) for i in range(6)]

NAT = [None] * 6  # NAT[i][p] = row p of the natural image of GROUP[i], 2 bits
for i, m in enumerate(GROUP):
    NAT[i] = [
        ((m >> (2 * p)) & 1) | (((m >> (2 * p + 1)) & 1) << 1) for p in range(2)
    ]

PARITY = [0] * 256
for _i in range(256):
    PARITY[_i] = bin(_i).count("1") & 1


# ---------------------------------------------------------------------------
# Rank-one idempotents N = v phi over F2^r with phi(v) = 1.
# ---------------------------------------------------------------------------

def idempotents(r: int):
    out = []
    for v in range(1, 1 << r):
        for phi in range(1 << r):
            if PARITY[v & phi]:
                out.append((v, phi))
    return out


def mat_of(v: int, phi: int, r: int) -> int:
    out = 0
    for i in range(r):
        if (v >> i) & 1:
            out |= phi << (r * i)
    return out


def mat_mul(u: int, v: int, r: int) -> int:
    out = 0
    mask = (1 << r) - 1
    for i in range(r):
        row = (u >> (r * i)) & mask
        acc = 0
        for k in range(r):
            if (row >> k) & 1:
                acc ^= (v >> (r * k)) & mask
        out |= acc << (r * i)
    return out


def mat_sum(mats, r=None) -> int:
    out = 0
    for m in mats:
        out ^= m
    return out


def mat_ident(r: int) -> int:
    out = 0
    for i in range(r):
        out |= 1 << (r * i + i)
    return out


# ---------------------------------------------------------------------------
# Engine A: natural image.  State = 2r x 2r binary matrix, rows of 2r bits.
# A call is I + U W^T with U = v (x) beta, W = phi (x) gamma, where
# rho(g) + I = beta gamma^T (rank one) for g in {a,b}.
# ---------------------------------------------------------------------------

def beta_gamma(gi: int):
    bg = [[(NAT[gi][p] >> q) & 1 for q in range(2)] for p in range(2)]
    for p in range(2):
        for q in range(2):
            bg[p][q] ^= 1 if p == q else 0
    flat = [(p, q) for p in range(2) for q in range(2) if bg[p][q]]
    assert len(flat) == 1
    p, q = flat[0]
    return 1 << p, 1 << q


def make_gens(r: int):
    """Generators as (Umask, Wmask, Urows, Wrows, gi, v, phi) over 2r bits."""
    gens = []
    for (v, phi) in idempotents(r):
        for gi in (A_IDX, B_IDX):
            beta, gamma = beta_gamma(gi)
            U = W = 0
            urows = []
            wrows = []
            for i in range(r):
                if (v >> i) & 1:
                    U |= beta << (2 * i)
                    urows.append(2 * i + (beta.bit_length() - 1))
                if (phi >> i) & 1:
                    W |= gamma << (2 * i)
                    wrows.append(2 * i + (gamma.bit_length() - 1))
            gens.append((U, W, urows, wrows, gi, v, phi))
    return gens


ROWSZ = None  # set per r
ROWMASK = 255


def set_r(r: int):
    global ROWSZ, ROWMASK
    ROWSZ = 2 * r
    ROWMASK = (1 << ROWSZ) - 1


def nat_right_mul(s: int, gen) -> int:
    """s' = s (I + U W^T) = s + (s U) W^T."""
    U, W = gen[0], gen[1]
    out = s
    for i in range(ROWSZ):
        if PARITY[((s >> (ROWSZ * i)) & ROWMASK) & U]:
            out ^= W << (ROWSZ * i)
    return out


def nat_left_mul(s: int, gen) -> int:
    """s' = (I + U W^T) s = s + U (W^T s)."""
    U, W, urows, wrows = gen[0], gen[1], gen[2], gen[3]
    r = 0
    for i in wrows:
        r ^= (s >> (ROWSZ * i)) & ROWMASK
    if r == 0:
        return s
    out = s
    for i in urows:
        out ^= r << (ROWSZ * i)
    return out


def nat_identity() -> int:
    out = 0
    for i in range(ROWSZ):
        out |= 1 << (ROWSZ * i + i)
    return out


def nat_right_target(s: int, mat: int, r: int) -> int:
    """s' = s * (I_r (x) mat); mixes the two column bits of each register."""
    out = 0
    for i in range(2 * r):
        row = (s >> (ROWSZ * i)) & ROWMASK
        for k in range(r):
            b0 = (row >> (2 * k)) & 1
            b1 = (row >> (2 * k + 1)) & 1
            n0 = ((mat & 1) & b0) ^ (((mat >> 2) & 1) & b1)
            n1 = (((mat >> 1) & 1) & b0) ^ (((mat >> 3) & 1) & b1)
            row = (row & ~(3 << (2 * k))) | (n0 << (2 * k)) | (n1 << (2 * k + 1))
        out |= row << (ROWSZ * i)
    return out


# ---------------------------------------------------------------------------
# Engine B: formal coefficients in M_r(F2[G]); state = 6 planes of r x r
# binary matrices, rows of r bits.
# ---------------------------------------------------------------------------

def formal_identity(r: int):
    pl = [0] * 6
    pl[E_IDX] = mat_ident(r)
    return tuple(pl)


def formal_left_call(pl, gi: int, v: int, phi: int, r: int):
    """Multiply on the left by C = I + ([g]+1) N."""
    mask = (1 << r) - 1
    ginv = GINV[gi]
    out = [0] * 6
    for h in range(6):
        q = pl[h]
        acc = q ^ pl[GTAB[ginv][h]]
        comb = 0
        for i in range(r):
            if (phi >> i) & 1:
                comb ^= (acc >> (r * i)) & mask
        nacc = 0
        for i in range(r):
            if (v >> i) & 1:
                nacc |= comb << (r * i)
        out[h] = q ^ nacc
    return tuple(out)


def formal_right_call(pl, gi: int, v: int, phi: int, r: int):
    """Multiply on the right by C = I + ([g]+1) N:  (P C)^h = P^h + (P^h + P^{h g^-1}) N."""
    mask = (1 << r) - 1
    ginv = GINV[gi]
    out = [0] * 6
    for h in range(6):
        q = pl[h]
        acc = q ^ pl[GTAB[h][ginv]]
        # acc * N = (acc v) phi
        col = 0
        for i in range(r):
            row = (acc >> (r * i)) & mask
            if PARITY[row & v]:
                col |= 1 << i
        rn = 0
        for i in range(r):
            if (col >> i) & 1:
                rn |= phi << (r * i)
        out[h] = q ^ rn
    return tuple(out)


def formal_right_target(pl, gi: int):
    out = [0] * 6
    for h in range(6):
        out[GTAB[h][gi]] = pl[h]
    return tuple(out)


def formal_is_target(pl, r: int, target_gi: int = None) -> bool:
    if target_gi is None:
        target_gi = C_IDX
    return list(pl) == [mat_ident(r) if h == target_gi else 0 for h in range(6)]


# ---------------------------------------------------------------------------
# Balls and meets.
# ---------------------------------------------------------------------------

def build_ball(gens, r: int, depth: int):
    """Values of products of exactly `depth` generators (newest on the right).

    Returns (states_sorted_array, invs_list, sizes, sorted_index_helper).
    invs[i] is the inverse value of states[i] (well defined per value).
    """
    global ROWSZ
    set_r(r)
    ident = nat_identity()
    states = array("Q", [ident])
    invs = array("Q", [ident])
    seen = {ident: 0}
    sizes = [1]
    frontier = [0]
    for _ in range(depth):
        nxt = []
        for idx in frontier:
            s = states[idx]
            inv = invs[idx]
            for g in gens:
                s2 = nat_right_mul(s, g)
                if s2 in seen:
                    continue
                seen[s2] = len(states)
                states.append(s2)
                invs.append(nat_left_mul(inv, g))
                nxt.append(len(states) - 1)
        sizes.append(len(states) - sum(sizes))
        frontier = nxt
        if not frontier:
            break
    return states, invs, sizes, seen


def meet_count(gens, r: int, k: int, target_mat: int):
    """Pairs (u,v) of exact-length-k words with u v = T in the natural image.

    Returns (hits, sizes, seen).  hits == 0 excludes length 2k in the formal
    model, given the exclusions at shorter lengths (README section 4).
    """
    global ROWSZ
    set_r(r)
    states, invs, sizes, seen = build_ball(gens, r, k)
    hits = 0
    for idx in range(len(states)):
        v = nat_right_target(invs[idx], target_mat, r)
        if v in seen:
            hits += 1
    return hits, sizes, seen


def exact_value_counts(gens, r: int):
    """|V_k| = number of VALUES of words of exactly k calls.

    V_0 = {I}; V_k = {y*g : y in V_{k-1}, g in gens}.  Values recur across
    depths (C*C = I and C*C*C = C), so these differ from the counts of
    values first reached at each BFS depth.
    """
    set_r(r)
    ident = nat_identity()
    V1 = {nat_right_mul(ident, g) for g in gens}
    V2 = set()
    for x in V1:
        for g in gens:
            V2.add(nat_right_mul(x, g))
    V3 = set()
    for x in V2:
        for g in gens:
            V3.add(nat_right_mul(x, g))
    return len(V1), len(V2), len(V3)


def formal_ball(gens, r: int, depth: int):
    """Engine-B ball: values of products of exactly `depth` formal calls."""
    ident = formal_identity(r)
    states = [ident]
    invs = [ident]
    seen = {ident: 0}
    sizes = [1]
    frontier = [0]
    for _ in range(depth):
        nxt = []
        for idx in frontier:
            s = states[idx]
            inv = invs[idx]
            for g in gens:
                s2 = formal_right_call(s, g[4], g[5], g[6], r)
                if s2 in seen:
                    continue
                seen[s2] = len(states)
                states.append(s2)
                invs.append(formal_left_call(inv, g[4], g[5], g[6], r))
                nxt.append(len(states) - 1)
        sizes.append(len(states) - sum(sizes))
        frontier = nxt
        if not frontier:
            break
    return states, invs, sizes, seen


def formal_meet_count(gens, r: int, k: int, target_gi: int):
    states, invs, sizes, seen = formal_ball(gens, r, k)
    hits = 0
    for idx in range(len(states)):
        v = formal_right_target(invs[idx], target_gi)
        if v in seen:
            hits += 1
    return hits, sizes


# ---------------------------------------------------------------------------
# Free-layer sums (README section 3).  For a word w with letters g_i in
# {a,b} and idempotents N_i, expand prod (I + E_i) = T in the free filtered
# algebra F_2<x,y>/(x^2, y^2).  Matching degrees 1..3 against the kernel of
# F -> F_2[G] is valid only for words of length q <= 3: up to degree 3 that
# kernel is 1-dimensional, spanned by R = xyx + yxy + x + y alone, since
# Z = z + z^2 + z^3 (z = x + y + xy) carries degrees up to 6 and its
# degree <= 3 truncation is not in the kernel.  The checks below are
# screening filters only -- not necessary (r=1 b a b a is a target word they
# reject) and not sufficient (r=2 a b on one projector passes and is not a
# target).  See README section 3.
# ---------------------------------------------------------------------------

def layer_sums(word, r: int):
    mats = [mat_of(v, phi, r) for (_g, v, phi) in word]
    gis = [gi for (gi, _v, _p) in word]
    n = len(word)
    sum_a = mat_sum([mats[i] for i in range(n) if gis[i] == A_IDX], r)
    sum_b = mat_sum([mats[i] for i in range(n) if gis[i] == B_IDX], r)
    sum_ab = mat_sum(
        [mat_mul(mats[i], mats[j], r) for i in range(n) for j in range(i + 1, n)
         if gis[i] == A_IDX and gis[j] == B_IDX], r)
    sum_ba = mat_sum(
        [mat_mul(mats[i], mats[j], r) for i in range(n) for j in range(i + 1, n)
         if gis[i] == B_IDX and gis[j] == A_IDX], r)
    sum_aba = mat_sum(
        [mat_mul(mat_mul(mats[i], mats[j], r), mats[k], r)
         for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)
         if (gis[i], gis[j], gis[k]) == (A_IDX, B_IDX, A_IDX)], r)
    sum_bab = mat_sum(
        [mat_mul(mat_mul(mats[i], mats[j], r), mats[k], r)
         for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)
         if (gis[i], gis[j], gis[k]) == (B_IDX, A_IDX, B_IDX)], r)
    return {"sum_a": sum_a, "sum_b": sum_b, "sum_ab": sum_ab,
            "sum_ba": sum_ba, "sum_aba": sum_aba, "sum_bab": sum_bab}


def layer_ok_even_target(word, r: int) -> bool:
    """Screening filter for words hitting T = [c] I_r (README section 3).

    Not necessary and not sufficient; never use it to exclude candidates.
    """
    s = layer_sums(word, r)
    ident = mat_ident(r)
    if s["sum_a"] != s["sum_b"]:
        return False
    if s["sum_ba"] != 0:
        return False
    lam = s["sum_a"] ^ ident
    nu = s["sum_ab"] ^ ident
    if s["sum_aba"] != (lam ^ nu):
        return False
    if s["sum_bab"] != (lam ^ nu):
        return False
    return True


def layer_ok_swap_target(word, r: int) -> bool:
    """Layer conditions for the SWAP target T = [S] I_r.

    Used here only as a rejection control; necessity is not established
    (same degree-matching caveat as README section 3).
    """
    s = layer_sums(word, r)
    ident = mat_ident(r)
    if (s["sum_a"] ^ s["sum_b"]) != ident:
        return False
    if s["sum_ba"] != ident:
        return False
    if (s["sum_aba"] ^ s["sum_bab"]) != ident:
        return False
    if s["sum_bab"] != (s["sum_a"] ^ s["sum_ab"] ^ ident):
        return False
    return True


# ---------------------------------------------------------------------------
# Words and controls.
# ---------------------------------------------------------------------------

def word_even(r: int):
    """2r calls: (a, N_k) then (b, N_k) on each diagonal idempotent."""
    w = []
    for k in range(r):
        w.append((A_IDX, 1 << k, 1 << k))
        w.append((B_IDX, 1 << k, 1 << k))
    return w


def word_swap(r: int):
    """3r calls: aba on each diagonal idempotent (predecessor upper bound)."""
    w = []
    for k in range(r):
        w.append((A_IDX, 1 << k, 1 << k))
        w.append((B_IDX, 1 << k, 1 << k))
        w.append((A_IDX, 1 << k, 1 << k))
    return w


def formal_word_value(word, r: int):
    pl = formal_identity(r)
    for (gi, v, phi) in word:
        pl = formal_right_call(pl, gi, v, phi, r)
    return pl


def gen_lookup(gi, v, phi, gens):
    for g in gens:
        if (g[4], g[5], g[6]) == (gi, v, phi):
            return g
    raise KeyError((gi, v, phi))


def ctrl_group_table():
    assert all(GTAB[i][E_IDX] == i and GTAB[E_IDX][i] == i for i in range(6))
    assert all(GTAB[i][GINV[i]] == E_IDX for i in range(6))
    assert mmul(MAT_A, MAT_A) == MAT_I and mmul(MAT_B, MAT_B) == MAT_I
    assert mmul(MAT_C, mmul(MAT_C, MAT_C)) == MAT_I
    assert MAT_S == mmul(MAT_C, MAT_A) == mmul(MAT_B, MAT_C)
    return 1


def ctrl_fast_update(rng, trials=200):
    """Packed rank-1 updates agree with dense multiplication (r = 4)."""
    r = 4
    set_r(r)
    gens = make_gens(r)
    n = 2 * r

    def dense(g):
        U, W = g[0], g[1]
        c = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                c[i][j] = (1 if i == j else 0) ^ (((U >> i) & 1) & ((W >> j) & 1))
        return c

    def to_mat(s):
        return [[(s >> (ROWSZ * i + j)) & 1 for j in range(n)] for i in range(n)]

    def to_int(m):
        out = 0
        for i in range(n):
            for j in range(n):
                if m[i][j]:
                    out |= 1 << (ROWSZ * i + j)
        return out

    def mm(a, b):
        return [[sum(a[i][k] & b[k][j] for k in range(n)) & 1 for j in range(n)]
                for i in range(n)]

    for _ in range(trials):
        s = rng.getrandbits(ROWSZ * ROWSZ)
        g = gens[rng.randrange(len(gens))]
        c = dense(g)
        sm = to_mat(s)
        assert to_int(mm(c, sm)) == nat_left_mul(s, g)
        assert to_int(mm(sm, c)) == nat_right_mul(s, g)
    return trials


def ctrl_formal_natural(rng, trials=100):
    """Engine B projected entrywise equals engine A on random short words."""
    r = 4
    set_r(r)
    gens = make_gens(r)
    for _ in range(trials):
        n = rng.randrange(1, 5)
        picks = [gens[rng.randrange(len(gens))] for _ in range(n)]
        word = [(g[4], g[5], g[6]) for g in picks]
        pl = formal_word_value(word, r)
        s = nat_identity()
        for g in picks:
            s = nat_right_mul(s, g)
        proj = 0
        for h in range(6):
            m = pl[h]
            for i in range(r):
                for j in range(r):
                    if (m >> (r * i + j)) & 1:
                        for p in range(2):
                            for q in range(2):
                                if (NAT[h][p] >> q) & 1:
                                    proj ^= 1 << (ROWSZ * (2 * i + p) + (2 * j + q))
        assert proj == s
    return trials


def ctrl_parity(rng, trials=50):
    """L1' sign-quotient parity: an odd-length product never equals T."""
    r = 2
    set_r(r)
    gens = make_gens(r)
    for _ in range(trials):
        n = rng.randrange(1, 8) | 1
        s = nat_identity()
        for _k in range(n):
            s = nat_right_mul(s, gens[rng.randrange(len(gens))])
        assert s != nat_right_target(nat_identity(), MAT_C, r)
    return trials


# ---------------------------------------------------------------------------
# Main run.
# ---------------------------------------------------------------------------

def run(fast: bool = False):
    t0 = time.time()
    rng = random.Random(20261014)
    rec = {"group": {"elements": GROUP, "c": MAT_C, "s": MAT_S}}
    rec["controls"] = {
        "group_table": ctrl_group_table(),
        "fast_update_crosscheck": ctrl_fast_update(rng),
        "formal_natural_crosscheck": ctrl_formal_natural(rng),
        "parity_control": ctrl_parity(rng),
    }

    # t = 1, r = 1: minimum 2 (control).
    r = 1
    gens = make_gens(r)
    w = word_even(1)
    assert formal_is_target(formal_word_value(w, 1), 1)
    # direct q = 1 check in the formal model
    hit1 = 0
    for g in gens:
        if formal_is_target(formal_left_call(formal_identity(1), g[4], g[5], g[6], 1), 1):
            hit1 += 1
    assert hit1 == 0
    assert layer_ok_even_target(w, 1)
    rec["t1r1"] = {"min": 2, "q1_formal_hits": hit1, "layer_ok": True}

    small = {}
    for r in (2, 3):
        gens = make_gens(r)
        w = word_even(r)
        assert formal_is_target(formal_word_value(w, r), r), f"attaining word r={r}"
        for drop in range(len(w)):
            mut = w[:drop] + w[drop + 1:]
            assert not formal_is_target(formal_word_value(mut, r), r), "drop-one"
        assert layer_ok_even_target(w, r)
        cand = {}
        for q in (2, 4):
            hits, _sizes, _seen = meet_count(gens, r, q // 2, MAT_C)
            cand[q] = hits
        # independent engine B meet at the same lengths
        bcand = {}
        for q in (2, 4):
            bcand[q] = formal_meet_count(gens, r, q // 2, C_IDX)[0]
        assert bcand == cand, (r, cand, bcand)
        assert cand[2] == 0, (r, cand)  # two calls cover one register only
        min_q = 4 if cand[4] else 2 * r
        small[f"t{r}r{r}"] = {"min": min_q, "nat_hits": cand,
                              "engine_b_agrees": True}
    assert small["t2r2"]["min"] == 4, small
    rec["small_minima"] = small

    # SWAP control at t = r = 2: predecessor minimum 6 (PR1414/1491 line).
    r = 2
    gens = make_gens(r)
    wsw = word_swap(2)
    assert formal_is_target(formal_word_value(wsw, 2), 2, S_IDX), "SWAP attaining word"
    assert layer_ok_swap_target(wsw, 2)
    sw = {}
    for q in (2, 4):
        sw[q] = meet_count(gens, r, q // 2, MAT_S)[0]
        assert sw[q] == 0, (q, sw)
    # a word that hits T=[c] but not [S] must fail the SWAP layer system
    assert not layer_ok_swap_target(word_even(2), 2)
    rec["swap_t2r2"] = {"min": 6, "excluded_q": sw, "layer_ok": True}

    # main case t = r = 4.
    r = 4
    gens = make_gens(r)
    w = word_even(4)
    assert formal_is_target(formal_word_value(w, 4), 4), "t=4 attaining word"
    for drop in range(len(w)):
        mut = w[:drop] + w[drop + 1:]
        assert not formal_is_target(formal_word_value(mut, 4), 4), "drop-one t=4"
    assert layer_ok_even_target(w, 4)
    main = {"upper": 8, "layer_ok": True, "q": {}}
    if not fast:
        for q in (2, 4):
            hits, sizes_k, _seen_k = meet_count(gens, r, q // 2, MAT_C)
            main["q"][q] = hits
            main[f"novel_depth{q // 2}"] = sizes_k[q // 2]
        hits6, sizes3, seen3 = meet_count(gens, r, 3, MAT_C)
        main["q"][6] = hits6
        main["novel_depth3"] = sizes3[3]
        del seen3
        e1, e2, e3 = exact_value_counts(gens, r)
        main["ball_depth1"] = e1
        main["ball_depth2"] = e2
        main["ball_depth3"] = e3
        main["pr1705_ball_match"] = (e1 == 240 and e2 == 32651 and e3 == 3639920)
        assert main["pr1705_ball_match"], (e1, e2, e3)
    rec["main_t4r4"] = main
    rec["runtime_seconds"] = round(time.time() - t0, 1)
    return rec


def final_line(rec) -> str:
    m = rec["main_t4r4"]
    q = m.get("q", {})
    small = rec["small_minima"]
    return (
        "PASS_EVEN_TARGET_CNOT_CENSUS "
        f"t1r1_min=2 t2r2_min={small['t2r2']['min']} t3r3_min={small['t3r3']['min']} "
        f"t4r4_upper={m['upper']} t4r4_excluded={q} "
        f"balls4={m.get('ball_depth1')},{m.get('ball_depth2')},{m.get('ball_depth3')} "
        f"pr1705_ball_match={m.get('pr1705_ball_match')} no_new_kappa"
    )


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip the r=4 depth-3 meet")
    ap.add_argument("--record", action="store_true", help="write RECEIPT.json")
    ap.add_argument("--check-receipt", action="store_true")
    args = ap.parse_args(argv)
    rec = run(fast=args.fast)
    print(json.dumps(rec, indent=1, default=str))
    here = Path(__file__).resolve().parent
    if args.record:
        (here / "RECEIPT.json").write_text(
            json.dumps(rec, indent=1, default=str, sort_keys=True), encoding="utf-8")
        print("RECEIPT.json written")
    if args.check_receipt:
        stored = json.loads((here / "RECEIPT.json").read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(rec, default=str))
        for key in ("t1r1", "small_minima", "swap_t2r2", "main_t4r4", "controls"):
            if stored.get(key) != fresh.get(key):
                print("RECEIPT_MISMATCH", key)
                print(" stored:", json.dumps(stored.get(key), default=str)[:400])
                print(" fresh :", json.dumps(fresh.get(key), default=str)[:400])
                return 2
    print(final_line(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
