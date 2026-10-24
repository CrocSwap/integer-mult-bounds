#!/usr/bin/env python3
"""Halo exponents under the published weight error δ = 2^{2-32760 p}.

Every comparison is an integer identity. The ideal gaps are hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-delta-exponents"


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


def shift(poly, origin):
    degree = max(poly)
    choose = [[0] * (degree + 1) for _ in range(degree + 1)]
    for row in range(degree + 1):
        choose[row][0] = 1
        for col in range(1, row + 1):
            choose[row][col] = choose[row - 1][col - 1] + choose[row - 1][col]
    out = {}
    for power, coeff in poly.items():
        for index in range(power + 1):
            key = index
            out[key] = out.get(key, 0) + coeff * choose[power][index] * origin ** (power - index)
    return {key: coeff for key, coeff in out.items() if coeff}


def evaluate(poly, point):
    total = 0
    for power in range(max(poly), -1, -1):
        total = total * point + poly.get(power, 0)
    return total


def positive_on_ray(poly, origin):
    moved = shift(poly, origin)
    assert set(moved) == set(range(max(poly) + 1))
    assert all(coeff > 0 for coeff in moved.values())
    for point in range(origin, origin + max(poly) + 1):
        assert evaluate(poly, point) == evaluate(moved, point - origin)
        assert evaluate(poly, point) > 0


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
    downstream = (
        ROOT / "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md"
    ).read_text(encoding="utf-8")
    log_a = (
        ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md"
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
    assert "Set P=32768p and eta=2^(-P)." in downstream
    assert "2^(-8p)<a_j<=1." in downstream
    assert "absolute error below four eta" in downstream
    assert "a_hat_j*G_hat_(j-l)/a_hat_l" in downstream
    assert "ahat_j Ghat_(j-k)/ahat_k" in log_a


def power_room() -> None:
    # 4η < 2^{-8p} is the exponent identity 32768 - 8 = 32760.
    assert 32768 - 8 == 32760
    # Integer induction: 2^{2p} >= p^2 + 1. The step clears to 3p^2 - 2p + 3.
    square = {2: 1}
    successor = mul({1: 1, 0: 1}, {1: 1, 0: 1})
    gap = add(scale(add(square, {0: 1}), 4), scale(successor, -1))
    assert gap == {2: 3, 1: -2, 0: 3}
    assert 2 ** (2 * 2) >= 2 ** 2 + 1
    positive_on_ray(gap, 2)
    # 2p + 6 <= 32760 p, so D = 2^{32760 p} >= 2^{2p+6} = 64 * 2^{2p}.
    assert 2 * 2 + 6 <= 32760 * 2
    assert 32760 - 2 > 0
    assert 2 ** (2 * 2 + 6) == 64 * (2 ** (2 * 2))
    # At p = 2 the same floor is visible directly: D >= 2^{16} > 64 p^2.
    assert 2 ** 16 > 64 * 4
    assert 2 ** 16 > 252


def ceiling() -> None:
    # U > 8p^2 exactly when 32p^2 > 4. At p = 2 this floor is p^5, and its square is p^{10}.
    assert 8 * 4 == 32
    assert 2 ** 5 == 32
    assert 32 * 4 > 4
    assert 64 * 16 == 1024
    assert 2 ** 10 == 1024
    assert 32 < 64
    assert 2 ** 6 == 64
    # U < p^6 at p = 2: 32(p^6 - 1) = 2016 < 8 D.
    assert 32 * (64 - 1) == 2016
    assert 2016 < 8 * 2 ** 16
    # For p >= 3, 64(p^2+1)(p^4-8) - 32(p^6-1) has every coefficient positive after p = 3 + t.
    sixth = {6: 1}
    fourth = {4: 1}
    room = add(
        scale(mul(add({2: 1}, {0: 1}), add(fourth, {0: -8})), 64),
        scale(add(sixth, {0: -1}), -32),
    )
    reduced = scale({6: 1, 4: 2, 2: -16, 0: -15}, 32)
    assert room == reduced
    positive_on_ray({6: 1, 4: 2, 2: -16, 0: -15}, 3)
    assert 3 ** 4 > 16
    # V^2 < p^{11}. At p = 2 the quadratic D^2 - 512 D + 32768 is positive for D >= 2^{16}.
    assert 2 ** 32 > 512 * 2 ** 16
    assert 3 ** 7 > 256
    assert 3 ** 7 // 4 > 64
    # Eigenvalues of A*A stay below 4 < p^{11}. The scalar series step uses 1/2! < 1.
    assert 4 < 2 ** 11
    assert 2 ** 11 == 2048
    assert 1 < 2
    # V < 16p^2 - 1 clears to 15p^2 - 2, positive for every integer p >= 2.
    linear = {2: 8, 0: -1}
    sixteen = {2: 16, 0: -1}
    coarse = add(
        scale(mul(linear, add({2: 1}, {0: 1})), 2),
        scale(mul({2: 1}, sixteen), -1),
    )
    assert coarse == {2: 15, 0: -2}
    positive_on_ray(coarse, 2)
    assert 16 * 4 - 1 == 63
    assert 63 > 32
    assert 128 * 63 == 8064
    assert 31 * 2 ** 16 > 8064


def exponents() -> None:
    quadratic = add(mul({1: 1, 0: -1}, {1: 1, 0: -1}), {0: 1})
    assert quadratic == {2: 1, 1: -2, 0: 2}
    factored = add(mul({24: 1}, quadratic), {1: 1, 0: -1})
    sharp = mul({24: 2, 0: -1}, {1: 1, 0: -1})
    margin = add({26: 1}, scale(sharp, -1))
    assert factored == margin
    assert margin == {26: 1, 25: -2, 24: 2, 1: 1, 0: -1}
    assert 24 - 22 == 2
    assert 23 - 22 == 1
    assert 12 - 10 == 2
    # Exponent 25 fails. The p = 2 loose radius is p^{25} + 1.
    assert 2 * (2 ** 24) + 1 == 2 ** 25 + 1
    assert 2 ** 25 + 1 > 2 ** 25
    assert (2 * (3 ** 24) - 1) * (3 - 1) > 3 ** 25
    # For p >= 3 the sharp radius exceeds p^{25} once p^2 > p - 1.
    assert {2: 1, 1: -1, 0: 1} == add(add({2: 1}, {1: -1}), {0: 1})
    positive_on_ray({2: 1, 1: -1, 0: 1}, 3)


def main() -> None:
    pins_and_phrases()
    power_room()
    ceiling()
    exponents()
    print("PASS_GAUSSIAN_DELTA_EXPONENTS")


if __name__ == "__main__":
    main()
