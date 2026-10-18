"""KB3g engine: tight-class resolution for the 18-point cover question for
F2^7 (set level; no words).  Exact Python integer arithmetic only.

Object (unchanged from PR 2911/2933): S = A u B covers F2^7 iff P + P = F2^7.
With D = p + B inside E = F2^6 (PR 2911 reduction, PROVEN there) the pair
(A, D) covers iff (i) A + D = E and (ii) (A+A) u (D+D) = E.

This module decides the two PR 2933 TIGHT classes of the (10,8) split and
the full-sumset class (6,0) of (12,6) by exact enumeration of the L7-forced
Sidon equality configurations.  All arithmetic is integers; masks are Python
ints.

Halves.  Fix the character psi = bit 0 (WLOG under GL(6,2)).  H = ker(psi)
and the coset H' are both identified with F2^5 = {0..31}; every cross sum is
the XOR of the two F2^5 coordinates (the coset offset cancels in pairs, and
H'-valued sums are read in H' coordinates).  A = A0 u A1 with A0 in H, A1 in
H'; D = D0 u D1 likewise.  Coverage is equivalent to the four L3 lines
(PR 2933, PROVEN):

  (i)  (A0+D0) u (A1+D1) = H
  (ii) (A0+D1) u (A1+D0) = H'
  (iii) (A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = H
  (iv) (A0+A1) u (D0+D1) = H'

Half-translations (h on (A0,D0), h' on (A1,D1)) and a common GL(5,2) map M
preserve all four lines (each H'-valued sumset translates by h + h', which
preserves its being all of H').  Hence WLOG 0 in A0, 0 in A1.

L7 (PR 2933, PROVEN; general pigeonhole valid at m = 6): at F1 equality
a0*a1 + d0*d1 = 32 with (iv) holding, |A0+A1| = a0*a1, |D0+D1| = d0*d1 (both
Sidon: all cross sums distinct) and the two cross sumsets are disjoint with
union H'.

Class (10,8) A-vanish (7,1):  A0, A1 5-sets with |A0+A1| = 25; D0 a 7-set,
D1 a singleton {d1}.  (iv) forces D0 + d1 = T := H' \\ (A0+A1) (7 points).
Substituting D0 = T + d1 into (i)-(iii) and translating by d1 shows coverage
is INDEPENDENT of d1:
  (I)  (A0+T) u A1 = F2^5
  (II) (A1+T) u A0 = F2^5
  (III) (A0+A0) u (A1+A1) u (T+T) = F2^5
and (iv) holds by construction.  Each covering (A0, A1) yields 32 covering
configurations (one per d1) in the normalized chart.

Class (10,8) D-vanish (8,2):  D0, D1 4-sets with |D0+D1| = 16; A splits
(8,2): A0 an 8-set, A1 = {w, w+delta}, delta != 0.  |A0+A1| = 16 iff
A0 u (A0+delta) = 16 points iff A0 n (A0+delta) = 0.  Normalize instead on
the D side: 0 in D0, 0 in D1 (the class forces both nonempty), and WLOG
delta = 1 under GL(5,2).  With T = D0+D1 (16 points) and C = H' \\ T,
(iv) forces A0 + w to choose one element of each pair {x, x+1} inside C, so
C must be 1-invariant; the choice is one of at most 2^8 sets A0t = A0 + w.
Coverage is then independent of w:
  (I')  (A0t+D0) u (D1+{0,1}) = F2^5
  (II') (A0t+D1) u (D0+{0,1}) = F2^5
  (III') (A0t+A0t) u {0,1} u (D0+D0) u (D1+D1) = F2^5

Class (12,6) A-vanish (6,0):  A0, A1 6-sets with A0+A1 = H' (36 pairs, excess
exactly 4), D = D0 a 6-set in H, D1 empty.  Lines reduce to
  (I'')  A0+D = F2^5,  (II'') A1+D = F2^5,
  (III'') (A0+A0) u (A1+A1) u (D+D) = F2^5.
Normalize 0 in A0, 0 in A1.
"""

import json
import sys
import time
from itertools import combinations
from pathlib import Path

ALL = (1 << 32) - 1
N5 = 32


# ------------------------------------------------------- mask primitives


