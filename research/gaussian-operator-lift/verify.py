#!/usr/bin/env python3
"""Separate a shared-row sum from the operator 2-norm.

Every comparison is an integer identity. The ideal-gap gauges stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-operator-lift"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    core = (ROOT / "research/gaussian-core-row/README.md").read_text(encoding="utf-8")
    bridge = (ROOT / "research/gaussian-tensor-bridge/README.md").read_text(encoding="utf-8")
    audit = (ROOT / "research/halo-locality-witness-audit/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "For any row at distance A=ceil(p^48) from a section" in halo
    assert "EXACTLY the corresponding row of the global P_i" in halo
    assert "||P - H_sec^{-1}||_2 < p^6 exp(-p^2)," in core
    assert "and the core row is a row of that operator." in core
    assert "meets `||B - C|| < 2 ε` once both are within `ε` of the" in bridge
    assert "distance exactly (2J-1)W differs" in audit
    assert "||H_sec^-1-P_sec|| + ||P-H^-1|| <= 2p^10 exp(-p^2)." in audit


def apply_row(matrix: tuple[tuple[int, int], tuple[int, int]], vector: tuple[int, int]) -> tuple[int, int]:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def squared_length(vector: tuple[int, int]) -> int:
    return vector[0] * vector[0] + vector[1] * vector[1]


def operator_gap() -> None:
    # The first row is strictly below the two-error cap. The operator is not.
    small_row = ((3, 0), (0, 9))
    assert squared_length(small_row[0]) == 3 * 3
    assert 3 * 3 < 8 * 8
    image = apply_row(small_row, (0, 1))
    assert image == (0, 9)
    assert squared_length(image) == 9 * 9
    assert 9 * 9 > 8 * 8
    # A zero row does not force the operator difference to vanish.
    zero_row = ((0, 0), (0, 2))
    assert squared_length(zero_row[0]) == 0
    assert squared_length(apply_row(zero_row, (0, 1))) == 2 * 2
    assert 2 * 2 > 0
    # An upper bound that meets twice the cap is not a strict operator bound.
    assert 3 + 2 + 3 == 8
    assert not (8 < 2 * 4)


def main() -> None:
    pins_and_phrases()
    operator_gap()
    print("PASS_GAUSSIAN_OPERATOR_LIFT")


if __name__ == "__main__":
    main()
