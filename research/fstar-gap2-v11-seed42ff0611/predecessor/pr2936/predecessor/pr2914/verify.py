#!/usr/bin/env python3
"""KB5g: the family gap of the F-star residue - sub-instance census of the
canonical fixtures, the sub-anchor-box decomposition of the attaining
certificates, and the smallest-first falsifier criterion (no kappa).

Object: exact 3-total rational decoders M = sum_j p_j q_j^T (v lines, nonzero
diagonal). Quantities per instance: zero digraph Z, Lemma SG anchor reach
|S_gamma|, tie numbers tau(t), matched-pivot value MP (Lemma MP), the named
family value (PR 2901's convention: max(MP, |S_gamma|, CL3 mixing)), the
sub-anchor-box value (NEW: a(t) subset of a0(t), b(t) subset of b0(t),
K_tt = 1), exact cert(M) by exhaustive a-enumeration with exact b-completion
(small v), engine witnesses with independent replay, and the bounded
admissible-B chain scan as falsifier criterion.

Engine lineage: model, subset-DP acyclic/MAS tables, anchor/tie data,
matched pivots, exact-completion DP, witness replay and the chain machinery
are adapted from Aaron Wang's PR 2717 / PR 2747 / PR 2869 / PR 2901 engine
(see README credit); the sub-anchor-box machinery, the sub-instance census
and the decomposition are new here. F-star and the chain cost >= cert(M) are
from research/root-unit-decoder-lemmas (PR 1590, DreamingOfClouds), cited,
not restated.

Deterministic, stdlib only, exact integer/F2 arithmetic. Run:
python3 -B verify.py
"""
import hashlib
import itertools
import json
import os
import random
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def log(msg):
    print("[%6.1fs] %s" % (time.time() - T0, msg), flush=True)


# ---------------------------------------------------------------- model
# (adapted from the PR 2717/2901 engine lineage, Aaron Wang)

def load_decoder(path):
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    P = [tuple(int(x) for x in line[0]) for line in raw]
    Q = [tuple(int(x) for x in line[1]) for line in raw]
    return P, Q


def model(P, Q):
    v = len(P)
    for t in range(v):
        for x in list(P[t]) + list(Q[t]):
            assert isinstance(x, int), "entries must be exact integers"
    M = [[sum(P[t][j] * Q[s][j] for j in range(3)) for s in range(v)] for t in range(v)]
    pi = [sum((1 << j) for j in range(3) if P[t][j] != 0) for t in range(v)]
    sg = [sum((1 << j) for j in range(3) if Q[t][j] != 0) for t in range(v)]
    D = [pi[t] & sg[t] for t in range(v)]
    assert all(M[t][t] != 0 for t in range(v)), "diagonal must be nonzero"
    assert all(D[t] != 0 for t in range(v)), "D(t) must be nonempty"
    arcs = [(t, s) for t in range(v) for s in range(v) if t != s and M[t][s] == 0]
    return dict(v=v, P=P, Q=Q, M=M, pi=pi, sg=sg, D=D, arcs=arcs)


def load_model(name):
    return model(*load_decoder(os.path.join(DATA, name)))


def restrict(mod, S):
    """Sub-decoder M[S,S]: restriction of an exact decoder is exact (rank <= 3
    and nonzero diagonal are preserved). S is a sorted list of line indices."""
    P = [mod["P"][t] for t in S]
    Q = [mod["Q"][t] for t in S]
    return model(P, Q)


def digraph_tables(v, arcs):
    inm = [0] * v
    outm = [0] * v
    for (t, s) in arcs:
        inm[s] |= 1 << t
        outm[t] |= 1 << s
    return inm, outm


def acyclic_table(v, inm):
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


def mas_argmax(mas, acyc, S, memo):
    if S == 0:
        return 0
    if S in memo:
        return memo[S]
    if acyc[S]:
        memo[S] = S
        return S
    T = S
    while T:
        b = T & -T
        if mas[S ^ b] == mas[S]:
            val = mas_argmax(mas, acyc, S ^ b, memo)
            memo[S] = val
            return val
        T ^= b
    raise AssertionError("mas_argmax: no witness")


# -------------------------------------------- Lemma SG anchor + Lemma CT data

def v2_int(n):
    if n == 0:
        raise ValueError("v2(0)")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def anchor_data(mod):
    """Canonical reduced normalization (alpha_j = -m_j): a0_j(t) =
    [v2(p_j(t)) = m_j], b0_j(t) = [v2(q_j(t)) = gamma - m_j], with the scope
    identity K0_ts = 2^{-gamma} M_ts mod 2 (Lemma SG of PR 2869)."""
    P, Q, M = mod["P"], mod["Q"], mod["M"]
    v = mod["v"]
    SENTINEL = 10 ** 9
    m, n, c = [], [], []
    for j in range(3):
        mp = [v2_int(P[t][j]) for t in range(v) if P[t][j] != 0]
        mq = [v2_int(Q[t][j]) for t in range(v) if Q[t][j] != 0]
        if mp and mq:
            m.append(min(mp))
            n.append(min(mq))
        else:
            m.append(SENTINEL)
            n.append(SENTINEL)
        c.append(m[-1] + n[-1])
    assert min(c) < SENTINEL, "at least one total must be nondegenerate"
    gamma = min(c)
    diag = [v2_int(M[t][t]) for t in range(v)]
    reach = [t for t in range(v) if diag[t] == gamma]
    cancel = [t for t in range(v) if diag[t] > gamma]
    tau = []
    for t in range(v):
        cnt = 0
        for j in range(3):
            if (P[t][j] != 0 and Q[t][j] != 0
                    and v2_int(P[t][j]) + v2_int(Q[t][j]) == gamma):
                cnt += 1
        tau.append(cnt)
    a0 = [sum((1 << j) for j in range(3)
              if P[t][j] != 0 and v2_int(P[t][j]) == m[j])
          for t in range(v)]
    b0 = [sum((1 << j) for j in range(3)
              if Q[t][j] != 0 and v2_int(Q[t][j]) == gamma - m[j])
          for t in range(v)]
    return dict(gamma=gamma, m=m, n=n, c=c, diag=diag, reach=reach,
                cancel=cancel, tau=tau, a0=a0, b0=b0)


