#!/usr/bin/env python3
"""Smallest uniform halo exponents under the ceiling 16 p^2.

The argument is HALO.md's, with p^10 replaced by 16 p^2. Every comparison
is an integer identity. It does not prove that ceiling for the rounded
matrix H.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-halo-exponents"
NOTES = ROOT / "research" / "unconditional-batched-crt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_match() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            assert digest(ROOT / row["path"]) == row["sha256"], row["path"]


def notes_still_use_the_old_exponents() -> None:
    halo = (NOTES / "HALO.md").read_text(encoding="utf-8")
    gaussian = (NOTES / "GAUSSIAN.md").read_text(encoding="utf-8")
    fine = (NOTES / "vendor" / "FINE-PRIME.md").read_text(encoding="utf-8")
    proof = (NOTES / "PROOF.md").read_text(encoding="utf-8")
    assert "2-norm at most p^10 and inverse\n2-norm at most p^10" in halo
    assert "Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42)" in halo
    assert "bandwidth <=(2J+1)W<p^45 eventually" in halo
    assert "||P_i-H_i^-1||_2 <= p^10 exp(-p^2)." in halo
    assert "[p^-20,p^20]" in halo
    assert "(1-p^-40)^J<=exp(-p^2)" in halo
    assert "A=ceil(p^48)" in halo
    assert "L=2^ceil(400 log2 p)" in halo
    assert "For A=p^48, L>=p^400" in halo
    assert "bandwidth<p^45" in gaussian
    assert "error<=p^10 exp(-p^2)" in gaussian
    assert "A=ceil(p^48)" in gaussian
    assert "dyadic p^100 bound" in gaussian
    assert "2^ceil(100 log2 p)" in fine
    assert "||H||_2,||H^-1||_2<=p^10" in fine
    assert "[0,1-p^-40]" in fine
    assert "J=ceil(p^42)" in fine
    assert "A=C_A p^48" in fine
    assert "halo exponent 48 and core exponent 128" in fine
    assert "core exponent400 and halo48" in proof
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def sparse_mul(left: dict[int, int], right: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for degree, coeff in left.items():
        for other, factor in right.items():
            key = degree + other
            out[key] = out.get(key, 0) + coeff * factor
    return {key: value for key, value in out.items() if value}


def exponents() -> None:
    # 16 p^2 <= p^6, with equality at p=2, because p^4 - 16 = (p^2-4)(p^2+4)
    # and p^2-4 = (p-2)(p+2).
    assert sparse_mul({2: 1, 0: -4}, {2: 1, 0: 4}) == {4: 1, 0: -16}
    assert sparse_mul({1: 1, 0: -2}, {1: 1, 0: 2}) == {2: 1, 0: -4}
    # p=2 makes every factor on the right of (p-2) zero, so equality.
    # p^5 does not cover 16 p^2: 64 > 32.
    assert 16 * 2 * 2 == 64 > 32 == 2**5
    # Strict normalizer: p^7 - 16 p^2 = p^2 (p^5 - 16) and p^5 >= 32 > 16.
    assert 2**5 == 32 > 16
    # p^6 meets 16 p^2 at p=2, so division by p^6 is not strictly below one.
    assert 2**6 == 64 == 16 * 2 * 2

    # Spectral exponent. (16 p^2)^2 = 256 p^4 <= p^12 iff p^8 >= 256.
    # p^8 - 256 = (p^4 - 16)(p^4 + 16), and p^4 - 16 >= 0 as above.
    assert sparse_mul({4: 1, 0: -16}, {4: 1, 0: 16}) == {8: 1, 0: -256}
    assert 256 == 2**8
    # Exponent 11 fails at p=2: p^7 = 128 < 256.
    assert 2**7 == 128 < 256

    # Q = I - p^-12 H* H then has spectrum in [0, 1 - p^-24].
    # J = p^26 gives J p^-24 = p^2, so (1 - p^-24)^J <= exp(-p^2)
    # by exp(x) = sum x^k/k! <= sum x^k = 1/(1-x) for x in (0, 1).
    assert 26 - 24 == 2
    assert 25 - 24 == 1
    # The series bound is strict for x>0 because 1/2! < 1.
    assert 1 / 2 < 1

    # Sharp radius (2 p^26 - 1)(p - 1) = 2 p^27 - 2 p^26 - p + 1.
    sharp = sparse_mul({26: 2, 0: -1}, {1: 1, 0: -1})
    assert sharp == {27: 2, 26: -2, 1: -1, 0: 1}
    # p^28 - sharp = p^26 ((p-1)^2 + 1) + p - 1.
    quadratic = sparse_mul({1: 1, 0: -1}, {1: 1, 0: -1})
    quadratic[0] = quadratic.get(0, 0) + 1
    assert quadratic == {2: 1, 1: -2, 0: 2}
    margin = sparse_mul({26: 1}, quadratic)
    margin[1] = margin.get(1, 0) + 1
    margin[0] = margin.get(0, 0) - 1
    assert margin == {28: 1, 27: -2, 26: 2, 1: 1, 0: -1}
    # (p-1)^2 + 1 >= 2 for integer p >= 2, so the margin is at least
    # 2 p^26 + p - 1 > 0. Exponent 28 covers the sharp radius.
    # Exponent 27 does not for p >= 3: sharp - p^27 = p^26 (p-2) - p + 1
    # >= p^26 - p + 1 >= 1.
    excess = dict(sharp)
    excess[27] = excess.get(27, 0) - 1
    assert excess == {27: 1, 26: -2, 1: -1, 0: 1}
    reduced = sparse_mul({26: 1}, {1: 1, 0: -2})
    reduced[1] = reduced.get(1, 0) - 1
    reduced[0] = reduced.get(0, 0) + 1
    assert reduced == excess

    # HALO's looser (2 p^26 + 1)(p - 1) is still below p^28, and above p^27
    # already at p=2.
    loose = sparse_mul({26: 2, 0: 1}, {1: 1, 0: -1})
    assert loose == {27: 2, 26: -2, 1: 1, 0: -1}
    loose_margin = {28: 1}
    for degree, coeff in loose.items():
        loose_margin[degree] = loose_margin.get(degree, 0) - coeff
    assert loose_margin == {28: 1, 27: -2, 26: 2, 1: -1, 0: 1}
    loose_excess = dict(loose)
    loose_excess[27] = loose_excess.get(27, 0) - 1
    assert loose_excess == {27: 1, 26: -2, 1: 1, 0: -1}
    # At p=2 this excess is 2^26 * 0 + 2 - 1 = 1, so the loose radius
    # bound is p^27 + 1.
    assert 2**26 * 0 + 2 - 1 == 1

    # Core exponent 86 keeps L >= p^86 > 4 p^28 and both sparse powers
    # negative for every epsilon, beta < 1. Exponent 85 does not.
    assert 86 - 28 >= 1 and 2**58 > 4
    assert 84 - 86 == -2  # epsilon + beta + 84 - 86 < 0
    assert 85 - 84 == 1  # epsilon + beta - 1 can be positive
    assert 28 + 2 - 86 < 0


def main() -> None:
    pins_match()
    notes_still_use_the_old_exponents()
    exponents()
    print("halo exponents 20,42,45,48,100 can fall to 12,26,28,28,7")


if __name__ == "__main__":
    main()
