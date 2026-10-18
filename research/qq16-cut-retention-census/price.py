#!/usr/bin/env python3
"""Map the retention census onto philippeVV's C=0 / C=64 pricing convention.

This is a convention transfer, not a new cost model.  The convention is
Philippe Van Velzen's `price3.py` (https://github.com/philippeVV/integer-mult-bounds,
commit 680d0997621a2cecfef2186ab143377658687825, path
research/joint-query-first-pair-catalogue/four-bank/price3.py, read on 2026-10-15;
sha256 1c2ca9a4f89d7851dee6b765119f1f84f1227e30ec23f3e169aa327d2cc7f1f7; the three
hard-coded reproduction values below are copied from price3.json at that commit),
re-implemented here in a few lines against the pinned repository
`research/complex-local-word-ceiling/ceiling.py`.  Its prices are unreviewed:

* per-call local profile MIX = (5 F + 4 B)/9 with the QQ16 F and B profiles;
* base centre charge C (0 or 64);
* a retained coordinate held for L live calls costs, per coordinate-call,
  either one rank-8 child plus 8 units of total mass ("centre") or 72 units
  of total mass paid by ideal idle children ("family"); coordinate-calls are
  per nine-call replica, so the per-call increment is coords * L / 9.

`None` means ceiling.ceiling raises ValueError, i.e. the relaxation has no
positive saving (no admissible ceiling).  Each retained port array counts as
one coordinate per owner per replica, the unit of #2074 Theorem B.

Apache-2.0.  Prepared by thakrarsagar with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5).
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CEILING = ROOT / "research/complex-local-word-ceiling/ceiling.py"
CEILING_PIN = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
if sha256(CEILING.read_bytes()).hexdigest() != CEILING_PIN:
    raise SystemExit("ceiling.py pin mismatch")
sys.path.insert(0, str(CEILING.parent))
import ceiling as C  # noqa: E402

M, FAM, ST, GRID = 73, 896, 9, Q(1, 10 ** 10)
SEL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
B = {1: 2436, 2: 418, 3: 432, 4: 142, 5: 82}
F = {1: 2420, 2: 418, 3: 432, 4: 142, 5: 82}
MIX = {r: Q(5 * F[r] + 4 * B[r], 9) for r in B}


def cap(profile, centre):
    try:
        return C.ceiling(profile, M, FAM, ST, centre, grid=GRID)[1]
    except ValueError:
        return None


def priced(base, coordinate_calls, kind):
    n = Q(coordinate_calls, 9)
    p, c = dict(MIX), Q(base)
    if kind == "centre":
        p[8] = p.get(8, 0) + n
        c += 8 * n
    else:
        c += 72 * n
    return cap(p, c)


def largest(base, kind, beats):
    """Largest integer coordinate-calls per replica whose ceiling exists and beats `beats`."""
    ok = lambda x: (lambda a: a is not None and a > beats)(priced(base, x, kind))
    if not ok(0):
        return None
    lo, hi = 0, 1
    while ok(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def main():
    res = json.loads((Path(__file__).resolve().parent / "RESULT.json").read_text())
    pi = res["per_item"]
    f0 = sum(pi[k]["d18"]["copy_required"] for k in ("x1_A", "x1_T", "y1_A", "y1_T", "x1_S"))
    b1 = sum(pi[k]["d18"]["copy_required"] for k in ("y2_A", "C=x2_U"))
    d1 = sum(pi[k]["d1"]["copy_required"] for k in pi)
    # live calls held: F0 cut -> d1 spans B1 (1 call); F0 cut -> d18 spans B1,F2,...,F8 (8 calls);
    # B1 cut -> d18 spans F2,...,F8 (7 calls).  Bridges and the terminal are not calls.
    demand = {"d1": d1 * 1, "d18": f0 * 8 + b1 * 7,
              # L2 variant (extra Y2_U read outside PR2443's contract): 32 retained arrays for 1 call.
              "d1_L2_variant": res["leads"]["L2_variant_d1"]["retained_F0_cut_arrays"] * 1,
              # Free controller (no retention at all), for reference.
              "zero_retention": 0}
    sel = cap(SEL, 64)
    # Convention reproduction: two rows of philippeVV's committed price3.json (fork 680d0997).
    if (str(sel), str(priced(0, 62, "centre")), str(priced(0, 64, "centre"))) != (
            "8450271/5000000000", "5267381/2500000000", "5056523/2500000000"):
        raise SystemExit("price3 convention not reproduced")
    out = {"selected_ceiling": str(sel), "copied_arrays": {"d1": d1, "d18_F0_cut": f0, "d18_B1_cut": b1},
           "coordinate_calls_per_replica": demand, "rows": [], "break_even": {}}
    for base in (0, 64):
        for kind in ("centre", "family"):
            for name, x in sorted(demand.items()):
                a = priced(base, x, kind)
                out["rows"].append({"C": base, "kind": kind, "decode": name, "coordinate_calls": x,
                                    "ceiling": None if a is None else str(a),
                                    "vs_selected_percent": None if a is None else "%+.4f" % (float(a / sel - 1) * 100)})
            out["break_even"]["C%d_%s" % (base, kind)] = {
                "max_coordinate_calls_positive_saving": largest(base, kind, Q(0)),
                "max_coordinate_calls_beating_selected": largest(base, kind, sel)}
    return out


if __name__ == "__main__":
    out = main()
    here = Path(__file__).resolve().parent / "PRICE.json"
    if "--write" in sys.argv:
        here.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    elif json.loads(here.read_text()) != out:
        raise SystemExit("PRICE.json mismatch")
    print(json.dumps(out, indent=1))
    print("PASS_QQ16_CUT_RETENTION_PRICE_TRANSFER")
