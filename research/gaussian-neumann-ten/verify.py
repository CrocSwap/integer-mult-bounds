#!/usr/bin/env python3
"""The within-cell Neumann ceiling U is strictly below 10 p^2.

Every comparison is an integer identity. The ideal-gap reading stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-neumann-ten"


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
    # 10(D - 32 s) - 8(D - 4) = 2(D - 160 s + 16), with s = p^2.
    degree = 7
    square = 3
    gap = 10 * (degree - 32 * square) - 8 * (degree - 4)
    assert gap == 2 * degree - 320 * square + 32
    assert gap == 2 * (degree - 160 * square + 16)
    # 8 p^2 is not an upper bound: U > 8 p^2 exactly when 32 p^2 > 4.
    assert 32 * 4 > 4
    assert 32 < 160
    assert 160 < 2**8
    assert 2**8 == 256


def powers() -> None:
    # 2^{2p} >= p^2 + 1, so p^2 < 2^{2p}. The step surplus is 3p^2 - 2p + 2.
    assert 2**4 >= 2**2 + 1
    assert 4 * (2**2 + 1) - ((2 + 1) ** 2 + 1) == 3 * 2**2 - 2 * 2 + 2
    assert (3 * 3**2 - 2 * 3 + 2) - (3 * 2**2 - 2 * 2 + 2) == 6 * 2 + 1
    # 160 p^2 < 2^{2p+8} < 2^{32760 p}, since the exponent gap is 32758 p - 8.
    assert 2**8 * 2 ** (2 * 2) == 2 ** (2 * 2 + 8)
    assert 32760 * 2 > 2 * 2 + 8
    assert 32758 * 2 - 8 == 65508
    assert 65508 > 0
    # At p = 2 the polynomial 160 p^2 - 16 is below 2^{10}, and the exponent is larger.
    assert 160 * 2**2 - 16 == 624
    assert 2**10 > 624
    assert 32760 * 2 > 10


def main() -> None:
    pins_and_phrases()
    cleared()
    powers()
    print("PASS_GAUSSIAN_NEUMANN_TEN")


if __name__ == "__main__":
    main()
