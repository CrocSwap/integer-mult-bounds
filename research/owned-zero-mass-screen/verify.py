#!/usr/bin/env python3
"""Forward-mass screen of the nine-stage owned-zero invoice.

The checker applies the pinned idle rules. It does not replay the word.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_OWNED_ZERO_MASS_SCREEN mass=8658/5 no_new_kappa"
RECIPE = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py"
CONFIG = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/config.py"
PORTS = "research/e8-bit-p111-tuned/README.md"
HALF = 4


def fail(message):
    raise SystemExit("FAIL_OWNED_ZERO_MASS_SCREEN " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def calls(half):
    forward = 1
    reverse = 0
    for _pair in range(half):
        reverse += 1
        forward += 1
    return forward, reverse


def idle_histogram(ports, replicas, half):
    histogram = Counter()
    block = 2 * ports * replicas
    for stage in range(2 * half + 1):
        if stage % 2 == 1 and stage <= 2 * half - 3:
            histogram[7 * (stage + 1)] += block
        elif stage % 2 == 0 and 2 <= stage <= 2 * half - 2:
            histogram[7] += block
        elif stage == 2 * half:
            for pair in range(half):
                rank = 7 * (2 * half - (2 * pair + 2))
                if rank:
                    histogram[rank] += block
    return histogram


def evaluate():
    require(sha256(ROOT / RECIPE) == "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8", "recipe drift")
    require(sha256(ROOT / CONFIG) == "283d7fad45155ee91e704d63ec947cf4a60aeff5cc43510bc0e835f7da7d8767", "replica config drift")
    require(sha256(ROOT / PORTS) == "a054ce8453e2936d45c4edd1c3678993903fcf6705ac241b9f1a4c4f9accda2d", "port note drift")
    recipe = (ROOT / RECIPE).read_text(encoding="utf-8")
    for clause in (
        "M=1+7*L",
        "DATA=2*K*V*T",
        "rank=7*(s+1)",
        "rank=7,source_level=s-1",
        "rank=7*(2*K-oldlevel)",
        "paid[e['rank']]+=2*V*T",
        "reverse=True",
        "reverse=False",
    ):
        require(clause in recipe, "a schedule clause moved")
    require("REPLICAS = 32" in (ROOT / CONFIG).read_text(encoding="utf-8"), "the replica count moved")
    require("v = 111 live ports" in (ROOT / PORTS).read_text(encoding="utf-8"), "the live port count moved")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    ports, replicas = 111, 32
    forward, reverse = calls(HALF)
    require((forward, reverse) == (5, 4), "the call split moved")
    histogram = idle_histogram(ports, replicas, HALF)
    idle_mass = sum(rank * count for rank, count in histogram.items())
    width = 1 + 7 * (2 * HALF + 1)
    live = 2 * HALF * ports * replicas
    capacity = width * live
    reverse_allowance = reverse * replicas * 14 * ports
    room = capacity - idle_mass - reverse_allowance
    unit = Fraction(room, forward * replicas)
    require(unit == Fraction(8658, 5), "the unit forward mass moved")
    require(forward * replicas * unit + reverse_allowance + idle_mass == capacity, "the unit bill moved")
    return {
        "ports": ports,
        "replicas": replicas,
        "forward_calls": forward,
        "reverse_calls": reverse,
        "width": width,
        "live": live,
        "capacity": capacity,
        "idle_histogram": {str(rank): histogram[rank] for rank in sorted(histogram)},
        "idle_mass": idle_mass,
        "reverse_allowance": reverse_allowance,
        "unit_bill_forward_mass": "8658/5",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
