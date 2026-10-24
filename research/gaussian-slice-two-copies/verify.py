#!/usr/bin/env python3
"""Absorb g copies of the heavy slice by the factor-2 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-two-copies"


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


def budget() -> None:
    # Halves spend 80 p. Copies replace 16 L by 2 p once 8 L <= p.
    assert 80 * 2 == 160
    assert 2 * 8 == 16
    assert 16 == 2 * 8
    assert 80 + 2 == 82
    assert 16 * (2 * 3 + 5) == 8 * (4 * 3 + 2 * 5)
    # 2 L > 1, so the gate forces g < 2^L.
    assert 2 > 1
    # 8 (m + 1) <= 2^m for m >= 6, and the step preserves a doubling.
    assert 8 * 7 <= 2**6
    assert 8 <= 2**6
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert 8 * 6 <= 64
    assert 8 * 7 <= 65
    # 8 p^2 - 82 p - 32 is positive at p = 64 and increases by 16 p - 74.
    assert 8 * 64 * 64 - 82 * 64 - 32 == 27488
    assert 27488 > 0
    assert (8 * 65 * 65 - 82 * 65 - 32) - 27488 == 16 * 64 - 74


def witness() -> None:
    # Six axes at p = 84 meet factor 2 and miss factor 3.
    level = ceil_log2(84)
    assert level == 7
    assert 2 * 6 * level <= 84
    assert 3 * 6 * level > 84
    assert 6 < 2**level
    one = 10 * 6 * level + 1 - 84 * 84
    copies = one + level
    assert one == -6635
    assert copies == -6628
    assert copies <= -1


def outside() -> None:
    # At p = 2 and g = 1 the factor holds, but p < 64 and the one copy exceeds 1.
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
    budget()
    witness()
    outside()
    print("PASS_GAUSSIAN_SLICE_TWO_COPIES")


if __name__ == "__main__":
    main()