def dot1(x, y):
    return bin(x & y).count("1") & 1


def scope_identity(mod, ad):
    v, M = mod["v"], mod["M"]
    for t in range(v):
        for s in range(v):
            want = 1 if (M[t][s] != 0 and v2_int(M[t][s]) == ad["gamma"]) else 0
            if dot1(ad["a0"][t], ad["b0"][s]) != want:
                return False
    return True


def tie_parity(mod, ad):
    v = mod["v"]
    for t in range(v):
        if (ad["tau"][t] % 2 == 1) != (ad["diag"][t] == ad["gamma"]):
            return False
        if (ad["tau"][t] % 2 == 0) != (ad["diag"][t] > ad["gamma"]):
            return False
        if ad["tau"][t] > mod["D"][t].bit_count():
            return False
    return True


# --------------------------------------------------------- Lemma MP pivots

def matched_pivot(mod, mas, exhaustive_cap=200000, seed=20261016):
    v = mod["v"]
    allowed = [[1 << j for j in range(3) if mod["D"][t] & (1 << j)]
               for t in range(v)]
    prod = 1
    for a in allowed:
        prod *= len(a)
    best, best_map = -1, None
    exhaustive = prod <= exhaustive_cap
    if exhaustive:
        for combo in itertools.product(*allowed):
            classes = [0, 0, 0]
            for t in range(v):
                i = combo[t].bit_length() - 1
                classes[i] |= 1 << t
            val = mas[classes[0]] + mas[classes[1]] + mas[classes[2]]
            if val > best:
                best, best_map = val, combo
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
                best, best_map = val, combo
    return best, best_map, exhaustive, prod


# --------------------------------------------------------- cert engine
# (PR 2717's exact-completion engine design (Aaron Wang), adapted: for fixed
# a-labels the completion over b-labels, order and kept set is exact by
# subset DP.)

def span_add(basis, x):
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


def completion(mod, a):
    """Exact completion over b-labels/order/kept set for fixed a-labels.
    Returns (best size, witness dict or None)."""
    v = mod["v"]
    sg = mod["sg"]
    inm, _ = digraph_tables(v, mod["arcs"])
    blockers = [inm[t] for t in range(v)]
    bex = {}
    basis_tab = [dict() for _ in range(v)]
    b_all = [[b for b in range(8) if (b & ~sg[t]) == 0] for t in range(v)]

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
    return best.bit_count(), dict(a=list(a), b=bvec, order=list(kept),
                                 kept=list(kept))


def completion_box(mod, ad, a):
    """Completion with every b-label restricted to b(t) subset of b0(t).
    Used for the sub-anchor-box value (new here)."""
    v = mod["v"]
    b0 = ad["b0"]
    inm, _ = digraph_tables(v, mod["arcs"])
    blockers = [inm[t] for t in range(v)]
    bex = {}
    basis_tab = [dict() for _ in range(v)]
    b_all = [[b for b in range(8) if (b & ~b0[t]) == 0] for t in range(v)]

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
    return best.bit_count(), dict(a=list(a), b=bvec, order=list(kept),
                                 kept=list(kept))


def replay_witness(mod, wit):
    """Independent replay: supports, K_tt = 1 on kept, order constraints."""
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


def in_box(mod, ad, wit):
    """Every kept label pair is a sub-anchor pair: a(t) subset of a0(t) and
    b(t) subset of b0(t). Returns (all_in_box, escape_lines)."""
    esc = []
    for t in wit["kept"]:
        if (wit["a"][t] & ~ad["a0"][t]) or (wit["b"][t] & ~ad["b0"][t]):
            esc.append(t)
    return (not esc), esc


def cert_exact(mod, max_v=6):
    """Exact cert by exhaustive a-enumeration (small v only)."""
    v = mod["v"]
    if v > max_v:
        return None, None
    choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0]
               for t in range(v)]
    best, best_wit = -1, None
    for combo in itertools.product(*choices):
        val, wit = completion(mod, list(combo))
        if val > best:
            best, best_wit = val, wit
    return best, best_wit


def box_exact(mod, ad, max_v=6):
    """Exact sub-anchor-box value: exhaustive a-subsets of a0 with the
    b-side completed inside b0 (small v only)."""
    v = mod["v"]
    if v > max_v:
        return None, None
    choices = []
    for t in range(v):
        subs = [m for m in range(8) if (m & ~ad["a0"][t]) == 0]
        subs = [m for m in subs
                if any(dot1(m, b) == 1 and (b & ~ad["b0"][t]) == 0
                       for b in range(8))]
        choices.append(subs)
    best, best_wit = -1, None
    for combo in itertools.product(*choices):
        val, wit = completion_box(mod, ad, list(combo))
        if val > best:
            best, best_wit = val, wit
    return best, best_wit


