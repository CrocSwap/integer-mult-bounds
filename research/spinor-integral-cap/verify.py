#!/usr/bin/env python3
"""Exact finite corroboration of the D16 antipodal integrality improvement."""

import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path


FULL = (1 << 16) - 1
DISTANCES = (0, 2, 6, 8, 10, 14, 16)
DEGREES = (2, 6, 8)
WEIGHTS = (25, 1, 2)
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def krawtchouk(k: int, distance: int) -> int:
    require(0 <= k <= 16 and 0 <= distance <= 16, "Krawtchouk domain")
    return sum(
        (-1) ** j * comb(distance, j) * comb(16 - distance, k - j)
        for j in range(max(0, k - (16 - distance)), min(distance, k) + 1)
    )


def dual_values(weights: tuple[int, int, int]) -> tuple[int, ...]:
    require(len(weights) == 3 and all(w >= 0 for w in weights), "dual weights")
    values = tuple(
        sum(w * krawtchouk(k, d) for k, w in zip(DEGREES, weights, strict=True))
        for d in DISTANCES
    )
    require(values == (36748, -116, -116, -116, -116, -116, 36748), "dual table")
    return values


def weighted_masks() -> tuple[tuple[int, int], ...]:
    weights = dict(zip(DEGREES, WEIGHTS, strict=True))
    masks = tuple((u, weights[u.bit_count()]) for u in range(1 << 16)
                  if u.bit_count() in weights)
    require(len(masks) == 20998, "mask count")
    require(sum(w for _, w in masks) == 36748, "weighted character count")
    for d, expected in zip(DISTANCES, dual_values(WEIGHTS), strict=True):
        x = (1 << d) - 1
        actual = sum(w * (-1 if (u & x).bit_count() % 2 else 1) for u, w in masks)
        require(actual == expected, "literal character/kernel disagreement")
    return masks


def parity_cases() -> int:
    checked = 0
    for pairs in range(1, 318, 2):
        for negative_pairs in range(pairs + 1):
            coefficient = 2 * (pairs - 2 * negative_pairs)
            require(coefficient % 4 == 2 and coefficient**2 >= 4, "odd-pair parity")
            checked += 1
    require(checked == 25440, "parity case count")
    return checked


def cap_certificate() -> dict[str, int]:
    real_cap = Fraction(18432, 29)
    require(real_cap.numerator // real_cap.denominator // 2 == 317, "old pair cap")
    cardinality = 2 * 317
    upper = cardinality * (73728 - 116 * cardinality)
    lower = 4 * sum(w * comb(16, k) for k, w in zip(DEGREES, WEIGHTS, strict=True))
    require((upper, lower, lower - upper) == (116656, 146992, 30336), "gap")
    require(lower > upper, "317-pair contradiction")
    return {"spinor_line_cap": 316, "root_plus_spinor_cap": 556,
            "excluded_code_size": cardinality, "upper": upper, "lower": lower,
            "contradiction_gap": lower - upper}


def validate_fixture(code: tuple[int, ...]) -> None:
    require(0 < len(code) <= 16 and len(set(code)) == len(code), "fixture cardinality")
    require(all(0 <= x <= FULL for x in code), "fixture word width")
    require(all(x ^ FULL in code for x in code), "fixture antipodality")
    require(all((x ^ y).bit_count() in DISTANCES for x in code for y in code),
            "fixture forbidden distance")


def coefficient(code: tuple[int, ...], mask: int) -> int:
    require(len(code) <= 16 and 0 <= mask <= FULL, "character fixture domain")
    return sum(-1 if (x & mask).bit_count() % 2 else 1 for x in code)


def literal_codes(masks: tuple[tuple[int, int], ...]) -> dict[str, int]:
    seeds = (0, 3, 5, 9)
    characters = pairs = odd_characters = 0
    for subset in range(1, 16):
        representatives = tuple(seeds[j] for j in range(4) if subset & (1 << j))
        code = representatives + tuple(x ^ FULL for x in representatives)
        validate_fixture(code)
        total = 0
        for mask, weight in masks:
            value = coefficient(code, mask)
            total += weight * value**2
            characters += 1
            if len(representatives) % 2:
                require(value % 4 == 2 and value**2 >= 4, "literal odd-pair failure")
                odd_characters += 1
        require(total == len(code) * (73728 - 116 * len(code)), "Fourier pair identity")
        pair_total = 0
        for x in code:
            for y in code:
                distance = (x ^ y).bit_count()
                pair_total += 36748 if distance in (0, 16) else -116
                pairs += 1
        require(pair_total == total, "ordered-pair/Fourier disagreement")
    require((characters, pairs, odd_characters) == (314970, 320, 167984), "fixture counts")
    return {"codes": 15, "characters": characters, "ordered_pairs": pairs,
            "odd_pair_characters": odd_characters}


def controls() -> dict[str, int]:
    rejected = 0
    for weights in ((24, 1, 2), (25, 0, 2), (25, 1, 1)):
        try:
            dual_values(weights)
        except ValueError:
            rejected += 1
    bad_codes = ((0, 15, FULL, FULL ^ 15), (0, FULL, 0, FULL),
                 (0, 1 << 16), (0, 3, 5, 9, 17, 33))
    for code in bad_codes:
        try:
            validate_fixture(code)
        except ValueError:
            rejected += 1
    require(rejected == 7, "corrupted dual/invalid code accepted")
    even = (0, 3, 5, 9, FULL, FULL ^ 3, FULL ^ 5, FULL ^ 9)
    validate_fixture(even)
    require(coefficient(even, 6) == 0, "even-pair zero control")
    nonantipodal = (0, 3, 5, 9, 17, 33)
    require(len(nonantipodal) % 4 == 2 and coefficient(nonantipodal, 462) == 0,
            "antipodality necessity control")
    bound = cap_certificate()
    require(bound["upper"] >= 0 and bound["lower"] // 4 < bound["upper"],
            "missing parity/factor control")
    return {"rejections": rejected, "semantic_discriminators": 3}


def source_hashes() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "receipt file type")
        require(path.stat().st_size <= 1 << 20, "receipt file capacity")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    masks = weighted_masks()
    result = {"claim_type": "scoped proof with finite corroboration",
              "bound": cap_certificate(), "parity_cases": parity_cases(),
              "fixtures": literal_codes(masks), "controls": controls(),
              "files_sha256": source_hashes(), "new_kappa": False}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_SPINOR_INTEGRAL_CAP spinor_lines=316 roots_plus_spinors=556 "
          "gap=30336 no_new_kappa")


if __name__ == "__main__":
    main()
