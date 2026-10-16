#!/usr/bin/env python3
"""KB5f: cancellation lines (residue (i-prime)) of F-star, plus the dyadic
corollary normalization-gap reproduction (no kappa, no frontier change).

Exact stdlib engine over integer rank-3 decoders M = sum_j p_j q_j^T (v lines,
nonzero diagonal). Quantities per instance: zero digraph Z, Lemma SG anchor
reach |S_gamma| (PR 2869), the tie-parity classification tau(t) of Lemma CT,
the matched-pivot value MP (Lemma MP, PR 2717), the insertion-finite mixing
value of Lemma CL3 (this package: anchor labels a0 on A, matched pivots on T,
joint insertion at valid cuts), exact cert(M) by exhaustive a-enumeration with
exact b-completion (small v), engine witnesses with independent replay, and a
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
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


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


def mas_argmax(mas, acyc, S, memo):
    """An acyclic induced subset of S of size mas[S] (deterministic)."""
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


# ------------------------------------------------- Lemma SG anchor + Lemma CT

def v2_int(n):
    if n == 0:
        raise ValueError("v2(0)")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def anchor_data(mod):
    """Lemma SC/SG (PR 2869) plus Lemma CT tie parity (this package).

    c_j = min v2(p_j) + min v2(q_j) (Lemma SC); gamma = min_j c_j;
    S_gamma = {t : v2(M_tt) = gamma}; C = {t : v2(M_tt) > gamma} (cancellation
    lines); tau(t) = #{j : v2(p_j(t) q_j(t)) = gamma}. Lemma CT: t in S_gamma
    iff tau(t) odd; t in C iff tau(t) even. Canonical reduced normalization
    (alpha_j = -m_j): a0_j(t) = [v2(p_j(t)) = m_j], b0_j(t) =
    [v2(q_j(t)) = gamma - m_j], with scope identity K0_ts = 2^{-gamma} M_ts
    mod 2.
    """
    P, Q, M = mod["P"], mod["Q"], mod["M"]
    v = mod["v"]
    SENTINEL = 10 ** 9  # degenerate total (empty side): contributes no terms
    m = []
    n = []
    c = []
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
            if P[t][j] != 0 and Q[t][j] != 0 and v2_int(P[t][j]) + v2_int(Q[t][j]) == gamma:
                cnt += 1
        tau.append(cnt)
    a0 = [sum((1 << j) for j in range(3) if P[t][j] != 0 and v2_int(P[t][j]) == m[j])
          for t in range(v)]
    b0 = [sum((1 << j) for j in range(3) if Q[t][j] != 0 and v2_int(Q[t][j]) == gamma - m[j])
          for t in range(v)]
    return dict(gamma=gamma, m=m, n=n, c=c, diag=diag, reach=reach, cancel=cancel,
                tau=tau, a0=a0, b0=b0)


def dot1(x, y):
    return bin(x & y).count("1") & 1


def scope_identity(mod, ad):
    """K0_ts = 2^{-gamma} M_ts mod 2 for all t, s (Lemma SG (b), machine check)."""
    v, M = mod["v"], mod["M"]
    for t in range(v):
        for s in range(v):
            want = 1 if (M[t][s] != 0 and v2_int(M[t][s]) == ad["gamma"]) else 0
            if dot1(ad["a0"][t], ad["b0"][s]) != want:
                return False
    return True


def tie_parity(mod, ad):
    """Lemma CT (a): tau(t) odd iff t in S_gamma; tau(t) even iff t is a
    cancellation line. Returns True iff the identity holds on every line."""
    v = mod["v"]
    for t in range(v):
        if (ad["tau"][t] % 2 == 1) != (ad["diag"][t] == ad["gamma"]):
            return False
        if (ad["tau"][t] % 2 == 0) != (ad["diag"][t] > ad["gamma"]):
            return False
        if ad["tau"][t] > mod["D"][t].bit_count():
            return False
    return True


# ----------------------------------------------------- Lemma MP pivots

def matched_pivot(mod, mas, exhaustive_cap=200000, seed=20261016):
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


def pivot_witness(mod, best_map, mas, acyc):
    """Matched-pivot L8 witness for a pivot map: a(t)=b(t)=e_{c(t)}, kept set
    the MAS argmax subsets, order with every conflict pointing backward."""
    v = mod["v"]
    memo = {}
    kept = []
    for i in range(3):
        cls = sum((1 << t) for t in range(v) if best_map[t].bit_length() - 1 == i)
        kept.append(mas_argmax(mas, acyc, cls, memo))
    S = kept[0] | kept[1] | kept[2]
    a = [best_map[t] if (S >> t) & 1 else 0 for t in range(v)]
    b = [best_map[t] if (S >> t) & 1 else 0 for t in range(v)]
    order = topo_order_backward(mod, S, a, b)
    return dict(a=a, b=b, order=order, kept=order)


def topo_order_backward(mod, S, a, b):
    """Order kept set S with every conflict (u->v) pointing backward; None if
    the conflict digraph on S is cyclic. Deterministic (smallest index first)."""
    v, M = mod["v"], mod["M"]
    verts = [t for t in range(v) if (S >> t) & 1]
    succ = {t: set() for t in verts}
    indeg = {t: 0 for t in verts}
    for u in verts:
        for w in verts:
            if u != w and M[u][w] == 0 and dot1(a[u], b[w]) == 1:
                # conflict (u->w): u must come after w  =>  w before u
                if u not in succ[w]:
                    succ[w].add(u)
                    indeg[u] += 1
    order = []
    avail = sorted(t for t in verts if indeg[t] == 0)
    while avail:
        t = avail.pop(0)
        order.append(t)
        for u in sorted(succ[t]):
            indeg[u] -= 1
            if indeg[u] == 0:
                avail.append(u)
        avail.sort()
    return order if len(order) == len(verts) else None


# --------------------------------------------------------- cert engine
# PR 2717's exact-completion engine design (Aaron Wang), adapted here: for
# fixed a-labels the completion over b-labels, order and kept set is exact by
# subset DP.

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
    """Exact completion over b-labels/order/kept set for fixed a-labels.
    Returns (best size, witness dict or None)."""
    v = mod["v"]
    sg = mod["sg"]
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
    """Independent replay: supports, K_tt = 1 on kept, order constraints from
    scratch."""
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


def cert_exact(mod, max_v=6):
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


# --------------------------------- Lemma CL3: insertion-finite mixing (new)
# Anchor lines (S_gamma) labelled (a0, b0); the remaining lines carry matched
# pivots e_{c(t)}; a kept pivot subset per class with a backward-conflict
# order; anchor lines insert at valid cuts. Exact criterion: the joint demand
# digraph (pivot conflicts, plus for each inserted anchor x the demands
# L(x)-before-x and x-before-R(x)) must be acyclic.

def cl3_config(mod, ad, A, cmap, mas, acyc, memo=None, exact_A=False,
               want_witness=True):
    """Value of one mixing configuration (A anchor lines, pivot map cmap on
    T = complement): |A_kept| + sum_i |S_i| with S_i acyclic in Z[C_i] and
    A_kept jointly insertable at valid cuts (Lemma CL3). A_kept is chosen
    greedily in line order; with exact_A and |A| <= 12 the joint insertion is
    maximized exactly. Returns (value, witness or None, details)."""
    v, M = mod["v"], mod["M"]
    a0, b0 = ad["a0"], ad["b0"]
    if memo is None:
        memo = {}
    Tmask = ((1 << v) - 1) & ~A
    S = [0, 0, 0]
    for t in range(v):
        if (Tmask >> t) & 1:
            i = cmap[t].bit_length() - 1
            S[i] |= 1 << t
    keptP = [mas_argmax(mas, acyc, S[i], memo) for i in range(3)]
    S_T = keptP[0] | keptP[1] | keptP[2]
    piv = [t for t in range(v) if (S_T >> t) & 1]
    a = [a0[t] if (A >> t) & 1 else (cmap[t] if (S_T >> t) & 1 else 0) for t in range(v)]
    b = [b0[t] if (A >> t) & 1 else (cmap[t] if (S_T >> t) & 1 else 0) for t in range(v)]
    # demands among pivot-kept: conflict (u->w) => w before u
    succ = {t: set() for t in piv}
    indeg = {t: 0 for t in piv}
    for u in piv:
        for w in piv:
            if u != w and M[u][w] == 0 and cmap[u] == cmap[w]:
                if u not in succ[w]:
                    succ[w].add(u)
                    indeg[u] += 1
    # anchor lines: L(x) = pivot-kept t with M[x][t]==0 and bit c(t) set in
    # a0[x] (t before x); R(x) = pivot-kept t with M[t][x]==0 and bit c(t)
    # set in b0[x] (x before t). Joint insertion kept iff the union of
    # demands is acyclic (exact; anchors carry no conflicts with each other
    # by the scope identity K0 = M' mod 2 = 0 at incidences).
    alines = [t for t in range(v) if (A >> t) & 1]
    LX = {}
    RX = {}
    for x in alines:
        LX[x] = [t for t in piv if M[x][t] == 0 and (a0[x] & cmap[t])]
        RX[x] = [t for t in piv if M[t][x] == 0 and (b0[x] & cmap[t])]

    def joint_acyclic(subset):
        # eliminate anchors: x contributes demands t->x (t in LX) and x->t
        # (t in RX); a cycle through x needs an x-free pivot-demand path from
        # some r in RX(x) to some l in LX(x), or a pivot cycle.
        s2 = {t: set(succ[t]) for t in piv}
        for x in subset:
            for r in RX[x]:
                for l in LX[x]:
                    s2[r].add(l)
        ind2 = {t: 0 for t in piv}
        for u in piv:
            for w in s2[u]:
                ind2[w] += 1
        avail = [t for t in piv if ind2[t] == 0]
        seen = 0
        while avail:
            t = avail.pop()
            seen += 1
            for w in s2[t]:
                ind2[w] -= 1
                if ind2[w] == 0:
                    avail.append(w)
        return seen == len(piv)

    if not joint_acyclic([]):
        return 0, None, dict(insertable=0)
    keptA = []
    for x in alines:  # deterministic greedy insertion, then exact on <= 12
        if joint_acyclic(keptA + [x]):
            keptA.append(x)
    if exact_A and len(alines) <= 12:
        bestA = list(keptA)
        import itertools
        for r in range(len(alines) + 1):
            for sub in itertools.combinations(alines, r):
                if len(sub) > len(bestA) and joint_acyclic(list(sub)):
                    bestA = list(sub)
        keptA = bestA
    value = len(keptA) + S_T.bit_count()
    if not want_witness:
        return value, None, dict(insertable=len(keptA))
    # build the combined witness order: topological order of the joint demand
    # digraph (pivot demands + anchor demands), kept = keptA union S_T
    kept = sorted(keptA) + piv
    K = keptA + piv
    succ2 = {t: set() for t in K}
    indeg2 = {t: 0 for t in K}
    for u in piv:
        for w in piv:
            if u != w and M[u][w] == 0 and cmap[u] == cmap[w]:
                if u not in succ2[w]:
                    succ2[w].add(u)
                    indeg2[u] += 1
    for x in keptA:
        for t in LX[x]:
            if x not in succ2[t]:
                succ2[t].add(x)
                indeg2[x] += 1
        for t in RX[x]:
            if t not in succ2[x]:
                succ2[x].add(t)
                indeg2[t] += 1
    order = []
    avail = sorted(t for t in K if indeg2[t] == 0)
    while avail:
        t = avail.pop(0)
        order.append(t)
        for u in sorted(succ2[t]):
            indeg2[u] -= 1
            if indeg2[u] == 0:
                avail.append(u)
        avail.sort()
    if len(order) != len(K):
        return 0, None, dict(insertable=0)
    wit = dict(a=a, b=b, order=order, kept=order)
    return value, wit, dict(insertable=len(keptA))


def mxins_value(mod, ad, mas, acyc, scan_cap=20000, refine=32):
    """Bounded max of cl3_config over configurations (A subset of S_gamma,
    pivot map cmap on T = complement). Deterministic scan: A-subsets in
    descending size order, pivot maps in product order, stopped at scan_cap of
    the (possibly huge) family; greedy A per scanned config; the top `refine`
    scanned configs are then re-evaluated with exact joint insertion (exact_A,
    |A| <= 12). Returns (value, witness, details)."""
    v = mod["v"]
    reach = ad["reach"]
    Aall = 0
    for t in reach:
        Aall |= 1 << t
    allowed = [[1 << j for j in range(3) if mod["D"][t] & (1 << j)] for t in range(v)]
    alines = [t for t in range(v) if (Aall >> t) & 1]
    tlines = [t for t in range(v) if not (Aall >> t) & 1]
    family = 1
    for t in range(v):
        family *= (1 + len(allowed[t])) if (Aall >> t) & 1 else len(allowed[t])
    best = -1
    best_wit = None
    best_det = {}
    memo = {}
    max_ins = [0]

    def consider(A, cmap, exact):
        nonlocal best, best_wit, best_det
        val, _wit, det = cl3_config(mod, ad, A, cmap, mas, acyc, memo,
                                    exact_A=exact, want_witness=False)
        if det.get("insertable", 0) > max_ins[0]:
            max_ins[0] = det.get("insertable", 0)
        if val > best:
            _v2, wit, det2 = cl3_config(mod, ad, A, cmap, mas, acyc, memo,
                                        exact_A=exact, want_witness=True)
            if wit is not None and replay_witness(mod, wit):
                best, best_wit, best_det = val, wit, det2
        return val

    import itertools
    scanned_configs = []
    done = False
    for r in range(len(alines), -1, -1):
        if done:
            break
        for sub in itertools.combinations(alines, r):
            A = 0
            for t in sub:
                A |= 1 << t
            for combo in itertools.product(*[allowed[t] for t in tlines]):
                cmap = [0] * v
                for i, t in enumerate(tlines):
                    cmap[t] = combo[i]
                val = consider(A, cmap, False)
                scanned_configs.append((val, A, tuple(cmap)))
                if len(scanned_configs) >= scan_cap:
                    done = True
                    break
            if done:
                break
    scanned_configs.sort(key=lambda rc: (-rc[0], rc[1], rc[2]))
    for _val, A, cmapt in scanned_configs[:refine]:
        consider(A, list(cmapt), True)
    return best, best_wit, dict(exhaustive=(len(scanned_configs) == family),
                                family=family, scanned=len(scanned_configs),
                                refined=min(refine, len(scanned_configs)),
                                max_insertable=max_ins[0],
                                **best_det)


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
    """Bounded deterministic scan for an admissible B with chain cost <
    threshold."""
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


def v2_frac(x):
    """v2 of a nonzero Fraction: v2(num) - v2(den)."""
    from fractions import Fraction
    x = Fraction(x)
    return v2_int(x.numerator) - v2_int(x.denominator)


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
    mp, _m, _exh, _prod = matched_pivot(mod, mas)
    assert mp == 3, "diagonal decoder MP"
    # 3. corrupted witnesses rejected
    mod = model([(1, 1, 0), (1, 0, 1)], [(1, 0, -1), (1, -1, 0)])
    _val, wit = cert_exact(mod)
    assert replay_witness(mod, wit)
    bad1 = dict(wit); bad1["a"] = list(wit["a"]); bad1["a"][0] = 0
    bad2 = dict(wit); bad2["b"] = list(wit["b"]); bad2["b"][1] = 0
    assert not replay_witness(mod, bad1), "corrupt a not rejected"
    assert not replay_witness(mod, bad2), "corrupt b not rejected"
    # 4. Lemma CT hand values: diag(2,1,1): one tau=0 cancellation line
    mod = model([(2, 0, 0), (0, 1, 0), (0, 0, 1)], [(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    ad = anchor_data(mod)
    assert ad["gamma"] == 0 and ad["reach"] == [1, 2] and ad["cancel"] == [0], \
        "diag(2,1,1) anchor sets"
    assert ad["tau"] == [0, 1, 1] and tie_parity(mod, ad), "diag(2,1,1) tie parity"
    assert scope_identity(mod, ad), "diag(2,1,1) scope identity"
    # 5. Lemma CT hand values: one tau=2 tied line (two tied minima)
    mod = model([(1, 1, 0), (1, 0, 0), (0, 1, 1)], [(1, 1, 0), (1, 1, 0), (1, 0, 1)])
    ad = anchor_data(mod)
    assert ad["tau"] == [2, 1, 1] and ad["cancel"] == [0] and ad["reach"] == [1, 2], \
        "tau=2 hand instance: %r %r %r" % (ad["tau"], ad["cancel"], ad["reach"])
    assert tie_parity(mod, ad) and scope_identity(mod, ad), "tau=2 hand identities"
    # 6. Lemma CT (b): |D(t)| = 1 lines are pivot-bit-forced: every K_tt = 1
    # labelling has the unique bit j of D(t) set in both labels, and the
    # matched pivot (e_j, e_j) attains K_tt = 1 (so the line sits in the MP
    # family; it can never carry a tau = 2 tie since tau(t) <= |D(t)|).
    forced = 0
    for t in range(3):
        if mod["D"][t].bit_count() == 1:
            j = mod["D"][t].bit_length() - 1
            for a in range(8):
                if a & ~mod["pi"][t]:
                    continue
                for b in range(8):
                    if b & ~mod["sg"][t]:
                        continue
                    if dot1(a, b) == 1:
                        assert (a & (1 << j)) and (b & (1 << j)), "pivot-bit forcing"
                        forced += 1
            assert dot1(1 << j, 1 << j) == 1, "matched pivot attains K_tt = 1"
            assert ad["tau"][t] <= 1, "tau(t) <= |D(t)| = 1"
    assert forced >= 1, "pivot-forcing control must exercise a |D|=1 line"
    # 7. Lemma CL3 criterion vs exact completion on tiny instances: the CL3
    # witness replays and its value never exceeds completion with the same
    # a-labels (completion allows free b-labels).
    checked = 0
    for P, Q in tiny:
        m2 = model(P, Q)
        inm2, _ = digraph_tables(m2["v"], m2["arcs"])
        acyc2 = acyclic_table(m2["v"], inm2)
        mas2 = mas_table(m2["v"], acyc2)
        ad2 = anchor_data(m2)
        allowed = [[1 << j for j in range(3) if m2["D"][t] & (1 << j)] for t in range(m2["v"])]
        import itertools
        for r in range(len(ad2["reach"]) + 1):
            for sub in itertools.combinations(ad2["reach"], r):
                A = 0
                for t in sub:
                    A |= 1 << t
                for combo in itertools.product(*allowed):
                    val, wit, _det = cl3_config(m2, ad2, A, list(combo), mas2, acyc2,
                                                exact_A=True)
                    alist = [ad2["a0"][t] if (A >> t) & 1 else combo[t]
                             for t in range(m2["v"])]
                    cval, _cw = completion(m2, alist)
                    assert wit is None or replay_witness(m2, wit), "CL3 witness replay"
                    assert val <= cval, "CL3 must not exceed completion"
                    checked += 1
    assert checked >= 8, "CL3-vs-completion control must exercise configs"
    # 8. NORMALIZATION-GAP reproduction (CORRECTIVE): dyadic entries do NOT
    # imply Lemma AN's 2-integrality hypothesis. PR 2869 control SC1:
    # p = q = (1/2)(1,1) on two lines: entries dyadic, c_1 = -2, the interval
    # [-m, n] for the per-total rescaling alpha is empty, so no per-total
    # power of two makes both factors 2-integral; Lemma SG's global rescale
    # still anchors both lines (gamma = -2, S_gamma = both).
    from fractions import Fraction
    half = Fraction(1, 2)
    pv = [half, half]
    qv = [half, half]
    mv = [min(v2_frac(x) for x in pv), min(v2_frac(x) for x in qv)]
    cv = mv[0] + mv[1]
    assert cv == -2, "SC1 content must be -2"
    assert -mv[0] > mv[1], "SC1 per-total rescaling interval must be empty"
    Mdiag = [pv[t] * qv[t] for t in range(2)]
    assert all(v2_frac(d) == cv for d in Mdiag), "SC1 diagonals sit at gamma"
    reach_sc1 = sum(1 for t in range(2) if v2_frac(pv[t] * qv[t]) == cv)
    assert reach_sc1 == 2, "SC1 corrected anchor reaches both lines"
    # count gap (PR 2869 control SC2): M = 2 I_3 has naive odd-diagonal count
    # 0 while the corrected reach is 3 (gamma = 1).
    mod = model([(2, 0, 0), (0, 2, 0), (0, 0, 2)], [(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    ad = anchor_data(mod)
    naive = sum(1 for t in range(3) if mod["M"][t][t] % 2 != 0)
    assert naive == 0 and ad["gamma"] == 1 and ad["reach"] == [0, 1, 2], \
        "SC2 count gap exhibit"
    log("controls: brute_agree=3/3 diagonal=3 mp=3 corrupt_rejects=2/2 "
        "ct_hands=2 pivot_forced=%d cl3_vs_completion=%d gap_SC1=ok gap_SC2=ok" %
        (forced, checked))
    print("PASS_CL_CONTROLS")


# ------------------------------------------------------------- calibration

def run_calibration():
    """Reproduce every recorded anchor of PRs 2717/2747/2869/2890, then settle
    the fixtures through the Lemma CL3 ladder."""
    log("calibration (recorded anchors)")
    # tied_min (v = 12): PR 2717 witness 11/12; PR 2747 MP/MX 9; PR 2869
    # reach 0/12 = anchor_good; PR 2890 PASS_FC4_CALIBRATION 11/12.
    mod = load_model("tied_min.json")
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    ad = anchor_data(mod)
    assert (ad["gamma"], ad["reach"], ad["cancel"]) == (0, [], list(range(12))), \
        "tied_min must be 12/12 cancellation lines"
    assert tie_parity(mod, ad) and scope_identity(mod, ad), "tied_min CT identities"
    mp, mpmap, exh, prod = matched_pivot(mod, mas)
    assert exh and prod == 4096 and mp == 9, "tied_min MP must be 9 (4096 maps)"
    pw = pivot_witness(mod, mpmap, mas, acyc)
    assert replay_witness(mod, pw) and len(pw["kept"]) == 9, "tied_min MP witness"
    mxi, mxwit, mxdet = mxins_value(mod, ad, mas, acyc, scan_cap=6000, refine=8)
    assert mxwit is not None and replay_witness(mod, mxwit), "tied_min MX-ins witness"
    assert mxi == mp == 9, "tied_min MX-ins must equal MP (no anchor lines)"
    val, wit = cert_hillclimb(mod, iters=250, seed=11)
    assert replay_witness(mod, wit) and val == 11, "tied_min engine witness 11"
    assert val >= 8, "tied_min F-star threshold 8"
    log("tied_min.json: v=12 thr=8 MP=9 (4096 maps) MXins=9 reach=0/12 "
        "cancel=12/12 tau_even=12 witness=%d (PR 2717 recorded 11/12)" % val)
    tied_rec = dict(v=12, threshold=8, MP=9, MXins=9, reach=0, cancel=12,
                    witness=11, tau_hist={}, mxins_detail=mxdet)
    for t in range(12):
        tied_rec["tau_hist"][ad["tau"][t]] = tied_rec["tau_hist"].get(ad["tau"][t], 0) + 1
    # cex_min_1 (v = 19): PR 2717 stored witness 18/19; PR 2747 MP/MX 16
    # (6144 maps) with mixed route failing 6144/6144 in both block orders; PR
    # 2869 reach 8/19 = anchor_good; PR 2890 chain 22.
    mod = load_model("cex_min_1.json")
    inm, _ = digraph_tables(mod["v"], mod["arcs"])
    acyc = acyclic_table(mod["v"], inm)
    mas = mas_table(mod["v"], acyc)
    ad = anchor_data(mod)
    assert (ad["gamma"], ad["reach"], ad["cancel"]) == (0, [0, 4, 5, 6, 8, 11, 14, 15],
                                                        [1, 2, 3, 7, 9, 10, 12, 13, 16,
                                                         17, 18]), \
        "cex_min_1 anchor sets must match PR 2869 (reach 8 of 19, lines 0,4,5,6,8,11,14,15)"
    assert tie_parity(mod, ad) and scope_identity(mod, ad), "cex_min_1 CT identities"
    mp, mpmap, exh, prod = matched_pivot(mod, mas)
    assert exh and prod == 6144 and mp == 16, "cex_min_1 MP must be 16 (6144 maps)"
    pw = pivot_witness(mod, mpmap, mas, acyc)
    assert replay_witness(mod, pw) and len(pw["kept"]) == 16, "cex_min_1 MP witness"
    with open(os.path.join(DATA, "cex_min_1.witness.json"), "r", encoding="utf-8") as fh:
        wit = json.load(fh)
    wit = dict(a=wit["a"], b=wit["b"], order=wit["order"], kept=wit["kept"])
    assert replay_witness(mod, wit), "cex_min_1 stored witness replay"
    assert len(wit["kept"]) == 18 and 18 >= 12, "cex_min_1 stored witness 18/19"
    with open(os.path.join(DATA, "cex_min_1.B22.json"), "r", encoding="utf-8") as fh:
        B = json.load(fh)
    if isinstance(B, dict):
        B = B.get("B", B.get("pairing"))
    assert admissible(mod, B), "stored pairing admissible"
    cc = chain_cost(mod, B)
    assert cc == 22, "chain engine must reproduce 22 (10+6+6)"
    log("cex_min_1.json: v=19 thr=12 MP=16 (6144 maps) reach=8/19 cancel=11/19 "
        "witness=18 (PR 2717 recorded 18/19) chain=22 (PR 2111 recorded 10+6+6)")
    # Lemma CL3 insertion analysis on cex_min_1: how many of the 8 anchor
    # lines become placeable at valid cuts (PR 2747 open question 2)?
    mxi, mxwit, mxdet = mxins_value(mod, ad, mas, acyc, scan_cap=20000, refine=32)
    assert mxwit is not None and replay_witness(mod, mxwit), "cex_min_1 MX-ins witness"
    assert mxi >= mp, "MX-ins must not fall below MP"
    ins = mxdet.get("insertable", 0)
    log("cex_min_1.json: MXins=%d (insertable anchor lines at the best config "
        "%d of 8, max seen %d, family=%d scanned=%d refined=%d exhaustive=%s)"
        % (mxi, ins, mxdet.get("max_insertable", 0), mxdet["family"],
           mxdet["scanned"], mxdet["refined"], mxdet["exhaustive"]))
    cex_rec = dict(v=19, threshold=12, MP=16, MXins=mxi, reach=8, cancel=11,
                   witness=18, chain=22, insertable=ins, mxins_detail=mxdet)
    print("PASS_CL_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 "
          "reach=0/12,8/19")
    return tied_rec, cex_rec


# ------------------------------------------------------- cancellation search

def gen_parity(rng, v, k):
    """Parity-engineered factorization: prescribed tau(t) = |u(t)| pattern
    with exactly k even-|u(t)| lines (cancellation lines) and every total
    appearing with an odd entry on both sides (so all c_j = 0, gamma = 0)."""
    evens = set(rng.sample(range(v), k))
    for _ in range(300):
        u = []
        for t in range(v):
            if t in evens:
                u.append(sorted(rng.choice([[0, 1], [0, 2], [1, 2]])))
            else:
                u.append(sorted(rng.choice([[0], [1], [2], [0, 1, 2]])))
        if set().union(*[set(x) for x in u]) != {0, 1, 2}:
            continue
        P = []
        Q = []
        for t in range(v):
            P.append(tuple(rng.choice([1, -1, 3, -3]) if j in u[t]
                           else rng.choice([0, 2, -2]) for j in range(3)))
            Q.append(tuple(rng.choice([1, -1, 3, -3]) if j in u[t]
                           else rng.choice([0, 2, -2]) for j in range(3)))
        mod = valid_instance(P, Q)
        if mod is None:
            continue
        ad = anchor_data(mod)
        if tie_parity(mod, ad) and len(ad["cancel"]) == k:
            return mod
    return None


def valid_instance(P, Q):
    try:
        mod = model(P, Q)
    except AssertionError:
        return None
    for j in range(3):
        if all(P[t][j] == 0 for t in range(len(P))) or \
           all(Q[t][j] == 0 for t in range(len(Q))):
            return None
    return mod


def draw_row(rng, mask):
    return tuple(rng.choice([1, -1, 2, -2, 3, -3]) if (mask >> j) & 1 else 0
                for j in range(3))


def tune_scalings(P, Q, k, rng, tries=400):
    """Row/column scalings by positive powers of two leave Z unchanged (M_ts
    scales by 2^(a_t + b_s)) and move the tau-parity pattern; search small
    scalings for exactly k cancellation lines. Returns a model or None."""
    v = len(P)
    for _ in range(tries):
        a = [rng.randint(0, 2) for _ in range(v)]
        b = [rng.randint(0, 2) for _ in range(v)]
        P2 = [tuple(x * (1 << a[t]) for x in P[t]) for t in range(v)]
        Q2 = [tuple(x * (1 << b[t]) for x in Q[t]) for t in range(v)]
        mod = valid_instance(P2, Q2)
        if mod is None:
            continue
        ad = anchor_data(mod)
        if tie_parity(mod, ad) and len(ad["cancel"]) == k:
            return mod
    return None


MASKS2 = [3, 5, 6]  # size-2 supports {0,1}, {0,2}, {1,2}
MASKS3 = [7]


def gen_structured(rng, v, k, size2=True):
    """Dense-Z base with the tied_min hard signature: every line carries a
    size-2 support on both sides (|D(t)| = 2, the recorded fixture pattern),
    then valuation tuning to exactly k cancellation lines."""
    for _ in range(80):
        pool = MASKS2 if size2 else MASKS2 + MASKS3
        ms = [pool[rng.randrange(len(pool))] for _ in range(v)]
        P = [draw_row(rng, ms[t]) for t in range(v)]
        Q = [draw_row(rng, ms[t]) for t in range(v)]
        mod = valid_instance(P, Q)
        if mod is None:
            continue
        out = tune_scalings(P, Q, k, rng)
        if out is not None:
            return out
    return None


def gen_adversarial(rng, v, k):
    """Smallest-first adversary for the named families (PR 2747 open question
    1): hill-climb tied_min-signature instances toward a low matched-pivot
    floor max_c sum_i MAS(Z[C_i]) at exactly k cancellation lines. Returns the
    hardest instance found (lowest sampled MP, tie-broken by arc count)."""
    best = None
    best_mp = 99
    for restart in range(6):
        cur = gen_structured(rng, v, k, size2=(restart % 2 == 0))
        if cur is None:
            continue
        inm, _ = digraph_tables(cur["v"], cur["arcs"])
        acyc = acyclic_table(cur["v"], inm)
        mas = mas_table(cur["v"], acyc)
        mp, _m, _e, _p = matched_pivot(cur, mas, exhaustive_cap=4096)
        if (mp, -len(cur["arcs"])) < (best_mp, -(len(best["arcs"]) if best else 0)):
            best, best_mp = cur, mp
        for _step in range(12):
            P = [tuple(x) for x in cur["P"]]
            Q = [tuple(x) for x in cur["Q"]]
            t = rng.randrange(v)
            ms = MASKS2 if rng.randrange(2) else MASKS2 + MASKS3
            mt = ms[rng.randrange(len(ms))]
            if rng.randrange(2):
                P[t] = draw_row(rng, mt)
            else:
                Q[t] = draw_row(rng, mt)
            cand = tune_scalings(P, Q, k, rng, tries=60)
            if cand is None:
                continue
            inm2, _ = digraph_tables(cand["v"], cand["arcs"])
            acyc2 = acyclic_table(cand["v"], inm2)
            mas2 = mas_table(cand["v"], acyc2)
            mp2, _m2, _e2, _p2 = matched_pivot(cand, mas2, exhaustive_cap=4096)
            if (mp2, -len(cand["arcs"])) <= (mp, -len(cur["arcs"])):
                cur, mp = cand, mp2
                if (mp, -len(cur["arcs"])) < (best_mp, -(len(best["arcs"]) if best else 0)):
                    best, best_mp = cur, mp
    return best


def settle_search(mod, label, mp_cap=20000, run_mxins=False, mxins_cap=600,
                  force_engine=False):
    """Smallest-first falsifier-search settlement of one decoder. Cheap rungs
    first: anchor (SG), matched pivots (MP), then the Lemma CL3 ladder and the
    engine only where needed. Falsifier criterion (armed, decisive when it
    fires): exact cert < floor(2v/3) where exhaustive a-enumeration terminates,
    or an explicit admissible B with chain cost < floor(2v/3) (the proven
    chain of research/root-unit-decoder-lemmas)."""
    v = mod["v"]
    thr = (2 * v) // 3
    inm, _ = digraph_tables(v, mod["arcs"])
    acyc = acyclic_table(v, inm)
    mas = mas_table(v, acyc)
    ad = anchor_data(mod)
    assert tie_parity(mod, ad), "Lemma CT tie parity must hold"
    assert scope_identity(mod, ad), "scope identity must hold"
    rec = dict(label=label, v=v, k_cancel=len(ad["cancel"]), threshold=thr,
               gamma=ad["gamma"], reach=len(ad["reach"]),
               tau_hist={})
    for t in range(v):
        rec["tau_hist"][ad["tau"][t]] = rec["tau_hist"].get(ad["tau"][t], 0) + 1
    mp, mpmap, exh, prod = matched_pivot(mod, mas, exhaustive_cap=mp_cap)
    pw = pivot_witness(mod, mpmap, mas, acyc)
    assert pw is not None and replay_witness(mod, pw), "MP witness must replay"
    rec["MP"] = mp
    rec["MP_exhaustive"] = exh
    rec["MP_pivot_product"] = prod
    lower = max(mp, len(ad["reach"]))
    rec["MXins"] = None
    if run_mxins:
        mxi, mxwit, mxdet = mxins_value(mod, ad, mas, acyc, scan_cap=mxins_cap,
                                        refine=2)
        assert mxwit is not None and replay_witness(mod, mxwit), \
            "MX-ins witness must replay"
        rec["MXins"] = mxi
        rec["MXins_detail"] = mxdet
        rec["insertable"] = mxdet.get("insertable", 0)
        lower = max(lower, mxi)
    rec["cert_lower_bound"] = lower
    rec["meets_threshold"] = lower >= thr
    rec["falsifier"] = None
    if lower < thr or force_engine:
        # named families short of the threshold (or a forced adversary probe):
        # run the engine ladder; the falsifier criterion only matters below
        if v <= 13:
            val, wit = cert_hillclimb(mod, iters=300, seed=77)
            assert wit is not None and replay_witness(mod, wit), "engine witness"
            rec["engine_witness"] = val
            rec["engine_over_named"] = val - lower
            lower = max(lower, val)
            rec["cert_lower_bound"] = lower
            rec["meets_threshold"] = lower >= thr
        else:
            rec["engine_skipped_v"] = v
        if lower < thr:
            exact = None
            if v <= 5:
                exact, _ew = cert_exact(mod, max_v=5)
                rec["cert_exact"] = exact
                if exact is not None and exact < thr:
                    rec["falsifier"] = "exact cert %d < threshold %d" % (exact, thr)
                    return rec
            cc, _B, hit = chain_scan(mod, thr)
            rec["chain_scan_best"] = cc
            if hit:
                rec["falsifier"] = ("admissible B with chain cost %d < threshold %d"
                                    % (cc, thr))
    return rec


def mat_inv3(A):
    """Inverse of a unimodular 3x3 integer matrix (adjugate; det = +-1)."""
    det = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
           - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
           + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
    assert abs(det) == 1, "matrix must be unimodular"
    C = [[(A[1][1] * A[2][2] - A[1][2] * A[2][1]),
          -(A[0][1] * A[2][2] - A[0][2] * A[2][1]),
          (A[0][1] * A[1][2] - A[0][2] * A[1][1])],
         [-(A[1][0] * A[2][2] - A[1][2] * A[2][0]),
          (A[0][0] * A[2][2] - A[0][2] * A[2][0]),
          -(A[0][0] * A[1][2] - A[0][2] * A[1][0])],
         [(A[1][0] * A[2][1] - A[1][1] * A[2][0]),
          -(A[0][0] * A[2][1] - A[0][1] * A[2][0]),
          (A[0][0] * A[1][1] - A[0][1] * A[1][0])]]
    return [[C[r][c] // det for c in range(3)] for r in range(3)]


def gen_resplit(rng, P, Q, steps=4):
    """GL_3(Z) re-split of a stored factorization: P -> P A, Q -> Q A^{-T}
    with A unimodular. M and its zero digraph Z are unchanged; the supports
    pi, sigma, the contents c_j, gamma, S_gamma and the cancellation count all
    move (PR 2869 open question 2)."""
    A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for _ in range(steps):
        i, j = rng.sample(range(3), 2)
        lam = rng.choice([-2, -1, 1, 2])
        for r in range(3):
            A[r][i] += lam * A[r][j]
    Ainv = mat_inv3(A)
    AinvT = [[Ainv[c][r] for c in range(3)] for r in range(3)]
    P2 = [tuple(sum(P[t][j] * A[j][c] for j in range(3)) for c in range(3))
          for t in range(len(P))]
    Q2 = [tuple(sum(Q[t][j] * AinvT[j][c] for j in range(3)) for c in range(3))
          for t in range(len(Q))]
    return valid_instance(P2, Q2)


def run_resplit():
    """Fixture-density hard-instance probe: GL_3(Z) re-splits of the two
    canonical fixtures keep their dense zero digraphs (tied_min MAS(Z) = 4 of
    12, cex_min_1 MAS(Z) = 10 of 19) while sweeping gamma, S_gamma and the
    cancellation count; each re-split is settled through the named-family
    ladder. This probes the 1..v cancellation-line axis at the exact density
    where the recorded obstruction lives."""
    log("resplit probe (fixture-density Z, GL_3(Z) re-splits)")
    rng = random.Random(28690202)
    recs = []
    stats = dict(replits=0, falsifiers=0, min_named_ratio=9.9, k_seen=set(),
                 min_MP_ratio=9.9)
    falsifier = None
    hardest = None
    hardest_named = 99
    for name, tries in (("tied_min.json", 12), ("cex_min_1.json", 12)):
        base = load_model(name)
        for i in range(tries):
            mod = gen_resplit(rng, base["P"], base["Q"])
            if mod is None:
                continue
            rec = settle_search(mod, "resplit %s #%d" % (name, i), mp_cap=20000,
                                run_mxins=True, mxins_cap=2000)
            recs.append(rec)
            stats["replits"] += 1
            stats["k_seen"].add(rec["k_cancel"])
            named = max(rec["MP"], rec["reach"], rec["MXins"] or 0)
            if named < hardest_named and rec["v"] <= 13:
                hardest, hardest_named = mod, named
            if named / rec["v"] < stats["min_named_ratio"]:
                stats["min_named_ratio"] = named / rec["v"]
            if rec["MP"] / rec["v"] < stats["min_MP_ratio"]:
                stats["min_MP_ratio"] = rec["MP"] / rec["v"]
            if rec["falsifier"] is not None:
                falsifier = rec
                break
        if falsifier is not None:
            break
    # family-gap probe: the engine ladder on the hardest small-v re-split
    if hardest is not None:
        hrec = settle_search(hardest, "resplit hardest (engine probe)",
                             run_mxins=True, mxins_cap=2000, force_engine=True)
        recs.append(hrec)
        stats["engine_over_named_on_hardest"] = hrec.get("engine_over_named", 0)
        if hrec["falsifier"] is not None:
            falsifier = hrec
    stats["k_seen"] = sorted(stats["k_seen"])
    if falsifier is not None:
        stats["falsifiers"] = 1
    log("resplit: %d re-splits, falsifiers=%d, min named ratio %.3f, min MP "
        "ratio %.3f, cancellation counts seen %r, engine-over-named on hardest %s"
        % (stats["replits"], stats["falsifiers"], stats["min_named_ratio"],
           stats["min_MP_ratio"], stats["k_seen"],
           stats.get("engine_over_named_on_hardest", "n/a")))
    print("PASS_CL_RESPLIT")
    return recs, stats, falsifier


def run_search(vmax=12):
    """Smallest-first falsifier search across decoders with 1..v cancellation
    lines (the residue (i-prime) axis). Deterministic seeds. Generators:
    parity-engineered (exact k), generic integer, dense-Z structured
    (orthogonality pool + valuation tuning), and an adversary hill-climbing
    the matched-pivot floor at exactly k cancellation lines (PR 2747 open
    question 1). The Lemma CL3 ladder runs on every residue-axis instance
    (k > floor(v/3)); the engine ladder runs on every adversary winner and on
    every instance whose named families fall short of the threshold."""
    log("search (smallest first, 1..v cancellation lines)")
    rng = random.Random(8069336)
    recs = []
    falsifier = None
    stats = dict(instances=0, falsifiers=0, min_ratio=9.9, min_named_ratio=9.9,
                 exact_decided=0, engine_runs=0, mxins_runs=0, adversary_runs=0,
                 max_engine_over_named=0)
    for v in range(3, vmax + 1):
        for k in range(1, v + 1):
            reps = 2 if v <= 9 else 1
            for rep in range(reps):
                if rep == 0:
                    fam = "parity"
                    mod = gen_parity(rng, v, k)
                else:
                    fam = "structured"
                    mod = gen_structured(rng, v, k)
                if mod is None:
                    log("v=%d k=%d fam=%s: no instance in budget (recorded)"
                        % (v, k, fam))
                    continue
                run_mx = (k > v // 3)
                rec = settle_search(mod, "v=%d k=%d fam=%s" % (v, k, fam),
                                    run_mxins=run_mx)
                recs.append(rec)
                stats["instances"] += 1
                if run_mx:
                    stats["mxins_runs"] += 1
                if "engine_witness" in rec:
                    stats["engine_runs"] += 1
                if "cert_exact" in rec:
                    stats["exact_decided"] += 1
                ratio = rec["cert_lower_bound"] / v
                if ratio < stats["min_ratio"]:
                    stats["min_ratio"] = ratio
                if "MXins" in rec and rec["MXins"] is not None:
                    nr = max(rec["MP"], rec["reach"], rec["MXins"]) / v
                else:
                    nr = max(rec["MP"], rec["reach"]) / v
                if nr < stats["min_named_ratio"]:
                    stats["min_named_ratio"] = nr
                if rec["falsifier"] is not None:
                    falsifier = rec
                    break
            if falsifier is not None:
                break
            if k > v // 3 and v <= 11 and falsifier is None:
                # adversary pass (PR 2747 open question 1): minimize the
                # named-family floor at this (v, k)
                amod = gen_adversarial(rng, v, k)
                if amod is not None:
                    rec = settle_search(amod, "v=%d k=%d fam=adversarial" % (v, k),
                                        run_mxins=True, mxins_cap=2000,
                                        force_engine=True)
                    recs.append(rec)
                    stats["instances"] += 1
                    stats["mxins_runs"] += 1
                    stats["adversary_runs"] += 1
                    stats["engine_runs"] += 1
                    if "engine_over_named" in rec and \
                            rec["engine_over_named"] > stats["max_engine_over_named"]:
                        stats["max_engine_over_named"] = rec["engine_over_named"]
                    ratio = rec["cert_lower_bound"] / v
                    if ratio < stats["min_ratio"]:
                        stats["min_ratio"] = ratio
                    nr = max(rec["MP"], rec["reach"], rec["MXins"] or 0) / v
                    if nr < stats["min_named_ratio"]:
                        stats["min_named_ratio"] = nr
                    if rec["falsifier"] is not None:
                        falsifier = rec
                else:
                    log("v=%d k=%d fam=adversarial: no instance in budget (recorded)"
                        % (v, k))
        log("v=%d done (instances %d, falsifiers %d)" %
            (v, stats["instances"], stats["falsifiers"]))
        if falsifier is not None:
            break
    if falsifier is not None:
        stats["falsifiers"] = 1
        log("FALSIFIER: %s: %s" % (falsifier["label"], falsifier["falsifier"]))
    log("search: %d instances, falsifiers=%d, min cert ratio %.3f, min named "
        "ratio %.3f, exact-decided=%d, engine runs=%d, MX-ins runs=%d, "
        "adversary runs=%d, max engine-over-named=%d"
        % (stats["instances"], stats["falsifiers"], stats["min_ratio"],
           stats["min_named_ratio"], stats["exact_decided"], stats["engine_runs"],
           stats["mxins_runs"], stats["adversary_runs"],
           stats["max_engine_over_named"]))
    return recs, stats, falsifier


def main():
    run_controls()
    tied_rec, cex_rec = run_calibration()
    rrecs, rstats, rfalsifier = run_resplit()
    recs, stats, falsifier = run_search()
    if falsifier is None:
        falsifier = rfalsifier
    cert = dict(
        package="research/fstar-cancellation-lines-seed80d69336",
        controls="PASS_CL_CONTROLS",
        calibration="PASS_CL_CALIBRATION",
        gap_controls="PASS_CL_GAP",
        fixtures=dict(tied_min=tied_rec, cex_min_1=cex_rec),
        resplit_stats=rstats,
        resplit_records=rrecs,
        search_stats=stats,
        search_records=recs,
        falsifier=falsifier,
    )
    blob = json.dumps(cert, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()[:16]
    cert["digest"] = digest
    out = os.path.join(HERE, "CERTIFICATE.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    log("certificate digest %s" % digest)
    print("PASS_CL_GAP dyadic-corollary-normalization-gap=reproduced SC1 SC2")
    print("PASS_CL_SEARCH")
    print("PASS_FSTAR_CANCELLATION_LINES")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

