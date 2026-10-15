#!/usr/bin/env python3
"""Tied-residue checks for open problem F-star: anchor classification, the mixed
anchor-repair-pivot lemma (Lemma MX) with machine-checked witnesses, calibration
on PR 2111's stored fixtures, and a smallest-first bounded falsifier search in
the tied-minimum / isotropic domain. Stdlib only, deterministic. Part of
research/fstar-tied-residue-seeddcc97691.

Model (research/root-unit-decoder-lemmas section 7; PR 2111 section 1): a
T = 3 decoder is M = sum_{j=1..3} p_j q_j^T over Q on v lines with M_tt != 0.
Row support pi(t) = {j : p_j(t) != 0}, column support sigma(t) = {j : q_j(t)
!= 0}. An L8 labelling is F2 vectors a(t) supported in pi(t), b(t) supported
in sigma(t), K_ts = a(t) . b(s) mod 2. cert(M) is the largest |S| admitting an
order with K_tt = 1 on S and K_ts = 0 at every incidence M_ts = 0 with t before
s (t, s in S).

Engine and witness checker adapted from Aaron Wang's PR 2717
(research/fstar-proof-lemmas-seed3096ed3f/verify.py): for fixed a-labels the
(b-labels, order, kept set) completion is exact by subset DP. New here: the
per-line anchor/residue classification, the Lemma MX construction (anchor
labels on A, one-sided repairs on U, matched pivots on T with the A+U-first
order), its exact per-instance evaluation over pivot maps, and the tied-domain
generators and search.
"""
import hashlib
import itertools
import json
import os
import random
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.2f}s] {msg}")


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


# ------------------------------------------------- anchor / residue ----
def anchor_labels(P, Q):
    v = len(P)
    a0 = [sum(1 << j for j in range(3) if P[t][j] % 2 != 0) for t in range(v)]
    b0 = [sum(1 << j for j in range(3) if Q[t][j] % 2 != 0) for t in range(v)]
    return a0, b0


def classify_line(sig, a0, b0, t):
    """anchor_good: K0_tt = 1 (M_tt odd). repairable_1s: K0_tt = 0 but some
    a* inside pi(t) gives a* . b0(t) = 1 and a* . b0(s) = 0 at every incidence
    M_ts = 0 (b fixed at b0, full one-sided repair). tied_isotropic: neither
    (the stated residue of PR 2717 / root-unit-decoder-lemmas section 7)."""
    M, pi, sg, Z = sig
    v = len(M)
    if ((a0[t] & b0[t]).bit_count() & 1) == 1:
        return "anchor_good"
    for a_star in opts(pi[t]):
        if ((a_star & b0[t]).bit_count() & 1) == 0:
            continue
        good = True
        for s in range(v):
            if s != t and M[t][s] == 0 and ((a_star & b0[s]).bit_count() & 1):
                good = False
                break
        if good:
            return "repairable_1s"
    return "tied_isotropic"


def classify(sig, a0, b0):
    M = sig[0]
    v = len(M)
    return [classify_line(sig, a0, b0, t) for t in range(v)]


# ------------------------------------------- MAS and digraph utilities ----
def mas_masks(out, v, allowed):
    """Exact maximum induced acyclic subset of the digraph (out-adjacency masks
    out[t]) restricted to `allowed`; returns (size, subset mask, unused).
    Subsets of `allowed` are enumerated in compressed increasing order so every
    DP predecessor is processed first. Results are memoized on (allowed, out)
    — pivot maps repeat partitions."""
    key = (allowed, tuple(out))
    hit = _MAS_CACHE.get(key)
    if hit is not None:
        return hit
    verts = [t for t in range(v) if (allowed >> t) & 1]
    m = len(verts)
    out_c = [0] * m
    for i, t in enumerate(verts):
        cm = 0
        for j, s in enumerate(verts):
            if (out[t] >> s) & 1:
                cm |= 1 << j
        out_c[i] = cm
    acyc = bytearray(1 << m)
    acyc[0] = 1
    best, bestT_c = 0, 0
    for T in range(1, 1 << m):
        u, ok = T, 0
        while u:
            lb = u & -u
            i = lb.bit_length() - 1
            prev = T ^ lb
            if acyc[prev] and (out_c[i] & prev) == 0:
                ok = 1
                break
            u ^= lb
        acyc[T] = ok
        if ok and T.bit_count() > best:
            best, bestT_c = T.bit_count(), T
    bestT = 0
    for i, t in enumerate(verts):
        if (bestT_c >> i) & 1:
            bestT |= 1 << t
    res = (best, bestT, None)
    _MAS_CACHE[key] = res
    return res


