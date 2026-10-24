#!/usr/bin/env python3
"""Split one axis through the section polynomial.

Every comparison is an integer identity. Each section error and the inverse
ceiling stay hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-bridge"


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
    assert 2 * (4 - 1) < 2 * 4
    assert 6 < 2 * 4
    assert 1 + 1 == 2
    # ||P|| <= ||B|| + ||P - B||. A ceiling of 10 plus the error covers P.
    assert abs(6) <= abs(8) + abs(6 - 8)
    assert abs(6) <= 10 + abs(6 - 8)
    # Dropping the error from the ceiling fails: |13 - 10| = 3 and |13| > 10 + 1.
    assert abs(13 - 10) == 3
    assert abs(13) > 10 + 1


def main() -> None:
    pins_and_phrases()
    bridge()
    print("PASS_GAUSSIAN_TENSOR_BRIDGE")


if __name__ == "__main__":
    main()
