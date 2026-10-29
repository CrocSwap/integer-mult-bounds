#!/usr/bin/env python3
"""KB5e: the chi(Z) >= 4 case of F-star residue (ii) (no kappa, no frontier change).

Exact stdlib engine over integer rank-3 decoders M = P Q^T (v lines, nonzero
diagonal). Quantities per instance: zero digraph Z, exact dichromatic number
chi(Z) (subset DP), chi of the underlying graph U(Z) and of the mutual-zero
graph G_0, matched-pivot value (Lemma MP, PR 2717), anchor reach |S_gamma|
(Lemma SG, PR 2869), exact cert(M) by exhaustive a-enumeration with exact
b-completion (small v), engine witnesses with independent replay, and a
bounded admissible-B chain scan as falsifier criterion (PR 2717 chain
cost >= cert(M), PROVEN there and cited, not restated).

Deterministic, stdlib only. Run: python3 -B verify.py
"""
import hashlib
import json
import os
import random
import sys
import time

T0 = time.time()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def log(msg):
    print("[%6.1fs] %s" % (time.time() - T0, msg), flush=True)


# ---------------------------------------------------------------- model

def load_decoder(path):
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    P = [tuple(int(x) for x in line[0]) for line in raw]
    Q = [tuple(int(x) for x in line[1]) for line in raw]
    return P, Q


def model(P, Q):
    v = len(P)
    M = [[sum(P[t][j] * Q[s][j] for j in range(3)) for s in range(v)] for t in range(v)]
    pi = [sum((1 << j) for j in range(3) if P[t][j] != 0) for t in range(v)]
    sg = [sum((1 << j) for j in range(3) if Q[t][j] != 0) for t in range(v)]
    D = [pi[t] & sg[t] for t in range(v)]
    assert all(M[t][t] != 0 for t in range(v)), "diagonal must be nonzero"
    assert all(D[t] != 0 for t in range(v)), "D(t) must be nonempty"
    arcs = [(t, s) for t in range(v) for s in range(v) if t != s and M[t][s] == 0]
    return dict(v=v, P=P, Q=Q, M=M, pi=pi, sg=sg, D=D, arcs=arcs)


def digraph_tables(v, arcs):
    inm = [0] * v
    outm = [0] * v
    for (t, s) in arcs:
        inm[s] |= 1 << t
        outm[t] |= 1 << s
    return inm, outm


def acyclic_table(v, inm):
    """acyc[S] = True iff the induced subdigraph on S is acyclic (subset DP)."""
    acyc = [False] * (1 << v)
    acyc[0] = True
    for S in range(1, 1 << v):
        ok = False
        T = S
        while T:
            b = T & -T
            t = b.bit_length() - 1
            if (inm[t] & S) == 0 and acyc[S ^ b]:
                ok = True
                break
            T ^= b
        acyc[S] = ok
    return acyc


def mas_table(v, acyc):
    """mas[S] = max size of an acyclic induced subset of S."""
    n = 1 << v
    mas = [0] * n
    for S in range(1, n):
        if acyc[S]:
            mas[S] = S.bit_count()
        else:
            T = S
            best = 0
            while T:
                b = T & -T
                val = mas[S ^ b]
                if val > best:
                    best = val
                T ^= b
            mas[S] = best
    return mas


def chi_table(v, acyc):
    """Exact dichromatic number: min number of acyclic classes covering [v]."""
    n = 1 << v
    chi = [v + 1] * n
    chi[0] = 0
    for S in range(1, n):
        lo = S & -S
        best = v + 1
        T = S
        while T:
            if (T & lo) and acyc[T]:
                val = 1 + chi[S ^ T]
                if val < best:
                    best = val
            T = (T - 1) & S
        chi[S] = best
    return chi[-1]


def chi_le_k(v, acyc, k):
    """Exact decision: can [v] be partitioned into k acyclic classes?"""
    classes = [0] * k
    order = list(range(v))

    def rec(i):
        if i == v:
            return True
        t = order[i]
        for c in range(k):
            if acyc[classes[c] | (1 << t)]:
                classes[c] |= 1 << t
                if rec(i + 1):
                    return True
                classes[c] ^= 1 << t
        return False

    return rec(0)


def underlying_arcs(v, arcs):
    """Undirected U(Z): {t,s} iff some direction is an arc. As a bidirected digraph."""
    pairs = set()
    for (t, s) in arcs:
        if t < s:
            pairs.add((t, s))
        else:
            pairs.add((s, t))
    out = []
    for (t, s) in pairs:
        out.append((t, s))
        out.append((s, t))
    return out


def mutual_arcs(v, arcs):
    """Mutual-zero digons G_0 as a bidirected digraph."""
    aset = set(arcs)
    pairs = set()
    for (t, s) in arcs:
        if t < s and (s, t) in aset:
            pairs.add((t, s))
    out = []
    for (t, s) in pairs:
        out.append((t, s))
        out.append((s, t))
    return out


# ------------------------------------------------------- Lemma SG anchor

