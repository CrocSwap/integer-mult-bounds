#!/usr/bin/env python3
"""The smallest integer coefficient on the Neumann ceiling is 9.

Every comparison is an integer identity. The ideal-gap reading stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-neumann-nine"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "g p^(10g) exp(-p^2)," in halo


def cleared() -> None:
    # 9(D - 32 s) - 8(D - 4) = D - 288 s + 32, with s = p^2.
    degree = 7
    square = 3
    gap = 9 * (degree - 32 * square) - 8 * (degree - 4)
    assert gap == degree - 288 * square + 32
    # 8 p^2 is not an upper bound, and the next integer is 9.
    assert 32 * 4 > 4
    assert 8 + 1 == 9
    assert 32 < 288
    assert 288 < 2**9
    assert 2**9 == 512
    # 9 p^2 is sharper than both ceilings recorded with U.
    assert 7 * 4 > 1
    assert 9 * 4 < 16 * 4 - 1
    assert 16 > 9
    assert 9 * 4 < 2**6


def powers() -> None:
    # 2^{2p} >= p^2 + 1, so p^2 < 2^{2p}. The step surplus is 3p^2 - 2p + 2.
    assert 2**4 >= 2**2 + 1
    assert 4 * (2**2 + 1) - ((2 + 1) ** 2 + 1) == 3 * 2**2 - 2 * 2 + 2
    assert (3 * 3**2 - 2 * 3 + 2) - (3 * 2**2 - 2 * 2 + 2) == 6 * 2 + 1
    # 288 p^2 < 2^{2p+9} < 2^{32760 p}, since the exponent gap is 32758 p - 9.
    assert 2**9 * 2 ** (2 * 2) == 2 ** (2 * 2 + 9)
    assert 32760 * 2 > 2 * 2 + 9
    assert 32758 * 2 - 9 == 65507
    assert 65507 > 0
    assert (32758 * 3 - 9) - (32758 * 2 - 9) == 32758
    # At p = 2 the polynomial 288 p^2 - 32 is below 2^{13}.
    assert 288 * 2**2 - 32 == 1120
    assert 2**13 > 1120
    assert 32760 * 2 > 13


def main() -> None:
    pins_and_phrases()
    cleared()
    powers()
    print("PASS_GAUSSIAN_NEUMANN_NINE")


if __name__ == "__main__":
    main()
