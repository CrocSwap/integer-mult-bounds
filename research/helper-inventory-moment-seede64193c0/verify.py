#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Screen changed helper inventories against the packing ceiling (card complex-new-helper-inventory).

Scope: construction reading of the card's method 1 ("propose a changed helper inventory and
derive an optimistic exact moment"), with a small completed per-call instance and an
independent endpoint/rank-bill check (method 2). No new kappa, no supplier, no frontier change.

Model inputs are the pinned packing-ceiling model of research/complex-local-word-ceiling
(m = 73, families = 896, stages = 9, centre charge 64, one unpaid coordinate per live family).
Candidate inventories are the two recorded changed-helper-inventory contracts outside the
frozen 25-interface catalogue: R489 (PR1004, gauge44-leaver) and R480 (PR1005,
gauge44-leaver8), with per-call paid profile and hosted helper width inventory taken
byte-exactly from their SPEC.json blobs at PR1005 head 779e80aef469bc3a28b19f1adde199871a9a22e3.
A same-inventory profile direction (the PR987 U10 direction) is screened as a labelled
comparison row only.

Exact arithmetic only (fractions) plus one independent float cross-check. Deterministic
output; RESULT.json is a byte-stable receipt written with newline="\\n".
"""
import argparse
import importlib.util
import json
import math
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CEILING_DIR = ROOT / "research" / "complex-local-word-ceiling"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = load("pinned_ceiling", CEILING_DIR / "ceiling.py")
L = load("pinned_levers", CEILING_DIR / "levers.py")

M, FAM, ST, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10**12)

# Selected word per-call paid profile (pinned: complex-local-word-ceiling levers.WORD).
SELECTED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}

# Changed helper inventories outside the frozen catalogue. Profile and hosted helper
# width inventory are byte-exact against the pinned SPEC blobs (see SPEC_PINS).
R489 = {1: 2463, 2: 388, 3: 429, 4: 166, 5: 70, 8: 8}
R489_INV = {4: 65, 5: 32, 7: 39, 8: 122, 9: 231}
R480 = {1: 2412, 2: 418, 3: 418, 4: 170, 5: 68, 8: 8}
R480_INV = {4: 56, 5: 32, 7: 30, 8: 122, 9: 240}

# PR987 U10 direction (+4 rank-3, -8 rank-4, +4 rank-5) applied t times to SELECTED.
U10_DIRECTION = {3: 4, 4: -8, 5: 4}
FAMILY_T = list(range(-4, 18))

SPEC_PINS = [
    ("R489", "research/gauge44-leaver/data/SPEC.json",
     "779e80aef469bc3a28b19f1adde199871a9a22e3", R489, R489_INV),
    ("R480", "research/gauge44-leaver8/data/SPEC.json",
     "779e80aef469bc3a28b19f1adde199871a9a22e3", R480, R480_INV),
]


def profile(t):
    p = dict(SELECTED)
    for r, n in U10_DIRECTION.items():
        p[r] = p.get(r, 0) + t * n
    return {r: n for r, n in sorted(p.items()) if n}


def ceil_bracket(local):
    return C.ceiling(local, M, FAM, ST, CENTRE, grid=GRID)


def fr(x):
    return str(x)


def model_rows():
    rows = []
    names = [("selected", SELECTED), ("R489", R489), ("R480", R480)]
    for t in FAMILY_T:
        names.append(("U10_t%+d" % t, profile(t)))
    out = []
    for name, prof in names:
        q = C.model(prof, M, FAM, ST, CENTRE)
        lo, hi = ceil_bracket(prof)
        mass = sum(r * Q(n) for r, n in prof.items())
        need(mass == q["local_mass"], "mass mismatch")
        out.append(dict(name=name, profile={str(r): prof[r] for r in sorted(prof)},
                        local_mass=fr(mass), idle_mass=fr(q["idle_mass"]),
                        deficit=fr(q["deficit"]),
                        ceiling_lo=fr(lo), ceiling_hi=fr(hi)))
    return out


def float_relax(local, a):
    """Independent float implementation of the relaxation moment at saving a."""
    w = FAM / ST
    total = (M - 1) * w + CENTRE
    R = C.max_idle_rank(M)
    s = sum(n * (r / M) ** (1 - a) for r, n in local.items())
    s += ((total - sum(r * n for r, n in local.items())) / R) * (R / M) ** (1 - a)
    return s / w


def float_root(local):
    lo, hi = 0.0, 0.005
    for _ in range(200):
        mid = (lo + hi) / 2
        if float_relax(local, mid) < 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def check_spec_blobs():
    """Cross-check embedded inventory/profile constants against the pinned git blobs."""
    for label, path, commit, prof, inv in SPEC_PINS:
        try:
            raw = subprocess.run(["git", "cat-file", "-p", commit + ":" + path],
                                 capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return "git-unavailable"
        data = json.loads(raw.decode("utf-8"))
        got = data["providers"]["gauge44"]
        need(got["inventory"] == {str(k): v for k, v in inv.items()},
             label + " helper inventory drifted from the pinned SPEC blob")
        need(got["expected_profile"] == {str(k): v for k, v in prof.items()},
             label + " paid profile drifted from the pinned SPEC blob")
    return "git-blobs-match"


def run():
    # Positive control: the pinned engine reproduces the selected word's ceiling.
    need(L.WORD == SELECTED, "pinned levers.WORD changed")
    sel_lo, sel_hi = ceil_bracket(SELECTED)
    need(sel_lo < Q(1690054109089, 10**15) < sel_hi or Q(1690054109089, 10**15) == sel_lo
         or Q(1690054109089, 10**15) == sel_hi, "selected ceiling moved")

    rows = model_rows()
    by = {r["name"]: r for r in rows}

    # Deficit invariance: the coverage interface fixes the deficit for every inventory.
    need(len({r["deficit"] for r in rows}) == 1, "deficit not invariant")
    need(by["selected"]["deficit"] == fr(Q(320, 9)), "deficit value changed")
    for r in rows:
        need(Q(r["local_mass"]) + Q(r["idle_mass"]) == Q(7232), "rank bill mismatch")
    need(Q(7232) == (M - 1) * Q(FAM, ST) + CENTRE, "coverage identity mismatch")
    need(Q(320, 9) == M * Q(FAM, ST) - Q(7232), "deficit identity mismatch")

    # Screen verdicts against the selected word's packing ceiling (strict bracket separation).
    def gap(name):
        return Q(by[name]["ceiling_lo"]) - Q(by["selected"]["ceiling_hi"])

    need(gap("R489") < 0 and Q(by["R489"]["ceiling_hi"]) < Q(by["selected"]["ceiling_lo"]),
         "R489 not excluded")
    need(gap("R480") < 0 and Q(by["R480"]["ceiling_hi"]) < Q(by["selected"]["ceiling_lo"]),
         "R480 not excluded")
    need(Q(by["U10_t+1"]["ceiling_lo"]) > Q(by["selected"]["ceiling_hi"]),
         "U10 direction no longer beats")

    family = [by["U10_t%+d" % t] for t in FAMILY_T]
    best = max(family, key=lambda r: Q(r["ceiling_lo"]))
    for r in family:
        need(Q(r["ceiling_lo"]) < Q(r["ceiling_hi"]) + GRID, "bracket width")

    # Independent float cross-check of the endpoint and the rank bill.
    for name in ("selected", "R489", "R480", "U10_t+1"):
        r = by[name]
        lo, hi = Q(r["ceiling_lo"]), Q(r["ceiling_hi"])
        need(float_relax({int(k): v for k, v in r["profile"].items()}, float(lo)) < 1 + 1e-9,
             "float endpoint disagrees below " + name)
        need(float_relax({int(k): v for k, v in r["profile"].items()}, float(hi)) > 1 - 1e-9,
             "float endpoint disagrees above " + name)
        root = float_root({int(k): v for k, v in r["profile"].items()})
        need(float(lo) - 5e-12 < root < float(hi) + 5e-12, "float root outside bracket " + name)

    # Controls: one extra rank-1 child lowers the ceiling; broken contracts are rejected.
    worse = dict(SELECTED)
    worse[1] += 1
    w_lo, w_hi = ceil_bracket(worse)
    need(w_hi < sel_lo, "control: one extra rank-1 child did not lower the ceiling")
    try:
        C.model({1: 8000}, M, FAM, ST, CENTRE)
    except ValueError as err:
        need("coverage law" in str(err), "wrong rejection reason for over-mass profile")
    else:
        raise ValueError("control accepted: over-mass profile")
    try:
        C.model(SELECTED, M, FAM, ST, CENTRE, R=52)
    except ValueError as err:
        need("halving guard" in str(err), "wrong rejection reason for rank cap 52")
    else:
        raise ValueError("control accepted: idle rank cap 52")

    blob_state = check_spec_blobs()

    receipt = {
        "schema_version": 1,
        "model": {"m": M, "families": FAM, "stages": ST, "centre": CENTRE,
                  "unpaid": 1, "idle_rank_cap": C.max_idle_rank(M)},
        "deficit_per_call": fr(Q(320, 9)),
        "total_mass_per_call": "7232",
        "selected_ceiling": {"lo": by["selected"]["ceiling_lo"],
                             "hi": by["selected"]["ceiling_hi"]},
        "screen": {
            "R489_beats": False,
            "R480_beats": False,
            "U10_t+1_beats": True,
            "margin": "strict beat: candidate bracket entirely above the selected bracket",
        },
        "rows": rows,
        "family_direction": {str(k): v for k, v in sorted(U10_DIRECTION.items())},
        "family_argmax": {"name": best["name"], "ceiling_lo": best["ceiling_lo"],
                          "ceiling_hi": best["ceiling_hi"]},
    }
    return receipt, blob_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = parser.parse_args()
    receipt, blob_state = run()
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(payload, encoding="utf-8", newline="\n")
        print("WROTE", target.name)
    else:
        need(target.read_bytes() == payload.encode("utf-8"),
             "RESULT.json does not match the recomputed receipt")
    print("PASS_HELPER_INVENTORY_MOMENT_SCREEN",
          "selected", receipt["selected_ceiling"]["lo"],
          "R489", receipt["rows"][1]["ceiling_hi"],
          "R480", receipt["rows"][2]["ceiling_hi"],
          "argmax", receipt["family_argmax"]["name"],
          receipt["family_argmax"]["ceiling_lo"],
          "blobs", blob_state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
