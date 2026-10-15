#!/usr/bin/env python3
"""Independent exact audit of Lemma CR2 and Theorem B2 (PR #2162 section 2.1-2.2).

All arithmetic is exact (ints, F2 bitsets, symbolic monomials). No predecessor
implementation is imported; the model is re-implemented from the pinned
statements quoted in README.md. Deterministic generation; summary compared
against RECEIPT.json.

Run: python3 -B research/cr2-b2-audit-seed4f435ab7/verify.py
"""
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------- exact rank over F2, two independent implementations ----------

def rank_bitset(rows, ncols):
    """Rank over F2; rows are ints, bit i = column i. Gaussian elimination."""
    basis = [0] * ncols
    rank = 0
    for r in rows:
        x = r
        while x:
            piv = x.bit_length() - 1
            if basis[piv]:
                x ^= basis[piv]
            else:
                basis[piv] = x
                rank += 1
                break
    return rank


def rank_listmod2(rows, ncols):
    """Independent reference: list-of-lists elimination mod 2."""
    mat = [[(r >> c) & 1 for c in range(ncols)] for r in rows]
    rank = 0
    used = [False] * len(mat)
    for c in range(ncols):
        piv = None
        for i in range(len(mat)):
            if not used[i] and mat[i][c] == 1:
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        for i in range(len(mat)):
            if i != piv and mat[i][c] == 1:
                for cc in range(c, ncols):
                    mat[i][cc] ^= mat[piv][cc]
    return rank


# ---------- configuration model (PR #2162 section 1, re-derived) ----------

def shared_support(p, q, t, s):
    return tuple(j for j in range(3) if p[t][j] != 0 and q[s][j] != 0)


def classify(cfg):
    p, q = cfg["p"], cfg["q"]
    v = len(p)
    pi = [frozenset(j for j in range(3) if p[t][j] != 0) for t in range(v)]
    sig = [frozenset(j for j in range(3) if q[t][j] != 0) for t in range(v)]
    D = [pi[t] & sig[t] for t in range(v)]
    H = set()
    for t in range(v):
        if len(D[t]) == 2:
            i, j = sorted(D[t])
            if p[t][i] * q[t][i] == p[t][j] * q[t][j]:
                H.add(t)
    F = set(t for t in range(v) if len(pi[t]) == 3 and len(sig[t]) == 3)
    W = set()
    for t in range(v):
        for s in range(v):
            if t == s:
                continue
            if sum(p[t][j] * q[s][j] for j in range(3)) == 0:
                if len(pi[t] & sig[s]) == 3:
                    W.add((t, s))
    return pi, sig, D, H, F, W


def has_cycle(edges, verts):
    verts = list(verts)
    succ = {u: [] for u in verts}
    indeg = {u: 0 for u in verts}
    for (t, s) in edges:
        if t in succ and s in succ:
            succ[t].append(s)
            indeg[s] += 1
    stack = [u for u in verts if indeg[u] == 0]
    seen = 0
    while stack:
        u = stack.pop()
        seen += 1
        for s in succ[u]:
            indeg[s] -= 1
            if indeg[s] == 0:
                stack.append(s)
    return seen != len(verts)


def mas_vertices(W, F):
    """Largest A subseteq F with W[A] acyclic (the quantity the proof supports)."""
    best = 0
    Fl = sorted(F)
    for k in range(len(Fl), -1, -1):
        for A in itertools.combinations(Fl, k):
            A = set(A)
            if not has_cycle([e for e in W if e[0] in A and e[1] in A], A):
                return k
    return best


def mas_edges(W, F):
    """Maximum acyclic subset of the edge set W[F] (the literal MAS reading)."""
    E = sorted(e for e in W if e[0] in F and e[1] in F)
    Fl = sorted(F)
    best = 0
    for order in itertools.permutations(Fl):
        pos = {u: i for i, u in enumerate(order)}
        cnt = sum(1 for (t, s) in E if pos[t] < pos[s])
        if cnt > best:
            best = cnt
    return best


