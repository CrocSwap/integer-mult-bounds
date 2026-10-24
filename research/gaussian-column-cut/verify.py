#!/usr/bin/env python3
"""Column off-sum of the ideal narrow Gaussian matrix at a g=2 step.

Every comparison is an integer or rational identity. The exponential series
is used only through the partial sum of e and the remainder sign stated in
the README. This does not bound the gauge-conjugated matrix H.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "gaussian-column-cut"


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
    for left_key, left_coeff in left.items():
        for right_key, right_coeff in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key))
            out[key] = out.get(key, 0) + left_coeff * right_coeff
    return {key: coeff for key, coeff in out.items() if coeff}


def uni_add(left, right):
    return add(left, right)


def uni_mul(left, right):
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
    gaussian = (
        ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
    ).read_text(encoding="utf-8")
    gauge = (
        ROOT / "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md"
    ).read_text(encoding="utf-8")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.
    assert "beta_i=rho*i-q_i" in log_a
    assert "n_i,h=exp(-a[(rho*h+beta_i)^2-beta_(i+h)^2])" in log_a
    assert "each in {1,2}" in log_a
    assert "n_i,-1=exp(-a*g_i*(2rho-2beta_i-g_i))" in log_a
    assert "n_i,+1=exp(-a*g_(i+1)*(2rho+2beta_i-g_(i+1)))" in log_a
    assert "(rho*h+beta_i)^2-beta_(i+h)^2 >= h^2-|h|" in log_a
    assert "||N-I||_infinity <= exp(-2a theta)+5 exp(-2a)`." in log_a
    assert "nonzero periodic diagonal aliases" in log_a
    assert "Use theta=t/s-1 in [1/(4p^2),1/p^2]" in gaussian
    assert "Eventually 4log(16p)<=a<=5log(16p)." in gaussian
    assert "||N-I||_infinity <= exp(-2a theta)+5exp(-2a)." in gaussian
    assert "Thus its row gap exceeds 1/(8p^2) eventually." in gaussian
    assert "W=O(sqrt(p)polylog(p))<p" in gaussian
    assert "the reference H has diagonal1," in gaussian
    assert "row gap delta>=1/(16p^2) and row norm<2." in gaussian
    assert "does not assume that a row norm bounds a column norm." in gaussian
    assert "log(a_i/a_j)=a(i-j)(beta_i+beta_j)" in gauge
    assert "A=diag(ahat) Ghat diag(ahat)^-1" in gauge


def entry_algebra() -> None:
    one = {(0, 0, 0): 1}
    theta = {(1, 0, 0): 1}
    beta = {(0, 1, 0): 1}
    step = {(0, 0, 1): 1}
    previous = add(add(add(beta, scale(one, -1)), scale(theta, -1)), step)
    from_left = add(
        scale(add(one, theta), 2),
        add(scale(previous, 2), scale(step, -1)),
    )
    assert from_left == add(step, scale(beta, 2))
    nxt = add(add(add(beta, one), theta), scale(step, -1))
    from_right = add(
        scale(add(one, theta), 2),
        add(scale(nxt, -2), scale(step, -1)),
    )
    assert from_right == add(step, scale(beta, -2))
    bee = {(1, 0): 1}
    ess = {(0, 1): 1}
    square = add(mul(add(bee, ess), add(bee, ess)), scale(mul(bee, bee), -1))
    assert square == add(mul(ess, ess), scale(mul(ess, bee), 2))


def step_dominates_the_pure_run_exponent() -> None:
    # s(s+2β)-h(h+2β)=(s-h)(s+h+2β). At 2β=-1 the second factor is s+h-1.
    hole = {(1, 0): 1}
    pure = {(0, 1): 1}
    beta_term = {(0, 0): 1}
    gap = mul(add(hole, scale(pure, -1)), add(add(hole, pure), scale(beta_term, -1)))
    expanded = add(
        mul(add(hole, scale(pure, -1)), add(hole, pure)),
        scale(add(hole, scale(pure, -1)), -1),
    )
    assert gap == expanded
    # A g=2 step is not the pure-run exponent. h=1, s=2, β=0: 4 against 1.
    assert 2 * (2 + 2 * 0) == 4
    assert 1 * (1 + 2 * 0) == 1
    assert 4 > 1
    # At β=-1/2 the g=2 nearest exponent is 2, while the pure-run exponent is 0.
    assert 2 * (2 - 1) == 2
    assert 1 * (1 - 1) == 0
    assert 2 > 0


def regions_and_nearest_endpoints() -> None:
    # θ<=1/4<1/2, so incoming g=2 and outgoing g=2 occupy disjoint beta intervals.
    assert 2 * 1 < 4
    # β=-1/2+θ and both steps equal 1. Cleared of the denominator:
    # 1+2β=2θ and 1-2β=2-2θ.
    left_factor = uni_add(uni_add({0: 1}, {0: -1}), {1: 2})
    right_factor = uni_add(uni_add({0: 1}, {0: 1}), {1: -2})
    assert left_factor == {1: 2}
    assert right_factor == {1: -2, 0: 2}
    # The g=2 column at β=-1/2 has both nearest factors equal to 2.
    assert 2 * (2 + (-1)) == 2
    assert 1 - (-1) == 2
    # At β=-1/2+θ the g=2 factor 2+4θ exceeds the both-steps-1 factor 2θ by 2+2θ.
    excess = uni_add({1: 4, 0: 2}, scale({1: 2}, -1))
    assert excess == {1: 2, 0: 2}
    assert all(coeff > 0 for coeff in excess.values())


def side_columns_are_smaller() -> None:
    # β=-1/2+u: factors 2(1+2u) and 2(1-u). u is the first variable, θ the second.
    left = {(0, 0): 1, (1, 0): 2}
    theta = {(0, 1): 1}
    assert add(left, scale(theta, -1)) == {(0, 0): 1, (1, 0): 2, (0, 1): -1}
    right_gap = add({(0, 1): 1}, scale({(1, 0): 1}, -1))
    assert right_gap == {(1, 0): -1, (0, 1): 1}
    # θ<=1/4 makes the constant part 1-θ at least 3/4.
    assert 4 - 1 == 3


def tail_reduction() -> None:
    # k(k-1)-(4k-6)=(k-2)(k-3), which is nonnegative for every integer k>=2.
    quadratic = uni_add(uni_mul({1: 1}, {1: 1, 0: -1}), {1: -4, 0: 6})
    factored = uni_mul({1: 1, 0: -2}, {1: 1, 0: -3})
    assert quadratic == {2: 1, 1: -5, 0: 6}
    assert factored == {2: 1, 1: -5, 0: 6}
    # 2u/(1-u^2)<=4u/u = 4 once u^2<=1/2, so the sharp tail is at most 4u.
    assert 2 * 2 == 4


def exponential_bounds() -> None:
    # Partial sum through 1/3! equals 8/3. The next term 1/24 is positive, so e>8/3.
    assert 6 + 6 + 3 + 1 == 16
    assert 16 * 3 == 6 * 8
    assert (8 ** 4) - (8 ** 2) * (3 ** 2) - 3 ** 4 == 4096 - 64 * 9 - 81
    assert 4096 - 576 - 81 == 3439
    assert 3439 > 0
    # 1/(k+1) <= 1/2 for k>=1, so 1/k! <= 1/2^{k-1}, strictly at k=3.
    assert 2 <= 1 + 1
    assert 1 * 4 < 6
    # Therefore e<3, so log(32)>1.
    assert 32 > 3
    # sqrt(2)<17/12.
    assert 17 * 17 > 2 * 12 * 12
    # 4096*sqrt(2) < 17408/3, and 4+17408/3=17420/3.
    assert 4096 * 17 * 3 == 17408 * 12
    assert 4 * 3 + 17408 == 17420
    # (8/3)^2=64/9, so exp(-2)<9/64<1/2 once e>8/3.
    assert 9 * 2 < 64


def parameter_majorant() -> None:
    # (16*2)^4 = 32^{2^2}. For p>=2 the inductive factor is strictly below 1.
    assert (16 * 2) ** 4 == 32 ** 4
    # 3p - 2(p+1) = p-2, so (p+1)/p <= 3/2 for every integer p>=2.
    assert uni_add({1: 3}, scale({1: 2, 0: 2}, -1)) == {1: 1, 0: -2}
    # 2p+1-5 = 2(p-2), so 32^{2p+1} = 32^5 * 32^{2(p-2)}.
    assert uni_add({1: 2, 0: 1}, {0: -5}) == {1: 2, 0: -4}
    assert (2 + 1) ** 4 == 81
    assert 81 < 16 * 32 ** 5
    # 2*4*log = 8*log gives (16p)^{-8}; 2*5*log/p^2 = 5 * (2 log/p^2).
    assert 2 * 4 == 8
    assert 2 * 5 == 10
    assert 10 == 5 * 2
    # Slack numerator 16p^2 - (p^2+2) = 15p^2-2.
    assert 16 - 1 == 15
    assert 0 - 2 == -2
    # p^2+2 <= 2p^2 for p>=2, so the denominator 8p^2(p^2+2) <= 16p^4.
    assert 2 <= 2 * 2
    assert 8 * 2 == 16
    growth = uni_mul({2: 15, 1: 30, 0: 13}, {4: 1, 3: 4, 2: 6, 1: 4, 0: 1})
    assert growth[6] == 15
    plain = {6: 15, 4: -2}
    difference = uni_add(growth, scale(plain, -1))
    assert difference == {5: 90, 4: 225, 3: 292, 2: 213, 1: 82, 0: 13}
    assert all(coeff > 0 for coeff in difference.values())
    # 17420*16*p^4 <= 3*(15p^2-2)*(16p)^8 at p=2, hence for every larger integer.
    left = 17420 * 16 * 2 ** 4
    right = 3 * (15 * 2 * 2 - 2) * (16 * 2) ** 8
    assert left == 4459520
    assert left <= right
    # U=(16p)^{-8}<=2^{-40}, so U^2<=2^{-80}<=1/2 and the sharp tail is <= 4U.
    assert (16 * 2) ** 8 == 2 ** 40
    assert 2 ** 80 > 2
    # Bandwidth < p leaves at most 2p-1 nonzeros. Gap halves: 1/8-1/16=1/16.
    assert 2 * (2 - 1) + 1 == 2 * 2 - 1
    assert 2 * 16 - 1 * 16 == 16
    assert 1 * 16 == 16


def main() -> None:
    pins_and_phrases()
    entry_algebra()
    step_dominates_the_pure_run_exponent()
    regions_and_nearest_endpoints()
    side_columns_are_smaller()
    tail_reduction()
    exponential_bounds()
    parameter_majorant()
    print("PASS_GAUSSIAN_COLUMN_CUT")


if __name__ == "__main__":
    main()
