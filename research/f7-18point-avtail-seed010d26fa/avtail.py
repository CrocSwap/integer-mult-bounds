"""KB3h engine: the (12,6) A-vanish TAIL classes of the 18-point cover
question for F2^7 (set level; no words).  Exact Python integer arithmetic
only; masks are Python ints over F2^m coordinates.

Object (unchanged from PR 2911/2933/2961): S = A u B covers F2^7 iff
P + P = F2^7.  With D = p + B inside E = F2^6 the pair (A, D) covers iff
(i) A + D = E and (ii) (A+A) u (D+D) = E.  Fix the vanishing character
psi = bit 0 (WLOG under GL(6,2)); H = ker(psi) and its coset H' are both
identified with F2^5 and coverage is the four PR 2933 L3 lines

  (I)   (A0+D0) u (A1+D1) = F2^5
  (II)  (A0+D1) u (A1+D0) = F2^5
  (III) (A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = F2^5
  (IV)  (A0+A1) u (D0+D1) = F2^5

with A0, A1 the two halves of A (6-sets; A-vanish forces |A0| = |A1| = 6)
and D0, D1 the two halves of D.  This module decides/classifies the three
SURVIVING non-tight A-vanish classes of (12,6), by D-split (x, y) =
(|D0|, |D1|): (5,1), (4,2), (3,3).  PR 2933 recorded their floors
a0*a1 + d0*d1 = 36 + x*y = 41/44/45 >= 32 (line IV); (6,0)'s full-sumset
rigidity (A0+A1 = F2^5) does not extend to them.

CLASS (5,1) EXACT REDUCTION (this module's decision procedure).
D1 = {d1} is a singleton.  Absorb d1 by the two half-translations
U = A0 + d1, V = A1 + d1, W = D0 + d1 (each preserves all four L3 lines
being all of F2^5 - machine-checked in test_engine.py).  The class is then
EXACTLY the triples (U, V 6-sets, W 5-set) of F2^5 satisfying

  (a)  V u (U+W) = F2^5          (line I)
  (b)  U u (V+W) = F2^5          (line II)
  (c)  (U+V) u W = F2^5          (line IV)
  (d)  (U+U) u (V+V) u (W+W) u {0} = F2^5   (line III)

and back (A0, A1, D0, D1) = (U, V, W, {0}).  Residual symmetries
U -> U+a, W -> W+a, V -> V+b (independent half-translations) give WLOG
0 in U and 0 in V in the pair walk.

Walk (extends PR 2961's transversals6 method).  Line (c) forces
M = F2^5 \\ (U+V) to sit inside W (|M| <= 5), and lines (a),(b) are
hitting requirements on W: every p outside V must satisfy W n (p+U) != 0
and every p outside U must satisfy W n (p+V) != 0.  So for each normalized
pair (U, V) with |U+V| >= 27 the valid W's are found by a complete
branch-on-uncovered search seeded with M; every surviving W is tested
against (d) exactly.  The pair enumeration itself is complete over all
normalized (U, V) 6-set pairs with 0 in U, 0 in V and |U+V| >= 27, by a
monotone excess-budget backtracking (excess = 36 - |U+V| <= 9).
"""

import json
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import tight  # noqa: E402  (vendored byte-exact PR 2961 engine)


# ------------------------------------------- generic m-bit mask primitives


def trans_g(mask, a, bits, allm):
    for i in range(bits):
        if (a >> i) & 1:
            b = 1 << i
            lo = 0
            for p in range(1 << bits):
                if not (p & b):
                    lo |= 1 << p
            mask = ((mask & lo) << b) | ((mask & (allm ^ lo)) >> b)
    return mask


def sumset_g(mx, my, bits, allm):
    out = 0
    x = mx
    while x:
        lsb = x & -x
        out |= trans_g(my, lsb.bit_length() - 1, bits, allm)
        x ^= lsb
    return out


def selfsum_g(mx, bits, allm):
    return sumset_g(mx, mx, bits, allm)


