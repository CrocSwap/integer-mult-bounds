#!/usr/bin/env python3
"""KB5i bounded run (job 1 + job 2 inputs): EXACT named on the twelve open
tied_min v = 11 sub-decoders, with replayed construction witnesses, plus a
deterministic multi-seed witness regeneration for cert/box cross-checked
against PR 2936's stored values (predecessor/pr2936/receipt-*.json).

Recorded evidence only: every value carries its status
  exact  - both sides settled (named is exact by construction here; cert/box
           exact when a replayed witness hits the ceiling v or an exact rung)
  lower  - witnessed lower bound only.

Writes data/named-v11-receipt.json. Stdlib, deterministic.
Run: python3 -B run_named_v11.py
"""
import importlib.util
import json
import os
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
PR2936 = os.path.join(HERE, "predecessor", "pr2936",
                      "receipt-tied_min-s11-deep.json")

# deterministic regeneration seeds: the deep run's own seeds first
# (census_v7_11.py used iters=400, box seed 910, cert seed 911), then extra
# deterministic restarts to look for ceiling witnesses
CERT_SEEDS = [(911, 400), (2025, 400), (1234, 400), (2026, 2000),
              (42, 2000), (7, 2000), (13, 2000), (99, 2000), (31, 2000)]
BOX_SEEDS = [(910, 400), (2024, 400), (2026, 2000), (42, 2000),
             (7, 2000), (13, 2000), (99, 2000), (31, 2000)]


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def load_sub(label):
    fx = label.split("|")[0] + ".json"
    mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fx)))
    S = [int(x) for x in label.split("|")[1].split(",")]
    return fg.restrict(mod0, S)


def tables(sub):
    inm, _ = fg.digraph_tables(sub["v"], sub["arcs"])
    acyc = fg.acyclic_table(sub["v"], inm)
    mas = fg.mas_table(sub["v"], acyc)
    return mas, acyc


def best_witness(sub, ad, seeds, box):
    """Deterministic multi-seed hill-climb; returns (value, witness, runs)."""
    best, best_wit = -1, None
    runs = []
    for seed, iters in seeds:
        if box:
            val, wit = fg.cert_hillclimb(sub, iters=iters, seed=seed,
                                         box=True, ad=ad)
        else:
            val, wit = fg.cert_hillclimb(sub, iters=iters, seed=seed)
        ok = wit is not None and fg.replay_witness(sub, wit)
        runs.append(dict(seed=seed, iters=iters, value=val, replayed=ok))
        assert ok, "hill-climb witness must replay"
        if val > best:
            best, best_wit = val, wit
    return best, best_wit, runs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(PR2936, encoding="utf-8") as fh:
        stored = {r["label"]: r for r in json.load(fh)["records"]}
    out = {}
    for label in sorted(stored):
        sub = load_sub(label)
        ad = fg.anchor_data(sub)
        mas, acyc = tables(sub)
        v = sub["v"]
        named, det = ne.named_exact(sub, ad, mas, acyc, cap=6000000)
        wit = det["mx_detail"]["witness"]
        replayed = ne.replay_mx_witness(sub, ad, mas, wit)
        assert replayed == det["mx"], "mx witness replay"
        mp, _m, mp_exh, mp_prod = fg.matched_pivot(sub, mas)
        assert mp_exh and mp == det["MP"] == stored[label]["MP"]
        r = stored[label]
        ce, ce_wit, ce_runs = best_witness(sub, ad, CERT_SEEDS, box=False)
        bx, bx_wit, bx_runs = best_witness(sub, ad, BOX_SEEDS, box=True)
        ce_inb, ce_esc = fg.in_box(sub, ad, ce_wit)
        bx_inb, _ = fg.in_box(sub, ad, bx_wit)
        assert bx <= ce, "box witness exceeds cert witness"
        cert_exact = ce >= v or bx >= v  # ceiling; box <= cert always
        cert_val = v if cert_exact else None
        box_exact = bx >= v
        rec = dict(
            label=label, v=v, threshold=(2 * v) // 3,
            named=named, named_exact=True, named_detail=dict(
                MP=det["MP"], reach=det["reach"], mx=det["mx"],
                cl3=det["cl3"], cl3_how=det["cl3_how"],
                mx_coarse_product=det["mx_detail"]["coarse_product"]),
            mx_witness=wit, mx_witness_replayed=True,
            stored_cert=r["cert"], stored_box=r["box"],
            stored_named=r["named"],
            stored_cert_exact=r["cert_exact"], stored_box_exact=r["box_exact"],
            cert_witness=ce_wit, cert_witness_value=ce,
            cert_witness_replayed=True,
            cert_witness_in_box=ce_inb, cert_witness_escapes_box=ce_esc,
            cert_exact=cert_exact, cert=(cert_val if cert_exact else ce),
            cert_status=("exact" if cert_exact else "lower"),
            box_witness=bx_wit, box_witness_value=bx,
            box_witness_replayed=True, box_witness_in_box=bx_inb,
            box_exact=box_exact,
            box=(v if box_exact else bx), box_status=("exact" if box_exact
                                                      else "lower"),
            cert_runs=ce_runs, box_runs=bx_runs,
            mx_product=r["mx_product"],
            gap_named=(None if not cert_exact else cert_val - named),
            gap_named_lo=(ce - named),
        )
        out[label] = rec
        log("%s: named=%d(exact) cert=%s(%s) box=%s(%s) gap=%s" % (
            label, named, rec["cert"], rec["cert_status"], rec["box"],
            rec["box_status"], rec["gap_named"]))
    with open(os.path.join(HERE, "data", "named-v11-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(dict(records=out, generator="run_named_v11.py",
                       cert_seeds=CERT_SEEDS, box_seeds=BOX_SEEDS),
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    n2 = [l for l, r in out.items() if r["gap_named"] == 2]
    log("gap_named = 2 PROVEN on %d records" % len(n2))
    print("PASS_NAMED_V11 records=%d named-exact=12 gap2-proven=%d"
          % (len(out), len(n2)))


if __name__ == "__main__":
    main()
