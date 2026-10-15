#!/usr/bin/env python3
"""F-star residue class (ii): non-3-dichromatic zero digraphs (no kappa).

Exact stdlib computation over rank-3 rational decoders M = sum_j p_j q_j^T:
the zero digraph Z, its MAS profile over all subsets, the exact matched-pivot
value of Lemma MP (max over pivot maps c into D(t) of sum_i MAS(Z[C_i])),
dichromatic decisions for Z with and without the pivot constraints, and a
smallest-first adversarial search for instances where the matched-pivot value
falls below floor(2v/3), with the proven chain cost >= cert(M) as the
falsifier criterion.

Engine credit: the model (signature/opts), the exact-completion engine
(bfeas_tables/blockers_pred/complete/reconstruct), the independent witness
checker, hill_climb/exact_cert and the chain machinery (block_rank/chain_cost/
min_chain_cost) are adapted from Aaron Wang's PR 2747
research/fstar-tied-residue-seeddcc97691 and PR 2717
research/fstar-proof-lemmas-seed3096ed3f, which adapt DreamingOfClouds'
PR 2111 rank-3 model. New in this file: the subset-DP zero-digraph machinery
(acyclic/MAS for every subset), mp_exact, chi_exact_dp / chi_le3_backtrack,
omega_mutual, the class-(ii) generators and the search driver. Apache-2.0.
"""

import hashlib
import itertools
import json
import os
import random
import sys
import time

sys.setrecursionlimit(10000)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.2f}s] {msg}", flush=True)


# ---------------------------------------------------------------- model ----
def signature(P, Q):
    v = len(P)
    M = [[sum(P[t][j] * Q[s][j] for j in range(3)) for s in range(v)] for t in range(v)]
    pi = [sum(1 << j for j in range(3) if P[t][j]) for t in range(v)]
    sg = [sum(1 << j for j in range(3) if Q[t][j]) for t in range(v)]
    Z = [[M[t][s] == 0 for s in range(v)] for t in range(v)]
    assert all(M[t][t] != 0 for t in range(v)), "decoder must have nonzero diagonal"
    return M, pi, sg, Z


def opts(pi_t):
    return [m for m in range(1, 8) if not (m & ~pi_t)]


def threshold(v):
    return (2 * v) // 3


# --------------------------------------------- exact completion engine ----
def bfeas_tables(pi, sg):
    tabs = []
    for t in range(len(pi)):
        tab = [[False] * 256 for _ in range(8)]
        for am in range(1, 8):
            if am & ~pi[t]:
                continue
            for bset in range(256):
                ok = False
                for b in range(1, 8):
                    if b & ~sg[t] or ((am & b).bit_count() & 1) == 0:
                        continue
                    good, bs = True, bset
                    while bs:
                        lb = bs & -bs
                        if (((lb.bit_length() - 1) & b).bit_count() & 1):
                            good = False
                            break
                        bs ^= lb
                    if good:
                        ok = True
                        break
                tab[am][bset] = ok
        tabs.append(tab)
    return tabs


def blockers_pred(Z, v):
    pred = [0] * v
    for t in range(v):
        m = 0
        for s in range(v):
            if s != t and Z[s][t]:
                m |= 1 << s
        pred[t] = m
    return pred


def complete(a, pi, sg, Z, v, tabs):
    """Exact max |S| over (b, order, S) for fixed a-labels. Returns (value, bestT, f)."""
    pred = blockers_pred(Z, v)
    N = 1 << v
    Abits = bytearray(N)
    for U in range(1, N):
        lb = U & -U
        Abits[U] = Abits[U ^ lb] | (1 << a[lb.bit_length() - 1])
    f = bytearray(N)
    f[0] = 1
    best, bestT = 0, 0
    for T in range(1, N):
        ok, U = 0, T
        while U:
            lb = U & -U
            u = lb.bit_length() - 1
            prev = T ^ lb
            if f[prev] and tabs[u][a[u]][Abits[prev & pred[u]]]:
                ok = 1
                break
            U ^= lb
        f[T] = ok
        if ok and T.bit_count() > best:
            best, bestT = T.bit_count(), T
    return best, bestT, f