def cert_hillclimb(mod, iters=400, seed=1234, box=False, ad=None):
    """Bounded deterministic hill-climb over a-labels with exact completion.
    box=True restricts both sides to the sub-anchor box."""
    v = mod["v"]
    rng = random.Random(seed)
    if box:
        choices = [[m for m in range(8) if (m & ~ad["a0"][t]) == 0]
                   for t in range(v)]
        comp = lambda a: completion_box(mod, ad, a)  # noqa: E731
    else:
        choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0]
                   for t in range(v)]
        comp = lambda a: completion(mod, a)  # noqa: E731
    a = [c[rng.randrange(len(c))] for c in choices]
    best, best_wit = comp(a)
    cur = list(a)
    for _ in range(iters):
        t = rng.randrange(v)
        old = cur[t]
        new = choices[t][rng.randrange(len(choices[t]))]
        if new == old:
            continue
        cur[t] = new
        val, wit = comp(cur)
        if val >= best:
            best, best_wit = val, wit
        else:
            cur[t] = old
    return best, best_wit


# ----------------------------------------------- chain machinery (falsifier)
# (PR 2717/2901 lineage)

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
    """Bounded deterministic scan for an admissible B with chain cost below
    the threshold (the falsifier criterion of PR 2901)."""
    v = mod["v"]
    rng = random.Random(seed)
    best, best_cost, hit = None, None, False
    for _ in range(tries):
        B = [[0] * v for _ in range(v)]
        for t in range(v):
            B[t][t] = 1
            for s in range(v):
                if t != s and mod["M"][t][s] == 0 and rng.randrange(2):
                    B[t][s] = 1
        if not admissible(mod, B):
            continue
        cc = chain_cost(mod, B)
        if best_cost is None or cc < best_cost:
            best, best_cost = B, cc
            if cc < threshold:
                hit = True
                break
    return best_cost, best, hit


# ------------------------------- named label forms and the ladder (NEW here)
#
# The named families of PR 2901 (Lemma SG anchor, Lemma MX one-sided
# repairs, Lemma MP matched pivots, Lemma CL3 insertion mixings) all build
# their certificates from per-line labels of three forms: (a0(t), b0(t)),
# (a*(t), b0(t)) with a* . b0(t) = 1, or (e_c, e_c) with c in D(t).  Call
# their union the Form-R space.  For ANY fixed label assignment (a, b) its
# exact certificate value is MAS(D_K[good]) where D_K is the conflict
# digraph and good = {t : K_tt = 1}; so the Form-R maximum is a rigorous
# upper bound on the PR 2901 named value and a lower bound on cert(M).
#
# Ladder per instance:  MP <= named_lo <= named <= form_r <= box <= cert
#   named_lo = max(MP, |S_gamma|)         (PR 2901's cheap rung)
#   named    = PR 2901's family value     (<= form_r, proved above)
#   form_r   = max over Form-R labels     (NEW upper bound on named)
#   box      = max over a(t) subset of a0(t), b(t) subset of b0(t) (NEW)
#   cert     = max over all labels.

def ab_value(mod, a, b):
    """Exact certificate value of a fixed label assignment: the largest kept
    set with K_tt = 1 and every conflict pointing backward in some order."""
    v, M = mod["v"], mod["M"]
    good = 0
    inm = [0] * v
    for t in range(v):
        if dot1(a[t], b[t]) == 1:
            good |= 1 << t
    for t in range(v):
        for s in range(v):
            if t != s and M[t][s] == 0 and dot1(a[t], b[s]) == 1:
                inm[s] |= 1 << t
    n = 1 << v
    acyc = [False] * n
    acyc[0] = True
    best = 0
    for S in range(1, n):
        if S & ~good:
            continue
        ok = False
        T = S
        while T:
            x = T & -T
            t = x.bit_length() - 1
            if (inm[t] & S) == 0 and acyc[S ^ x]:
                ok = True
                break
            T ^= x
        acyc[S] = ok
        if ok and S.bit_count() > best:
            best = S.bit_count()
    return best


def form_r_options(mod, ad, t):
    """The named-form label pairs on line t (deduplicated): anchor (a0, b0),
    one-sided repairs (a*, b0) with a* . b0(t) = 1, matched pivots (e_c, e_c)."""
    opts = {(ad["a0"][t], ad["b0"][t])}
    for a in range(8):
        if (a & ~mod["pi"][t]) == 0 and dot1(a, ad["b0"][t]) == 1:
            opts.add((a, ad["b0"][t]))
    for j in range(3):
        if mod["D"][t] & (1 << j):
            opts.add((1 << j, 1 << j))
    return sorted(opts)


def form_r_max(mod, ad, exhaustive_cap=300000, iters=250, seed=4242):
    """Max of ab_value over the Form-R label space. Exact when the product of
    per-line option counts is within the cap; deterministic hill-climb
    otherwise (lower bound, flagged)."""
    v = mod["v"]
    opts = [form_r_options(mod, ad, t) for t in range(v)]
    prod = 1
    for o in opts:
        prod *= len(o)
    best, best_wit = -1, None

    def take(combo):
        nonlocal best, best_wit
        a = [c[0] for c in combo]
        b = [c[1] for c in combo]
        val = ab_value(mod, a, b)
        if val > best:
            best = val
            best_wit = dict(a=list(a), b=b, order=list(range(v)), kept=[])
        return val

    exhaustive = prod <= exhaustive_cap
    if exhaustive:
        for combo in itertools.product(*opts):
            take(combo)
    else:
        rng = random.Random(seed)
        cur = [o[rng.randrange(len(o))] for o in opts]
        take(cur)
        for _ in range(iters):
            t = rng.randrange(v)
            old = cur[t]
            new = opts[t][rng.randrange(len(opts[t]))]
            if new == old:
                continue
            cur[t] = new
            val = take(cur)
            if val < best:
                cur[t] = old
    # materialize a replayable witness for the best assignment: kept set is
    # the largest acyclic conflict subset; order is a backward topological
    # order of the conflicts (sink-first).
    a = best_wit["a"]
    b = best_wit["b"]
    v_, M = mod["v"], mod["M"]
    good = [t for t in range(v_) if dot1(a[t], b[t]) == 1]
    inm = [0] * v_
    for t in good:
        for s in good:
            if t != s and M[t][s] == 0 and dot1(a[t], b[s]) == 1:
                inm[s] |= 1 << t
    S = 0
    for t in good:
        S |= 1 << t
    acyc = [False] * (1 << v_)
    acyc[0] = True
    for X in range(1, 1 << v_):
        if X & ~S:
            continue
        ok = False
        Tm = X
        while Tm:
            x = Tm & -Tm
            t = x.bit_length() - 1
            if (inm[t] & X) == 0 and acyc[X ^ x]:
                ok = True
                break
            Tm ^= x
        acyc[X] = ok
    bestS, bestN = 0, -1
    for X in range(1, 1 << v_):
        if (X & ~S) == 0 and acyc[X] and X.bit_count() > bestN:
            bestS, bestN = X, X.bit_count()
    order = []
    rem = bestS
    while rem:
        sinks = [t for t in range(v_) if (rem >> t) & 1 and (inm[t] & rem) == 0]
        t = min(sinks)
        order.append(t)
        rem ^= 1 << t
    order.reverse()
    best_wit = dict(a=a, b=b, order=order, kept=list(order))
    return best, best_wit, exhaustive, prod


