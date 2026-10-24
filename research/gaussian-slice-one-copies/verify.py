#!/usr/bin/env python3
"""Absorb g copies of the heavy slice by the factor-1 gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
The coefficient-9 monomial gate stays at 16. The gate forces g <= 2^L, not
the stricter g < 2^L.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-slice-one-copies"


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
    # Eighths spend 80 p. Copies replace 8 L by p once 8 L <= p.
    assert 80 * 1 == 80
    assert 1 * 8 == 8
    assert 80 + 1 == 81
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    # g >= 2^L + 1 would make g L exceed p <= 2^L. Equality g = 2^L can hold.
    assert 6 * (2**6 + 1) > 2**6
    assert 1 * (2**1 + 1) > 2**1
    assert 2 == 2**1
    # 8 (m + 1) <= 2^m for m >= 6, and the step preserves a doubling.
    assert 8 * 7 <= 2**6
    assert 8 <= 2**6
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert 8 * 6 <= 64
    assert 8 * 7 <= 65
    # 4 p^2 - 81 p - 16 is positive at p = 64 and increases by 8 p - 77.
    assert 4 * 64 * 64 - 81 * 64 - 16 == 11184
    assert 11184 > 0
    assert (4 * 65 * 65 - 81 * 65 - 16) - 11184 == 8 * 64 - 77
    # Dropping the 1 in 1 + p^4 leaves p^{10 g}.
    assert 10 * (12 - 1) + 6 + 4 == 10 * 12
    assert 1 + 2**4 < 2 * 2**4


def witness() -> None:
    # Twelve axes at p = 84 meet factor 1 and miss factor 2.
    level = ceil_log2(84)
    assert level == 7
    assert 12 * level <= 84
    assert 2 * 12 * level > 84
    assert 12 <= 2**level
    one = 10 * 12 * level + 1 - 84 * 84
    copies = one + level
    assert one == -6215
    assert copies == -6208
    assert copies <= -1


def outside() -> None:
    # At p = 2 and g = 1 the factor holds, but p < 64 and the one copy exceeds 1.
    assert ceil_log2(2) == 1
    assert 1 * 1 <= 2
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
    print("PASS_GAUSSIAN_SLICE_ONE_COPIES")


if __name__ == "__main__":
    main()
