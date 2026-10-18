"""Resumable recomputation of the two heavy PR 2773 census anchors (KB3d).

Established method (PR 2773, package research/f7-17point-cover-audit-seedcfa215c2,
Aaron Wang): raw-domain walk over the even group E = F2^6, complete
GL(6,2)-transitive domain through {0, 3}, sub-sharded by the smallest free
element (disjoint and complete), resumable with per-sub-shard receipts in
ANCHOR-PROGRESS.json.  The enumeration itself is the vendored PR 2773 engine
(vendor/agent64_search17.py, byte-pinned; credit: Aaron Wang, PR 2773).

  anchors.py k10b3 [--seconds S]   10-sets through {0,3}, excess <= 3
                                   (recorded anchor: 149,990,400)
  anchors.py k11b4 [--seconds S]   11-sets through {0,3}, excess <= 4
                                   (recorded anchor: level3 = level4 = 0)

Each invocation processes sub-shards until the elapsed budget (default 540 s),
writes receipts after every sub-shard, and exits 0; re-invoke to continue.
A completed run prints PASS_ANCHORS_<mode> with the exact totals and compares
them with the recorded anchor values.
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import agent64_search17 as s17

PROGRESS = HERE / "ANCHOR-PROGRESS.json"

MODES = {
    "k10b3": {
        "k": 10,
        "budget": 3,
        "anchor_count": 149990400,
        "description": "10-sets through {0,3}, pair-sum excess <= 3",
    },
    "k11b4": {
        "k": 11,
        "budget": 4,
        "anchor_count": 0,
        "description": "11-sets through {0,3}, pair-sum excess <= 4",
    },
}


def load_progress(mode):
    """Per-mode sections in one file (v1 kept one mode per file and lost the
    other mode's receipts when switching; migrated on read)."""
    data = {"modes": {}}
    if PROGRESS.exists():
        old = json.loads(PROGRESS.read_text(encoding="utf-8"))
        if "modes" in old:
            data = old
        elif "mode" in old:
            data["modes"][old["mode"]] = {
                k: v for k, v in old.items() if k != "mode"
            }
    return data["modes"].setdefault(mode, {"shards": {}})


def save_progress(mode, prog):
    data = {"modes": {}}
    if PROGRESS.exists():
        old = json.loads(PROGRESS.read_text(encoding="utf-8"))
        if "modes" in old:
            data = old
        elif "mode" in old:
            data["modes"][old["mode"]] = {
                k: v for k, v in old.items() if k != "mode"
            }
    data["modes"][mode] = prog
    PROGRESS.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in MODES:
        raise SystemExit("usage: anchors.py k10b3|k11b4 [--seconds S]")
    budget_seconds = 540.0
    if "--seconds" in sys.argv:
        budget_seconds = float(sys.argv[sys.argv.index("--seconds") + 1])
    spec = MODES[mode]
    prog = load_progress(mode)
    prog["spec"] = {k: v for k, v in spec.items()}
    t_start = time.time()
    for v0 in sorted(s17.EVEN):
        if v0 in (0, 3):
            continue
        key = f"v0={v0}"
        if key in prog["shards"]:
            continue
        t1 = time.time()
        hist, examples = s17.hist_sets(
            s17.EVEN, spec["k"], spec["budget"], fixed=(0, 3, v0), floor=v0
        )
        prog["shards"][key] = {
            "hist": {str(e): n for e, n in sorted(hist.items())},
            "examples": examples,
            "seconds": round(time.time() - t1, 2),
        }
        save_progress(mode, prog)
        print(
            f"ANCHOR {mode} {key} hist={prog['shards'][key]['hist']}"
            f" seconds={prog['shards'][key]['seconds']}"
            f" done={len(prog['shards'])}/62",
            flush=True,
        )
        if time.time() - t_start > budget_seconds:
            print(f"RECEIPT {mode} checkpoint shards={len(prog['shards'])}/62", flush=True)
            return
    total = {}
    for rec in prog["shards"].values():
        for e, n in rec["hist"].items():
            total[e] = total.get(e, 0) + n
    count = sum(total.values())
    prog["total_hist"] = {str(e): n for e, n in sorted(total.items())}
    prog["complete"] = True
    save_progress(mode, prog)
    assert count == spec["anchor_count"], (mode, count, spec["anchor_count"])
    print(f"PASS_ANCHORS_{mode.upper()} count={count} total_hist={prog['total_hist']} shards=62", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
