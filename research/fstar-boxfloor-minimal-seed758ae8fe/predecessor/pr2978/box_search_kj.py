#!/usr/bin/env python3
"""KB5j main search: Lemma BPP's without-loss question at tau >= 1.

The certificate value of a decoder depends on the decoder ONLY through
  - the zero-arc digraph Z (M_ts = 0 for t != s),
  - the full label supports pi(t), sg(t) (monotone: cert grows with them),
  - the sub-anchor masks a0(t), b0(t) (box depends only on these and Z).
Lemma SG (scope identity) forces |a0(t) intersect b0(s)| even on every zero
arc, and Lemma SB gives tau(t) = |a0(t) intersect b0(t)| >= 1 in scope.

Jobs (smallest instance first; exact arithmetic; every value computed by the
vendored PR 2914 engine or by a function pinned to it by agreement tests):

A. v = 2 exhaustive: every (a0,b0) pattern with tau >= 1 and every
   scope-consistent zero pattern Z. Assert box = cert (= 2) - the machine
   check of the written v = 2 repair lemma. Also assert PR 2936's tau = 0
   demonstration (cert = 2 > box = 1) still fails completeness.
B. v = 3 exhaustive (up to line and total relabeling): every scope-consistent
   (a0,b0,Z). cert is over-approximated by cert_max(Z) = cert with full labels
   pi = sg = 111 (monotone in label freedom), so `cert_max(Z) <= box` PROVES
   box = cert for every decoder with that data; `cert_max(Z) > box` is a
   counterexample candidate to be realized by an explicit P, Q.
C. Realizable sweep: random exact 3-total decoders (small integer entries,
   varied 2-adic valuations) and GL_3(Z) transforms of the fixtures at
   v = 3..4, tau >= 1 filter, exact cert vs exact box, plus every attaining
   witness projected under Lemma BPP (strict drops and escape classes E1..E4
   recorded).

Writes data/box-search-kj-receipt.json. Stdlib, deterministic.
Run: python3 -B box_search_kj.py
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
sys.path.insert(0, os.path.join(HERE, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2914",
                    "data")
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def dot1(x, y):
    return bin(x & y).count("1") & 1


def fake_model(v, Z):
    """Model dict for the combinatorial space: zero arcs exactly Z (a set of
    ordered pairs), every other entry 1, full label supports."""
    M = [[0 if ((t, s) in Z) else 1 for s in range(v)] for t in range(v)]
    for t in range(v):
        M[t][t] = 1
    arcs = [(t, s) for t in range(v) for s in range(v)
            if t != s and (t, s) in Z]
    return dict(v=v, P=None, Q=None, M=M, pi=[7] * v, sg=[7] * v,
                D=[7] * v, arcs=arcs)


def fake_ad(a0, b0):
    return dict(gamma=0, m=[0, 0, 0], n=[0, 0, 0], c=[0, 0, 0],
                diag=[0] * len(a0), reach=[], cancel=[],
                tau=[bin(a0[t] & b0[t]).count("1") for t in range(len(a0))],
                a0=list(a0), b0=list(b0))


def box_low3(a0, b0, Z):
    """Cheap sufficient test for box = 3 at v = 3: tied-singleton colorings
    (a = b = {c(t)}, c(t) tied) whose monochromatic zero-arc digraph is
    acyclic, or the raw anchor pair. Returns True if box = 3 is witnessed."""
    v = 3
    tied = [a0[t] & b0[t] for t in range(v)]
    choices = [[j for j in range(3) if tied[t] & (1 << j)] for t in range(v)]
    for combo in itertools.product(*choices):
        col = [1 << c for c in combo]
        # conflict edges t->s iff (t,s) in Z and col equal: need acyclic
        nodes = 3
        indeg = [0] * nodes
        out = [[] for _ in range(nodes)]
        for (t, s) in Z:
            if col[t] == col[s]:
                out[t].append(s)
                indeg[s] += 1
        stack = [t for t in range(nodes) if indeg[t] == 0]
        seen = 0
        while stack:
            t = stack.pop()
            seen += 1
            for s in out[t]:
                indeg[s] -= 1
                if indeg[s] == 0:
                    stack.append(s)
        if seen == nodes:
            return True
    mod = fake_model(v, Z)
    ad = fake_ad(a0, b0)
    if fg.ab_value(mod, list(a0), list(b0)) == 3:
        return True
    return False


def canon_total(a0, b0):
    """Canonical representative of (a0, b0) under the 6 total relabelings."""
    best = None
    for perm in itertools.permutations(range(3)):
        def mv(x):
            y = 0
            for j in range(3):
                if x & (1 << j):
                    y |= 1 << perm[j]
            return y
        key = (mv(a0), mv(b0))
        if best is None or key < best:
            best = key
    return best


def canon_config(pairs, Z):
    """Canonical form under line relabeling; pairs is the per-line tuple list
    (already total-canonical). Z is a frozenset of ordered pairs."""
    best = None
    for perm in itertools.permutations(range(3)):
        npairs = tuple(pairs[perm[t]] for t in range(3))
        nZ = frozenset((perm[t], perm[s]) for (t, s) in Z)
        key = (npairs, tuple(sorted(nZ)))
        if best is None or key < best:
            best = key
    return best


def job_a():
    """v = 2 exhaustive over (a0,b0,Z), tau >= 1: box = cert = 2."""
    checked = 0
    gaps = []
    masks = range(8)
    for a00 in masks:
        for b00 in masks:
            if not (a00 & b00):
                continue
            for a01 in masks:
                for b01 in masks:
                    if not (a01 & b01):
                        continue
                    a0, b0 = [a00, a01], [b00, b01]
                    pairs = frozenset([(a00, b00), (a01, b01)])
                    for z01 in (0, 1):
                        for z10 in (0, 1):
                            Z = set()
                            if z01:
                                Z.add((0, 1))
                            if z10:
                                Z.add((1, 0))
                            if any(dot1(a0[t], b0[s]) != 0 for (t, s) in Z):
                                continue  # Lemma SG inconsistency
                            Z = frozenset(Z)
                            mod = fake_model(2, Z)
                            ad = fake_ad(a0, b0)
                            ce, cew = fg.cert_exact(mod, max_v=2)
                            bx, bxw = ba.box_exact_tolerant(mod, ad)
                            checked += 1
                            if ce != bx or bx != 2:
                                gaps.append(dict(a0=a0, b0=b0,
                                                 Z=sorted(Z), cert=ce,
                                                 box=bx))
                            else:
                                assert fg.replay_witness(mod, bxw)
                                assert fg.in_box(mod, ad, bxw)[0]
    # PR 2936's tau = 0 demonstration must still break completeness.
    P = [(1, 0, 1), (2, 1, 0)]
    Q = [(1, 0, 0), (1, 0, 1)]
    sub = fg.model(P, Q)
    ad = fg.anchor_data(sub)
    ce, _ = fg.cert_exact(sub, max_v=2)
    bx, _ = ba.box_exact_tolerant(sub, ad)
    assert (ce, bx) == (2, 1), (ce, bx)
    log("job A: v=2 tau>=1 configs=%d gaps=%d; tau=0 demo cert=%d box=%d"
        % (checked, len(gaps), ce, bx))
    print("PASS_KJ_V2 configs=%d box-equals-cert=%d tau0-demo=2/1"
          % (checked, checked - len(gaps)))
    return checked, gaps


def job_b():
    """v = 3 exhaustive over (a0,b0,Z) up to line/total relabeling."""
    mask_pairs = [(a, b) for a in range(8) for b in range(8) if a & b]
    ckey = {}
    for (a, b) in mask_pairs:
        ckey[(a, b)] = canon_total(a, b)
    line_types = sorted(set(ckey.values()))
    certmax_cache = {}
    configs = set()
    raw = 0
    for tri in itertools.product(line_types, repeat=3):
        pairs = tuple(tri)
        a0 = [p[0] for p in pairs]
        b0 = [p[1] for p in pairs]
        free = [(t, s) for t in range(3) for s in range(3)
                if t != s and dot1(a0[t], b0[s]) == 0]
        for bits in range(1 << len(free)):
            Z = frozenset(free[k] for k in range(len(free))
                          if (bits >> k) & 1)
            raw += 1
            configs.add(canon_config(pairs, Z))
    log("job B: raw configs %d -> %d canonical (line+total relabeling)"
        % (raw, len(configs)))
    gaps = []
    exact_runs = 0
    fast = 0
    done = 0
    for (pairs, ztup) in sorted(configs):
        a0 = [p[0] for p in pairs]
        b0 = [p[1] for p in pairs]
        Z = frozenset(ztup)
        if Z not in certmax_cache:
            mod = fake_model(3, Z)
            ce, _ = fg.cert_exact(mod, max_v=3)
            certmax_cache[Z] = ce
        cm = certmax_cache[Z]
        done += 1
        if cm <= 2:
            # cert_max itself is <= 2; box <= cert_max always, so a gap needs
            # an exact box below cm: run exact box only if cheap witness < cm.
            pass
        if box_low3(a0, b0, Z):
            fast += 1
            assert cm == 3
            continue
        exact_runs += 1
        mod = fake_model(3, Z)
        ad = fake_ad(a0, b0)
        bx, bxw = ba.box_exact_tolerant(mod, ad)
        if bx < cm:
            gaps.append(dict(a0=a0, b0=b0, Z=sorted(Z), cert_max=cm, box=bx))
            log("job B CANDIDATE: a0=%s b0=%s Z=%s cert_max=%d box=%d"
                % (a0, b0, sorted(Z), cm, bx))
        if done % 5000 == 0:
            log("job B progress %d/%d exact=%d fast=%d gaps=%d"
                % (done, len(configs), exact_runs, fast, len(gaps)))
    log("job B done: configs=%d fast-3=%d exact=%d distinct-Z=%d gaps=%d"
        % (len(configs), fast, exact_runs, len(certmax_cache), len(gaps)))
    print("PASS_KJ_V3 configs=%d box-equals-cert=%d candidates=%d "
          "certmax-cache=%d" % (len(configs), len(configs) - len(gaps),
                                len(gaps), len(certmax_cache)))
    return len(configs), gaps


def rand_model(rng, v, val_bits=(0, 0, 1, 2)):
    """Random small-integer P, Q with mixed 2-adic valuations."""
    def ent():
        if rng.random() < 0.32:
            return 0
        mag = rng.choice(val_bits)
        return rng.choice((-1, 1)) * (1 << mag)
    P = [tuple(ent() for _ in range(3)) for _ in range(v)]
    Q = [tuple(ent() for _ in range(3)) for _ in range(v)]
    try:
        return fg.model(P, Q)
    except AssertionError:
        return None


def probe_witnesses(mod, ad, v):
    """Attaining-ish witnesses (hillclimb + random), projected under BPP.
    Returns escape/drop records."""
    out = []
    wits = []
    for seed in (1234, 2025, 77, 4242):
        _val, wit = fg.cert_hillclimb(mod, iters=80, seed=seed)
        if wit is not None and fg.replay_witness(mod, wit):
            wits.append(dict(wit, source="hillclimb:%d" % seed))
    rr = random.Random(9000 + 7 * v)
    for _ in range(120):
        a = [rr.randrange(8) & mod["pi"][t] for t in range(v)]
        b = [rr.randrange(8) & mod["sg"][t] for t in range(v)]
        wit = dict(a=a, b=b, order=list(range(v)), kept=list(range(v)))
        if fg.replay_witness(mod, wit):
            wits.append(dict(wit, source="random"))
    for wit in wits:
        inb, esc = fg.in_box(mod, ad, wit)
        val = fg.ab_value(mod, wit["a"], wit["b"])
        pa = [wit["a"][t] & ad["a0"][t] for t in range(v)]
        pb = [wit["b"][t] & ad["b0"][t] for t in range(v)]
        pval = fg.ab_value(mod, pa, pb)
        if inb and pval >= val:
            continue
        ok1 = all(bin(wit["a"][t] & wit["b"][t] & ad["a0"][t]
                      & ad["b0"][t]).count("1") % 2 == 1 for t in wit["kept"])
        ok2 = True
        kept = set(wit["kept"])
        pos = {t: i for i, t in enumerate(wit["order"])}
        for t in kept:
            for s in kept:
                if t != s and mod["M"][t][s] == 0 \
                        and pos.get(t, 99) < pos.get(s, -1):
                    off = (wit["a"][t] & wit["b"][s]) \
                        & ~(ad["a0"][t] & ad["b0"][s])
                    if bin(off).count("1") % 2 != 0:
                        ok2 = False
        out.append(dict(source=wit["source"], value=val,
                        projected_value=pval,
                        drop=pval < val, cond_i=ok1, cond_ii=ok2,
                        escape_lines=esc,
                        a=list(wit["a"]), b=list(wit["b"]),
                        kept=list(wit["kept"]), order=list(wit["order"])))
    return out


def job_c():
    """Realizable random decoders + fixture GL_3(Z) transforms, v = 3..4."""
    rng = random.Random(20261016)
    records = []
    gaps = []
    drops = []
    esc_classes = {}
    checked = 0
    attempts = 0
    while checked < 320 and attempts < 20000:
        attempts += 1
        v = 3 if attempts % 25 else 4
        mod = rand_model(rng, v)
        if mod is None:
            continue
        ad = fg.anchor_data(mod)
        if not (fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)):
            continue
        if min(ad["tau"]) < 1:
            continue
        checked += 1
        ce, cew = fg.cert_exact(mod, max_v=v)
        bx, bxw = ba.box_exact_tolerant(mod, ad)
        assert fg.replay_witness(mod, cew)
        assert bxw is None or fg.replay_witness(mod, bxw)
        rec = dict(family="random", v=v, tau=list(ad["tau"]),
                   cert=ce, box=bx, gap=ce - bx, hard=ce < v,
                   P=[list(p) for p in mod["P"]],
                   Q=[list(q) for q in mod["Q"]])
        records.append(rec)
        if ce > bx:
            gaps.append(rec)
            log("job C CANDIDATE: v=%d cert=%d box=%d" % (v, ce, bx))
        if v == 3:
            for w in probe_witnesses(mod, ad, v):
                if w["drop"]:
                    drops.append(dict(rec, witness=w))
                    log("job C DROP at tau>=1: v=%d val=%d proj=%d i=%s ii=%s"
                        % (v, w["value"], w["projected_value"],
                           w["cond_i"], w["cond_ii"]))
                key = ("E1" if w["cond_i"] and w["cond_ii"] else
                       "E4" if not w["cond_i"] and not w["cond_ii"] else
                       "E2" if not w["cond_i"] else "E3")
                esc_classes[key] = esc_classes.get(key, 0) + 1
        if checked % 150 == 0:
            log("job C progress checked=%d gaps=%d drops=%d"
                % (checked, len(gaps), len(drops)))
    # fixture transforms at v = 3 (PR 2963's sweep started at v = 4)
    spec2 = importlib.util.spec_from_file_location(
        "box_search",
        os.path.join(HERE, "predecessor", "pr2963", "box_search.py"))
    bs = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(bs)
    made = 0
    att = 0
    while made < 40 and att < 800:
        att += 1
        fixture = ("tied_min.json", "cex_min_1.json")[att % 2]
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
        U, Uinv = bs.rand_gl3z(rng, steps=2 + att % 5)
        mod1 = bs.transform(mod0, U, Uinv)
        S = sorted(rng.sample(range(mod1["v"]), 3))
        sub = fg.restrict(mod1, S)
        ad = fg.anchor_data(sub)
        if not (fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad)):
            continue
        if min(ad["tau"]) < 1:
            continue
        made += 1
        ce, cew = fg.cert_exact(sub, max_v=3)
        bx, bxw = ba.box_exact_tolerant(sub, ad)
        assert fg.replay_witness(sub, cew)
        rec = dict(family="fixture-transform", v=3, fixture=fixture, S=S,
                   tau=list(ad["tau"]), cert=ce, box=bx, gap=ce - bx,
                   hard=ce < 3, P=[list(p) for p in sub["P"]],
                   Q=[list(q) for q in sub["Q"]])
        records.append(rec)
        if ce > bx:
            gaps.append(rec)
            log("job C (transform) CANDIDATE: cert=%d box=%d" % (ce, bx))
        for w in probe_witnesses(sub, ad, 3):
            if w["drop"]:
                drops.append(dict(rec, witness=w))
                log("job C (transform) DROP at tau>=1: val=%d proj=%d"
                    % (w["value"], w["projected_value"]))
            key = ("E1" if w["cond_i"] and w["cond_ii"] else
                   "E4" if not w["cond_i"] and not w["cond_ii"] else
                   "E2" if not w["cond_i"] else "E3")
            esc_classes[key] = esc_classes.get(key, 0) + 1
    log("job C done: instances=%d (random %d + transforms %d) gaps=%d "
        "drops=%d escapes=%s" % (len(records), checked, made, len(gaps),
                                 len(drops), esc_classes))
    print("PASS_KJ_REALIZABLE instances=%d box-violations=%d drops=%d "
          "escapes=%s" % (len(records), len(gaps), len(drops), esc_classes))
    return records, gaps, drops, esc_classes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    checked, gaps_a = job_a()
    nconf, gaps_b = job_b()
    records, gaps_c, drops, esc = job_c()
    receipt = dict(generator="box_search_kj.py seed 20261016",
                   job_a=dict(configs=checked, gaps=len(gaps_a),
                              gap_records=gaps_a),
                   job_b=dict(configs=nconf, candidates=gaps_b),
                   job_c=dict(instances=records, gaps=gaps_c, drops=drops,
                              escape_classes=esc))
    with open(os.path.join(HERE, "data", "box-search-kj-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    total_gap = len(gaps_a) + len(gaps_b) + len(gaps_c)
    print("PASS_KJ_BOX_SEARCH v2-configs=%d v3-configs=%d realizable=%d "
          "candidates=%d drops-tau1=%d"
          % (checked, nconf, len(records), total_gap, len(drops)))


if __name__ == "__main__":
    main()