def reconstruct(a, sg, Z, v, tabs, bestT, f):
    pred = blockers_pred(Z, v)

    def ab(U):
        r, x = 0, U
        while x:
            lb = x & -x
            r |= 1 << a[lb.bit_length() - 1]
            x ^= lb
        return r

    rev, T = [], bestT
    while T:
        found, U = None, T
        while U:
            lb = U & -U
            u = lb.bit_length() - 1
            prev = T ^ lb
            if f[prev] and tabs[u][a[u]][ab(prev & pred[u])]:
                found = u
                break
            U ^= lb
        assert found is not None
        rev.append(found)
        T ^= 1 << found
    order = rev[::-1]
    kept, bs = [], [0] * v
    for t in order:
        bset = 0
        for s in kept:
            if Z[s][t]:
                bset |= 1 << a[s]
        for cand in range(1, 8):
            if cand & ~sg[t] or ((a[t] & cand).bit_count() & 1) == 0:
                continue
            good, x = True, bset
            while x:
                lb = x & -x
                if (((lb.bit_length() - 1) & cand).bit_count() & 1):
                    good = False
                    break
                x ^= lb
            if good:
                bs[t] = cand
                break
        kept.append(t)
    return order, bs


def check_witness(sig, wit):
    """Independent replay of a labelling/order witness. True iff valid."""
    M, pi, sg, Z = sig
    a, b, order = wit["a"], wit["b"], wit["order"]
    if sorted(order) != sorted(set(order)) or not order:
        return False
    for t in order:
        if not (1 <= a[t] <= 7) or (a[t] & ~pi[t]) or (b[t] & ~sg[t]):
            return False
        if (((a[t] & b[t]).bit_count() & 1)) != 1:
            return False
    for i, t in enumerate(order):
        for s in order[i + 1:]:
            if M[t][s] == 0 and (((a[t] & b[s]).bit_count() & 1)) == 1:
                return False
    return True


def hill_climb(sig, tabs, iters=240, seed=5, start=None):
    """Deterministic hill-climb over a-labels with exact completion; returns witness dict."""
    M, pi, sg, Z = sig
    v = len(M)
    rng = random.Random(seed)
    a = list(start) if start else [rng.choice(opts(pi[t])) for t in range(v)]
    best, bestT, bestF = complete(a, pi, sg, Z, v, tabs)
    for _ in range(iters):
        t = rng.randrange(v)
        old = a[t]
        cand = [m for m in opts(pi[t]) if m != old]
        if not cand:
            continue
        a[t] = rng.choice(cand)
        val, T, F = complete(a, pi, sg, Z, v, tabs)
        if val >= best:
            best, bestT, bestF = val, T, F
        else:
            a[t] = old
    order, bs = reconstruct(a, sg, Z, v, tabs, bestT, bestF)
    wit = {"a": a, "b": bs, "order": order}
    assert check_witness(sig, wit), "hill-climb produced an invalid witness"
    return best, wit


def exact_cert(sig, tabs, cap=200000):
    """Exact cert by enumerating all a-labelings, when the product of option
    counts is within cap. Returns (value, exhausted)."""
    M, pi, sg, Z = sig
    v = len(M)
    counts = [len(opts(pi[t])) for t in range(v)]
    total = 1
    for c in counts:
        total *= c
        if total > cap:
            return None, False
    best = 0
    for pick in itertools.product(*[opts(pi[t]) for t in range(v)]):
        val, T, _ = complete(list(pick), pi, sg, Z, v, tabs)
        if val > best:
            best = val
            if val == v:
                break
    return best, True


# ---------------------------------------- zero-digraph machinery (new) ----
def pred_masks_from_Z(Z, v):
    return blockers_pred(Z, v)


def ac_mas_tables(pred, v):
    """acyclic[U] and mas[U] for every subset U of [v] of the digraph given by
    predecessor masks pred[t]. acyclic[U] = some source t of Z[U] with
    acyclic[U \\ {t}]; mas[U] = max size of an acyclic induced subset of U.
    O(v * 2^v) with bit operations."""
    N = 1 << v
    ac = bytearray(N)
    ac[0] = 1
    mas = [0] * N
    mas[0] = 0
    for U in range(1, N):
        ok = 0
        x = U
        while x:
            lb = x & -x
            t = lb.bit_length() - 1
            if (pred[t] & U) == 0 and ac[U ^ lb]:
                ok = 1
                break
            x ^= lb
        ac[U] = ok
        if ok:
            mas[U] = U.bit_count()
        else:
            best, x = 0, U
            while x:
                lb = x & -x
                m = mas[U ^ lb]
                if m > best:
                    best = m
                x ^= lb
            mas[U] = best
    return ac, mas


