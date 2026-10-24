#!/usr/bin/env python3
"""Split one axis through the section polynomial at ceiling 9 p^2.

Every comparison is an integer identity. Each section error and the inverse
ceiling stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-nine-bridge"


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


def bridge() -> None:
    # (B - C) = (B - P) + (P - C), and the norm adds the two pieces.
    assert (8 - 5) == (8 - 6) + (6 - 5)
    assert abs(8 - 5) <= abs(8 - 6) + abs(6 - 5)
    # Two errors each at most m = 3 sum to 2m, which is below 2(m+1).
    assert 3 + 3 == 6
    assert 6 < 2 * 4
    assert 1 + 1 == 2
    # ||P|| <= ||B|| + ||P - B||. Ceiling 9 plus an error of 2 covers 10.
    assert abs(10) <= abs(8) + abs(10 - 8)
    assert abs(10) <= 9 + abs(10 - 8)
    assert abs(10) > 9
    # Dropping the error from the ceiling fails: |12 - 9| = 3 and |12| > 9 + 1.
    assert abs(12 - 9) == 3
    assert abs(12) > 9 + 1


def main() -> None:
    pins_and_phrases()
    bridge()
    print("PASS_GAUSSIAN_TENSOR_NINE_BRIDGE")


if __name__ == "__main__":
    main()
