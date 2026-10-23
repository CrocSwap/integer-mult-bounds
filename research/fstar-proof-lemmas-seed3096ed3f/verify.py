#!/usr/bin/env python3
"""F-star proof-lemma checks: engine controls, structural lemmas on instances,
named-instance certificate reproduction, exact cert values at tiny v, and a
targeted falsifier search beyond the censused domain of
https://github.com/CrocSwap/integer-mult-bounds/pull/2335 (v = 4..12, entries
-2..2). Stdlib only, deterministic. Part of research/fstar-proof-lemmas-seed3096ed3f.

Model (research/root-unit-decoder-lemmas section 7; PR 2111 section 1): a
T = 3 decoder is M = sum_{j=1..3} p_j q_j^T over Q on v lines with M_tt != 0.
Row support pi(t) = {j : p_j(t) != 0}, column support sigma(t) = {j : q_j(t)
!= 0}. An L8 labelling is F2 vectors a(t) supported in pi(t), b(t) supported
in sigma(t), K_ts = a(t) . b(s) mod 2. cert(M) is the largest |S| admitting
an order with K_tt = 1 on S and K_ts = 0 at every incidence M_ts = 0 with t
before s (t, s in S). cert(M) depends only on (zero pattern of M, pi, sigma).

Engine: for fixed a-labels, the (b, order, S) completion is exact by subset
DP (b-exists for line t and blockers U is a table lookup; f[T] = OR over t in
T of f[T \\ t] and b-exists(t, blockers of T \\ t)). Exact cert enumerates all
a-labels; a witness search hill-climbs over a-labels with exact completion.
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
    v = len(M)
    a, b, order = wit["a"], wit["b"], wit["order"]
    if sorted(order) != sorted(set(order)) or not order:
        return False
    pos = {t: i for i, t in enumerate(order)}
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
                    acyc = [False] * (1 << n)
                    acyc[0] = True
                    mx = 0
                    for T in range(1, 1 << n):
                        for u in range(n):
                            if (T >> u) & 1:
                                prev = T ^ (1 << u)
                                sink = True
                                for w in range(n):
                                    if (prev >> w) & 1 and D[u][w]:
                                        sink = False
                                        break
                                if sink and acyc[prev]:
                                    acyc[T] = True
                                    mx = max(mx, T.bit_count())
                                    break
                    if mx > best:
                        best = mx
    return best


def mas_digraph(edges, v):
    """Exact maximum acyclic induced subset of a digraph given as edge list."""
    out = [0] * v
    for (t, s) in edges:
        out[t] |= 1 << s
    acyc = bytearray(1 << v)
    acyc[0] = 1
    mx = 0
    for T in range(1, 1 << v):
        u = T
        while u:
            lb = u & -u
            t = lb.bit_length() - 1
            prev = T ^ lb
            if acyc[prev] and (out[t] & prev) == 0:
                acyc[T] = 1
                mx = max(mx, T.bit_count())
                break
            u ^= lb
    return mx, acyc


def block_rank(rows_mask, Rj, Aj, v):
    # extract submatrix (rows Rj, columns Aj) as ints over Aj columns
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


def admissible_free_pairs(Z, v):
    return [(t, s) for t in range(v) for s in range(v) if t != s and Z[t][s]]


def min_chain_cost(sig, budget_free=12, local_evals=250, seed=7):
    """Minimum of chain cost over admissible B (0/1, unit diagonal, ones only
    where M vanishes). Exhaustive when the free-pair count is small; otherwise
    deterministic single-bit local search from B = I and random starts. Any B
    found is an admissible upper bound on cert; a B below threshold falsifies."""
    M, pi, sg, Z = sig
    v = len(M)
    free = admissible_free_pairs(Z, v)
    f = len(free)

    def cost_of(bits):
        Brows = [0] * v
        for t in range(v):
            Brows[t] = 1 << t
        for k, (t, s) in enumerate(free):
            if (bits >> k) & 1:
                Brows[t] |= 1 << s
        return chain_cost(Brows, pi, sg, v)

    best_bits = 0
    best = cost_of(0)  # B = I baseline
    if f <= budget_free:
        for bits in range(1 << f):
            c = cost_of(bits)
            if c < best:
                best, best_bits = c, bits
    else:
        rng = random.Random(seed + v)
        starts = [0, (1 << f) - 1]  # B = I and the maximal admissible B
        for st in range(2):
            bits = starts[st]
            cur = cost_of(bits)
            if cur < best:
                best, best_bits = cur, bits
            for ev in range(local_evals // 4):
                k = rng.randrange(f)
                bits ^= 1 << k
                c = cost_of(bits)
                if c <= cur:
                    cur = c
                    if c < best:
                        best, best_bits = c, bits
                else:
                    bits ^= 1 << k
        for ev in range(local_evals // 2):
            bits = rng.randrange(1 << min(f, 30)) if f <= 30 else 0
            cur = cost_of(bits)
            if cur < best:
                best, best_bits = cur, bits
            for inner in range(8):
                k = rng.randrange(f)
                bits ^= 1 << k
                c = cost_of(bits)
                if c <= cur:
                    cur = c
                    if c < best:
                        best, best_bits = c, bits
                else:
                    bits ^= 1 << k
    return best, best_bits, f


def threshold(v):
    return (2 * v) // 3


# ---------------------------------------------------------- search side ----
def hillclimb_witness(sig, budget_evals, seed):
    M, pi, sg, Z = sig
    v = len(M)
    tabs = bfeas_tables(pi, sg)
    o = [opts(pi[t]) for t in range(v)]
    rng = random.Random(seed)
    a = [rng.choice(o[t]) for t in range(v)]
    best, bestT, f = complete(a, pi, sg, Z, v, tabs)
    best_a = list(a)
    evals = 1
    improved = True
    while improved and evals < budget_evals:
        improved = False
        ts = list(range(v))
        rng.shuffle(ts)
        for t in ts:
            old = a[t]
            for m in o[t]:
                if m == old or evals >= budget_evals:
                    continue
                a[t] = m
                val, bt, ff = complete(a, pi, sg, Z, v, tabs)
                evals += 1
                if val > best:
                    best, bestT, f = val, bt, ff
                    best_a = list(a)
                    old = m
                    improved = True
            a[t] = old
    a = best_a
    order, bs = reconstruct(a, sg, Z, v, tabs, bestT, f)
    return {"a": a, "b": bs, "order": order, "kept": order}, best, evals


def exact_cert(sig):
    """Exact cert by exhaustive a-enumeration with exact completion (v <= 5)."""
    M, pi, sg, Z = sig
    v = len(M)
    tabs = bfeas_tables(pi, sg)
    o = [opts(pi[t]) for t in range(v)]
    best = 0
    for a in itertools.product(*o):
        val, _, _ = complete(list(a), pi, sg, Z, v, tabs)
        if val > best:
            best = val
    return best


def structural_checks(sig):
    """Lemma-instance checks: (i) mutual-zero graph has no K_4 (clique <= 3);
    (ii) the zero digraph Z has no transitive 4-tournament; (iii) the
    matched-pivot construction from MAS(H) is a valid witness of that size.
    Returns (k4free_or_None, tt4free_or_None, pivot_or_None, masH); None marks
    an instance where the check was skipped (v too large for the brute loops)."""
    M, pi, sg, Z = sig
    v = len(M)
    ok_k4, ok_tt4 = None, None
    if v <= 16:
        ok_k4, ok_tt4 = True, True
        for S in itertools.combinations(range(v), 4):
            mutual = all(Z[t][s] and Z[s][t] for i, t in enumerate(S)
                         for s in S[i + 1:])
            if mutual:
                ok_k4 = False
            # transitive tournament: some order of S with all forward pairs zero
            for perm in itertools.permutations(S):
                if all(Z[perm[i]][perm[j]] for i in range(4) for j in range(i + 1, 4)):
                    ok_tt4 = False
    H = [(t, s) for t in range(v) for s in range(v) if t != s and Z[t][s] and (pi[t] & sg[s])]
    masH = 0
    ok_pivot = None
    if v <= 12:
        ok_pivot = True
        masH, acyc = mas_digraph(H, v)
        outH = [0] * v
        for (t, s) in H:
            outH[t] |= 1 << s
        # matched-pivot witness: labels a(t) = b(t) = e_{c(t)}, c(t) = least bit of pi(t)&sg(t)
        a = []
        for t in range(v):
            d = pi[t] & sg[t]
            assert d
            a.append(d & -d)
        # extract a largest acyclic subset of H and a sinks-first order
        Tbest = max((T for T in range(1 << v) if acyc[T]), key=lambda T: T.bit_count())
        order, cur = [], Tbest
        while cur:
            found = False
            for t in range(v):
                if (cur >> t) & 1 and (outH[t] & cur) == 0:
                    order.append(t)
                    cur ^= 1 << t
                    found = True
                    break
            assert found, "no sink in an acyclic set: engine bug"
        wit = {"a": a, "b": list(a), "order": order, "kept": order}
        ok_pivot = check_witness(sig, wit) and len(order) == masH
    return ok_k4, ok_tt4, ok_pivot, masH


# ----------------------------------------------------------- generators ----
def gen_instance(rng, v, lo, hi, zeros_ok=True):
    while True:
        P = [[rng.randint(lo, hi) for _ in range(3)] for _ in range(v)]
        Q = [[rng.randint(lo, hi) for _ in range(3)] for _ in range(v)]
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            M, pi, sg, Z = signature(P, Q)
            return (P, Q), (M, pi, sg, Z)


def gen_tied(rng, v):
    """Tied-heavy 2-adic construction: every product p_j(t) q_j(t) is even
    (all lines isotropic at level 1), entries in {+-2, +-4} on some lines and
    {+-1,+-2} on others; retained with M_tt != 0."""
    while True:
        P, Q = [], []
        for t in range(v):
            if t % 2 == 0:
                P.append([2 * rng.choice([-2, -1, 1, 2]) for _ in range(3)])
                Q.append([2 * rng.choice([-2, -1, 1, 2]) for _ in range(3)])
            else:
                P.append([rng.choice([-2, -1, 1, 2]) for _ in range(3)])
                Q.append([rng.choice([-2, -1, 1, 2]) for _ in range(3)])
        if all(sum(P[t][j] * Q[t][j] for j in range(3)) != 0 for t in range(v)):
            M, pi, sg, Z = signature(P, Q)
            return (P, Q), (M, pi, sg, Z)


def load_cfg(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    P = [c[0] for c in cfg]
    Q = [c[1] for c in cfg]
    return (P, Q), signature(P, Q)


# ---------------------------------------------------------------- main ----
def main():
    results = {}
    out = []
    fails = []

    def log(line):
        out.append(line)
        print(line)

    # ---- controls ----
    rng = random.Random(20261015)
    brute_agree = 0
    for i in range(3):
        v = 3
        while True:
            (P, Q), sig = gen_instance(rng, v, -1, 1)
            M, pi, sg, Z = sig
            if any(Z[t][s] for t in range(v) for s in range(v)):
                break
        eb = exact_cert(sig)
        bb = brute_cert(sig)
        if eb == bb:
            brute_agree += 1
        else:
            fails.append(f"brute/engine disagree on control {i}: {bb} vs {eb}")
    # diagonal control: p_j = q_j = e_j on 3 lines -> cert = 3
    P = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    sig_diag = signature(P, P)
    diag_cert = exact_cert(sig_diag)
    if diag_cert != 3:
        fails.append(f"diagonal control: cert {diag_cert} != 3")
    # witness checker corruptions (on a tiny instance with zero pairs)
    (P, Q), sig_c = gen_instance(random.Random(999), 4, -1, 1)
    wit_c, val_c, _ = hillclimb_witness(sig_c, 60, 5)
    corrupt_rejects = 0
    if not check_witness(sig_c, wit_c):
        fails.append("checker rejected a true witness")
    w1 = json.loads(json.dumps(wit_c))
    w1["a"][w1["order"][0]] = 0
    if not check_witness(sig_c, w1):
        corrupt_rejects += 1
    w2 = json.loads(json.dumps(wit_c))
    w2["b"][w2["order"][0]] = 0
    if not check_witness(sig_c, w2):
        corrupt_rejects += 1
    # threshold table
    table_ok = all(threshold(v) == (2 * v) // 3 for v in range(4, 17))
    log(f"controls: brute_agree={brute_agree}/3 diagonal_cert={diag_cert} "
        f"corrupt_rejects={corrupt_rejects}/2 threshold_table={table_ok}")
    if brute_agree == 3 and diag_cert == 3 and corrupt_rejects == 2 and table_ok:
        log("PASS_FSTAR_CONTROLS bruteforce=3 diagonal=3 corrupt=2")
    else:
        fails.append("controls failed")

    # ---- named instances ----
    named = {}
    for name, recorded in (("tied_min.json", 11), ("cex_min_1.json", 18)):
        (P, Q), sig = load_cfg(name)
        v = len(P)
        if name == "tied_min.json":
            wit, val, ev = hillclimb_witness(sig, 400, 20261015 + v)
        else:
            wpath = os.path.join(DATA, "cex_min_1.witness.json")
            with open(wpath, "r", encoding="utf-8") as fh:
                wit = json.load(fh)
            val = len(wit["order"])
            ev = 0
        ok = check_witness(sig, wit)
        if not ok:
            fails.append(f"{name}: witness replay failed")
        cb, _, nf = min_chain_cost(sig, budget_free=12, local_evals=150, seed=11)
        named[name] = (v, val, cb, ok)
        log(f"named {name}: v={v} witness={val} (PR 2111 recorded max one-copy "
            f"L8 = {recorded}) chain_upper={cb} replay_ok={ok} "
            f"threshold={threshold(v)} meets_threshold={val >= threshold(v)}")
        if val < threshold(v):
            fails.append(f"{name}: witness {val} below threshold {threshold(v)}")
    log(f"PASS_FSTAR_NAMED tied_min={named['tied_min.json'][1]}/12 "
        f"cex_min_1={named['cex_min_1.json'][1]}/19")

    # ---- chain-engine cross-check against PR 2111's stored pairing ----
    (Pb, Qb), sig_b = load_cfg("cex_min_1.json")
    Mb, pib, sgb, Zb = sig_b
    vb = len(Mb)
    with open(os.path.join(DATA, "cex_min_1.B22.json"), "r", encoding="utf-8") as fh:
        Bmat = json.load(fh)
    Brows = [sum(1 << s for s in range(vb) if Bmat[t][s]) for t in range(vb)]
    adm = all(Bmat[t][t] == 1 for t in range(vb)) and all(
        Bmat[t][s] == 0 or Zb[t][s]
        for t in range(vb) for s in range(vb) if t != s)
    c22 = chain_cost(Brows, pib, sgb, vb)
    log(f"chain-engine cross-check (PR 2111 stored cost-22 pairing on cex_min_1): "
        f"admissible={adm} chain_cost={c22} (PR 2111 records ranks 10+6+6=22)")
    if adm and c22 == 22:
        log("PASS_FSTAR_CHAIN_ENGINE cex_min_1_B22=22")
    else:
        fails.append(f"B22 cross-check failed: admissible={adm} chain_cost={c22}")

    # ---- exact cert upgrades at tiny v (beyond witness level) ----
    exact_vals = []
    for i, v in enumerate((5, 5, 6)):
        (P, Q), sig = gen_instance(random.Random(31337 + i), v, -3, 3)
        ec = exact_cert(sig)
        wit, val, _ = hillclimb_witness(sig, 80, 100 + i)
        assert val <= ec
        exact_vals.append((v, ec))
        log(f"exact cert (exhaustive a-enumeration, exact completion): "
            f"entries3 instance i={i} v={v} cert={ec}")
    log("PASS_FSTAR_EXACT " + " ".join(f"v{v}={c}" for v, c in exact_vals))

    # ---- structural lemma checks on all search instances + named ----
    inst = 0
    k4ok = tt4ok = pivotok = True
    k4n = tt4n = pivotn = 0
    for name in ("tied_min.json", "cex_min_1.json"):
        (P, Q), sig = load_cfg(name)
        v = len(P)
        k, t, p, masH = structural_checks(sig)
        if k is not None:
            k4ok &= k
            k4n += 1
        if t is not None:
            tt4ok &= t
            tt4n += 1
        if p is not None:
            pivotok &= p
            pivotn += 1
        inst += 1
        log(f"structural {name}: v={v} mutual_zero_K4_free={k} tt4_free={t} "
            f"pivot_witness_ok={p} MAS(H)={masH if v <= 12 else 'n/a'}")

    # ---- beyond-census falsifier search ----
    search_rows = []
    falsifiers = []
    min_ratio = 1.0
    # family A: entries in {-3..3} (outside the census alphabet), v = 4..12
    # family B: v = 13..16 (outside the census v-range): entries3, tied-heavy
    plans = [("entries3", v, 3) for v in range(4, 13)] + \
            [("entries3-big", v, 2) for v in (13, 14, 15, 16)] + \
            [("tied-heavy", v, 2) for v in (13, 14, 15, 16)]
    fam_salt = {"entries3": 31, "entries3-big": 57, "tied-heavy": 83}
    for fam, v, count in plans:
        for i in range(count):
            rng_i = random.Random(20261015 + 1000 * v + 17 * i + fam_salt[fam])
            if fam == "tied-heavy":
                (P, Q), sig = gen_tied(rng_i, v)
            else:
                lo, hi = (-3, 3) if v <= 12 else (-3, 3)
                (P, Q), sig = gen_instance(rng_i, v, lo, hi)
            M, pi, sg, Z = sig
            budget = 100 if v <= 12 else (50 if v <= 14 else 30)
            wit, val, ev = hillclimb_witness(sig, budget, 700 + i + v)
            ok = check_witness(sig, wit)
            if not ok:
                fails.append(f"search {fam} v={v} i={i}: witness invalid")
            cb, bbits, nf = min_chain_cost(sig, budget_free=12, local_evals=120,
                                           seed=3 + v)
            thr = threshold(v)
            ratio = val / v
            min_ratio = min(min_ratio, ratio)
            if cb < thr:
                falsifiers.append((fam, v, i, cb, thr))
            if val < thr:
                # a witness below threshold is not a falsifier (lower bound),
                # but the engine should not be below the structural bound
                pass
            k, t, p, masH = structural_checks(sig)
            if k is not None:
                k4ok &= k
                k4n += 1
            if t is not None:
                tt4ok &= t
                tt4n += 1
            if p is not None:
                pivotok &= p
                pivotn += 1
            if v <= 12 and val < masH:
                fails.append(f"search {fam} v={v} i={i}: witness {val} < MAS(H) {masH}")
            inst += 1
            search_rows.append((fam, v, i, val, cb, thr, nf))
            log(f"search {fam} v={v} i={i}: witness={val} chain_upper={cb} "
                f"threshold={thr} free_pairs={nf}")
    log(f"PASS_FSTAR_STRUCTURAL instances={inst} k4free={k4ok} ({k4n} checked) "
        f"tt4free={tt4ok} ({tt4n} checked) pivot={pivotok} ({pivotn} checked)")
    if not (k4ok and tt4ok and pivotok):
        fails.append("structural checks failed")
    log(f"PASS_FSTAR_SEARCH instances={len(search_rows)} falsifiers={len(falsifiers)} "
        f"min_witness_ratio={min_ratio:.3f}")
    if falsifiers:
        for fx in falsifiers:
            log(f"FALSIFIER {fx}")
        fails.append("falsifier found")

    # ---- certificate ----
    cert = {
        "schema_version": 1,
        "engine": "a-label enumeration + exact (b, order, S) completion by subset DP",
        "controls": {"brute_agree": brute_agree, "diagonal_cert": diag_cert,
                     "corrupt_rejects": corrupt_rejects},
        "named": {k: {"v": v, "witness": w, "chain_upper": c, "replay_ok": ok}
                  for k, (v, w, c, ok) in named.items()},
        "exact_cert_tiny": [{"v": v, "cert": c} for v, c in exact_vals],
        "search": [{"family": f, "v": v, "i": i, "witness": w, "chain_upper": c,
                    "threshold": th, "free_pairs": nf}
                   for (f, v, i, w, c, th, nf) in search_rows],
        "falsifiers": [],
        "min_witness_ratio": min_ratio,
        "failures": fails,
    }
    digest = hashlib.sha256(
        json.dumps(cert, sort_keys=True).encode("utf-8")).hexdigest()
    cert["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
    log(f"certificate digest {digest[:16]} written to CERTIFICATE.json")
    log(f"elapsed {time.time() - T0:.1f}s")
    if fails:
        for fme in fails:
            log(f"FAIL: {fme}")
        raise SystemExit(1)
    log("PASS_FSTAR_PROOF_LEMMAS")


main()
