"""Finite corroboration of the new reserve optimization, not a source replay."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

from reserve import (
    check_certificate,
    common_ratio,
    first_cutoff,
    next_prefix,
    parse_menu,
    require,
)

PACKAGE = Path(__file__).resolve().parent
WEIGHT = (F(37), F(20))
RATIO = F(137, 185)
RESERVE = (F(111, 20), F(3))
TOTAL = (F(5), F(3))  # Cited PR6472 total, used only as the tail boundary.


def polynomial(q: F) -> F:
    return 5 * q * q - q - 2


def sharp_ratio_checks(menu) -> dict:
    """Rational brackets and all algebraic reductions used in the proof."""
    lower, upper = F(7403124237, 10**10), F(7403124238, 10**10)
    require(polynomial(lower) < 0 < polynomial(upper), "wrong root bracket")
    require(F(1, 4) < lower < upper < RATIO < F(4, 5), "wrong ratio order")
    count = 0
    for x in range(1, 65):
        for y in range(1, 65):
            q = common_ratio(menu, (F(x), F(y)))
            expected = max(F(6 * y, 5 * x), F(1, 5) + F(y, x),
                           F(2 * x, 5 * y), F(1, 4))
            require(q == expected, "literal row/formula mismatch")
            require(polynomial(q) > 0 and q > upper, "sharp lower bound failed")
            count += 1
    check_certificate(menu, WEIGHT, RATIO)
    require(common_ratio(menu, RESERVE) == RATIO, "reserve scaling changed ratio")
    require(min(RESERVE[i] - TOTAL[i] for i in range(2)) >= 0, "boundary too small")
    require(F(111, 100) * (RATIO / F(4, 5)) ** 2 < 1, "depth-two comparison failed")
    return {"rational_weights": count, "root_bracket": [str(lower), str(upper)]}


def prefix_checks(menu) -> dict:
    """Literal nonlinear row-max recurrence and an independent matrix recurrence."""
    value, matrix_value = (F(0), F(0)), (F(0), F(0))
    old_cutoff = first_cutoff(F(4, 5), F(1), 64)
    cutoff = first_cutoff(RATIO, F(111, 100), 64)
    require((old_cutoff, cutoff) == (199, 149), "wrong exact cutoff")
    for depth in range(257):
        require(value == matrix_value, "literal row choices differ from fixed matrix")
        for i in range(2):
            error = TOTAL[i] - value[i]
            require(0 <= error <= RATIO**depth * RESERVE[i], "new tail bound failed")
        value = next_prefix(menu, value)
        a, b = matrix_value
        matrix_value = (1 + a / 5 + b, 1 + 2 * a / 5)
    for q, c, d in ((F(4, 5), F(1), old_cutoff), (RATIO, F(111, 100), cutoff)):
        require(c * q**d <= F(1, 2**64) < c * q**(d - 1), "nonminimal cutoff")
    return {"prefix_depths": 257, "old_64_bit_cutoff": old_cutoff,
            "new_64_bit_cutoff": cutoff}


def reject_controls(menu, source: bytes) -> int:
    failures = (
        (WEIGHT, F(37, 50)),
        (WEIGHT, F(1851, 2500)),
        ((F(5), F(3)), RATIO),
        ((F(0), F(1)), RATIO),
        ((F(-1), F(1)), RATIO),
        (WEIGHT, F(1)),
        (WEIGHT, F(-1)),
    )
    rejected = 0
    for weight, ratio in failures:
        try:
            check_certificate(menu, weight, ratio)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("false reserve certificate accepted")
    for data in (source + b" ", source.replace(b"6/5", b"5/6")):
        try:
            parse_menu(data)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("source corruption accepted")
    for ratio, prefactor, bits in (
        (RATIO, F(1), 0), (RATIO, F(1), 129), (RATIO, F(1), True),
        (F(0), F(1), 1), (F(1), F(1), 1), (RATIO, F(1, 2), 1),
        (F(9999, 10000), F(1), 128),
    ):
        try:
            first_cutoff(ratio, prefactor, bits)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid or exhausted cutoff request accepted")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write the generated receipt outside the package")
    args = parser.parse_args()
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(PACKAGE), "receipt must be external")
    source = (PACKAGE / "inputs/example6472.json").read_bytes()
    menu = parse_menu(source)
    result = {"marker": "PASS_SHARP_ADAPTIVE_RESERVE", "claim_type": "scoped proof with finite corroboration",
              "optimal_ratio": "(1+sqrt(41))/10", "rational_ratio": str(RATIO),
              "weight": [str(x) for x in WEIGHT]}
    result.update(sharp_ratio_checks(menu))
    result.update(prefix_checks(menu))
    result["rejection_controls"] = reject_controls(menu, source)
    names = ("ORIGIN.json", "PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "reserve.py", "verify.py", "inputs/example6472.json")
    result["sha256"] = {name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