def elems(mask):
    out = []
    while mask:
        lsb = mask & -mask
        out.append(lsb.bit_length() - 1)
        mask ^= lsb
    return out


def mask_of(pts):
    m = 0
    for p in pts:
        m |= 1 << p
    return m


# Precomputed per-bit XOR-translation block masks (5 bits, F2^5).
_BIT_LO = []
_BIT_HI = []
for _i in range(5):
    _b = 1 << _i
    _lo = 0
    for _p in range(N5):
        if not (_p & _b):
            _lo |= 1 << _p
    _BIT_LO.append(_lo)
    _BIT_HI.append(ALL ^ _lo)


def trans(mask, a):
    """{x ^ a : x in mask} as a bitmask."""
    for i in range(5):
        if (a >> i) & 1:
            b = 1 << i
            mask = ((mask & _BIT_LO[i]) << b) | ((mask & _BIT_HI[i]) >> b)
    return mask


def sumset_mask(mx, my):
    """{x ^ y : x in mx, y in my}."""
    out = 0
    x = mx
    while x:
        lsb = x & -x
        out |= trans(my, lsb.bit_length() - 1)
        x ^= lsb
    return out


def selfsum_mask(mx):
    """{x ^ y : x, y in mx} (includes 0)."""
    return sumset_mask(mx, mx)


def delta_mask(mx):
    """{x ^ y : x != y in mx} = selfsum minus {0}."""
    return selfsum_mask(mx) & ALL & ~1


def sidon_cross(mx, my, px, py):
    """|X+Y| = |X|*|Y| with sizes px, py (all cross sums distinct)."""
    return sumset_mask(mx, my).bit_count() == px * py


# ------------------------------------------- class (7,1) at (10,8)


def class71_pairs():
    """All normalized Sidon 5-pairs: 0 in A0, 0 in A1, |A0+A1| = 25.
    Backtracks A0 = {0, a1, a2, a3, a4} against the forbidden difference
    set of A1 (condition Delta(A0) n Delta(A1) = 0)."""
    out = []
    rest = list(range(1, N5))

    def extend(a1m):
        forb = delta_mask(a1m)
        cand = [v for v in rest if not (forb >> v) & 1]
        chosen = [0, 0, 0, 0, 0]

        def rec(depth, start):
            if depth == 5:
                out.append((mask_of(chosen), a1m))
                return
            for i in range(start, len(cand)):
                v = cand[i]
                if v <= chosen[depth - 1]:
                    continue
                ok = True
                for j in range(1, depth):
                    if (forb >> (v ^ chosen[j])) & 1:
                        ok = False
                        break
                if ok:
                    chosen[depth] = v
                    rec(depth + 1, i + 1)

        rec(1, 0)

    for bs in combinations(rest, 4):
        a1m = 1 | mask_of(bs)
        extend(a1m)
    return out


def class71_check(a0m, a1m):
    """The three translated coverage lines (I),(II),(III) for one pair.
    Returns (ok, which_lines_fail)."""
    sums = sumset_mask(a0m, a1m)
    if sums.bit_count() != 25:
        return False, ("sidon",)
    tm = ALL ^ sums
    fails = []
    if (sumset_mask(a0m, tm) | a1m) != ALL:
        fails.append("I")
    if (sumset_mask(a1m, tm) | a0m) != ALL:
        fails.append("II")
    if (selfsum_mask(a0m) | selfsum_mask(a1m) | selfsum_mask(tm)) != ALL:
        fails.append("III")
    return (not fails), tuple(fails)


def class71_run(progress=None, budget=None):
    """Full decision run for class (7,1).  Counts every normalized equality
    configuration (A0, A1, d1) and every covering one; records witnesses."""
    t0 = time.time()
    pairs = class71_pairs()
    total = len(pairs)
    checked = 0
    covering = 0
    fail_hist = {}
    witnesses = []
    for (a0m, a1m) in pairs:
        ok, fails = class71_check(a0m, a1m)
        checked += 1
        if ok:
            covering += 1
            if len(witnesses) < 5:
                witnesses.append((elems(a0m), elems(a1m)))
        else:
            fail_hist[fails] = fail_hist.get(fails, 0) + 1
        if budget is not None and checked % 5000 == 0 and time.time() - t0 > budget:
            break
    return dict(
        normalized_pairs=total,
        checked=checked,
        covering_pairs=covering,
        equality_configs_normalized=total * 32,
        covering_configs_normalized=covering * 32,
        fail_hist={str(k): v for k, v in sorted(fail_hist.items())},
        witnesses=witnesses,
        seconds=round(time.time() - t0, 2),
    )


