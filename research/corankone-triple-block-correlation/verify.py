#!/usr/bin/env python3
"""Check the new grouped inequality, using cited probability formulas.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


MAX_DIMENSION = 128
TAIL_START = 42
TRIPLE_TERMS = (
    (27, 1),
    (21, -6),
    (19, 6),
    (17, -6),
    (15, 16),
    (13, -18),
    (11, 9),
    (9, -2),
)
FILES = (
    "PROOF.md",
    "README.md",
    "SOURCES.json",
    "TASK.json",
    "VERIFY.json",
    "verify.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_sums(m):
    require(type(m) is int and 3 <= m <= MAX_DIMENSION, "invalid replay dimension")
    n = m - 1
    pair = 9**n - 2 * 7**n + 5**n
    triple = sum(coefficient * base**n for base, coefficient in TRIPLE_TERMS)
    block = 3**n * pair
    require(pair > 0 and triple >= 0, "cited count outside its probability range")
    require(block == 27**n - 2 * 21**n + 15**n, "pair normalization failed")
    return n, block, triple


def probabilities(m):
    n, block, triple = power_sums(m)
    size = 2**m
    single = Fraction(3**n, (size - 1) * 2**n)
    pair = Fraction(block // 3**n, (size - 1) * (size - 2) * 2 ** (2 * n))
    joint = Fraction(triple, (size - 1) * (size - 2) * (size - 4) * 2 ** (3 * n))
    require(0 <= joint <= pair <= single <= 1, "invalid probability ordering")
    return single, pair, joint


def check_split(single, pair, joint):
    require(joint < pair * single, "strict grouped inequality failed")
    return joint / (pair * single)


def check_dimensions():
    finite = []
    tail_cases = 0
    for m in range(3, MAX_DIMENSION + 1):
        n, block, triple = power_sums(m)
        size = 2**m
        ratio = check_split(*probabilities(m))
        require(
            ratio == Fraction((size - 1) * triple, (size - 4) * block),
            "finite-GL ratio normalization failed",
        )
        gap = (size - 4) * block - (size - 1) * triple
        require(gap > 0, "integer gap is not positive")
        if n < TAIL_START:
            finite.append(
                {"m": m, "integer_gap": gap, "joint_over_pair_single": str(ratio)}
            )
        else:
            x = Fraction(7, 9) ** n
            require(ratio < (1 - 3 * x) * (1 + x) < 1, "tail bound failed")
            tail_cases += 1
    require(len(finite) == 40 and tail_cases == 86, "dimension coverage changed")
    return finite, tail_cases


def check_tail_constants():
    residual = TRIPLE_TERMS[2:]
    require(
        sum(abs(coefficient) for _, coefficient in residual) == 57,
        "spectral remainder bound changed",
    )
    require(max(base for base, _ in residual) == 19, "spectral remainder base changed")
    require(57 * 19**TAIL_START < 21**TAIL_START, "tail cutoff is insufficient")
    require(3 * 7**TAIL_START < 9**TAIL_START, "tail upper bound is not positive")
    require(2 * 9**2 < 14**2, "geometric GL comparison base failed")
    return {
        "n_start": TAIL_START,
        "remainder_weight": 57,
        "remainder_base": 19,
        "cutoff_left": 57 * 19**TAIL_START,
        "cutoff_right": 21**TAIL_START,
    }


def check_controls():
    single, pair, joint = probabilities(4)
    require(
        (single, pair, joint) == (Fraction(9, 40), Fraction(1, 80), Fraction(1, 1680)),
        "cited m=4 fixture changed",
    )
    mutations = (pair * single, joint + Fraction(12 * 21**3, 15 * 14 * 12 * 2**9))
    for mutated_joint in mutations:
        try:
            check_split(single, pair, mutated_joint)
        except ValueError as error:
            require(
                str(error) == "strict grouped inequality failed",
                "wrong mutation rejection",
            )
        else:
            raise ValueError("grouped-independence/sign mutant survived")
    _, block, triple = power_sums(4)
    require(
        joint / (pair * single) != Fraction(triple, block),
        "missing finite-GL correction went undetected",
    )
    for invalid in (2, MAX_DIMENSION + 1, 3.0, True):
        try:
            power_sums(invalid)
        except ValueError as error:
            require(str(error) == "invalid replay dimension", "wrong domain rejection")
        else:
            raise ValueError("invalid replay dimension accepted")
    require(
        check_split(single, pair, joint) == Fraction(40, 189),
        "split ratio fixture changed",
    )
    return [
        "grouped independence",
        "leading-mode sign",
        "finite-GL correction",
        "dimension below domain",
        "dimension above bound",
        "noninteger dimension",
        "boolean dimension",
    ]


def main():
    tail = check_tail_constants()
    finite, tail_cases = check_dimensions()
    controls = check_controls()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = package / name
        require(
            path.stat().st_size <= 1024 * 1024, "package file exceeds receipt bound"
        )
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "status": "PASS_CORANKONE_TRIPLE_BLOCK_CORRELATION",
                "finite_proof_cases": finite,
                "tail_corroboration_cases": tail_cases,
                "tail_constants": tail,
                "controls": controls,
                "sha256": hashes,
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