def box_witness_from(mod, ad, a, b, order):
    return dict(a=list(a), b=list(b), order=list(order), kept=list(order))


def diff_labels(mod, ad, wit):
    """Classify each kept line's label pair against the named forms and the
    sub-anchor box (PR 2901 open question 2, first step)."""
    rows = []
    for t in wit["kept"]:
        a, b = wit["a"][t], wit["b"][t]
        anchor = (a, b) == (ad["a0"][t], ad["b0"][t])
        repair = (b == ad["b0"][t] and dot1(a, b) == 1
                  and (a & ~mod["pi"][t]) == 0)
        pivot = a == b and a in (1, 2, 4) and (mod["D"][t] & a) != 0
        inbox = (a & ~ad["a0"][t]) == 0 and (b & ~ad["b0"][t]) == 0
        if anchor:
            kind = "ANCHOR"
        elif repair:
            kind = "REPAIR"
        elif pivot:
            kind = "PIVOT"
        elif inbox:
            kind = "BOX-INTERIOR"
        else:
            kind = "BOX-ESCAPE"
        rows.append(dict(t=t, a=a, b=b, a0=ad["a0"][t], b0=ad["b0"][t],
                         tau=ad["tau"][t], D=mod["D"][t], kind=kind))
    return rows


def named_exact_small(mod, ad, mas, acyc, cap=400000, scan_iters=None):
    """Exact PR 2901 named value on small instances: max over the union of
    the named families' constructions (Lemma SG anchor |S_gamma|, Lemma MP
    matched pivots, Lemma MX one-sided-repair constructions with their two
    exact hypothesis sets, Lemma CL3 insertion mixings - whose value for its
    label forms is exactly ab_value). Returns (named, detail). Large
    construction spaces fall back to a deterministic bounded scan (the
    detail flags exactness)."""
    v = mod["v"]
    if scan_iters is None:
        scan_iters = 20000 if v <= 13 else 300
    mp, _m, _e, _p = matched_pivot(mod, mas)
    best = max(mp, len(ad["reach"]))
    detail = dict(MP=mp, reach=len(ad["reach"]), mx=None, cl3=None,
                  exhaustive=True, product=0)
    # per-line options for the MX construction space: ('A'), ('U', a*),
    # ('T', c-bit)
    opts = []
    for t in range(v):
        o = [("A", 0)]
        for a in range(8):
            if (a & ~mod["pi"][t]) == 0 and dot1(a, ad["b0"][t]) == 1 \
                    and a != ad["a0"][t]:
                o.append(("U", a))
        for j in range(3):
            if mod["D"][t] & (1 << j):
                o.append(("T", 1 << j))
        opts.append(o)
    prod = 1
    for o in opts:
        prod *= len(o)
    detail["product"] = prod
    M = mod["M"]

    def mx_eval(combo):
        A = [t for t in range(v) if combo[t][0] == "A"]
        U = [t for t in range(v) if combo[t][0] == "U"]
        T = [t for t in range(v) if combo[t][0] == "T"]
        for t in A:
            if not (mod["M"][t][t] != 0 and ad["tau"][t] % 2 == 1):
                return None  # Lemma MX: every t in A has K0_tt = 1
        classes = [0, 0, 0]
        cval = [0] * v
        for t in T:
            c = combo[t][1]
            cval[t] = c
            classes[c.bit_length() - 1] |= 1 << t
        val = len(A) + len(U) + mas[classes[0]] + mas[classes[1]] \
            + mas[classes[2]]
        # (A-first) (i): for t in U: a* . b0(s) = 0 for s in A+U with
        # M_ts = 0, and no pivot bit c(s) set in a* for s in T with M_ts = 0;
        # (ii): no c(s) set in a0(t) for t in A, s in T with M_ts = 0.
        ok_a = True
        for t in U:
            a_star = combo[t][1]
            for s in A + U:
                if M[t][s] == 0 and dot1(a_star, ad["b0"][s]) != 0:
                    ok_a = False
            for s in T:
                if M[t][s] == 0 and (a_star & cval[s]) != 0:
                    ok_a = False
        for t in A:
            for s in T:
                if M[t][s] == 0 and (ad["a0"][t] & cval[s]) != 0:
                    ok_a = False
        # (T-first) (i')/(ii')
        ok_t = True
        for t in U:
            a_star = combo[t][1]
            for s in A + U:
                if M[t][s] == 0 and dot1(a_star, ad["b0"][s]) != 0:
                    ok_t = False
        for t in T:
            for s in A + U:
                if M[s][t] == 0 and (cval[t] & ad["b0"][s]) != 0:
                    ok_t = False
        return val if (ok_a or ok_t) else None

    if prod <= cap:
        mx_best = 0
        for combo in itertools.product(*opts):
            val = mx_eval(combo)
            if val is not None and val > mx_best:
                mx_best = val
        detail["mx"] = mx_best
        best = max(best, mx_best)
    else:
        detail["exhaustive"] = False
        rng = random.Random(31337)
        mx_best = 0
        best_cur = None
        # structured seeds (pure matched-pivot maps always satisfy both MX
        # forms; the greedy walk below gets stuck in hypothesis-failing
        # mixed assignments without them)
        seeds = [[("A", 0)] * v]
        for j in range(3):
            seeds.append([("T", (1 << j)) if (mod["D"][t] & (1 << j))
                          else ("T", 1 << (mod["D"][t].bit_length() - 1))
                          for t in range(v)])
        mp0, mpmap0, _e0, _p0 = matched_pivot(mod, mas)
        if mpmap0 is not None:
            seeds.append([("T", mpmap0[t]) for t in range(v)])
        for s0 in seeds:
            val = mx_eval(s0)
            if val is not None and val > mx_best:
                mx_best, best_cur = val, list(s0)
        cur = list(best_cur) if best_cur is not None \
            else [o[rng.randrange(len(o))] for o in opts]
        since_restart = 0
        for _ in range(scan_iters):
            if since_restart >= 4 * v:
                since_restart = 0
                if best_cur is not None and rng.randrange(2):
                    cur = list(best_cur)
                else:
                    cur = [o[rng.randrange(len(o))] for o in opts]
            since_restart += 1
            t = rng.randrange(v)
            old = cur[t]
            cur[t] = opts[t][rng.randrange(len(opts[t]))]
            val = mx_eval(cur)
            if val is None or val < mx_best:
                cur[t] = old
            elif val > mx_best:
                mx_best = val
                best_cur = list(cur)
        detail["mx"] = mx_best
        best = max(best, mx_best)
    # CL3 value for its label forms (anchor (a0,b0) on A, matched pivots):
    # exact ab_value over the combined forms, small product only.
    cl3_opts = [[(ad["a0"][t], ad["b0"][t], "A")] +
                [((1 << j), (1 << j), "T") for j in range(3)
                 if mod["D"][t] & (1 << j)]
                for t in range(v)]
    cl3_prod = 1
    for o in cl3_opts:
        cl3_prod *= len(o)
    cl3_best = 0
    if cl3_prod <= cap:
        for combo in itertools.product(*cl3_opts):
            a = [c[0] for c in combo]
            b = [c[1] for c in combo]
            val = ab_value(mod, a, b)
            if val > cl3_best:
                cl3_best = val
    else:
        rng = random.Random(4242)
        cur = [o[rng.randrange(len(o))] for o in cl3_opts]
        for _ in range(scan_iters):
            t = rng.randrange(v)
            old = cur[t]
            cur[t] = cl3_opts[t][rng.randrange(len(cl3_opts[t]))]
            a = [c[0] for c in cur]
            b = [c[1] for c in cur]
            val = ab_value(mod, a, b)
            if val < cl3_best:
                cur[t] = old
            elif val > cl3_best:
                cl3_best = val
        detail["exhaustive"] = False
    detail["cl3"] = cl3_best
    best = max(best, cl3_best)
    return best, detail