# ------------------------------------------- class (8,2) at (10,8)


def sidon44_pairs_normalized():
    """All Sidon 4-pairs: 0 in D0, 0 in D1, |D0+D1| = 16."""
    out = []
    rest = list(range(1, N5))
    for c0 in combinations(rest, 3):
        d0m = 1 | mask_of(c0)
        for c1 in combinations(rest, 3):
            d1m = 1 | mask_of(c1)
            if sumset_mask(d0m, d1m).bit_count() == 16:
                out.append((d0m, d1m))
    return out


def class82_choices(tm):
    """All A0t = choice sets: one element of each {x, x+1} pair inside
    C = H' \\ T, where T = D0+D1 must have 1-invariant complement.
    Returns (choices, reason): choices empty with reason if impossible."""
    cm = ALL ^ tm
    if trans(cm, 1) != cm:
        return [], "C_not_1_invariant"
    pairs = []
    seen = 0
    x = cm
    choices = [0]
    while x:
        lsb = x & -x
        p = lsb.bit_length() - 1
        if (seen >> p) & 1:
            x ^= lsb
            continue
        q = p ^ 1
        if not (cm >> q) & 1:
            return [], "C_pair_incomplete"
        seen |= (1 << p) | (1 << q)
        choices = [c | (1 << p) for c in choices] + [c | (1 << q) for c in choices]
        x ^= lsb
    return choices, "ok"


def class82_check(a0tm, d0m, d1m):
    """The three coverage lines (I'),(II'),(III') for one configuration.
    Returns (ok, which_lines_fail)."""
    fails = []
    if (sumset_mask(a0tm, d0m) | sumset_mask(d1m, 3)) != ALL:
        fails.append("I")
    if (sumset_mask(a0tm, d1m) | sumset_mask(d0m, 3)) != ALL:
        fails.append("II")
    if (selfsum_mask(a0tm) | 3 | selfsum_mask(d0m) | selfsum_mask(d1m)) != ALL:
        fails.append("III")
    return (not fails), tuple(fails)


def class82_run(budget=None, shard=0, shards=1):
    """Full decision run for class (8,2): every normalized Sidon D-pair, every
    admissible A0t choice.  Counts equality configurations and coverings.
    Per-pair D-side masks are precomputed; (I') and (II') are decided by
    OR-chains over the 8 chosen candidate translates, (III') only for
    survivors.  Deterministic sharding: pairs[shard::shards]."""
    import itertools as _it

    t0 = time.time()
    pairs = sidon44_pairs_normalized()
    n_pairs_total = len(pairs)
    pairs = pairs[shard::shards]
    n_pairs = len(pairs)
    n_choice_sets = 0
    covering = 0
    checked = 0
    fail_hist = {}
    witnesses = []
    noninv = 0
    budget_hit = False
    for (d0m, d1m) in pairs:
        tm = sumset_mask(d0m, d1m)
        choices, reason = class82_choices(tm)
        if not choices:
            noninv += 1
            continue
        n_choice_sets += len(choices)
        md1_01 = sumset_mask(d1m, 3)
        md0_01 = sumset_mask(d0m, 3)
        mdd = selfsum_mask(d0m) | selfsum_mask(d1m)
        # per {x, x+1} pair inside C: (bit_p, bit_q, d0p, d0q, d1p, d1q)
        cand = []
        seen = 0
        x = ALL ^ tm
        while x:
            lsb = x & -x
            p = lsb.bit_length() - 1
            if (seen >> p) & 1:
                x ^= lsb
                continue
            q = p ^ 1
            seen |= (1 << p) | (1 << q)
            cand.append(
                (
                    1 << p,
                    1 << q,
                    trans(d0m, p),
                    trans(d0m, q),
                    trans(d1m, p),
                    trans(d1m, q),
                )
            )
            x ^= lsb
        for pick in _it.product((0, 1), repeat=len(cand)):
            a0tm = 0
            s0 = 0
            s1 = 0
            for i, which in enumerate(pick):
                c = cand[i]
                if which == 0:
                    a0tm |= c[0]
                    s0 |= c[2]
                    s1 |= c[4]
                else:
                    a0tm |= c[1]
                    s0 |= c[3]
                    s1 |= c[5]
            checked += 1
            fails = []
            if (s0 | md1_01) != ALL:
                fails.append("I")
            if (s1 | md0_01) != ALL:
                fails.append("II")
            if (selfsum_mask(a0tm) | 3 | mdd) != ALL:
                fails.append("III")
            if fails:
                fail_hist[tuple(fails)] = fail_hist.get(tuple(fails), 0) + 1
            else:
                covering += 1
                if len(witnesses) < 5:
                    witnesses.append((elems(a0tm), elems(d0m), elems(d1m)))
        if budget is not None and time.time() - t0 > budget:
            budget_hit = True
            break
    return dict(
        shard=shard,
        shards=shards,
        normalized_sidon_pairs_total=n_pairs_total,
        normalized_sidon_pairs=n_pairs,
        non_1_invariant_pairs=noninv,
        admissible_choice_sets=n_choice_sets,
        checked=checked,
        covering_configs=covering,
        fail_hist={str(k): v for k, v in sorted(fail_hist.items())},
        witnesses=witnesses,
        budget_hit=budget_hit,
        seconds=round(time.time() - t0, 2),
    )


