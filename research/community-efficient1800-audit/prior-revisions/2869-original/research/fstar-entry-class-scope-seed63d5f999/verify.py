#!/usr/bin/env python3
"""F-star residue class (iii): the exact entry-class scope of Lemma AN / Lemma MX.

Exact stdlib computation over rank-3 rational decoders M = sum_j p_j q_j^T.
New scope machinery: the per-total 2-adic contents c_j and gamma = min_j c_j;
the exact mod-2 anchor reach S_gamma = {t : v_2(M_tt) = gamma} after the
scale-invariant normalization (Lemma SC/SG); entry-class classification
(integer / dyadic / 2-integral odd-denominator / general Q); the mixed
anchor+pivot Lemma-MX values with A = S_gamma; and a smallest-first falsifier
search over entry classes with even and odd denominators.

Engine credit: the model (signature/opts), the exact-completion engine
(bfeas_tables/blockers_pred/complete/reconstruct), the independent witness
checker, hill_climb/exact_cert, the chain machinery (block_rank/chain_cost/
min_chain_cost) and the zero-digraph machinery (ac_mas_tables/mp_exact/
chi_exact_dp/chi_le3_backtrack/omega_mutual) are adapted from Aaron Wang's
PR 2774 research/fstar-zero-digraph-residue-seede9937f18, PR 2747
research/fstar-tied-residue-seeddcc97691 and PR 2717
research/fstar-proof-lemmas-seed3096ed3f, which adapt DreamingOfClouds'
PR 2111 rank-3 model. New in this file: v2/contents/gamma, anchor_labels
(scale-invariant mod-2 reduction), scope identity checks, reach witnesses,
mx_anchor_pivot (Lemma MX with U = empty and A = S_gamma), the entry-class
generators and the scope controls. Apache-2.0.
"""

import hashlib
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction

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


# ---------------------------------------- zero-digraph machinery ----
def pred_masks_from_Z(Z, v):
    return blockers_pred(Z, v)


def ac_mas_tables(pred, v):
    """acyclic[U] and mas[U] for every subset U of [v] (bitmask), O(v * 2^v)."""
    N = 1 << v
    ac = bytearray(N)
    ac[0] = 1
    mas = [0] * N
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


def mas_subset(ac, mas, U):
    """One acyclic induced subset A of U with |A| = mas[U] (greedy reconstruction)."""
    if ac[U]:
        return U
    best = mas[U]
    x = U
    while x:
        lb = x & -x
        if mas[U ^ lb] == best:
            return mas_subset(ac, mas, U ^ lb)
        x ^= lb
    raise AssertionError("mas reconstruction failed")


def sink_first_order(Z, S):
    """Repeatedly take sinks (no outgoing Z-edge inside the remainder) first."""
    order = []
    rem = S
    while rem:
        found = None
        x = rem
        while x:
            lb = x & -x
            t = lb.bit_length() - 1
            if not any(Z[t][s] for s in range(len(Z)) if s != t and (rem >> s) & 1):
                found = t
                break
            x ^= lb
        assert found is not None, "subset not acyclic"
        order.append(found)
        rem ^= 1 << found
    return order


def mp_exact(sig, mas, mp_cap=5000000):
    """Exact Lemma MP value: max over pivot maps c: [v] -> D(t) of
    sum_i MAS(Z[C_i]). Returns (value, worst, nmaps, best_pick) or
    (None, None, nmaps, None) when nmaps > mp_cap."""
    M, pi, sg, Z = sig
    v = len(M)
    Dopts = [pi[t] & sg[t] for t in range(v)]
    lists = [[b for b in (1, 2, 4) if Dopts[t] & b] for t in range(v)]
    nmaps = 1
    for cl in lists:
        nmaps *= len(cl)
    if nmaps > mp_cap:
        return None, None, nmaps, None
    best, worst, best_pick = 0, v, None
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
            best, best_pick = val, pick
        if val < worst:
            worst = val
    return best, worst, nmaps, best_pick