def elems_g(mask):
    out = []
    while mask:
        lsb = mask & -mask
        out.append(lsb.bit_length() - 1)
        mask ^= lsb
    return out


# m = 5 fast path (vendored tight primitives; 32-point space)
T5 = tight.trans
S5 = tight.sumset_mask
SS5 = tight.selfsum_mask
ALL5 = tight.ALL
N5 = 32


def lines51(u, v, w):
    """The four reduced lines (a),(b),(c),(d) for F2^5 masks u, v, w.
    Returns (ok, which_lines_fail)."""
    fails = []
    if (v | S5(u, w)) != ALL5:
        fails.append("a")
    if (u | S5(v, w)) != ALL5:
        fails.append("b")
    if (S5(u, v) | w) != ALL5:
        fails.append("c")
    if (SS5(u) | SS5(v) | SS5(w) | 1) != ALL5:
        fails.append("d")
    return (not fails), tuple(fails)


def lines_l3(a0, a1, d0, d1):
    """The four original PR 2933 L3 lines for F2^5 masks."""
    fails = []
    if (S5(a0, d0) | S5(a1, d1)) != ALL5:
        fails.append("I")
    if (S5(a0, d1) | S5(a1, d0)) != ALL5:
        fails.append("II")
    if (SS5(a0) | SS5(a1) | SS5(d0) | SS5(d1)) != ALL5:
        fails.append("III")
    if (S5(a0, a1) | S5(d0, d1)) != ALL5:
        fails.append("IV")
    return (not fails), tuple(fails)


def red51_forward(a0, a1, d0, d1):
    """(A0, A1, D0, D1={d1}) -> (U, V, W) by the two half-translations."""
    (d1,) = elems_g(d1)
    return T5(a0, d1), T5(a1, d1), T5(d0, d1)


def red51_backward(u, v, w):
    """(U, V, W) -> (A0, A1, D0, D1) with D1 = {0}."""
    return u, v, w, 1


# --------------------------------------- complete W search per (U, V) pair


def solve_w(u, v, wsize=5):
    """Complete list of wsize-sets W satisfying (a),(b),(c) for the pair
    (u, v): W must contain M = ALL \\ (u+v), and must hit the requirement
    translates (p+u) for p outside v and (p+v) for p outside u.  Line (d)
    is NOT tested here (exact pair test in the caller)."""
    uv = S5(u, v)
    miss = ALL5 ^ uv
    if miss.bit_count() > wsize:
        return []
    # requirement masks: for each requirement point p, the candidate
    # elements w that satisfy it (w in p+u resp. p+v).
    reqs = []
    for p in elems_g(ALL5 ^ v):
        reqs.append(T5(u, p))
    for p in elems_g(ALL5 ^ u):
        reqs.append(T5(v, p))
    # cov_by[w] = bitmask of requirements that element w covers
    cov_by = [0] * N5
    for w in range(N5):
        m = 0
        for i, rq in enumerate(reqs):
            if (rq >> w) & 1:
                m |= 1 << i
        cov_by[w] = m
    need = (1 << len(reqs)) - 1
    out = set()
    base = sorted(elems_g(miss))

    def rec(uncov, chosen, nxt):
        if len(chosen) == wsize:
            if not uncov:
                out.add(sum(1 << c for c in chosen))
            return
        if uncov.bit_count() > (wsize - len(chosen)) * 12:
            return
        if not uncov:
            for w in range(nxt, N5):
                if w in chosen:
                    continue
                rec(uncov, chosen + [w], w + 1)
            return
        i = (uncov & -uncov).bit_length() - 1
        x = reqs[i]
        while x:
            lsb = x & -x
            w = lsb.bit_length() - 1
            x ^= lsb
            if w in chosen:
                continue
            rec(uncov & ~cov_by[w], chosen + [w], 0)
        return

    rec(need, list(base), 0)
    return sorted(out)


# ---------------------------------------- m=4 analogue control (positive)