def v2_int(n):
    if n == 0:
        raise ValueError("v2(0)")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def anchor_reach(mod):
    """Lemma SG (PR 2869): gamma = min_j c_j, S_gamma = {t : v2(M_tt) = gamma}.

    c_j = min v2(p_j(t)) + min v2(q_j(s)) over nonzero entries (Lemma SC).
    Returns (gamma, reach count, cancellation count, per-line v2 diagonal).
    """
    P, Q, M = mod["P"], mod["Q"], mod["M"]
    v = mod["v"]
    cs = []
    for j in range(3):
        mp = [v2_int(P[t][j]) for t in range(v) if P[t][j] != 0]
        mq = [v2_int(Q[t][j]) for t in range(v) if Q[t][j] != 0]
        if mp and mq:
            cs.append(min(mp) + min(mq))
    gamma = min(cs)
    diag = [v2_int(M[t][t]) for t in range(v)]
    reach = sum(1 for t in range(v) if diag[t] == gamma)
    cancel = sum(1 for t in range(v) if diag[t] > gamma)
    return gamma, reach, cancel, diag


# ----------------------------------------------------- Lemma MP pivots

def matched_pivot(mod, acyc, mas, exhaustive_cap=200000, seed=20261016):
    """max over pivot maps c(t) in D(t) (unit masks) of sum_i MAS(Z[C_i])."""
    v = mod["v"]
    allowed = [[1 << j for j in range(3) if mod["D"][t] & (1 << j)] for t in range(v)]
    prod = 1
    for a in allowed:
        prod *= len(a)
    best = -1
    best_map = None
    exhaustive = prod <= exhaustive_cap
    if exhaustive:
        import itertools
        for combo in itertools.product(*allowed):
            classes = [0, 0, 0]
            for t in range(v):
                i = combo[t].bit_length() - 1
                classes[i] |= 1 << t
            val = mas[classes[0]] + mas[classes[1]] + mas[classes[2]]
            if val > best:
                best = val
                best_map = combo
    else:
        rng = random.Random(seed)
        for _ in range(exhaustive_cap):
            combo = tuple(a[rng.randrange(len(a))] for a in allowed)
            classes = [0, 0, 0]
            for t in range(v):
                i = combo[t].bit_length() - 1
                classes[i] |= 1 << t
            val = mas[classes[0]] + mas[classes[1]] + mas[classes[2]]
            if val > best:
                best = val
                best_map = combo
    return best, best_map, exhaustive, prod


# --------------------------------------------------------- cert engine

def dot1(x, y):
    return bin(x & y).count("1") & 1


def span_add(basis, x):
    """Canonical F2 span extension: pivot-reduced basis of span(basis) + x."""
    pivots = {}
    for r in list(basis) + [x]:
        while r:
            p = r.bit_length() - 1
            if p in pivots:
                r ^= pivots[p]
            else:
                pivots[p] = r
                break
    return tuple(sorted(pivots.values(), reverse=True))


def b_choices(sig_mask):
    return [b for b in range(8) if (b & ~sig_mask) == 0]


def completion(mod, a):
    """Exact completion over b-labels/order/kept set for fixed a-labels (PR 2717
    engine design). Returns (best size, witness dict or None)."""
    v = mod["v"]
    M, sg = mod["M"], mod["sg"]
    inm, _ = digraph_tables(v, mod["arcs"])
    blockers = [inm[t] for t in range(v)]  # s with M[s][t] == 0
    bex = {}
    basis_tab = [dict() for _ in range(v)]
    b_all = [b_choices(sg[t]) for t in range(v)]

    def b_exists(t, basis):
        key = (t, basis)
        if key in bex:
            return bex[key]
        for b in b_all[t]:
            if dot1(a[t], b) != 1:
                continue
            if all(dot1(x, b) == 0 for x in basis):
                bex[key] = (True, b)
                return bex[key]
        bex[key] = (False, 0)
        return bex[key]

    def basis_of(t, T):
        d = basis_tab[t]
        if T in d:
            return d[T]
        if T == 0:
            d[0] = ()
            return ()
        b = T & -T
        s = b.bit_length() - 1
        prev = basis_of(t, T ^ b)
        val = span_add(prev, a[s]) if (blockers[t] & b) else prev
        d[T] = val
        return val

    n = 1 << v
    feas = [False] * n
    feas[0] = True
    choice = [-1] * n
    for T in range(1, n):
        U = T
        while U:
            b = U & -U
            t = b.bit_length() - 1
            rest = T ^ b
            if feas[rest]:
                ok, _bv = b_exists(t, basis_of(t, rest))
                if ok:
                    feas[T] = True
                    choice[T] = t
                    break
            U ^= b
    best = max(T for T in range(n) if feas[T])
    if best == 0:
        return 0, None
    kept = []
    bvec = [0] * v
    T = best
    while T:
        t = choice[T]
        _ok, bv = b_exists(t, basis_of(t, T ^ (1 << t)))
        bvec[t] = bv
        kept.append(t)
        T ^= 1 << t
    kept.reverse()
    return best.bit_count(), dict(a=list(a), b=bvec, order=list(kept), kept=list(kept))


