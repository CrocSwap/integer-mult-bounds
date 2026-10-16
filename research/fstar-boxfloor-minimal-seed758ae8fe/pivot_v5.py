#!/usr/bin/env python3
"""KB5k pivot (one bounded): the box floor on the tau >= 1 domain.

PR 2978's stated surviving domain for the box-floor route is tau(t) >= 1
everywhere. Lemma LB2 (box_floor_min.py) proves the floor for v <= 4 there
(threshold floor(2v/3) <= 2), so v = 5 (threshold 3) is the first open case.
This script searches for the smallest tau >= 1 decoder with box <= 2 at v = 5,
exact on every reported value, and records the structural features (tau
pattern, shareable count r_box, zero-arc density) of every instance.

Falsifier criterion is EXACT and fast: box <= 2 iff NO kept set of size 3 is
feasible inside the sub-anchor box (kept_k_witness ladder, exhaustive a-label
enumeration with per-line b-mask filtering). On a hit, the exact box and cert
are recomputed by the vendored PR 2914 engine.

Writes data/pivot-v5-receipt.json. Run: python3 -B pivot_v5.py
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
sys.path.insert(0, HERE)
from box_floor_min import kept_k_witness, gf2_rank_int, log  # noqa: E402


def features(mod, ad):
    v = mod["v"]
    arcs = mod["arcs"]
    return dict(v=v, tau=list(ad["tau"]),
                r_box=sum(1 for j in range(3) if ad["c"][j] == ad["gamma"]),
                c=list(ad["c"]), gamma=ad["gamma"],
                n_zero_arcs=len(arcs),
                zero_density=len(arcs) / (v * (v - 1)))


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
    if gf2_rank_int(mod["M"]) != 3:
        return None
    return mod, ad


def extend_2978(rng, v=5):
    """PR 2978's minimal counterexample core (M = diag(8, 8, 12), r_box = 2)
    plus (v - 3) new lines with small integer entries, q-column 2 kept even
    (so total 2 stays non-shareable and r_box = 2), tau >= 1 on new lines."""
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
    if gf2_rank_int(mod["M"]) != 3:
        return None
    return mod, ad


def unit_template(rng, v=5):
    """Role-template family: q(s) = e_{j(s)} (scaled), p(t) sparse with
    p_{j(t)}(t) odd; total 2 forced non-shareable through even q-column 2.
    Dense zero arcs by design (M_ts = p_{j(s)}(t))."""
    roles = [rng.randrange(3) for _ in range(v)]
    if len(set(roles)) < 3:
        return None
    q_scale = [rng.choice((1, -1, 1, 3, -3)) for _ in range(v)]
    P, Q = [], []
    for t in range(v):
        row = [0, 0, 0]
        for j in range(3):
            if rng.random() < 0.45:
                row[j] = rng.choice((-3, -2, -1, 1, 2, 3))
        if row[roles[t]] == 0 or row[roles[t]] % 2 == 0:
            row[roles[t]] = rng.choice((-3, -1, 1, 3))
        P.append(tuple(row))
        q = [0, 0, 0]
        q[roles[t]] = q_scale[t]
        for j in range(3):
            if j != roles[t] and rng.random() < 0.18:
                q[j] = rng.choice((-2, 2, -4, 4))  # even: keeps n_2 >= 1
        Q.append(tuple(q))
    try:
        mod = fg.model(P, Q)
    except (AssertionError, ValueError):
        return None
    ad = fg.anchor_data(mod)
    if min(ad["tau"]) < 1:
        return None
    if gf2_rank_int(mod["M"]) != 3:
        return None
    return mod, ad


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rng = random.Random(20261016)
    gens = [("random", rand_dec), ("extend2978", extend_2978),
            ("unit_template", unit_template)]
    tested = {"random": 0, "extend2978": 0, "unit_template": 0}
    hits = []
    dist = {}
    n = 0
    v = 5
    k = (2 * v) // 3  # threshold: falsifier needs box < k, i.e. no k-kept
    target = 240  # deterministic instance count (no wall-clock dependence)
    while n < target:
        name, gen = gens[n % 3]
        got = gen(rng, v)
        if got is None:
            continue
        mod, ad = got
        n += 1
        tested[name] += 1
        arcs = frozenset(mod["arcs"])
        wit = kept_k_witness(v, arcs, ad["a0"], ad["b0"], k)
        ft = features(mod, ad)
        key = (v, ft["r_box"], tuple(ft["tau"]), wit is None)
        dist[key] = dist.get(key, 0) + 1
        if wit is None:
            # box < threshold: exact both sides by the vendored engine
            bx, bxw = ba.box_exact_tolerant(mod, ad)
            ce, cew = fg.cert_exact(mod, max_v=v)
            assert fg.replay_witness(mod, cew)
            assert bxw is None or fg.replay_witness(mod, bxw)
            assert bx < k, (v, bx, k)
            hits.append(dict(family=name, features=ft, cert=ce, box=bx,
                             P=[list(p) for p in mod["P"]],
                             Q=[list(q) for q in mod["Q"]],
                             cert_witness=cew, box_witness=bxw))
            log("PIVOT HIT v=%d family=%s tau=%s r_box=%d cert=%d box=%d "
                "< thr=%d" % (v, name, ft["tau"], ft["r_box"], ce, bx, k))
    log("pivot done: tested=%d hits=%d" % (n, len(hits)))
    for key in sorted(dist, key=str):
        log("  dist v=%d r_box=%d tau=%s below-threshold=%s count=%d"
            % (key[0], key[1], list(key[2]), key[3], dist[key]))
    print("PASS_KM_PIVOT_V5 tested=%d hits=%d "
          "families=%s" % (n, len(hits),
                           ",".join("%s:%d" % (k2, tested[k2])
                                    for k2 in tested)))
    receipt = dict(generator="pivot_v5.py seed 20261016",
                   tested=tested, hits=hits,
                   dist=[dict(v=k[0], r_box=k[1], tau=list(k[2]),
                              below=bool(k[3]), count=c)
                         for k, c in sorted(dist.items(), key=str)])
    with open(os.path.join(HERE, "data", "pivot-v5-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":
    main()