def settle_ladder(mod, ad, mas, acyc, exact=False, engine_iters=150,
                  provided_cert_wit=None, label=""):
    """One ladder record: all rungs, the gap decomposition, and the armed
    falsifier criterion (exact cert below threshold where exhaustive, or an
    explicit admissible B with chain cost below threshold). exact=True runs
    the exhaustive Form-R / box / cert rungs (small v); otherwise the engine
    rungs are deterministic hill-climbs (lower bounds) and provided_cert_wit
    (e.g. a stored witness) is used as the cert rung on large instances."""
    v = mod["v"]
    thr = (2 * v) // 3
    mp, mpmap, mp_exh, mp_prod = matched_pivot(mod, mas)
    named_lo = max(mp, len(ad["reach"]))
    fr_val, fr_wit, fr_exh, fr_prod = form_r_max(
        mod, ad, exhaustive_cap=(300000 if exact else 0))
    assert fr_wit is not None and replay_witness(mod, fr_wit), "form-R witness"
    if exact:
        bx_val, bx_wit = box_exact(mod, ad, max_v=6)
        ce_val, ce_wit = cert_exact(mod, max_v=6)
        bx_exact, ce_exact = True, True
    else:
        if v > 13:
            bx_val, bx_wit = None, None
        else:
            bx_val, bx_wit = cert_hillclimb(mod, iters=engine_iters, seed=2024,
                                            box=True, ad=ad)
        if provided_cert_wit is not None:
            ce_wit = provided_cert_wit
            ce_val = len(ce_wit["kept"])
        elif v > 13:
            ce_val, ce_wit = 0, None
        else:
            ce_val, ce_wit = cert_hillclimb(mod, iters=engine_iters, seed=2025)
        bx_exact, ce_exact = False, False
    if bx_wit is not None:
        assert replay_witness(mod, bx_wit), "box witness"
    if ce_wit is not None:
        assert replay_witness(mod, ce_wit), "engine witness"
    named_val, named_detail = None, None
    if exact:
        named_val, named_detail = named_exact_small(mod, ad, mas, acyc)
    rec = dict(label=label, v=v, threshold=thr, k_cancel=len(ad["cancel"]),
               reach=len(ad["reach"]), MP=mp, MP_exhaustive=mp_exh,
               MP_product=mp_prod, named_lo=named_lo,
               named=named_val, named_detail=named_detail,
               form_r=fr_val, form_r_exhaustive=fr_exh, form_r_product=fr_prod,
               box=bx_val, box_exact=bx_exact,
               cert=ce_val, cert_exact=ce_exact,
               gap_forms=(ce_val - fr_val), gap_pr=(ce_val - named_lo),
               gap_named=((ce_val - named_val) if named_val is not None
                          else None),
               named_ge_threshold=(named_lo >= thr),
               forms_ge_threshold=(fr_val >= thr),
               cert_ge_threshold=(ce_val >= thr))
    if ce_wit is not None:
        inb, esc = in_box(mod, ad, ce_wit)
        rec["cert_witness_in_box"] = inb
        rec["cert_witness_box_escape"] = esc
        rec["cert_witness_diff"] = diff_labels(mod, ad, ce_wit)
    rec["falsifier"] = None
    if rec["cert_exact"]:
        if ce_val < thr:
            rec["falsifier"] = "exact cert %d < threshold %d" % (ce_val, thr)
    elif named_lo < thr or ce_val < thr:
        cc, _B, hit = chain_scan(mod, thr)
        rec["chain_scan_best"] = cc
        if hit:
            rec["falsifier"] = ("admissible B with chain cost %d < "
                                "threshold %d" % (cc, thr))
    return rec