def topo_backward(sub, out):
    """Order of `sub` with every internal out-edge pointing backward: sinks first."""
    order = []
    remaining = sub
    while remaining:
        found = None
        u = remaining
        while u:
            lb = u & -u
            t = lb.bit_length() - 1
            if (out[t] & remaining) == 0:
                found = t
                break
            u ^= lb
        assert found is not None, "subgraph must be acyclic"
        order.append(found)
        remaining ^= 1 << found
    return order


# ------------------------------------------ Lemma MX construction ----
_MAS_CACHE = {}


def mx_bound(sig, a0, b0, c_map, classes, mode="A_first"):
    """Lemma MX construction (two order forms). classes: per line one of 'A'
    (anchor label), 'U' (one-sided repair attempt), 'T' (matched pivot with
    c_map[t] in D(t) as a unit mask), 'X' (excluded from the kept set).

    A_first order: A + U before the pivot block; exact hypotheses: every U line
    admits a one-sided repair killing its A + U blockers (b0 labels) and its T
    blockers (pivot bits), and A -> T conflicts vanish (a0(t) has no bit c(s)
    at incidences t in A, s in T).
    T_first order: the pivot block before A + U; exact hypotheses: every U line
    admits a one-sided repair killing its A + U blockers, and T -> (A + U)
    conflicts vanish (b0(s) has no bit c(t) at incidences t in T, s in A + U).

    In both forms the kept set is all of A and U plus per-class MAS subsets of
    T, so the bound is |A| + |U| + sum_i MAS(Z[C_i]) with C_i = {t in T :
    c_map[t] = 1<<i}. Every returned witness is replayed by check_witness
    before it is accepted; failure returns (None, reason)."""
    M, pi, sg, Z = sig
    v = len(M)
    A = [t for t in range(v) if classes[t] == "A"]
    U = [t for t in range(v) if classes[t] == "U"]
    T = [t for t in range(v) if classes[t] == "T"]
    for t in A:
        if ((a0[t] & b0[t]).bit_count() & 1) != 1:
            return None, "A line not anchor-good"
    for t in T:
        if not (c_map[t] & (pi[t] & sg[t])):
            return None, "T pivot outside D(t)"
    a_lab = {t: a0[t] for t in A}
    b_lab = {t: b0[t] for t in A + U}
    for t in U:
        found = None
        for a_star in opts(pi[t]):
            if ((a_star & b0[t]).bit_count() & 1) == 0:
                continue
            good = True
            for s in A + U:
                if s != t and M[t][s] == 0 and ((a_star & b0[s]).bit_count() & 1):
                    good = False
                    break
            if good and mode == "A_first":
                for s in T:
                    if M[t][s] == 0 and (a_star & c_map[s]):
                        good = False
                        break
            if good:
                found = a_star
                break
        if found is None:
            return None, f"U line {t} has no admissible one-sided repair"
        a_lab[t] = found
    if mode == "A_first":
        for t in A:
            for s in T:
                if M[t][s] == 0 and (a0[t] & c_map[s]):
                    return None, f"A->T conflict at ({t},{s})"
    elif mode == "T_first":
        for t in T:
            for s in A + U:
                if M[t][s] == 0 and (b0[s] & c_map[t]):
                    return None, f"T->AU conflict at ({t},{s})"
    else:
        return None, f"unknown mode {mode}"
    outT = [0] * v
    for t in T:
        for s in T:
            if t != s and M[t][s] == 0 and c_map[t] == c_map[s]:
                outT[t] |= 1 << s
    kept_T = []
    for i in (1, 2, 4):
        allowed = sum(1 << t for t in T if c_map[t] == i)
        if not allowed:
            continue
        sz, sub, _ = mas_masks(outT, v, allowed)
        kept_T.extend(topo_backward(sub, outT))
        for t in range(v):
            if (sub >> t) & 1:
                a_lab[t] = c_map[t]
                b_lab[t] = c_map[t]
    order = (A + U + kept_T) if mode == "A_first" else (kept_T + A + U)
    for t in T:
        if t in a_lab:
            continue
        a_lab[t] = c_map[t]
        b_lab[t] = c_map[t]
    wit = {"a": [a_lab.get(t, 1) for t in range(v)],
           "b": [b_lab.get(t, 1) for t in range(v)],
           "order": order}
    if not check_witness(sig, wit):
        return None, "constructed witness failed independent replay"
    return len(order), wit


