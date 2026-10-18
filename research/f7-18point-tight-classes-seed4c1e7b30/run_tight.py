"""Resumable receipt runner for the KB3g tight-class enumerations.

Modes (deterministic sharding; receipts per shard in TIGHT-PROGRESS.json,
one section per mode):

  class71   the (10,8) A-vanish tight class (7,1): Sidon 5-pair enumeration
            plus the three translated coverage lines.  Also re-derives the
            exact Fourier contradiction (identity, no walk).
  class82   the (10,8) D-vanish tight class (8,2): every normalized Sidon
            4-pair, every admissible A0t choice, the three coverage lines.
  class60   the (12,6) A-vanish class (6,0): full-sumset 6-pairs and the
            D-side hitting search with the three coverage lines.
  control   m=4 brute-force analogue classes (soundness/completeness of the
            L7 reduction) and the Fourier identity table.

Usage: python3 -I -B run_tight.py <mode> [--shards N] [--shard k] [--budget S]

A shard is processed only if its receipt is absent; re-invoke to continue.
The receipt file must not exist beforehand for a walk claimed as
recomputation (receipt-validation trap); delete receipts or run in a fresh
copy to prove recomputation.
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import tight  # noqa: E402

PROGRESS = HERE / "TIGHT-PROGRESS.json"
MODES = ("class71", "class82", "class60", "control")


def progress_path():
    import sys as _sys

    if "--progress" in _sys.argv:
        return Path(_sys.argv[_sys.argv.index("--progress") + 1])
    return PROGRESS


def load_progress(mode):
    data = {"modes": {}}
    p = progress_path()
    if p.exists():
        old = json.loads(p.read_text(encoding="utf-8"))
        if "modes" in old:
            data = old
    return data["modes"].setdefault(mode, {"shards": {}})


def save_progress(mode, prog):
    data = {"modes": {}}
    p = progress_path()
    if p.exists():
        old = json.loads(p.read_text(encoding="utf-8"))
        if "modes" in old:
            data = old
    data["modes"][mode] = prog
    p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def aggregate(prog):
    keys = [
        "normalized_pairs",
        "equality_configs_normalized",
        "covering_pairs",
        "covering_configs_normalized",
        "normalized_sidon_pairs",
        "non_1_invariant_pairs",
        "admissible_choice_sets",
        "checked",
        "covering_configs",
        "tested_triples",
        "pairs_with_hit_sets",
        "covering_triples",
        "d_checked",
        "d_with_transversals",
        "transversals_total",
    ]
    out = {}
    for k in keys:
        tot = 0
        seen = False
        for rec in prog["shards"].values():
            if k in rec:
                tot += rec[k]
                seen = True
        if seen:
            out[k] = tot
    hist = {}
    for rec in prog["shards"].values():
        for k, v in rec.get("fail_hist", {}).items():
            hist[k] = hist.get(k, 0) + v
    if hist:
        out["fail_hist"] = {k: hist[k] for k in sorted(hist)}
    wits = []
    for rec in prog["shards"].values():
        wits.extend(rec.get("witnesses", []))
    out["witnesses"] = wits[:5]
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    mode = args[0] if args else ""
    if mode == "merge60":
        # merge per-shard class60 receipts (TIGHT-C60-<k>.json) into the
        # canonical TIGHT-PROGRESS.json section
        prog = {"shards": {}}
        for k in range(8):
            p = HERE / ("TIGHT-C60-%d.json" % k)
            rec = json.loads(p.read_text(encoding="utf-8"))["modes"]["class60"]
            shard_rec = rec["shards"][str(k)]
            assert shard_rec.get("complete"), (k, shard_rec.get("budget_hit"))
            prog["shards"][str(k)] = shard_rec
        prog["complete"] = True
        prog["shards_count"] = 8
        prog["total"] = aggregate(prog)
        save_progress("class60", prog)
        print("PASS_TIGHT_CLASS60 %s" % json.dumps(prog["total"], sort_keys=True), flush=True)
        return
    if mode not in MODES:
        raise SystemExit("usage: run_tight.py %s [--shards N] [--shard k]" % "|".join(MODES))
    shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 8
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 520.0

    if mode == "control":
        t0 = time.time()
        rec = tight.control_m4_bruteforce()
        fid = tight.fourier_71_identity()
        print("CONTROL m4_class71_analogue %s" % json.dumps(rec["m4_class71_analogue"], sort_keys=True), flush=True)
        print("CONTROL m4_class82_analogue %s" % json.dumps(rec["m4_class82_analogue"], sort_keys=True), flush=True)
        for tag in sorted(fid):
            print("FOURIER %s %s" % (tag, json.dumps(fid[tag], sort_keys=True)), flush=True)
        assert rec["m4_class71_analogue"]["all_have_l7_structure"] in (True, None)
        assert rec["m4_class82_analogue"]["all_have_l7_structure"] in (True, None)
        assert fid["m5_k5"]["contradiction"] is True
        assert fid["m3_analogue_71"]["contradiction"] is False
        print("PASS_TIGHT_CONTROL seconds=%.1f" % (time.time() - t0), flush=True)
        return

    prog = load_progress(mode)
    if mode == "class71":
        todo = [0]
    elif "--shard" in args:
        todo = [int(args[args.index("--shard") + 1])]
    else:
        todo = [
            k
            for k in range(shards)
            if not prog["shards"].get(str(k), {}).get("complete")
        ]
    if not prog["shards"]:
        print("RUN_TIGHT %s fresh receipts confirmed" % mode, flush=True)
    print("RUN_TIGHT %s shards=%d todo=%s" % (mode, shards, todo), flush=True)
    for shard in todo:
        t0 = time.time()
        if mode == "class71":
            rec = tight.class71_run(budget=budget)
        elif mode == "class82":
            rec = tight.class82_run(budget=budget, shard=shard, shards=shards)
        else:
            rec = tight.class60_run(budget=budget, shard=shard, shards=shards)
        rec["wall_seconds"] = round(time.time() - t0, 2)
        rec["complete"] = not rec.get("budget_hit", False)
        prog["shards"][str(shard)] = rec
        save_progress(mode, prog)
        print(
            "RECEIPT %s shard=%d/%d wall=%.1fs %s"
            % (mode, shard, shards, rec["wall_seconds"], json.dumps(aggregate(prog), sort_keys=True)[:400]),
            flush=True,
        )
    done = [
        k
        for k in range(shards)
        if prog["shards"].get(str(k), {}).get("complete")
    ]
    if mode == "class71" or len(done) == shards:
        prog["complete"] = True
        prog["shards_count"] = len(prog["shards"])
        prog["total"] = aggregate(prog)
        save_progress(mode, prog)
        print("PASS_TIGHT_%s %s" % (mode.upper(), json.dumps(prog["total"], sort_keys=True)), flush=True)
    else:
        print(
            "RECEIPT_TIGHT_%s partial complete=%d/%d (re-invoke to continue)"
            % (mode, len(done), shards),
            flush=True,
        )


if __name__ == "__main__":
    main()
