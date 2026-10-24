#!/usr/bin/env python3
"""Across-cell transfer of the within-cell halo exponents.

Every comparison is an integer identity. The ideal gaps and the within-cell
factor 1/(1-ε) are hypotheses. The across-cell hypothesis is 0 ≤ H ≤ n.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-cross-exponents"


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


def tadd(left, right):
    out = dict(left)
    for key, coeff in right.items():
        out[key] = out.get(key, 0) + coeff
        if out[key] == 0:
            del out[key]
    return out


def tscale(poly, factor):
    return {key: factor * coeff for key, coeff in poly.items() if factor * coeff}


def tmul(left, right):
    out = {}
    for left_key, left_coeff in left.items():
        for right_key, right_coeff in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key))
            out[key] = out.get(key, 0) + left_coeff * right_coeff
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
    downstream = (
        ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    review = (
        ROOT / "references/semantic-bulk/rad20/reports/review-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    fine = (
        ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
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
    assert "n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])" in log_a
    assert (
        "one globally fixed downward dyadic Toeplitz kernel `Ghat_delta`" in log_a
    )
    assert (
        "across cells, use the retained downward Gaussian entries; set H_jj=1."
        in log_a
    )
    assert "(1-epsilon) a_i <= ahat_i <= a_i`, with epsilon<=1/2." in gauge
    assert (
        "Across different cells use the downward\n"
        "dyadic approximation of the original entry for abs(delta)<=w."
        in downstream
    )
    assert "across cells use downward dyadic entries." in review
    assert "slightly above\nthe true entries." in review
    assert "across cells use rounded\nGaussian entries, with diagonal exactly one." in fine
    assert "downward Gaussian entries" not in fine


def split_identity() -> None:
    # Symbols (s, t, u). Cleared form of
    # u/(1-1/s) + (t-u) ≤ t/(1-1/s) when u ≤ t:
    # s*u + (t-u)*(s-1) - t*s = u - t.
    symbol_s = {(1, 0, 0): 1}
    symbol_t = {(0, 1, 0): 1}
    symbol_u = {(0, 0, 1): 1}
    one = {(0, 0, 0): 1}
    within = tmul(symbol_s, symbol_u)
    across = tmul(tadd(symbol_t, tscale(symbol_u, -1)), tadd(symbol_s, tscale(one, -1)))
    total = tmul(symbol_t, symbol_s)
    cleared = tadd(tadd(within, across), tscale(total, -1))
    assert cleared == tadd(symbol_u, tscale(symbol_t, -1))


def rounded_ceilings() -> None:
    # Ideal off-sum ≤ (16p^2-2)/(16p^2). After the split, off-sum
    # ≤ (16p^2-2)/(16p^2-1), hence gap ≥ 1/(16p^2-1).
    numerator = add({2: 16}, {0: -2})
    denominator = add({2: 16}, {0: -1})
    assert add(denominator, scale(numerator, -1)) == {0: 1}
    row_sum = add({2: 32}, {0: -3})
    twice = scale(denominator, 2)
    assert add(twice, scale(row_sum, -1)) == {0: 1}
    # At p=2 the ceiling is 63. One extra part in 64 already exceeds it:
    # 63/64 > 62/63 because 63*63 = 3969 > 3968 = 62*64.
    assert 16 * 4 - 1 == 63
    assert 16 * 4 - 2 == 62
    assert 63 * 63 == 3969
    assert 62 * 64 == 3968
    assert 3969 > 3968
    assert 2 ** 12 == 4096
    assert 3969 <= 4096
    assert 2 ** 11 == 2048
    assert 3969 > 2048
    assert 2 ** 5 == 32
    assert 63 > 32


def bare_kernel_gap() -> None:
    # θ=1/4, β=1/4, h=1 and g=2 give β_next=β+θ-1=-1/2.
    # The Gaussian square gap is 2. The bare kernel uses ρ h^2=5/4.
    assert 1 + 1 - 4 == -2
    assert 6 * 6 - 2 * 2 == 32
    assert 5 * 4 == 20
    assert 32 > 20


def exponent_arithmetic() -> None:
    quartic = mul(mul({1: 1, 0: -2}, {1: 1, 0: 2}), {2: 1, 0: 4})
    assert quartic == {4: 1, 0: -16}
    assert add(mul({2: 1}, quartic), {0: 1}) == add(
        add({6: 1}, scale({2: 16}, -1)), {0: 1}
    )
    assert 2 ** 6 == 64
    assert 64 - 63 == 1
    assert 2 ** 11 < 3969
    assert 1 < 2
    assert 26 - 24 == 2
    assert 25 - 24 == 1
    quadratic = add(mul({1: 1, 0: -1}, {1: 1, 0: -1}), {0: 1})
    assert quadratic == {2: 1, 1: -2, 0: 2}
    factored = add(mul({26: 1}, quadratic), {1: 1, 0: -1})
    sharp = mul({26: 2, 0: -1}, {1: 1, 0: -1})
    margin = add({28: 1}, scale(sharp, -1))
    assert factored == margin
    assert margin == {28: 1, 27: -2, 26: 2, 1: 1, 0: -1}
    assert 2 * (2 ** 26) + 1 == 2 ** 27 + 1
    assert (2 * (2 ** 26) - 1) == 2 ** 27 - 1
    assert (2 * (3 ** 26) - 1) * (3 - 1) > 3 ** 27 + 1
    assert 3 ** 8 > 256
    assert 63 < 64
    assert 63 > 32


def main() -> None:
    pins_and_phrases()
    split_identity()
    rounded_ceilings()
    bare_kernel_gap()
    exponent_arithmetic()
    print("PASS_GAUSSIAN_CROSS_EXPONENTS")


if __name__ == "__main__":
    main()
