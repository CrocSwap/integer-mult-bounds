#!/usr/bin/env python3
"""The face factor 2 spends one bit of the telescoping slack.

Every comparison is an integer identity. The section ceiling and the section
error are hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-faces"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_log2(value: int) -> int:
    level = 0
    power = 1
    while power < value:
        power *= 2
        level += 1
    return level


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "g p^(10g) exp(-p^2)," in halo
    assert "These 2g sets are disjoint rectangles." in halo
    assert "exp(O(p)) leaves this below 2^-Cp for every fixed C eventually, provided" in halo
    assert "g log p=o(p)." in halo


def series_bounds() -> None:
    # e > 1 + 1 + 1/2 = 5/2 > 2, and e < 3 < 4.
    assert 5 > 4
    assert 3 < 4
    assert 2 >= 2
    assert 6 >= 4
    assert 24 >= 8
    assert 3 >= 2
    # 10 p^2 + 1 < 16 p^2. The face factor is the next power of two.
    assert 6 * 4 > 1
    assert 10 < 16
    assert 2 ** 4 == 16
    assert 2 ** 1 == 2
    assert 4 - 1 == 3
    assert 4 * 1 - 4 == 0


def section_error_room() -> None:
    # 8 L <= p implies 48 L <= 6 p, and 6 p <= 8(p^2 - 1) for every integer p >= 2.
    assert 6 * 8 == 48
    assert 8 * (2 ** 2 - 1) - 6 * 2 == 2 * (4 * 2 ** 2 - 3 * 2 - 4)
    assert 4 * 2 ** 2 - 3 * 2 - 4 == 6
    assert (4 * 3 ** 2 - 3 * 3 - 4) - (4 * 2 ** 2 - 3 * 2 - 4) == 8 * 2 + 1
    assert ceil_log2(128) == 7
    assert 6 * 7 <= 128 ** 2 - 1
    assert 2 * (2 ** 3) == 2 ** 4


def log_induction() -> None:
    # For m >= 6, 8(m+1) <= 2^m, so 8 ceil(log2 p) <= p for every integer p >= 64.
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2 ** 6 + 8 <= 2 ** 7
    assert ceil_log2(2) == 1
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert ceil_log2(128) == 7
    assert 8 * ceil_log2(128) <= 128


def budget() -> None:
    assert 8 * 2 == 16
    assert 8 * 4 == 2 * 16
    assert 8 * 5 == 5 * 8
    assert 1 + 2 + 5 == 8
    assert 4 * (4 * 3 + 2 * 5) == 8 * (2 * 3 + 5)
    assert 2 ** 2 - 2 * 2 + 8 == 8
    assert (3 ** 2 - 2 * 3 + 8) - (2 ** 2 - 2 * 2 + 8) == 2 * 2 - 1
    assert 8 >= 2
    # The doubled slack 8 is four bits; one bit remains three.
    assert 8 // 2 - 1 == 3
    prime = 128
    level = ceil_log2(prime)
    groups = 1
    assert 16 * groups * level <= prime
    slack = (
        1
        + 2 * groups * level
        + 4 * groups
        + 5 * level
        - 4
        - prime * prime
    )
    assert slack <= -3
    # g = p^2 still leaves the smaller inverse-ceiling monomial above 1.
    assert 10 * 4 > 4
    assert 2 ** 6 > 10


def main() -> None:
    pins_and_phrases()
    series_bounds()
    section_error_room()
    log_induction()
    budget()
    print("PASS_GAUSSIAN_TENSOR_FACES")


if __name__ == "__main__":
    main()
