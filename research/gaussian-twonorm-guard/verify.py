#!/usr/bin/env python3
"""The written p^10 guards still cover both inverse 2-norm ceilings.

Callers and exponents are read from the pinned #4100 notes. The comparison
uses exact integers. It does not prove a column gap for the rounded matrix H.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-twonorm-guard"
NOTES = ROOT / "research" / "unconditional-batched-crt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> str:
    return (NOTES / name).read_text(encoding="utf-8")


def pins_match() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    expected = {
        row["path"]: row["sha256"]
        for row in sources["files"]
        if row["usage"] == "input"
    }
    for path, sha in expected.items():
        assert digest(ROOT / path) == sha, path


def callers_write_these_exponents() -> None:
    inverse = load("INVERSE-CONDITIONING.md")
    gaussian = load("GAUSSIAN.md")
    halo = load("HALO.md")
    fine = load("vendor/FINE-PRIME.md")
    proof = load("PROOF.md")
    audit = load("AUDIT.md")

    assert "||H^-1||_infinity <= 1/delta," in inverse
    assert "||H^-1||_1 <= 1/delta + 2 b rho/delta^2," in inverse
    assert (
        "||H^-1||_2 <= sqrt((1/delta)(1/delta + 2 b rho/delta^2))." in inverse
    )
    assert "establishes b<p and\ndelta>=1/(16p^2)" in inverse

    assert "row gap delta>=1/(16p^2) and row norm<2" in gaussian
    assert "||H^-1||_1<=delta^-1+2w(1-delta)delta^-2." in gaussian
    assert "less than p^10 eventually" in gaussian
    assert "||K^-1||_2<O(alpha p^5)<p^6" in gaussian
    assert "The conservative p^10 allowance\nis ample." in gaussian
    assert (
        "P=p^-20 sum_{j<ceil(p^42)}(I-p^-20 H*H)^j H*, bandwidth<p^45 and\n"
        "error<=p^10 exp(-p^2)"
    ) in gaussian
    assert "A=ceil(p^48)" in gaussian
    assert "dyadic p^100 bound" in gaussian

    assert "2-norm at most p^10 and inverse\n2-norm at most p^10" in halo
    assert "Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42)" in halo
    assert "bandwidth <=(2J+1)W<p^45 eventually" in halo
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "[p^-20,p^20]" in halo
    assert "(1-p^-40)^J<=exp(-p^2)" in halo
    assert "A=ceil(p^48)" in halo
    assert "For A=p^48, L>=p^400" in halo
    assert "prove the p^10 narrow bounds" in halo

    assert "conservative common eventual bound p^10 covers" in fine
    assert "2^ceil(100 log2 p)" in fine
    assert "||H||_2,||H^-1||_2<=p^10" in fine
    assert "Q=I-p^-20 H* H." in fine
    assert "[0,1-p^-40]" in fine
    assert "J=ceil(p^42)" in fine
    assert "p^10 exp(-p^2)" in fine
    assert "A=C_A p^48" in fine
    assert "halo exponent 48 and core exponent 128" in fine

    assert "core exponent400 and halo48" in proof
    assert "p^10" not in proof
    assert "p^10" not in audit
    assert "INVERSE-CONDITIONING.md bounds narrow principal restrictions" in audit

    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def multiply(left: list[int], right: list[int]) -> list[int]:
    """Product of polynomials, lowest degree first."""
    out = [0] * (len(left) + len(right) - 1)
    for i, coeff in enumerate(left):
        for j, other in enumerate(right):
            out[i + j] += coeff * other
    return out


def bracket_coefficients() -> list[int]:
    """Coefficients of 1 + 2(p-1)(16p^2-1)."""
    # (p-1)(16p^2-1) = 16p^3 - 16p^2 - p + 1, then double and add 1.
    product = multiply([-1, 1], [-1, 0, 16])
    assert product == [1, -1, -16, 16]
    doubled = [2 * coeff for coeff in product]
    doubled[0] += 1
    assert doubled == [3, -2, -32, 32]
    return doubled


def bracket(p: int) -> int:
    coeffs = bracket_coefficients()
    return sum(coeff * p**degree for degree, coeff in enumerate(coeffs))


def corner_square(p: int) -> int:
    """Squared bandwidth ceiling at b=p-1 and delta=1/(16p^2)."""
    delta_den = 16 * p * p
    rho_num = delta_den - 1
    inf = delta_den
    # 2 b rho / delta^2 = 32 p^2 (p-1) (16p^2-1)
    one_extra = 32 * p * p * (p - 1) * rho_num
    return inf * (inf + one_extra)


def ceilings_stay_below_p10() -> None:
    coeffs = bracket_coefficients()
    # 32p^3 - bracket(p) = -3 + 2p + 32p^2.
    difference = [-coeffs[0], -coeffs[1], -coeffs[2], 32 - coeffs[3]]
    assert difference == [-3, 2, 32, 0]
    # 16p^2 + p - 17 = (p-1)(16p+17), so the difference is
    # 2(p-1)(16p+17) + 31 >= 31 for every integer p >= 1.
    assert multiply([-1, 1], [17, 16]) == [-17, 1, 16]
    assert [2 * coeff for coeff in [-17, 1, 16]] == [-34, 2, 32]
    assert [-34 + 31, 2, 32] == [-3, 2, 32]

    for p in (2, 19):
        assert corner_square(p) == 256 * p**4 * bracket(p)
        assert 32 * p**3 - bracket(p) == 32 * p * p + 2 * p - 3

    # At p=2 the loose multiple 8192 p^7 equals p^20, so the strict bracket
    # step is what puts the corner below p^10. Exponent 9 does not.
    assert 8192 * 2**7 == 2**20
    assert corner_square(2) < 2**20
    assert corner_square(2) >= 2**18
    assert 4 * 2 < 2**20
    assert (16 * 2 * 2) ** 2 < 2**20

    # For p >= 3, 8192 < p^13, so even the loose multiple is below p^20.
    assert 8192 < 3**13
    assert corner_square(3) < 8192 * 3**7 < 3**20

    # From p=19 the bandwidth ceiling is already below p^6, the column-gap
    # ceiling below p^3, and the squared ratio below p^6.
    assert 8192 < 19**5
    assert bracket(19) == 207901
    assert corner_square(19) == 6936029752576
    assert corner_square(19) < 19**12
    assert 16 * 19 * 19 == 5776 < 19**3
    assert bracket(19) < 19**6
    assert 19**20 > corner_square(19) * 19**8
    assert 4 * 19 < 19**2


def main() -> None:
    pins_match()
    callers_write_these_exponents()
    ceilings_stay_below_p10()
    print("p10 guards unchanged under both ceilings")


if __name__ == "__main__":
    main()
