#!/usr/bin/env python3
"""Independent bounded checks of the odd-modulus three-cube construction.

No primary verifier, certificate, or predecessor implementation is imported.
Exact rational expansion, CRT, primitive integer lifts, Bezout frames, and
literal source restoration are checked separately.  These finite checks
corroborate the proof; they are not a proof of its universal quantifiers.
"""

from fractions import Fraction as F
from math import gcd
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cube(a, b):
    return (a**3, 3 * a * a * b, 3 * a * b * b, b**3)


def add_scaled(left, right, coefficient):
    return tuple(x + coefficient * y for x, y in zip(left, right))


def defect(arity):
    result = (-arity, 0, 0, 0)
    for i in range(arity):
        result = add_scaled(result, cube(1, i), 1)
    return result


def identities(arity):
    r = arity
    s = r * (r - 1) // 2
    at_three = (
        (F(-r * (r - 1) * (r + 13), 6 * (3 * r - 1)), F(1), F(0)),
        (F(r * (r * r - 1), 6 * (3 * r - 5)), F(1), F(1)),
        (F(16 * r * (r - 1) * (r - 2), 3 * (3 * r - 1) * (3 * r - 5)),
         F(1), F(3 * r - 1, 4)),
    )
    away_from_three = (
        (F(s, 9), F(3), F(r)),
        (F(-s, 9), F(3), F(r - 1)),
        (F(s * (3 * s - 1), 9), F(0), F(1)),
    )
    return at_three, away_from_three


def check_rational_identities(arity):
    expected = defect(arity)
    at_three, away = identities(arity)
    for terms in (at_three, away):
        result = (F(0),) * 4
        for weight, a, b in terms:
            require(weight != 0, "zero rational identity weight")
            result = add_scaled(result, cube(a, b), weight)
        require(result == expected, "rational cubic identity failed")
    for term in at_three:
        require(all(value.denominator % 3 for value in term), "nonintegral at 3")
    for term in away:
        for value in term:
            denominator = value.denominator
            while denominator % 3 == 0:
                denominator //= 3
            require(denominator == 1, "denominator has prime factor other than 3")


def residue(value, modulus):
    if modulus == 1:
        return 0
    require(gcd(value.denominator, modulus) == 1, "denominator not invertible")
    return value.numerator * pow(value.denominator, -1, modulus) % modulus


def crt(left, left_modulus, right, right_modulus):
    if left_modulus == 1:
        return right % right_modulus
    if right_modulus == 1:
        return left % left_modulus
    correction = (right - left) * pow(left_modulus, -1, right_modulus)
    return (left + left_modulus * (correction % right_modulus)) % (left_modulus * right_modulus)


def bezout(a, b):
    old_r, new_r = a, b
    old_s, new_s = 1, 0
    old_t, new_t = 0, 1
    while new_r:
        quotient = old_r // new_r
        old_r, new_r = new_r, old_r - quotient * new_r
        old_s, new_s = new_s, old_s - quotient * new_s
        old_t, new_t = new_t, old_t - quotient * new_t
    require(old_r == 1, "row is not primitive")
    return old_s, old_t


def primitive_frame(a, b, modulus):
    require(gcd(gcd(a, b), modulus) == 1, "row is not unimodular modulo m")
    if b == 0:
        b = modulus
    # A complete residue period suffices.  The proof supplies existence;
    # this independent finite implementation does not factor b.
    for k in range(b):
        lifted_a = a + k * modulus
        if gcd(lifted_a, b) == 1:
            s, t = bezout(lifted_a, b)
            frame = (lifted_a, b, -t, s)
            require(frame[0] * frame[3] - frame[1] * frame[2] == 1, "frame determinant")
            return frame
    raise ValueError("primitive integer lift not found")


def certificate(arity, modulus, reduce_fraction=residue):
    require(modulus > 1 and modulus % 2 == 1, "modulus must be odd and greater than one")
    a, b = 1, modulus
    while b % 3 == 0:
        a *= 3
        b //= 3
    first, second = identities(arity)
    terms = []
    for first_term, second_term in zip(first, second):
        combined = tuple(
            crt(reduce_fraction(x, a), a, reduce_fraction(y, b), b)
            for x, y in zip(first_term, second_term)
        )
        weight, u, v = combined
        frame = primitive_frame(u, v, modulus)
        require(frame[0] % modulus == u and frame[1] % modulus == v, "lift changed row residues")
        terms.append((weight, frame))
    return tuple(terms)