# ------------------------------------------- class (6,0) at (12,6)


def transversals6(dm):
    """All 6-sets X with X + D = F2^5 (X hits every translate x + D), for
    D = dm.  Complete branch-on-uncovered-requirement search with a bitmask
    of covered requirements; results deduplicated as sets."""
    cov_by = [0] * N5
    for v in range(N5):
        m = 0
        for x in range(N5):
            if (dm >> (x ^ v)) & 1:
                m |= 1 << x
        cov_by[v] = m
    out = set()
    cur = []

    def rec(uncov, vlo):
        if len(cur) == 6:
            if not uncov:
                out.add(frozenset(cur))
            return
        if uncov.bit_count() > 6 * (6 - len(cur)):
            return
        if not uncov:
            for v in range(vlo, N5):
                if v in cur:
                    continue
                cur.append(v)
                rec(uncov, v + 1)
                cur.pop()
            return
        i = (uncov & -uncov).bit_length() - 1
        target = trans(dm, i)
        for v in elems(target):
            if v in cur:
                continue
            cur.append(v)
            rec(uncov & ~cov_by[v], 0)
            cur.pop()

    rec((1 << N5) - 1, 0)
    return out


def class60_check(a0m, a1m, dm):
    """Lines (I''),(II''),(III'') for one (A0, A1, D) triple."""
    fails = []
    if (sumset_mask(a0m, dm)) != ALL:
        fails.append("I")
    if (sumset_mask(a1m, dm)) != ALL:
        fails.append("II")
    if (selfsum_mask(a0m) | selfsum_mask(a1m) | selfsum_mask(dm)) != ALL:
        fails.append("III")
    return (not fails), tuple(fails)


def class60_run(budget=None, shard=0, shards=1):
    """Decision run for class (6,0) at (12,6): complete D-side transversal
    walk.  Normalize 0 in D (H-half translation) and 0 in A1 (H'-half
    translation; the class forces D1 = empty).  For each normalized 6-set D,
    F(D) = {6-sets X : X + D = F2^5} by complete search; then test every
    (A0, A1) with A0 in F(D), A1 in F(D) containing 0 against A0+A1 = F2^5
    and line (III'').  If F(D) is empty for every D, no (6,0) cover exists
    (lines (I'')/(II'') are unsatisfiable).  Deterministic sharding over the
    C(31,5) normalized D by index."""
    t0 = time.time()
    total_d = 169911
    tested_triples = 0
    covering = 0
    witnesses = []
    d_with_transversals = 0
    transversal_total = 0
    d_done = 0
    budget_hit = False
    for idx, dc in enumerate(combinations(range(1, N5), 5)):
        if idx % shards != shard:
            continue
        d_done += 1
        dm = 1 | mask_of(dc)
        F = transversals6(dm)
        if F:
            d_with_transversals += 1
            transversal_total += len(F)
            f_list = sorted(tuple(sorted(s)) for s in F)
            for a1t in f_list:
                if 0 not in a1t:
                    continue
                a1m = mask_of(a1t)
                for a0t in f_list:
                    a0m = mask_of(a0t)
                    if sumset_mask(a0m, a1m) != ALL:
                        continue
                    dm_self = selfsum_mask(dm)
                    if (selfsum_mask(a0m) | selfsum_mask(a1m) | dm_self) != ALL:
                        continue
                    tested_triples += 1
                    covering += 1
                    if len(witnesses) < 5:
                        witnesses.append((a0t, a1t, tuple(sorted(dc)) + (0,)))
        if budget is not None and d_done % 64 == 0 and time.time() - t0 > budget:
            budget_hit = True
            break
    return dict(
        shard=shard,
        shards=shards,
        normalized_d_total=total_d,
        d_checked=d_done,
        d_with_transversals=d_with_transversals,
        transversals_total=transversal_total,
        tested_triples=tested_triples,
        covering_triples=covering,
        witnesses=witnesses,
        budget_hit=budget_hit,
        seconds=round(time.time() - t0, 2),
    )


