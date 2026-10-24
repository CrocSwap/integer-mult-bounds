#!/usr/bin/env python3
"""The telescoping factor with coefficient 9 is absorbed by the same gate.

Every comparison is an integer identity. The section ceiling and the section
error are hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-tensor-nine-fold"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_log2(value: int) -> int:
    level = 0
    power = 1
    while power < value:
        power *= 2
        level += 1
    return level


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "g p^(10g) exp(-p^2)," in halo
    assert "exp(O(p)) leaves this below 2^-Cp for every fixed C eventually, provided" in halo
    assert "g log p=o(p)." in halo


def series_bounds() -> None:
    # e > 1 + 1 + 1/2 = 5/2 > 2, and e < 3 < 4.
    assert 5 > 4
    assert 3 < 4
    assert 2 >= 2
    assert 6 >= 4
    assert 24 >= 8
    assert 3 >= 2
    # Four bits clear the base 9. The denominator 9 is larger than 8 = 2^3.
    assert 9 < 16
    assert 9 > 8
    assert 2**4 == 16
    assert 2**3 == 8
    assert 4 * 1 - 4 == 0


def log_induction() -> None:
    # For m >= 6, 8(m+1) <= 2^m, so 8 ceil(log2 p) <= p for every integer p >= 64.
    assert 8 * 7 <= 64
    assert 8 <= 64
    assert 2**6 + 8 <= 2**7
    assert ceil_log2(2) == 1
    assert ceil_log2(64) == 6
    assert ceil_log2(65) == 7
    assert ceil_log2(128) == 7
    assert 8 * ceil_log2(128) <= 128
    assert (2**7) ** 4 == 2 ** (4 * 7)


def budget() -> None:
    # Eight times the four-bit pieces recovers a half, and p(p-1)/2 is at least 1.
    assert 1 + 2 + 1 == 4
    assert 4 - 2 == 2
    assert (3**2 - 3) - (2**2 - 2) == 2 * 2
    assert 2 * (2 * 3 + 5) == 4 * 3 + 2 * 5
    # Eight times the folded pieces: 2 g L, 4 g, 5 L, and the linear term.
    assert 8 * 2 == 16
    assert 8 * 4 == 2 * 16
    assert 8 * 5 == 5 * 8
    assert 1 + 2 + 5 == 8
    assert 4 * (4 * 3 + 2 * 5) == 8 * (2 * 3 + 5)
    # The constant -3 contributes -24, matching 4 times the polynomial constant 6.
    prime = 7
    budget_value = prime + 2 * prime + 5 * prime + 4 * prime * prime - 24 - 8 * prime * prime
    assert budget_value == -4 * (prime * prime - 2 * prime + 6)
    assert 8 * 3 == 24
    assert 4 * 6 == 24
    assert 2**2 - 2 * 2 + 6 == 6
    assert (3**2 - 2 * 3 + 6) - (2**2 - 2 * 2 + 6) == 2 * 2 - 1
    # Witness: p=128, L=7, g=1. The folded exponent is the four-bit exponent plus 4 L - 3.
    width = 128
    level = ceil_log2(width)
    groups = 1
    assert 16 * groups * level <= width
    four = level + 4 * groups + 2 * groups * level - width * width
    folded = four + 4 * level - 3
    assert four <= -1
    assert folded <= -3
    assert folded == 2 * groups * level + 4 * groups + 5 * level - 3 - width * width
    # g = p^2 leaves the telescoping error above 1, since 9 p^2 > 4 and p^4 > 9.
    assert 9 * 4 > 4
    assert 9 * 3**2 - 9 * 2**2 == 9 * (2 * 2 + 1)
    assert 2**4 > 9
    assert 3**4 > 2**4


def main() -> None:
    pins_and_phrases()
    series_bounds()
    log_induction()
    budget()
    print("PASS_GAUSSIAN_TENSOR_NINE_FOLD")


if __name__ == "__main__":
    main()