def pivot_maps(sig, budget, seed=3):
    """Pivot maps c: [v] -> {1,2,3} with c(t) in D(t) = pi(t) & sg(t). Exhaustive
    when the product of |D(t)| is within budget; otherwise a deterministic sample."""
    M, pi, sg, Z = sig
    v = len(M)
    D = [pi[t] & sg[t] for t in range(v)]
    # pivot values are F2 unit masks: 1, 2, 4 (not class indices 1..3)
    choices = [[1 << i for i in range(3) if (D[t] >> i) & 1] for t in range(v)]
    total = 1
    for c in choices:
        total *= len(c)
        if total > budget:
            rng = random.Random(seed)
            out = []
            for _ in range(budget):
                out.append({t: rng.choice(choices[t]) for t in range(v)})
            return out, False
    maps = []
    for pick in itertools.product(*choices):
        maps.append({t: pick[t] for t in range(v)})
    return maps, True


def mp_bound(sig, tabs, maps):
    """Matched-pivot certificate (Lemma MP of PR 2717): cert >= sum_i MAS(Z[C_i]).
    Achieved value over the given pivot maps, with the witnessing labelling."""
    M, pi, sg, Z = sig
    v = len(M)
    best, bestWit = 0, None
    for c_map in maps:
        out = [0] * v
        for t in range(v):
            for s in range(v):
                if t != s and M[t][s] == 0 and c_map[t] == c_map[s]:
                    out[t] |= 1 << s
        total, kept = 0, []
        for i in (1, 2, 4):
            allowed = sum(1 << t for t in range(v) if c_map[t] == i)
            if not allowed:
                continue
            sz, sub, _ = mas_masks(out, v, allowed)
            total += sz
            kept.extend(topo_backward(sub, out))
        if total > best:
            best = total
            a = [c_map[t] for t in range(v)]
            bestWit = {"a": a, "b": list(a), "order": kept}
    if bestWit is not None and not check_witness(sig, bestWit):
        return 0, None, "MP witness failed replay"
    return best, bestWit, None


def mx_search(sig, a0, b0, classes, maps):
    """Lemma MX achieved bound: maximized over the two order forms and three
    class variants (as given; U demoted to T; all lines pivoted = Lemma MP).
    The all-T variant makes the result always at least the matched-pivot
    certificate. Returns (bound, witness, map, meta, failures)."""
    best, bestWit, bestMap, bestMeta = 0, None, None, None
    fails = {}
    has_U = any(c == "U" for c in classes)
    has_AU = has_U or any(c == "A" for c in classes)
    variants = [("given", list(classes))]
    if has_U:
        variants.append(("A/T", ["A" if c == "A" else "T" for c in classes]))
    variants.append(("allT", ["T" if c != "X" else "X" for c in classes]))
    for vname, vcls in variants:
        modes = ("A_first", "T_first") if (has_AU and vname != "allT") else ("A_first",)
        for mode in modes:
            for c_map in maps:
                val, res = mx_bound(sig, a0, b0, c_map, vcls, mode)
                if val is None:
                    key = res.split(" at ")[0]
                    fails[f"{vname}/{mode}: {key}"] = fails.get(f"{vname}/{mode}: {key}", 0) + 1
                elif val > best:
                    best, bestWit, bestMap = val, res, c_map
                    bestMeta = {"variant": vname, "mode": mode}
    return best, bestWit, bestMap, bestMeta, fails


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