def xbest(cfg, H, W):
    """max |X| over X subseteq [v] \\ H with W[X] acyclic (Theorem B2 X-form)."""
    v = len(cfg["p"])
    rest = [t for t in range(v) if t not in H]
    best = 0
    for k in range(len(rest), -1, -1):
        for X in itertools.combinations(rest, k):
            X = set(X)
            if not has_cycle([e for e in W if e[0] in X and e[1] in X], X):
                return k
    return best


# ---------- cost and exhaustive minimum over admissible pairings ----------

def free_pairs(cfg):
    p, q = cfg["p"], cfg["q"]
    v = len(p)
    return [(t, s) for t in range(v) for s in range(v)
            if t != s and sum(p[t][j] * q[s][j] for j in range(3)) == 0]


def blocks(cfg):
    p, q = cfg["p"], cfg["q"]
    v = len(p)
    out = []
    for j in range(3):
        R = [t for t in range(v) if p[t][j] != 0]
        A = [s for s in range(v) if q[s][j] != 0]
        colidx = {s: i for i, s in enumerate(A)}
        out.append((R, A, colidx))
    return out


def cost_of(rows, blk, crosscheck=False):
    total = 0
    for (R, A, colidx) in blk:
        sub = []
        for t in R:
            bits = 0
            for s in A:
                if (rows[t] >> s) & 1:
                    bits |= 1 << colidx[s]
            sub.append(bits)
        r1 = rank_bitset(sub, len(A))
        if crosscheck:
            assert r1 == rank_listmod2(sub, len(A)), "rank implementation mismatch"
        total += r1
    return total


def min_cost_search(cfg, crosscheck=False):
    """Exhaustive minimum of cost(B) over all admissible B; returns (mincost, argmin)."""
    v = len(cfg["p"])
    fp = free_pairs(cfg)
    blk = blocks(cfg)
    base = [1 << t for t in range(v)]  # unit diagonal
    by_row = [[] for _ in range(v)]
    for k, (t, s) in enumerate(fp):
        by_row[t].append((k, s))
    best = None
    arg = None
    for mask in range(1 << len(fp)):
        rows = list(base)
        for t in range(v):
            r = rows[t]
            for (k, s) in by_row[t]:
                if (mask >> k) & 1:
                    r |= 1 << s
            rows[t] = r
        c = cost_of(rows, blk, crosscheck=(crosscheck and mask % 511 == 0))
        if best is None or c < best:
            best = c
            arg = mask
    return best, arg, len(fp)


# ---------- phi structure over F2 monomials (Theorem B2 map) ----------

def monomial(n):
    """phi(|n|) as a monomial: tuple of (prime, exponent) pairs; exponents kept."""
    n = abs(n)
    d = {}
    f = 2
    while f * f <= n:
        while n % f == 0:
            d[f] = d.get(f, 0) + 1
            n //= f
        f += 1
    if n > 1:
        d[n] = d.get(n, 0) + 1
    return tuple(sorted(d.items()))


def phi_dot(pt, qs):
    """sum_j phi(pt_j) phi(qs_j) over F2 monomials; returns set of odd monomials."""
    acc = {}
    for a, b in zip(pt, qs):
        if a != 0 and b != 0:
            m = monomial(a * b)
            acc[m] = acc.get(m, 0) ^ 1
    return set(m for m, e in acc.items() if e)


def phi0_dot(pt, qs):
    """Full collapse: every nonzero entry maps to 1; sum mod 2."""
    return sum(1 for a, b in zip(pt, qs) if a != 0 and b != 0) % 2


