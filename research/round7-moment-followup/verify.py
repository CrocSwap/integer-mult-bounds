#!/usr/bin/env python3
"""Exact additive moment/assembly check above the frozen CrocSwap PR #97 basis.

This checks arithmetic only. The physical networks and the inherited analytic
and fixed-tape interfaces remain the dependencies described in PR #97.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

if not __debug__:
    raise SystemExit("Assertions required; do not use Python -O")
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/deferred-signed"
BIT = BASE / "swapnil-round7"
A0 = Q(63983013240044, 10**18)
A1 = Q(63983013240045, 10**18)
OLD_A = Q(31987, 500000000)
B = Q(36926111, 500000000000)
ETA = Q(1, 10**8)
BETA = Q(1, 10)
GRID = 10**12

from check_sources import check_sources
from refine_moment import taylor_moment
from independent_moment import moment as independent_moment

sys.path.insert(0, str(ROOT / "scripts"))
from structured_bulk_assembly import assembly, js


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def certificate():
    count = check_sources()
    imported = read(BIT / "lean/round7-histograms.json")["bit"]
    physical = read(BASE / "round7-literal-ledger/result.json")
    assert physical["histogram_matches_external"]
    hist = {int(t): n for t, n in physical["histogram"].items()}
    assert hist == dict(imported["hist"])
    assert (imported["m"], imported["W"], imported["s"]) == (529, 108516254, 57403754177)
    assert sum(t*n for t,n in hist.items()) == imported["s"]

    primary0 = taylor_moment(imported, A0)
    primary1 = taylor_moment(imported, A1)
    secondary0 = independent_moment(imported, A0, "exponential")
    secondary1 = independent_moment(imported, A1, "exponential")
    assert primary0["upper"] < 1 < primary1["lower"]
    assert Q(secondary0["upper"]) < 1 < Q(secondary1["lower"])
    # Every width is strictly between 0 and m, so the true moment increases.
    assert all(0 < t < imported["m"] and n > 0 for t,n in imported["hist"])

    old = read(BASE / "round7-balanced-assembly-candidate.json")
    assert Q(old["candidate_kappa"]) == Q(63965813, GRID)
    assert Q(old["assembly"]["parameters"]["a_bit"]) == OLD_A
    assert Q(old["assembly"]["parameters"]["a_complex"]) == B
    assert Q(old["assembly"]["parameters"]["eta"]) == ETA
    assert Q(old["assembly"]["parameters"]["beta"]) == BETA
    assert old["bridge"]["bit"]["m"] == imported["m"]
    assert old["bridge"]["bit"]["W"] == imported["W"]
    assert old["bridge"]["bit"]["maxchild"] == max(hist)
    bridge = old["bridge"]
    bridge["rows"]["degree_gap"] = Q(bridge["rows"]["degree_gap"])
    baseline = assembly(OLD_A, B, bridge, Q(old["candidate_kappa"]), eta=ETA, beta=BETA)
    assert js(baseline) == old["assembly"]

    q = A0 * (1 - 2*ETA)
    c = q * (1 + ETA)
    epsilon = (1 - ETA) / (1 + c + q)
    upper = epsilon * q
    candidate = Q((upper * GRID).numerator // (upper * GRID).denominator, GRID)
    cert = assembly(A0, B, bridge, candidate, eta=ETA, beta=BETA)
    assert candidate > Q(old["candidate_kappa"]) > Q(1, 16384)
    assert len(cert["strict_constraints"]) == 47
    assert len(cert["margins"]) == 7
    assert all(v > 0 for v in cert["strict_constraints"].values())
    assert all(v > candidate for v in cert["margins"].values())
    assert cert["minimum_margin"] == upper
    assert 0 < cert["absorption_gap"] < Q(1, GRID)
    # The next grid point fails the binding compact-phase-layer margin.
    assert candidate + Q(1, GRID) >= upper
    try:
        assembly(A0, B, bridge, candidate + Q(1, GRID), eta=ETA, beta=BETA)
    except AssertionError:
        rejected = True
    else:
        rejected = False
    assert rejected

    return dict(
        status="PASS exact additive moment and CrocSwap assembly arithmetic",
        scope="Conditional on PR97 physical construction, retained analytic/fixed-tape interfaces, and its complex saving; not an unconditional theorem.",
        basis_commit="f5f9c56e637463cac1e300d1589ccf42838f688a",
        pin_count=count,
        source_sha256={k: digest(ROOT/k) for k in (
            "scripts/structured_bulk_assembly.py",
            "research/deferred-signed/round7-balanced-assembly-candidate.json",
            "research/deferred-signed/round7-literal-ledger/result.json",
            "research/deferred-signed/swapnil-round7/lean/round7-histograms.json",
        )},
        bit_saving=A0, adjacent_rejected_bit_saving=A1,
        true_moment_primary=dict(accepted_upper=primary0["upper"], adjacent_lower=primary1["lower"]),
        true_moment_independent=dict(accepted_upper=secondary0["upper"], adjacent_lower=secondary1["lower"]),
        old_kappa=Q(old["candidate_kappa"]), new_kappa=candidate,
        gain=candidate-Q(old["candidate_kappa"]),
        exact_binding_margin=upper, adjacent_kappa_grid_rejected=rejected,
        assembly=cert,
        dependency="No new network, complex moment, semantic/tape interface, or unconditional multiplication proof.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New JSON receipt; refuses overwrite")
    args = parser.parse_args()
    result = certificate()
    print("PASS old", result["old_kappa"], "new", result["new_kappa"],
          "gain", result["gain"], "pins", result["pin_count"])
    if args.output:
        assert not args.output.exists(), "Do not overwrite an existing receipt"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(js(result), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