def min_chain_cost(sig, budget_free=12, local_evals=200, seed=7):
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
def _tied_line(rng, tied_count):
    """One line with exactly `tied_count` coordinates carrying odd values in
    both p and q (tied minimal valuations at level 0) and all remaining
    coordinates carrying at least one even factor (so their product is even).
    M_tt = sum of tied_count signed ones plus an even remainder."""
    while True:
        coords = [0, 1, 2]
        rng.shuffle(coords)
        S = coords[:tied_count]
        P, Q = [0, 0, 0], [0, 0, 0]
        for j in S:
            P[j] = rng.choice([-1, 1])
            Q[j] = rng.choice([-1, 1])
        for j in coords[tied_count:]:
            P[j] = rng.choice([-2, -1, 1, 2])
            Q[j] = rng.choice([-2, -1, 1, 2])
            if P[j] % 2 != 0 and Q[j] % 2 != 0:
                Q[j] = 2 * rng.choice([-1, 1])
        if sum(P[j] * Q[j] for j in range(3)) != 0:
            return P, Q


def gen_tied_isotropic(rng, v):
    """All-diagonal-even decoders with exactly two tied minimal valuations on
    every line: the mod-2 anchor is isotropic on every line (K0_tt = 0 with two
    tied odd products). This is PR 2717's tied-heavy idea pushed to the
    maximal-tie residue: PR 2717 tied on half its lines, this family ties on
    all of them (the anchor contributes nothing)."""
    P, Q = [], []
    for _ in range(v):
        p, q = _tied_line(rng, 2)
        P.append(p)
        Q.append(q)
    return (P, Q), signature(P, Q)


