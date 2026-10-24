"""Exact arithmetic accompanying the all-precision Neumann tail proof.

The uniform quantifier is proved in README.md. The finite comparisons below
check its boundary constants, polynomial identity and direct calibration cases.
Normal replay is read-only; --receipt creates a new hash-bound JSON file.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform


PACKAGE = Path(__file__).resolve().parent
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
MAX_PRECISION = 16
MAX_COEFFICIENT = 512


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def tail_below_grid(precision: int, coefficient: int) -> bool:
    """Compare the full scalar tail with one grid unit, using integers."""
    require(1 <= precision <= MAX_PRECISION, "precision outside calibration")
    require(1 <= coefficient <= MAX_COEFFICIENT, "coefficient outside calibration")
    modulus = 16 * precision
    length = coefficient * precision * precision
    left = 32 * precision * (modulus - 1) ** length * 2 ** (16 * precision)
    right = modulus ** length
    return left < right


def proof_constants() -> dict[str, object]:
    # Coefficients are ordered by ascending powers of n. Multiplying the
    # four-term binomial sum by 6(n-1)^2 gives the left polynomial.
    binomial_numerator = (
        6,
        -12 - 6 - 3 - 2,
        6 + 6 + 3 + 1,
    )
    claimed_numerator = (16 - 10, -32 + 9, 16)
    require(binomial_numerator == claimed_numerator, "binomial identity")
    require(9 * 16 - 10 > 0, "positive binomial surplus at n=16")
    require(9 > 0, "binomial surplus increases with n")
    require(3**14 < 2**23, "rho must be strictly less than 1/8")
    require(32 * 2 == 8**2, "geometric induction base")
    require(Fraction(3, 2) < 8, "geometric induction step for p>=2")
    require(226 >= 224 == 14 * 16, "discarded positive truncation power")
    require(2**21 * 15**226 < 16**226, "226 must pass at p=1")
    require(2**21 * 15**225 > 16**225, "225 must fail at p=1")
    return {
        "minimum_integer_coefficient": 226,
        "excluded_coefficient": 225,
        "excluding_precision": 1,
        "binomial_numerator_ascending": list(binomial_numerator),
        "rho": str(Fraction(3**14, 2**26)),
        "rho_upper_bound": "1/8",
        "uniform_claim": "32p(1-1/(16p))^(226p^2) < 2^(-16p), p>=1",
    }


def calibrate() -> dict[str, object]:
    """Compare two arithmetic representations on precisely sixteen cases."""
    checked = []
    for precision in range(1, MAX_PRECISION + 1):
        modulus = 16 * precision
        length = 226 * precision * precision
        rational_tail = 32 * precision * Fraction(modulus - 1, modulus) ** length
        rational_result = rational_tail < Fraction(1, 2 ** (16 * precision))
        integer_result = tail_below_grid(precision, 226)
        require(integer_result and rational_result, "direct tail comparison")
        checked.append(precision)
    require(not tail_below_grid(1, 225), "undersized coefficient control")
    rejected = 0
    for precision, coefficient in ((0, 226), (17, 226), (1, 0), (1, 513)):
        try:
            tail_below_grid(precision, coefficient)
        except ValueError:
            rejected += 1
    require(rejected == 4, "calibration domain rejection controls")
    return {"direct_precisions": checked, "rejected_domain_cases": rejected}


def source_hashes() -> dict[str, str]:
    hashes = {}
    for name in FILES:
        path = PACKAGE / name
        require(path.is_file() and not path.is_symlink(), "regular package file")
        require(path.stat().st_size <= 1024 * 1024, "package file capacity")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="create a new JSON receipt")
    arguments = parser.parse_args()
    result = {
        "status": "PASS_OPTIMAL_NEUMANN_QUADRATIC_TAIL",
        "claim_type": "scoped proof with exact finite corroboration",
        "proof_constants": proof_constants(),
        "calibration": calibrate(),
        "sha256": source_hashes(),
        "python": platform.python_version(),
        "no_new_kappa": True,
    }
    if arguments.receipt is not None:
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with arguments.receipt.open("x", encoding="utf-8") as handle:
            written = handle.write(payload)
            require(written == len(payload), "incomplete receipt write")
    print("PASS_OPTIMAL_NEUMANN_QUADRATIC_TAIL coefficient=226 excluded=225 "
          "direct_precisions=16 domain_controls=4 no_new_kappa")


if __name__ == "__main__":
    main()
