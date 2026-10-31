#!/usr/bin/env python3
"""KB5h box-completeness attack (priority 2), part 1: exact small instances.

(a) tau = 0 DEMONSTRATION (smallest instance first): an explicit exact
    3-total rational decoder on v = 2 lines with a tau = 0 line, where
    cert = 2 > box = 1.  This PROVES the hypothesis "every line has
    tau(t) >= 1" is needed for box-completeness (Lemma SB (iii) predicts the
    mechanism; this realizes it end to end).
(b) SYNTHETIC SWEEP at tau >= 1: deterministic random exact 3-total decoders
    at v = 4..6 (smallest first), exact cert vs exact box, looking for the
    minimal instance with cert > box (a box-completeness counterexample).

Exact rungs are the vendored PR 2914 engine (cert_exact / box_exact:
exhaustive a-enumeration with exact completion). Stdlib, deterministic.
Writes data/box-attack-receipt.json. Run: python3 -B box_attack.py
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
ENG = os.path.join(HERE, "predecessor", "pr2914", "verify.py")
spec = importlib.util.spec_from_file_location("pr2914_engine", ENG)
fg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fg)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def box_exact_tolerant(mod, ad):
    """box_exact with one edge-case fix: when a line has NO certifying
    sub-anchor pair (tau = 0, Lemma SB (iii)), the vendored filter empties
    that line's option list and itertools.product yields nothing at all
    (returns (-1, None)). Here such a line is pinned to a = 0 (it can never
    be kept inside the box) and the enumeration proceeds. Identical to
    fg.box_exact on tau >= 1 instances (checked in verify.py)."""
    v = mod["v"]
    choices = []
    for t in range(v):
        subs = [m for m in range(8) if (m & ~ad["a0"][t]) == 0]
        subs = [m for m in subs
                if any(fg.dot1(m, b) == 1 and (b & ~ad["b0"][t]) == 0
                       for b in range(8))]
        choices.append(subs if subs else [0])
    best, best_wit = -1, None
    for combo in itertools.product(*choices):
        val, wit = fg.completion_box(mod, ad, list(combo))
        if val > best:
            best, best_wit = val, wit
    return best, best_wit


def tau0_demo():
    """Explicit v = 2 decoder: P = [[1,0,1],[2,1,0]], Q = [[1,0,0],[1,0,1]].
    M = [[1,2],[2,2]], gamma = 0, tau = (1, 0): line 1 has tau = 0."""
    P = [(1, 0, 1), (2, 1, 0)]
    Q = [(1, 0, 0), (1, 0, 1)]
    mod = fg.model(P, Q)
    ad = fg.anchor_data(mod)
    assert fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad), \
        "the demo decoder must satisfy the CT/scope identities"
    assert ad["tau"] == [1, 0], "tau must be (1, 0), got %s" % ad["tau"]
    ce, cew = fg.cert_exact(mod, max_v=2)
    bx, bxw = box_exact_tolerant(mod, ad)
    assert fg.replay_witness(mod, cew) and fg.in_box(mod, ad, cew)[0] is False
    assert fg.replay_witness(mod, bxw) and fg.in_box(mod, ad, bxw)[0] is True
    assert ce == 2 and bx == 1, "expected cert=2 box=1, got %s %s" % (ce, bx)
    log("tau0 demo: cert=2 box=1 (cert witness escapes the box on the "
        "tau=0 line) - unrestricted box-completeness FAILS at v=2")
    return dict(v=2, tau=list(ad["tau"]), cert=ce, box=bx,
                cert_witness_escapes_box=True,
                status="PROVEN: tau >= 1 hypothesis needed")


def random_decoder(rng, v, sparse=True):
    # biased entry pool: mostly odd (v2 = 0 -> ties at gamma = 0) with a
    # minority of singly-even entries to create high/cancellation structure
    pool = [0, 0, 1, -1, 1, -1, 3, -3, 2, -2, 6, -6]
    while True:
        P = [tuple(rng.choice(pool) for _ in range(3)) for _ in range(v)]
        Q = [tuple(rng.choice(pool) for _ in range(3)) for _ in range(v)]
        try:
            mod = fg.model(P, Q)
        except (AssertionError, ValueError):
            continue
        ad = fg.anchor_data(mod)
        if not (fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)):
            continue
        return mod, ad


def sweep():
    rng = random.Random(20261016)
    out = []
    for v, tries in ((4, 60), (5, 40), (6, 20), (7, 6)):
        tested = tau1 = 0
        for k in range(tries):
            mod, ad = random_decoder(rng, v)
            tested += 1
            ce, cew = fg.cert_exact(mod, max_v=v)
            bx, bxw = box_exact_tolerant(mod, ad)
            assert fg.replay_witness(mod, cew)
            assert (bxw is None and bx == 0) or (
                bxw is not None and fg.replay_witness(mod, bxw))
            inb, esc = fg.in_box(mod, ad, cew)
            has0 = min(ad["tau"]) < 1
            rec = dict(v=v, k=k, tau=list(ad["tau"]), tau_min=min(ad["tau"]),
                       cert=ce, box=bx, cert_witness_in_box=inb,
                       gap_box=ce - bx, tau0_line=has0)
            out.append(rec)
            if not has0:
                tau1 += 1
                log("  v=%d k=%2d tau=%s cert=%d box=%d in_box=%s"
                    % (v, k, ad["tau"], ce, bx, inb))
                if ce > bx:
                    log("BOX-COMPLETENESS COUNTEREXAMPLE at v=%d (tau>=1): "
                        "cert=%d > box=%d" % (v, ce, bx))
                    return out, rec
            else:
                log("  v=%d k=%2d tau=%s cert=%d box=%d [tau0-line, "
                    "out-of-claim]" % (v, k, ad["tau"], ce, bx))
        log("sweep v=%d: %d tested, %d with tau>=1, no counterexample"
            % (v, tested, tau1))
    return out, None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    demo = tau0_demo()
    records, cex = sweep()
    rec = dict(demo=demo, sweep=records, counterexample=cex)
    with open(os.path.join(HERE, "data", "box-attack-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    if cex is not None:
        print("PASS_BOX_ATTACK counterexample-found v=%d" % cex["v"])
    else:
        print("PASS_BOX_ATTACK tau0-demo-cert2-box1 "
              "sweep=%d-no-counterexample" % len(records))


if __name__ == "__main__":
    main()
