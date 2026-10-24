#!/usr/bin/env python3
"""Absorb one heavy slice by the factor-2 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-two-gate"


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


def halves() -> None:
    # Two times the eighths is 16 (E + C p). The gate enters as 80 * 2 g L.
    assert 80 * 2 == 160
    assert 2 * 8 == 16
    assert 2 * 4 == 8
    assert 16 * (2 * 3 + 5) == 8 * (4 * 3 + 2 * 5)
    # 8 p^2 - 80 p - 32 is positive at p = 64 and increases by 16 p - 72.
    assert 8 * 64 * 64 - 80 * 64 - 32 == 27616
    assert 27616 > 0
    assert (8 * 65 * 65 - 80 * 65 - 32) - 27616 == 16 * 64 - 72
    # Dropping the 1 in 1 + p^4 leaves p^{10 g}.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 < 2 * 2**4


def separates_three() -> None:
    # p = 84, g = 6 meets factor 2 and misses factor 3.
    assert ceil_log2(84) == 7
    assert 2 * 6 * 7 <= 84
    assert 3 * 6 * 7 > 84
    # The factor-3 line 240 g L <= 80 p fails at this point.
    assert 240 * 6 * 7 > 80 * 84
    one = 10 * 6 * 7 + 1 - 84 * 84
    assert one == -6635
    assert one <= -1


def outside() -> None:
    # At p = 2 and g = 1 the factor holds, but p < 64 and the slice exceeds 1.
    assert ceil_log2(2) == 1
    assert 2 * 1 * 1 <= 2
    assert 2 < 64
    total = 5040 + 5040 + 2520 + 840 + 210 + 42 + 7
    assert total == 13699
    assert 3 * 5040 - total == 1421
    assert 8 < 1421 * 7
    assert 3**4 == 81
    assert 2**6 * (1 + 2**4) == 1088
    assert 81 < 1088


def main() -> None:
    pins_and_phrases()
    halves()
    separates_three()
    outside()
    print("PASS_GAUSSIAN_SLICE_TWO_GATE")


if __name__ == "__main__":
    main()