def omega_mutual(sig):
    """Exact size of the largest mutual-zero clique (Lemma RK (a): <= 3)."""
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
    """Exact dichromatic number by subset DP (exact for v <= 13)."""
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
    """Decide 3-colourability into acyclic classes with optional per-vertex
    allowed colours; returns (result, exhausted), result None when budget ends."""
    if allowed is None:
        allowed = [7] * v
    order = sorted(range(v), key=lambda t: -((pred[t].bit_count()) +
                                             sum(1 for s in range(v) if s != t and (pred[s] >> t) & 1)))
    cls = [0, 0, 0]
    nodes = [0]
    succ = [[s for s in range(v) if s != t and ((pred[s] >> t) & 1)] for t in range(v)]

    def adds_cycle(t, cmask):
        seen = 0
        stack = [u for u in succ[t] if (cmask >> u) & 1]
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
    total = 0
    for j in range(3):
        Rj = sum(1 << t for t in range(v) if (pi[t] >> j) & 1)
        Aj = sum(1 << t for t in range(v) if (sg[t] >> j) & 1)
        total += block_rank(Brows, Rj, Aj, v)
    return total


def min_chain_cost(sig, budget_free=12, local_evals=30, seed=7):
    """Minimum chain cost over admissible B; exhaustive when few free pairs,
    else bounded deterministic local search. Any B found bounds cert from
    above through the proven chain cost >= cert(M)."""
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
                best_bits = bits
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


# ------------------------------------------------- scope machinery (new) ----
def v2(x):
    """2-adic valuation of a Fraction; 0 maps to +10**9."""
    if x == 0:
        return 10 ** 9
    n, d = x.numerator, x.denominator
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    while d % 2 == 0:
        d //= 2
        k -= 1
    return k


def total_contents(P, Q):
    """c_j = min_t v2(p_j(t)) + min_s v2(q_j(s)) = 2-content of total j's
    rank-1 matrix p_j q_j^T (invariant under per-total rescaling)."""
    v = len(P)
    cs = []
    for j in range(3):
        ps = [v2(P[t][j]) for t in range(v) if P[t][j] != 0]
        qs = [v2(Q[t][j]) for t in range(v) if Q[t][j] != 0]
        if not ps or not qs:
            cs.append(None)  # zero total
        else:
            cs.append(min(ps) + min(qs))
    return cs


def gamma_of(cs):
    fin = [c for c in cs if c is not None]
    return min(fin)


def anchor_labels(P, Q):
    """Scale-invariant mod-2 anchor (Lemma SC/SG): gamma = min_j c_j; per total
    j rescale p_j by 2^{-m_j} (m_j = min_t v2(p_j(t))) and q_j by 2^{-gamma+m_j}.
    Every total is then 2-integral; reduce mod 2 to labels a(t), b(t).
    Returns (a, b, gamma, cs, diagv2) with K_ts = a(t).b(s) == [v2(M_ts) == gamma]
    for M_ts != 0 and 0 at every zero (the scope identity, machine-checked)."""
    v = len(P)
    cs = total_contents(P, Q)
    gamma = gamma_of(cs)
    a = [0] * v
    b = [0] * v
    for j in range(3):
        if cs[j] is None:
            continue
        m = min(v2(P[t][j]) for t in range(v) if P[t][j] != 0)
        for t in range(v):
            if P[t][j] != 0 and v2(P[t][j]) == m:
                a[t] |= 1 << j
        qmin = gamma - m
        for s in range(v):
            if Q[s][j] != 0 and v2(Q[s][j]) == qmin:
                b[s] |= 1 << j
    M = [[sum(P[t][j] * Q[s][j] for j in range(3)) for s in range(v)] for t in range(v)]
    diagv2 = [v2(M[t][t]) for t in range(v)]
    return a, b, gamma, cs, diagv2


def scope_identity_ok(sig, a, b, gamma):
    """Machine identity of the anchor: K_ts == 1 iff v2(M_ts) == gamma."""
    M, pi, sg, Z = sig
    v = len(M)
    for t in range(v):
        for s in range(v):
            k = 1 if (((a[t] & b[s]).bit_count() & 1)) else 0
            want = 1 if (M[t][s] != 0 and v2(M[t][s]) == gamma) else 0
            if k != want:
                return False
    return True


def entry_class(P, Q):
    entries = [x for row in P + Q for x in row]
    if all(x.denominator == 1 for x in entries):
        return "integer"
    if all(x.denominator & (x.denominator - 1) == 0 for x in entries):
        return "dyadic"
    if all(v2(x) >= 0 for x in entries):
        return "2-integral-oddden"
    return "general-Q"


