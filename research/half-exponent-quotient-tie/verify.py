#!/usr/bin/env python3
"""Exact algebraic checks for the t=1/2 adjacent-quotient tie.

The written argument is PROOF.md. This program checks the rational-function
identities that the proof differentiates and clears. It does not sample a
grid of exponents and does not claim a general-t theorem.
"""
from fractions import Fraction

PASS = "PASS_HALF_EXPONENT_QUOTIENT_TIE"


def clean(poly):
    out = {}
    for u_pow, coeffs in poly.items():
        kept = {s_pow: coeff for s_pow, coeff in coeffs.items() if coeff}
        if kept:
            out[u_pow] = kept
    return out


def term(coeff, sigma_pow, u_pow):
    return {u_pow: {sigma_pow: coeff}}


def add(*parts):
    out = {}
    for poly in parts:
        for u_pow, coeffs in poly.items():
            slot = out.setdefault(u_pow, {})
            for s_pow, coeff in coeffs.items():
                slot[s_pow] = slot.get(s_pow, 0) + coeff
    return clean(out)


def scale(poly, factor):
    return clean({
        u_pow: {s_pow: coeff * factor for s_pow, coeff in coeffs.items()}
        for u_pow, coeffs in poly.items()
    })


def mul(left, right):
    out = {}
    for u_pow, coeffs in left.items():
        for s_pow, coeff in coeffs.items():
            for v_pow, other in right.items():
                slot = out.setdefault(u_pow + v_pow, {})
                for t_pow, extra in other.items():
                    key = s_pow + t_pow
                    slot[key] = slot.get(key, 0) + coeff * extra
    return clean(out)


def deriv_u(poly):
    out = {}
    for u_pow, coeffs in poly.items():
        if u_pow == 0:
            continue
        out[u_pow - 1] = {s_pow: coeff * u_pow for s_pow, coeff in coeffs.items()}
    return clean(out)


def is_zero(poly):
    return clean(poly) == {}


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def rational_derivative(num, den):
    return (
        add(mul(deriv_u(num), den), scale(mul(num, deriv_u(den)), -1)),
        mul(den, den),
    )


def same_rational(num, den, expected_num, expected_den):
    return is_zero(add(
        mul(num, expected_den),
        scale(mul(expected_num, den), -1),
    ))


SIGMA = term(1, 1, 0)
ONE = term(1, 0, 0)
U = term(1, 0, 1)


def main():
    # q(u) = (2σ-1) u^2 (2σ+1-4σ u) / (2σ u - 1)^2
    linear = add(scale(SIGMA, 2), ONE)          # 2σ+1
    slope = scale(mul(SIGMA, U), 4)             # 4σ u
    q_num = mul(mul(add(scale(SIGMA, 2), scale(ONE, -1)), mul(U, U)), add(linear, scale(slope, -1)))
    den1 = add(scale(mul(SIGMA, U), 2), scale(ONE, -1))  # 2σ u - 1
    q_den = mul(den1, den1)
    v_num = mul(mul(scale(SIGMA, 2), U), add(ONE, scale(U, -1)))

    cleared_curve = add(mul(v_num, v_num), scale(mul(mul(U, U), q_den), -1), scale(q_num, -1))
    require(is_zero(cleared_curve), "explicit q(u) is not v^2 - u^2")

    # H cleared by u (2σ u - 1)^2:
    # q_num + (1-2σ) u^2 den + -2σ u q_num + (2σ-1) v_num u den1
    h_cleared = add(
        q_num,
        mul(mul(add(ONE, scale(SIGMA, -2)), mul(U, U)), q_den),
        scale(mul(mul(scale(SIGMA, 2), U), q_num), -1),
        mul(mul(add(scale(SIGMA, 2), scale(ONE, -1)), v_num), mul(U, den1)),
    )
    require(is_zero(h_cleared), "explicit curve does not satisfy H = 0")
    # A sign error in the quotient formula must fail the same identity.
    require(not is_zero(add(h_cleared, ONE)), "rejection control was identically zero")

    q_prime_num, q_prime_den = rational_derivative(q_num, q_den)
    expected_prime_num = scale(
        mul(mul(scale(U, -2), add(scale(SIGMA, 2), scale(ONE, -1))),
            add(mul(mul(scale(SIGMA, 4), mul(U, U)), SIGMA),
                scale(mul(SIGMA, U), -6),
                scale(SIGMA, 2),
                ONE)),
        1,
    )
    expected_prime_den = mul(q_den, den1)  # (2σ u - 1)^3
    require(same_rational(q_prime_num, q_prime_den, expected_prime_num, expected_prime_den),
            "q' numerator does not match the factored form")

    q_second_num, q_second_den = rational_derivative(q_prime_num, q_prime_den)
    quadratic_factor = add(
        mul(mul(scale(SIGMA, 8), SIGMA), U),
        scale(mul(SIGMA, U), -8),
        scale(SIGMA, 2),
        ONE,
    )
    expected_second_num = mul(scale(add(scale(SIGMA, 2), scale(ONE, -1)), 2), quadratic_factor)
    expected_second_den = mul(q_den, q_den)  # (2σ u - 1)^4
    require(same_rational(q_second_num, q_second_den, expected_second_num, expected_second_den),
            "q'' numerator does not match the factored form")

    rewritten = add(mul(mul(scale(SIGMA, 8), add(SIGMA, scale(ONE, -1))), U), scale(SIGMA, 2), ONE)
    require(is_zero(add(quadratic_factor, scale(rewritten, -1))),
            "positive rewriting of q'' numerator failed")

    discriminant = add(
        scale(mul(SIGMA, SIGMA), 36),
        scale(mul(mul(SIGMA, SIGMA), add(scale(SIGMA, 2), ONE)), -16),
        scale(mul(mul(SIGMA, SIGMA), add(scale(ONE, 5), scale(SIGMA, -8))), -4),
    )
    require(is_zero(discriminant), "discriminant identity 4σ^2(5-8σ) failed")

    # Rational point on the peak of σ = 3/2: ζ(2) = 3/2 and u = 1/2, so q = 2.
    sigma = Fraction(3, 2)
    u = Fraction(1, 2)
    q = (2 * sigma - 1) * u * u * (2 * sigma + 1 - 4 * sigma * u) / (2 * sigma * u - 1) ** 2
    require(q == 2, "peak check q(1/2) at σ=3/2 is not 2")
    v = 2 * sigma * u * (1 - u) / (2 * sigma * u - 1)
    require(v * v - u * u == q, "peak check lost v^2 = q + u^2")
    require((v + u - 1) * 2 * u * sigma == v, "peak check lost the stationarity relation")

    def eval_poly(poly, sigma_value, u_value):
        total = 0
        for u_pow, coeffs in poly.items():
            for s_pow, coeff in coeffs.items():
                total += coeff * sigma_value ** s_pow * u_value ** u_pow
        return total

    q_prime = eval_poly(expected_prime_num, sigma, u) / eval_poly(expected_prime_den, sigma, u)
    q_second = eval_poly(expected_second_num, sigma, u) / eval_poly(expected_second_den, sigma, u)
    require(q_prime < 0 and q_second > 0, "peak derivatives have the wrong sign")
    print(PASS)


if __name__ == "__main__":
    main()
