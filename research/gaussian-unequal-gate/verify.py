#!/usr/bin/env python3
"""Absorb one p^6 section error and one p^10 global tail.

Every comparison is an integer identity. Both tails stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-unequal-gate"


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
    cell = (ROOT / "research/gaussian-delta-exponents/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "g (9 p^2)^{g-1} p^6 exp(K p - p^2) < 2^{-C p}." in fold
    assert "`-C p - 3`" in fold
    assert "||P - A^{-1}||_2 < p^6 exp(-p^2)" in cell


def factor() -> None:
    # p^6 + p^{10} = p^6 (1 + p^4). At p = 2 this is 64 + 1024.
    assert 2**6 + 2**10 == 2**6 * (1 + 2**4)
    assert 1 + 2**4 == 17
    # 4 L does not majorize 1 + p^4 at p = 2. One extra bit does.
    assert 1 + 2**4 > 2**4
    assert 1 + 2**4 < 2 * 2**4
    assert 2 * 2**4 == 2 ** (4 * 1 + 1)
    assert 1 < 2**4
    # Four bits still clear 9, and three bits do not.
    assert 8 < 9 < 16
    assert 2**3 == 8 and 2**4 == 16


def budget() -> None:
    # 8 L <= p for p >= 64, and the new linear piece is 9 L.
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(128) == 7
    assert 8 * 2 == 16
    assert 8 * 4 == 32
    assert 32 == 2 * 16
    assert 8 * 9 == 72
    assert 72 == 9 * 8
    assert 1 + 2 + 9 == 12
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    assert 8 * (-2) == -16
    # p^2 - 3 p + 4 equals 2 at p = 2 and then increases by 2 p - 2.
    assert 2 * 2 - 3 * 2 + 4 == 2
    assert -4 * 2 == -8
    assert (3 * 3 - 3 * 3 + 4) - (2 * 2 - 3 * 2 + 4) == 2 * 2 - 2


def witness_and_failure() -> None:
    prime = 128
    level = ceil_log2(prime)
    groups = 1
    assert 16 * groups * level <= prime
    # E = 2 g L + 4 g + 9 L - 2 - p^2 at K = 0.
    exponent = 2 * groups * level + 4 * groups + 9 * level - 2 - prime * prime
    assert exponent == -16305
    assert exponent <= -1
    # At g = p^2 the monomial exceeds 1. These are the integer ingredients.
    assert 9 * 2 * 2 > 4
    assert 2**4 > 9
    assert 1 + 2**4 > 1


def main() -> None:
    pins_and_phrases()
    factor()
    budget()
    witness_and_failure()
    print("PASS_GAUSSIAN_UNEQUAL_GATE")


if __name__ == "__main__":
    main()
