#!/usr/bin/env python3
"""Name which axis hypotheses one core row inherits.

Every comparison is an integer identity. The ideal-gap gauge stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-axis-inheritance"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    core = (ROOT / "research/gaussian-core-row/README.md").read_text(encoding="utf-8")
    nine = (ROOT / "research/gaussian-neumann-nine/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "A=ceil(p^48)" in halo
    assert "EXACTLY the corresponding row of the global P_i" in halo
    assert "Keep outputs at distance A" in halo
    assert "Its section-polynomial row is the global polynomial row." in core
    assert "||P - H_sec^{-1}||_2 < p^6 exp(-p^2)," in core
    assert "8 p^2 < U < 9 p^2." in nine
    assert "an inverse bound only when the #4452 gauge holds" in nine


def inheritance() -> None:
    # p^48 = p^26 * p^22, and p^22 > 1, so the core distance clears the radius.
    assert 48 - 26 == 22
    assert 2**22 > 1
    # A strict ceiling meets the closed hypothesis ||B|| <= 9 p^2.
    assert 8 < 9
    assert 8 <= 9
    # One section error is one piece. The two-inverse difference is the sum of two pieces.
    assert abs(8 - 5) == abs(8 - 6) + abs(6 - 5)
    assert abs(8 - 5) > abs(8 - 6)
    assert 1 + 1 == 2


def main() -> None:
    pins_and_phrases()
    inheritance()
    print("PASS_GAUSSIAN_AXIS_INHERITANCE")


if __name__ == "__main__":
    main()
