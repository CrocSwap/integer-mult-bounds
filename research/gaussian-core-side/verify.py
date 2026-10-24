#!/usr/bin/env python3
"""Smallest core-side exponent once the agreement distance is p^26.

Every comparison is an integer identity. The ideal gaps stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-core-side"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    gaussian = (ROOT / "research/unconditional-batched-crt/GAUSSIAN.md").read_text(
        encoding="utf-8"
    )
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "L=2^ceil(400 log2 p)" in halo
    assert "L>4A and gA/L=o(1) for every g<=p" in halo
    assert "g p^(10g) exp(-p^2)" in halo
    assert "O(V [d/g + d g A^3/L + d A p^2/L] polylog p)." in halo
    assert "For A=p^48, L>=p^400" in halo
    assert "two sparse powers are epsilon+beta+144-400 and epsilon+48+2-400, both negative." in halo
    assert "O(V [d/g + d g A^3/L + d A p^2/L] polylog(p))." in gaussian


def powers() -> None:
    # A^3 contributes 3*26 = 78, and the p^2 factor contributes 26+2 = 28.
    assert 3 * 26 == 78
    assert 26 + 2 == 28
    assert 3 * 48 == 144
    assert 48 + 2 == 50
    # The corner ε = β = 1 would make the first power 80 - C. Strictly below 1, C = 80 is negative.
    assert 2 + 78 == 80
    assert 1 + 28 == 29
    assert 29 < 80
    assert 1 + 28 - 80 == -51
    # C = 79 is positive at ε = β = 3/4. Clearing the denominator leaves +2.
    assert 3 + 3 + 4 * 78 - 4 * 79 == 2
    assert 3 + 3 + 4 * 78 - 4 * 80 == -2
    # The second power alone already fails at C = 28 for ε = 1/2.
    assert 1 + 2 * 28 - 2 * 28 == 1
    # The written 400 still has slack 254 at the same corner, and it is larger than 80.
    assert 2 + 144 == 146
    assert 400 - 146 == 254
    assert 400 > 80
    # L >= p^80 also meets L > 4A and gA/L = o(1) for g <= p.
    assert 80 - 26 == 54
    assert 2 ** 10 > 4
    assert 54 > 10
    assert 1 + 26 - 80 < 0
    # A uniform slack of 1 below zero needs 81, because the corner reaches 80 - C.
    assert 80 - 81 == -1


def main() -> None:
    pins_and_phrases()
    powers()
    print("PASS_GAUSSIAN_CORE_SIDE")


if __name__ == "__main__":
    main()
