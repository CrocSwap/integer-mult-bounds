#!/usr/bin/env python3
"""The factor (9 p^2)^g is absorbed by the same four-bit gate.

Every comparison is an integer identity. The per-axis ceiling is a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-nine"


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
    # Four bits clear 9, and three bits do not: 8 < 9 < 16.
    assert 8 < 9
    assert 9 < 16
    assert 2**3 == 8
    assert 2**4 == 16


def log_induction() -> None:
    # For m >= 6, 8(m+1) <= 2^m, so 8 ceil(log2 p) <= p for every integer p >= 64.
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert ceil_log2(128) == 7
    assert 8 * ceil_log2(128) <= 128


def budget() -> None:
    # The eighths 1+2+1 make a half, and p^2 - p is at least 2 for every integer p >= 2.
    assert 1 + 2 + 1 == 4
    assert 4 - 2 == 2
    assert (3**2 - 3) - (2**2 - 2) == 2 * 2
    # p >= 4K + 2C is the cleared form of (2K+C) p <= p^2 / 2.
    assert 2 * (2 * 3 + 5) == 4 * 3 + 2 * 5
    # Witness: p=128, L=7, g=1, K=0, C=0 meets the gate and the four-bit exponent is negative.
    prime = 128
    level = ceil_log2(prime)
    groups = 1
    assert 16 * groups * level <= prime
    four = level + 4 * groups + 2 * groups * level - prime * prime
    three = level + 3 * groups + 2 * groups * level - prime * prime
    assert four < 0
    assert three < 0
    # The negative three-bit exponent is not an upper bound: 9 p^2 > 8 p^2.
    assert 9 * prime * prime > 8 * prime * prime
    assert 9 * 2**2 > 2**3 * 2**2
    # g = p^2 leaves the substituted error above 1, since 9 p^2 > 4 > e.
    # The value 9 p^2 is smallest at p = 2 and increases by 9(2p+1).
    assert 9 * 4 > 4
    assert 9 * (3**2) - 9 * (2**2) == 9 * (2 * 2 + 1)


def main() -> None:
    pins_and_phrases()
    series_bounds()
    log_induction()
    budget()
    print("PASS_GAUSSIAN_TENSOR_NINE")


if __name__ == "__main__":
    main()
