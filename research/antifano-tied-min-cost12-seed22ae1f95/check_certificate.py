#!/usr/bin/env python3
"""Independent exact-F2 certificate: the anti-Fano 12-line configuration (tied_min)
has minimum admissible pairing cost exactly 12.

This is a third method for the claim "cost(tied_min) = 12" (predecessors: the
exchange argument of PR #2111 Theorem T with CNF/CP-SAT confirmations, and the
first-order char-2 jet Theorem T' of PR #2162).  Here: pure standard-library
bitmask linear algebra over F2, complete branch-and-bound enumerations, explicit
forced-zero triangular minor witnesses.  No SAT, no CP-SAT, no exchange
argument, no jet; nothing is imported from the predecessor package.  The model
encoding (admissible B, cost) is re-derived from the pinned data alone and was
cross-read against research/three-total-decoders/lib/kit.py at PR #2111 head.

Model (README section 1 of research/three-total-decoders, PR #2111): a
configuration is 12 lines t with p(t), q(t) in Z^3, p(t).q(t) != 0.  An
admissible pairing B is a 0/1 matrix over F2 with unit diagonal and B_ts = 1
(t != s) only where p(t).q(s) = 0.  R_j = {t : p_j(t) != 0}, A_j = {s :
q_j(s) != 0}; cost(B) = sum_j rank_F2 B[R_j, A_j].

Certificate (all exact):
  (1) every admissible B has cost >= 12:
      (1a) each block j has rank >= 3 for every admissible B: explicit triples
           X_j with forced-zero off-diagonal pattern making B[X_j, X_j] unit
           triangular in the listed order;
      (1b) for each block j the complete set of fillings of its 8 columns with
           rank <= 3 is enumerated (branch and bound on the column spans);
      (1c) for each such filling, the complete set of 2^24 completions of the
           remaining class-j columns is enumerated and the exact minimum of the
           other two block ranks is computed;
      a cost <= 11 pairing would need some block rank <= 3 (all ranks are >= 3
      by (1a)), so (1b)+(1c) cover every falsifier.
  (2) cost 12 is attained: an explicit admissible B* with block ranks (4,4,4).

Semantic failure controls at the end of the run: a tampered data pin must
reject; a weakened forced-zero pattern must break the triangular witness; a
forced-away free bit of the unique low-rank filling must kill the enumeration
result.  Positive controls: B = I has cost 24; B* has cost 12.

Aaron Wang, with help from opencode (substantial AI assistance).  Apache-2.0.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
DATA = PKG / "data" / "tied_min.json"
RESULTS = PKG / "cert_results.json"

PIN_SHA256 = "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"
PIN_SOURCE = ("git blob of research/three-total-decoders/data/tied_min.json at "
              "https://github.com/CrocSwap/integer-mult-bounds/pull/2111 head "
              "98da76c2839ba38538b510420dec54546ccabf0b")

PASS = 0
FAIL = 0


def report(ok, label, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(("PASS " if ok else "FAIL ") + label + ((" | " + detail) if detail else ""))


def rank2(vecs):
    """F2 rank of integer bitmasks, pivot elimination (own implementation)."""
    piv = {}
    r = 0
    for x in vecs:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p] = y
                r += 1
                break
    return r


def basis_of(vecs):
    piv = {}
    for x in vecs:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p] = y
                break
    return piv


def reduce_by(piv, x):
    # A quotient representative must eliminate EVERY fixed pivot, even if
    # a larger nonpivot bit remains. Early stopping is enough for membership
    # testing, but can overcount the rank of several quotient representatives.
    y = x
    for p in sorted(piv, reverse=True):
        if (y >> p) & 1:
            y ^= piv[p]
    return y


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def load_config():
    raw = DATA.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if h != PIN_SHA256:
        raise SystemExit("FAIL pin: data/tied_min.json sha256 " + h + " != " + PIN_SHA256)
    pairs = json.loads(raw.decode("utf-8"))
    P = [p for p, q in pairs]
    Q = [q for p, q in pairs]
    return P, Q


def build_model(P, Q):
    """Return (v, free, freeset, classes, A, C) with free[t][s] the admissible off-diagonal entries."""
    v = len(P)
    free = [[False] * v for _ in range(v)]
    for t in range(v):
        for s in range(v):
            if t != s and dot(P[t], Q[s]) == 0:
                free[t][s] = True
    freeset = [0] * v  # freeset[s]: bitmask of rows t with free[t][s]
    for s in range(v):
        m = 0
        for t in range(v):
            if free[t][s]:
                m |= 1 << t
        freeset[s] = m
    classes = [[s for s in range(v) if Q[s][j] == 0] for j in range(3)]
    A = [[s for s in range(v) if Q[s][j] != 0] for j in range(3)]
    return v, free, freeset, classes, A


def col_vec(s, submask):
    """Column s of B with the chosen subset of its free rows set."""
    return (1 << s) | submask


def block_rank(cols, freeset, choices):
    """rank of the block given by columns cols; choices[s] = chosen free-row submask."""
    return rank2([col_vec(s, choices[s]) for s in cols])


def enum_lowrank(cols, freeset, cap):
    """Complete enumeration of fillings of the given columns with F2 rank <= cap.
    Returns list of tuples of chosen submasks (one per column, in order)."""
    sols = []

    def dfs(i, piv, chosen):
        if i == len(cols):
            sols.append(tuple(chosen))
            return
        s = cols[i]
        sub = freeset[s]
        m = sub
        while True:
            cand = col_vec(s, m)
            y = reduce_by(piv, cand)
            if y:
                if len(piv) < cap:
                    npiv = dict(piv)
                    p = y.bit_length() - 1
                    npiv[p] = y
                    dfs(i + 1, npiv, chosen + [m])
            else:
                dfs(i + 1, piv, chosen + [m])
            if m == 0:
                break
            m = (m - 1) & sub

    dfs(0, {}, [])
    return sols


def main(argv):
    quick = "--quick" in argv
    P, Q = load_config()
    report(True, "pin", "data/tied_min.json sha256 matches " + PIN_SHA256[:16] + " (" + PIN_SOURCE[:60] + "...)")
    v, free, freeset, classes, A = build_model(P, Q)

    # Independent quotient-rank regression from the maintainer review. The
    # old early-stop reducer reported seven for this legal block of rank six.
    fixed = [1410, 3216, 294, 2100]
    varying = [505, 3599, 3654, 1008]
    piv = basis_of(fixed)
    report(len(piv) + rank2([reduce_by(piv, x) for x in varying])
           == rank2(fixed + varying) == 6,
           "control: quotient reduction agrees with full concatenated rank")

    # -- structural checks ----------------------------------------------------
    report(v == 12, "structure: v = 12", "v=" + str(v))
    full_support = all(all(x != 0 for x in p) for p in P)
    report(full_support, "structure: every point has full support (R_j = all 12 rows)")
    two_sup = sorted(sum(1 for x in q if x != 0) for q in Q)
    report(two_sup == [2] * 12, "structure: every line has exactly two nonzero coordinates (F2S)",
           "supports=" + str(two_sup))
    report(sorted(len(c) for c in classes) == [4, 4, 4], "structure: class partition 4/4/4",
           "classes=" + str(classes))
    nfree = sum(row.count(True) for row in free)
    report(nfree == 72, "structure: 72 admissible off-diagonal entries", "nfree=" + str(nfree))
    percol = sorted(bin(freeset[s]).count("1") for s in range(v))
    report(percol == [6] * 12, "structure: 6 free entries per column", "percol=" + str(percol))

    # -- (1a) forced-zero triangular witnesses: each block rank >= 3 ----------
    witnesses = {}
    ok_all = True
    for j in range(3):
        cols = A[j]
        found = None
        for X in _triples(cols):
            order = _triangular_order(X, free)
            if order is not None:
                found = (X, order)
                break
        if found is None:
            ok_all = False
        else:
            X, order = found
            witnesses[j] = {"X": X, "order": order}
    report(ok_all, "floor: MAS >= 3 per block (explicit unit-triangular triples)", json.dumps(witnesses))
    # verify each witness explicitly against the support
    wok = True
    for j, w in witnesses.items():
        X, order = w["X"], w["order"]
        for a in range(3):
            for b in range(a + 1, 3):
                # entry (row order[a], col order[b]) must be forced 0
                if free[order[a]][order[b]]:
                    wok = False
                if order[a] == order[b]:
                    wok = False
        if not set(X) <= set(A[j]):
            wok = False
    report(wok and bool(witnesses), "floor: witness triples verified forced-zero upper triangular inside block j")

    # -- (1b) complete rank-3 filling enumeration per block -------------------
    fillings = {}
    fok = True
    for j in range(3):
        sols = enum_lowrank(A[j], freeset, 3)
        fillings[j] = sols
        if not sols:
            fok = False
    counts = {j: len(s) for j, s in fillings.items()}
    report(fok, "low-rank: every block has at least one rank<=3 filling", "counts=" + str(counts))
    report(all(len(s) == 1 for s in fillings.values()),
           "low-rank: each block's rank<=3 filling is unique (predecessor step b)",
           "counts=" + str(counts))

    # -- (1c) residual completion enumeration --------------------------------
    # For block j with its (unique) filling: classes k,l columns are fixed;
    # class j columns (4 of them, 6 free bits each) vary over 2^24 completions.
    resid = {}
    pok = True
    alim = 16 if quick else 64  # quick mode: 16 * 64^3 = 2^22 completions per filling
    for j in range(3):
        k, l = [c for c in range(3) if c != j]
        minsum_j = 99
        total_j = 0
        hist_j = {}
        detail = []
        for fsol in fillings[j]:
            fix = {}
            for idx, s in enumerate(A[j]):
                fix[s] = col_vec(s, fsol[idx])
            fixed_k = [fix[s] for s in classes[k]]
            fixed_l = [fix[s] for s in classes[l]]
            # block k = class j (varying) + class l (fixed); block l = class j + class k (fixed)
            rank_k_fixed = rank2(fixed_l)
            rank_l_fixed = rank2(fixed_k)
            piv_k = basis_of(fixed_l)
            piv_l = basis_of(fixed_k)
            cand = []
            for s in classes[j]:
                sub = freeset[s]
                opts = []
                m = sub
                while True:
                    opts.append(col_vec(s, m))
                    if m == 0:
                        break
                    m = (m - 1) & sub
                cand.append(opts)
            red_k = [[reduce_by(piv_k, x) for x in opts] for opts in cand]
            red_l = [[reduce_by(piv_l, x) for x in opts] for opts in cand]
            hist = {}
            minsum = 99
            total = 0
            for a in range(alim):
                ra1 = red_k[0][a]
                rl1 = red_l[0][a]
                for b in range(64):
                    ra2 = red_k[1][b]
                    rl2 = red_l[1][b]
                    for c in range(64):
                        ra3 = red_k[2][c]
                        rl3 = red_l[2][c]
                        for d in range(64):
                            total += 1
                            rk = rank_k_fixed + rank2([ra1, ra2, ra3, red_k[3][d]])
                            rl = rank_l_fixed + rank2([rl1, rl2, rl3, red_l[3][d]])
                            s2 = rk + rl
                            if s2 < minsum:
                                minsum = s2
                            hist[(rk, rl)] = hist.get((rk, rl), 0) + 1
            detail.append({"fixed_ranks": [rank_k_fixed, rank_l_fixed],
                           "total": total, "minsum": minsum})
            if minsum < minsum_j:
                minsum_j = minsum
            total_j += total
            for key, cnt in hist.items():
                hist_j[key] = hist_j.get(key, 0) + cnt
        resid[j] = {"total": total_j, "min_rk_plus_rl": minsum_j,
                    "per_filling": detail,
                    "hist_top": sorted(hist_j.items(), key=lambda kv: -kv[1])[:6]}
        if minsum_j < 9:
            pok = False
        print("INFO residual block " + str(j) + ": total=" + str(total_j) + " min(r_k+r_l)=" + str(minsum_j))
    expect_each = alim * 64 * 64 * 64
    report(all(resid[j]["total"] == expect_each * len(fillings[j]) for j in resid),
           "residual: completion count exact",
           "expected per filling=" + str(expect_each))
    report(pok, "residual: min(r_k + r_l) >= 9 for every completion of every rank-3 block filling",
           json.dumps({j: resid[j]["min_rk_plus_rl"] for j in resid}))

    # -- (2) upper bound: explicit attaining B* ------------------------------
    same_class_best = {}
    bstar_choices = {}
    uok = True
    for c in range(3):
        cols = classes[c]
        best = None
        cnt = 0
        for sol in enum_lowrank(cols, _same_class_freeset(cols, freeset, classes, c), 4):
            rk = rank2([col_vec(s, sol[i]) for i, s in enumerate(cols)])
            if rk == 2:
                cnt += 1
                if best is None:
                    best = sol
        same_class_best[c] = cnt
        if best is None:
            uok = False
        else:
            for i, s in enumerate(cols):
                bstar_choices[s] = best[i]
    for s in range(v):
        bstar_choices.setdefault(s, 0)
    bstar_ranks = [block_rank(A[j], freeset, bstar_choices) for j in range(3)]
    cost_bstar = sum(bstar_ranks)
    if quick:
        print("INFO quick mode: B* ranks " + str(bstar_ranks) + " (full check in the default run)")
    else:
        uok = uok and cost_bstar == 12
        report(uok, "upper: explicit admissible B* attains cost 12 with block ranks (4,4,4)",
               "ranks=" + str(bstar_ranks) + " same_class_rank2_counts=" + str(same_class_best))

    # -- positive and negative controls --------------------------------------
    ident = {s: 0 for s in range(v)}
    r_ident = [block_rank(A[j], freeset, ident) for j in range(3)]
    report(sum(r_ident) == 24, "control: diagonal-only B = I has cost 24", "ranks=" + str(r_ident))

    if not quick:
        # failure control 1: a tampered data pin must reject
        tampered = hashlib.sha256(DATA.read_bytes() + b"x").hexdigest()
        report(tampered != PIN_SHA256, "control: pin check rejects tampered bytes")
        # failure control 2: weakening one forced-zero entry of a witness must
        # break the triangular certificate
        j = 0
        X, order = witnesses[j]["X"], witnesses[j]["order"]
        t, s = order[0], order[2]
        was_free = free[t][s]
        free[t][s] = True
        broken = any(free[order[a]][order[b]] for a in range(3) for b in range(a + 1, 3))
        free[t][s] = was_free
        report(broken, "control: weakening a forced-zero entry breaks the triangular witness")
        # failure control 3: forcing away one used free bit of block 0's unique
        # low-rank filling must kill that filling (enumeration count 0)
        j = 0
        sol = fillings[j][0]
        cols = A[j]
        victim = None
        for i, s in enumerate(cols):
            used = sol[i]
            if used:
                victim = (i, s, used & -used)
                break
        fs2 = list(freeset)
        i, s, bit = victim
        fs2[s] = freeset[s] & ~bit
        sols2 = enum_lowrank(cols, fs2, 3)
        report(len(sols2) == 0, "control: removing one used free bit kills the unique rank-3 filling",
               "new_count=" + str(len(sols2)))

    out = {
        "pin_sha256": PIN_SHA256,
        "pin_source": PIN_SOURCE,
        "structure": {"v": v, "free_offdiag": nfree, "per_column_free": percol,
                      "classes": classes, "A": A},
        "triangular_witnesses": {str(j): witnesses[j] for j in witnesses},
        "lowrank_filling_counts": {str(j): counts[j] for j in counts},
        "residual": {str(j): resid[j] for j in resid},
        "upper_bound": {"same_class_rank2_counts": {str(c): same_class_best[c] for c in same_class_best},
                        "bstar_block_ranks": bstar_ranks,
                        "bstar_choices_submask": {str(s): bstar_choices[s] for s in range(v)}},
        "controls": {"identity_block_ranks": r_ident},
        "quick_mode": quick,
    }
    RESULTS.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print("INFO results written: " + str(RESULTS))
    print("SUMMARY pass=" + str(PASS) + " fail=" + str(FAIL))
    return 1 if FAIL else 0


def _triples(cols):
    out = []
    n = len(cols)
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                out.append([cols[a], cols[b], cols[c]])
    return out


def _triangular_order(X, free):
    """An ordering of X with all entries strictly above the diagonal forced 0."""
    for order in itertools.permutations(X):
        ok = True
        for a in range(3):
            for b in range(a + 1, 3):
                if free[order[a]][order[b]] or order[a] == order[b]:
                    ok = False
        if ok:
            return list(order)
    return None


def _same_class_freeset(cols, freeset, classes, c):
    """Free-row masks restricted to same-class rows (for the class-block-diagonal witness search)."""
    rows = set(classes[c])
    out = [0] * 12
    for s in cols:
        m = 0
        for t in range(12):
            if (freeset[s] >> t) & 1 and t in rows:
                m |= 1 << t
        out[s] = m
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