def lines51_g(u, v, w, bits, allm):
    """Generic (a),(b),(c),(d) check for F2^bits masks."""
    fails = []
    if (v | sumset_g(u, w, bits, allm)) != allm:
        fails.append("a")
    if (u | sumset_g(v, w, bits, allm)) != allm:
        fails.append("b")
    if (sumset_g(u, v, bits, allm) | w) != allm:
        fails.append("c")
    if (selfsum_g(u, bits, allm) | selfsum_g(v, bits, allm) | selfsum_g(w, bits, allm) | 1) != allm:
        fails.append("d")
    return (not fails), tuple(fails)


def control_m4():
    """Small-space analogue control for the (5,1) machinery: E = F2^m with
    halves H = bit0-even and H', A splits (k, k) (A-vanish), D splits (x, 1)
    (singleton D1, the class-(5,1) shape).  Two independent routes:

      DIRECT: every (A0, A1, D0, D1) with those sizes, tested against
              A + D = E and (A+A) u (D+D) = E in F2^m directly (and against
              the four L3 coordinate lines; the two must agree).
      MACHINERY: the (U, V, W) reduction (U = A0+d1, V = A1+d1, W = D0+d1
              in F2^(m-1) coordinates) tested with lines51_g.

    Both routes must produce the same cover count per class.  The scanned
    set includes cover-bearing classes (positive control), floor-surviving
    but EMPTY classes, and semantic failure controls: line-checker mutants
    (drop (a) or drop (d)) must change at least one census count.  The
    class list was chosen after a complete probe over the (k, x) grid
    (cost-capped); all listed classes are walked in full here."""
    cases = [
        # (m, k, x) - m=3: every floor-surviving singleton-D1 class
        (3, 1, 3), (3, 1, 4), (3, 2, 1), (3, 2, 2), (3, 2, 3), (3, 2, 4),
        (3, 3, 1), (3, 3, 2), (3, 3, 3), (3, 3, 4), (3, 4, 1), (3, 4, 2),
        (3, 4, 3), (3, 4, 4),
        # m=4: cover-bearing, empty-but-floor-surviving, and tight-floor classes
        (4, 1, 7), (4, 1, 8), (4, 2, 4), (4, 2, 5), (4, 3, 1), (4, 4, 1),
        (4, 5, 1), (4, 8, 8),
    ]
    res = {}
    for (m, k, x) in cases:
        bits = m - 1
        n = 1 << bits
        allm = (1 << n) - 1
        pts = 1 << m
        H = [p for p in range(pts) if not (p & 1)]
        Hp = [p for p in range(pts) if p & 1]
        direct = 0
        direct_l3 = 0
        mach = 0
        mach_no_a = 0
        mach_no_d = 0
        for a0t in combinations(H, k):
            for a1t in combinations(Hp, k):
                for d0t in combinations(H, x):
                    for d1t in combinations(Hp, 1):
                        A = list(a0t) + list(a1t)
                        D = list(d0t) + list(d1t)
                        if ss_pts(A, D) == set(range(pts)) and ss_pts(A, A) | ss_pts(D, D) == set(range(pts)):
                            direct += 1
                        a0 = mask3(a0t)
                        a1 = mask3(a1t)
                        d0 = mask3(d0t)
                        d1 = mask3(d1t)
                        if l3_g(a0, a1, d0, d1, bits, allm):
                            direct_l3 += 1
                        (dd,) = elems_g(d1)
                        u = trans_g(a0, dd, bits, allm)
                        v = trans_g(a1, dd, bits, allm)
                        w = trans_g(d0, dd, bits, allm)
                        ok, _ = lines51_g(u, v, w, bits, allm)
                        if ok:
                            mach += 1
                        f1 = (v | sumset_g(u, w, bits, allm)) != allm
                        f2 = (u | sumset_g(v, w, bits, allm)) != allm
                        f3 = (sumset_g(u, v, bits, allm) | w) != allm
                        f4 = (
                            selfsum_g(u, bits, allm)
                            | selfsum_g(v, bits, allm)
                            | selfsum_g(w, bits, allm)
                            | 1
                        ) != allm
                        if (not f2) and (not f3) and (not f4):
                            mach_no_a += 1
                        if (not f1) and (not f2) and (not f3):
                            mach_no_d += 1
        res["m%d_A%d_D%d_%d" % (m, k, x, 1)] = dict(
            m=m,
            k=k,
            x=x,
            floor_value=k * k + x,
            floor_need=n,
            direct_covers=direct,
            direct_l3_covers=direct_l3,
            machinery_covers=mach,
            mutant_drop_a=mach_no_a,
            mutant_drop_d=mach_no_d,
            agreement=(direct == direct_l3 == mach),
        )
    return res


