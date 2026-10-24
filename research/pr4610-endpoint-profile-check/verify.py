#!/usr/bin/env python3
"""Scoped independent check of PR #4610 (intqwq): conditional kappa 0.00302152 from changed native warp maps.

#4610 (head 4b4c75bc) substitutes 34 of PR4470's 72 independent warp generators by other invertible maps and relabels
422 scalar frames, keeping every scalar opcode and external interface, and claims the paid list
    Pnew = 2201 H1 + 412 H2 + 506 H3 + 135 H4 + 36 H5 + 8 H8   (Pold = 2237 H1 + 388 H2 + 494 H3 + 147 H4 + 36 H5 + 8 H8),
    Pold - Pnew = 12(3 H1 - 2 H2 - H3 + H4) > 0 for every 0 < t < 1.
This verifier checks, independently of #4610's code (nothing imported from it):
  1. endpoint frames (the test #4596 failed, see #4604): the vendored emitted ACTUAL-WORD (sha256-pinned, its
     canonical payload hash equal to #4610's frozen value) has, for all 632 roles, the same start and final frame
     (as subspaces of F2^9) as PR4470's word from main's pinned constructor, and the same 112 ports, v and h;
  2. the emitted word's local profile is exactly Pnew; Pold - Pnew = 12(3,-2,-1,1) on (H1,H2,H3,H4); paid rank mass is
     unchanged (5,327) with 12 fewer jobs per call; 18 calls give 216 fewer, 64,620 -> 64,404;
  3. 3 - 2*2^a - 3^a + 4^a > 0 for every 0 < a < 1 (so the difference is positive whichever of t, 1 - t is the
     exponent): with x = 2^a in (1,2) and c = log2 3, it equals g(x) = (x-1)^2 + 2 - x^c; g'' >= 2 - c(c-1) > 0 because
     c < 2 (3 < 4), and g'(2) = 2 - 3c/2 < 0 because c > 4/3 (27 > 16); so g is convex and strictly decreasing on
     [1,2] with g(2) = 0. The integer facts are checked, and g is evaluated on a grid as a numerical sanity control.
Not covered: native Clifford/phase lowering, the Lean certificates, the outer crossing interval.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = HERE / "PR4610-ACTUAL-WORD.json.gz"
WORD_SHA256 = "d578875344095047c383ef513e69b9deb9d99d2b75abe14f7359d06365a924ac"
PAYLOAD_SHA256 = "4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc"
P_NEW = {1: 2201, 2: 412, 3: 506, 4: 135, 5: 36, 8: 8}
P_OLD = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def span(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return frozenset(s)


def pr4470_word():
    with tempfile.TemporaryDirectory(prefix="audit-cache-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c}))")
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
                              str(ROOT / "research/joint-helper-lattice")], capture_output=True, check=True, timeout=180)
    return json.loads(run.stdout)["c"]


def main():
    raw = WORD.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "vendored #4610 ACTUAL-WORD")
    word = json.loads(gzip.decompress(raw))
    payload = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "canonical payload equals #4610 freeze")
    a = word["canonical"]
    c = pr4470_word()
    # 1. endpoint frames
    need(len(a["final"]) == len(c["final"]) == 632 and len(a["start"]) == len(c["start"]) == 632, "632 roles")
    final_same = sum(span(a["frames"][i]) == span(c["frames"][j]) for i, j in zip(a["final"], c["final"]))
    start_same = sum(span(a["frames"][i]) == span(c["frames"][j]) for i, j in zip(a["start"], c["start"]))
    need(final_same == 632 and start_same == 632, "every start and final frame equals PR4470's")
    need(a["ports"] == c["ports"] and a["v"] == c["v"] == 112 and a["h"] == c["h"] == 9, "ports, v, h unchanged")
    need(a["warps"] != c["warps"], "the warp layer itself did change")
    # 2. profile arithmetic
    need({int(k): v for k, v in a["local_profile"].items()} == P_NEW, "emitted local profile is Pnew")
    diff = {r: P_OLD[r] - P_NEW[r] for r in P_OLD}
    need(diff == {1: 36, 2: -24, 3: -12, 4: 12, 5: 0, 8: 0}, "Pold - Pnew = 12(3 H1 - 2 H2 - H3 + H4)")
    mass = lambda p: sum(r * n for r, n in p.items())
    need(mass(P_OLD) == mass(P_NEW) == 5327 and sum(P_OLD.values()) - sum(P_NEW.values()) == 12, "mass and jobs")
    need(64620 - 18 * 12 == 64404, "controller paid calls")
    # 3. moment positivity: exact facts used by the convexity proof, then a numerical sanity grid
    need(3 < 4 and 27 > 16, "1 < c = log2 3 < 2 and c > 4/3")
    c_log = math.log2(3)
    need(2 - c_log * (c_log - 1) > 1 and 2 - 1.5 * c_log < -0.3, "g'' > 0 and g'(2) < 0 (numerical margins)")
    grid = [k / 1000 for k in range(1, 1000)]
    need(all(3 - 2 * 2 ** s - 3 ** s + 4 ** s > 0 for s in grid), "grid sanity: 3 - 2*2^a - 3^a + 4^a > 0")
    need(abs(3 - 2 * 2 - 3 + 4) == 0 and 3 - 2 - 1 + 1 == 1, "endpoint values 0 at a = 1 and 1 at a = 0")
    print(json.dumps({"status": "PASS_PR4610_SCOPED_CHECK",
                      "endpoint_frames_equal_pr4470": {"start": start_same, "final": final_same},
                      "ports_v_h_unchanged": True, "warps_changed": True,
                      "canonical_payload_hash_matches_freeze": True,
                      "local_profile": P_NEW, "paid_rank_mass": 5327, "jobs_removed_per_call": 12,
                      "moment_difference_positive_on_open_interval": True,
                      "not_covered": ["native phase lowering", "Lean certificates", "outer crossing interval"],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