def structure_checks(cfg, H, W):
    """The structural facts behind B2; returns list of failed assertions."""
    p, q = cfg["p"], cfg["q"]
    v = len(p)
    fails = []
    for t in range(v):
        for s in range(v):
            inc = sum(p[t][j] * q[s][j] for j in range(3)) == 0
            kept = len(phi_dot(p[t], q[s])) == 0
            if t == s:
                if kept != (t in H):
                    fails.append(("diagonal", t))
            elif inc:
                wild = (t, s) in W
                if not wild and not kept:
                    fails.append(("nonwild_not_preserved", t, s))
                if wild and kept:
                    fails.append(("wild_preserved", t, s))
    return fails


def phi0_disagrees(cfg, H):
    p, q = cfg["p"], cfg["q"]
    for t in range(len(p)):
        if len(phi_dot(p[t], q[t])) == 0:
            continue
        if phi0_dot(p[t], q[t]) == 0:
            return True
    return False


# ---------- deterministic instance generation ----------

def gen_instance(rng, v, freecap):
    """One candidate draw; returns cfg or None."""
    p, q = [], []
    for t in range(v):
        pt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        qt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        if all(x == 0 for x in pt) or all(x == 0 for x in qt):
            return None
        if sum(a * b for a, b in zip(pt, qt)) == 0:
            return None
        if not any(a != 0 and b != 0 for a, b in zip(pt, qt)):
            return None
        p.append(pt)
        q.append(qt)
    cfg = {"p": p, "q": q}
    if len(free_pairs(cfg)) > freecap:
        return None
    return cfg


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def gen_dense(rng, v, freecap):
    """One candidate with a dense wild core on lines 0-2: p_i = cross(q_j, q_k)
    gives all six off-diagonal pairs wild whenever all supports are full."""
    qs = [tuple(rng.choice((-2, -1, 1, 2)) for _ in range(3)) for _ in range(3)]
    ps = [cross(qs[1], qs[2]), cross(qs[2], qs[0]), cross(qs[0], qs[1])]
    if any(0 in x for x in ps):
        return None
    if any(sum(a * b for a, b in zip(ps[i], qs[i])) == 0 for i in range(3)):
        return None
    p, q = list(ps), list(qs)
    for t in range(3, v):
        pt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        qt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        if all(x == 0 for x in pt) or all(x == 0 for x in qt):
            return None
        if sum(a * b for a, b in zip(pt, qt)) == 0:
            return None
        if not any(a != 0 and b != 0 for a, b in zip(pt, qt)):
            return None
        p.append(pt)
        q.append(qt)
    cfg = {"p": p, "q": q}
    if len(free_pairs(cfg)) > freecap:
        return None
    return cfg


def bucket_of(H, F, W):
    if not W:
        return "no-wild"
    if has_cycle(W, set(u for e in W for u in e)):
        return "wild-cycle"
    return "wild-acyclic"


# ---------- fixtures with analytically known answers (controls) ----------

FIXTURE_V2 = {"p": [[1, 0, 0], [0, 1, 0]], "q": [[1, 0, 0], [0, 1, 0]]}
# cost = 2 for every admissible B; H = empty, W = empty, Xbest = 2.
FIXTURE_PHI0 = {"p": [[1, 1, 0]], "q": [[1, -2, 0]]}
# |D| = 2 non-harmonic line: phi diagonal = {z2, z2^2} != 0, phi0 diagonal = 0.
FIXTURE_DENSE3 = {
    "p": [[2, -3, -1], [1, -5, 3], [-5, 4, -1]],
    "q": [[1, 2, 3], [1, 1, -1], [2, 1, 1]],
}
# All six off-diagonal pairs are wild (all supports full, p_i . q_j = 0 for
# i != j; diagonals -7). Then F = 3, masE = 3, masV = 1, mincost = 3.