def mp_exact(sig, mas, mp_cap=5000000):
    """Exact Lemma MP value: max over pivot maps c: [v] -> D(t) (D(t) = pi(t)
    intersect sigma(t)) of sum_i MAS(Z[C_i]), C_i = c^{-1}(i). Returns
    (value, worst_value, nmaps) or (None, None, nmaps) when nmaps > mp_cap."""
    M, pi, sg, Z = sig
    v = len(M)
    Dopts = [pi[t] & sg[t] for t in range(v)]
    counts = []
    for t in range(v):
        dl = [b for b in (1, 2, 4) if Dopts[t] & b]
        counts.append(len(dl))
    nmaps = 1
    for c in counts:
        nmaps *= c
    if nmaps > mp_cap:
        return None, None, nmaps
    best, worst = 0, v
    lists = [[b for b in (1, 2, 4) if Dopts[t] & b] for t in range(v)]
    for pick in itertools.product(*lists):
        c1 = c2 = c3 = 0
        for t, m in enumerate(pick):
            if m == 1:
                c1 |= 1 << t
            elif m == 2:
                c2 |= 1 << t
            else:
                c3 |= 1 << t
        val = mas[c1] + mas[c2] + mas[c3]
        if val > best:
            best = val
        if val < worst:
            worst = val
    return best, worst, nmaps


def omega_mutual(sig):
    """Exact size of the largest mutual-zero clique (both M_ts and M_st zero).
    Lemma RK (a): this is at most 3 for rank-3 decoders with nonzero diagonal."""
    M, pi, sg, Z = sig
    v = len(M)
    mnei = [0] * v
    for t in range(v):
        for s in range(v):
            if s != t and Z[t][s] and Z[s][t]:
                mnei[t] |= 1 << s
    N = 1 << v
    clq = bytearray(N)
    clq[0] = 1
    best = 0
    for U in range(1, N):
        lb = U & -U
        t = lb.bit_length() - 1
        rest = U ^ lb
        if clq[rest] and (mnei[t] & rest) == rest:
            clq[U] = 1
            if U.bit_count() > best:
                best = U.bit_count()
    return best


def chi_exact_dp(pred, v):
    """Exact dichromatic number of the digraph (min number of colors so every
    color class induces an acyclic subdigraph), by subset DP
    chi[S] = 1 + min over nonempty acyclic A subseteq S of chi[S \\ A].
    Exact for v <= 13 (3^v subset pairs)."""
    N = 1 << v
    ac, mas = ac_mas_tables(pred, v)
    chi = [99] * N
    chi[0] = 0
    for S in range(1, N):
        best = 99
        A = S
        while A:
            if ac[A]:
                val = 1 + chi[S ^ A]
                if val < best:
                    best = val
            A = (A - 1) & S
        chi[S] = best
    return chi[N - 1]


def chi_le3_backtrack(pred, v, allowed=None, budget=2000000):
    """Decide whether the digraph is 3-colorable into acyclic classes, with
    optional per-vertex allowed colors (bitmask of {1,2,4}); vertex-by-vertex
    backtracking with incremental acyclicity. Returns (result, exhausted).
    result is None when the node budget is exhausted without a decision."""
    if allowed is None:
        allowed = [7] * v
    order = sorted(range(v), key=lambda t: -((pred[t].bit_count()) +
                                             sum(1 for s in range(v) if s != t and (pred[s] >> t) & 1)))
    cls = [0, 0, 0]
    nodes = [0]
    succ = [[s for s in range(v) if s != t and ((pred[s] >> t) & 1)] for t in range(v)]

    def adds_cycle(t, cmask):
        # cycle through t in Z[cmask | {t}] iff some successor of t inside the
        # class reaches t inside the class
        start = 1 << t
        seen = 0
        stack = [u for u in succ[t] if (cmask >> u) & 1]
        seen = 0
        while stack:
            u = stack.pop()
            if u == t:
                return True
            if (seen >> u) & 1:
                continue
            seen |= 1 << u
            for w in succ[u]:
                if w == t:
                    return True
                if (cmask >> w) & 1 and not ((seen >> w) & 1):
                    stack.append(w)
        return False

    def rec(k):
        nodes[0] += 1
        if nodes[0] > budget:
            return None
        if k == v:
            return True
        t = order[k]
        for bi in (0, 1, 2):
            if not (allowed[t] & (1 << bi)):
                continue
            if adds_cycle(t, cls[bi]):
                continue
            cls[bi] |= 1 << t
            r = rec(k + 1)
            cls[bi] ^= 1 << t
            if r is not None:
                return r
        return False

    r = rec(0)
    return r, nodes[0] > budget


def mutual_pair_count(sig):
    M, pi, sg, Z = sig
    v = len(M)
    return sum(1 for t in range(v) for s in range(t + 1, v) if Z[t][s] and Z[s][t])


def arc_count(sig):
    M, pi, sg, Z = sig
    v = len(M)
    return sum(1 for t in range(v) for s in range(v) if s != t and Z[t][s])


