#!/usr/bin/env python3
"""Absorb the heavy slice by the factor-10 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-ten-gate"


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
    gate = (ROOT / "research/gaussian-tensor-nine/README.md").read_text(encoding="utf-8")
    nine = (ROOT / "research/gaussian-neumann-nine/README.md").read_text(encoding="utf-8")
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "16 g L ≤ p" in gate
    assert "9 < 16" in gate
    assert "9 > 8" in gate
    assert "8 p^2 < U < 9 p^2." in nine
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo


def factor_ten() -> None:
    # Eight times the exponent turns 10 g L into 8 p.
    assert 8 * 10 == 80
    assert 8 * 1 == 8
    # 8 (2 K + C) = 4 (4 K + 2 C), so p >= 4 K + 2 C pays for the linear term.
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    # 4 p^2 - 8 p - 16 is positive at p = 64 and increases by 8 p - 4.
    assert 4 * 64 * 64 - 8 * 64 - 16 == 15856
    assert 15856 > 0
    assert (4 * 65 * 65 - 8 * 65 - 16) - 15856 == 8 * 64 - 4
    # The slice power is p^{10 g} once the extra 1 is dropped.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 < 2 * 2**4
    assert 2 * 2**4 == 2 ** (4 + 1)


def separates_sixteen() -> None:
    # p = 64, g = 1 meets factor 10 and misses factor 16.
    assert ceil_log2(64) == 6
    assert 10 * 1 * 6 <= 64
    assert 16 * 1 * 6 > 64
    one = 10 * 1 * 6 + 1 - 64 * 64
    assert one == -4035
    assert one <= -1
    # A point already legal for 16 remains legal for 10.
    assert ceil_log2(128) == 7
    assert 16 * 1 * 7 <= 128
    assert 10 * 1 * 7 + 1 - 128 * 128 == -16313


def outside() -> None:
    # At p = 2 and g = 1 the factor-10 hypothesis fails.
    assert ceil_log2(2) == 1
    assert 10 * 1 * 1 > 2
    assert 10 * 1 * 1 + 1 - 2 * 2 == 7
    # e < 3: the partial sum through 1/6! leaves a gap larger than the tail.
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 81 < 1088


def main() -> None:
    pins_and_phrases()
    factor_ten()
    separates_sixteen()
    outside()
    print("PASS_GAUSSIAN_SLICE_TEN_GATE")


if __name__ == "__main__":
    main()
