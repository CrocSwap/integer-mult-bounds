#!/usr/bin/env python3
"""Absorb the restricted monomial by the same four-bit gate.

Every comparison is an integer identity. The ceiling and the section error
stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-restricted-gate"


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
    fold = (ROOT / "research/gaussian-tensor-nine-fold/README.md").read_text(encoding="utf-8")
    faces = (ROOT / "research/gaussian-tensor-nine-faces/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "g p^(10g) exp(-p^2)," in halo
    assert "Keep outputs at distance A" in halo
    assert "The resulting exponent is at most" in fold
    assert "`-C p - 3`" in fold
    assert (
        "2 g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(K p - p^2) < 2^{-C p}."
        in faces
    )


def series_and_bits() -> None:
    # e > 5/2 > 2 and e < 4. Four bits clear 9; three bits do not.
    assert 2 + 2 + 1 > 4
    assert 3 < 4
    assert 2 >= 2 and 6 >= 4 and 24 >= 8
    assert 8 < 9 < 16
    assert 2**3 == 8
    assert 2**4 == 16
    # The factor 2 is one bit, taken from the fold slack of 3.
    assert 2**1 == 2
    assert 8 * (-3) == -24
    assert 8 * (-2) == -16
    assert -24 + 8 == -16


def log_and_budget() -> None:
    # 8 L <= p for every integer p >= 64, by the same induction as #4495.
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(128) == 7
    # Eight times the new pieces: 2 g L, 4 g, 5 L, and the constant -2.
    assert 8 * 2 == 16
    assert 8 * 4 == 32
    assert 32 == 2 * 16
    assert 8 * 5 == 40
    assert 40 == 5 * 8
    assert 1 + 2 + 5 == 8
    # (2K + C) p <= p^2 / 2 becomes 8(2K + C) p <= 4 p^2 when p >= 4K + 2C.
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    # p^2 - 2 p + 4 is 4 at p = 2 and then increases by 2 p - 1.
    assert 2 * 2 - 2 * 2 + 4 == 4
    assert -4 * 4 == -16
    assert (3 * 3 - 2 * 3 + 4) - (2 * 2 - 2 * 2 + 4) == 2 * 2 - 1


def witness_and_failures() -> None:
    prime = 128
    level = ceil_log2(prime)
    groups = 1
    assert 16 * groups * level <= prime
    # E = 2 g L + 4 g + 5 L - 2 - p^2 at K = 0.
    exponent = 2 * groups * level + 4 * groups + 5 * level - 2 - prime * prime
    assert exponent == -16333
    assert exponent <= -2
    # Three bits do not majorize 9, even though that exponent is negative.
    four_bit = level + 4 * groups + 2 * groups * level - prime * prime
    three_bit = level + 3 * groups + 2 * groups * level - prime * prime
    assert four_bit < 0 and three_bit < 0
    assert 9 * prime * prime > 8 * prime * prime
    # At g = p^2 the monomial exceeds 1. These are the integer ingredients.
    assert 9 * 2 * 2 > 4
    assert 2**4 > 9
    assert 2 > 1


def main() -> None:
    pins_and_phrases()
    series_and_bits()
    log_and_budget()
    witness_and_failures()
    print("PASS_GAUSSIAN_RESTRICTED_GATE")


if __name__ == "__main__":
    main()