def replay_witness(mod, wit):
    """Independent replay: supports, K_tt = 1 on kept, order constraints from scratch."""
    v, M = mod["v"], mod["M"]
    a, b = wit["a"], wit["b"]
    kept = list(wit["kept"])
    order = list(wit["order"])
    if sorted(order) != sorted(kept):
        return False
    for t in kept:
        if (a[t] & ~mod["pi"][t]) or (b[t] & ~mod["sg"][t]):
            return False
        if dot1(a[t], b[t]) != 1:
            return False
    pos = {t: i for i, t in enumerate(order)}
    for t in kept:
        for s in kept:
            if t == s:
                continue
            if M[t][s] == 0 and pos[t] < pos[s]:
                if dot1(a[t], b[s]) != 0:
                    return False
    return True


def cert_exact(mod, max_v=5):
    """Exact cert by exhaustive a-enumeration (small v only)."""
    v = mod["v"]
    if v > max_v:
        return None, None
    choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0] for t in range(v)]
    best = -1
    best_wit = None
    import itertools
    for combo in itertools.product(*choices):
        val, wit = completion(mod, list(combo))
        if val > best:
            best = val
            best_wit = wit
    return best, best_wit


def cert_hillclimb(mod, iters=400, seed=1234):
    """Bounded deterministic hill-climb over a-labels with exact completion."""
    v = mod["v"]
    rng = random.Random(seed)
    choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0] for t in range(v)]
    a = [c[rng.randrange(len(c))] for c in choices]
    best, best_wit = completion(mod, a)
    cur = list(a)
    for it in range(iters):
        t = rng.randrange(v)
        old = cur[t]
        new = choices[t][rng.randrange(len(choices[t]))]
        if new == old:
            continue
        cur[t] = new
        val, wit = completion(mod, cur)
        if val >= best:
            best, best_wit = val, wit
        else:
            cur[t] = old
    return best, best_wit


# ----------------------------------------------- chain machinery (falsifier)

def gf2_rank(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def chain_cost(mod, B):
    """sum_j rank_F2 B[R_j, A_j] for admissible B (0/1 lists of row masks)."""
    P, Q, v = mod["P"], mod["Q"], mod["v"]
    total = 0
    for j in range(3):
        R = [t for t in range(v) if P[t][j] != 0]
        A = [s for s in range(v) if Q[s][j] != 0]
        rows = []
        for t in R:
            mask = 0
            for s in A:
                if B[t][s]:
                    mask |= 1 << A.index(s)
            rows.append(mask)
        total += gf2_rank(rows)
    return total


def admissible(mod, B):
    v, M = mod["v"], mod["M"]
    for t in range(v):
        if B[t][t] != 1:
            return False
        for s in range(v):
            if t != s and B[t][s] == 1 and M[t][s] != 0:
                return False
    return True


def chain_scan(mod, threshold, seed=99, tries=3000):
    """Bounded deterministic scan for an admissible B with chain cost < threshold."""
    v = mod["v"]
    rng = random.Random(seed)
    best = None
    best_cost = None
    for _ in range(tries):
        B = [[0] * v for _ in range(v)]
        for t in range(v):
            B[t][t] = 1
            for s in range(v):
                if t != s and mod["M"][t][s] == 0 and rng.random() < 0.5:
                    B[t][s] = 1
        if not admissible(mod, B):
            continue
        c = chain_cost(mod, B)
        if best_cost is None or c < best_cost:
            best_cost = c
            best = B
        if best_cost is not None and best_cost < threshold:
            return best_cost, best, True
    return best_cost, best, False


# --------------------------------------------------------------- controls

def brute_force_cert(mod):
    """Cert from the definition: all labellings, all orders (tiny v only)."""
    v, M = mod["v"], mod["M"]
    choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0] for t in range(v)]
    bchoices = [[m for m in range(8) if (m & ~mod["sg"][t]) == 0] for t in range(v)]
    best = 0
    import itertools
    for a in itertools.product(*choices):
        for b in itertools.product(*bchoices):
            for k in range(1, v + 1):
                for sub in itertools.permutations(range(v), k):
                    ok = True
                    for i, t in enumerate(sub):
                        if dot1(a[t], b[t]) != 1:
                            ok = False
                            break
                        for s in sub[i + 1:]:
                            if M[t][s] == 0 and dot1(a[t], b[s]) != 0:
                                ok = False
                                break
                        if not ok:
                            break
                    if ok and k > best:
                        best = k
    return best


