#!/usr/bin/env python3
"""Independent check of PR #4610's warp-substitution claims on its emitted word (intqwq, head 4b4c75bc).

#4610 states that its emitted word substitutes 34 of PR4470's 72 warp generators by other invertible binary maps,
each transporting its declared input frame onto its output frame, relabels 422 scalar frames, keeps all 17,453
scalar opcodes with their order and coefficients, and pays 3,298 calls (12 fewer than PR4470's 3,310).
Against PR4470's word from main's pinned constructor (run isolated) and the vendored, sha256-pinned emitted word, this
verifier checks in Python, independently of #4610's Lean shards and Python admission:
  * all 72 bound G maps are invertible on F2^9 (512 distinct images) and map span(from_frame) onto span(to_frame);
    exactly 34 differ from PR4470's maps; op, lender and B_pos agree for all 72;
  * in both orientations the 17,453 scalar opcodes/coefficients agree in order with PR4470's and exactly 422 scalar
    frame labels differ; climbs drop from 3,302 to 3,290, so with the 8 centre jobs the paid calls are 3,298 vs 3,310;
    adapters (448), warps (240), phases (10) and centres (8) keep their counts.
Not covered: Clifford absolute phases / monomial lowering, the symbolic endpoint identity, contract admissibility.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = HERE / "PR4610-ACTUAL-WORD.json.gz"
WORD_SHA256 = "d578875344095047c383ef513e69b9deb9d99d2b75abe14f7359d06365a924ac"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def span(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return frozenset(s)


def apply(cols, x):
    y = 0
    for j in range(9):
        if x >> j & 1:
            y ^= cols[j]
    return y


def pr4470():
    with tempfile.TemporaryDirectory(prefix="audit-cache-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c,'p':p}))")
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
                              str(ROOT / "research/joint-helper-lattice")], capture_output=True, check=True, timeout=180)
    out = json.loads(run.stdout)
    return out["c"], out["p"]


def main():
    raw = WORD.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "vendored #4610 ACTUAL-WORD")
    word = json.loads(gzip.decompress(raw))
    a, (c, p) = word["canonical"], pr4470()
    changed = 0
    for w, w0 in zip(a["warps"], c["warps"]):
        g = w["G_columns"]
        need(len({apply(g, x) for x in range(512)}) == 512, "G invertible")
        need({apply(g, x) for x in span(a["frames"][w["from_frame"]])} == span(a["frames"][w["to_frame"]]),
             "G transports its input frame onto its output frame")
        need(all(w[k] == w0[k] for k in ("op", "lender", "B_pos")), "op, lender, B_pos unchanged")
        changed += g != w0["G_columns"]
    need(len(a["warps"]) == 72 and changed == 34, "34 of 72 G maps changed")
    summary = {}
    for side in ("forward", "backward"):
        new, old = word["programs"][side], p[side]
        sn, so = [e for e in new if e[0] == "scalar"], [e for e in old if e[0] == "scalar"]
        need(len(sn) == len(so) == 17453 and all(x[1] == y[1] for x, y in zip(sn, so)), "scalar opcodes unchanged")
        labels = sum(x[2:] != y[2:] for x, y in zip(sn, so))
        need(labels == 422, "422 scalar frame labels changed")
        kn, ko = Counter(e[0] for e in new), Counter(e[0] for e in old)
        need(ko["climb"] - kn["climb"] == 12 and kn["climb"] + kn["center"] == 3298 and ko["climb"] + ko["center"] == 3310,
             "12 fewer climbs; 3,298 vs 3,310 paid calls")
        need(all(kn[k] == ko[k] for k in ("adapter", "warp", "phase", "center")), "other event counts unchanged")
        summary[side] = {"scalars": len(sn), "label_changes": labels, "climbs": [ko["climb"], kn["climb"]]}
    print(json.dumps({"status": "PASS_PR4610_WARP_SUBSTITUTION_CHECK", "warps": 72, "changed_G": changed,
                      "all_transport_and_invertible": True, "programs": summary, "paid_calls": [3310, 3298],
                      "not_covered": ["absolute phases / monomial lowering", "symbolic endpoint identity",
                                      "contract admissibility"], "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