def gen_mixed(rng, v):
    """Half the lines have a unique minimal valuation (anchor-good, M_tt odd),
    half have two tied minima (isotropic): the mixed residue where Lemma AN's
    anchor and the tied obstruction coexist."""
    P, Q = [], []
    n_good = max(1, v // 2)
    for t in range(v):
        p, q = _tied_line(rng, 1 if t < n_good else 2)
        P.append(p)
        Q.append(q)
    return (P, Q), signature(P, Q)


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
                    out = [0] * n
                    for i in range(n):
                        for j in range(n):
                            if D[i][j]:
                                out[i] |= 1 << j
                    sz, _, _ = mas_masks(out, n, (1 << n) - 1)
                    if sz > best:
                        best = sz
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
    # engine exact-cert vs definition-level brute force on three v = 3 instances
    brute_agree = 0
    for seed in (11, 22, 33):
        (P, Q), sig = gen_instance(random.Random(seed), 3, -1, 1)
        tabs = bfeas_tables(sig[1], sig[2])
        ec, exh = exact_cert(sig, tabs, cap=100000)
        bb = brute_cert(sig)
        if ec == bb:
            brute_agree += 1
        else:
            fails.append(f"brute/engine disagree (seed {seed}): {bb} vs {ec}")

    P3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    sig_diag = signature(P3, P3)
    tabs_diag = bfeas_tables(sig_diag[1], sig_diag[2])
    diag_cert, _ = exact_cert(sig_diag, tabs_diag, cap=100000)
    if diag_cert != 3:
        fails.append(f"diagonal control: cert {diag_cert} != 3")

    (Pc, Qc), sig_c = gen_instance(random.Random(999), 4, -1, 1)
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

    # Lemma MX special cases must reproduce AN and MP on controls
    (Pm, Qm), sig_m = gen_instance(random.Random(7), 5, -2, 2)
    a0m, b0m = anchor_labels(Pm, Qm)
    cls_m = classify(sig_m, a0m, b0m)
    maps_m, _ = pivot_maps(sig_m, budget=3000)
    mp_v, mp_wit, mp_err = mp_bound(sig_m, bfeas_tables(sig_m[1], sig_m[2]), maps_m)
    if mp_err:
        fails.append(f"MP control error: {mp_err}")
    elif mp_wit is not None and not check_witness(sig_m, mp_wit):
        fails.append("MP control witness failed replay")
    an_count = sum(1 for t in range(5) if cls_m[t] == "anchor_good")
    classes_allA = ["A" if cls_m[t] == "anchor_good" else "X" for t in range(5)]
    val_allA, wit_allA = mx_bound(sig_m, a0m, b0m, maps_m[0], classes_allA)
    if val_allA != an_count:
        fails.append(f"MX all-anchor special case {val_allA} != AN count {an_count}")
    elif not check_witness(sig_m, wit_allA):
        fails.append("MX all-anchor witness failed replay")
    classes_allT = ["T"] * 5
    val_allT, wit_allT = mx_bound(sig_m, a0m, b0m, maps_m[0], classes_allT)
    if val_allT is not None and not check_witness(sig_m, wit_allT):
        fails.append("MX all-pivot witness failed replay")
    log(f"controls: brute_agree={brute_agree}/3 diagonal_cert={diag_cert} "
        f"corrupt_rejects={corrupt_rejects}/2 mx_an={val_allA}/{an_count} "
        f"mp_control={mp_v}")
    if brute_agree != 3:
        fails.append(f"brute/engine agreement {brute_agree}/3")
    results["controls"] = {"brute_agree": brute_agree, "diag_cert": diag_cert,
                           "corrupt_rejects": corrupt_rejects,
                           "mx_all_anchor": val_allA, "an_count": an_count,
                           "mp_control": mp_v}
    if not fails:
        print("PASS_FSTARTIED_CONTROLS")

    # ---- fixtures: tied_min and cex_min_1 ----
    log("fixtures")
    fixtures = {}
    for name, recorded in (("tied_min.json", 11), ("cex_min_1.json", 18)):
        (P, Q), sig = load_cfg(name)
        M, pi, sg, Z = sig
        v = len(M)
        a0, b0 = anchor_labels(P, Q)
        cls = classify(sig, a0, b0)
        an_bound = sum(1 for t in range(v) if cls[t] == "anchor_good")
        tabs = bfeas_tables(pi, sg)
        maps, exh = pivot_maps(sig, budget=20000)
        mp_v, mp_wit, mp_err = mp_bound(sig, tabs, maps)
        # MX: A = anchor_good, U = repairable_1s (repair test is inside mx_bound),
        # T = tied_isotropic and any U line whose repair fails (auto-demoted).
        classes = ["A" if cls[t] == "anchor_good" else
                   ("U" if cls[t] == "repairable_1s" else "T") for t in range(v)]
        mx_v, mx_wit, mx_map, mx_meta, mx_fails = mx_search(sig, a0, b0, classes, maps)
        wit_val, wit = hill_climb(sig, tabs, iters=400, seed=9)
        if name == "cex_min_1.json":
            with open(os.path.join(DATA, "cex_min_1.witness.json"), "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if not check_witness(sig, stored):
                fails.append("cex_min_1 stored witness failed replay")
            wit_val = max(wit_val, len(stored["order"]))
        if wit_val < recorded:
            fails.append(f"{name}: engine witness {wit_val} < recorded {recorded}")
        fixtures[name] = {
            "v": v, "threshold": threshold(v), "diag_odd": an_bound,
            "classification": {k: cls.count(k) for k in
                               ("anchor_good", "repairable_1s", "tied_isotropic")},
            "an_bound": an_bound, "mp_bound": mp_v, "mp_exhaustive": exh,
            "mx_bound": mx_v, "mx_meta": mx_meta, "mx_map": mx_map,
            "mx_failures": mx_fails,
            "engine_witness": wit_val, "recorded_cert": recorded,
            "fstar_holds": wit_val >= threshold(v),
        }
        log(f"{name}: v={v} thr={threshold(v)} AN={an_bound} MP={mp_v} "
            f"MX={mx_v} witness={wit_val} cls={fixtures[name]['classification']}")
        for tag, w in (("mp", mp_wit), ("mx", mx_wit)):
            if w is not None and not check_witness(sig, w):
                fails.append(f"{name}: {tag} witness failed replay")
    results["fixtures"] = fixtures
    if not fails:
        print("PASS_FSTARTIED_FIXTURES")

    # ---- Lemma MX summary marker ----
    if all(fixtures[k]["mx_bound"] >= fixtures[k]["threshold"] for k in fixtures):
        print("PASS_FSTARTIED_MX")
    else:
        fails.append("MX bound below threshold on a fixture")

    # ---- search: tied residue, smallest falsifying instance first ----
    log("search (smallest first)")
    search_records = []
    falsifiers = []
    min_ratio = None
    worst = None
    for v in range(3, 13):
        thr = threshold(v)
        for fam, gen in (("tied_isotropic", gen_tied_isotropic),
                         ("mixed", gen_mixed)):
            n_inst = 2
            for k in range(n_inst):
                (P, Q), sig = gen(random.Random(1000 * v + 37 * k + (0 if fam == "tied_isotropic" else 1)), v)
                M, pi, sg, Z = sig
                a0, b0 = anchor_labels(P, Q)
                cls = classify(sig, a0, b0)
                an_bound = sum(1 for t in range(v) if cls[t] == "anchor_good")
                tabs = bfeas_tables(pi, sg)
                # exact cert when cheap, else hill-climb witness
                ec, exh = exact_cert(sig, tabs, cap=120000)
                wit_val, wit = hill_climb(sig, tabs, iters=300 if v <= 8 else 200, seed=13)
                val = ec if exh else wit_val
                maps, mexh = pivot_maps(sig, budget=800)
                mp_v, mp_wit, mp_err = mp_bound(sig, tabs, maps)
                classes = ["A" if cls[t] == "anchor_good" else
                           ("U" if cls[t] == "repairable_1s" else "T") for t in range(v)]
                mx_v, mx_wit, mx_map, mx_meta, mx_fails = mx_search(sig, a0, b0, classes, maps)
                cb, _ = min_chain_cost(sig, budget_free=12, local_evals=120, seed=17)
                rec = {"family": fam, "v": v, "k": k, "threshold": thr,
                       "exact": exh, "cert_or_witness": val,
                       "an_bound": an_bound, "mp_bound": mp_v, "mx_bound": mx_v,
                       "mx_meta": mx_meta, "chain_cost_upper": cb,
                       "classification": {key: cls.count(key) for key in
                                          ("anchor_good", "repairable_1s", "tied_isotropic")},
                       "mx_failures": mx_fails}
                search_records.append(rec)
                ratio = val / v
                if min_ratio is None or ratio < min_ratio:
                    min_ratio, worst = ratio, rec
                if cb < thr:
                    falsifiers.append(rec)
                    log(f"FALSIFIER at v={v} family={fam} k={k}: chain cost {cb} < {thr}")
                if not exh and val < thr:
                    log(f"unresolved below threshold at v={v} {fam} k={k}: witness {val} < {thr}")
        log(f"v={v} done: {sum(1 for r in search_records if r['v'] == v)} instances")
    n = len(search_records)
    results["search"] = {
        "instances": n, "falsifiers": len(falsifiers),
        "min_witness_ratio": None if min_ratio is None else round(min_ratio, 4),
        "worst": worst,
        "exact_decided": sum(1 for r in search_records if r["exact"]),
        "mx_below_threshold": sum(1 for r in search_records
                                  if r["mx_bound"] < r["threshold"]),
        "mp_below_threshold": sum(1 for r in search_records
                                  if r["mp_bound"] < r["threshold"]),
        "mx_strictly_above_mp": sum(1 for r in search_records
                                    if r["mx_bound"] > r["mp_bound"]),
        "records": search_records,
    }
    log(f"search: {n} instances, falsifiers={len(falsifiers)}, "
        f"min witness ratio={results['search']['min_witness_ratio']}, "
        f"exact-decided={results['search']['exact_decided']}, "
        f"MX below threshold on {results['search']['mx_below_threshold']}")
    if falsifiers:
        fails.append(f"{len(falsifiers)} falsifier(s) found — F-star refuted on the searched domain")
    if not fails:
        print("PASS_FSTARTIED_SEARCH")

    # ---- certificate ----
    digest = hashlib.sha256(
        json.dumps(results, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    results["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True, default=str)
    log(f"certificate digest {digest}")
    if fails:
        for f in fails:
            print("FAIL:", f)
        raise SystemExit(1)
    print("PASS_FSTAR_TIED_RESIDUE")


def gen_instance(rng, v, lo, hi):
    while True:
        P = [[rng.randint(lo, hi) for _ in range(3)] for _ in range(v)]
        Q = [[rng.randint(lo, hi) for _ in range(3)] for _ in range(v)]
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            M, pi, sg, Z = signature(P, Q)
            return (P, Q), (M, pi, sg, Z)


if __name__ == "__main__":
    main()
