"""KB3j engine: the (12,6) A-vanish (4,2) class of the 18-point cover question
for F2^7 (set level; no words).  Exact Python integer arithmetic only.

Class (4,2) EXACT REDUCTION (extends PR 3023's (5,1) reduction).  D1 has two
elements {d1, d1+delta}; global translation by d1 and GL(5,2) (delta -> 1)
give WLOG D1 = {0, 1}.  With U = A0+d1, V = A1+d1, W = D0+d1 the class is
EXACTLY the triples (U, V 6-sets, W 4-set) of F2^5 satisfying

  (a)  (U+W) u (V+D1) = F2^5
  (b)  (U+D1) u (V+W) = F2^5
  (c)  (U+V) u (W+D1) = F2^5
  (d)  (U+U) u (V+V) u (W+W) u (D1+D1) = F2^5      (D1+D1 = {0,1})

and back (A0, A1, D0, D1) = (U, V, W, {0,1}).  The four lines are invariant
under (U+a, V+b, W+a+b) for arbitrary a, b in F2^5 (each line is invariant or
its two summands co-translate; machine-checked in test_engine.py), so WLOG
0 in U and 0 in V.  Mirror symmetry U <-> V is not used for sharding.

Walk (extends avtail.class51_run).  Line (c) forces
M = F2^5 \\ (U+V) into W u (W+1) (|M| <= 8, so |U+V| >= 24), and lines (a),(b)
are hitting requirements on W: every p outside V+D1 must meet p+U in W and
every p outside U+D1 must meet p+V in W.  For each normalized pair (U, V) the
valid W's are found by a complete branch-on-uncovered search over the M
clusters {m, m+1}; every surviving W is tested against (d) exactly.

The (5,1) kill shape is instrumented: per pair we record w_candidates (W
passing (a),(b),(c)) and, among those, how many pass (d).  A class is
pair-killed iff w_candidates = 0 for every normalized pair.

Small-space ground truth: census_k3() is a COMPLETE census of the (4,2) shape
over F2^3 halves (every normalized (U, V, W) triple, every (|U|,|V|,|W|)
class) and census_k4() is a complete normalized census of the floor-surviving
(u, u, w) classes over F2^4 halves.  Both classify each class by kill shape
(pair / line-d / mixed / cover) and are the smallest-instance validation of
the walk machinery.
"""

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

# D1 = {0,1} in F2^5 (or F2^k): its mask and selfsum
D1M5 = 0b11


def lines42(u, v, w, d1=D1M5):
    """The four reduced lines (a),(b),(c),(d) for F2^5 masks u, v, w and
    D1 mask d1 = {0,1}.  Returns (ok, which_lines_fail)."""
    vd = S5(v, d1)
    ud = S5(u, d1)
    wd = S5(w, d1)
    dd = S5(d1, d1)
    fails = []
    if (S5(u, w) | vd) != ALL5:
        fails.append("a")
    if (ud | S5(v, w)) != ALL5:
        fails.append("b")
    if (S5(u, v) | wd) != ALL5:
        fails.append("c")
    if (SS5(u) | SS5(v) | SS5(w) | dd) != ALL5:
        fails.append("d")
    return (not fails), tuple(fails)


def lines42_g(u, v, w, d1, bits, allm):
    """Generic (a),(b),(c),(d) check for F2^bits masks."""
    vd = sumset_g(v, d1, bits, allm)
    ud = sumset_g(u, d1, bits, allm)
    wd = sumset_g(w, d1, bits, allm)
    dd = sumset_g(d1, d1, bits, allm)
    fails = []
    if (sumset_g(u, w, bits, allm) | vd) != allm:
        fails.append("a")
    if (ud | sumset_g(v, w, bits, allm)) != allm:
        fails.append("b")
    if (sumset_g(u, v, bits, allm) | wd) != allm:
        fails.append("c")
    if (selfsum_g(u, bits, allm) | selfsum_g(v, bits, allm) | selfsum_g(w, bits, allm) | dd) != allm:
        fails.append("d")
    return (not fails), tuple(fails)


# --------------------------------------- complete W search per (U, V) pair


X32 = [[1 << (i ^ j) for j in range(N5)] for i in range(N5)]


def _cluster_options(miss):
    """The M-clusters {m, m^1} for m in miss; per cluster the admissible
    subsets of W n miss (every cluster must be met)."""
    clusters = []
    seen = set()
    for m in elems_g(miss):
        if m in seen:
            continue
        p1 = m ^ 1
        seen.add(m)
        seen.add(p1)
        if (miss >> p1) & 1:
            clusters.append([(m,), (p1,), (m, p1)])
        else:
            clusters.append([(m,), (p1,)])
    return clusters


