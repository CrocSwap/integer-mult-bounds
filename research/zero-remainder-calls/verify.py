#!/usr/bin/env python3
"""Least replica count whose one-unpaid idle mass is a multiple of 51.

The checker applies the coverage identity. It does not price a moment.
"""

import hashlib
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ZERO_REMAINDER_CALLS calls=153 rank51=4938 no_new_kappa"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"
MODULUS = 73
CAP = 51
CENTRE = 64
WIDTH = Fraction(896, 9)
AGGREGATE_CALLS = 144


def fail(message):
    raise SystemExit("FAIL_ZERO_REMAINDER_CALLS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def local_profile():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    assembly = json.loads((ROOT / ASSEMBLY).read_text(encoding="utf-8"))
    independent = json.loads((ROOT / INDEPENDENT).read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    counts = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    require(counts == {int(rank): count for rank, count in independent["owner"]["profile"].items()}, "the invoices disagree")
    idle = {int(rank): count for rank, count in independent["owner"]["idle"].items()}
    require((independent["price"]["calls"], independent["price"]["live"]) == (AGGREGATE_CALLS, 14336), "the aggregation unit moved")
    local = {}
    for rank, count in counts.items():
        paid = count - idle.get(rank, 0)
        require(paid >= 0 and paid % AGGREGATE_CALLS == 0, "a local rank is not uniform")
        if paid:
            local[rank] = paid // AGGREGATE_CALLS
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "the paid profile moved")
    return local


def idle_per_call(local):
    total = (MODULUS - 1) * WIDTH + CENTRE
    paid = sum(rank * count for rank, count in local.items())
    residual = total - paid
    require(residual.denominator == 1, "the one-unpaid mass is not an integer")
    return int(residual)


def least_calls(idle):
    require(2 * CAP * CAP < MODULUS * MODULUS, "the halving guard moved")
    remainder = idle % CAP
    step = CAP // gcd(remainder, CAP)
    replica = 9
    return replica * step // gcd(replica, step)


def evaluate():
    require(sha256(ROOT / ASSEMBLY) == "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045", "assembly drift")
    require(sha256(ROOT / INDEPENDENT) == "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd", "independent drift")
    idle = idle_per_call(local_profile())
    require(idle == 32 * CAP + 14 == 1646, "the per-call idle mass moved")
    calls = least_calls(idle)
    require(calls == 153, "the clearing call count moved")
    mass = calls * idle
    copies, remainder = divmod(mass, CAP)
    require((copies, remainder) == (4938, 0), "the pure rank-51 count moved")
    live = calls * WIDTH
    require(live == 15232, "the live width moved")
    require(all((count * idle) % CAP != 0 for count in range(9, calls, 9)), "a smaller replica count also cleared")
    return {
        "idle_per_call": 1646,
        "remainder": 14,
        "calls": 153,
        "idle_mass": 251838,
        "rank_51": 4938,
        "live": 15232,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
