#!/usr/bin/env python3
"""Finite budget of the physical chirp consumer.

The checker evaluates the phase guards and the stated power formula.
It does not run the middle-map consumer.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CHIRP_BUDGET_CLEARANCE rows=7910 online=603/1000 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_CHIRP_BUDGET_CLEARANCE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def phase_rows():
    count = 0
    for precision in range(16, 129):
        for length in range(2, precision):
            width = length + 1
            guard = (width - 1).bit_length() + 4
            scale = precision + guard
            require(16 <= scale <= 2 * precision and width <= scale, "a phase row left its width")
            require(Fraction(4 * width, 1 << guard) <= Fraction(1, 4), "a phase row left its guard")
            count += 1
    return count


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    rows = phase_rows()
    require(rows == 7910, "the phase row count moved")
    require(Fraction(7, 4) ** 2 > 2 and Fraction(7, 4) + Fraction(1, 4) == 2, "the phase error left two ulps")
    require(32 * 1000 ** 2 < 2 ** 26, "the ring margin moved")
    require(Fraction(3, 5) + Fraction(1, 1000) == Fraction(601, 1000), "the norm margin moved")
    require(3 * 4 + 2 + 2 * 4 == 22, "the error bill moved")
    online = Fraction(8, 5) - Fraction(997, 1000)
    fourier = 1 - Fraction(997, 1000) * (1 - Fraction(99827101, 100000000))
    primitive = Fraction(332353, 332929)
    require(online == Fraction(603, 1000), "the online power moved")
    require(fourier == Fraction(99827619697, 100000000000), "the Fourier power moved")
    require(online < fourier and primitive < fourier, "a power left the Fourier allowance")
    return {
        "phase_rows": 7910,
        "error_bill": 22,
        "online_power": "603/1000",
        "fourier_power": "99827619697/100000000000",
        "primitive_power": "332353/332929",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