# ---------------------------------------------------- chain / B search ----
def block_rank(rows_mask, Rj, Aj, v):
    cols = [c for c in range(v) if (Aj >> c) & 1]
    mat = []
    for t in range(v):
        if (Rj >> t) & 1:
            row = 0
            for i, c in enumerate(cols):
                if (rows_mask[t] >> c) & 1:
                    row |= 1 << i
            mat.append(row)
    rank = 0
    for i in range(len(cols)):
        piv = None
        for r in range(rank, len(mat)):
            if (mat[r] >> i) & 1:
                piv = r
                break
        if piv is not None:
            mat[rank], mat[piv] = mat[piv], mat[rank]
            for r in range(len(mat)):
                if r != rank and ((mat[r] >> i) & 1):
                    mat[r] ^= mat[rank]
            rank += 1
    return rank


def chain_cost(Brows, pi, sg, v):
    """sum_j rank_F2 B[R_j, A_j]; R_j = {t : j in pi(t)}, A_j = {t : j in sigma(t)}."""
    total = 0
    for j in range(3):
        Rj = sum(1 << t for t in range(v) if (pi[t] >> j) & 1)
        Aj = sum(1 << t for t in range(v) if (sg[t] >> j) & 1)
        total += block_rank(Brows, Rj, Aj, v)
    return total


def min_chain_cost(sig, budget_free=12, local_evals=60, seed=7):
    """Minimum of chain cost over admissible B (0/1, unit diagonal, ones only
    where M vanishes). Exhaustive when the free-pair count is small; otherwise
    deterministic single-bit local search from B = I and random starts. Any B
    found is an admissible upper bound on cert; a B below threshold falsifies
    F-star on that instance via the proven chain cost >= cert(M)."""
    M, pi, sg, Z = sig
    v = len(M)
    free = [(t, s) for t in range(v) for s in range(v) if t != s and Z[t][s]]
    f = len(free)

    def cost_of(bits):
        Brows = [1 << t for t in range(v)]
        for k, (t, s) in enumerate(free):
            if (bits >> k) & 1:
                Brows[t] |= 1 << s
        return chain_cost(Brows, pi, sg, v)

    best_bits = 0
    best = cost_of(0)
    if f <= budget_free:
        for bits in range(1, 1 << f):
            c = cost_of(bits)
            if c < best:
                best, best_bits = c, bits
    else:
        rng = random.Random(seed)
        for start in range(local_evals):
            bits = 0 if start == 0 else rng.getrandbits(f)
            cur = cost_of(bits)
            improved = True
            while improved:
                improved = False
                for k in range(f):
                    nxt = bits ^ (1 << k)
                    c = cost_of(nxt)
                    if c < cur:
                        best, best_bits, cur, improved, bits = c, nxt, c, True, nxt
                    elif c == cur and rng.random() < 0.02:
                        bits, cur = nxt, c
    return best, best_bits


# ---------------------------------------------------------- generators ----
def gen_random(rng, v, box):
    while True:
        P = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        Q = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            return (P, Q), signature(P, Q)


def gen_sparse(rng, v, box):
    """1-2 nonzero coordinates per p(t)/q(t): dense zero digraphs."""
    while True:
        P, Q = [], []
        for _ in range(v):
            p = [0, 0, 0]
            q = [0, 0, 0]
            for arr in (p, q):
                k = rng.choice((1, 2))
                for j in rng.sample((0, 1, 2), k):
                    arr[j] = rng.choice(box)
            P.append(p)
            Q.append(q)
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            return (P, Q), signature(P, Q)


def gen_forced(rng, v, box):
    """Support masks chosen first with small D(t) = pi(t) intersect sigma(t)
    (|D| = 1 on at least half the lines): the pivot map is heavily constrained,
    which is where the matched-pivot value of Lemma MP can lose against the
    unconstrained dichromatic number."""
    sup = [1, 2, 4, 3, 5, 6, 7]
    while True:
        P, Q = [], []
        for _ in range(v):
            psi = rng.choice(sup)
            sgi = rng.choice(sup)
            p = [0, 0, 0]
            q = [0, 0, 0]
            for j in range(3):
                if psi & (1 << j):
                    p[j] = rng.choice(box)
                if sgi & (1 << j):
                    q[j] = rng.choice(box)
            P.append(p)
            Q.append(q)
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            sig = signature(P, Q)
            Ds = [sig[1][t] & sig[2][t] for t in range(v)]
            if sum(1 for d in Ds if d in (1, 2, 4)) >= (v + 1) // 2:
                return (P, Q), sig