# --------------------------------------------------------------- controls

def brute_force_cert(mod):
    """Cert from the definition: all labellings, all orders (tiny v only)."""
    v, M = mod["v"], mod["M"]
    choices = [[m for m in range(8) if (m & ~mod["pi"][t]) == 0]
               for t in range(v)]
    bchoices = [[m for m in range(8) if (m & ~mod["sg"][t]) == 0]
                for t in range(v)]
    best = 0
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


def sparse_v3(seed):
    """A tiny v = 3 decoder with sparse supports (for the brute-force
    control). Deterministic small-integer factorization."""
    rng = random.Random(seed)
    while True:
        P = [tuple(rng.choice([0, 0, 0, 1, -1, 2]) for _ in range(3))
             for _ in range(3)]
        Q = [tuple(rng.choice([0, 0, 0, 1, -1, 2]) for _ in range(3))
             for _ in range(3)]
        try:
            mod = model(P, Q)
        except AssertionError:
            continue
        if max(mod["pi"][t].bit_count() for t in range(3)) <= 2:
            return mod


def run_controls():
    # 1. exact cert vs brute force from the definition (3 sparse v = 3 cases)
    agree = 0
    for seed in (11, 22, 33):
        mod = sparse_v3(seed)
        bf = brute_force_cert(mod)
        ex, wit = cert_exact(mod, max_v=6)
        assert ex == bf and wit is not None and replay_witness(mod, wit), \
            "cert_exact must agree with brute force at v = 3"
        agree += 1
    # 2. corrupted witnesses must fail the independent replay
    mod = sparse_v3(44)
    ex, wit = cert_exact(mod, max_v=6)
    bad = dict(a=list(wit["a"]), b=list(wit["b"]), order=list(wit["order"]),
               kept=list(wit["kept"]))
    bad["a"][bad["kept"][0]] = 0  # kills K_tt on a kept line
    assert not replay_witness(mod, bad), "corrupted label must be rejected"
    bad2 = dict(a=list(wit["a"]), b=list(wit["b"]), order=list(wit["order"]),
                kept=list(wit["kept"]))
    bad2["kept"] = bad2["kept"][1:]  # kept/order mismatch
    assert not replay_witness(mod, bad2), "corrupted kept set must be rejected"
    # 3. ab_value is a sound rung: for random fixed labels it never exceeds
    #    the exact completion value for the same a-side
    rng = random.Random(7)
    sound = 0
    for seed in (55, 66):
        m2 = sparse_v3(seed)
        ad2 = anchor_data(m2)
        tries = 0
        while sound < 10 and tries < 500:
            tries += 1
            a = [rng.randrange(8) & m2["pi"][t] for t in range(m2["v"])]
            b = [rng.randrange(8) & m2["sg"][t] for t in range(m2["v"])]
            if any(dot1(a[t], b[t]) != 1 for t in range(m2["v"])):
                continue
            f_ab = ab_value(m2, a, b)
            f_a, _w = completion(m2, a)
            assert f_ab <= f_a, "ab_value must not exceed completion"
            sound += 1
    # 4. restriction exactness: M[S,S] rows, nonzero diagonal, and the
    #    per-instance Lemma CT / scope identities on a sub-decoder
    mod = load_model("tied_min.json")
    S = [0, 2, 5, 7]
    sub = restrict(mod, S)
    for i, t in enumerate(S):
        for j, s in enumerate(S):
            assert sub["M"][i][j] == mod["M"][t][s], "restriction must be exact"
    ads = anchor_data(sub)
    assert tie_parity(sub, ads) and scope_identity(sub, ads), \
        "sub-decoder must satisfy the CT/scope identities"
    # 5. diagonal decoder sanity: cert = v and MP = v
    md = model([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)],
               [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1)])
    inm, _ = digraph_tables(md["v"], md["arcs"])
    mas = mas_table(md["v"], acyclic_table(md["v"], inm))
    mp, _mpmap, _e, _p = matched_pivot(md, mas)
    ex, _w = cert_exact(md, max_v=6)
    assert mp == 4 and ex == 4, "diagonal-style decoder must give 4"
    print("PASS_FG_CONTROLS brute-force=%d/3 corrupted=2/2 ab-sound=%d "
          "restriction=1/1 diagonal=1/1" % (agree, sound))