# ------------------------------------------------- Fourier identity (7,1)


def fourier_71_identity():
    """Exact-integer contradiction for the (10,8) A-vanish tight class (7,1).

    L7 forces |A0+A1| = 25 with |A0| = |A1| = 5 (both odd) inside F2^5.
    With f = 1_A0, g = 1_A1 and h = 1_S on S = A0+A1 (|S| = 25, all pair
    sums distinct), Fourier over F2^5 gives h_hat(v) = f_hat(v) g_hat(v) for
    every v (r = 1_S exactly).  Parseval:
      sum_{v != 0} f_hat^2 = 32*5 - 25 = 135 = sum_{v != 0} g_hat^2,
      sum_{v != 0} h_hat^2 = 32*25 - 625 = 175.
    Parity: |A0| odd makes every f_hat(v) odd, so f_hat^2 >= 1 pointwise;
    hence (f_hat^2 - 1)(g_hat^2 - 1) >= 0 gives f_hat^2 g_hat^2 >=
    f_hat^2 + g_hat^2 - 1 pointwise on v != 0 and therefore
    sum h_hat^2 >= 135 + 135 - 31 = 239 > 175.  Contradiction.

    Returns exact integers; the m=4 analogue (|A0| = 7, |A1| = 1 in F2^3)
    computes need = lower = 7 (no contradiction), matching the real covers
    of the m=4 analogue class in the PR 2933 F2^5 census."""
    out = {}
    for tag, m, kx, ky, s_size in (("m5_k5", 5, 5, 5, 25), ("m3_k2", 3, 2, 2, 4)):
        n = 1 << m
        need = n * s_size - s_size * s_size
        sum_alpha = n * kx - kx * kx
        sum_beta = n * ky - ky * ky
        odd = (kx % 2 == 1) and (ky % 2 == 1)
        lower = sum_alpha + sum_beta - (n - 1) if odd else 0
        out[tag] = dict(
            n=n,
            kx=kx,
            ky=ky,
            s_size=s_size,
            need=need,
            sum_alpha=sum_alpha,
            sum_beta=sum_beta,
            lower_bound=lower,
            parity_odd=odd,
            contradiction=bool(odd and lower > need),
        )
    n = 8
    out["m3_analogue_71"] = dict(
        n=n,
        kx=7,
        ky=1,
        s_size=7,
        need=n * 7 - 49,
        sum_alpha=n * 7 - 49,
        sum_beta=n * 1 - 1,
        lower_bound=(n * 7 - 49) + (n * 1 - 1) - (n - 1),
        parity_odd=True,
        contradiction=(n * 7 - 49) + (n * 1 - 1) - (n - 1) > n * 7 - 49,
    )
    return out


# ------------------------------------------------- m=4 brute-force control


