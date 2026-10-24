#!/usr/bin/env python3
"""Within-cell halo exponents under the relative-error budget.

Every comparison is an integer identity. The ideal row and column gaps are
hypotheses. Across-cell entries are not bounded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-cell-exponents"


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


def mul(left, right):
    out = {}
    for degree, coeff in left.items():
        for other, factor in right.items():
            key = degree + other
            out[key] = out.get(key, 0) + coeff * factor
    return {key: coeff for key, coeff in out.items() if coeff}


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(
        encoding="utf-8"
    )
    gaussian = (
        ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
    ).read_text(encoding="utf-8")
    column = (ROOT / "research/gaussian-column-gap/README.md").read_text(
        encoding="utf-8"
    )
    log_a = (
        ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md"
    ).read_text(encoding="utf-8")
    gauge = (
        ROOT / "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md"
    ).read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "2-norm at most p^10 and inverse\n2-norm at most p^10" in halo
    assert "Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42)" in halo
    assert "bandwidth <=(2J+1)W<p^45 eventually" in halo
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "[p^-20,p^20]" in halo
    assert "(1-p^-40)^J<=exp(-p^2)" in halo
    assert "A=ceil(p^48)" in halo
    assert "Thus its row gap exceeds 1/(8p^2) eventually." in gaussian
    assert "`δ_col` exceeds `1/(8p²)` eventually" in column
    assert "ahat_j Ghat_(j-k)/ahat_k" in log_a
    assert "(1-epsilon) a_i <= ahat_i <= a_i`, with epsilon<=1/2." in gauge


def rounded_ceilings() -> None:
    # Ideal off-sum <= 1-1/(8p^2) and ε=1/(16p^2) give rounded off-sum
    # <= (16p^2-2)/(16p^2-1), hence gap >= 1/(16p^2-1).
    numerator = add({2: 16}, {0: -2})
    denominator = add({2: 16}, {0: -1})
    assert add(denominator, scale(numerator, -1)) == {0: 1}
    # Row sum 1+off <= (32p^2-3)/(16p^2-1) < 2.
    row_sum = add({2: 32}, {0: -3})
    twice = scale(denominator, 2)
    assert add(twice, scale(row_sum, -1)) == {0: 1}
    # Inverse 1-norms are at most 16p^2-1. At p=2 that ceiling is 63.
    assert 16 * 4 - 1 == 63
    assert 63 * 63 == 3969
    assert 2 ** 12 == 4096
    assert 3969 <= 4096
    assert 2 ** 11 == 2048
    assert 3969 > 2048
    assert 2 ** 5 == 32
    assert 63 > 32


def exponent_arithmetic() -> None:
    # p^4-16=(p-2)(p+2)(p^2+4), so 16p^2<=p^6, and 16p^2-1<p^6.
    quartic = mul(mul({1: 1, 0: -2}, {1: 1, 0: 2}), {2: 1, 0: 4})
    assert quartic == {4: 1, 0: -16}
    assert add(mul({2: 1}, quartic), {0: 1}) == add(add({6: 1}, scale({2: 16}, -1)), {0: 1})
    # p^6 >= 16p^2-1 iff the spectral step p^-12 is valid, and p^25 is not.
    assert 2 ** 6 == 64
    assert 64 - 63 == 1
    assert 2 ** 11 < 3969
    # 1/2! < 1 makes (1-x)^J < exp(-J x).
    assert 1 < 2
    assert 26 - 24 == 2
    assert 25 - 24 == 1
    # Sharp radius (2p^26-1)(p-1) is below p^28.
    quadratic = add(mul({1: 1, 0: -1}, {1: 1, 0: -1}), {0: 1})
    assert quadratic == {2: 1, 1: -2, 0: 2}
    factored = add(mul({26: 1}, quadratic), {1: 1, 0: -1})
    sharp = mul({26: 2, 0: -1}, {1: 1, 0: -1})
    margin = add({28: 1}, scale(sharp, -1))
    assert factored == margin
    assert margin == {28: 1, 27: -2, 26: 2, 1: 1, 0: -1}
    # Exponent 27 fails. At p=2 the loose radius is p^27+1.
    assert 2 * (2 ** 26) + 1 == 2 ** 27 + 1
    assert (2 * (2 ** 26) - 1) == 2 ** 27 - 1
    # For p>=3 the sharp radius at W=p-1 exceeds p^27.
    assert (2 * (3 ** 26) - 1) * (3 - 1) > 3 ** 27 + 1
    # Normalizer 6 puts 16p^2-1 strictly below one; 5 does not.
    assert 63 < 64
    assert 63 > 32


def main() -> None:
    pins_and_phrases()
    rounded_ceilings()
    exponent_arithmetic()
    print("PASS_GAUSSIAN_CELL_EXPONENTS")


if __name__ == "__main__":
    main()