# ------------------------------------ mixed anchor+pivot (Lemma MX, U=0) ----
def mx_anchor_pivot(sig, a0, b0, anchor_set, ac, mas, mp_best, map_cap=200000):
    """Lemma MX (PR 2747) with U = empty and A = anchor_set (labels a0, b0):
    max over pivot maps c on T = [v] \\ A of |A| + sum_i MAS(Z[C_i]) under the
    A-first hypothesis (ii) or the T-first hypothesis (ii'), together with the
    pure matched-pivot value mp_best (the A = empty special case).
    Returns (value, form, nmaps_evaluated)."""
    M, pi, sg, Z = sig
    v = len(M)
    A = anchor_set
    Tmask = ((1 << v) - 1) ^ A
    Dopts = [pi[t] & sg[t] for t in range(v)]
    lists = [[b for b in (1, 2, 4) if Dopts[t] & b] for t in range(v) if (Tmask >> t) & 1]
    tids = [t for t in range(v) if (Tmask >> t) & 1]
    nmaps = 1
    for cl in lists:
        nmaps *= len(cl)
    if nmaps > map_cap:
        return mp_best, "all-T (MP only; mixed maps over cap)", 0
    best, form = mp_best, "all-T (MP)"
    evaluated = 0
    for pick in itertools.product(*lists):
        evaluated += 1
        cmap = dict(zip(tids, pick))
        classes = [0, 0, 0]
        for t, m in zip(tids, pick):
            classes[(m.bit_length() - 1)] |= 1 << t
        base = A.bit_count() + mas[classes[0]] + mas[classes[1]] + mas[classes[2]]
        if base <= best:
            continue
        ok_a_first = True
        for t in range(v):
            if not (A >> t) & 1:
                continue
            for s in tids:
                if M[t][s] == 0 and (a0[t] & cmap[s]):
                    ok_a_first = False
                    break
            if not ok_a_first:
                break
        if ok_a_first:
            best, form = base, "A-first (A=S_gamma)"
            continue
        ok_t_first = True
        for t in tids:
            for s in range(v):
                if (A >> s) & 1 and M[t][s] == 0 and (cmap[t] & b0[s]):
                    ok_t_first = False
                    break
            if not ok_t_first:
                break
        if ok_t_first:
            best, form = base, "T-first (A=S_gamma)"
    return best, form, evaluated


def mx_witness(sig, a0, b0, anchor_set, pick, tids, ac, mas):
    """Build the MX witness: A lines with anchor labels, T lines with matched
    pivots; order A first (any order), then each class sink-first."""
    M, pi, sg, Z = sig
    v = len(M)
    a = [0] * v
    b = [0] * v
    order = []
    for t in range(v):
        if (anchor_set >> t) & 1:
            a[t] = a0[t]
            b[t] = b0[t]
            order.append(t)
    classes = [0, 0, 0]
    for t, m in zip(tids, pick):
        a[t] = m
        b[t] = m
        classes[m.bit_length() - 1] |= 1 << t
    for cmask in classes:
        sub = mas_subset(ac, mas, cmask)
        order.extend(sink_first_order(Z, sub))
    return {"a": a, "b": b, "order": order}


# ---------------------------------------------------------- generators ----
def _accept(P, Q):
    return all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(len(P)))


def gen_evenden(rng, v):
    """Entries with even denominators (negative 2-valuation): totals whose
    content c_j < 0, where Lemma AN's literal normalization hypothesis fails
    and only the scale-invariant anchor applies."""
    box = [Fraction(1, 2), Fraction(-1, 2), Fraction(1, 4), Fraction(-1, 4),
           Fraction(3, 2), Fraction(-3, 2), Fraction(1), Fraction(-1),
           Fraction(2), Fraction(-2), Fraction(1, 8)]
    while True:
        P = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        Q = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        if _accept(P, Q):
            return (P, Q), signature(P, Q)


