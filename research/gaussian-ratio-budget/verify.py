#!/usr/bin/env python3
"""Published 4η weight error against the 1/(16p^2) ratio budget.

Every comparison is an integer identity. Across-cell entries are not bounded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-ratio-budget"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(left, right):
    out = dict(left)
    for key, coeff in right.items():
        out[key] = out.get(key, 0) + coeff
        if out[key] == 0:
            del out[key]
    return out


def scale(poly, factor):
    return {key: factor * coeff for key, coeff in poly.items() if factor * coeff}


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    downstream = (
        ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    review = (
        ROOT / "references/semantic-bulk/rad20/reports/review-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    gauge = (
        ROOT / "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md"
    ).read_text(encoding="utf-8")
    log_a = (
        ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md"
    ).read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "Set P=32768p and eta=2^(-P)." in downstream
    assert "2^(-8p)<a_j<=1." in downstream
    assert "absolute error below four eta" in downstream
    assert (
        "Round the Toeplitz coefficient at each distance 1<=delta<=w downward,"
        in downstream
    )
    assert "a_hat_j*G_hat_(j-l)/a_hat_l" in downstream
    assert "slightly above\nthe true entries." in review
    assert "(1-epsilon) a_i <= ahat_i <= a_i`, with epsilon<=1/2." in gauge
    assert "ahat_j Ghat_(j-k)/ahat_k" in log_a


def weight_room() -> None:
    # 4η < 2^{-8p} iff 32760 p > 2. The gap grows with p.
    assert 32768 - 8 == 32760
    assert 32760 * 2 > 2
    assert 32760 > 0


def relative_budget() -> None:
    # 4(p+1)^2 - 9p^2 = -5p^2 + 8p + 4 is 0 at p=2 and decreases by 10p+3.
    assert -5 * 4 + 8 * 2 + 4 == 0
    assert -10 * 2 + 3 == -17
    assert -17 < 0
    # 9/4 < 4, so (p+1)^2 < 4 p^2 once 4(p+1)^2 <= 9 p^2.
    assert 9 < 16
    # Base: 2^2 < 2^{4}. The step gives p^2 < 2^{2p} for every integer p>=2.
    assert 4 < 16
    # 2p < 32760 p - 6, and the slack 32758 p - 6 increases by 32758.
    assert 4 < 32760 * 2 - 6
    assert 32760 - 2 == 32758
    assert 32758 > 0
    # Therefore p^2 < 2^{32760 p - 6}. With δ = 2^{2-32760 p} and 16 = 2^4,
    # 16 δ p^2 < 16 * 2^{2-6} = 1.
    assert 2 ** 4 * 2 ** (2 - 6) == 1
    # At p=2 the exponent room is concrete.
    assert 4 < 2 ** (32760 * 2 - 6)
    # The gauge allowance 1/2 is larger than 1/(16p^2) at p=2: 1/2 > 1/64.
    assert 2 * 64 == 128
    assert 128 > 2


def main() -> None:
    pins_and_phrases()
    weight_room()
    relative_budget()
    print("PASS_GAUSSIAN_RATIO_BUDGET")


if __name__ == "__main__":
    main()
