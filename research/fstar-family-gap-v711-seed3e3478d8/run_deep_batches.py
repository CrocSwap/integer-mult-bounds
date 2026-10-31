#!/usr/bin/env python3
"""Deep-tier batch driver for the v = 7..11 census. Reads the cheap receipts
and data/census_v711/deep-priorities.json, builds bounded deep batches:

  batch A: every gap_pr >= 2 record (headline: the family-gap question),
  batch B: up to 4 box-completeness testbed records (cert witness < v) per
           (fixture, size) cell, smallest v first,
  batch C: the gap_pr == 1 sample (one per cell),

and runs census_v7_11.py --mode deep per (fixture, size) as blocking
subprocesses with periodic receipts. Resumable: already-done deep subsets are
skipped by the census driver's own receipt."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "data", "census_v711")
PY = sys.executable


def load(fn):
    with open(os.path.join(CENSUS, fn), "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    prio = load("deep-priorities.json")
    cheap = {}
    for fn in sorted(os.listdir(CENSUS)):
        if fn.startswith("receipt-") and fn.endswith("-cheap.json"):
            for r in load(fn)["records"]:
                cheap[r["label"]] = r
    batches = {}  # (fixture, size) -> (labels, budget)
    def add(label, budget):
        r = cheap[label]
        fx = label.split("|")[0] + ".json"
        key = (fx, r["v"])
        cur = batches.get(key, ([], 0))
        if label not in cur[0]:
            batches[key] = (cur[0] + [label], max(cur[1], budget))
    for lab in prio["gap2"]:
        add(lab, 240.0)
    # testbed: cert witness < v, up to 4 per cell, smallest v first
    per_cell = {}
    for lab in prio["certltv"]:
        r = cheap[lab]
        key = (lab.split("|")[0], r["v"])
        per_cell.setdefault(key, []).append(lab)
    for key in sorted(per_cell, key=lambda k: (k[1], k[0])):
        for lab in sorted(per_cell[key])[:4]:
            add(lab, 120.0)
    for lab in prio["gap1_sample"]:
        add(lab, 120.0)
    # batch D: the remaining gap-2-potential records (v - named_lo >= 2) -
    # closing the family-gap-2 question on the whole potential set
    for lab in prio.get("potential", []):
        add(lab, 150.0)
    total = sum(len(v[0]) for v in batches.values())
    print("deep batches: %d cells, %d records" % (len(batches), total))
    n = 0
    for (fx, size) in sorted(batches, key=lambda k: (k[1], k[0])):
        labels, budget = batches[(fx, size)]
        n += len(labels)
        print("=== deep %s size=%d labels=%d budget=%.0fs (%d/%d)"
              % (fx, size, len(labels), budget, n, total), flush=True)
        cmd = [PY, "-B", os.path.join(HERE, "census_v7_11.py"),
               "--fixture", fx, "--size", str(size), "--mode", "deep",
               "--labels", ";".join(labels), "--budget-s", str(budget)]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONUNBUFFERED="1")
        res = subprocess.run(cmd, env=env)
        if res.returncode != 0:
            print("FAILED cell %s size=%d rc=%d" % (fx, size, res.returncode))
            return 1
    print("deep batches complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
