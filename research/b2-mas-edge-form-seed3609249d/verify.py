#!/usr/bin/env python3
"""Independent exact screen of the MAS edge form of Theorem B2 (iii) (PR #2162).

Question under test (PR #2293 open next question 1): does

    cost(B) >= v - |H| - |F| + masE

hold for every rank-3 decoder configuration and every admissible pairing B,
where masE is the largest acyclic edge subset of the wild digraph W[F]? The
printed proof of PR #2162 yields only the vertex form with masV (PR #2293
finding 4). No predecessor implementation is imported; the model is
re-implemented from the pinned statements quoted in README.md. All arithmetic
is exact (Python ints, F2 bitsets). Deterministic generation; the summary is
compared against RECEIPT.json.

Run: python3 -B research/b2-mas-edge-form-seed3609249d/verify.py
"""
import hashlib
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EXACT_FREE_CAP_BULK = 15      # every instance at or below this is exhaustive
EXACT_FREE_CAP_FLAGSHIP = 20  # first FLAGSHIP_N instances above the bulk cap
FLAGSHIP_N = 4
SEED = 20261015
ANNEAL_RESTARTS = 24
ANNEAL_PASSES = 6


# ---------- exact rank over F2, two independent implementations ----------

def rank_bitset(rows, ncols):
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
    return H, F, W


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
    """Largest A subseteq F with W[A] acyclic (vertex reading of MAS)."""
    Fl = sorted(F)
    f = len(Fl)
    idx = {u: i for i, u in enumerate(Fl)}
    ein = [[] for _ in range(f)]
    for (t, s) in W:
        if t in idx and s in idx:
            ein[idx[s]].append(idx[t])
    best = 0
    for mask in range(1, 1 << f):
        # Kahn on the induced sub-digraph.
        deg = [0] * f
        succ = [[] for _ in range(f)]
        for s in range(f):
            if not (mask >> s) & 1:
                continue
            for t in ein[s]:
                if (mask >> t) & 1:
                    succ[t].append(s)
                    deg[s] += 1
        stack = [u for u in range(f) if (mask >> u) & 1 and deg[u] == 0]
        seen = 0
        while stack:
            u = stack.pop()
            seen += 1
            for s in succ[u]:
                deg[s] -= 1
                if deg[s] == 0:
                    stack.append(s)
        if seen == bin(mask).count("1"):
            if seen > best:
                best = seen
    return best


def mas_edges(W, F):
    """Maximum acyclic edge subset of W[F] (literal edge reading of MAS)."""
    Fl = sorted(F)
    f = len(Fl)
    idx = {u: i for i, u in enumerate(Fl)}
    # inc[u][mask] = number of wild edges (t -> u) with t in mask
    inc = [[0] * (1 << f) for _ in range(f)]
    for (t, s) in W:
        if t in idx and s in idx:
            tu, us = idx[t], idx[s]
            for mask in range(1 << f):
                if (mask >> tu) & 1:
                    inc[us][mask] += 1
    dp = [-1] * (1 << f)
    dp[0] = 0
    for mask in range(1 << f):
        if dp[mask] < 0:
            continue
        for u in range(f):
            if (mask >> u) & 1:
                continue
            nmask = mask | (1 << u)
            val = dp[mask] + inc[u][mask]
            if val > dp[nmask]:
                dp[nmask] = val
    return dp[(1 << f) - 1] if f else 0


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


# ---------- cost and exact minimum over admissible pairings ----------

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


def build_rows(base, fp_by_row, mask):
    rows = list(base)
    for t, lst in fp_by_row:
        r = rows[t]
        for (k, s) in lst:
            if (mask >> k) & 1:
                r |= 1 << s
        rows[t] = r
    return rows


def min_cost_exhaustive(cfg, crosscheck=False):
    v = len(cfg["p"])
    fp = free_pairs(cfg)
    blk = blocks(cfg)
    base = [1 << t for t in range(v)]
    by_row = []
    for t in range(v):
        by_row.append((t, [(k, s) for k, (tt, s) in enumerate(fp) if tt == t]))
    best = None
    arg = None
    for mask in range(1 << len(fp)):
        rows = build_rows(base, by_row, mask)
        c = cost_of(rows, blk, crosscheck=(crosscheck and mask % 511 == 0))
        if best is None or c < best:
            best = c
            arg = mask
    return best, arg, len(fp)