def apply_frame(a, b, frame):
    u, v, c, d = frame
    if isinstance(a, tuple):
        return add_scaled(tuple(u * x for x in a), b, v), add_scaled(tuple(c * x for x in a), b, d)
    return u * a + v * b, c * a + d * b


def inverse(frame):
    u, v, c, d = frame
    return d, -v, -c, u


def symbolic_program(arity, terms, skip_inverse=None):
    a, b, output = (1, 0), (0, 1), (0, 0, 0, 0)
    for _ in range(arity):
        output = add_scaled(output, cube(*a), 1)
        a = add_scaled(a, b, 1)
    a = add_scaled(a, b, -arity)
    for index, (weight, frame) in enumerate(terms):
        a, b = apply_frame(a, b, frame)
        output = add_scaled(output, cube(*a), -weight)
        if index != skip_inverse:
            a, b = apply_frame(a, b, inverse(frame))
    return a, b, output


def accept(arity, modulus, terms, skip_inverse=None):
    actual = (0, 0, 0, 0)
    for weight, frame in terms:
        u, v, c, d = frame
        require(u * d - v * c == 1, "frame is not determinant one")
        actual = add_scaled(actual, cube(u, v), weight)
    require(all((x - y) % modulus == 0 for x, y in zip(actual, defect(arity))), "modular identity failed")
    a, b, output = symbolic_program(arity, terms, skip_inverse)
    require(a == (1, 0) and b == (0, 1), "sources not restored exactly")
    require(all((x - y) % modulus == 0 for x, y in zip(output, (arity, 0, 0, 0))), "modular eager output failed")


def literal_program(arity, terms, a, b, y):
    for _ in range(arity):
        y += a**3
        a += b
    a -= arity * b
    for weight, frame in terms:
        a, b = apply_frame(a, b, frame)
        y -= weight * a**3
        a, b = apply_frame(a, b, inverse(frame))
    return a, b, y


def reject(label, callback):
    try:
        callback()
    except ValueError:
        return label
    raise ValueError(f"negative control accepted: {label}")


def wrong_inverse(value, modulus):
    if modulus == 1:
        return 0
    return value.numerator * value.denominator % modulus


def run_checks():
    arities = tuple(range(3, 65)) + (97, 128)
    moduli = (3, 9, 27, 81, 5, 7, 11, 23, 25, 49, 121, 529,
              15, 33, 69, 99, 207, 363, 1587, 2783, 29403)
    dirty_inputs = ((1, 0, 7), (0, 1, -3), (-2, 3, 19), (5, -4, -11))
    for arity in range(3, 129):
        check_rational_identities(arity)
    for arity in arities:
        for modulus in moduli:
            terms = certificate(arity, modulus)
            accept(arity, modulus, terms)
            for a, b, y in dirty_inputs:
                final_a, final_b, final_y = literal_program(arity, terms, a, b, y)
                require((final_a, final_b) == (a, b), "literal source restoration failed")
                require((final_y - y - arity * a**3) % modulus == 0, "literal modular output failed")

    terms = certificate(15, 33)
    controls = [
        reject("denominator used instead of its inverse", lambda: accept(15, 33, certificate(15, 33, wrong_inverse))),
        reject("omitted inverse source frame", lambda: accept(15, 33, terms, skip_inverse=2)),
        reject("wrong retained arity", lambda: accept(16, 33, terms)),
    ]
    a, b, y = 1, 1, 7
    final_a, final_b, final_y = literal_program(15, terms, a, b, y)
    exact_target = y + 15 * a**3
    require((final_a, final_b) == (a, b), "counterexample source restoration failed")
    require(final_y != exact_target, "counterexample unexpectedly gives exact equality")
    require((final_y - exact_target) % 33 == 0, "counterexample lacks modular equality")
    controls.append("modular equality distinguished from exact global equality")
    return {
        "status": "pass",
        "rational_identity_arities": [3, 128],
        "modular_arities": list(arities),
        "moduli": list(moduli),
        "symbolic_modular_certificates": len(arities) * len(moduli),
        "literal_dirty_runs": len(arities) * len(moduli) * len(dirty_inputs),
        "rejected_controls": controls,
        "not_an_exact_repair": {
            "arity": 15, "modulus": 33, "input_a_b_y": [a, b, y],
            "exact_target": exact_target, "actual_output": final_y,
            "difference": final_y - exact_target,
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