def solve_w42(u, v, wsize=4):
    """Complete list of wsize-sets W satisfying (a),(b),(c) for the pair
    (u, v) in F2^5: W u (W+1) must contain M = ALL5 \\ (u+v) (so W n miss
    meets every cluster {m, m^1}), and W must hit the requirement translates
    (p+u) for p outside v+D1 and (p+v) for p outside u+D1.  Line (d) is NOT
    tested here (exact four-line test in the caller).  Returns W masks."""
    uv = S5(u, v)
    miss = ALL5 ^ uv
    vd = S5(v, D1M5)
    ud = S5(u, D1M5)
    reqs = []
    for p in elems_g(ALL5 ^ vd):
        reqs.append(T5(u, p))
    for p in elems_g(ALL5 ^ ud):
        reqs.append(T5(v, p))
    cov_by = [0] * N5
    for w in range(N5):
        m = 0
        for i, rq in enumerate(reqs):
            if (rq >> w) & 1:
                m |= 1 << i
        cov_by[w] = m
    need = (1 << len(reqs)) - 1
    free = [x for x in range(N5) if not ((miss >> x) & 1)]
    clusters = _cluster_options(miss)
    out = set()

    def emit_supersets(chosen, need_r):
        if need_r == 0:
            out.add(sum(1 << c for c in chosen))
            return
        rest = [x for x in free if x not in chosen]
        for combo in combinations(rest, need_r):
            out.add(sum(1 << c for c in chosen) + sum(1 << c for c in combo))

    def rec(ci, chosen, uncov):
        if len(chosen) > wsize:
            return
        if ci == len(clusters):
            if uncov == 0:
                emit_supersets(chosen, wsize - len(chosen))
                return
            if len(chosen) == wsize:
                return
            # any W must cover the lowest uncovered requirement with a
            # non-miss element (W n miss is already fixed by the clusters)
            i = (uncov & -uncov).bit_length() - 1
            x = reqs[i]
            while x:
                lsb = x & -x
                w = lsb.bit_length() - 1
                x ^= lsb
                if w in chosen or (miss >> w) & 1:
                    continue
                rec(ci, chosen + [w], uncov & ~cov_by[w])
            return
        for opt in clusters[ci]:
            if len(chosen) + len(opt) > wsize:
                continue
            nc = list(chosen)
            nu = uncov
            ok = True
            for w in opt:
                if w in nc:
                    ok = False
                    break
                nc.append(w)
                nu &= ~cov_by[w]
            if ok:
                rec(ci + 1, nc, nu)

    rec(0, [], need)
    return sorted(m for m in out if m.bit_count() == wsize)


def solve_w42_fast(u, v, wsize, TU, vd, ud):
    """Same complete W search as solve_w42 for F2^5, with the requirement
    masks taken from the per-U translate table TU and a per-pair V translate
    (hot path of the walk).  Exact same output as solve_w42 (cross-checked in
    test_engine.py on sampled pairs)."""
    reqs = []
    for p in elems_g(ALL5 ^ vd):
        reqs.append(TU[p])
    vl = elems_g(v)
    for p in elems_g(ALL5 ^ ud):
        m = 0
        for a in vl:
            m |= X32[a][p]
        reqs.append(m)
    cov_by = [0] * N5
    for i, rq in enumerate(reqs):
        x = rq
        bit = 1 << i
        while x:
            lsb = x & -x
            cov_by[lsb.bit_length() - 1] |= bit
            x ^= lsb
    need = (1 << len(reqs)) - 1
    miss = ALL5 ^ S5(u, v)
    free = [x for x in range(N5) if not ((miss >> x) & 1)]
    clusters = _cluster_options(miss)
    out = set()

    def emit_supersets(chosen, need_r):
        if need_r == 0:
            out.add(sum(1 << c for c in chosen))
            return
        rest = [x for x in free if x not in chosen]
        for combo in combinations(rest, need_r):
            out.add(sum(1 << c for c in chosen) + sum(1 << c for c in combo))

    def rec(ci, chosen, uncov):
        if len(chosen) > wsize:
            return
        if ci == len(clusters):
            if uncov == 0:
                emit_supersets(chosen, wsize - len(chosen))
                return
            if len(chosen) == wsize:
                return
            i = (uncov & -uncov).bit_length() - 1
            x = reqs[i]
            while x:
                lsb = x & -x
                w = lsb.bit_length() - 1
                x ^= lsb
                if w in chosen or (miss >> w) & 1:
                    continue
                rec(ci, chosen + [w], uncov & ~cov_by[w])
            return
        for opt in clusters[ci]:
            if len(chosen) + len(opt) > wsize:
                continue
            nc = list(chosen)
            nu = uncov
            ok = True
            for w in opt:
                if w in nc:
                    ok = False
                    break
                nc.append(w)
                nu &= ~cov_by[w]
            if ok:
                rec(ci + 1, nc, nu)

    rec(0, [], need)
    return sorted(m for m in out if m.bit_count() == wsize)