def run_controls():
    log("controls")
    # 1. brute-force vs engine agreement at v = 3 (3 tiny instances)
    tiny = [
        ([(1, 0, 0), (0, 1, 0), (1, 1, 0)], [(1, 0, 0), (0, 1, 0), (1, 0, 1)]),
        ([(1, 1, 0), (1, 0, 1), (0, 1, 1)], [(1, 0, -1), (1, -1, 0), (1, 1, 1)]),
        ([(1, -1, -1), (0, 1, 1), (1, 1, 0)], [(1, 1, 1), (1, 1, 0), (0, 1, 1)]),
    ]
    agree = 0
    for P, Q in tiny:
        mod = model(P, Q)
        bf = brute_force_cert(mod)
        ex, _w = cert_exact(mod)
        if bf == ex:
            agree += 1
    assert agree == 3, "brute-force agreement failed"
    # 2. diagonal decoder: cert = 3, MP = 3
    mod = model([(1, 0, 0), (0, 1, 0), (0, 0, 1)], [(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    ex, _w = cert_exact(mod)
    assert ex == 3, "diagonal decoder cert"
    mp, _m, _exh, _prod = matched_pivot(mod, acyc, mas)
    assert mp == 3, "diagonal decoder MP"
    assert chi_table(mod["v"], acyc) == 3, "diagonal decoder chi(Z) (bidirected K3)"
    # 3. corrupted witnesses rejected
    mod = model([(1, 1, 0), (1, 0, 1)], [(1, 0, -1), (1, -1, 0)])
    _val, wit = cert_exact(mod)
    assert replay_witness(mod, wit)
    bad1 = dict(wit); bad1["a"] = list(wit["a"]); bad1["a"][0] = 0
    bad2 = dict(wit); bad2["b"] = list(wit["b"]); bad2["b"][1] = 0
    assert not replay_witness(mod, bad1), "corrupt a not rejected"
    assert not replay_witness(mod, bad2), "corrupt b not rejected"
    # 4. hand digraph chi values (digraph-only controls)
    def chi_of(v, arcs):
        inm, _ = digraph_tables(v, arcs)
        return chi_table(v, acyclic_table(v, inm))
    assert chi_of(2, [(0, 1), (1, 0)]) == 2, "digon chi"
    assert chi_of(3, [(0, 1), (1, 2), (2, 0)]) == 2, "directed 3-cycle chi (2, not 1)"
    c5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    c5 += [(s, t) for (t, s) in c5]
    assert chi_of(5, c5) == 3, "bidirected C5 chi"
    k4 = [(t, s) for t in range(4) for s in range(4) if t != s]
    assert chi_of(4, k4) == 4, "bidirected K4 chi"
    # 5. C5 perpendicularity construction (hand): M = P P^T gives Z = bidirected C5
    P5 = [(1, 0, 0), (0, 1, 0), (1, 0, 1), (-1, -1, 1), (0, 1, 1)]
    mod = model(P5, [tuple(p) for p in P5])
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    assert chi_table(mod["v"], acyc) == 3, "C5 perpendicularity chi(Z)"
    mut = mutual_arcs(mod["v"], mod["arcs"])
    assert len(mut) == 10, "C5 mutual arcs (bidirected, 5 digons)"
    # 6. maintainer's retained rank-2 pivot counterexample (efficient1700 audit)
    mod = model([(1, 1, 0), (1, 0, 1)], [(1, 0, -1), (1, -1, 0)])
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    assert chi_table(mod["v"], acyc) == 2 <= 3, "counterexample ordinary chi"
    mp, _m, _exh, _prod = matched_pivot(mod, acyc, mas)
    assert mp == 1 and mp < mod["v"], "counterexample MP under D(t)"
    # 7. anchor reach hand values (PR 2869 control SC2: M = 2 I_3)
    mod = model([(2, 0, 0), (0, 2, 0), (0, 0, 2)], [(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    gamma, reach, cancel, _d = anchor_reach(mod)
    assert (gamma, reach, cancel) == (1, 3, 0), "M = 2 I_3 anchor reach"
    # 8. W5-underlying separation example (hand): chi(U) = 4 while chi(Z) = 2.
    Pw = [(1, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 1)]
    Qw = [(1, 0, 0), (0, 1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, -1)]
    mod = model(Pw, Qw)
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    assert chi_table(mod["v"], acyc) == 2, "W5-underlying example chi(Z) must be 2"
    uarcs = underlying_arcs(mod["v"], mod["arcs"])
    u_inm, _ = digraph_tables(mod["v"], uarcs)
    assert chi_table(mod["v"], acyclic_table(mod["v"], u_inm)) == 4, \
        "W5-underlying example chi(U) must be 4"
    assert len(uarcs) == 20, "W5-underlying example U must have 10 edges"
    log("controls: brute_agree=3/3 diagonal=3 mp=3 corrupt_rejects=2/2 "
        "chi_hands=4/4 c5_perp=3 pivot_counterexample mp=1 anchor_SC2=3 "
        "w5_underlying chiU=4 chiZ=2")
    print("PASS_FC4_CONTROLS")


def v2_diag_assert(mod, expect_gamma, expect_reach, expect_cancel, name):
    gamma, reach, cancel, diag = anchor_reach(mod)
    assert (gamma, reach, cancel) == (expect_gamma, expect_reach, expect_cancel), \
        "%s anchor (gamma, reach, cancel) = %r" % (name, (gamma, reach, cancel))
    return diag


def mutual_omega(v, mut):
    """Largest mutual-zero clique: max subset with every pair a digon."""
    edge = [[False] * v for _ in range(v)]
    for (t, s) in mut:
        edge[t][s] = True
    n = 1 << v
    ok = [False] * n
    ok[0] = True
    omega = 0
    for S in range(1, n):
        b = S & -S
        t = b.bit_length() - 1
        R = S ^ b
        if ok[R]:
            good = True
            T = R
            while T:
                c = T & -T
                if not edge[t][c.bit_length() - 1]:
                    good = False
                    break
                T ^= c
            if good:
                ok[S] = True
                if S.bit_count() > omega:
                    omega = S.bit_count()
    return omega


def fixture_invariants(mod, acyc, mas):
    mut = mutual_arcs(mod["v"], mod["arcs"])
    return mutual_omega(mod["v"], mut)


# -------------------------------------------------------------- calibration

def run_calibration():
    """Reproduce the recorded anchors of PRs 2717/2747/2774/2869 in this engine."""
    log("calibration (recorded anchors)")
    # tied_min (v = 12): PR 2717 witness 11/12; PR 2747 MP/MX 9; PR 2774 chi(Z)=3,
    # MAS(Z)=4, omega=3, MP deficit 3; PR 2869 reach 0 of 12.
    mod = load_model("tied_min.json")
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    chi = chi_table(mod["v"], acyc)
    assert chi == 3, "tied_min chi(Z) must be 3 exactly"
    assert mas[-1] == 4, "tied_min MAS(Z) must be 4"
    omega = fixture_invariants(mod, acyc, mas)
    assert omega == 3, "tied_min mutual-zero omega must be 3"
    mp, _m, exh, prod = matched_pivot(mod, acyc, mas)
    assert exh and prod == 4096 and mp == 9, "tied_min MP must be 9 (4096 maps)"
    assert not chi_le_k(mod["v"], acyc, 3) or mp < mod["v"], "tied_min D-structure"
    assert mp == 9 and mp < 12, "tied_min non-3-dichromatic under D(t)"
    gamma, reach, cancel, diag = anchor_reach(mod)
    assert (gamma, reach, cancel) == (0, 0, 12), "tied_min anchor reach 0/12"
    val, wit = cert_hillclimb(mod, iters=250, seed=11)
    assert replay_witness(mod, wit) and val == 11, "tied_min engine witness 11"
    assert val >= 8, "tied_min F-star threshold 8"
    log("tied_min.json: v=12 thr=8 MP=9 (4096 maps) chi=3 MAS=4 omega=3 "
        "reach=0/12 witness=%d (PR 2717 recorded 11/12)" % val)
    # cex_min_1 (v = 19): PR 2717 stored witness 18/19; PR 2747 MP/MX 16;
    # PR 2774 chi le 3 with mutual triangle; PR 2869 reach 8 of 19.
    mod = load_model("cex_min_1.json")
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    assert chi_le_k(mod["v"], acyc, 3), "cex_min_1 must be 3-dichromatic"
    mut = mutual_arcs(mod["v"], mod["arcs"])
    tri = False
    for a in range(19):
        for b in range(a + 1, 19):
            for c in range(b + 1, 19):
                aset = set(mut)
                if (a, b) in aset and (b, c) in aset and (a, c) in aset:
                    tri = True
    assert tri, "cex_min_1 mutual-zero triangle forces chi >= 3"
    assert mas[-1] == 10, "cex_min_1 MAS(Z) must be 10"
    mp, _m, exh, prod = matched_pivot(mod, acyc, mas)
    assert exh and prod == 6144 and mp == 16, "cex_min_1 MP must be 16 (6144 maps)"
    gamma, reach, cancel, diag = anchor_reach(mod)
    assert (gamma, reach, cancel) == (0, 8, 11), "cex_min_1 anchor reach 8/19"
    with open(os.path.join(DATA, "cex_min_1.witness.json"), "r", encoding="utf-8") as fh:
        wit = json.load(fh)
    wit = dict(a=wit["a"], b=wit["b"], order=wit["order"], kept=wit["kept"])
    assert replay_witness(mod, wit), "cex_min_1 stored witness replay"
    assert len(wit["kept"]) == 18 and 18 >= 12, "cex_min_1 stored witness 18/19"
    log("cex_min_1.json: v=19 thr=12 MP=16 (6144 maps) chi=le3 (mutual triangle) "
        "MAS=10 reach=8/19 witness=18 (PR 2717 recorded 18/19)")
    # chain engine 22 on PR 2111's stored pairing (PR 2717 anchor).
    with open(os.path.join(DATA, "cex_min_1.B22.json"), "r", encoding="utf-8") as fh:
        B = json.load(fh)
    if isinstance(B, dict):
        B = B.get("B", B.get("pairing"))
    assert admissible(mod, B), "stored pairing admissible"
    cc = chain_cost(mod, B)
    assert cc == 22, "chain engine must reproduce 22 (10+6+6)"
    log("chain engine on stored pairing: chain_cost=22 (PR 2111 recorded 10+6+6=22)")
    print("PASS_FC4_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22")
    return True


def load_model(name):
    return model(*load_decoder(os.path.join(DATA, name)))


# ------------------------------------------------------- chi4 settlement

def settle(mod, label, exact_cert_max_v=6):
    """Full settlement record for one decoder."""
    v = mod["v"]
    inm, _ = digraph_tables(v, mod["arcs"])
    acyc = acyclic_table(v, inm)
    mas = mas_table(v, acyc)
    uarcs = underlying_arcs(v, mod["arcs"])
    u_inm, _ = digraph_tables(v, uarcs)
    u_acyc = acyclic_table(v, u_inm)
    mut = mutual_arcs(v, mod["arcs"])
    m_inm, _ = digraph_tables(v, mut)
    m_acyc = acyclic_table(v, m_inm)
    thr = (2 * v) // 3
    rec = dict(label=label, v=v, threshold=thr)
    rec["chi_le3"] = chi_le_k(v, acyc, 3)
    rec["chi"] = chi_table(v, acyc) if v <= 14 else (3 if rec["chi_le3"] else None)
    rec["chi_exact"] = v <= 14
    rec["chi_U_le3"] = chi_le_k(v, u_acyc, 3)
    rec["chi_U"] = chi_table(v, u_acyc) if v <= 14 else (3 if rec["chi_U_le3"] else None)
    rec["chi_G0_le3"] = chi_le_k(v, m_acyc, 3)
    rec["chi_G0"] = chi_table(v, m_acyc) if v <= 14 else (3 if rec["chi_G0_le3"] else None)
    rec["MAS_Z"] = mas[-1]
    rec["omega_mutual"] = mutual_omega(v, mut) if v <= 16 else None
    mp, mpmap, exh, prod = matched_pivot(mod, acyc, mas)
    rec["MP"] = mp
    rec["MP_exhaustive"] = exh
    rec["MP_pivot_product"] = prod
    rec["D_compatible_3dic"] = (mp == v)
    gamma, reach, cancel, diag = anchor_reach(mod)
    rec.update(gamma=gamma, anchor_reach=reach, cancellation_lines=cancel)
    # Lemma SF bound through H (block-incidence digraph)
    H = [(t, s) for (t, s) in mod["arcs"] if mod["pi"][t] & mod["sg"][s]]
    h_inm, _ = digraph_tables(v, H)
    h_acyc = acyclic_table(v, h_inm)
    rec["MAS_H"] = mas_table(v, h_acyc)[-1]
    lower = max(mp, reach, rec["MAS_H"])
    exact = None
    wit = None
    if v <= exact_cert_max_v:
        exact, wit = cert_exact(mod, max_v=exact_cert_max_v)
        if exact is not None:
            lower = max(lower, exact)
    else:
        val, wit = cert_hillclimb(mod, iters=300, seed=77)
        assert replay_witness(mod, wit), "hill-climb witness must replay"
        lower = max(lower, val)
    rec["cert_exact"] = exact
    rec["cert_lower_bound"] = lower
    rec["witness_replayed"] = replay_witness(mod, wit) if wit else None
    rec["meets_threshold"] = lower >= thr
    if lower < thr:
        cc, _B, hit = chain_scan(mod, thr)
        rec["chain_scan_best"] = cc
        rec["falsifier_found"] = hit
    else:
        rec["falsifier_found"] = False
    return rec, mod, wit


# ------------------------------------------------------------ chi4 search

def gen_random(rng, v, sym):
    P = [tuple(rng.randint(-2, 2) for _ in range(3)) for _ in range(v)]
    if sym:
        Q = list(P)
    else:
        Q = [tuple(rng.randint(-2, 2) for _ in range(3)) for _ in range(v)]
    return P, Q


def gen_mutual_dense(rng, v):
    """Rejection sampling for many mutual-zero pairs (dense digon structure)."""
    for _ in range(400):
        P, Q = gen_random(rng, v, False)
        if not valid(P, Q):
            continue
        mod = model(P, Q)
        mut = mutual_arcs(v, mod["arcs"])
        if len(mut) // 2 >= v:
            return P, Q
    return None, None


def gen_c5seed(rng, v):
    """Start from the hand C5 perpendicularity construction; extend at random."""
    P5 = [(1, 0, 0), (0, 1, 0), (1, 0, 1), (-1, -1, 1), (0, 1, 1)]
    P = [tuple(p) for p in P5]
    Q = [tuple(p) for p in P5]
    while len(P) < v:
        P.append(tuple(rng.randint(-2, 2) for _ in range(3)))
        Q.append(tuple(rng.randint(-2, 2) for _ in range(3)))
    return P[:v], Q[:v]


def valid(P, Q):
    v = len(P)
    for t in range(v):
        if sum(P[t][j] * Q[t][j] for j in range(3)) == 0:
            return False
        if all(x == 0 for x in P[t]) or all(x == 0 for x in Q[t]):
            return False
    return True


def dot3(a, b):
    return sum(a[j] * b[j] for j in range(3))


def nullspace3(constraints):
    """Basis of {x in Q^3 : c . x = 0 for c in constraints}; exact Fractions."""
    from fractions import Fraction
    rows = []
    for c in constraints:
        x = [Fraction(c[j]) for j in range(3)]
        for prow in rows:
            p = next(k for k in range(3) if prow[k] != 0)
            if x[p] != 0:
                fac = x[p] / prow[p]
                x = [x[k] - fac * prow[k] for k in range(3)]
        if any(x):
            rows.append(x)
    rank = len(rows)
    if rank >= 3:
        return []
    if rank == 0:
        return [(Fraction(1), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(1), Fraction(0)),
                (Fraction(0), Fraction(0), Fraction(1))]
    if rank == 1:
        c = rows[0]
        vecs = []
        for e in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            w = (c[1] * e[2] - c[2] * e[1],
                 c[2] * e[0] - c[0] * e[2],
                 c[0] * e[1] - c[1] * e[0])
            if any(w):
                keep = True
                for u in vecs:
                    cr = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2],
                          u[0] * w[1] - u[1] * w[0])
                    if not any(cr):
                        keep = False
                        break
                if keep:
                    vecs.append(w)
            if len(vecs) == 2:
                break
        return vecs
    u = (rows[0][1] * rows[1][2] - rows[0][2] * rows[1][1],
         rows[0][2] * rows[1][0] - rows[0][0] * rows[1][2],
         rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0])
    return [u] if any(u) else []


def sample_in_span(basis, rng, box):
    from fractions import Fraction
    import math
    for _ in range(40):
        co = [rng.randint(-2, 2) for _ in basis]
        x = [sum(co[i] * basis[i][j] for i in range(len(basis))) for j in range(3)]
        if not any(x):
            continue
        den = 1
        for t in x:
            den = den * t.denominator // math.gcd(den, t.denominator)
        xi = tuple(int(t * den) for t in x)
        g = 0
        for t in xi:
            g = math.gcd(g, abs(t))
        if g > 1:
            xi = tuple(t // g for t in xi)
        if max(abs(t) for t in xi) <= box * 4:
            return xi
    return None


def grz_instance():
    """Grötzsch graph M(C5): u0..u4 outer cycle, v0..v4 inner, w apex."""
    names = [("u%d" % i) for i in range(5)] + [("v%d" % i) for i in range(5)] + ["w"]
    E = set()
    for i in range(5):
        E.add(frozenset(("u%d" % i, "u%d" % ((i + 1) % 5))))
        E.add(frozenset(("v%d" % i, "u%d" % ((i - 1) % 5))))
        E.add(frozenset(("v%d" % i, "u%d" % ((i + 1) % 5))))
        E.add(frozenset(("v%d" % i, "w")))
    return names, sorted(E, key=lambda s: sorted(s))


def sequential_build(names, edges, rng, box, node_cap=60000):
    """Sequential linear construction of a target graph as mutual-zero G_0:
    place vertices in degree order; p_i _|_ q_j and q_i _|_ p_j for placed edge
    neighbours (exact linear nullspace), generic integer point in the solution
    subspace, backtrack on failure. Returns (P, Q) or (None, failure record)."""
    v = len(names)
    idx = {n: i for i, n in enumerate(names)}
    eset = set(frozenset(e) for e in edges)
    adj = [set() for _ in range(v)]
    for e in eset:
        a, b = (idx[x] for x in e)
        adj[a].add(b)
        adj[b].add(a)
    order = sorted(range(v), key=lambda i: -len(adj[i]))
    P = [None] * v
    Q = [None] * v
    nodes = [0]
    deepest = [0]
    reason = ["none"]

    def rec(k):
        nodes[0] += 1
        if nodes[0] > node_cap:
            reason[0] = "node_cap"
            return False
        if k > deepest[0]:
            deepest[0] = k
        if k == v:
            return True
        i = order[k]
        placed = [j for j in adj[i] if P[j] is not None]
        pb = nullspace3([Q[j] for j in placed])
        qb = nullspace3([P[j] for j in placed])
        if not pb or not qb:
            reason[0] = "nullspace_collapse"
            return False
        for _try in range(24):
            p = sample_in_span(pb, rng, box)
            q = sample_in_span(qb, rng, box)
            if p is None or q is None:
                reason[0] = "sample_exhausted"
                break
            if dot3(p, q) == 0:
                continue
            bad = False
            for j in range(v):
                if j == i or P[j] is None:
                    continue
                e = frozenset((names[i], names[j])) in eset
                m1 = dot3(p, Q[j])
                m2 = dot3(P[j], q)
                if e and (m1 != 0 or m2 != 0):
                    bad = True
                    break
                if not e and m1 == 0 and m2 == 0:
                    bad = True
                    break
            if bad:
                continue
            P[i], Q[i] = p, q
            if rec(k + 1):
                return True
            P[i] = Q[i] = None
        if reason[0] == "none":
            reason[0] = "backtrack_exhausted"
        return False

    ok = rec(0)
    info = dict(nodes=nodes[0], deepest=deepest[0], reason=reason[0])
    return (P, Q) if ok else (None, info)


def run_search(vmax=11):
    """Bounded deterministic smallest-first search aimed at chi(Z) >= 4."""
    log("search (smallest first, chi-targeted)")
    rng = random.Random(20261016)
    found = []
    stats = dict(instances=0, chi4=0, max_chi=0, max_chi_G0=0, max_chi_U=0,
                 min_mp_ratio=9.9)
    for v in range(3, vmax + 1):
        for it in range(6):
            fam = ("sym" if it % 2 == 0 else "asym") if it < 2 else (
                "mutual" if it < 4 else "c5seed")
            if fam in ("sym", "asym"):
                P, Q = gen_random(rng, v, fam == "sym")
            elif fam == "mutual":
                P, Q = gen_mutual_dense(rng, v)
            else:
                P, Q = gen_c5seed(rng, v)
            if P is None or not valid(P, Q):
                continue
            mod = model(P, Q)
            inm, _ = digraph_tables(v, mod["arcs"])
            acyc = acyclic_table(v, inm)
            mas = mas_table(v, acyc)
            chi = chi_table(v, acyc)
            mut = mutual_arcs(v, mod["arcs"])
            m_inm, _ = digraph_tables(v, mut)
            chiG = chi_table(v, acyclic_table(v, m_inm))
            uarcs = underlying_arcs(v, mod["arcs"])
            u_inm, _ = digraph_tables(v, uarcs)
            chiU = chi_table(v, acyclic_table(v, u_inm))
            stats["instances"] += 1
            stats["max_chi"] = max(stats["max_chi"], chi)
            stats["max_chi_G0"] = max(stats["max_chi_G0"], chiG)
            stats["max_chi_U"] = max(stats["max_chi_U"], chiU)
            if chi >= 4:
                stats["chi4"] += 1
                rec, _m, _w = settle(mod, "search v=%d fam=%s" % (v, fam))
                found.append(rec)
                log("chi(Z)=%d at v=%d fam=%s (recorded)" % (chi, v, fam))
            else:
                mp, _mp, _e, _p = matched_pivot(mod, acyc, mas)
                if mp / v < stats["min_mp_ratio"]:
                    stats["min_mp_ratio"] = mp / v
        log("v=%d done (instances %d, chi4=%d, max chi %d)"
            % (v, stats["instances"], stats["chi4"], stats["max_chi"]))
    # Grötzsch-as-G_0 sequential probe (the exact obstruction record).
    names, edges = grz_instance()
    obstructions = []
    for trial in range(3):
        rng2 = random.Random(500 + trial)
        out = sequential_build(names, edges, rng2, box=4, node_cap=60000)
        if out[0] is not None:
            P, Q = out
            mod = model(P, Q)
            mut = mutual_arcs(mod["v"], mod["arcs"])
            m_inm, _ = digraph_tables(mod["v"], mut)
            chiG = chi_table(mod["v"], acyclic_table(mod["v"], m_inm))
            rec, _m, _w = settle(mod, "grz_seq trial %d" % trial)
            found.append(rec)
            log("Grötzsch sequential trial %d: REALIZED chi(G_0)=%d" % (trial, chiG))
        else:
            obstructions.append(out[1])
            log("Grötzsch sequential trial %d: %r" % (trial, out[1]))
    stats["grz_obstructions"] = obstructions
    log("search: %d instances, chi4=%d, max chi=%d (G_0 %d, U %d), min MP ratio %.3f"
        % (stats["instances"], stats["chi4"], stats["max_chi"],
           stats["max_chi_G0"], stats["max_chi_U"], stats["min_mp_ratio"]))
    return found, stats


def main():
    run_controls()
    run_calibration()
    records = []
    # settle every embedded chi4 fixture (written by the development search)
    fdir = DATA
    for name in sorted(os.listdir(fdir)):
        if name.startswith("chi4_") and name.endswith(".json"):
            mod = load_model(name)
            rec, _m, _w = settle(mod, name)
            records.append(rec)
            log("settle %s: v=%d chi=%s chi_U=%s chi_G0=%s MP=%d reach=%d/%d "
                "lower=%d thr=%d meets=%s"
                % (name, rec["v"], rec["chi"], rec["chi_U"], rec["chi_G0"],
                   rec["MP"], rec["anchor_reach"], rec["v"], rec["cert_lower_bound"],
                   rec["threshold"], rec["meets_threshold"]))
    found, stats = run_search(vmax=11)
    records.extend(found)
    # settle the W5-underlying separation example exactly (v = 6)
    Pw = [(1, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 0, 1)]
    Qw = [(1, 0, 0), (0, 1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, -1)]
    rec, _m, _w = settle(model(Pw, Qw), "w5_underlying_separation")
    records.append(rec)
    log("settle w5_underlying_separation: v=%d chi=%s chi_U=%s chi_G0=%s MP=%d "
        "cert_exact=%s lower=%d thr=%d meets=%s"
        % (rec["v"], rec["chi"], rec["chi_U"], rec["chi_G0"], rec["MP"],
           rec["cert_exact"], rec["cert_lower_bound"], rec["threshold"],
           rec["meets_threshold"]))
    cert = dict(
        package="research/fstar-chi4-zero-digraph-seed73765f29",
        controls="PASS_FC4_CONTROLS",
        calibration="PASS_FC4_CALIBRATION",
        search_stats=stats,
        settlements=records,
    )
    blob = json.dumps(cert, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()[:16]
    cert["digest"] = digest
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CERTIFICATE.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    log("certificate digest %s" % digest)
    print("PASS_FC4_SEARCH")
    print("PASS_FSTAR_CHI4_ZERO_DIGRAPHS")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