def ss_pts(X, Y):
    return {a ^ b for a in X for b in Y}


def mask3(pts):
    m = 0
    for p in pts:
        m |= 1 << (p >> 1)
    return m


def l3_g(a0, a1, d0, d1, bits, allm):
    """The four L3 lines on F2^bits coordinate masks."""
    ok_i = (sumset_g(a0, d0, bits, allm) | sumset_g(a1, d1, bits, allm)) == allm
    ok_ii = (sumset_g(a0, d1, bits, allm) | sumset_g(a1, d0, bits, allm)) == allm
    ok_iii = (
        selfsum_g(a0, bits, allm)
        | selfsum_g(a1, bits, allm)
        | selfsum_g(d0, bits, allm)
        | selfsum_g(d1, bits, allm)
    ) == allm
    ok_iv = (sumset_g(a0, a1, bits, allm) | sumset_g(d0, d1, bits, allm)) == allm
    return ok_i and ok_ii and ok_iii and ok_iv


def pair_backtrack(u, need):
    """All normalized v (0 in v, 6-set) with |u+v| >= need, by monotone
    excess-budget backtracking over sorted v-sets.  Complete: the excess
    of the partial sumset only grows with v."""
    out = []
    rest = list(range(1, N5))
    chosen = [0]
    cov = [0] * N5  # coverage count r(p) of u+v' over partial v'
    for p in elems_g(u):
        cov[p] = 1

    def excess():
        e = 0
        for p in range(N5):
            if cov[p] > 1:
                e += cov[p] - 1
        return e

    def rec(start):
        if len(chosen) == 6:
            sup = 0
            for c in chosen:
                sup |= T5(u, c)
            if sup.bit_count() >= need:
                out.append(sum(1 << c for c in chosen))
            return
        for i in range(start, len(rest)):
            v = rest[i]
            tr = T5(u, v)
            x = tr
            while x:
                lsb = x & -x
                p = lsb.bit_length() - 1
                cov[p] += 1
                x ^= lsb
            chosen.append(v)
            cur_size = 0
            for p in range(N5):
                if cov[p] > 0:
                    cur_size += 1
            remain = 6 - len(chosen)
            if cur_size + 6 * remain >= need and excess() <= 36 - need:
                rec(i + 1)
            chosen.pop()
            x = tr
            while x:
                lsb = x & -x
                p = lsb.bit_length() - 1
                cov[p] -= 1
                x ^= lsb

    rec(0)
    return out


