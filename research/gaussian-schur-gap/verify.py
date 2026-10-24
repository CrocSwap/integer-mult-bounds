#!/usr/bin/env python3
"""Row-dominance margins survive a Schur step, and 10 p^2 keeps the exponents.

Every comparison is an integer or polynomial identity. The ideal gaps are hypotheses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-schur-gap"


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


def mul_uni(left, right):
    out = {}
    for degree, coeff in left.items():
        for other, factor in right.items():
            key = degree + other
            out[key] = out.get(key, 0) + coeff * factor
    return {key: coeff for key, coeff in out.items() if coeff}


def mul(left, right):
    out = {}
    for left_key, left_coeff in left.items():
        for right_key, right_coeff in right.items():
            key = tuple(left_key[i] + right_key[i] for i in range(len(left_key)))
            out[key] = out.get(key, 0) + left_coeff * right_coeff
    return {key: coeff for key, coeff in out.items() if coeff}


def mono(exponent, coeff=1):
    return {exponent: coeff}


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    gaussian = (ROOT / "research/unconditional-batched-crt/GAUSSIAN.md").read_text(
        encoding="utf-8"
    )
    conditioning = (
        ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
    ).read_text(encoding="utf-8")
    fine = (ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md").read_text(
        encoding="utf-8"
    )
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "L=2^ceil(400 log2 p)" in halo
    assert "For A=p^48, L>=p^400" in halo
    assert "S=D-C A^-1 B; do not solve with S^-1" in halo
    assert "strict row diagonal dominance survives every\nelimination with at least the original row gap" in gaussian
    assert "complementary Schur inverse is the corresponding\nprincipal block of T^-1" in conditioning
    assert "The Schur complement itself is bounded by D-C A^-1 B" in conditioning
    assert "its Schur complements retain that gap." in fine


def elimination_identities() -> None:
    # Variables a, d, o, c, o1. The cleared one-step identities are identically zero.
    a = mono((1, 0, 0, 0, 0))
    d = mono((0, 1, 0, 0, 0))
    o = mono((0, 0, 1, 0, 0))
    c = mono((0, 0, 0, 1, 0))
    o1 = mono((0, 0, 0, 0, 1))
    # a(L-delta) = a(d-o-delta) + c(a-o1), so the delta terms were already cleared
    # into the two margin factors. The polynomial below is a*L_cleared minus that sum,
    # with L_cleared = a*d - a*(o-c) - c*o1 and delta removed from both sides.
    cleared_margin = add(
        add(mul(a, d), scale(mul(a, add(scale(o, -1), c)), 1)),
        scale(mul(c, o1), -1),
    )
    claimed_margin = add(mul(a, add(d, scale(o, -1))), mul(c, add(a, scale(o1, -1))))
    assert add(cleared_margin, scale(claimed_margin, -1)) == {}
    # a(U - (d+o)) = c(o1-a).
    cleared_sum = add(
        add(add(mul(a, d), mul(a, o)), scale(mul(a, c), -1)),
        mul(c, o1),
    )
    claimed_sum = add(mul(a, add(d, o)), mul(c, add(o1, scale(a, -1))))
    assert add(cleared_sum, scale(claimed_sum, -1)) == {}
    # Integer witness. Pivot 40, diagonal 40, off-sums 36 and 30, coupling 6.
    # The current margin equals 4, so the cleared slack is the coupling term only.
    pivot, diagonal, off, coupling, pivot_off = 40, 40, 36, 6, 30
    margin_product = pivot * (diagonal - off) + coupling * (pivot - pivot_off)
    raw = pivot * diagonal - pivot * (off - coupling) - coupling * pivot_off
    assert raw == margin_product == 220
    assert raw - pivot * (diagonal - off) == coupling * (pivot - pivot_off) == 60
    row_raw = pivot * (diagonal + off - coupling) + coupling * pivot_off
    previous = pivot * (diagonal + off)
    assert previous - row_raw == coupling * (pivot - pivot_off) == 60


def ceilings() -> None:
    # 10 p^2 against p^5 and p^6 at p=2, and its square against p^{10} and p^{11}.
    assert 10 * 4 == 40
    assert 2 ** 5 == 32
    assert 40 > 32
    assert 2 ** 6 == 64
    assert 40 < 64
    assert 100 * (2 ** 4) == 1600
    assert 2 ** 10 == 1024
    assert 1600 > 1024
    assert 2 ** 7 == 128
    assert 100 < 128
    assert 2 ** 11 == 2048
    assert 1600 < 2048
    assert 2 ** 4 == 16
    assert 10 < 16
    assert 4 < 2048
    assert 1 < 2
    # The older ceiling 16p^2-1 has square 3969 > 2048 at p=2, so endpoint 11 fails.
    assert 16 * 4 - 1 == 63
    assert 63 * 63 == 3969
    assert 3969 > 2048
    # #4462's margin (4p-1)/(32 p^3) is at least 7/(64 p^2), hence at least 1/(10 p^2).
    assert 7 * 10 > 64
    cubic = add(scale({3: 1}, 32), {2: -64})
    factored = mul_uni({2: 32}, {1: 1, 0: -2})
    assert cubic == factored == {3: 32, 2: -64}
    assert 32 * 4 * (2 - 2) == 0
    assert 32 * 9 * (3 - 2) == 32 * 9


def exponents() -> None:
    quadratic = add(mul_uni({1: 1, 0: -1}, {1: 1, 0: -1}), {0: 1})
    assert quadratic == {2: 1, 1: -2, 0: 2}
    factored = add(mul_uni({24: 1}, quadratic), {1: 1, 0: -1})
    sharp = mul_uni({24: 2, 0: -1}, {1: 1, 0: -1})
    margin = add({26: 1}, scale(sharp, -1))
    assert factored == margin
    assert margin == {26: 1, 25: -2, 24: 2, 1: 1, 0: -1}
    assert 24 - 22 == 2
    assert 23 - 22 == 1
    assert 2 * (2 ** 24) + 1 == 2 ** 25 + 1
    assert 2 ** 25 + 1 > 2 ** 25
    assert (2 * (3 ** 24) - 1) * (3 - 1) > 3 ** 25


def main() -> None:
    pins_and_phrases()
    elimination_identities()
    ceilings()
    exponents()
    print("PASS_GAUSSIAN_SCHUR_GAP")


if __name__ == "__main__":
    main()