def anneal_min(cfg, rng):
    """Heuristic minimiser only. Every returned candidate is scored exactly."""
    v = len(cfg["p"])
    fp = free_pairs(cfg)
    blk = blocks(cfg)
    base = [1 << t for t in range(v)]
    by_row = []
    for t in range(v):
        by_row.append((t, [(k, s) for k, (tt, s) in enumerate(fp) if tt == t]))
    n = len(fp)

    def score(mask):
        return cost_of(build_rows(base, by_row, mask), blk)

    best_mask = 0
    best = score(0)
    for _ in range(ANNEAL_RESTARTS):
        mask = rng.getrandbits(n) if n else 0
        cur = score(mask)
        for _pass in range(ANNEAL_PASSES):
            improved = False
            order = list(range(n))
            rng.shuffle(order)
            for k in order:
                cand = mask ^ (1 << k)
                c = score(cand)
                if c < cur:
                    mask, cur = cand, c
                    improved = True
            if not improved:
                break
        if cur < best:
            best, best_mask = cur, mask
    return best, best_mask, n


# ---------- deterministic instance families ----------

def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def valid(cfg):
    p, q = cfg["p"], cfg["q"]
    for t in range(len(p)):
        if all(x == 0 for x in p[t]) or all(x == 0 for x in q[t]):
            return False
        if sum(a * b for a, b in zip(p[t], q[t])) == 0:
            return False
        if not any(a != 0 and b != 0 for a, b in zip(p[t], q[t])):
            return False
    return True


