#!/usr/bin/env python3
"""KB5L job 2: realizable-shape analysis of the 33 v = 5 obstruction families
and the exact minimal blocking-Z enumeration, plus a bounded construction
hunt for an actual tau >= 1 falsifier with box = 2 at v = 5.

Facts used (written proofs in the README; engine-anchored definitions):
  A1  a0 omits bit j on every line  =>  p_j == 0 identically  (m_j is a
      minimum over nonzero entries, so it is attained).  Then rank(M) <= 2.
  A2  b0 omits bit j on every line  <=>  q_j == 0 or c_j > gamma (unshareable).
  A3  scope identity (iff):  dot1(a0[t], b0[s]) = 1  <=>  v2(M_ts) = gamma.
So a family with bit j in some b0 but in no a0 is unrealizable (A1+A2).

Construction reduction (exact): with P fixed, q(s) must lie in
W_s^perp = {p(t) : (t,s) zero arc}^perp, and p(s) not in W_s is necessary and
sufficient for some q(s) with p(s).q(s) != 0.  We search small-integer P,
solve integer kernels for q(s), and accept only engine-verified models.

Prints PASS_KL_* markers; writes data/family-v5-receipt.json.
Run: python3 -B family_v5.py
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


def dot3(u, w):
    return sum(x * y for x, y in zip(u, w))


def int_kernel3(rows):
    """Integer kernel basis of a set of rows in Z^3 (exact): rank 2 via cross
    products; rank 1 via two vectors orthogonal to the row; rank 0 all."""
    rows = [r for r in rows if r != (0, 0, 0)]
    if not rows:
        return [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    rank = bm.gf2_rank_int([list(r) for r in rows])
    if rank >= 3:
        return []
    if rank == 1:
        r = rows[0]
        out = []
        for i in range(3):
            e = [0, 0, 0]
            e[i] = 1
            k = (r[1] * e[2] - r[2] * e[1],
                 r[2] * e[0] - r[0] * e[2],
                 r[0] * e[1] - r[1] * e[0])
            if k != (0, 0, 0):
                g = 0
                for x in k:
                    g = _gcd(g, abs(x))
                k = tuple(x // g for x in k)
                if k not in out:
                    out.append(k)
            if len(out) == 2:
                break
        return out
    basis = []
    seen = set()
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            k = (a[1] * b[2] - a[2] * b[1],
                 a[2] * b[0] - a[0] * b[2],
                 a[0] * b[1] - a[1] * b[0])
            if k != (0, 0, 0):
                g = 0
                for x in k:
                    g = _gcd(g, abs(x))
                k = tuple(x // g for x in k)
                if k[0] < 0 or (k[0] == 0 and (k[1] < 0 or (k[1] == 0 and k[2] < 0))):
                    k = tuple(-x for x in k)
                if k not in seen:
                    seen.add(k)
                    basis.append(k)
    return basis


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# ------------------------------------------------- per-triple blocking table
# Exact: a triple of line masks is blocked (no kept 3-set inside the triple,
# any order) under a 6-bit zero-arc pattern iff kept_k_witness on the 3-line
# fake config finds nothing.  Cached on (a0 masks, b0 masks, rel).

TRIPLE_BLOCK = {}


def triple_blocked(a0t, b0t, rel):
    key = (tuple(a0t), tuple(b0t), rel)
    hit = TRIPLE_BLOCK.get(key)
    if hit is not None:
        return hit
    v = 3
    arcs = frozenset(
        (u, w) for (u, w, bit) in ((0, 1, 0), (1, 0, 1), (0, 2, 2),
                                   (2, 0, 3), (1, 2, 4), (2, 1, 5))
        if (rel >> bit) & 1)
    wit = bm.kept_k_witness(v, arcs, list(a0t), list(b0t), 3)
    res = wit is None
    TRIPLE_BLOCK[key] = res
    return res


def blocking_z_patterns(a0, b0):
    """All Z subsets of the 20 ordered pairs that block every triple (exact,
    via the per-triple tables).  Returns the list of blocking Z as 20-bit
    masks, and the minimal ones."""
    pairs = [(t, s) for t in range(5) for s in range(5) if t != s]
    pidx = {p: i for i, p in enumerate(pairs)}
    triples = list(itertools.combinations(range(5), 3))
    # per triple: allowed rel patterns (blocked)
    ok_rel = []
    for S in triples:
        rels = []
        for rel in range(64):
            a0t = [a0[t] for t in S]
            b0t = [b0[t] for t in S]
            if triple_blocked(a0t, b0t, rel):
                rels.append(rel)
        ok_rel.append(set(rels))
    # Z subsets: iterate all 2^20
    blocking = []
    tri_pairs = []
    for S in triples:
        bits = []
        for (u, w, bit) in ((0, 1, 0), (1, 0, 1), (0, 2, 2),
                            (2, 0, 3), (1, 2, 4), (2, 1, 5)):
            bits.append((pidx[(S[u], S[w])], bit))
        tri_pairs.append(bits)
    for zmask in range(1 << 20):
        good = True
        for ti in range(len(triples)):
            rel = 0
            for (pi, bit) in tri_pairs[ti]:
                if (zmask >> pi) & 1:
                    rel |= 1 << bit
            if rel not in ok_rel[ti]:
                good = False
                break
        if good:
            blocking.append(zmask)
    # minimal ones
    bset = set(blocking)
    minimal = [z for z in blocking
               if not any((z & ~(1 << i)) in bset for i in range(20)
                          if (z >> i) & 1)]
    return blocking, minimal


# ------------------------------------------------------ job F: family screen

FAMILY_LOG = None


def families_from_obstructions():
    """Re-derive the 33 envelope families exactly as floor_v5.job2 does."""
    import floor_v5 as fv
    res = fv.job2()
    obs = res["obstructions"]
    return obs


def anchor_screen(obs):
    """A1/A2 screen: reject families with bit j in some b0 but in no a0."""
    rejected, surv_rank3, surv_rank2 = [], [], []
    for ob in obs:
        a0, b0 = ob["a0"], ob["b0"]
        bits_a = set()
        bits_b = set()
        for t in range(5):
            for j in range(3):
                if a0[t] & (1 << j):
                    bits_a.add(j)
                if b0[t] & (1 << j):
                    bits_b.add(j)
        if bits_b - bits_a:
            rejected.append(dict(reason="bit-in-b0-not-in-a0", a0=a0, b0=b0))
            continue
        # bits absent from every a0 => p-column identically zero (A1)
        missing = {0, 1, 2} - bits_a
        if missing:
            surv_rank2.append(dict(a0=a0, b0=b0, zero_p_columns=sorted(missing)))
        else:
            surv_rank3.append(dict(a0=a0, b0=b0))
    return rejected, surv_rank3, surv_rank2


# ------------------------------------------- job G: direct falsifier search
# Generators: PR 3012's three families (vendored logic re-derived minimally)
# plus a nullspace-driven dense-zero generator aimed at the surviving shapes.

def rand_dec(rng, v, val_bits=(0, 1, 2, 3), p_zero=0.30):
    def ent():
        if rng.random() < p_zero:
            return 0
        mag = rng.choice(val_bits)
        return rng.choice((-1, 1)) * (1 << mag)
    P = [tuple(ent() for _ in range(3)) for _ in range(v)]
    Q = [tuple(ent() for _ in range(3)) for _ in range(v)]
    try:
        mod = fg.model(P, Q)
    except (AssertionError, ValueError):
        return None
    ad = fg.anchor_data(mod)
    if min(ad["tau"]) < 1:
        return None
    return mod, ad


def extend_core(rng, v=5):
    P = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    Q = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    pool = [-3, -2, -1, 1, 2, 3]
    for _ in range(v - 3):
        P.append(tuple(rng.choice(pool) for _ in range(3)))
        q = [rng.choice(pool) for _ in range(2)]
        q.append(rng.choice((-2, 2, -4, 4)))
        Q.append(tuple(q))
    try:
        mod = fg.model(P, Q)
    except (AssertionError, ValueError):
        return None
    ad = fg.anchor_data(mod)
    if min(ad["tau"]) < 1:
        return None
    return mod, ad


def nullspace_dense(rng, v=5):
    """Dense-zero construction: pick P small-integer rank 3; for each s pick
    q(s) inside the integer kernel of {p(t) : (t,s) targeted zero} so that
    p(s).q(s) != 0.  Zero pattern randomized dense."""
    pool = [-3, -2, -1, 1, 2, 3]
    P = [tuple(rng.choice(pool) for _ in range(3)) for _ in range(v)]
    if bm.gf2_rank_int(P) != 3:
        return None
    Q = []
    for s in range(v):
        zpre = [t for t in range(v) if t != s and rng.random() < 0.65]
        rows = [P[t] for t in zpre]
        ker = int_kernel3(rows)
        cands = []
        for k in ker:
            for sc in (1, -1, 2, -2):
                q = tuple(sc * x for x in k)
                if dot3(P[s], q) != 0:
                    cands.append(q)
        if not cands:
            return None
        Q.append(rng.choice(cands))
    try:
        mod = fg.model(P, Q)
    except (AssertionError, ValueError):
        return None
    ad = fg.anchor_data(mod)
    if min(ad["tau"]) < 1:
        return None
    return mod, ad


def job_g(target=600):
    import floor_v5 as fv

    def tau_targeted(rng, v):
        return fv.tau_model(rng, v)

    rng = random.Random(20261016)
    gens = [("tau_targeted", tau_targeted), ("extend_core", extend_core),
            ("nullspace_dense", nullspace_dense)]
    tested = {g[0]: 0 for g in gens}
    attempts = {g[0]: 0 for g in gens}
    hits = []
    n = 0
    v = 5
    k = (2 * v) // 3
    while n < target:
        name, gen = gens[n % 3]
        attempts[name] += 1
        if attempts[name] > 20000:
            break
        got = gen(rng, v)
        if got is None:
            continue
        mod, ad = got
        n += 1
        tested[name] += 1
        arcs = frozenset(mod["arcs"])
        wit = bm.kept_k_witness(v, arcs, ad["a0"], ad["b0"], k)
        if wit is None:
            bx, bxw = bm.ba.box_exact_tolerant(mod, ad)
            ce, cew = fg.cert_exact(mod, max_v=v)
            assert fg.replay_witness(mod, cew)
            assert bx < k, (v, bx, k)
            hits.append(dict(family=name, cert=ce, box=bx,
                             P=[list(p) for p in mod["P"]],
                             Q=[list(q) for q in mod["Q"]],
                             tau=list(ad["tau"])))
            log("G HIT family=%s cert=%d box=%d" % (name, ce, bx))
        if n % 500 == 0:
            log("job G progress %d attempts=%s" % (n, attempts))
    print("PASS_KL_HUNT tested=%d hits=%d attempts=%s"
          % (n, len(hits), json.dumps(attempts, sort_keys=True)))
    return dict(tested=tested, attempts=attempts, hits=hits)


# ------------------------------------------------- job D: diagnostic probe

def job_d():
    """Why did the naive generator produce no tau >= 1 instance at v = 5?
    Instrumented counts (exact)."""
    rng = random.Random(777)
    counts = dict(model_ok=0, model_fail=0, tau_all=0, tau_hist={})
    for _ in range(400):
        mod = bm.rand_model(rng, 5, val_bits=(0, 1, 2, 3))
        if mod is None:
            counts["model_fail"] += 1
            continue
        counts["model_ok"] += 1
        ad = fg.anchor_data(mod)
        t = tuple(sorted(ad["tau"]))
        counts["tau_hist"][str(t)] = counts["tau_hist"].get(str(t), 0) + 1
        if min(ad["tau"]) >= 1:
            counts["tau_all"] += 1
    log("job D: %s" % json.dumps(counts, sort_keys=True))
    print("PASS_KL_PROBE model-ok=%d tau>=1-all=%d"
          % (counts["model_ok"], counts["tau_all"]))
    return counts


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    probe = job_d()
    obs = families_from_obstructions()
    rejected, surv3, surv2 = anchor_screen(obs)
    log("anchor screen: rejected=%d surv-rank3=%d surv-rank2=%d"
        % (len(rejected), len(surv3), len(surv2)))
    # minimal blocking Z per surviving shape (bit-relabeling: dedupe shapes)
    shapes = []
    seen = set()
    for fam in surv3 + surv2:
        key = (tuple(fam["a0"]), tuple(fam["b0"]))
        # canonical under total relabeling
        best = None
        for perm in itertools.permutations(range(3)):
            def mv(x):
                y = 0
                for j in range(3):
                    if x & (1 << j):
                        y |= 1 << perm[j]
                return y
            cand = (tuple(mv(x) for x in fam["a0"]),
                    tuple(mv(x) for x in fam["b0"]))
            if best is None or cand < best:
                best = cand
        if best in seen:
            continue
        seen.add(best)
        shapes.append(fam)
    blocking_rec = []
    for fam in shapes:
        blocking, minimal = blocking_z_patterns(fam["a0"], fam["b0"])
        log("shape a0=%s b0=%s: blocking=%d minimal=%d"
            % (fam["a0"], fam["b0"], len(blocking), len(minimal)))
        blocking_rec.append(dict(fam=fam, n_blocking=len(blocking),
                                 n_minimal=len(minimal),
                                 minimal_masks=minimal[:64]))
    print("PASS_KL_SHAPES shapes=%d screen-rejected=%d" % (len(shapes),
                                                           len(rejected)))
    hunt = job_g()
    receipt = dict(generator="family_v5.py", probe=probe,
                   screen=dict(rejected=len(rejected), rank3=len(surv3),
                               rank2=len(surv2)),
                   shapes=blocking_rec, hunt=hunt)
    with open(os.path.join(HERE, "data", "family-v5-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KL_FAMILY_ALL shapes=%d hunt-tested=%d hunt-hits=%d"
          % (len(shapes), sum(hunt["tested"].values()), len(hunt["hits"])))


if __name__ == "__main__":
    main()
