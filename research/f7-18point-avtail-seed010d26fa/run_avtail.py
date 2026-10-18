"""Resumable walk driver for the KB3h package (f7-18point-avtail).

Modes (deterministic sharding; per-shard receipt files AVTAIL-<TAG>-<k>.json,
one progress section per mode in AVTAIL-PROGRESS.json after `merge`):

  class71   ANCHOR re-walk (empty receipts): PR 2961's class (7,1)
            enumeration (expected normalized_pairs=0).
  class82   ANCHOR re-walk (empty receipts): PR 2961's class (8,2)
            equality-configuration walk (expected checked=28,815,360
            covering=0 across 8 shards).
  class60   ANCHOR re-walk (empty receipts): PR 2961's class (6,0)
            D-side transversal walk (expected d_checked=169,911
            d_with_transversals=0 across 8 shards).
  av51      the new class (12,6) A-vanish (5,1) decision walk
            (avtail.class51_run).

Usage: python3 -I -B run_avtail.py <mode> [--shards N] [--shard k]
                                    [--budget S]
       python3 -I -B run_avtail.py merge <mode>

Shard receipt files are written ONLY by their own shard process (safe for
parallel shard runs); `merge` rebuilds AVTAIL-PROGRESS.json from the shard
files (idempotent, run after all shards finish).  A shard is processed only
if its receipt file is absent or incomplete; re-invoke to continue.
Receipts carry explicit complete/budget_hit flags (a partial walk is never
recorded as complete).  Starting a mode with no receipt prints
'fresh receipts confirmed' (the receipt-validation trap: replaying against
a committed receipt validates nothing).
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import tight  # noqa: E402
import avtail  # noqa: E402

PROGRESS = HERE / "AVTAIL-PROGRESS.json"
MODES = ("class71", "class82", "class60", "av51")
TAGS = {"class71": "C71", "class82": "C82", "class60": "C60", "av51": "AV51"}


def shard_file(mode, k):
    return HERE / ("AVTAIL-%s-%d.json" % (TAGS[mode], k))


def load_shard(mode, k):
    p = shard_file(mode, k)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def aggregate(shards):
    keys = set()
    for rec in shards:
        keys |= set(rec)
    tot = {}
    for k in sorted(keys):
        vals = [
            rec[k]
            for rec in shards
            if isinstance(rec.get(k), (int, float))
            and k not in ("shard", "shards", "seconds", "wall_seconds")
        ]
        if vals:
            if k.endswith("_total") and len(set(vals)) == 1:
                tot[k] = vals[0]
            else:
                tot[k] = sum(vals)
        dicts = [rec[k] for rec in shards if isinstance(rec.get(k), dict)]
        if dicts:
            merged = {}
            for d in dicts:
                for kk, vv in d.items():
                    merged[kk] = merged.get(kk, 0) + vv
            tot[k] = merged
    return tot


def run_shard(mode, k, shards, budget):
    rec = load_shard(mode, k)
    if rec and rec.get("complete"):
        print("SKIP %s shard=%d already complete" % (mode, k), flush=True)
        return rec
    t0 = time.time()
    if mode == "class71":
        rec = tight.class71_run(budget=budget)
    elif mode == "class82":
        rec = tight.class82_run(budget=budget, shard=k, shards=shards)
    elif mode == "class60":
        rec = tight.class60_run(budget=budget, shard=k, shards=shards)
    elif mode == "av51":
        rec = avtail.class51_run(budget=budget, shard=k, shards=shards)
    rec["wall_seconds"] = round(time.time() - t0, 2)
    rec["complete"] = not rec.get("budget_hit", False)
    shard_file(mode, k).write_text(
        json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "RECEIPT %s shard=%d/%d wall=%.1fs complete=%s budget_hit=%s"
        % (mode, k, shards, rec["wall_seconds"], rec["complete"], rec.get("budget_hit")),
        flush=True,
    )
    return rec


def merge(mode, shards):
    recs = []
    done = []
    for k in range(shards):
        rec = load_shard(mode, k)
        if rec and rec.get("complete"):
            recs.append(rec)
            done.append(k)
    prog = (
        json.loads(PROGRESS.read_text(encoding="utf-8"))
        if PROGRESS.exists()
        else {"modes": {}}
    )
    sec = {
        "shards": {str(k): r for k, r in zip(done, recs)},
        "shards_count": shards,
        "complete": len(done) == shards,
    }
    sec["total"] = aggregate(recs)
    prog["modes"][mode] = sec
    PROGRESS.write_text(
        json.dumps(prog, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "MERGE %s shards=%d/%d complete=%s total=%s"
        % (mode, len(done), shards, sec["complete"], json.dumps(sec["total"], sort_keys=True)[:400]),
        flush=True,
    )
    return sec


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_avtail.py %s [--shards N] [--shard k]" % "|".join(MODES))
    mode = sys.argv[1]
    args = sys.argv[2:]
    if mode == "merge":
        target = args[0]
        shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 8
        merge(target, shards)
        return
    if mode not in MODES:
        raise SystemExit("usage: run_avtail.py %s [--shards N] [--shard k]" % "|".join(MODES))
    shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 8
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 3000.0
    if not any(shard_file(mode, k).exists() for k in range(shards)) and not PROGRESS.exists():
        print("fresh receipts confirmed (%s: no receipt file existed)" % mode, flush=True)
    if "--shard" in args:
        run_shard(mode, int(args[args.index("--shard") + 1]), shards, budget)
        return
    for k in range(shards):
        rec = load_shard(mode, k)
        if rec and rec.get("complete"):
            continue
        run_shard(mode, k, shards, budget)
    sec = merge(mode, shards)
    if sec["complete"]:
        print("PASS_RUN %s" % mode, flush=True)
    else:
        print("PARTIAL_RUN %s complete=false" % mode, flush=True)


if __name__ == "__main__":
    main()
