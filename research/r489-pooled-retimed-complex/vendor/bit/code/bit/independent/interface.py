"""Audit the structural hypotheses of PR #425's scalar-interface lemma (Zhihao Chen) on a bitE8/1 word whose source
registers may be gate destinations.  No producer code is imported.
usage: interface.py WORD.json.gz [--json OUT]

PR #425's lemma (research/hamming-mutable-basis-complex/.../hamming/PROOF.txt, section 3): write z = (x, s) for the
sources and the dirty helpers and y for the targets.  If no target feeds a z register, the raw word has block form
z' = U z, y' = V y + J x + K s.  A frame-zero preconditioner y <- V^-1 y - V^-1 K s (here: the dirt compensation D)
and U^-1 executed at the common full frame after the last climb (here: the cleanup C) give exactly
(x, s, y) -> (x, s, y + x).  Over F2 the conclusion is checked column by column by the relaxed PR #370 checker; this
script checks the hypotheses that make the word an instance of the lemma:
  (1) no gate anywhere whose destination is a z register (source or helper) reads a target register;
  (2) D writes only targets and reads only helpers, at frame zero; the scatter writes only targets;
  (3) every cleanup gate acts at the full frame and has a z destination; C is the literal reverse of the z-destination
      gates of A and B (so C = U^-1 gate by gate over F2);
  (4) targets are written only in B, D and the scatter, and B writes only targets (V = I here).
It also reports where sources are written (frame dimensions), which is the review point of this package.
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import gzip
import json
import sys
from collections import Counter
from fractions import Fraction as Fr

w = json.load(gzip.open(sys.argv[1], "rt"))
v, R = w["v"], w["R"]
n = 2 * v + R
lines = w["lines"]


def rank(idx):
    rows = [[Fr(x) for x in lines[i]] for i in idx]
    rk = 0
    for col in range(8):
        p = next((i for i in range(rk, len(rows)) if rows[i][col] != 0), None)
        if p is None:
            continue
        rows[rk], rows[p] = rows[p], rows[rk]
        for i in range(len(rows)):
            if i != rk and rows[i][col] != 0:
                f = rows[i][col] / rows[rk][col]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[rk])]
        rk += 1
    return rk


fdim = [rank(f) if f else 0 for f in w["frames"]]
is_y = lambda r: v <= r < 2 * v
is_z = lambda r: 0 <= r < n and not is_y(r)
full = [k for k, d in enumerate(fdim) if d == 8]
zero = [k for k, d in enumerate(fdim) if d == 0]
assert len(full) == 1 and len(zero) == 1
FULL, ZERO = full[0], zero[0]

bad = []
for sec in ("D", "A", "B", "C"):
    for k, (f, d, srcs) in enumerate(w[sec]):
        if is_z(d) and any(is_y(s) for s in srcs):
            bad.append((sec, k))
assert not bad, ("(1) a target feeds a z register", bad[:5])
for f, d, srcs in w["D"]:
    assert f == ZERO and is_y(d) and all(s >= 2 * v for s in srcs), "(2) D must be target <- helpers at frame zero"
assert len(w["scatter"]) == v and all(0 <= k < len(w["ret"]) for row in w["scatter"] for k in row), "(2) scatter rows"
assert all(q >= 2 * v for q in w["ret"]), "(2) retained totals live on helpers"
assert all(f == FULL and is_z(d) and all(is_z(s) for s in srcs) for f, d, srcs in w["C"]), "(3) C off the full frame"
zg = [[FULL, d, list(srcs)] for sec in ("A", "B") for f, d, srcs in w[sec] if is_z(d)]
assert [list(g) for g in w["C"]] == list(reversed(zg)), "(3) C is not the literal reverse of the z-gates of A and B"
assert all(is_z(d) for f, d, srcs in w["A"]), "(4) a target is written in phase A"
assert all(is_y(d) for f, d, srcs in w["B"]), "(4) phase B writes a z register (V = I form expected)"
xa = [(f, d, srcs) for f, d, srcs in w["A"] if d < v]
xb = [(f, d, srcs) for f, d, srcs in w["B"] if any(s < v for s in srcs)]
print("PASS PR #425 interface hypotheses: no target feeds a source or helper; D at frame 0 (targets <- helpers);"
      " C = literal U^-1 at the full frame (%d gates); B writes only targets" % len(w["C"]))
print("   sources written in phase A: %d gates into %d of %d source registers, at frame dimensions %s; operands: %s" %
      (len(xa), len({d for _, d, _ in xa}), v, dict(sorted(Counter(fdim[f] for f, _, _ in xa).items())),
       dict(Counter("source" if s < v else "helper" for _, _, srcs in xa for s in srcs))))
print("   phase-B gates reading a (rewritten) source register: %d; the matching %d cleanup gates restore every source" %
      (len(xb), sum(1 for f, d, srcs in w["C"] if d < v)))
if "--json" in sys.argv:
    json.dump(dict(status="PASS_PR425_INTERFACE_HYPOTHESES", source_destination_gates_A=len(xa),
                   sources_rewritten=len({d for _, d, _ in xa}),
                   source_write_frame_dims={str(k): x for k, x in sorted(Counter(fdim[f] for f, _, _ in xa).items())},
                   phase_B_reads_of_sources=len(xb), cleanup_gates=len(w["C"]),
                   cleanup_source_gates=sum(1 for f, d, srcs in w["C"] if d < v)),
              open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
