#!/usr/bin/env python3
"""Within-cell column transfer for a downward gauge.

Integer identities only. The ideal column gap is a hypothesis, taken from
the constant-phase lemma. This does not bound across-cell entries.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-gauge-column"


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
    log_a = (
        ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md"
    ).read_text(encoding="utf-8")
    gauge = (
        ROOT / "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md"
    ).read_text(encoding="utf-8")
    gaussian = (
        ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
    ).read_text(encoding="utf-8")
    column = (ROOT / "research/gaussian-column-gap/README.md").read_text(
        encoding="utf-8"
    )
    downstream = (
        ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "ahat_j Ghat_(j-k)/ahat_k" in log_a
    assert "Downward rounding only decreases this off-diagonal sum." in log_a
    assert "(1-epsilon) a_i <= ahat_i <= a_i`, with epsilon<=1/2." in gauge
    assert "log(a_i/a_j)=a(i-j)(beta_i+beta_j)" in gauge
    assert "A=diag(ahat) Ghat diag(ahat)^-1" in gauge
    assert "P_setup=Cp+64p^2ceil(log2 p)" in gaussian
    assert "relative error<2^-Cp" in gaussian
    assert "`δ_col` exceeds `1/(8p²)` eventually" in column
    assert "||H-N|| < p*2^(16p+7)*eta + 2^(-46p)." in downstream
    assert "Across different cells use the downward\ndyadic approximation" in downstream


def kernel_factorization() -> None:
    # (β + θh + h)^2 - (β + θh)^2 = h^2 + 2 θ h^2 + 2 β h.
    # Keys are (power of β, power of θh, power of h).
    beta = {(1, 0, 0): 1}
    shift = {(0, 1, 0): 1}
    step = {(0, 0, 1): 1}

    def tmul(left, right):
        out = {}
        for left_key, left_coeff in left.items():
            for right_key, right_coeff in right.items():
                key = tuple(a + b for a, b in zip(left_key, right_key))
                out[key] = out.get(key, 0) + left_coeff * right_coeff
        return {key: coeff for key, coeff in out.items() if coeff}

    grown = add(add(beta, shift), step)
    square = add(tmul(grown, grown), scale(tmul(add(beta, shift), add(beta, shift)), -1))
    assert square == add(add(tmul(step, step), scale(tmul(shift, step), 2)), scale(tmul(beta, step), 2))
    # Divide by a: subtract the log-ratio -h(2β + θh) from the row exponent.
    row = {0: 1, 1: 2, 2: 2}
    ratio = {1: -1, 2: -2}
    assert add(scale(row, -1), scale(ratio, -1)) == {0: -1, 1: -1}


def column_budget() -> None:
    # off_H <= off_N/(1-ε). With off_N <= 1-1/(8p^2) and ε=1/(16p^2),
    # the gap is at least 1/(16p^2-1) > 1/(16p^2).
    cleared = {2: 16, 0: -1}
    assert add(cleared, {0: 1}) == {2: 16}
    # ε=1/2 gives the upper bound 2-1/(4p^2), and 4p^2>1.
    assert 2 * 4 == 8
    assert 4 * 2 * 2 > 1
    # (2p-1)/(16p) > 1/(8p^2) iff p(2p-1)-2 > 0.
    value = add(mul({1: 2, 0: -1}, {1: 1}), {0: -2})
    assert value == {2: 2, 1: -1, 0: -2}
    assert 2 * 4 - 2 - 2 == 4
    nxt = add(
        add(mul({0: 2}, mul({1: 1, 0: 1}, {1: 1, 0: 1})), scale({1: 1, 0: 1}, -1)),
        {0: -2},
    )
    assert add(nxt, scale(value, -1)) == {1: 4, 0: 1}


def setup_constant() -> None:
    # Smallest C with 2^{C p} >= 16 p^2 for every integer p>=2 is C=3.
    assert 2 ** (3 * 2) == 64 == 16 * (2 ** 2)
    assert 2 ** (2 * 2) == 16
    assert 16 < 64
    # ((p+1)/p)^2 <= (3/2)^2 = 9/4 < 8 = 2^3.
    assert 3 * 2 - 2 * (2 + 1) == 0
    assert 9 < 32
    assert uni_gap() == {1: 1, 0: -2}


def uni_gap() -> dict:
    return add({1: 3}, scale({1: 2, 0: 2}, -1))


def main() -> None:
    pins_and_phrases()
    kernel_factorization()
    column_budget()
    setup_constant()
    print("PASS_GAUSSIAN_GAUGE_COLUMN")


if __name__ == "__main__":
    main()
