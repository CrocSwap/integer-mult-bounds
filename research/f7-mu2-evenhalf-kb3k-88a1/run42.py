"""Resumable walk driver for the KB3j package (f7-18point-av42-kb3j-b1).

Modes (deterministic sharding over the 169,911 normalized U; per-shard
receipt files AV42-<k>.json; one progress section per mode in
AV42-PROGRESS.json after `merge`):

  av42   the class (12,6) A-vanish (4,2) decision walk (walk42.class42_run):
         complete over all normalized (U, V) pairs with |U+V| >= 24 and all
         admissible W 4-sets per pair, exact four-line test on each.
  size   sizing probe: walk a few U slices and report pairs/s and the
         |U+V| distribution (no receipts; budget-honest sizing evidence).
  k3     complete (4,2)-shape census over F2^3 halves (walk42.census_k3).
  k4     complete normalized (4,2)-shape census of floor-surviving
         (u,u,w) classes over F2^4 halves (walk42.census_k4).

Usage: python3 -I -B run42.py <mode> [--shards N] [--shard k] [--budget S]
       python3 -I -B run42.py merge <mode> [--shards N]

Shard receipt files are written ONLY by their own shard process (safe for
parallel shard runs); `merge` rebuilds AV42-PROGRESS.json from the shard
files (idempotent, run after all shards finish).  A shard is processed only
if its receipt file is absent or incomplete; re-invoke to continue.
Receipts carry explicit complete/budget_hit flags (a partial walk is never
recorded as complete).  Starting a mode with no receipt prints 'fresh
receipts confirmed' (the receipt-validation trap: replaying against a
committed receipt validates nothing).
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import walk42  # noqa: E402

PROGRESS = HERE / "AV42-PROGRESS.json"
MODES = ("av42", "size", "k3", "k4")
TAGS = {"av42": "AV42"}


def shard_file(mode, k):
    return HERE / ("AV42-%s-%d.json" % (TAGS.get(mode, mode.upper()), k))


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
    rec = walk42.class42_run(budget=budget, shard=k, shards=shards)
    rec["wall_seconds"] = round(time.time() - t0, 2)
    rec["complete"] = not rec.get("budget_hit", False)
    shard_file(mode, k).write_text(
        json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        "RECEIPT %s shard=%d/%d wall=%.1fs complete=%s budget_hit=%s u=%d pairs=%d w_cand=%d covering=%d"
        % (
            mode,
            k,
            shards,
            rec["wall_seconds"],
            rec["complete"],
            rec.get("budget_hit"),
            rec["u_checked"],
            rec["uv_pairs"],
            rec["w_candidates"],
            rec["covering_configs"],
        ),
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


def size_probe(budget):
    """Budget-honest sizing: walk a bounded number of normalized U slices
    with the real engine and report pairs/s plus the |U+V| histogram
    (need 24)."""
    t0 = time.time()
    rec = walk42.class42_run(budget=budget, shard=0, shards=2048, u_limit=64, progress=True)
    el = max(time.time() - t0, 1e-9)
    print(
        "SIZE u_checked=%d uv_pairs=%d w_candidates=%d covering=%d pairs_per_s=%.1f hist=%s seconds=%.1f"
        % (
            rec["u_checked"],
            rec["uv_pairs"],
            rec["w_candidates"],
            rec["covering_configs"],
            rec["uv_pairs"] / el,
            json.dumps(rec["uv_pairs_by_sumset_size"], sort_keys=True),
            el,
        ),
        flush=True,
    )
    if rec["u_checked"] > 0:
        per_u = rec["uv_pairs"] / rec["u_checked"]
        est_pairs = per_u * 169911
        print(
            "SIZE estimate total_pairs=%.3e total_core_hours_at_probe_rate=%.1f"
            % (est_pairs, el / rec["u_checked"] * 169911 / 3600.0),
            flush=True,
        )


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit("usage: run42.py %s [--shards N] [--shard k]" % "|".join(MODES))
    mode = sys.argv[1]
    args = sys.argv[2:]
    if mode == "merge":
        target = args[0]
        shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 8
        merge(target, shards)
        return
    if mode not in MODES:
        raise SystemExit("usage: run42.py %s [--shards N] [--shard k]" % "|".join(MODES))
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 3600.0
    if mode == "size":
        size_probe(budget)
        return
    if mode == "k3":
        t0 = time.time()
        res = walk42.census_k3()
        out = HERE / "CENSUS-K3.json"
        out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        n_cover = sum(1 for r in res.values() if r["covers"] > 0)
        n_pair = sum(1 for r in res.values() if r["kill_shape"] == "pair")
        print(
            "CENSUS_K3 classes=%d cover=%d pair_killed=%d seconds=%.1f"
            % (len(res), n_cover, n_pair, time.time() - t0),
            flush=True,
        )
        return
    if mode == "k4":
        t0 = time.time()
        res = walk42.census_k4(u_max=4, w_max=6)
        out = HERE / "CENSUS-K4.json"
        out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        n_cover = sum(1 for r in res.values() if r.get("pairs_with_cover", 0) > 0)
        n_pair = sum(1 for r in res.values() if r["kill_shape"] == "pair")
        print(
            "CENSUS_K4 classes=%d cover=%d pair_killed=%d seconds=%.1f"
            % (len(res), n_cover, n_pair, time.time() - t0),
            flush=True,
        )
        return
    shards = int(args[args.index("--shards") + 1]) if "--shards" in args else 8
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
