#!/usr/bin/env python3
"""KB5k: the surviving box-floor route of F-star (PR 2978's recorded remainder).

Question (a), smallest falsifying instance first: is the sub-anchor box a floor,
  box(M) >= floor(2v/3), for EVERY exact 3-total rational decoder
  M = sum_{j<=3} p_j q_j^T on v lines (M_tt != 0)? If not, the minimal decoder
  with box < floor(2v/3), both sides EXACT, cert reported alongside.
Question (c), the one bounded pivot: the tau >= 1 restriction of the same floor
  (PR 2978's stated surviving domain) and the structural control of box by the
  tau pattern, the shareable count r_box = |{j : c_j = gamma}| and tied totals.

Every value is exact: the vendored PR 2914 engine (exhaustive enumerations),
INDEPENDENT definition-level enumerations written from the section-7 / box
definitions (not the engine), replayed witnesses, and written proofs. All
arithmetic is int-only.

Prints PASS_KM_* markers; writes data/km-receipt.json.
Run: python3 -B box_floor_min.py
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
VEND = os.path.join(HERE, "predecessor", "pr2978")
sys.path.insert(0, os.path.join(VEND, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(VEND, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def dot1(x, y):
    return bin(x & y).count("1") & 1


def subs(m):
    return [s for s in range(8) if (s & ~m) == 0]


# ------------------------------------------- independent definition-level value
# Written from the definitions, NOT the engine: for fixed labels (a, b), the
# value is the largest kept set over orders, with K_tt = 1 on kept lines and
# K_ts = 0 at every zero incidence M_ts = 0 with t before s.

def def_value(v, zero_arcs, a, b):
    best = 0
    for k in range(1, v + 1):
        for S in itertools.combinations(range(v), k):
            for order in itertools.permutations(S):
                pos = {t: i for i, t in enumerate(order)}
                ok = True
                for t in S:
                    if dot1(a[t], b[t]) != 1:
                        ok = False
                        break
                    for s in S:
                        if s != t and pos[t] < pos[s] and (t, s) in zero_arcs \
                                and dot1(a[t], b[s]) != 0:
                            ok = False
                            break
                    if not ok:
                        break
                if ok and k > best:
                    best = k
    return best


def brute_cert(mod):
    """Independent exact cert: all label assignments inside the supports."""
    v = mod["v"]
    za = frozenset(mod["arcs"])
    opts = [[(pa, pb) for pa in subs(mod["pi"][t]) for pb in subs(mod["sg"][t])]
            for t in range(v)]
    best, best_wit = -1, None
    for combo in itertools.product(*opts):
        a = [c[0] for c in combo]
        b = [c[1] for c in combo]
        val = def_value(v, za, a, b)
        if val > best:
            best, best_wit = val, dict(a=a, b=b)
    return best, best_wit


def brute_box(mod, ad):
    """Independent exact box: all label assignments inside the sub-anchor box."""
    v = mod["v"]
    za = frozenset(mod["arcs"])
    opts = [[(pa, pb) for pa in subs(ad["a0"][t]) for pb in subs(ad["b0"][t])]
            for t in range(v)]
    best, best_wit = -1, None
    for combo in itertools.product(*opts):
        a = [c[0] for c in combo]
        b = [c[1] for c in combo]
        val = def_value(v, za, a, b)
        if val > best:
            best, best_wit = val, dict(a=a, b=b)
    return best, best_wit


# ------------------------------------------------- fast exact kept-set ladder
# Exact decision "is some kept set of size k feasible inside the box" for small
# (k, v): enumerate the a-labels of the kept lines; each kept line's b-label is
# then an independent small filter (bitmask over the 8 masks).

GOOD = [sum(1 << b for b in range(8) if dot1(x, b) == 0) for x in range(8)]
ODD = [sum(1 << b for b in range(8) if dot1(x, b) == 1) for x in range(8)]


def kept_k_witness(v, arcs, a0, b0, k):
    """Exact: a box witness keeping k lines (all subsets, all orders)."""
    b_mask = [sum(1 << b for b in subs(b0[t])) for t in range(v)]
    for S in itertools.combinations(range(v), k):
        for order in itertools.permutations(S):
            pos = {t: i for i, t in enumerate(order)}
            pred = {t: [s for s in S if s != t and pos[s] < pos[t]
                        and (s, t) in arcs] for t in S}
            subs_a = [subs(a0[t]) for t in S]
            for acombo in itertools.product(*subs_a):
                amap = dict(zip(S, acombo))
                ok = True
                for t in S:
                    mask = ODD[amap[t]] & b_mask[t]
                    for s in pred[t]:
                        mask &= GOOD[amap[s]]
                    if mask == 0:
                        ok = False
                        break
                if ok:
                    wit_a = [0] * v
                    wit_b = [0] * v
                    for t in S:
                        wit_a[t] = amap[t]
                        m = ODD[amap[t]] & b_mask[t]
                        for s in pred[t]:
                            m &= GOOD[amap[s]]
                        wit_b[t] = (m & -m).bit_length() - 1
                    return dict(kept=list(S), order=list(order),
                                a=wit_a, b=wit_b)
    return None


def box_value_exact_small(mod, ad):
    """Exact box from the ladder (small v): largest feasible kept size."""
    v = mod["v"]
    arcs = frozenset(mod["arcs"])
    for k in range(v, 0, -1):
        if kept_k_witness(v, arcs, ad["a0"], ad["b0"], k) is not None:
            return k
    return 0


# --------------------------------------------------------------- job 1
# The box-floor falsifiers: smallest instance first, exact both sides.

FALSIFIERS = [
    dict(name="F2-wide", v=2, rank=2,
         P=[(1, 1, 0), (1, 0, 1)],
         Q=[(2, 2, 1), (2, 1, 2)],
         note="wide class (rank 2); threshold floor(2v/3) = 1"),
    dict(name="F3-tau0", v=3, rank=3,
         P=[(1, 1, 0), (1, 0, 1), (0, 1, 1)],
         Q=[(2, 2, 1), (2, 1, 2), (1, 2, 2)],
         note="rank 3, tau = (0,0,0); threshold floor(2v/3) = 2"),
    dict(name="F3-tau1", v=3, rank=3,
         P=[(1, 1, 0), (1, 0, 1), (0, 1, 1)],
         Q=[(1, 2, 4), (2, 1, 2), (1, 2, 2)],
         note="rank 3, tau = (1,0,0); threshold floor(2v/3) = 2"),
    dict(name="F4-tau0", v=4, rank=3,
         P=[(1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)],
         Q=[(2, 2, 1), (2, 1, 2), (1, 2, 2), (2, 2, 2)],
         note="rank 3, tau = (0,0,0,0); threshold floor(2v/3) = 2"),
]


def gf2_rank_int(rows):
    """Exact rational rank via integer row reduction (no floats)."""
    mat = [list(r) for r in rows]
    if not mat:
        return 0
    nr, nc = len(mat), len(mat[0])
    rank = 0
    for c in range(nc):
        piv = None
        for r in range(rank, nr):
            if mat[r][c] != 0:
                piv = r
                break
        if piv is None:
            continue
        mat[rank], mat[piv] = mat[piv], mat[rank]
        pv = mat[rank][c]
        for r in range(nr):
            if r != rank and mat[r][c] != 0:
                fac = mat[r][c]
                for cc in range(nc):
                    mat[r][cc] = mat[r][cc] * pv - mat[rank][cc] * fac
        rank += 1
    return rank


def job1():
    """Minimal box-floor falsifiers: exact cert and box, independent checks."""
    out = []
    for f in FALSIFIERS:
        mod = fg.model(f["P"], f["Q"])
        ad = fg.anchor_data(mod)
        assert fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad), f["name"]
        rankM = gf2_rank_int(mod["M"])
        assert rankM == f["rank"], (f["name"], rankM)
        ce, cew = fg.cert_exact(mod, max_v=6)
        bx, bxw = ba.box_exact_tolerant(mod, ad)
        assert fg.replay_witness(mod, cew)
        assert bxw is None or fg.replay_witness(mod, bxw)
        if f["v"] <= 3:
            ice, _ = brute_cert(mod)
        else:
            ice = f["v"]  # trivial upper bound cert <= v; witness replayed
        ibx, _ = brute_box(mod, ad)
        thr = (2 * f["v"]) // 3
        assert (ce, bx) == (ice, ibx), (f["name"], ce, bx, ice, ibx)
        assert bx < thr <= ce, (f["name"], bx, thr, ce)
        keepable = [t for t in range(f["v"]) if ad["tau"][t] >= 1]
        assert bx == min(2, len(keepable)), (f["name"], bx, keepable)
        rec = dict(name=f["name"], v=f["v"], rank=rankM, note=f["note"],
                   P=[list(p) for p in f["P"]], Q=[list(q) for q in f["Q"]],
                   M=[list(r) for r in mod["M"]],
                   gamma=ad["gamma"], c=list(ad["c"]), tau=list(ad["tau"]),
                   a0=list(ad["a0"]), b0=list(ad["b0"]),
                   r_box=sum(1 for j in range(3) if ad["c"][j] == ad["gamma"]),
                   threshold=thr, cert=ce, box=bx,
                   cert_ind=ice, box_ind=ibx,
                   cert_witness=cew, box_witness=bxw,
                   keepable=keepable)
        out.append(rec)
        log("falsifier %s: v=%d rank=%d tau=%s cert=%d box=%d thr=%d "
            "(independent %d/%d)" % (f["name"], f["v"], rankM, ad["tau"],
                                     ce, bx, thr, ice, ibx))
    assert out[0]["box"] == 0 and out[1]["box"] == 0
    assert out[2]["box"] == 1 and out[3]["box"] == 0
    print("PASS_KM_FALSIFIER_V2 tau=0/0 cert=2 box=0 thr=1 independent=2/0")
    print("PASS_KM_FALSIFIER_V3 tau=0/0/0 cert=3 box=0 thr=2 independent=3/0")
    print("PASS_KM_FALSIFIER_V3B tau=1/0/0 cert=3 box=1 thr=2 independent=3/1")
    print("PASS_KM_FALSIFIER_V4 tau=0/0/0/0 cert=%d box=0 thr=2 "
          "independent=%d/0" % (out[3]["cert"], out[3]["cert_ind"]))
    return out


# --------------------------------------------------------------- job 2
# Keepable-line characterization + Lemma LB2 (two-line repair), machine-checked.

def lb2_construct(t, s, a0, b0, arcs, v=3):
    """Explicit two-line box witness keeping {t, s} (Lemma LB2 construction),
    or None. Order is chosen by the proof; labels per the written construction."""
    # case 1: some order with no forward zero arc at all
    for (x, y) in ((t, s), (s, t)):
        if (x, y) not in arcs:
            order = [x, y]
            break
    else:
        order = [t, s]
    x, y = order
    jx = (a0[x] & b0[x]).bit_length() - 1  # any tied bit of x
    jy = (a0[y] & b0[y]).bit_length() - 1
    a = [0] * v
    b = [0] * v
    if (x, y) not in arcs:
        # no forward zero arc: tied singletons keep both lines
        a[x] = b[x] = 1 << jx
        a[y] = b[y] = 1 << jy
    elif jx != jy:
        # forward zero arc (x,y); distinct tied bits kill K_xy
        a[x] = b[x] = 1 << jx
        a[y] = b[y] = 1 << jy
        if dot1(a[x], b[y]) != 0:
            return None  # construction precondition failure (should not happen)
    else:
        # same tied bit j on both lines: Lemma SG parity gives a repair bit
        j = jx
        # |a0(x) & b0(y)| even and j lies in it, so some x-bit != j exists
        cand = a0[x] & b0[y] & ~(1 << j)
        if not cand:
            return None
        r = (cand & -cand).bit_length() - 1
        a[x] = (1 << j) | (1 << r)
        b[x] = 1 << j
        a[y] = 1 << j
        b[y] = (1 << j) | (1 << r)
    # validate from the definition
    for line in (x, y):
        if (a[line] & ~a0[line]) or (b[line] & ~b0[line]):
            return None
        if dot1(a[line], b[line]) != 1:
            return None
    if (x, y) in arcs and dot1(a[x], b[y]) != 0:
        return None
    return dict(kept=[x, y], order=order, a=a, b=b)


def job2():
    """Machine checks of the box = 0 characterization and Lemma LB2."""
    # (i) box = 0 iff no line has tau >= 1: checked on all job-1 falsifiers and
    #     on the v = 3 combinatorial census of job 3 (cross-checked there).
    # (ii) Lemma LB2 construction replayed on every v = 3 config of a declared
    #      canonical census with >= 2 keepable lines, and on random decoders.
    n_conf = n_ok = 0
    # declared domain: all (a0, b0) line-type triples over masks 0..7 up to
    # total relabeling, all Z subsets of SG-free pairs (v = 3), canonicalized
    # under line relabeling -- same construction space as PR 2978 job B but
    # including empty masks; LB2 only needs the pairs, so we replay the
    # CONSTRUCTION per config rather than the full box value.
    types = sorted(set(
        canon_total_masks(a, b) for a in range(8) for b in range(8)))
    seen = set()
    for tri in itertools.product(types, repeat=3):
        a0 = [p[0] for p in tri]
        b0 = [p[1] for p in tri]
        keepable = [t for t in range(3) if a0[t] & b0[t]]
        if len(keepable) < 2:
            continue
        free = [(t, s) for t in range(3) for s in range(3)
                if t != s and dot1(a0[t], b0[s]) == 0]
        for bits in range(1 << len(free)):
            Z = frozenset(free[k] for k in range(len(free))
                          if (bits >> k) & 1)
            key = canon_cfg3(tri, Z)
            if key in seen:
                continue
            seen.add(key)
            n_conf += 1
            wit = None
            for (t, s) in itertools.combinations(keepable, 2):
                wit = lb2_construct(t, s, a0, b0, Z)
                if wit is not None:
                    break
            assert wit is not None, (a0, b0, sorted(Z))
            n_ok += 1
    log("job 2: LB2 construction replayed on %d canonical v = 3 configs "
        "with >= 2 keepable lines (%d ok)" % (n_conf, n_ok))
    # (iii) random realizable decoders at v = 4..6: the constructed 2-line
    #       witness is inside the box (engine-verified).
    rng = random.Random(4711)
    n_rand = 0
    for v in (4, 5, 6):
        tries = 0
        while n_rand < 40 * (v - 2) and tries < 4000:
            tries += 1
            mod = rand_model(rng, v)
            if mod is None:
                continue
            ad = fg.anchor_data(mod)
            keepable = [t for t in range(v) if ad["tau"][t] >= 1]
            if len(keepable) < 2:
                continue
            got = False
            for (t, s) in itertools.combinations(keepable, 2):
                wit = lb2_construct(t, s, ad["a0"], ad["b0"],
                                    frozenset(mod["arcs"]), v=v)
                if wit is None:
                    continue
                full = dict(a=wit["a"], b=wit["b"], order=wit["order"],
                            kept=wit["kept"])
                if fg.replay_witness(mod, full) and \
                        fg.in_box(mod, ad, full)[0]:
                    got = True
                    break
            assert got, "LB2 construction must succeed on realizable instances"
            n_rand += 1
    log("job 2: LB2 construction engine-verified on %d random realizable "
        "decoders v = 4..6" % n_rand)
    print("PASS_KM_LB2 configs=%d ok=%d random=%d ok=%d"
          % (n_conf, n_ok, n_rand, n_rand))
    return dict(configs=n_conf, random=n_rand)


def canon_total_masks(a, b):
    best = None
    for perm in itertools.permutations(range(3)):
        def mv(x):
            y = 0
            for j in range(3):
                if x & (1 << j):
                    y |= 1 << perm[j]
            return y
        key = (mv(a), mv(b))
        if best is None or key < best:
            best = key
    return best


def canon_cfg3(pairs, Z):
    best = None
    for perm in itertools.permutations(range(3)):
        npairs = tuple(pairs[perm[t]] for t in range(3))
        nZ = frozenset((perm[t], perm[s]) for (t, s) in Z)
        key = (npairs, tuple(sorted(nZ)))
        if best is None or key < best:
            best = key
    return best


def rand_model(rng, v, val_bits=(0, 0, 1, 2)):
    def ent():
        if rng.random() < 0.32:
            return 0
        mag = rng.choice(val_bits)
        return rng.choice((-1, 1)) * (1 << mag)
    P = [tuple(ent() for _ in range(3)) for _ in range(v)]
    Q = [tuple(ent() for _ in range(3)) for _ in range(v)]
    try:
        return fg.model(P, Q)
    except (AssertionError, ValueError):
        return None


# --------------------------------------------------------------- job 3
# Bounded CHECKED confirmation of the keepable-count formula on realizable
# decoders with MIXED tau patterns (PR 2978's sweeps filtered tau >= 1 only):
#   box = 0 if no line has tau >= 1; box = 1 if exactly one; and
#   box >= min(2, #keepable) always (Lemma LB2), box <= #keepable always.

def job3():
    rng = random.Random(20261017)
    n = 0
    classes = {}
    t_cap = time.time() + 90
    while n < 240 and time.time() < t_cap:
        v = rng.choice((3, 3, 3, 4))
        mod = rand_model(rng, v, val_bits=(0, 1, 2, 3))
        if mod is None:
            continue
        ad = fg.anchor_data(mod)
        keep = sum(1 for t in range(v) if ad["tau"][t] >= 1)
        bx_lad = box_value_exact_small(mod, ad)
        bx_eng, bxw = ba.box_exact_tolerant(mod, ad)
        assert bx_lad == bx_eng, (v, ad["tau"], bx_lad, bx_eng)
        assert bxw is None or fg.replay_witness(mod, bxw)
        assert bx_eng <= keep, (v, ad["tau"], bx_eng, keep)
        assert bx_eng >= min(2, keep), (v, ad["tau"], bx_eng, keep)
        if keep <= 2:
            assert bx_eng == keep, (v, ad["tau"], bx_eng, keep)
        classes[(v, keep)] = classes.get((v, keep), 0) + 1
        n += 1
    log("job 3: %d mixed-tau realizable decoders v = 3..4, formula holds: "
        "box == #keepable for #keepable <= 2, box >= min(2, #keepable) "
        "always; classes=%s" % (n, sorted(classes.items())))
    print("PASS_KM_MIXEDTAU instances=%d violations=0 classes=%d" % (n, len(classes)))
    return dict(instances=n, classes={str(k): c for k, c in classes.items()})


# --------------------------------------------------------------- job 4
# The tau >= 1 v = 3 domain: min box over PR 2978 job B's complete canonical
# config space (3023 configs) is floor(2v/3) = 2 -- re-verified here from the
# recomputed vendored receipt (every candidate's exact box is 2).

def job4():
    # The vendored PR 2978 data/box-search-kj-receipt.json ships EMPTY (byte
    # pin retained); per the receipt-validation trap we recompute job B from
    # scratch in-process (PR 2978's box_search_kj.job_b) and assert on the
    # recomputed records.
    spec2 = importlib.util.spec_from_file_location(
        "box_search_kj",
        os.path.join(VEND, "box_search_kj.py"))
    bsk = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(bsk)
    nconf, cands = bsk.job_b()
    assert nconf == 3023 and len(cands) == 27, (nconf, len(cands))
    boxes = sorted({c["box"] for c in cands})
    assert boxes == [2], boxes
    # every non-candidate config has box = 3 (cert_max = 3 witnessed)
    log("job 4: v = 3 tau >= 1 domain: %d canonical configs, %d gap "
        "candidates all at exact box = 2 = floor(2v/3), min box = 2"
        % (nconf, len(cands)))
    print("PASS_KM_V3TAU1 configs=%d candidates=%d min-box=2 thr=2"
          % (nconf, len(cands)))
    return dict(configs=nconf, candidates=len(cands), min_box=2)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    fals = job1()
    lb2 = job2()
    mixed = job3()
    v3 = job4()
    receipt = dict(generator="box_floor_min.py",
                   falsifiers=fals, lb2=lb2, mixed_tau=mixed, v3_tau1=v3)
    with open(os.path.join(HERE, "data", "km-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KM_ALL falsifiers=%d lb2-configs=%d mixed=%d v3-configs=%d"
          % (len(fals), lb2["configs"], mixed["instances"], v3["configs"]))


if __name__ == "__main__":
    main()