def pair_backtrack42(u, need, TU):
    """All normalized v (0 in v, 6-set) with |u+v| >= need, by monotone
    excess-budget backtracking (excess = 36 - |u+v| grows with v).  Returns
    (vmask, vlist, support=u+v, sv=selfsum(v)) tuples like (5,1)'s engine."""
    out = []
    rest = list(range(1, N5))
    chosen = [0]
    sup = u
    excess = 0
    sv = 1

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


def class42_run(budget=None, shard=0, shards=1, u_limit=None, progress=False):
    """Decision walk for class (12,6) A-vanish (4,2): complete over all
    normalized (U, V) pairs (0 in U, 0 in V, |U+V| >= 24), every admissible W
    per pair (W 4-set with W u (W+1) containing M = F2^5 \\ (U+V) and hitting
    the (a)/(b) requirement translates), exact four-line test on every
    surviving W.  Per-shard resumable via run42.py receipts.  The budget is
    checked after EVERY U (the (5,1) lesson: coarse checks overshoot)."""
    t0 = time.time()
    total_u = 169911
    u_done = 0
    pairs = 0
    pairs_by_size = {}
    w_candidates = 0
    w_by_m = {}
    covering = 0
    fail_hist = {}
    witnesses = []
    budget_hit = False
    for idx, uc in enumerate(combinations(range(1, N5), 5)):
        if idx % shards != shard:
            continue
        if u_limit is not None and u_done >= u_limit:
            budget_hit = True
            break
        u_done += 1
        u = 1 | tight.mask_of(uc)
        ue = (0,) + uc
        TU = [0] * N5
        for r in range(N5):
            m = 0
            for a in ue:
                m |= X32[a][r]
            TU[r] = m
        for (vm, vl, uv, sv) in pair_backtrack42(u, 24, TU):
            pairs += 1
            sz = uv.bit_count()
            pairs_by_size[sz] = pairs_by_size.get(sz, 0) + 1
            miss = ALL5 ^ uv
            mb = miss.bit_count()
            vd = S5(vm, D1M5)
            ud = S5(u, D1M5)
            ws = solve_w42_fast(u, vm, 4, TU, vd, ud)
            w_candidates += len(ws)
            w_by_m[mb] = w_by_m.get(mb, 0) + len(ws)
            for wm in ws:
                ok, fails = lines42(u, vm, wm)
                if ok:
                    covering += 1
                    if len(witnesses) < 5:
                        witnesses.append((list(ue), vl, elems_g(wm)))
                else:
                    fail_hist[fails] = fail_hist.get(fails, 0) + 1
        if progress and u_done % 8 == 0:
            print(
                "PROGRESS shard=%d u=%d pairs=%d w_cand=%d el=%.1f"
                % (shard, u_done, pairs, w_candidates, time.time() - t0),
                flush=True,
            )
        if budget is not None and time.time() - t0 > budget:
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
        w_candidates_by_m_size={str(k): v for k, v in sorted(w_by_m.items())},
        covering_configs=covering,
        fail_hist={str(k): v for k, v in sorted(fail_hist.items())},
        witnesses=witnesses,
        budget_hit=budget_hit,
        seconds=round(time.time() - t0, 2),
    )


# ------------------------------------- small-space complete censuses (k=3/4)