def control_m4_bruteforce():
    """Complete brute force of the two m=4 analogue classes (soundness and
    completeness control for the L7 structural reduction).

    Analogue of the (7,1)-tight class: D-vanish (1,1), A split (7,1),
    F1 = 7*1 + 1*1 = 8 = need.  Analogue of the (8,2)-tight class:
    A-vanish (2,2), D split (2,2), F1 = 4 + 4 = 8 = need.

    Direct route: every (A, D) pair with those splits inside E = F2^4
    (H = bit-0-even half, 8 points each coset), tested against the four L3
    lines.  Every direct cover must show the L7 equality structure (both
    cross sumsets Sidon, disjoint, union the whole odd half)."""
    H = [x for x in range(16) if not (x & 1)]
    Hp = [x for x in range(16) if x & 1]

    def ss(X, Y):
        return {x ^ y for x in X for y in Y}

    def se(X):
        return {x ^ y for x in X for y in X}

    def l3_lines(a0, a1, d0, d1):
        ok_i = ss(a0, d0) | ss(a1, d1) == set(H)
        ok_ii = ss(a0, d1) | ss(a1, d0) == set(Hp)
        ok_iii = se(a0) | se(a1) | se(d0) | se(d1) == set(H)
        ok_iv = ss(a0, a1) | ss(d0, d1) == set(Hp)
        return ok_i and ok_ii and ok_iii and ok_iv

    res = {}

    covers_71 = []
    struct_71 = []
    for a0t in combinations(H, 7):
        a0 = list(a0t)
        for a1 in Hp:
            for d0 in H:
                for d1 in Hp:
                    if l3_lines(a0, [a1], [d0], [d1]):
                        covers_71.append((a0t, a1, d0, d1))
                        sums = ss(a0, [a1])
                        tset = set(Hp) - sums
                        struct_71.append(
                            len(sums) == 7
                            and len(tset) == 1
                            and ({d0 ^ d1} == tset)
                        )
    res["m4_class71_analogue"] = dict(
        direct_covers=len(covers_71),
        all_have_l7_structure=all(struct_71) if struct_71 else None,
    )

    covers_82 = []
    struct_82 = []
    for a0c in combinations(H, 2):
        for a1c in combinations(Hp, 2):
            for d0c in combinations(H, 2):
                for d1c in combinations(Hp, 2):
                    a0, a1 = list(a0c), list(a1c)
                    d0, d1 = list(d0c), list(d1c)
                    if l3_lines(a0, a1, d0, d1):
                        covers_82.append((a0c, a1c, d0c, d1c))
                        sumsA = ss(a0, a1)
                        sumsD = ss(d0, d1)
                        struct_82.append(
                            len(sumsA) == 4
                            and len(sumsD) == 4
                            and not (sumsA & sumsD)
                            and (sumsA | sumsD) == set(Hp)
                        )
    res["m4_class82_analogue"] = dict(
        direct_covers=len(covers_82),
        all_have_l7_structure=all(struct_82) if struct_82 else None,
    )
    return res


