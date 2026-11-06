#!/usr/bin/env python3
"""Exact optimization of a cited dyadic cut formula. Apache-2.0."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path


MAX_HEIGHT = 4096
PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_height(height: int) -> None:
    require(type(height) is int and 2 <= height <= MAX_HEIGHT, "height outside 2..4096")


def mass(height: int, k: int) -> int:
    """PR6784 equation (12), taken as the mathematical input."""
    validate_height(height)
    require(type(k) is int and 0 <= k <= height - 2, "invalid family index")
    m = height - k - 1
    numerator = (
        (48 * 4**m - 4) * 4**k
        + (-36 * 4**m - 24 * 2**m + 12 * 3**m + 3) * 3**k
        + 24 * 2 ** (m + k) - 5
    )
    quotient, remainder = divmod(numerator, 6)
    require(remainder == 0 and quotient > 0, "nonintegral or nonpositive family mass")
    return quotient


def deficit(height: int, k: int) -> int:
    return 2 * 4**height - mass(height, k)


def difference_sign(height: int, k: int) -> int:
    validate_height(height)
    require(type(k) is int and 0 <= k <= height - 3, "invalid adjacent index")
    t = 2 ** (height - k)
    return 16 * 4**k - 3**k * (3 * t * t - 8 * t + 8)


def optimum(height: int) -> int:
    """Find the first positive adjacent difference, with the right endpoint sentinel."""
    validate_height(height)
    low, high = 0, height - 2
    for _ in range(height.bit_length()):
        if low == high:
            return low
        middle = (low + high) // 2
        if difference_sign(height, middle) > 0:
            high = middle
        else:
            low = middle + 1
    require(low == high, "bisection exhausted its bound")
    return low


def balanced_index(height: int) -> int:
    """Exactly floor(alpha*height), alpha=log(4)/log(16/3); no logarithms."""
    validate_height(height)
    low, high = 0, height
    for _ in range((height + 1).bit_length()):
        if low == high:
            return low
        middle = (low + high + 1) // 2
        if 16**middle <= 4**height * 3**middle:
            low = middle
        else:
            high = middle - 1
    require(low == high, "balance bisection exhausted its bound")
    return low


def check_height(height: int) -> tuple[int, int]:
    values = tuple(deficit(height, k) for k in range(height - 1))
    chosen = optimum(height)
    require(values.count(min(values)) == 1, "nonunique optimum")
    require(chosen == values.index(min(values)), "bisection missed exhaustive optimum")
    previous_normalized = None
    for k in range(height - 2):
        sign = difference_sign(height, k)
        require(sign == 8 * (values[k + 1] - values[k]), "adjacent identity failed")
        require(sign != 0, "unexpected adjacent tie")
        normalized = Fraction(sign, 3**k)
        if previous_normalized is not None:
            require(normalized > previous_normalized, "normalized signs not increasing")
        previous_normalized = normalized
    return len(values), max(0, height - 2)


def check_rate(height: int) -> None:
    chosen = optimum(height)
    d = deficit(height, chosen)
    k = balanced_index(height)
    require(16**k <= 4**height * 3**k, "bad balance lower bracket")
    require(16 ** (k + 1) > 4**height * 3 ** (k + 1), "bad balance upper bracket")
    # Both intervals contain lambda**height by the definition of alpha.
    a = 4**k
    q = Fraction(4**height * 3**k, 4**k)
    lower = max(Fraction(a), 3 * q / 4)
    upper = min(Fraction(4 * a), q)
    require(lower <= upper, "empty rational rate enclosure")
    require(6 * d >= upper, "lower deficit rate bound failed")
    require(d <= 6 * lower, "upper deficit rate bound failed")
    if height >= 12:
        require(k <= height - 2, "balanced index outside family")
        require(deficit(height, k) <= 6 * lower, "constructive rate choice failed")


def check_rejections() -> int:
    bad_heights = (None, True, 1, -1, 4097, "11")
    count = 0
    for bad in bad_heights:
        try:
            optimum(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid height accepted")
    for bad in (-1, 10, True, "8"):
        try:
            mass(11, bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid index accepted")
    return count


def check_controls() -> int:
    # These wrong decisions must violate the independently enumerated objective.
    reference = tuple(deficit(11, k) for k in range(10))
    chosen = optimum(11)
    require(chosen == 8 and mass(11, chosen) == 7735559, "new finite witness failed")
    for wrong in (0, 7, 9):
        require(reference[wrong] > reference[chosen], "wrong optimizer control survived")
    sign = difference_sign(11, chosen)
    actual = 8 * (reference[chosen + 1] - reference[chosen])
    require(-sign != actual, "reversed sign control survived")
    require(sign + 8 * 3**chosen != actual, "omitted constant control survived")
    return 5


def check_sources() -> dict[str, str]:
    record = json.loads((PACKAGE / "PREDECESSOR.json").read_text())
    require(record["commit"] == "c134aa6edc8ed6444bbf7bfcabbed8124ff26c39", "changed source head")
    require(record["author"] == "CubeJerry", "changed source attribution")
    raw = (PACKAGE / "predecessor-proof.md").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == record["sha256"], "retained predecessor bytes changed")
    names = (
        "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
        "PREDECESSOR.json", "predecessor-proof.md", "verify.py",
    )
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    hashes = check_sources()
    candidates = adjacent = heights = rate_brackets = 0
    for height in range(2, 257):
        n, d = check_height(height)
        candidates += n
        adjacent += d
        heights += 1
    for height in range(2, 513):
        check_rate(height)
        rate_brackets += 1
    for height in (1024, 2048, 4096):
        check_rate(height)
        rate_brackets += 1
        k = optimum(height)
        require(k == 0 or difference_sign(height, k - 1) < 0, "left optimality failed")
        require(k == height - 2 or difference_sign(height, k) > 0, "right optimality failed")
    require(3**5 < 4**4, "alpha<5/6 proof ingredient failed")
    for height in range(2, 12):
        require(deficit(height, optimum(height)) <= 6 * 3**height, "small-height bound failed")
    receipt = {
        "result": "PASS_DYADIC_CUT_FAMILY_OPTIMUM",
        "claim_type": "scoped proof with finite arithmetic corroboration",
        "exhaustive_heights": heights,
        "family_candidates": candidates,
        "adjacent_identities": adjacent,
        "rate_brackets": rate_brackets,
        "input_rejections": check_rejections(),
        "semantic_controls": check_controls(),
        "witness": {"height": 11, "k": 8, "m": 2, "mass": mass(11, 8)},
        "sha256": hashes,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