# ------------------------------------------------------------- calibration

def run_calibration():
    recs = {}
    for name, want in (("tied_min.json", dict(mp=9, prod=4096, reach=[],
                                             wit=11, chain=None)),
                       ("cex_min_1.json", dict(mp=16, prod=6144,
                                               reach=[0, 4, 5, 6, 8, 11, 14, 15],
                                               wit=18, chain=22))):
        mod = load_model(name)
        ad = anchor_data(mod)
        assert tie_parity(mod, ad) and scope_identity(mod, ad), name
        inm, _ = digraph_tables(mod["v"], mod["arcs"])
        acyc = acyclic_table(mod["v"], inm)
        mas = mas_table(mod["v"], acyc)
        mp, mpmap, exh, prod = matched_pivot(mod, mas)
        assert exh and prod == want["prod"] and mp == want["mp"], \
            "%s MP must match the recorded anchors" % name
        assert sorted(ad["reach"]) == want["reach"], "%s reach" % name
        if name == "cex_min_1.json":
            with open(os.path.join(DATA, "cex_min_1.witness.json"), "r",
                      encoding="utf-8") as fh:
                sw = json.load(fh)
            wit = dict(a=sw["a"], b=sw["b"], order=sw["order"], kept=sw["kept"])
            assert replay_witness(mod, wit) and len(wit["kept"]) == 18, \
                "cex_min_1 stored witness must replay at 18"
            got = 18
            with open(os.path.join(DATA, "cex_min_1.B22.json"), "r",
                      encoding="utf-8") as fh:
                B = json.load(fh)
            if isinstance(B, dict):
                B = B.get("B", B.get("pairing"))
            assert admissible(mod, B), "stored pairing admissible"
            cc = chain_cost(mod, B)
            assert cc == want["chain"], "chain engine must reproduce 22"
        else:
            val, wit = cert_hillclimb(mod, iters=400, seed=1234)
            assert wit is not None and replay_witness(mod, wit), name
            got = val
            assert got == want["wit"], \
                "tied_min hill-climb must re-find 11 (got %d)" % got
        rows = diff_labels(mod, ad, wit)
        inb, esc = in_box(mod, ad, wit)
        kinds = {}
        for r in rows:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        recs[name] = dict(v=mod["v"], threshold=(2 * mod["v"]) // 3,
                          MP=mp, reach=len(ad["reach"]),
                          cancel=len(ad["cancel"]), witness=got,
                          in_box=inb, box_escape=esc, kinds=kinds,
                          diff=rows)
        log("%s: MP=%d reach=%d witness=%d in_box=%s kinds=%s"
            % (name, mp, len(ad["reach"]), got, inb, kinds))
    print("PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 "
          "chain=22 reach=0/12,8/19")
    return recs


# -------------------------------------------- fixture ladder + form-R probes

def run_fixture_ladder():
    """The ladder on both fixtures, plus the Form-R / box probes that answer
    PR 2901 open question 2 (what do the attaining certificates use?)."""
    out = {}
    for name in ("tied_min.json", "cex_min_1.json"):
        mod = load_model(name)
        ad = anchor_data(mod)
        inm, _ = digraph_tables(mod["v"], mod["arcs"])
        acyc = acyclic_table(mod["v"], inm)
        mas = mas_table(mod["v"], acyc)
        provided = None
        if name == "cex_min_1.json":
            with open(os.path.join(DATA, "cex_min_1.witness.json"), "r",
                      encoding="utf-8") as fh:
                sw = json.load(fh)
            provided = dict(a=sw["a"], b=sw["b"], order=sw["order"],
                            kept=sw["kept"])
        rec = settle_ladder(mod, ad, mas, acyc, exact=False,
                            engine_iters=(400 if name == "tied_min.json"
                                          else 0),
                            provided_cert_wit=provided, label=name)
        named_v, named_det = named_exact_small(
            mod, ad, mas, acyc,
            scan_iters=(20000 if name == "tied_min.json" else 300))
        rec["named_scan"] = named_v
        rec["named_scan_detail"] = named_det
        # probe: can the Form-R space alone reach the recorded witness value?
        fr_deep, fr_wit, fr_exh, fr_prod = form_r_max(
            mod, ad, exhaustive_cap=0,
            iters=(800 if name == "tied_min.json" else 300), seed=909)
        if fr_wit is not None and replay_witness(mod, fr_wit):
            rec["form_r_deep"] = fr_deep
            rec["form_r_deep_witness_in_box"] = in_box(mod, ad, fr_wit)[0]
            rec["form_r_deep_witness_diff"] = diff_labels(mod, ad, fr_wit)
        if name == "tied_min.json":
            bx_deep, bx_wit = cert_hillclimb(mod, iters=400, seed=910,
                                             box=True, ad=ad)
            if bx_wit is not None and replay_witness(mod, bx_wit):
                rec["box_deep"] = bx_deep
                rec["box_deep_witness_in_box"] = in_box(mod, ad, bx_wit)[0]
            ce_deep, ce_wit = cert_hillclimb(mod, iters=400, seed=911)
            if ce_wit is not None and replay_witness(mod, ce_wit):
                rec["cert_deep"] = ce_deep
                rec["cert_deep_witness_in_box"] = in_box(mod, ad, ce_wit)[0]
                rec["cert_deep_witness_diff"] = diff_labels(mod, ad, ce_wit)
        out[name] = rec
        log("fixture ladder %s: named_lo=%d form_r=%d box=%s cert=%d" %
            (name, rec["named_lo"], rec["form_r"], rec["box"], rec["cert"]))
    return out


# ------------------------------------------------------- sub-instance census

