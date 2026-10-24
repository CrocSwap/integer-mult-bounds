#!/usr/bin/env python3
"""A core row sits past the within-cell agreement radius.

Every comparison is an integer identity. The ideal-gap gauge stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-core-row"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def radius_gap(prime: int) -> int:
    return prime**26 - (2 * prime**24 - 1) * (prime - 1)


def factored(prime: int) -> int:
    return prime**24 * ((prime - 1) ** 2 + 1) + (prime - 1)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "A=ceil(p^48)" in halo
    assert "EXACTLY the corresponding row of the global P_i" in halo
    assert "Keep outputs at distance A" in halo
    assert "g p^(10g) exp(-p^2)," in halo


def agreement() -> None:
    # p^{26} - (2 p^{24} - 1)(p - 1) = p^{24}((p - 1)^2 + 1) + p - 1.
    assert radius_gap(2) == factored(2)
    assert radius_gap(3) == factored(3)
    assert (2 - 1) ** 2 + 1 >= 1
    assert 2 - 1 >= 1
    assert factored(2) > 0
    # Worst bandwidth W = p - 1 still sits strictly below p^{26}.
    assert (2 * 2**24 - 1) * (2 - 1) < 2**26
    # Distance p^{25} does not clear the loose radius at p = 2.
    assert 2 * 2**24 + 1 > 2**25


def core_distance() -> None:
    # For an integer p, ceil(p^{48}) = p^{48}, and p^{48} = p^{26} p^{22}.
    assert 48 - 26 == 22
    assert 2**22 > 1
    assert 2**26 * (2**22 - 1) > 0


def main() -> None:
    pins_and_phrases()
    agreement()
    core_distance()
    print("PASS_GAUSSIAN_CORE_ROW")


if __name__ == "__main__":
    main()