def rho_classification():
    """Exact classification of the cross-multiplicity pattern of any
    full-sumset pair of 6-sets in F2^5 (the forced structure of the (12,6)
    A-vanish class (6,0), and of every (A, D) line (I'')/(II'')).

    Let X, Y be 6-sets with X + Y = F2^5 and r(s) = #{(x,y): x+y = s} =
    1 + rho(s), sum rho = 36 - 32 = 4.  Fourier: rho_hat(v) = f_hat(v)
    g_hat(v) for v != 0.  Every f_hat(v), g_hat(v) is even and
    |rho_hat(v)| <= sum rho = 4, so per nonzero v: f_hat(v) g_hat(v) is in
    {0, 4, -4}, i.e. (f_hat, g_hat) = (0, *) or (*, 0) or both +-2.
    Parseval gives sum_{v != 0} f_hat^2 = 156 and rho-Parseval gives
    |V22| = 2 sum rho^2 - 1 where V22 = {v != 0: |f_hat| = |g_hat| = 2}.

    Case table (exact integers; the Walsh constraints are machine-checked in
    test_engine.py):

      rho type   sum rho^2  |V22| needed   Walsh constraint        verdict
      4 delta_p       16          31      rho_hat = +-4 always    DEAD
      3+1             10          19      +-2 occurs for p != q   DEAD
      2+2              8          15      subspace size 15        SURVIVES
      2+1+1            6          11      sizes 2^{5-r}-1         DEAD
      1+1+1+1          4           7      rank-3 flat / rank-2    SURVIVES

    DEAD reasons: (4 delta_p) Parseval 156 = 4*31 + (36a+16b) forces
    32 = 36a+16b with |Vf| = a + b = 0, impossible; (3+1) rho_hat =
    3(-1)^{vq} + (-1)^{vp} lies in {+-2, +-4} and |rho_hat| <= 4 needs
    v*(p+q) = 0 for every v != 0, i.e. p = q; (2+1+1) V22 is
    {v: v*(p1+p2) = 0 and v*(p1+q) = 0} minus {0}, of size 2^{5-r} - 1 in
    {1,3,7,15,31}, never 11.

    Surviving types:
      (T1) rho = 1 on an affine 2-flat {p1, p2, p3, p1+p2+p3} and 0 else;
      (T2) rho = 2 on two distinct points {q1, q2} and 0 else.
    Both sides' spectra are pinned: T1 has |Vf| = |Vg| = 8 all of magnitude
    4 and |V00| = 8; T2 has |Vf| = |Vg| = 6 and |V00| = 4."""
    return {
        "types": [
            dict(
                rho="4*delta_p",
                sum_rho2=16,
                v22_needed=31,
                verdict="DEAD",
                reason="Parseval 156 = 4*31 + (36a+16b) needs 32 = 36a+16b with |Vf| = 0",
            ),
            dict(
                rho="3+1",
                sum_rho2=10,
                v22_needed=19,
                verdict="DEAD",
                reason="v*(p+q) = 0 for all v != 0 forces p = q",
            ),
            dict(
                rho="2+2",
                sum_rho2=8,
                v22_needed=15,
                verdict="SURVIVES",
                v22=15,
                vf=6,
                vg=6,
                v00=4,
            ),
            dict(
                rho="2+1+1",
                sum_rho2=6,
                v22_needed=11,
                verdict="DEAD",
                reason="2^{5-r}-1 in {1,3,7,15,31}, never 11",
            ),
            dict(
                rho="1+1+1+1",
                sum_rho2=4,
                v22_needed=7,
                verdict="SURVIVES",
                v22=7,
                vf=8,
                vg=8,
                v00=8,
            ),
        ],
        "surviving": ["2+2", "1+1+1+1"],
    }


def identity_odd_sides(s, t, m=6):
    """Cross-sum multiplicity identity for splits with BOTH sides odd (the
    (11,7) and (9,9) splits, where no character can vanish - PR 2933 L2).

    With A an s-set and D a t-set in E = F2^m covering the odd line
    A + D = E, the multiplicity is r = 1 + rho with sum rho = s*t - 2^m.
    Fourier over E: rho_hat(v) = f_hat(v) g_hat(v) for v != 0, every f_hat
    and g_hat is odd (s, t odd), so f_hat^2 g_hat^2 >= f_hat^2 + g_hat^2 - 1
    pointwise.  Parseval: sum_{v != 0} f_hat^2 = 2^m s - s^2 and likewise
    for g, sum_{v != 0} rho_hat^2 = 2^m sum rho^2 - (sum rho)^2.

    The pointwise inequality yields the EXACT necessary condition
        2^m sum rho^2 - (st - 2^m)^2 >= (2^m s - s^2) + (2^m t - t^2)
                                       - (2^m - 1),
    i.e. a lower bound on sum rho^2.  For (11,7) and (9,9) at m = 6 the
    bound is satisfiable (the excess 13 resp. 17 is too large for the
    identity to contradict), so the identity is DEMOTED as an exclusion
    mechanism for these splits; the numbers below are exact."""
    n = 1 << m
    excess = s * t - n
    sum_alpha = n * s - s * s
    sum_beta = n * t - t * t
    lower = sum_alpha + sum_beta - (n - 1)
    # sum rho^2 >= ceil((lower + excess^2) / n)
    num = lower + excess * excess
    rho2_min = -(-num // n)
    parity_odd = (s % 2 == 1) and (t % 2 == 1)
    # products f_hat*g_hat must lie within +-excess pointwise
    return dict(
        split=(s, t),
        m=m,
        excess=excess,
        sum_alpha=sum_alpha,
        sum_beta=sum_beta,
        pointwise_lower_sum_rho_hat_sq=lower,
        sum_rho2_min=rho2_min,
        sum_rho2_max=excess * excess,
        parity_odd=parity_odd,
        contradiction=bool(parity_odd and rho2_min > excess * excess),
    )
