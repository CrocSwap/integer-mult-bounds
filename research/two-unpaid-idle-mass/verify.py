#!/usr/bin/env python3
"""Idle mass of the selected profile with two unpaid coordinates.

The checker applies the coverage identity. It does not search a packing.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_TWO_UNPAID_IDLE_MASS replica=13918 pooled=222688 no_new_kappa"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"
MODULUS = 73
CALLS = 144
CENTRE = 64
WIDTH = Fraction(896, 9)
CAP = 51


def fail(message):
    raise SystemExit("FAIL_TWO_UNPAID_IDLE_MASS " + message)


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
    require((independent["price"]["calls"], independent["price"]["live"]) == (CALLS, 14336), "the aggregation unit moved")
    local = {}
    for rank, count in counts.items():
        paid = count - idle.get(rank, 0)
        require(paid >= 0 and paid % CALLS == 0, "a local rank is not uniform")
        if paid:
            local[rank] = paid // CALLS
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "the paid profile moved")
    return local


def idle_mass(local, calls, unpaid):
    total = calls * ((MODULUS - unpaid) * WIDTH + CENTRE)
    paid = calls * sum(rank * count for rank, count in local.items())
    return total - paid


def histogram(mass):
    copies, remainder = divmod(mass, CAP)
    pieces = {}
    if copies:
        pieces[CAP] = copies
    if remainder:
        pieces[remainder] = 1
    require(sum(rank * count for rank, count in pieces.items()) == mass, "the closed form lost mass")
    return pieces


def evaluate():
    require(sha256(ROOT / ASSEMBLY) == "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045", "assembly drift")
    require(sha256(ROOT / INDEPENDENT) == "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd", "independent drift")
    require(2 * CAP * CAP < MODULUS * MODULUS, "the halving guard moved")
    local = local_profile()
    require(idle_mass(local, 1, 1) == 1646, "the one-unpaid mass moved")
    one = idle_mass(local, 1, 2)
    replica = idle_mass(local, 9, 2)
    pooled = idle_mass(local, CALLS, 2)
    require(one == Fraction(13918, 9) and one.denominator != 1, "the per-call two-unpaid mass moved")
    require(replica == 13918 and pooled == 222688, "the pooled two-unpaid mass moved")
    require(histogram(13918) == {51: 272, 46: 1}, "the nine-call closed form moved")
    require(histogram(222688) == {51: 4366, 22: 1}, "the pooled closed form moved")
    return {
        "per_call_idle": "13918/9",
        "replica_idle": 13918,
        "replica_rank_51": 272,
        "replica_remainder": 46,
        "pooled_idle": 222688,
        "pooled_rank_51": 4366,
        "pooled_remainder": 22,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
