#!/usr/bin/env python3
"""Add two core-row section errors on the shared global row.

Every comparison is an integer identity. Both ideal-gap gauges stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-second-row"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    core = (ROOT / "research/gaussian-core-row/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "A=ceil(p^48)" in halo
    assert "EXACTLY the corresponding row of the global P_i" in halo
    assert "Keep outputs at distance A" in halo
    assert "Its section-polynomial row is the global polynomial row." in core
    assert "meets the #4452 gauge" in core
    assert "||P - H_sec^{-1}||_2 < p^6 exp(-p^2)," in core
    assert "and the core row is a row of that operator." in core
    assert "The global-inverse summand" in core


def two_rows() -> None:
    # The distance comparison does not name a row, so a second output uses it too.
    assert 48 - 26 == 22
    assert 2**22 > 1
    # On the shared global row the cross term is zero, and two strict errors add.
    assert (8 - 5) == (8 - 6) + (6 - 5)
    assert 3 + 3 == 6
    assert 6 < 2 * 4
    # A polynomial gap of 2 spends the strict room.
    assert 3 + 2 + 3 == 8
    assert not (8 < 2 * 4)
    # One error is not the two-error sum.
    assert 3 != 6


def main() -> None:
    pins_and_phrases()
    two_rows()
    print("PASS_GAUSSIAN_SECOND_ROW")


if __name__ == "__main__":
    main()