def gen_oddden(rng, v):
    """Entries in Z_(2) \\ Z (odd denominators): 2-integral, non-integer,
    non-dyadic. Lemma AN applies to these verbatim (residue (iii) audit)."""
    box = [Fraction(1, 3), Fraction(-1, 3), Fraction(2, 3), Fraction(-2, 3),
           Fraction(1, 5), Fraction(-1, 5), Fraction(3, 5), Fraction(2),
           Fraction(-2), Fraction(1), Fraction(-1), Fraction(4, 3)]
    while True:
        P = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        Q = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        if _accept(P, Q):
            return (P, Q), signature(P, Q)


def gen_mixed(rng, v):
    """General Q: halves and thirds mixed."""
    box = [Fraction(1, 2), Fraction(-1, 2), Fraction(1, 3), Fraction(-1, 3),
           Fraction(3, 2), Fraction(2, 3), Fraction(1), Fraction(-1),
           Fraction(6, 5), Fraction(-6, 5), Fraction(1, 6)]
    while True:
        P = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        Q = [[rng.choice(box) for _ in range(3)] for _ in range(v)]
        if _accept(P, Q):
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
    P = [[Fraction(x) for x in c[0]] for c in cfg]
    Q = [[Fraction(x) for x in c[1]] for c in cfg]
    return (P, Q), signature(P, Q)