def census_k3():
    """COMPLETE census of the (4,2) shape over F2^3 halves (8-point space):
    every normalized (U, V) pair with 0 in U, 0 in V and every W subset,
    every (|U|,|V|,|W|) class.  Per class: normalized pairs, W candidates
    passing (a),(b),(c), covers passing all four lines, line-(d)-only
    failures, and the kill shape ('pair' = every pair has w_candidates 0;
    'line-d' = every W candidate fails only (d); 'mixed'; 'cover').  Used as
    the smallest complete ground truth for the (4,2) shape."""
    bits = 3
    n = 1 << bits
    allm = (1 << n) - 1
    d1 = 0b11
    subs = list(range(1 << n))
    norm_u = [m for m in subs if m & 1]
    classes = {}
    for u in norm_u:
        for v in norm_u:
            uv = sumset_g(u, v, bits, allm)
            miss = allm ^ uv
            for w_size in range(0, n + 1):
                ws = solve_w42_g(u, v, bits, allm, d1, w_size, miss)
                key = (u.bit_count(), v.bit_count(), w_size)
                r = classes.setdefault(
                    key,
                    dict(
                        pairs=0,
                        pairs_with_w=0,
                        w_candidates=0,
                        covers=0,
                        d_fail_only=0,
                    ),
                )
                r["pairs"] += 1
                r["w_candidates"] += len(ws)
                if ws:
                    r["pairs_with_w"] += 1
                cov = 0
                for wm in ws:
                    ok, _ = lines42_g(u, v, wm, d1, bits, allm)
                    if ok:
                        cov += 1
                r["covers"] += cov
                r["d_fail_only"] += len(ws) - cov
    out = {}
    for key, r in sorted(classes.items()):
        if r["covers"] > 0:
            r["kill_shape"] = "cover"
        elif r["w_candidates"] == 0:
            r["kill_shape"] = "pair"
        else:
            r["kill_shape"] = "line-d"
        out[str(key)] = r
    return out


def census_k4(u_max=5, w_max=6):
    """Complete normalized census of the (4,2) shape classes (u, v, w) over
    F2^4 halves (0 in U, 0 in V) for u, v <= u_max, w <= w_max, by the same
    M-cluster W search as the real walk.  For each class: pairs, the exact
    number of W passing (a),(b),(c) (counted combinatorially over the free
    completions), pairs admitting at least one full cover (decision per pair)
    and the kill shape ('pair' = every pair has w_candidates 0; 'line-d' =
    candidates exist but no completion passes (d); 'cover')."""
    bits = 4
    n = 1 << bits
    allm = (1 << n) - 1
    d1 = 0b11
    pts = list(range(n))
    res = {}
    for u_size in range(1, u_max + 1):
        for u_c in combinations([p for p in pts if p != 0], u_size - 1):
            u = 1 | sum(1 << p for p in u_c)
            ue = (0,) + u_c
            TU = [0] * n
            for r in range(n):
                m = 0
                for a in ue:
                    m |= 1 << (a ^ r)
                TU[r] = m
            for v_size in range(1, u_max + 1):
                for v_c in combinations([p for p in pts if p != 0], v_size - 1):
                    v = 1 | sum(1 << p for p in v_c)
                    uv = sumset_g(u, v, bits, allm)
                    miss = allm ^ uv
                    for w_size in range(1, w_max + 1):
                        key = (u_size, v_size, w_size)
                        r = res.setdefault(
                            key,
                            dict(
                                pairs=0,
                                w_candidates=0,
                                pairs_with_cover=0,
                                pairs_with_w=0,
                            ),
                        )
                        r["pairs"] += 1
                        if 2 * w_size < n - uv.bit_count():
                            continue
                        cnt, has_cover = solve_count_cover_g(u, v, bits, allm, d1, w_size, miss)
                        r["w_candidates"] += cnt
                        if cnt:
                            r["pairs_with_w"] += 1
                        if has_cover:
                            r["pairs_with_cover"] += 1
    out = {}
    for key, r in sorted(res.items()):
        if r["pairs_with_cover"] > 0:
            r["kill_shape"] = "cover"
        elif r["w_candidates"] == 0:
            r["kill_shape"] = "pair"
        else:
            r["kill_shape"] = "line-d"
        out[str(key)] = r
    return out