def gen_mutual_dense(rng, v, box, tries=60):
    """Rejection sample for many mutual-zero pairs (dense bidirected structure):
    the population where MAS collapses and the 3-class partition is under
    pressure."""
    best_sig = None
    best_mp = -1
    for _ in range(tries):
        (P, Q), sig = gen_sparse(rng, v, box)
        mc = mutual_pair_count(sig)
        if mc >= (v + 1) // 2:
            return (P, Q), sig
        if best_sig is None or mc > best_mp:
            best_sig, best_mp = ((P, Q), sig), mc
    return best_sig


# ------------------------------------------------------------- controls ----
def brute_cert(sig):
    """Definition-level brute force over all labellings; MAS of D_K on V(K)."""
    M, pi, sg, Z = sig
    v = len(M)
    best = 0
    for a in itertools.product(range(8), repeat=v):
        for t in range(v):
            if a[t] & ~pi[t]:
                break
        else:
            for b in itertools.product(range(8), repeat=v):
                for t in range(v):
                    if b[t] & ~sg[t]:
                        break
                else:
                    Vk = [t for t in range(v) if ((a[t] & b[t]).bit_count() & 1)]
                    if len(Vk) <= best:
                        continue
                    n = len(Vk)
                    D = [[0] * n for _ in range(n)]
                    for i, t in enumerate(Vk):
                        for j, s in enumerate(Vk):
                            if t != s and M[t][s] == 0 and ((a[t] & b[s]).bit_count() & 1):
                                D[i][j] = 1
                    pred = [0] * n
                    for i in range(n):
                        for j in range(n):
                            if D[j][i]:
                                pred[i] |= 1 << j
                    _, mas = ac_mas_tables(pred, n)
                    if mas[(1 << n) - 1] > best:
                        best = mas[(1 << n) - 1]
    return best


