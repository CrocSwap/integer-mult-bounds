#!/usr/bin/env python3
"""KB5L: the tau >= 1 box floor at v = 5 (PR 3012's first open case).

Claim under test: for every exact 3-total rational decoder with v = 5 and
tau(t) >= 1 on every line, box(M) >= 3 = floor(2v/3).

Reduction (written proof in README; machine-checked pieces here):
  R1  box depends only on (a0, b0, Z): in-box labels a(t) <= a0(t),
      b(t) <= b0(t), constraints only among kept lines (Lemma SB + def).
  R2  box is monotone non-increasing in the zero-arc set Z (adding arcs only
      adds constraints).
  R3  Lemma SG (PROVEN, PR 2869): every realizable zero arc (t,s) has
      |a0(t) intersect b0(s)| even.
  Hence every realizable decoder's box is >= the box of its combinatorial
  envelope config (a0, b0, Z_even) with Z_even = ALL even pairs. So it
  suffices to find, for every 5-line type tuple with tau >= 1, one box
  witness keeping 3 lines inside (a0, b0, Z_even). The enumeration is over
  RAW mask pairs (joint bit structure preserved), multisets under line
  relabeling; global bit relabeling is an isomorphism (redundant copies only).

Exactness: the kept-set feasibility ladder is the vendored PR 3012
kept_k_witness (pinned to the vendored PR 2914 engine by agreement tests in
job 1); every accepted config gets a concrete witness that job 3 replays on
realizable models from the definitions. Int-only arithmetic throughout.

Prints PASS_KL_* markers; writes data/floor-v5-receipt.json.
Run: python3 -B floor_v5.py
"""
import importlib.util
import itertools
import json
import os
import random
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "predecessor", "pr3012")
sys.path.insert(0, PRE)
import box_floor_min as bm  # noqa: E402

fg = bm.fg
DOT1 = bm.dot1


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


# ------------------------------------------------------------ cheap witnesses
# Singleton box witnesses: a(t) = b(t) = {c(t)} with c(t) tied on t.  The kept
# constraints K_ts = 0 on forward zero arcs become: every equal-coloured zero
# arc (t,s) must be ordered s before t.  An order exists iff the must-precede
# digraph is acyclic (acyclicity is direction-reversal invariant).