def subsets_smallest_first(v, size, cap, stride=1):
    """Deterministic enumeration of `size`-subsets of range(v), lexicographic,
    thinned by a fixed stride when the count exceeds cap (the thinning and
    the exact domain are recorded in CERTIFICATE.json)."""
    all_subs = list(itertools.combinations(range(v), size))
    if len(all_subs) <= cap:
        return all_subs, len(all_subs), False
    step = max(1, len(all_subs) // cap)
    picked = all_subs[::step][:cap]
    return picked, len(all_subs), True


def run_census():
    """Smallest-first sub-decoder census of both fixtures. Sub-decoders are
    exact 3-total decoders and inherit fixture-density zero digraphs (the
    exact recorded generator obstruction of PR 2901). Cheap rungs on every
    enumerated subset; the exact ladder (Form-R / box / cert exhaustive) on
    every flagged subset (gap risk or falsifier risk), smallest first."""
    plan = [
        ("tied_min.json", 3, 240), ("tied_min.json", 4, 240),
        ("tied_min.json", 5, 240), ("tied_min.json", 6, 60),
        ("cex_min_1.json", 3, 240), ("cex_min_1.json", 4, 240),
        ("cex_min_1.json", 5, 120), ("cex_min_1.json", 6, 50),
    ]
    deep_budget = {"n": 20, "v6": 1}
    records = []
    domain = []
    falsifier = None
    deep_done = 0
    for name, size, cap in plan:
        mod = load_model(name)
        subs, total, thinned = subsets_smallest_first(mod["v"], size, cap)
        domain.append(dict(fixture=name, size=size, enumerated=len(subs),
                           total=total, thinned=thinned))
        flagged_here = 0
        for S in subs:
            sub = restrict(mod, list(S))
            ad = anchor_data(sub)
            assert tie_parity(sub, ad) and scope_identity(sub, ad)
            inm, _ = digraph_tables(sub["v"], sub["arcs"])
            acyc = acyclic_table(sub["v"], inm)
            mas = mas_table(sub["v"], acyc)
            iters = 40 if size <= 4 else 120
            rec = settle_ladder(sub, ad, mas, acyc, exact=False,
                                engine_iters=iters,
                                label="%s|%s" % (name.split(".")[0],
                                                 ",".join(map(str, S))))
            risk = (not rec["cert_ge_threshold"]) or rec["gap_pr"] >= 1 \
                or rec["gap_forms"] >= 1
            if risk and rec["falsifier"] is None and size <= 5 \
                    and deep_done < deep_budget["n"]:
                deep = settle_ladder(sub, ad, mas, acyc, exact=True,
                                     engine_iters=iters,
                                     label=rec["label"] + "|deep")
                rec = deep
                deep_done += 1
                flagged_here += 1
            elif risk and size == 6 and deep_budget["v6"] > 0 \
                    and rec["falsifier"] is None:
                deep = settle_ladder(sub, ad, mas, acyc, exact=True,
                                     engine_iters=300,
                                     label=rec["label"] + "|deep6")
                rec = deep
                deep_budget["v6"] -= 1
                flagged_here += 1
            records.append(rec)
            if rec["falsifier"] is not None:
                falsifier = rec
                log("FALSIFIER: %s" % rec["falsifier"])
                return records, domain, falsifier
        log("census %s size=%d: %d enumerated (of %d%s), flagged/deep %d"
            % (name, size, len(subs), total,
               ", thinned" if thinned else "", flagged_here))
    return records, domain, falsifier


def summarize(records):
    n = len(records)
    gap2 = [r for r in records if r["gap_pr"] >= 2 or r["gap_forms"] >= 2
            or (r.get("gap_named") or 0) >= 2]
    gap1 = [r for r in records if r["gap_pr"] >= 1 or r["gap_forms"] >= 1
            or (r.get("gap_named") or 0) >= 1]
    named_gap = [r for r in records if r.get("gap_named") is not None]
    below = [r for r in records if not r["cert_ge_threshold"]]
    min_named_ratio = min(
        (r["named_lo"] / r["v"]) for r in records) if records else 1.0
    exact_n = sum(1 for r in records if r["cert_exact"])
    max_gap_named = max((r["gap_named"] for r in named_gap), default=None)
    return dict(records=n, exact_records=exact_n, gap2=len(gap2),
                gap1=len(gap1), below_threshold=len(below),
                min_named_ratio=round(min_named_ratio, 4),
                falsifiers=sum(1 for r in records if r["falsifier"]),
                exact_named_records=len(named_gap),
                max_gap_named=max_gap_named,
                gap2_records=gap2[:6], gap1_records=gap1[:10])


def main():
    run_controls()
    cal = run_calibration()
    ladder = run_fixture_ladder()
    records, domain, falsifier = run_census()
    stats = summarize(records)
    cert = dict(
        package="research/fstar-family-gap-seed1c25f56f",
        controls="PASS_FG_CONTROLS",
        calibration="PASS_FG_CALIBRATION",
        fixtures=cal,
        fixture_ladder=ladder,
        census_domain=domain,
        census_stats=stats,
        census_records=records,
        falsifier=falsifier,
    )
    blob = json.dumps(cert, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()[:16]
    cert["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    log("certificate digest %s" % digest)
    print("PASS_FG_CENSUS records=%d exact=%d exact-named=%d gap1=%d gap2=%d "
          "below-threshold=%d falsifiers=%d max-gap-named=%s"
          % (stats["records"], stats["exact_records"],
             stats["exact_named_records"], stats["gap1"], stats["gap2"],
             stats["below_threshold"], stats["falsifiers"],
             stats["max_gap_named"]))
    if falsifier is not None:
        print("PASS_FSTAR_FAMILY_GAP falsifier-realized")
    else:
        print("PASS_FSTAR_FAMILY_GAP no-falsifier-in-domain")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