def frac_json(x):
    return x.numerator if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def main():
    fails = []
    results = {}

    # ---- controls ----
    log("controls")
    brute_agree = 0
    for seed in (11, 22, 33):
        # three tiny random instances (v = 3) from the integer model
        rng = random.Random(seed)
        while True:
            P = [[Fraction(rng.choice([-1, 0, 1])) for _ in range(3)] for _ in range(3)]
            Q = [[Fraction(rng.choice([-1, 0, 1])) for _ in range(3)] for _ in range(3)]
            if _accept(P, Q):
                break
        sig = signature(P, Q)
        tabs = bfeas_tables(sig[1], sig[2])
        ec, exh = exact_cert(sig, tabs, cap=100000)
        bb = brute_cert(sig)
        if ec == bb:
            brute_agree += 1
        else:
            fails.append(f"brute/engine disagree (seed {seed}): {bb} vs {ec}")

    P3 = [[Fraction(x) for x in row] for row in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]]
    sig_diag = signature(P3, P3)
    tabs_diag = bfeas_tables(sig_diag[1], sig_diag[2])
    diag_cert, _ = exact_cert(sig_diag, tabs_diag, cap=100000)
    if diag_cert != 3:
        fails.append(f"diagonal control: cert {diag_cert} != 3")

    rng = random.Random(999)
    while True:
        Pc = [[Fraction(rng.choice([-1, 0, 1])) for _ in range(3)] for _ in range(4)]
        Qc = [[Fraction(rng.choice([-1, 0, 1])) for _ in range(3)] for _ in range(4)]
        if _accept(Pc, Qc):
            break
    sig_c = signature(Pc, Qc)
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

    mas_checks = 0
    pred_tri = [0b110, 0b101, 0b011]
    _, mas_tri = ac_mas_tables(pred_tri, 3)
    if mas_tri[7] == 1:
        mas_checks += 1
    else:
        fails.append(f"MAS bidirected triangle {mas_tri[7]} != 1")
    pred_c3 = [1 << 2, 1 << 0, 1 << 1]
    _, mas_c3 = ac_mas_tables(pred_c3, 3)
    if mas_c3[7] == 2:
        mas_checks += 1
    else:
        fails.append(f"MAS directed 3-cycle {mas_c3[7]} != 2")
    _, mas_e4 = ac_mas_tables([0, 0, 0, 0], 4)
    if mas_e4[15] == 4:
        mas_checks += 1
    else:
        fails.append(f"MAS empty-4 {mas_e4[15]} != 4")
    if mas_checks != 3:
        fails.append(f"MAS controls {mas_checks}/3")

    chi_checks = 0
    if chi_exact_dp(pred_tri, 3) == 3:
        chi_checks += 1
    else:
        fails.append("chi bidirected triangle != 3")
    pred_k4 = [sum(1 << s for s in range(4) if s != t) for t in range(4)]
    if chi_exact_dp(pred_k4, 4) == 4:
        chi_checks += 1
    else:
        fails.append("chi bidirected K4 != 4")
    pred_chain = [0, 1 << 0, 1 << 1]
    if chi_exact_dp(pred_chain, 3) == 1:
        chi_checks += 1
    else:
        fails.append("chi acyclic chain != 1")
    if chi_exact_dp(pred_c3, 3) == 2:
        chi_checks += 1
    else:
        fails.append("chi directed 3-cycle != 2")
    if chi_checks != 4:
        fails.append(f"chi controls {chi_checks}/4")

    pred_diag = pred_masks_from_Z(sig_diag[3], 3)
    _, mas_diag = ac_mas_tables(pred_diag, 3)
    mp_v, mp_worst, mp_nmaps, mp_pick = mp_exact(sig_diag, mas_diag)
    if mp_v != 3:
        fails.append(f"MP diagonal control {mp_v} != 3")

    # ---- scope controls (new) ----
    log("scope controls")
    scope_ctl = {}

    # SC1: dyadic entries, c_j < 0 (Lemma AN literal hypothesis fails), M = (1/4)J_2
    Pf = [[Fraction(1, 2), Fraction(0), Fraction(0)], [Fraction(1, 2), Fraction(0), Fraction(0)]]
    Qf = [[Fraction(1, 2), Fraction(0), Fraction(0)], [Fraction(1, 2), Fraction(0), Fraction(0)]]
    sig_f = signature(Pf, Qf)
    a_f, b_f, g_f, cs_f, dv_f = anchor_labels(Pf, Qf)
    reach_f = sum(1 for t in range(2) if dv_f[t] == g_f)
    ok_f = scope_identity_ok(sig_f, a_f, b_f, g_f)
    entry_f = entry_class(Pf, Qf)
    an_hyp_f = gamma_of(cs_f) >= 0
    sc1 = (entry_f == "dyadic" and not an_hyp_f and g_f == -2 and reach_f == 2 and ok_f)
    scope_ctl["SC1_dyadic_negative_content"] = sc1
    if not sc1:
        fails.append(f"SC1 failed: entry={entry_f} ANhyp={an_hyp_f} gamma={g_f} reach={reach_f} id={ok_f}")

    # SC2: scaled integer decoder M = 2*I_3 (p_j = 2 e_j, q_j = e_j): gamma = 1,
    # all diagonals at level gamma although every M_tt is even (naive odd count 0)
    P2 = [[Fraction(2), Fraction(0), Fraction(0)], [Fraction(0), Fraction(2), Fraction(0)],
          [Fraction(0), Fraction(0), Fraction(2)]]
    Q2 = [[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0)],
          [Fraction(0), Fraction(0), Fraction(1)]]
    sig_2 = signature(P2, Q2)
    a_2, b_2, g_2, cs_2, dv_2 = anchor_labels(P2, Q2)
    reach_2 = sum(1 for t in range(3) if dv_2[t] == g_2)
    ok_2 = scope_identity_ok(sig_2, a_2, b_2, g_2)
    naive_odd_2 = sum(1 for t in range(3) if dv_2[t] == 0)
    sc2 = (g_2 == 1 and reach_2 == 3 and naive_odd_2 == 0 and ok_2)
    scope_ctl["SC2_positive_content_scaled"] = sc2
    if not sc2:
        fails.append(f"SC2 failed: gamma={g_2} reach={reach_2} odd={naive_odd_2} id={ok_2}")

    # SC3: odd-denominator (non-dyadic) entries: Lemma AN applies verbatim
    Po = [[Fraction(1, 3), Fraction(2, 3), Fraction(0)], [Fraction(0), Fraction(1, 5), Fraction(3, 5)],
          [Fraction(2, 3), Fraction(0), Fraction(1, 5)]]
    Qo = [[Fraction(1, 5), Fraction(2, 3), Fraction(0)], [Fraction(0), Fraction(3, 5), Fraction(1, 3)],
          [Fraction(1, 3), Fraction(0), Fraction(2, 5)]]
    sig_o = signature(Po, Qo)
    a_o, b_o, g_o, cs_o, dv_o = anchor_labels(Po, Qo)
    reach_o = sum(1 for t in range(3) if dv_o[t] == g_o)
    ok_o = scope_identity_ok(sig_o, a_o, b_o, g_o)
    entry_o = entry_class(Po, Qo)
    an_hyp_o = all(c is not None and c >= 0 for c in cs_o)
    sc3 = (entry_o == "2-integral-oddden" and an_hyp_o and ok_o and reach_o >= 1)
    scope_ctl["SC3_oddden_anchor_verbatim"] = sc3
    if not sc3:
        fails.append(f"SC3 failed: entry={entry_o} ANhyp={an_hyp_o} id={ok_o} reach={reach_o}")

    # SC4: reach witness replay on all three scope controls plus identity
    def reach_witness(sig, a, b, diagv2, gamma):
        kept = [t for t in range(len(diagv2)) if diagv2[t] == gamma]
        if not kept:
            return None
        wit = {"a": a, "b": b, "order": kept, "kept": kept}
        return wit

    sc4 = 0
    for (sigx, ax, bx, gx, dvx) in ((sig_f, a_f, b_f, g_f, dv_f),
                                    (sig_2, a_2, b_2, g_2, dv_2),
                                    (sig_o, a_o, b_o, g_o, dv_o)):
        wtx = reach_witness(sigx, ax, bx, dvx, gx)
        if wtx is not None and check_witness(sigx, wtx):
            sc4 += 1
        elif wtx is not None:
            fails.append("reach witness failed replay in scope controls")
    scope_ctl["SC4_reach_witness_replay"] = f"{sc4}/2_nonempty"  # SC1, SC2 nonempty; SC3 may be
    if sc4 < 2:
        fails.append(f"SC4 reach witness replay only {sc4}/2")

    log(f"controls: brute_agree={brute_agree}/3 diagonal_cert={diag_cert} "
        f"corrupt_rejects={corrupt_rejects}/2 mas={mas_checks}/3 chi={chi_checks}/4 "
        f"mp_diagonal={mp_v}")
    results["controls"] = {"brute_agree": brute_agree, "diag_cert": diag_cert,
                           "corrupt_rejects": corrupt_rejects, "mas_checks": mas_checks,
                           "chi_checks": chi_checks, "mp_control": mp_v,
                           "scope_controls": scope_ctl}
    if not fails:
        print("PASS_FSC_CONTROLS")

    # ---- fixtures: calibration anchors + entry-class settlement ----
    log("fixtures")
    fixtures = {}
    for name, recorded, anchor_mp, anchor_good_rec in (("tied_min.json", 11, 9, 0),
                                                       ("cex_min_1.json", 18, 16, 8)):
        (P, Q), sig = load_cfg(name)
        M, pi, sg, Z = sig
        v = len(M)
        thr = threshold(v)
        pred = pred_masks_from_Z(Z, v)
        t_ac = time.time()
        ac, mas = ac_mas_tables(pred, v)
        log(f"{name}: subset DP done ({time.time() - t_ac:.1f}s)")
        mp_v, mp_worst, mp_nmaps, mp_pick = mp_exact(sig, mas)
        if mp_v != anchor_mp:
            fails.append(f"{name}: MP {mp_v} != PR 2747 anchor {anchor_mp}")
        # scope settlement (new)
        a0, b0, gamma, cs, diagv2 = anchor_labels(P, Q)
        ident = scope_identity_ok(sig, a0, b0, gamma)
        if not ident:
            fails.append(f"{name}: scope identity failed")
        reach = [t for t in range(v) if diagv2[t] == gamma]
        naive_odd = sum(1 for t in range(v) if diagv2[t] == 0)
        entry = entry_class(P, Q)
        an_hyp = all(c is not None and c >= 0 for c in cs)
        if len(reach) != anchor_good_rec:
            fails.append(f"{name}: anchor reach {len(reach)} != PR 2747 anchor_good {anchor_good_rec}")
        if naive_odd != anchor_good_rec:
            fails.append(f"{name}: naive odd count {naive_odd} != PR 2747 anchor_good {anchor_good_rec}")
        # mixed anchor+pivot MX value with A = S_gamma
        anchor_mask = sum(1 << t for t in reach)
        mx_v, mx_form, mx_maps = mx_anchor_pivot(sig, a0, b0, anchor_mask, ac, mas, mp_v)
        # replay the winning MX witness (pure MP witness when that wins)
        if mx_v >= mp_v and mx_form.startswith("all-T"):
            classes = [0, 0, 0]
            for t, m in enumerate(mp_pick):
                classes[m.bit_length() - 1] |= 1 << t
            order = []
            wit_mp = {"a": [0] * v, "b": [0] * v, "order": []}
            for t, m in enumerate(mp_pick):
                wit_mp["a"][t] = m
                wit_mp["b"][t] = m
            for cmask in classes:
                sub = mas_subset(ac, mas, cmask)
                order.extend(sink_first_order(Z, sub))
            wit_mp["order"] = order
            if not check_witness(sig, wit_mp):
                fails.append(f"{name}: matched-pivot witness failed replay")
        if mx_v != anchor_mp:
            fails.append(f"{name}: MX {mx_v} != PR 2747 anchor {anchor_mp}")
        # engine witness
        tabs = bfeas_tables(pi, sg)
        if name == "tied_min.json":
            wit_val, wit = hill_climb(sig, tabs, iters=400, seed=9)
            if wit_val < recorded:
                fails.append(f"{name}: engine witness {wit_val} < recorded {recorded}")
            if not check_witness(sig, wit):
                fails.append(f"{name}: hill-climb witness failed replay")
            if wit_val > recorded:
                log(f"{name}: NOTE engine witness {wit_val} exceeds recorded CP-SAT limit {recorded}")
        else:
            with open(os.path.join(DATA, "cex_min_1.witness.json"), "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if not check_witness(sig, stored):
                fails.append("cex_min_1 stored witness failed replay")
            wit_val = len(stored["order"])
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
        if v <= 13:
            chi_val = chi_exact_dp(pred, v)
            chi_exh = True
        else:
            r, exh_budget = chi_le3_backtrack(pred, v, budget=300000)
            chi_val = ("le3" if r else ("gt3" if r is False else "unknown"))
            chi_exh = not exh_budget
        om = omega_mutual(sig)
        fixtures[name] = {
            "v": v, "threshold": thr,
            "entry_class": entry, "per_total_contents_c": cs, "gamma": gamma,
            "diag_v2": diagv2, "anchor_reach": len(reach),
            "anchor_reach_lines": reach,
            "naive_odd_count": naive_odd, "pr2747_anchor_good": anchor_good_rec,
            "untouchable_by_anchor": v - len(reach),
            "scope_identity": ident, "AN_hypothesis_holds": an_hyp,
            "mp_bound": mp_v, "mp_worst": mp_worst, "mp_maps": mp_nmaps,
            "mp_anchor": anchor_mp, "mx_value": mx_v, "mx_form": mx_form,
            "mx_maps_evaluated": mx_maps,
            "engine_witness": wit_val, "recorded_cert": recorded,
            "chain_anchor": chain_anchor,
            "mas_of_Z": mas[(1 << v) - 1], "omega_mutual": om,
            "chi_unconstrained": chi_val, "chi_exhaustive": chi_exh,
            "mp_deficit_vs_v": v - mp_v,
            "dichromatic_with_D": (mp_v == v),
            "arcs_Z": arc_count(sig), "mutual_pairs": mutual_pair_count(sig),
        }
        log(f"{name}: v={v} thr={thr} entry={entry} gamma={gamma} reach={len(reach)}/{v} "
            f"MP={mp_v} MX={mx_v} ({mx_form}) witness={wit_val} chi={chi_val}")
    results["fixtures"] = fixtures
    if not fails:
        print("PASS_FSC_FIXTURES")

    # ---- search: smallest-first in the entry-class domain ----
    log("search (smallest first)")
    search_records = []
    falsifiers = []
    certified = 0
    min_ratio = None
    fams = (("evenden", gen_evenden), ("oddden", gen_oddden), ("mixed", gen_mixed))
    search_v = list(range(3, 11))
    for v in search_v:
        thr = threshold(v)
        for fam, gen in fams:
            n_inst = 4 if v <= 6 else 3
            for k in range(n_inst):
                seed = 1000 * v + 131 * k + sum(ord(ch) for ch in fam)
                rng = random.Random(seed)
                (P, Q), sig = gen(rng, v)
                M, pi, sg, Z = sig
                a0, b0, gamma, cs, diagv2 = anchor_labels(P, Q)
                ident = scope_identity_ok(sig, a0, b0, gamma)
                reach = [t for t in range(v) if diagv2[t] == gamma]
                entry = entry_class(P, Q)
                an_hyp = all(c is not None and c >= 0 for c in cs)
                pred = pred_masks_from_Z(Z, v)
                ac, mas = ac_mas_tables(pred, v)
                mp_v, mp_worst, mp_nmaps, mp_pick = mp_exact(sig, mas, mp_cap=300000)
                anchor_mask = sum(1 << t for t in reach)
                mx_v, mx_form, mx_maps = mx_anchor_pivot(sig, a0, b0, anchor_mask, ac, mas,
                                                         mp_v if mp_v is not None else 0,
                                                         map_cap=300000)
                tabs = bfeas_tables(pi, sg)
                if v <= 5:
                    exact, exh = exact_cert(sig, tabs, cap=200000)
                else:
                    exact, exh = None, False
                wit_val, wit = hill_climb(sig, tabs, iters=120, seed=seed % 97)
                best_known = max(x for x in [wit_val, mx_v or 0, exact or 0] if x is not None)
                verdict = "certified>=thr" if best_known >= thr else "below-thr-pending"
                chain_min = None
                if best_known < thr:
                    chain_min, _ = min_chain_cost(sig)
                    if chain_min < thr:
                        verdict = "FALSIFIER"
                        falsifiers.append({"v": v, "seed": seed, "family": fam,
                                           "chain_min": chain_min, "thr": thr})
                else:
                    certified += 1
                ratio = best_known / v
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                rec = {"family": fam, "v": v, "seed": seed, "thr": thr,
                       "entry_class": entry, "per_total_contents_c": cs,
                       "gamma": gamma, "anchor_reach": len(reach),
                       "naive_odd_count": sum(1 for t in range(v) if diagv2[t] == 0),
                       "untouchable_by_anchor": v - len(reach),
                       "scope_identity": ident, "AN_hypothesis_holds": an_hyp,
                       "mp_bound": mp_v, "mp_maps": mp_nmaps,
                       "mx_value": mx_v, "mx_form": mx_form,
                       "exact_cert": exact, "exact_exhausted": exh,
                       "engine_witness": wit_val, "best_known": best_known,
                       "chain_min": chain_min, "verdict": verdict}
                search_records.append(rec)
                if not ident:
                    fails.append(f"search v={v} {fam} seed={seed}: scope identity failed")
                if falsifiers:
                    break
            if falsifiers:
                break
        if falsifiers:
            break
    results["search"] = {"instances": len(search_records),
                         "v_range": [search_v[0], search_v[-1]],
                         "families": [f for f, _ in fams],
                         "falsifiers": falsifiers,
                         "certified_at_or_above_threshold": certified,
                         "min_best_known_ratio": min_ratio,
                         "entry_class_counts": {
                             ec: sum(1 for r in search_records if r["entry_class"] == ec)
                             for ec in sorted({r["entry_class"] for r in search_records})},
                         "AN_hypothesis_failures": sum(
                             1 for r in search_records if not r["AN_hypothesis_holds"]),
                         "instances_with_negative_gamma": sum(
                             1 for r in search_records if r["gamma"] < 0),
                         "instances_with_anchor_reach_below_threshold": sum(
                             1 for r in search_records if r["anchor_reach"] < r["thr"]),
                         "instances_with_untouchable_lines": sum(
                             1 for r in search_records if r["untouchable_by_anchor"] > 0),
                         "records": search_records}
    log(f"search: {len(search_records)} instances, falsifiers={len(falsifiers)}, "
        f"certified={certified}, min ratio={min_ratio}")
    if not fails:
        print("PASS_FSC_SEARCH")

    if not fails:
        print("PASS_FSTAR_ENTRY_CLASS_SCOPE")

    cert_obj = {"package": "research/fstar-entry-class-scope-seed63d5f999",
                "generated_by": "verify.py", "results": results,
                "fails": fails}
    blob = json.dumps(cert_obj, sort_keys=True, indent=1).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()
    cert_obj["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8") as fh:
        json.dump(cert_obj, fh, sort_keys=True, indent=1)
    print(f"CERTIFICATE digest {digest[:16]}")
    if fails:
        print("FAIL_FSTAR_ENTRY_CLASS_SCOPE")
        for f in fails:
            print("  FAIL:", f)
        sys.exit(1)
    print("ALL_CHECKS_PASS")


if __name__ == "__main__":
    main()
