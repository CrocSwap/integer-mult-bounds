#!/usr/bin/env python3
"""KB5i bounded box-completeness attack (job 2), on the weak cells of PR
2936's record:

(a) BPP STRICTNESS DEMONSTRATION: Lemma BPP (PR 2936) says a witness
    projects to a sub-anchor box witness of the same value iff (i) each kept
    line has odd tied-bit overlap and (ii) every forward zero arc has even
    off-anchor shared parity. We exhibit an explicit exact 3-total decoder
    and a replayed witness whose projection STRICTLY drops the value: the
    obstruction is real, not formal.
(b) FIXTURE-DENSITY TAU >= 1 SWEEP: PR 2936's synthetic sweep (126 random
    decoders) never produced a hard (cert < v) tau >= 1 instance -
    fixture-density zeros are needed. This generator makes them: GL_3(Z)
    column transforms (P -> P U, Q -> Q U^{-T}, M fixed, anchor structure
    changed) of the canonical fixtures, restricted to v = 4..6, filtered to
    tau >= 1 everywhere, exact cert vs exact box (the vendored tolerant
    wrapper of PR 2936). Smallest instance first; deterministic seeds.

Writes data/box-search-receipt.json. Stdlib, deterministic.
Run: python3 -B box_search.py
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
sys.path.insert(0, HERE)
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
spec = importlib.util.spec_from_file_location(
    "box_attack", os.path.join(HERE, "predecessor", "pr2936", "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def mat_det3(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


def mat_inv3(M):
    """Exact integer inverse of a unimodular 3x3 (det in {1, -1})."""
    d = mat_det3(M)
    assert d in (1, -1), "not unimodular: det=%d" % d
    adj = [
        [M[1][1] * M[2][2] - M[1][2] * M[2][1],
         M[0][2] * M[2][1] - M[0][1] * M[2][2],
         M[0][1] * M[1][2] - M[0][2] * M[1][1]],
        [M[1][2] * M[2][0] - M[1][0] * M[2][2],
         M[0][0] * M[2][2] - M[0][2] * M[2][0],
         M[0][2] * M[1][0] - M[0][0] * M[1][2]],
        [M[1][0] * M[2][1] - M[1][1] * M[2][0],
         M[0][1] * M[2][0] - M[0][0] * M[2][1],
         M[0][0] * M[1][1] - M[0][1] * M[1][0]],
    ]
    return [[adj[i][j] * d for j in range(3)] for i in range(3)]


def mat_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def rand_gl3z(rng, steps=4):
    """Unimodular U as a short product of elementary ops; Uinv exact."""
    U = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for _ in range(steps):
        i, j = rng.randrange(3), rng.randrange(3)
        while j == i:
            j = rng.randrange(3)
        k = rng.choice([-1, 1, -1])
        E = [[1 if a == b else 0 for b in range(3)] for a in range(3)]
        E[i][j] += k
        U = mat_mul(E, U)
    return U, mat_inv3(U)


def transform(mod, U, Uinv):
    """P -> P U, Q -> Q U^{-T}: M is unchanged, the anchor data changes."""
    P = [tuple(sum(p[k] * U[k][j] for k in range(3)) for j in range(3))
         for p in mod["P"]]
    Q = [tuple(sum(q[k] * Uinv[j][k] for k in range(3)) for j in range(3))
         for q in mod["Q"]]
    return fg.model(P, Q)


def bpp_projection(mod, ad, wit):
    """Sub-anchor projection (Lemma BPP): a' = a & a0, b' = b & b0."""
    a = [x & ad["a0"][t] for t, x in enumerate(wit["a"])]
    b = [x & ad["b0"][t] for t, x in enumerate(wit["b"])]
    return dict(a=a, b=b, order=list(wit["order"]), kept=list(wit["kept"]))


def bpp_conditions(mod, ad, wit):
    """Lemma BPP's two sufficient conditions on a witness (README of PR
    2936): (i) odd tied overlap per kept line, (ii) even off-anchor shared
    parity on every forward zero arc among kept lines."""
    ok1 = True
    for t in wit["kept"]:
        tied = wit["a"][t] & wit["b"][t] & ad["a0"][t] & ad["b0"][t]
        if bin(tied).count("1") % 2 != 1:
            ok1 = False
    ok2 = True
    kept = set(wit["kept"])
    pos = {t: i for i, t in enumerate(wit["order"])}
    for t in kept:
        for s in kept:
            if t != s and mod["M"][t][s] == 0 and pos.get(t, 10 ** 9) < pos.get(s, -1):
                off = (wit["a"][t] & wit["b"][s]) \
                    & ~(ad["a0"][t] & ad["b0"][s])
                if bin(off).count("1") % 2 != 0:
                    ok2 = False
    return ok1, ok2


def bpp_strictness():
    """Projection strictness of Lemma BPP. Smallest instance first: the
    v = 2 tau = 0 decoder of PR 2936 (PROVEN strictness: cert = 2 > box = 1
    forces every cert-attaining witness to lose value under projection).
    Then a bounded tau >= 1 search for a strict drop among replayed valid
    witnesses of the fixture sub-decoders (v = 3..5)."""
    # (a) smallest instance, PROVEN
    P = [(1, 0, 1), (2, 1, 0)]
    Q = [(1, 0, 0), (1, 0, 1)]
    sub = fg.model(P, Q)
    ad = fg.anchor_data(sub)
    ce, cew = fg.cert_exact(sub, max_v=2)
    assert fg.replay_witness(sub, cew)
    val = fg.ab_value(sub, cew["a"], cew["b"])
    proj = bpp_projection(sub, ad, cew)
    pval = fg.ab_value(sub, proj["a"], proj["b"])
    ok1, ok2 = bpp_conditions(sub, ad, cew)
    assert pval < val, "tau=0 v=2 projection must strictly drop"
    log("BPP strictness (v=2 tau=0, PROVEN): witness %d -> projection %d "
        "(conditions i=%s ii=%s)" % (val, pval, ok1, ok2))
    proven = dict(v=2, tau=list(ad["tau"]), witness_value=val,
                  projected_value=pval, condition_i=ok1, condition_ii=ok2,
                  status="PROVEN strictness at tau = 0 (forced: cert=2 > "
                         "box=1)")
    # (b) bounded tau >= 1 search
    cands = []
    for fixture in ("tied_min.json", "cex_min_1.json"):
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
        for size in (3, 4, 5):
            subs, _n, _t = fg.subsets_smallest_first(mod0["v"], size, 40, 1)
            for S in subs:
                cands.append((fixture, list(S), size))
    cands.sort(key=lambda c: (c[2], sum(c[1])))
    seen_esc = 0
    for fixture, S, size in cands:
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
        sub = fg.restrict(mod0, S)
        ad = fg.anchor_data(sub)
        v = sub["v"]
        wits = []
        for seed in (1234, 2025, 77, 4242):
            _val, wit = fg.cert_hillclimb(sub, iters=200, seed=seed)
            if wit is not None and fg.replay_witness(sub, wit):
                wits.append(wit)
        rr = random.Random(4242 + 100 * size + sum(S))
        for _ in range(600):
            a = [rr.randrange(8) & sub["pi"][t] for t in range(v)]
            b = [rr.randrange(8) & sub["sg"][t] for t in range(v)]
            wit = dict(a=a, b=b, order=list(range(v)), kept=list(range(v)))
            if fg.replay_witness(sub, wit):
                wits.append(wit)
        for wit in wits:
            if fg.in_box(sub, ad, wit)[0]:
                continue
            seen_esc += 1
            val = fg.ab_value(sub, wit["a"], wit["b"])
            if val < 2:
                continue
            proj = bpp_projection(sub, ad, wit)
            pval = fg.ab_value(sub, proj["a"], proj["b"])
            if pval < val:
                ok1, ok2 = bpp_conditions(sub, ad, wit)
                return proven, dict(fixture=fixture, S=S, v=v,
                                    tau=list(ad["tau"]), tau_min=min(ad["tau"]),
                                    witness_value=val,
                                    projected_value=pval,
                                    condition_i=ok1, condition_ii=ok2,
                                    status="CHECKED strictness at tau >= 1")
    log("BPP strictness (tau >= 1 bounded): %d escaping witnesses examined, "
        "no strict projection drop" % seen_esc)
    return proven, dict(escape_witnesses_examined=seen_esc, found=False,
                        status="CHECKED bounded: no drop at tau >= 1 "
                               "(v = 3..5 fixture sub-decoders)")


def sweep():
    """Fixture-density tau >= 1 family: GL_3(Z) transforms + restrictions,
    exact cert vs exact box, smallest v first."""
    rng = random.Random(20261016)
    out = []
    for v_target, tries in ((4, 24), (5, 20), (6, 16)):
        made = 0
        attempts = 0
        while made < tries and attempts < 40 * tries:
            attempts += 1
            fixture = ("tied_min.json", "cex_min_1.json")[attempts % 2]
            mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
            U, Uinv = rand_gl3z(rng, steps=2 + attempts % 5)
            mod1 = transform(mod0, U, Uinv)
            S = sorted(rng.sample(range(mod1["v"]), v_target))
            sub = fg.restrict(mod1, S)
            ad = fg.anchor_data(sub)
            if not (fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad)):
                continue
            if min(ad["tau"]) < 1:
                continue
            made += 1
            ce, cew = fg.cert_exact(sub, max_v=v_target)
            bx, bxw = ba.box_exact_tolerant(sub, ad)
            assert fg.replay_witness(sub, cew)
            assert bxw is None or fg.replay_witness(sub, bxw)
            inb, esc = fg.in_box(sub, ad, cew)
            rec = dict(fixture=fixture, S=S, v=v_target,
                       tau=list(ad["tau"]), cert=ce, box=bx,
                       cert_witness_in_box=inb,
                       hard=(ce < v_target), gap_box=ce - bx,
                       P=[list(p) for p in sub["P"]],
                       Q=[list(q) for q in sub["Q"]])
            out.append(rec)
            log("v=%d %s S=%s tau=%s cert=%d box=%d in_box=%s hard=%s"
                % (v_target, fixture, S, ad["tau"], ce, bx, inb, ce < v_target))
            if ce > bx:
                log("BOX-COMPLETENESS COUNTEREXAMPLE: cert=%d > box=%d at "
                    "v=%d" % (ce, bx, v_target))
                return out, rec
        log("sweep v=%d: %d instances, %d attempts" % (v_target, made,
                                                       attempts))
    return out, None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bpp_proven, bpp_tau1 = bpp_strictness()
    records, cex = sweep()
    hard = [r for r in records if r["hard"]]
    tau1 = len(records)
    with open(os.path.join(HERE, "data", "box-search-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(dict(bpp_proven=bpp_proven, bpp_tau_ge1=bpp_tau1,
                       sweep=records, counterexample=cex,
                       generator="box_search.py seed 20261016"),
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    viol = sum(1 for r in records if r["gap_box"] > 0)
    print("PASS_BOX_SEARCH bpp-strict-tau0=yes bpp-strict-tau1=%s tau-ge1=%d "
          "hard=%d box-violations=%d"
          % ("yes" if bpp_tau1.get("found") else "no", tau1, len(hard), viol))
    if cex is not None:
        print("PASS_BOX_SEARCH counterexample v=%d" % cex["v"])


if __name__ == "__main__":
    main()
