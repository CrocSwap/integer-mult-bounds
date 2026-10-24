#!/usr/bin/env python3
"""Absorb the heaviest trailing p^10 slice by the same gate.

Every comparison is an integer identity. The inverse bound stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-heavy-slice"


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
    gate = (ROOT / "research/gaussian-tensor-nine/README.md").read_text(encoding="utf-8")
    nine = (ROOT / "research/gaussian-neumann-nine/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "g p^(10g) exp(-p^2)," in halo
    assert "16 g L ≤ p" in gate
    assert "8 p^2 < U < 9 p^2." in nine


def heaviest() -> None:
    # p^{10} = p^8 * p^2, and p^8 > 9, so a trailing factor beats 9 p^2.
    assert 2**8 == 256
    assert 256 > 9
    assert 2**10 > 9 * 2**2
    # p^6 * p^4 * (p^{10})^{g-1} = p^{10 g}. The extra 1 in 1 + p^4 needs one bit.
    assert 10 * (2 - 1) + 6 + 4 == 10 * 2
    assert 1 + 2**4 > 2**4
    assert 1 + 2**4 < 2 * 2**4
    assert 2 * 2**4 == 2 ** (4 + 1)
    # Outside the gate the p=2, g=2 slice already exceeds 1.
    assert 16 * 2 * 1 > 2
    assert 2**10 > 1


def budget() -> None:
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(64) == 6
    assert ceil_log2(128) == 7
    assert ceil_log2(256) == 8
    # 80 g L = 5 * 16 g L, and the constant 1 contributes 8.
    assert 8 * 10 == 80
    assert 80 == 5 * 16
    assert 8 * 1 == 8
    assert 8 * (2 * 3 + 5) == 4 * (4 * 3 + 2 * 5)
    # 4 p^2 - 5 p - 16 is positive at p = 64 and increases by 8 p - 1.
    assert 4 * 64 * 64 - 5 * 64 - 16 == 16048
    assert 16048 > 0
    assert (4 * 65 * 65 - 5 * 65 - 16) - 16048 == 8 * 64 - 1
    # g copies add one L. Then 4 p^2 - 6 p - 16 stays positive.
    assert 4 * 64 * 64 - 6 * 64 - 16 == 15984
    assert 15984 > 0
    assert (4 * 65 * 65 - 6 * 65 - 16) - 15984 == 8 * 64 - 2


def witness() -> None:
    # One trailing-free slice at the legal point p = 128, g = 1.
    level = ceil_log2(128)
    assert 16 * 1 * level <= 128
    one = 10 * 1 * level + 1 - 128 * 128
    assert one == -16313
    assert one <= -1
    # Two axes at p = 256 put one factor p^{10} inside the gate.
    wide = ceil_log2(256)
    assert 16 * 2 * wide <= 256
    two = 10 * 2 * wide + 1 - 256 * 256
    copies = two + wide
    assert two == -65375
    assert copies == two + 8
    assert copies <= -1


def main() -> None:
    pins_and_phrases()
    heaviest()
    budget()
    witness()
    print("PASS_GAUSSIAN_HEAVY_SLICE")


if __name__ == "__main__":
    main()
