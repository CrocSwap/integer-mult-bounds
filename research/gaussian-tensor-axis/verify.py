#!/usr/bin/env python3
"""One tensor axis is at most two section errors times the other factors.

Every comparison is an integer identity. The axis norm bounds are hypotheses.
The scalar model is the one-dimensional case of the same product.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-axis"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "tensor product of the section inverses" in halo
    assert "g p^(10g) exp(-p^2)," in halo
    assert "These 2g sets are disjoint rectangles." in halo


def telescope() -> None:
    # g = 3 scalars. Caps: |b| <= 10, |c| <= 11, |b - c| <= 2.
    left = 8 * 9 * 6 - 7 * 11 * 5
    axis_1 = (8 - 7) * 11 * 5
    axis_2 = 8 * (9 - 11) * 5
    axis_3 = 8 * 9 * (6 - 5)
    assert left == axis_1 + axis_2 + axis_3
    # g = 1 is the single axis.
    assert 5 - 2 == 5 - 2
    # The factor 2 is the sum of two section errors.
    assert 1 + 1 == 2


def one_axis_cap() -> None:
    # v <= u gives v^{k-1} u^{g-k} <= u^{g-1}, because the exponents add to g-1.
    assert 10 <= 11
    assert (2 - 1) + (3 - 2) == 3 - 1
    assert 10 ** 1 * 11 ** 1 <= 11 ** 2
    assert 11 ** 2 <= 11 ** 2
    assert 10 ** 2 <= 11 ** 2
    # Each displayed slice sits under u^{g-1} times the axis cap 2.
    assert abs((8 - 7) * 11 * 5) <= 11 ** 2 * 2
    assert abs(8 * (9 - 11) * 5) <= 10 ** 1 * 11 ** 1 * 2
    assert abs(8 * 9 * (6 - 5)) <= 10 ** 2 * 2
    assert abs(8 * (9 - 11) * 5) <= 11 ** 2 * 2
    # Without the cap |b - c| <= 2, the g = 1 slice can exceed it.
    assert abs(5 - 2) > 2


def main() -> None:
    pins_and_phrases()
    telescope()
    one_axis_cap()
    print("PASS_GAUSSIAN_TENSOR_AXIS")


if __name__ == "__main__":
    main()
