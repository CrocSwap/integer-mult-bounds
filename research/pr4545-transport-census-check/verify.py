#!/usr/bin/env python3
"""Independent recount of the transport census in PR #4545 (Clear1nsight) for PR4470's chronological words.

Main's pinned #4470 constructor (research/joint-helper-lattice/native_joint.py, run isolated) emits both the patched
#4470 certificate/word and the pre-patch PR4447 certificate/word. With this file's own frame tracking (each
persistent field keeps its current frame; a scalar contact or warp entrance at a different frame, and the final exit,
each require one transport E -> F), it checks:
  * 3,302 transport occurrences over 2,856 distinct (E, F) pairs in each orientation of the #4470 word;
  * 406 distinct pairs new relative to the PR4447 word, comparing exact ordered frame bases (not frame indices,
    which differ between the two certificates); the PR4447 word itself has 3,355 occurrences over 2,934 pairs;
  * 408 helper owners (632 persistent fields).
#4545's 17 helper-boundary recipes depend on its adapter-recipe definitions and are not recounted.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def roles(e):
    g = e[1]
    return g[1:3] if g[0] in ("add", "copy") else g[1:2]


def transports(cert, program):
    frames = cert["frames"]
    state, occ = list(cert["start"]), Counter()
    for e in program:
        if e[0] == "scalar":
            for r in roles(e):
                if r[0] == "L" and state[r[1]] != e[2]:
                    occ[tuple(frames[state[r[1]]]), tuple(frames[e[2]])] += 1
            for r in roles(e):
                if r[0] == "L":
                    state[r[1]] = e[2]
        elif e[0] == "warp":
            r = e[1][1]
            if state[r] != e[3]:
                occ[tuple(frames[state[r]]), tuple(frames[e[3]])] += 1
            state[r] = e[4]
    for r, f in enumerate(cert["final"]):
        if state[r] != f:
            occ[tuple(frames[state[r]]), tuple(frames[f])] += 1
    return occ


def main():
    with tempfile.TemporaryDirectory(prefix="census-cache-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c,'p':p,'b':b,'o':o}))")
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
                              str(ROOT / "research/joint-helper-lattice")], capture_output=True, check=True, timeout=120)
    d = json.loads(run.stdout)
    new, old = d["c"], d["b"]
    need(new["R"] == 408 and len(new["final"]) == 632, "408 helper owners, 632 persistent fields")
    counts = {}
    for orient in ("forward", "backward"):
        occ = transports(new, d["p"][orient])
        need(sum(occ.values()) == 3302 and len(occ) == 2856, f"#4470 {orient}: 3,302 occurrences over 2,856 pairs")
        counts[orient] = occ
    old_occ = transports(old, d["o"]["forward"])
    need(sum(old_occ.values()) == 3355 and len(old_occ) == 2934, "PR4447 word: 3,355 occurrences over 2,934 pairs")
    fresh = set(counts["forward"]) - set(old_occ)
    need(len(fresh) == 406, "406 distinct transport pairs new relative to PR4447")
    need(set(counts["backward"]) - set(transports(old, d["o"]["backward"])) == fresh, "same 406 in the backward word")
    print(json.dumps({"status": "PASS_PR4545_TRANSPORT_CENSUS_CHECK", "occurrences_per_orientation": 3302,
                      "distinct_pairs": 2856, "new_pairs_vs_pr4447": 406, "pr4447_occurrences": 3355,
                      "pr4447_distinct_pairs": 2934, "helper_owners": 408, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
