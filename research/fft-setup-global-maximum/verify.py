#!/usr/bin/env python3
"""Exact finite component and boundary checks for the all-width setup proof."""

import hashlib
import json
import platform
from fractions import Fraction
from pathlib import Path

MAX_BITS = 4096
PREFIX_STOP = 513
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def geometry(width: int) -> tuple[int, int, int, int, int]:
    """The executable oracle is bounded; the written theorem is all-width."""
    if type(width) is not int or not 3 <= width <= 1 << MAX_BITS:
        raise ValueError("width must be an integer in [3, 2^4096]")
    beta = (width - 1).bit_length()
    quotient = (width + beta - 1) // beta
    ell = (2 * quotient - 1).bit_length()
    ring = 1 << ell
    return beta, quotient, ell, ring, 2 * beta + ell


def setup_sum(ell: int, ring: int, precision: int) -> int:
    return ring * (ell + 1) * precision**2 + (ring + 1) * precision**3


def reference(width: int) -> tuple[int, int, int, int, int]:
    """Independent bounded doubling and quotient/remainder construction."""
    if type(width) is not int or not 3 <= width <= 1 << MAX_BITS:
        raise ValueError("reference width outside bounded domain")
    power = 1
    beta = 0
    for exponent in range(MAX_BITS + 1):
        if power >= width:
            beta = exponent
            break
        power *= 2
    require(beta >= 2, "reference beta not found")
    quotient, remainder = divmod(width, beta)
    quotient += int(remainder != 0)
    ring = 1
    ell = 0
    for exponent in range(MAX_BITS + 2):
        if ring >= 2 * quotient:
            ell = exponent
            break
        ring *= 2
    require(ring >= 2 * quotient, "reference ring not found")
    return beta, quotient, ell, ring, 2 * beta + ell


def finite_prefix() -> dict[str, object]:
    maximum = Fraction(0)
    winners = []
    count = 0
    for width in range(3, PREFIX_STOP):
        data = geometry(width)
        require(data == reference(width), "independent prefix geometry differs")
        beta, _, ell, ring, precision = data
        total = setup_sum(ell, ring, precision)
        require(total == ring * precision**2 * (ell + 1 + precision) + precision**3,
                "factored sum differs")
        ratio = Fraction(total, width * beta**2)
        require(ratio <= Fraction(1017, 7), "finite-prefix inequality failed")
        if ratio > maximum:
            maximum, winners = ratio, [width]
        elif ratio == maximum:
            winners.append(width)
        count += 1
    require(maximum == Fraction(1017, 7) and winners == [7], "sharpness failed")
    require(count == 510, "finite-prefix coverage differs")
    return {"widths": count, "maximum": str(maximum), "equality_widths": winners}


def tail_boundaries() -> dict[str, int]:
    """Corroboration of the written induction and exact rational envelope."""
    require(4 * 2**9 >= 19 * 10**2, "tail induction base failed")
    require(2 * 10**2 >= 11**2, "quadratic doubling base failed")
    comparisons = 0
    for beta in range(10, MAX_BITS + 1):
        require(4 * (1 << (beta - 1)) >= 19 * beta**2, "induction probe failed")
        require(2 * beta**2 >= (beta + 1)**2, "inductive step probe failed")
        for width in ((1 << (beta - 1)) + 1, 1 << beta):
            actual_beta, quotient, ell, ring, precision = geometry(width)
            require(actual_beta == beta, "beta boundary differs")
            require(ell <= beta - 1, "ell bound failed")
            require(ring < 4 * quotient, "power-of-two bound failed")
            require(beta * quotient < width + beta, "ceiling bound failed")
            total = setup_sum(ell, ring, precision)
            envelope = ((144 * beta - 36) * width * beta
                        + (171 * beta - 36) * beta**2)
            require(total < envelope < 144 * width * beta**2, "tail chain failed")
            comparisons += 1
    return {"beta_probes": MAX_BITS - 9, "endpoint_widths": comparisons}


def reject_controls() -> dict[str, int]:
    rejections = 0
    for bad in (True, False, 2, 0, -1, 3.0, "7", (1 << MAX_BITS) + 1):
        try:
            geometry(bad)
        except ValueError:
            rejections += 1
        else:
            raise ValueError("invalid width accepted")
    require(Fraction(1017, 7) > 145, "smaller constant control missed width 7")
    beta, quotient, ell, ring, precision = geometry(7)
    require((beta, quotient, ell, ring, precision) == (3, 3, 3, 8, 9),
            "attaining geometry differs")
    require(setup_sum(ell, ring, precision) == 9153, "attaining sum differs")
    # Each mutant must disagree with the independent literal recipe somewhere.
    caught = set()
    for width in range(3, PREFIX_STOP):
        beta, _, ell, ring, precision = reference(width)
        expected = setup_sum(ell, ring, precision)
        mutants = (
            ring * (ell + 1) * precision**2 + ring * precision**3,
            setup_sum(ell, ring // 2, precision),
            setup_sum(ell, ring, 2 * beta + ell - 1),
        )
        for index, value in enumerate(mutants):
            if value != expected:
                caught.add(index)
    require(caught == {0, 1, 2}, "a mathematical omission control escaped")
    return {"invalid_widths_rejected": rejections, "formula_mutants_rejected": len(caught),
            "smaller_constant_rejected": 1}


def main() -> None:
    prefix = finite_prefix()
    tail = tail_boundaries()
    controls = reject_controls()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "missing or linked package file")
        require(path.stat().st_size <= 1 << 20, "package file exceeds receipt bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_FFT_SETUP_GLOBAL_MAXIMUM", "claim_type": "scoped proof",
                      "python": platform.python_version(), "prefix": prefix, "tail": tail,
                      "controls": controls, "sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