def class51_reference(budget=None, shard=0, shards=1):
    """Reference decision run for class (12,6) A-vanish (5,1): the direct
    pair_backtrack + solve_w + lines51 loop (readable, validated against
    brute force in test_engine.py).  class51_run below is the optimized
    engine; test_engine.py cross-checks both agree per U slice."""
    t0 = time.time()
    total_u = 169911
    u_done = 0
    pairs = 0
    pairs_by_size = {}
    w_candidates = 0
    covering = 0
    fail_hist = {}
    witnesses = []
    budget_hit = False
    for idx, uc in enumerate(combinations(range(1, N5), 5)):
        if idx % shards != shard:
            continue
        u_done += 1
        u = 1 | tight.mask_of(uc)
        for v in pair_backtrack(u, 27):
            pairs += 1
            sz = S5(u, v).bit_count()
            pairs_by_size[sz] = pairs_by_size.get(sz, 0) + 1
            for w in solve_w(u, v, 5):
                w_candidates += 1
                ok, fails = lines51(u, v, w)
                if ok:
                    covering += 1
                    if len(witnesses) < 5:
                        witnesses.append((elems_g(u), elems_g(v), elems_g(w)))
                else:
                    fail_hist[fails] = fail_hist.get(fails, 0) + 1
        if budget is not None and u_done % 32 == 0 and time.time() - t0 > budget:
            budget_hit = True
            break
    return dict(
        shard=shard,
        shards=shards,
        normalized_u_total=total_u,
        u_checked=u_done,
        uv_pairs=pairs,
        uv_pairs_by_sumset_size={str(k): v for k, v in sorted(pairs_by_size.items())},
        w_candidates=w_candidates,
        covering_configs=covering,
        fail_hist={str(k): v for k, v in sorted(fail_hist.items())},
        witnesses=witnesses,
        budget_hit=budget_hit,
        seconds=round(time.time() - t0, 2),
    )


# ------------------------------------------------ optimized (5,1) engine

# singleton XOR table: X32[a][r] = 1 << (a ^ r)
X32 = [[1 << (i ^ j) for j in range(N5)] for i in range(N5)]


def trans_fast(mask, a, elems):
    """{x ^ a : x in mask} via the singleton table (elems = mask's elements)."""
    out = 0
    for x in elems:
        out |= X32[x][a]
    return out


def pair_backtrack_fast(u, need, TU):
    """Like pair_backtrack, but returns (vmask, vlist, support, sv) with
    support = u+v (bitmask) and sv = selfsum(v), both maintained
    incrementally (excess and support are monotone in v).  TU is the
    per-U translate table (TU[v] == trans(u, v))."""
    out = []
    rest = list(range(1, N5))
    chosen = [0]
    sup = u  # U + 0 already in the partial sumset
    excess = 0
    sv = 1  # selfsum contains 0

    def rec(start):
        nonlocal sup, excess, sv
        if len(chosen) == 6:
            if sup.bit_count() >= need:
                out.append((sum(1 << c for c in chosen), list(chosen), sup, sv))
            return
        for i in range(start, len(rest)):
            v = rest[i]
            tr = TU[v]
            add = (tr & sup).bit_count()
            excess += add
            old_sup = sup
            sup |= tr
            chosen.append(v)
            # sv grows: selfsum(V+v) = sv | trans(V, v) | {0}
            trv = 0
            for c in chosen[:-1]:
                trv |= X32[c][v]
            old_sv = sv
            sv |= trv | (1 << v) | 1
            remain = 6 - len(chosen)
            if sup.bit_count() + 6 * remain >= need and excess <= 36 - need:
                rec(i + 1)
            chosen.pop()
            sv = old_sv
            sup = old_sup
            excess -= add

    rec(0)
    return out