def load_cfg(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    P = [c[0] for c in cfg]
    Q = [c[1] for c in cfg]
    return (P, Q), signature(P, Q)


def main():
    fails = []
    results = {}

    # ---- controls ----
    log("controls")
    # (1) engine exact-cert vs definition-level brute force on three v = 3 instances
    brute_agree = 0
    for seed in (11, 22, 33):
        (P, Q), sig = gen_random(random.Random(seed), 3, [-1, 0, 1])
        tabs = bfeas_tables(sig[1], sig[2])
        ec, exh = exact_cert(sig, tabs, cap=100000)
        bb = brute_cert(sig)
        if ec == bb:
            brute_agree += 1
        else:
            fails.append(f"brute/engine disagree (seed {seed}): {bb} vs {ec}")

    # (2) diagonal decoder cert = 3
    P3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    sig_diag = signature(P3, P3)
    tabs_diag = bfeas_tables(sig_diag[1], sig_diag[2])
    diag_cert, _ = exact_cert(sig_diag, tabs_diag, cap=100000)
    if diag_cert != 3:
        fails.append(f"diagonal control: cert {diag_cert} != 3")

    # (3) corrupted-witness rejection
    (Pc, Qc), sig_c = gen_random(random.Random(999), 4, [-1, 0, 1])
    tabs_c = bfeas_tables(sig_c[1], sig_c[2])
    _, wit_c = hill_climb(sig_c, tabs_c, iters=60, seed=4)
    if not check_witness(sig_c, wit_c):
        fails.append("checker rejected a true witness")
    corrupt_rejects = 0
    w1 = json.loads(json.dumps(wit_c))
    w1["a"][w1["order"][0]] = 0
    if not check_witness(sig_c, w1):
        corrupt_rejects += 1
    w2 = json.loads(json.dumps(wit_c))
    w2["b"][w2["order"][0]] = 0
    if not check_witness(sig_c, w2):
        corrupt_rejects += 1
    if corrupt_rejects != 2:
        fails.append(f"corrupted witnesses accepted: {2 - corrupt_rejects}/2")

    # (4) subset-DP MAS vs hand values on tiny digraphs
    mas_checks = 0
    # bidirected triangle: MAS = 1
    pred_tri = [0b110, 0b101, 0b011]
    _, mas_tri = ac_mas_tables(pred_tri, 3)
    if mas_tri[7] == 1:
        mas_checks += 1
    else:
        fails.append(f"MAS bidirected triangle {mas_tri[7]} != 1")
    # directed 3-cycle (one direction): MAS = 2
    pred_c3 = [0, 0, 0]
    pred_c3[0] = 1 << 2  # 2 -> 0
    pred_c3[1] = 1 << 0  # 0 -> 1
    pred_c3[2] = 1 << 1  # 1 -> 2
    _, mas_c3 = ac_mas_tables(pred_c3, 3)
    if mas_c3[7] == 2:
        mas_checks += 1
    else:
        fails.append(f"MAS directed 3-cycle {mas_c3[7]} != 2")
    # empty digraph on 4 vertices: MAS = 4
    _, mas_e4 = ac_mas_tables([0, 0, 0, 0], 4)
    if mas_e4[15] == 4:
        mas_checks += 1
    else:
        fails.append(f"MAS empty-4 {mas_e4[15]} != 4")
    if mas_checks != 3:
        fails.append(f"MAS controls {mas_checks}/3")

    # (5) dichromatic numbers on tiny digraphs
    chi_checks = 0
    # bidirected triangle: chi = 3
    if chi_exact_dp(pred_tri, 3) == 3:
        chi_checks += 1
    else:
        fails.append(f"chi bidirected triangle {chi_exact_dp(pred_tri, 3)} != 3")
    # bidirected K4: chi = 4
    pred_k4 = []
    for t in range(4):
        m = 0
        for s in range(4):
            if s != t:
                m |= 1 << s
        pred_k4.append(m)
    if chi_exact_dp(pred_k4, 4) == 4:
        chi_checks += 1
    else:
        fails.append(f"chi bidirected K4 {chi_exact_dp(pred_k4, 4)} != 4")
    # acyclic chain 0 -> 1 -> 2: chi = 1; directed 3-cycle: chi = 2
    pred_chain = [0, 1 << 0, 1 << 1]
    if chi_exact_dp(pred_chain, 3) == 1:
        chi_checks += 1
    else:
        fails.append(f"chi acyclic chain {chi_exact_dp(pred_chain, 3)} != 1")
    if chi_exact_dp(pred_c3, 3) == 2:
        chi_checks += 1
    else:
        fails.append(f"chi directed 3-cycle {chi_exact_dp(pred_c3, 3)} != 2")
    if chi_checks != 4:
        fails.append(f"chi controls {chi_checks}/4")

    # (6) Lemma MP control: diagonal decoder has empty zero digraph, so every
    # pivot partition is acyclic and MP = v exactly
    pred_diag = pred_masks_from_Z(sig_diag[3], 3)
    _, mas_diag = ac_mas_tables(pred_diag, 3)
    mp_v, mp_worst, mp_nmaps = mp_exact(sig_diag, mas_diag)
    if mp_v != 3:
        fails.append(f"MP diagonal control {mp_v} != 3")

    log(f"controls: brute_agree={brute_agree}/3 diagonal_cert={diag_cert} "
        f"corrupt_rejects={corrupt_rejects}/2 mas={mas_checks}/3 chi={chi_checks}/4 "
        f"mp_diagonal={mp_v}")
    results["controls"] = {"brute_agree": brute_agree, "diag_cert": diag_cert,
                           "corrupt_rejects": corrupt_rejects, "mas_checks": mas_checks,
                           "chi_checks": chi_checks, "mp_control": mp_v}
    if not fails:
        print("PASS_FZD_CONTROLS")

    # ---- fixtures: calibration anchors + zero-digraph dichromatic analysis ----
    log("fixtures")
    fixtures = {}
    for name, recorded, anchor_mp in (("tied_min.json", 11, 9),
                                      ("cex_min_1.json", 18, 16)):
        (P, Q), sig = load_cfg(name)
        M, pi, sg, Z = sig
        v = len(M)
        thr = threshold(v)
        pred = pred_masks_from_Z(Z, v)
        t_ac = time.time()
        ac, mas = ac_mas_tables(pred, v)
        log(f"{name}: subset DP done ({time.time() - t_ac:.1f}s)")
        mp_v, mp_worst, mp_nmaps = mp_exact(sig, mas)
        if mp_v != anchor_mp:
            fails.append(f"{name}: MP {mp_v} != PR 2747 anchor {anchor_mp}")
        # engine witness: tied_min re-found by hill-climb; cex_min_1 stored replay
        tabs = bfeas_tables(pi, sg)
        if name == "tied_min.json":
            wit_val, wit = hill_climb(sig, tabs, iters=400, seed=9)
            if wit_val < recorded:
                fails.append(f"{name}: engine witness {wit_val} < recorded {recorded}")
            if not check_witness(sig, wit):
                fails.append(f"{name}: hill-climb witness failed replay")
        else:
            with open(os.path.join(DATA, "cex_min_1.witness.json"), "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if not check_witness(sig, stored):
                fails.append("cex_min_1 stored witness failed replay")
            wit_val = len(stored["order"])
        # chain engine anchor: PR 2111 stored cost-22 pairing on cex_min_1
        chain_anchor = None
        if name == "cex_min_1.json":
            with open(os.path.join(DATA, "cex_min_1.B22.json"), "r", encoding="utf-8") as fh:
                B22 = json.load(fh)
            rows = [0] * v
            for t in range(v):
                for s in range(v):
                    if B22[t][s]:
                        rows[t] |= 1 << s
            adm = all(B22[t][t] == 1 for t in range(v)) and all(
                B22[t][s] == 0 or Z[t][s]
                for t in range(v) for s in range(v) if t != s)
            chain_anchor = chain_cost(rows, pi, sg, v)
            if chain_anchor != 22 or not adm:
                fails.append(f"{name}: chain engine {chain_anchor} (admissible={adm}) != 22")
        # dichromatic analysis (new): constrained value = MP; unconstrained chi
        if v <= 13:
            chi_val = chi_exact_dp(pred, v)
            chi_exh = True
        else:
            r, exh_budget = chi_le3_backtrack(pred, v, budget=300000)
            chi_val = ("le3" if r else ("gt3" if r is False else "unknown"))
            chi_exh = not exh_budget
        om = omega_mutual(sig)
        fixtures[name] = {
            "v": v, "threshold": thr, "mp_bound": mp_v, "mp_worst": mp_worst,
            "mp_maps": mp_nmaps, "mp_anchor": anchor_mp,
            "engine_witness": wit_val, "recorded_cert": recorded,
            "chain_anchor": chain_anchor,
            "mas_of_Z": mas[(1 << v) - 1], "omega_mutual": om,
            "chi_unconstrained": chi_val, "chi_exhaustive": chi_exh,
            "mp_deficit_vs_v": v - mp_v,
            "dichromatic_with_D": (mp_v == v),
            "arcs_Z": arc_count(sig), "mutual_pairs": mutual_pair_count(sig),
        }
        log(f"{name}: v={v} thr={thr} MP={mp_v} (anchor {anchor_mp}, maps {mp_nmaps}) "
            f"witness={wit_val} chi={chi_val} omega={om} MAS(Z)={mas[(1 << v) - 1]}")
    results["fixtures"] = fixtures
    if not fails:
        print("PASS_FZD_FIXTURES")

    # ---- search: class (ii), smallest falsifying instance first ----
    log("search (smallest first)")
    search_records = []
    falsifiers = []
    min_mp_ratio = None
    min_wit_ratio = None
    worst_mp = None
    non3d_count = 0
    chi4_found = []
    for v in range(3, 13):
        thr = threshold(v)
        plans = []
        n_rand = 16 if v <= 6 else (8 if v <= 9 else 4)
        plans.append(("random", gen_random, n_rand, [-1, 0, 1]))
        plans.append(("random2", gen_random, max(3, n_rand // 2), [-2, -1, 0, 1, 2]))
        plans.append(("sparse", gen_sparse, max(3, n_rand // 2), [-2, -1, 1, 2]))
        plans.append(("forced", gen_forced, max(3, n_rand // 2), [-2, -1, 1, 2]))
        if v >= 4:
            plans.append(("mutual", gen_mutual_dense, 3, [-2, -1, 1, 2]))
        for fam, gen, n_inst, box in plans:
            for k in range(n_inst):
                seed = 1000 * v + 97 * k + sum(ord(ch) for ch in fam)
                rng = random.Random(seed)
                if fam == "mutual":
                    got = gen(rng, v, box)
                else:
                    got = gen(rng, v, box)
                (P, Q), sig = got
                M, pi, sg, Z = sig
                pred = pred_masks_from_Z(Z, v)
                ac, mas = ac_mas_tables(pred, v)
                mp_v, mp_worst, mp_nmaps = mp_exact(sig, mas, mp_cap=300000)
                rec = {"family": fam, "v": v, "seed": seed, "thr": thr,
                       "arcs": arc_count(sig), "mutual_pairs": mutual_pair_count(sig),
                       "omega": omega_mutual(sig),
                       "mas_Z": mas[(1 << v) - 1], "mp": mp_v, "mp_worst": mp_worst,
                       "mp_maps": mp_nmaps}
                if mp_v is not None and mp_v < v:
                    non3d_count += 1
                    rec["non3dichro_with_D"] = True
                # unconstrained chi
                r, exh_budget = chi_le3_backtrack(pred, v, budget=60000)
                rec["chi_status"] = "le3" if r else ("gt3" if r is False else "unknown")
                rec["chi_gt3"] = (r is False)
                if r is False and len(chi4_found) < 5:
                    chi4_found.append({"family": fam, "v": v, "seed": seed})
                # engine / falsifier side
                tabs = bfeas_tables(pi, sg)
                prod = 1
                for t in range(v):
                    prod *= len(opts(pi[t]))
                if prod <= 60000:
                    ec, _ = exact_cert(sig, tabs, cap=60000)
                    rec["cert_exact"] = ec
                    wit_val = ec
                else:
                    iters = 60 if v <= 10 else 25
                    wit_val, wit = hill_climb(sig, tabs, iters=iters, seed=seed % 97)
                    rec["witness"] = wit_val
                if wit_val is not None:
                    ratio = wit_val / v
                    if min_wit_ratio is None or ratio < min_wit_ratio:
                        min_wit_ratio = ratio
                chain_up, _ = min_chain_cost(sig, local_evals=40, seed=seed % 89)
                rec["chain_upper"] = chain_up
                if mp_v is not None:
                    ratio = mp_v / v
                    if min_mp_ratio is None or ratio < min_mp_ratio:
                        min_mp_ratio = ratio
                    if mp_v < thr:
                        rec["mp_below_threshold"] = True
                    if worst_mp is None or (mp_v - thr) < (worst_mp[0] - threshold(worst_mp[1])):
                        worst_mp = (mp_v, v, fam, seed)
                # falsifier test (early kill)
                fals = None
                if rec.get("cert_exact") is not None and rec["cert_exact"] < thr:
                    fals = "exact_cert_below_threshold"
                elif chain_up < thr:
                    fals = "chain_cost_below_threshold"
                if fals:
                    rec["FALSIFIER"] = fals
                    falsifiers.append(rec)
                    search_records.append(rec)
                    log(f"FALSIFIER {fals}: v={v} fam={fam} seed={seed} "
                        f"cert={rec.get('cert_exact')} chain={chain_up} thr={thr}")
                    break
                if len(search_records) < 1000:
                    search_records.append(rec)
            if falsifiers:
                break
        log(f"v={v} done (records so far {len(search_records)}, "
            f"non3dichro-with-D {non3d_count})")
        if falsifiers:
            break
    mp_below = sum(1 for r in search_records if r.get("mp_below_threshold"))
    chi_le3 = sum(1 for r in search_records if r.get("chi_status") == "le3")
    chi_unknown = sum(1 for r in search_records if r.get("chi_status") == "unknown")
    log(f"search: {len(search_records)} instances, falsifiers={len(falsifiers)}, "
        f"min_mp_ratio={min_mp_ratio}, min_witness_ratio={min_wit_ratio}, "
        f"non3d_with_D={non3d_count}, chi4={len(chi4_found)}, mp_below_thr={mp_below}, "
        f"chi_le3={chi_le3}, chi_unknown={chi_unknown}")
    if worst_mp is not None:
        log(f"worst MP margin: mp={worst_mp[0]} v={worst_mp[1]} fam={worst_mp[2]} "
            f"seed={worst_mp[3]} (floor(2v/3)={threshold(worst_mp[1])})")
    results["search"] = {
        "instances": len(search_records), "falsifiers": len(falsifiers),
        "min_mp_ratio": min_mp_ratio, "min_witness_ratio": min_wit_ratio,
        "non3dichro_with_D": non3d_count,
        "chi4_found": chi4_found,
        "chi_le3_count": chi_le3, "chi_unknown_count": chi_unknown,
        "mp_below_threshold_count": mp_below,
        "worst_mp": worst_mp,
    }
    if not fails and not falsifiers:
        print("PASS_FZD_SEARCH")
    elif falsifiers:
        print(f"PASS_FZD_SEARCH_FALSIFIER {falsifiers[0]['FALSIFIER']}")

    # ---- certificate ----
    if falsifiers:
        outcome = "FALSIFIER_FOUND"
    else:
        outcome = "NO_FALSIFIER_IN_DOMAIN"
    cert = {"outcome": outcome, "results": results,
            "worst_instances": sorted(
                [r for r in search_records if r.get("mp") is not None],
                key=lambda r: (r["mp"] - r["thr"]))[:8],
            "non3d_records": [r for r in search_records if r.get("non3dichro_with_D")],
            "search_records_head": search_records[:40]}
    digest = hashlib.sha256(
        json.dumps(cert, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    cert["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
    log(f"certificate digest {digest}")

    if fails:
        for f in fails:
            print("FAIL:", f)
        print("FAIL_FSTAR_ZERO_DIGRAPHS")
        return 1
    print("PASS_FSTAR_ZERO_DIGRAPHS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