def run():
    receipt = json.load(open(os.path.join(HERE, "RECEIPT.json"), encoding="utf-8"))
    rng = random.Random(receipt["seed"])
    instances = []
    counts = {}
    for v in receipt["domain_v"]:
        per = receipt["per_bucket"]
        got = {"no-wild": 0, "wild-acyclic": 0, "wild-cycle": 0}
        attempts = 0
        while min(got.values()) < per and attempts < per * 400:
            attempts += 1
            cfg = gen_instance(rng, v, receipt["free_cap"])
            if cfg is None:
                continue
            pi, sig, D, H, F, W = classify(cfg)
            b = bucket_of(H, F, W)
            if got[b] >= per:
                continue
            got[b] += 1
            instances.append((v, cfg, H, F, W, b))
        counts[v] = got
    # targeted larger-free instances (wild-dense), capped
    for _ in range(receipt["targeted_large_free"]):
        cfg = gen_instance(rng, 7, receipt["free_cap_large"])
        if cfg is None:
            continue
        pi, sig, D, H, F, W = classify(cfg)
        if len(free_pairs(cfg)) <= receipt["free_cap"]:
            continue
        instances.append((7, cfg, H, F, W, bucket_of(H, F, W)))
    # targeted dense-wild instances where the two MAS readings differ
    dense = 0
    attempts = 0
    while dense < receipt["targeted_dense_wild"] and attempts < 20000:
        attempts += 1
        v = rng.choice((4, 5, 6))
        cfg = gen_dense(rng, v, receipt["free_cap_dense"])
        if cfg is None:
            continue
        pi, sig, D, H, F, W = classify(cfg)
        if mas_edges(W, F) <= mas_vertices(W, F):
            continue
        dense += 1
        instances.append((v, cfg, H, F, W, bucket_of(H, F, W)))

    # smallest falsifying instance first
    instances.sort(key=lambda it: (it[0], len(free_pairs(it[1]))))

    results = []
    findings = {"iii_edge": None, "iii_vertex": None, "ii": None, "i": None}
    struct_fails = []
    for (v, cfg, H, F, W, bkt) in instances:
        fails = structure_checks(cfg, H, W)
        if fails:
            struct_fails.append((v, fails))
        mv = mas_vertices(W, F)
        me = mas_edges(W, F)
        xb = xbest(cfg, H, W)
        mc, arg, free = min_cost_search(cfg, crosscheck=True)
        rec = {
            "v": v, "bucket": bkt, "free": free, "H": sorted(H), "F": sorted(F),
            "W": len(W), "masV": mv, "masE": me, "xbest": xb, "mincost": mc,
        }
        results.append(rec)
        if not W and not H and mc < v and findings["i"] is None:
            findings["i"] = rec
        if not W and mc < v - len(H) and findings["ii"] is None:
            findings["ii"] = rec
        if mc < xb and findings["iii_vertex"] is None:
            findings["iii_vertex"] = rec
        if mc < v - len(H) - len(F) + me and findings["iii_edge"] is None:
            findings["iii_edge"] = rec

    # ---- controls ----
    ctrl = {}
    # Positive fixture: v = 2 no-interaction pair, exact min cost 2 = Xbest.
    pi, sig, D, H, F, W = classify(FIXTURE_V2)
    mc2, _, _ = min_cost_search(FIXTURE_V2)
    ctrl["fixture_v2_mincost_2"] = (mc2 == 2)
    ctrl["fixture_v2_xbest_2"] = (xbest(FIXTURE_V2, H, W) == 2)
    # Strengthened bound (+1) must be falsifiable: the fixture is tight.
    ctrl["strengthened_bound_detectable"] = (mc2 < xbest(FIXTURE_V2, H, W) + 1)
    # phi0 collapse must disagree with phi on some |D| = 2 non-harmonic line.
    pi, sig, D, H, F, W = classify(FIXTURE_PHI0)
    ctrl["phi0_fixture_detected"] = phi0_disagrees(FIXTURE_PHI0, H)
    dom_disagree = sum(1 for (v, cfg, Hh, Ff, Ww, _b) in instances if phi0_disagrees(cfg, Hh))
    ctrl["phi0_domain_disagreements"] = dom_disagree
    # Dense-wild fixture: masE > masV and exact min cost 3 against edge bound 3.
    pi, sig, D, H, F, W = classify(FIXTURE_DENSE3)
    mc3, _, _ = min_cost_search(FIXTURE_DENSE3)
    ctrl["fixture_dense3"] = (
        mas_edges(W, F) == 3 and mas_vertices(W, F) == 1 and mc3 == 3
        and len(W) == 6 and F == {0, 1, 2} and not H)
    ctrl["dense_domain_instances"] = sum(
        1 for r in results if r["masE"] > r["masV"])
    # Structural facts behind B2 on every instance.
    ctrl["structure_checks_clean"] = (len(struct_fails) == 0)
    # The identity Xbest == v - |H| - |F| + masV (proof-supported form).
    ident_ok = all(r["xbest"] == r["v"] - len(r["H"]) - len(r["F"]) + r["masV"]
                   for r in results)
    ctrl["xbest_identity"] = ident_ok
    # Rank double-implementation cross-check ran inside min_cost_search.
    ctrl["rank_crosscheck"] = True

    summary = {
        "instances": len(results),
        "buckets": {bkt: sum(1 for r in results if r["bucket"] == bkt)
                    for bkt in ("no-wild", "wild-acyclic", "wild-cycle")},
        "first_violation_iii_edge": findings["iii_edge"],
        "first_violation_iii_vertex": findings["iii_vertex"],
        "first_violation_ii": findings["ii"],
        "first_violation_i": findings["i"],
        "tight_iii_vertex_instances": sum(
            1 for r in results
            if r["mincost"] == r["v"] - len(r["H"]) - len(r["F"]) + r["masV"]),
        "tight_iii_edge_instances": sum(
            1 for r in results
            if r["mincost"] == r["v"] - len(r["H"]) - len(r["F"]) + r["masE"]),
        "masE_gt_masV_instances": sum(1 for r in results if r["masE"] > r["masV"]),
    }

    ok = (all(ctrl[k] for k in (
        "fixture_v2_mincost_2", "fixture_v2_xbest_2", "fixture_dense3",
        "strengthened_bound_detectable", "phi0_fixture_detected",
        "structure_checks_clean", "xbest_identity", "rank_crosscheck"))
        and ctrl["dense_domain_instances"] > 0
        and findings["iii_vertex"] is None and findings["ii"] is None
        and findings["i"] is None and not struct_fails)

    print("PASS_CR2_B2_AUDIT" if ok else "FAIL_CR2_B2_AUDIT",
          "instances=%d" % summary["instances"],
          "buckets=%s" % json.dumps(summary["buckets"], sort_keys=True))
    for k in sorted(ctrl):
        print("CONTROL %s = %s" % (k, ctrl[k]))
    for name in ("i", "ii", "iii_vertex", "iii_edge"):
        rec = findings[name]
        if rec is None:
            print("BOUND %s: no violation in declared domain" % name)
        else:
            print("BOUND %s: FALSIFIED first at v=%d free=%d mincost=%d boundrec=%s"
                  % (name, rec["v"], rec["free"], rec["mincost"], json.dumps(rec, sort_keys=True)))
    print("SUMMARY tight_iii_vertex=%d tight_iii_edge=%d masE_gt_masV=%d"
          % (summary["tight_iii_vertex_instances"], summary["tight_iii_edge_instances"],
             summary["masE_gt_masV_instances"]))
    print("DOMAIN v=%s per_bucket=%d free_cap=%d targeted_large_free=%d seed=%d"
          % (receipt["domain_v"], receipt["per_bucket"], receipt["free_cap"],
             receipt["targeted_large_free"], receipt["seed"]))
    if summary != receipt["expected_summary"]:
        print("RECEIPT MISMATCH")
        print("expected:", json.dumps(receipt["expected_summary"], sort_keys=True))
        print("actual:  ", json.dumps(summary, sort_keys=True))
        return 1
    print("RECEIPT_MATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(run())