def gen_random(rng, v, full):
    p, q = [], []
    for _t in range(v):
        pt = [0 if (not full and rng.random() < 0.25) else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        qt = [0 if (not full and rng.random() < 0.25) else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        p.append(pt)
        q.append(qt)
    cfg = {"p": p, "q": q}
    return cfg if valid(cfg) else None


def gen_cross_core(rng, v):
    """Dense wild 3-core (p_i = cross(q_j, q_k)) plus random extra lines."""
    qs = [tuple(rng.choice((-2, -1, 1, 2)) for _ in range(3)) for _ in range(3)]
    ps = [cross(qs[1], qs[2]), cross(qs[2], qs[0]), cross(qs[0], qs[1])]
    if any(0 in x for x in ps):
        return None
    if any(sum(a * b for a, b in zip(ps[i], qs[i])) == 0 for i in range(3)):
        return None
    p, q = list(ps), list(qs)
    for _t in range(3, v):
        pt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        qt = [0 if rng.random() < 0.25 else rng.choice((-2, -1, 1, 2))
              for _ in range(3)]
        p.append(pt)
        q.append(qt)
    cfg = {"p": p, "q": q}
    return cfg if valid(cfg) else None


def gen_hub(v):
    """Hub/coplanar-q cores: q(3) = a q(0) + b q(1) with p(i) = cross of two q's.

    For v = 4 this realizes 9 directed wild edges with masE = 5 > |F| = 4
    (see README, proposition P3). Extra lines for v > 4 are drawn from the
    same span relations where possible, else small full-support vectors.
    """
    out = []
    small = [t for t in itertools.product((1, 2), repeat=3)]
    for q0 in small:
        for q1 in small:
            for q2 in small:
                p2 = cross(q0, q1)
                p0 = cross(q1, q2)
                p1 = cross(q0, q2)
                if any(0 in x for x in (p0, p1, p2)):
                    continue
                if p0 == (0, 0, 0) or p1 == (0, 0, 0) or p2 == (0, 0, 0):
                    continue
                for a in (1, 2):
                    for b in (1, 2):
                        q3 = tuple(a * x + b * y for x, y in zip(q0, q1))
                        p3 = p1  # p3 || cross(q0,q2): edges 3->0, 3->2 only
                        cfg = {"p": [list(p0), list(p1), list(p2), list(p3)],
                               "q": [list(q0), list(q1), list(q2), list(q3)]}
                        if not valid(cfg):
                            continue
                        out.append(cfg)
                        if v > 4:
                            # Extend with twin/sum lines when they stay valid.
                            q4 = tuple(a * x + b * y for x, y in zip(q0, q2))
                            p4 = cross(q1, q2)
                            cfg5 = {"p": cfg["p"] + [list(p4)],
                                    "q": cfg["q"] + [list(q4)]}
                            if valid(cfg5):
                                out.append(cfg5)
                            if v > 5:
                                q5 = tuple(a * x + b * y for x, y in zip(q1, q2))
                                p5 = cross(q0, q1)
                                cfg6 = {"p": cfg5["p"] + [list(p5)],
                                        "q": cfg5["q"] + [list(q5)]}
                                if valid(cfg6):
                                    out.append(cfg6)
                        if len(out) >= 48:
                            return out
    return out


def gen_twinq(rng, v):
    """Direction-class cores: q directions from three base vectors with
    multiplicities, p(t) = cross of two base directions. Duplicated q
    directions multiply every zero dot, so these are the near-dense wild
    cores named in PR #2293's open next question 1 (v = 4..8)."""
    out = []
    bases = [((1, 1, 1), (1, 1, 2), (1, 2, 1)),
             ((1, 1, 2), (1, 2, 2), (2, 1, 1)),
             ((1, 2, 1), (2, 1, 2), (2, 2, 1)),
             ((2, 1, 1), (1, 2, 1), (1, 1, 2))]
    for d in bases:
        det = (d[0][0] * (d[1][1] * d[2][2] - d[1][2] * d[2][1])
               - d[0][1] * (d[1][0] * d[2][2] - d[1][2] * d[2][0])
               + d[0][2] * (d[1][0] * d[2][1] - d[1][1] * d[2][0]))
        if det == 0:
            continue
        for _ in range(400):
            assign = [rng.randrange(3) for _ in range(v)]
            pmix = [rng.randrange(3) for _ in range(v)]
            qs = [d[i] for i in assign]
            ps = []
            okp = True
            for t in range(v):
                a, b = [x for x in range(3) if x != pmix[t]]
                pt = cross(d[a], d[b])
                if 0 in pt:
                    okp = False
                    break
                ps.append(list(pt))
            if not okp:
                continue
            cfg = {"p": ps, "q": [list(x) for x in qs]}
            if valid(cfg):
                out.append(cfg)
            if len(out) >= 6:
                return out
    return out


# ---------- fixtures with analytically known answers (controls) ----------

FIXTURE_V2 = {"p": [[1, 0, 0], [0, 1, 0]], "q": [[1, 0, 0], [0, 1, 0]]}
# Analytic: H = empty, W = empty, min cost = 2 (diagonal blocks), bounds agree at 2.

FIXTURE_HARMONIC = {"p": [[1, 1, 0]], "q": [[1, 1, 0]]}
# |D| = 2 with equal terms 1 = 1: line 0 is harmonic (classification control).

FIXTURE_DENSE3 = {
    "p": [[2, -3, -1], [1, -5, 3], [-5, 4, -1]],
    "q": [[1, 2, 3], [1, 1, -1], [2, 1, 1]],
}
# All six off-diagonal pairs wild: F = 3, masE = 3 > masV = 1, min cost = 3
# (cost = 3 rank_F2 B, min rank 1 at B = all-ones). Tight for the edge form.

# Hub fixture (README proposition P3): filled in by gen_hub's first valid
# v = 4 member at runtime; expected wild digraph 9 directed edges, masE = 5,
# masV = 2, |F| = 4, min cost = 6 (3 * rank_F2 B, rank >= 2 since B = J is not
# admissible: pairs (0,3), (1,3), (3,1) have nonzero dot).


# ---------- run ----------

def instance_record(name, cfg, rng):
    v = len(cfg["p"])
    H, F, W = classify(cfg)
    fp = free_pairs(cfg)
    mv = mas_vertices(W, F)
    me = mas_edges(W, F)
    xb = xbest(cfg, H, W)
    rec = {
        "name": name, "v": v, "free": len(fp),
        "H": sorted(H), "F": sorted(F), "W": len(W),
        "masV": mv, "masE": me, "xbest": xb,
    }
    return rec, H, F, W, fp


def run():
    rpath = os.path.join(HERE, "RECEIPT.json")
    receipt = None
    if os.path.exists(rpath):
        receipt = json.load(open(rpath, encoding="utf-8"))
    rng = random.Random(SEED)
    instances = []  # (name, cfg, bucket)

    # Fixtures.
    instances.append(("fixture_v2", FIXTURE_V2, "fixture"))
    instances.append(("fixture_dense3", FIXTURE_DENSE3, "fixture"))
    hub_all = gen_hub(4)
    hub4 = hub_all[0] if hub_all else None
    assert hub4 is not None, "hub family failed to generate"
    instances.append(("fixture_hub4", hub4, "fixture"))

    # Family A: random all-full-support.
    for v in (3, 4, 5, 6, 7):
        got = 0
        for _ in range(200):
            cfg = gen_random(rng, v, full=True)
            if cfg:
                instances.append(("random_full_v%d" % v, cfg, "random-full"))
                got += 1
                if got >= 8:
                    break
    # Family B: cross-product cores.
    for v in (4, 5, 6, 7):
        got = 0
        for _ in range(200):
            cfg = gen_cross_core(rng, v)
            if cfg:
                instances.append(("cross_core_v%d" % v, cfg, "cross-core"))
                got += 1
                if got >= 8:
                    break
    # Family C: hub/coplanar-q cores (v = 4..6).
    for cfg in hub_all[:24]:
        instances.append(("hub_core_v%d" % len(cfg["p"]), cfg, "hub-core"))
    # Family D: random mixed supports.
    for v in (5, 6, 7, 8):
        got = 0
        for _ in range(200):
            cfg = gen_random(rng, v, full=False)
            if cfg:
                instances.append(("random_mixed_v%d" % v, cfg, "random-mixed"))
                got += 1
                if got >= 8:
                    break
    # Family E: direction-class (twin-q) cores, near-dense wild (large free).
    for v in (4, 5, 6, 7, 8):
        for cfg in gen_twinq(rng, v):
            instances.append(("twin_q_v%d" % v, cfg, "twin-q"))

    # Smallest falsifying instance first: (v, free, name).
    scored = []
    for i, (name, cfg, bucket) in enumerate(instances):
        rec, H, F, W, fp = instance_record(name, cfg, rng)
        if not name.startswith("fixture"):
            rec["name"] = "%s#%d" % (name, i)
        rec["bucket"] = bucket
        rec["cfg"] = cfg
        scored.append(rec)
    scored.sort(key=lambda r: (r["v"], r["free"], r["name"]))

    # Exactness plan: exhaustive at free <= BULK; the first FLAGSHIP_N
    # instances with BULK < free <= FLAGSHIP cap also exhaustive; the rest
    # heuristic-only (every candidate still scored exactly).
    flagship_left = FLAGSHIP_N
    results = []
    controls = {"rank_crosscheck": True}
    for rec in scored:
        cfg = rec["cfg"]
        free = rec["free"]
        if free <= EXACT_FREE_CAP_BULK or (
                free <= EXACT_FREE_CAP_FLAGSHIP and flagship_left > 0):
            if free > EXACT_FREE_CAP_BULK:
                flagship_left -= 1
            mc, arg, _n = min_cost_exhaustive(cfg, crosscheck=True)
            rec["method"] = "exhaustive"
        else:
            mc, arg, _n = anneal_min(cfg, rng)
            rec["method"] = "heuristic_upper_bound"
        rec["mincost"] = mc
        edge_rhs = rec["v"] - len(rec["H"]) - len(rec["F"]) + rec["masE"]
        vert_rhs = rec["v"] - len(rec["H"]) - len(rec["F"]) + rec["masV"]
        rec["edge_rhs"] = edge_rhs
        rec["vert_rhs"] = vert_rhs
        # Machine-checked identity: xbest == vertex RHS.
        assert rec["xbest"] == vert_rhs, ("xbest identity failed", rec["name"])
        results.append(rec)

    ident_ok = all(r["xbest"] == r["vert_rhs"] for r in results)

    # Controls with analytic answers.
    by_name = {r["name"]: r for r in results}
    ctrl = {}
    ctrl["fixture_v2_mincost_2"] = by_name["fixture_v2"]["mincost"] == 2
    d3 = by_name["fixture_dense3"]
    ctrl["fixture_dense3_mincost_3"] = d3["mincost"] == 3
    ctrl["fixture_dense3_masE_3_gt_masV_1"] = (d3["masE"] == 3 and d3["masV"] == 1)
    h4 = by_name["fixture_hub4"]
    ctrl["fixture_hub4_masE_5_gt_absF_4"] = (h4["masE"] == 5 and len(h4["F"]) == 4)
    ctrl["fixture_hub4_masV_2"] = h4["masV"] == 2
    ctrl["fixture_hub4_mincost_6"] = h4["mincost"] == 6
    # Sensitivity: the strengthened bound (+1) must be falsified on a fixture.
    ctrl["strengthened_bound_falsified"] = (
        d3["mincost"] < d3["edge_rhs"] + 1 or h4["mincost"] < h4["edge_rhs"] + 1)
    # Harmonic classification control.
    Hh, Fh, Wh = classify(FIXTURE_HARMONIC)
    ctrl["harmonic_classification"] = (Hh == {0} and not Fh and not Wh)
    # Mutation sensitivity: changing one entry must change the free-pair set.
    mut = {"p": [list(r) for r in FIXTURE_DENSE3["p"]],
           "q": [list(r) for r in FIXTURE_DENSE3["q"]]}
    mut["q"][0][0] += 1
    ctrl["mutation_sensitivity"] = (
        free_pairs(mut) != free_pairs(FIXTURE_DENSE3))
    # Lemma P1 side condition, machine-checked over the domain: no all-full
    # configuration at v >= 4 admits B = all-ones (some pair has nonzero dot).
    p1_ok = True
    for r in results:
        if len(r["F"]) == r["v"] and r["v"] >= 4:
            cfg = r["cfg"]
            if all(sum(a * b for a, b in zip(cfg["p"][t], cfg["q"][s]))
                   == 0 for t in range(r["v"]) for s in range(r["v"]) if t != s):
                p1_ok = False
    ctrl["p1_no_complete_pairs_v_ge_4"] = p1_ok

    # Bounds over the whole domain.
    def falsifiers(key, rhs_key):
        out = []
        for r in results:
            if r["mincost"] < r[rhs_key]:
                out.append(r)
        return out

    edge_fals = falsifiers("edge", "edge_rhs")
    vert_fals = falsifiers("vert", "vert_rhs")

    # Falsifier confirmation: every falsifier is re-minimised exhaustively and
    # its witness recomputed by the independent rank implementation.
    fals_detail = None
    for r in edge_fals + vert_fals:
        cfg = r["cfg"]
        mc, arg, _n = min_cost_exhaustive(cfg, crosscheck=True)
        assert mc == r["mincost"] or r["method"] != "exhaustive", (
            "falsifier minimum not reproducible", r["name"])
        r["mincost"] = mc
        r["method"] = "exhaustive_confirmed"
        v = len(cfg["p"])
        fp = free_pairs(cfg)
        base = [1 << t for t in range(v)]
        by_row = []
        for t in range(v):
            by_row.append((t, [(k, s) for k, (tt, s) in enumerate(fp) if tt == t]))
        rows = build_rows(base, by_row, arg)
        # Independent recomputation of cost(B) via rank_listmod2 only.
        indep = 0
        for (R, A, colidx) in blocks(cfg):
            sub = [[(rows[t] >> s) & 1 for s in A] for t in R]
            indep += rank_listmod2([sum(x << i for i, x in enumerate(row))
                                    for row in sub], len(A))
        assert indep == mc, ("independent witness recomputation failed", r["name"])
        if fals_detail is None:
            H, F, W = classify(cfg)
            fals_detail = {
                "name": r["name"], "v": r["v"], "free": r["free"],
                "H": sorted(H), "F": sorted(F),
                "W": sorted(list(W)), "masV": r["masV"], "masE": r["masE"],
                "xbest": r["xbest"], "edge_rhs": r["edge_rhs"],
                "vert_rhs": r["vert_rhs"], "mincost": mc,
                "p": cfg["p"], "q": cfg["q"],
                "B_rows": [format(rows[t], "0%db" % v)[::-1] for t in range(v)],
                "independent_recomputation": indep,
            }

    summary = {
        "instances": len(results),
        "exact": sum(1 for r in results if r["method"] == "exhaustive"),
        "heuristic_only": sum(1 for r in results if r["method"] != "exhaustive"),
        "max_free": max(r["free"] for r in results),
        "tight_edge": sum(1 for r in results if r["mincost"] == r["edge_rhs"]),
        "tight_vertex": sum(1 for r in results if r["mincost"] == r["vert_rhs"]),
        "masE_gt_masV": sum(1 for r in results if r["masE"] > r["masV"]),
        "masE_gt_absF": sum(1 for r in results if r["masE"] > len(r["F"])),
        "max_masE_minus_absF": max(r["masE"] - len(r["F"]) for r in results),
        "edge_falsifiers": len(edge_fals),
        "vertex_falsifiers": len(vert_fals),
        "ident_ok": ident_ok,
        "controls_ok": all(ctrl.values()),
    }

    # Stable digest over the proof-relevant fields of every instance.
    canon = json.dumps(
        [{k: r[k] for k in ("name", "v", "free", "H", "F", "W", "masV", "masE",
                           "xbest", "mincost", "method", "edge_rhs", "vert_rhs")}
         for r in results], sort_keys=True)
    digest = hashlib.sha256(canon.encode()).hexdigest()

    print("PASS_B2_EDGE_SCREEN instances=%d exact=%d heuristic_only=%d max_free=%d"
          % (summary["instances"], summary["exact"], summary["heuristic_only"],
             summary["max_free"]))
    if edge_fals:
        for r in edge_fals:
            print("BOUND iii_edge: FALSIFIER v=%d free=%d mincost=%d edge_rhs=%d "
                  "masE=%d method=%s name=%s"
                  % (r["v"], r["free"], r["mincost"], r["edge_rhs"], r["masE"],
                     r["method"], r["name"]))
    else:
        print("BOUND iii_edge: no falsifier in declared domain")
    if vert_fals:
        r = vert_fals[0]
        print("BOUND iii_vertex: FALSIFIED first at v=%d free=%d mincost=%d "
              "vert_rhs=%d name=%s" % (r["v"], r["free"], r["mincost"],
                                       r["vert_rhs"], r["name"]))
    else:
        print("BOUND iii_vertex: no falsifier in declared domain")
    print("IDENTITY xbest=vertex_rhs: %s on %d/%d"
          % ("ok" if ident_ok else "FAILED", summary["instances"],
             summary["instances"]))
    print("CONTROLS %s %s" % ("ok" if all(ctrl.values()) else "FAILED",
                              json.dumps(ctrl, sort_keys=True)))
    if fals_detail:
        print("FALSIFIER_DETAIL %s" % json.dumps(fals_detail, sort_keys=True))
    print("SUMMARY tight_edge=%d tight_vertex=%d masE_gt_masV=%d masE_gt_absF=%d "
          "max_masE_minus_absF=%d"
          % (summary["tight_edge"], summary["tight_vertex"], summary["masE_gt_masV"],
             summary["masE_gt_absF"], summary["max_masE_minus_absF"]))
    print("DOMAIN seed=%d exact_cap_bulk=%d exact_cap_flagship=%d flagship_n=%d "
          "families=random-full,cross-core,hub-core,random-mixed,twin-q "
          "entries=-2..2 v=3..8" % (SEED, EXACT_FREE_CAP_BULK,
                                    EXACT_FREE_CAP_FLAGSHIP, FLAGSHIP_N))
    print("DIGEST %s" % digest)

    if receipt is None:
        print("RECEIPT_PENDING (freeze RECEIPT.json from this run)")
        return 0
    expected = receipt["summary"]
    diffs = {k: (summary.get(k), expected[k]) for k in expected
             if summary.get(k) != expected[k]}
    if digest != receipt["digest"]:
        diffs["digest"] = (digest, receipt["digest"])
    ok = not diffs
    print("RECEIPT_%s" % ("MATCH" if ok else "MISMATCH"),
          "" if ok else json.dumps(diffs, sort_keys=True))
    return 0 if (ok and summary["controls_ok"] and ident_ok) else 1


if __name__ == "__main__":
    sys.exit(run())
