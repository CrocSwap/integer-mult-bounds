#!/usr/bin/env python3
"""Separate HALO's written global tail from the within-cell p^6 bound.

Every comparison is an integer identity. The ideal-gap gauge stays a hypothesis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-global-tail"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    audit = (ROOT / "research/halo-locality-witness-audit/README.md").read_text(encoding="utf-8")
    cell = (ROOT / "research/gaussian-delta-exponents/README.md").read_text(encoding="utf-8")
    conditional = (ROOT / "research/gaussian-halo-exponents/README.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "P - H^-1 = -Q^J H^-1." in audit
    assert "(1-p^-40)^J p^10 <= exp(-J p^-40) p^10 <= p^10 exp(-p^2)." in audit
    assert "||P - A^{-1}||_2 < p^6 exp(-p^2)" in cell
    assert "does not move the global reference." in cell
    assert "||P - H^-1||_2 < p^6 exp(-p^2)," in conditional
    assert "It does not prove `||H^-1||_2 <= 16 p^2` for the rounded reference." in conditional


def tail_gap() -> None:
    # J = p^{42} against p^{-40} fills exactly the exp(-p^2) slot.
    assert 42 - 40 == 2
    # The written inverse factor is larger than p^6 by p^4.
    assert 10 - 6 == 4
    assert 2 != 4
    assert 2**4 == 16
    assert 16 > 1
    assert 2**10 == 2**6 * 2**4
    # At p = 2 the conditional ceiling 16 p^2 equals p^6. It is smaller later.
    assert 16 * 2**2 == 2**6
    assert 16 * 3**2 < 3**6


def main() -> None:
    pins_and_phrases()
    tail_gap()
    print("PASS_GAUSSIAN_GLOBAL_TAIL")


if __name__ == "__main__":
    main()
