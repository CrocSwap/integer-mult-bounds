#!/usr/bin/env python3
"""Absorb one heavy slice by the factor-3 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-three-gate"


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


def thirds() -> None:
    # Three times the eighths is 24 (E + C p). The gate enters as 80 * 3 g L.
    assert 80 * 3 == 240
    assert 3 * 8 == 24
    assert 3 * 4 == 12
    assert 24 * (2 * 3 + 5) == 12 * (4 * 3 + 2 * 5)
    # 12 p^2 - 80 p - 48 is positive at p = 64 and increases by 24 p - 68.
    assert 12 * 64 * 64 - 80 * 64 - 48 == 43984
    assert 43984 > 0
    assert (12 * 65 * 65 - 80 * 65 - 48) - 43984 == 24 * 64 - 68
    # Dropping the 1 in 1 + p^4 leaves p^{10 g}.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 < 2 * 2**4


def separates_four() -> None:
    # p = 84, g = 4 meets factor 3 and misses factor 4.
    assert ceil_log2(84) == 7
    assert 3 * 4 * 7 <= 84
    assert 4 * 4 * 7 > 84
    # The factor-4 line 320 g L <= 80 p fails at this point.
    assert 320 * 4 * 7 > 80 * 84
    one = 10 * 4 * 7 + 1 - 84 * 84
    assert one == -6775
    assert one <= -1


def outside() -> None:
    # At p = 2 and g = 1 the factor-3 hypothesis fails, and the slice exceeds 1.
    assert ceil_log2(2) == 1
    assert 3 * 1 * 1 > 2
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 81 < 1088


def main() -> None:
    pins_and_phrases()
    thirds()
    separates_four()
    outside()
    print("PASS_GAUSSIAN_SLICE_THREE_GATE")


if __name__ == "__main__":
    main()