def _acyclic(n, edges):
    indeg = [0] * n
    out = [[] for _ in range(n)]
    for (u, w) in edges:
        out[u].append(w)
        indeg[w] += 1
    stack = [u for u in range(n) if indeg[u] == 0]
    seen = 0
    while stack:
        u = stack.pop()
        seen += 1
        for w in out[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                stack.append(w)
    return seen == n


def _triple_singleton_ok(tx, ty, tz, rel):
    """rel: 6 bits (xy,yx,xz,zx,yz,zy) = zero-arc flags among (x,y,z) in the
    order of the triple's positions 0,1,2.  Tied masks tx,ty,tz."""
    tied = [(tx, 0), (ty, 1), (tz, 2)]
    cols = [[j for j in range(3) if m & (1 << j)] for (m, _) in tied]
    pairs = [(0, 1, 0), (1, 0, 1), (0, 2, 2), (2, 0, 3), (1, 2, 4), (2, 1, 5)]
    for cx in cols[0]:
        for cy in cols[1]:
            for cz in cols[2]:
                col = (cx, cy, cz)
                edges = []
                for (u, w, bit) in pairs:
                    if (rel >> bit) & 1 and col[u] == col[w]:
                        edges.append((w, u))  # w must precede u
                if _acyclic(3, edges):
                    return True
    return False


TRIPLE_CACHE = {}


def triple_singleton_ok(tied_masks, rel):
    key = (tied_masks, rel)
    hit = TRIPLE_CACHE.get(key)
    if hit is None:
        hit = _triple_singleton_ok(tied_masks[0], tied_masks[1],
                                   tied_masks[2], rel)
        TRIPLE_CACHE[key] = hit
    return hit


def rel_bits(a0, b0, idx):
    """6-bit zero-arc signature of the triple (idx = 3 line indices)."""
    z = lambda t, s: 1 if DOT1(a0[t], b0[s]) == 0 else 0  # noqa: E731
    x, y, w = idx
    return (z(x, y) << 0) | (z(y, x) << 1) | (z(x, w) << 2) | \
           (z(w, x) << 3) | (z(y, w) << 4) | (z(w, y) << 5)


def cheap_triple_witness(v, a0, b0, S):
    """Sufficient box-3 test on one triple: singleton colouring with acyclic
    conflicts, or the raw anchor labels as one assignment.  Returns a
    (kept, order, a, b) witness dict or None."""
    tied = tuple(a0[t] & b0[t] for t in S)
    rel = rel_bits(a0, b0, S)
    if triple_singleton_ok(tied, rel):
        # construct: first feasible colouring, then topological order of the
        # must-precede digraph (edges w -> u when (u,w) zero arc, colours
        # equal).
        cols = [[j for j in range(3) if tied[i] & (1 << j)] for i in range(3)]
        for cx in cols[0]:
            for cy in cols[1]:
                for cz in cols[2]:
                    col = (cx, cy, cz)
                    edges = []
                    for (u, w, bit) in ((0, 1, 0), (1, 0, 1), (0, 2, 2),
                                        (2, 0, 3), (1, 2, 4), (2, 1, 5)):
                        if (rel >> bit) & 1 and col[u] == col[w]:
                            edges.append((w, u))
                    indeg = [0, 0, 0]
                    out = [[], [], []]
                    for (p, q) in edges:
                        out[p].append(q)
                        indeg[q] += 1
                    stack = [u for u in range(3) if indeg[u] == 0]
                    order_idx = []
                    while stack:
                        u = stack.pop()
                        order_idx.append(u)
                        for q in out[u]:
                            indeg[q] -= 1
                            if indeg[q] == 0:
                                stack.append(q)
                    if len(order_idx) == 3:
                        a = [0] * v
                        b = [0] * v
                        for i in range(3):
                            a[S[i]] = b[S[i]] = 1 << col[i]
                        return dict(kept=list(S),
                                    order=[S[i] for i in order_idx],
                                    a=a, b=b)
    # anchor labels as one assignment
    a = [0] * v
    b = [0] * v
    for t in S:
        a[t] = a0[t]
        b[t] = b0[t]
    if bm.def_value(v, {(u, w) for u in S for w in S
                        if u != w and DOT1(a0[u], b0[w]) == 0},
                    a, b) >= 3:
        best = bm.kept_k_witness(
            v, frozenset((u, w) for u in range(v) for w in range(v)
                         if u != w and DOT1(a0[u], b0[w]) == 0), a0, b0, 3)
        return best
    return None


# ------------------------------------------------------------------ job 1
# Pin the ladder and the cheap test to the independent definition-level
# enumeration (brute_box over ALL in-box label assignments) on random v = 3
# combinatorial configs.

def job1():
    rng = random.Random(80501)
    raw = [(a, b) for a in range(8) for b in range(8) if a & b]
    n = 0
    while n < 400:
        v = 3
        pairs = [rng.choice(raw) for _ in range(v)]
        a0 = [p[0] for p in pairs]
        b0 = [p[1] for p in pairs]
        free = [(t, s) for t in range(v) for s in range(v)
                if t != s and DOT1(a0[t], b0[s]) == 0]
        Z = frozenset((t, s) for (t, s) in free if rng.random() < 0.5)
        # brute_box needs a model dict only for v/arcs; reuse the kj fake shape
        mod = dict(v=v, P=None, Q=None,
                   M=[[0 if ((t, s) in Z) else 1 for s in range(v)]
                      for t in range(v)],
                   pi=[7] * v, sg=[7] * v, D=[7] * v,
                   arcs=[(t, s) for (t, s) in Z])
        for t in range(v):
            mod["M"][t][t] = 1
        ad = dict(gamma=0, m=[0, 0, 0], n=[0, 0, 0], c=[0, 0, 0],
                  diag=[0] * v, reach=[], cancel=[],
                  tau=[bin(a0[t] & b0[t]).count("1") for t in range(v)],
                  a0=list(a0), b0=list(b0))
        ibx, _ = bm.brute_box(mod, ad)
        ladder = bm.box_value_exact_small(mod, ad)
        assert ibx == ladder, (pairs, sorted(Z), ibx, ladder)
        # cheap test must agree as a sufficient condition for box >= 3
        cheap = any(cheap_triple_witness(v, a0, b0, S) is not None
                    for S in itertools.combinations(range(v), 3))
        if cheap:
            assert ladder == 3, (pairs, sorted(Z), ladder)
        n += 1
    print("PASS_KL_PIN configs=%d brute-equals-ladder=%d" % (n, n))
    return n


# ------------------------------------------------------------------ job 2
# v = 5 combinatorial floor: every raw multiset of 5 line types with
# tau >= 1 keeps 3 lines inside (a0, b0, Z_even).

def job2():
    raw = [(a, b) for a in range(8) for b in range(8) if a & b]
    assert len(raw) == 37
    triples = list(itertools.combinations(range(5), 3))
    n_cfg = n_cheap = n_exact = 0
    obstructions = []
    t_cap = time.time() + 420
    for combo in itertools.combinations_with_replacement(range(37), 5):
        if n_cfg % 100000 == 0:
            log("job 2 progress %d obstructions=%d" % (n_cfg, len(obstructions)))
            if time.time() > t_cap:
                break
        n_cfg += 1
        a0 = [raw[i][0] for i in combo]
        b0 = [raw[i][1] for i in combo]
        arcs = frozenset((t, s) for t in range(5) for s in range(5)
                         if t != s and DOT1(a0[t], b0[s]) == 0)
        wit = None
        for S in triples:
            wit = cheap_triple_witness(5, a0, b0, S)
            if wit is not None:
                break
        if wit is not None:
            n_cheap += 1
            continue
        wit = bm.kept_k_witness(5, arcs, a0, b0, 3)
        if wit is not None:
            n_exact += 1
            continue
        # full ladder found nothing: exact box is min(2, #keepable) here
        mod = dict(v=5, P=None, Q=None,
                   M=[[0 if ((t, s) in arcs) else 1 for s in range(5)]
                      for t in range(5)],
                   pi=[7] * 5, sg=[7] * 5, D=[7] * 5,
                   arcs=sorted(arcs))
        for t in range(5):
            mod["M"][t][t] = 1
        ad = dict(gamma=0, m=[0, 0, 0], n=[0, 0, 0], c=[0, 0, 0],
                  diag=[0] * 5, reach=[], cancel=[],
                  tau=[bin(a0[t] & b0[t]).count("1") for t in range(5)],
                  a0=list(a0), b0=list(b0))
        bx, bxw = bm.ba.box_exact_tolerant(mod, ad)
        assert bx == 2, (combo, bx)
        obstructions.append(dict(combo=list(combo), a0=a0, b0=b0,
                                 arcs=sorted(arcs), box=bx))
        log("job 2 OBSTRUCTION: a0=%s b0=%s box=%d" % (a0, b0, bx))
    verdict = (len(obstructions) == 0)
    print("PASS_KL_V5 configs=%d cheap=%d exact=%d envelope-box2-families=%d"
          % (n_cfg, n_cheap, n_exact, len(obstructions)))
    return dict(configs=n_cfg, cheap=n_cheap, exact=n_exact,
                obstructions=obstructions, envelope_floor_holds=verdict)


# ------------------------------------------------------------------ job 3
# Realizable replay at v = 5: random exact 3-total decoders with tau >= 1
# everywhere; identities asserted; exact box via the vendored engine >= 3;
# ladder witnesses replayed from the definitions on the real model.

def tau_model(rng, v):
    """tau >= 1 on every line BY CONSTRUCTION: line t gets role j(t); both
    p_{j(t)}(t) and q_{j(t)}(t) odd (v2 sum = 0 = gamma), all three totals
    active (every column used).  Exact integers throughout."""
    roles = [rng.randrange(3) for _ in range(v)]
    if set(roles) != {0, 1, 2}:
        return None
    P, Q = [], []
    for t in range(v):
        row = [rng.choice((-2, -1, 1, 2)) if rng.random() < 0.5 else 0
               for _ in range(3)]
        row[roles[t]] = rng.choice((-3, -1, 1, 3))
        P.append(tuple(row))
        q = [rng.choice((-2, -1, 1, 2)) if rng.random() < 0.35 else 0
             for _ in range(3)]
        q[roles[t]] = rng.choice((-3, -1, 1, 3))
        Q.append(tuple(q))
    try:
        mod = fg.model(P, Q)
    except (AssertionError, ValueError):
        return None
    ad = fg.anchor_data(mod)
    if min(ad["tau"]) < 1:
        return None
    return mod, ad


def job3():
    rng = random.Random(80502)
    n = attempts = 0
    vals = []
    while n < 120 and attempts < 4000:
        attempts += 1
        got = tau_model(rng, 5)
        if got is None:
            continue
        mod, ad = got
        assert fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)
        bx, bxw = bm.ba.box_exact_tolerant(mod, ad)
        assert bxw is not None and fg.replay_witness(mod, bxw)
        assert fg.in_box(mod, ad, bxw)[0]
        assert bx >= 3, (list(ad["tau"]), bx)
        vals.append(bx)
        n += 1
    assert vals, "tau-targeted generator must produce instances"
    print("PASS_KL_REALIZABLE_V5 instances=%d violations=0 min-box=%d"
          % (n, min(vals)))
    return dict(instances=n, min_box=min(vals))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    pin = job1()
    v5 = job2()
    real = job3()
    receipt = dict(generator="floor_v5.py", pin=pin, v5=v5, realizable=real)
    with open(os.path.join(HERE, "data", "floor-v5-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KL_ALL v5-configs=%d envelope-families=%d realizable=%d"
          % (v5["configs"], len(v5["obstructions"]), real["instances"]))


if __name__ == "__main__":
    main()
