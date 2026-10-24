#!/usr/bin/env python3
"""Absorb one heavy slice by the factor-7 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-seven-gate"


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


def sevenths() -> None:
    # Seven times the eighths is 56 (E + C p). The gate enters as 80 * 7 g L.
    assert 80 * 7 == 560
    assert 7 * 8 == 56
    assert 7 * 4 == 28
    assert 56 * (2 * 3 + 5) == 28 * (4 * 3 + 2 * 5)
    # 28 p^2 - 80 p - 112 is positive at p = 64 and increases by 56 p - 52.
    assert 28 * 64 * 64 - 80 * 64 - 112 == 109456
    assert 109456 > 0
    assert (28 * 65 * 65 - 80 * 65 - 112) - 109456 == 56 * 64 - 52
    # Dropping the 1 in 1 + p^4 leaves p^{10 g}.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 < 2 * 2**4


def separates_eight() -> None:
    # p = 98, g = 2 meets factor 7 and misses factor 8.
    assert ceil_log2(98) == 7
    assert 7 * 2 * 7 <= 98
    assert 8 * 2 * 7 > 98
    # The factor-8 line 80 g L <= 10 p fails at this point.
    assert 80 * 2 * 7 > 10 * 98
    one = 10 * 2 * 7 + 1 - 98 * 98
    assert one == -9463
    assert one <= -1


def outside() -> None:
    # At p = 2 and g = 1 the factor-7 hypothesis fails, and the slice exceeds 1.
    assert ceil_log2(2) == 1
    assert 7 * 1 * 1 > 2
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 81 < 1088


def main() -> None:
    pins_and_phrases()
    sevenths()
    separates_eight()
    outside()
    print("PASS_GAUSSIAN_SLICE_SEVEN_GATE")


if __name__ == "__main__":
    main()