def solve_count_cover_g(u, v, bits, allm, d1, wsize, miss):
    """Exact W-candidate count for (a),(b),(c) with completions counted
    combinatorially, plus a decision flag for (d) (does any completion pass
    all four lines).  Same search skeleton as solve_w42_g."""
    from math import comb

    n = 1 << bits
    vd = sumset_g(v, d1, bits, allm)
    ud = sumset_g(u, d1, bits, allm)
    reqs = []
    for p in elems_g(allm ^ vd):
        reqs.append(trans_g(u, p, bits, allm))
    for p in elems_g(allm ^ ud):
        reqs.append(trans_g(v, p, bits, allm))
    cov_by = [0] * n
    for i, rq in enumerate(reqs):
        x = rq
        bit = 1 << i
        while x:
            lsb = x & -x
            cov_by[lsb.bit_length() - 1] |= bit
            x ^= lsb
    need = (1 << len(reqs)) - 1
    free = [x for x in range(n) if not ((miss >> x) & 1)]
    clusters = _cluster_options(miss)
    total = 0
    has_cover = [False]

    def test_completions(chosen, need_r):
        nonlocal total
        rest = [x for x in free if x not in chosen]
        if need_r == 0:
            total += 1
            ok, _ = lines42_g(u, v, sum(1 << c for c in chosen), d1, bits, allm)
            if ok:
                has_cover[0] = True
            return
        total += comb(len(rest), need_r)
        if has_cover[0]:
            return
        for combo in combinations(rest, need_r):
            ok, _ = lines42_g(u, v, sum(1 << c for c in chosen) + sum(1 << c for c in combo), d1, bits, allm)
            if ok:
                has_cover[0] = True
                return

    def rec(ci, chosen, uncov):
        if len(chosen) > wsize:
            return
        if ci == len(clusters):
            if uncov == 0:
                test_completions(chosen, wsize - len(chosen))
                return
            if len(chosen) == wsize:
                return
            i = (uncov & -uncov).bit_length() - 1
            x = reqs[i]
            while x:
                lsb = x & -x
                w = lsb.bit_length() - 1
                x ^= lsb
                if w in chosen or (miss >> w) & 1:
                    continue
                rec(ci, chosen + [w], uncov & ~cov_by[w])
            return
        for opt in clusters[ci]:
            if len(chosen) + len(opt) > wsize:
                continue
            nc = list(chosen)
            nu = uncov
            ok = True
            for w in opt:
                if w in nc:
                    ok = False
                    break
                nc.append(w)
                nu &= ~cov_by[w]
            if ok:
                rec(ci + 1, nc, nu)

    rec(0, [], need)
    return total, has_cover[0]


def solve_w42_g(u, v, bits, allm, d1, wsize, miss=None):
    """Generic complete W search (a),(b),(c) for F2^bits: returns W masks.
    Same completeness contract as solve_w42 (cluster options over W n miss,
    free slots from non-miss elements, requirements from both lines)."""
    n = 1 << bits
    if miss is None:
        miss = allm ^ sumset_g(u, v, bits, allm)
    vd = sumset_g(v, d1, bits, allm)
    ud = sumset_g(u, d1, bits, allm)
    reqs = []
    for p in elems_g(allm ^ vd):
        reqs.append(trans_g(u, p, bits, allm))
    for p in elems_g(allm ^ ud):
        reqs.append(trans_g(v, p, bits, allm))
    cov_by = [0] * n
    for w in range(n):
        m = 0
        for i, rq in enumerate(reqs):
            if (rq >> w) & 1:
                m |= 1 << i
        cov_by[w] = m
    need = (1 << len(reqs)) - 1
    free = [x for x in range(n) if not ((miss >> x) & 1)]
    clusters = _cluster_options(miss)
    out = set()

    def emit_supersets(chosen, need_r):
        if need_r == 0:
            out.add(sum(1 << c for c in chosen))
            return
        rest = [x for x in free if x not in chosen]
        for combo in combinations(rest, need_r):
            out.add(sum(1 << c for c in chosen) + sum(1 << c for c in combo))

    def rec(ci, chosen, uncov):
        if len(chosen) > wsize:
            return
        if ci == len(clusters):
            if uncov == 0:
                emit_supersets(chosen, wsize - len(chosen))
                return
            if len(chosen) == wsize:
                return
            i = (uncov & -uncov).bit_length() - 1
            x = reqs[i]
            while x:
                lsb = x & -x
                w = lsb.bit_length() - 1
                x ^= lsb
                if w in chosen or (miss >> w) & 1:
                    continue
                rec(ci, chosen + [w], uncov & ~cov_by[w])
            return
        for opt in clusters[ci]:
            if len(chosen) + len(opt) > wsize:
                continue
            nc = list(chosen)
            nu = uncov
            ok = True
            for w in opt:
                if w in nc:
                    ok = False
                    break
                nc.append(w)
                nu &= ~cov_by[w]
            if ok:
                rec(ci + 1, nc, nu)

    rec(0, [], need)
    return sorted(m for m in out if m.bit_count() == wsize)