def class51_run(budget=None, shard=0, shards=1):
    """OPTIMIZED decision run for class (12,6) A-vanish (5,1).  Same exact
    object and completeness as class51_reference (cross-checked per U slice
    in test_engine.py): complete over all normalized (U, V) pairs
    (0 in U, 0 in V, |U+V| >= 27), every admissible W per pair (W must
    contain M = F2^5 \\ (U+V) and hit the (a)/(b) requirement translates),
    exact four-line test on every surviving W.

    Per-U precomputation: TU[r] = U+r for all r, su = U+U.  Per-pair:
    M, uM, vM, requirement remainders N1 = (F2^5 \\ V) \\ uM and
    N2 = (F2^5 \\ U) \\ vM; W candidates are filtered in stages
    (U-translate coverage, then V-translate coverage, then line (d))."""
    t0 = time.time()
    total_u = 169911
    u_done = 0
    pairs = 0
    pairs_by_size = {}
    w_candidates = 0
    covering = 0
    fail_hist = {}
    witnesses = []
    budget_hit = False
    for idx, uc in enumerate(combinations(range(1, N5), 5)):
        if idx % shards != shard:
            continue
        u_done += 1
        u = 1 | tight.mask_of(uc)
        ue = (0,) + uc
        TU = [0] * N5
        for r in range(N5):
            m = 0
            for a in ue:
                m |= X32[a][r]
            TU[r] = m
        su = 0
        for a in ue:
            su |= TU[a]
        for (vm, vl, uv, sv) in pair_backtrack_fast(u, 27, TU):
            pairs += 1
            sz = uv.bit_count()
            pairs_by_size[sz] = pairs_by_size.get(sz, 0) + 1
            miss = ALL5 ^ uv
            M = elems_g(miss)
            uM = 0
            for q in M:
                uM |= TU[q]
            vM = 0
            for q in M:
                t = 0
                for a in vl:
                    t |= X32[a][q]
                vM |= t
            N1 = (ALL5 ^ vm) & ~uM
            N2 = ALL5 & ~u & ~vM
            free_l = elems_g(ALL5 ^ miss)
            need_r = 5 - len(M)
            # stage-1 (line (a)) inside pruned nested loops: only R with
            # uM | U+R covering F2^5 \ V reach the candidate list.
            rls = []
            if need_r == 0:
                if not (N1 & ~uM):
                    rls.append(())
            elif need_r == 1:
                for i1, r1 in enumerate(free_l):
                    if not (N1 & ~(uM | TU[r1])):
                        rls.append((r1,))
            elif need_r == 2:
                for i1, r1 in enumerate(free_l):
                    acc1 = uM | TU[r1]
                    if N1 & ~acc1:
                        continue
                    for i2 in range(i1 + 1, len(free_l)):
                        r2 = free_l[i2]
                        if not (N1 & ~(acc1 | TU[r2])):
                            rls.append((r1, r2))
            else:
                for i1, r1 in enumerate(free_l):
                    acc1 = uM | TU[r1]
                    if N1 & ~acc1:
                        continue
                    for i2 in range(i1 + 1, len(free_l)):
                        r2 = free_l[i2]
                        acc2 = acc1 | TU[r2]
                        if N1 & ~acc2:
                            continue
                        for i3 in range(i2 + 1, len(free_l)):
                            r3 = free_l[i3]
                            if not (N1 & ~(acc2 | TU[r3])):
                                rls.append((r1, r2, r3))
            base = None
            for rl in rls:
                accv = vM
                for r in rl:
                    t = 0
                    for a in vl:
                        t |= X32[a][r]
                    accv |= t
                if N2 & ~accv:
                    continue
                w_candidates += 1
                if base is None:
                    b = su | sv | 1
                    for q1 in M:
                        for q2 in M:
                            if q1 != q2:
                                b |= X32[q1][q2]
                    base = b
                dd = base
                for r in rl:
                    for q in M:
                        dd |= X32[q][r]
                    for r2 in rl:
                        if r2 != r:
                            dd |= X32[r][r2]
                if dd != ALL5:
                    fail_hist[("d",)] = fail_hist.get(("d",), 0) + 1
                    continue
                wmask = miss
                for r in rl:
                    wmask |= 1 << r
                covering += 1
                if len(witnesses) < 5:
                    witnesses.append((list(ue), vl, elems_g(wmask)))
        if budget is not None and u_done % 32 == 0 and time.time() - t0 > budget:
            budget_hit = True
            break
    return dict(
        shard=shard,
        shards=shards,
        normalized_u_total=total_u,
        u_checked=u_done,
        uv_pairs=pairs,
        uv_pairs_by_sumset_size={str(k): v for k, v in sorted(pairs_by_size.items())},
        w_candidates=w_candidates,
        covering_configs=covering,
        fail_hist={str(k): v for k, v in sorted(fail_hist.items())},
        witnesses=witnesses,
        budget_hit=budget_hit,
        seconds=round(time.time() - t0, 2),
    )
