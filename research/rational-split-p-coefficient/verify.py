#!/usr/bin/env python3
"""Checks for the rational-splitting character obstruction.

PROOF.md holds the argument. This program checks the closed forms, the
displayed t=2 residue census, the mod-2 absence of character (1,1), and the
small-multiset half of the ten-call count. The coordinate box is a finite
control of those identities, not a census of directions.
"""

from fractions import Fraction
from itertools import product
from math import gcd


BOUND = 24
BOX_COUNT = 1440

A = (Fraction(1), Fraction(0), Fraction(0))
B = (Fraction(0), Fraction(1), Fraction(0))
P = (Fraction(0), Fraction(0), Fraction(1))
Q = (Fraction(1), Fraction(1), Fraction(-1))
TWO_I = (Fraction(2), Fraction(2), Fraction(0))
FOUR_I = (Fraction(4), Fraction(4), Fraction(0))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def add(left, right):
    return tuple(left[i] + right[i] for i in range(3))


def scale(frame, factor):
    return tuple(factor * value for value in frame)


def sub(left, right):
    return add(left, scale(right, -1))


def quadric(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def determinant(frame):
    a, b, c = frame
    return a * b + c * (a + b) / 2


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and quadric(frame) == 0


def targets():
    return (add(A, P), add(A, Q), add(B, P), add(B, Q))


def splitting(u1, u2):
    require(gcd(u1, u2) == 1, "direction is not primitive")
    n = u1 * u1 + u2 * u2
    require(n % 4 in (1, 2), "primitive square-length is divisible by 4")
    factor = Fraction(2, n)
    frame = (
        factor * u1 * (u1 - u2),
        factor * u2 * (u2 - u1),
        factor * 2 * u1 * u2,
    )
    partner = splitting_unchecked(-u2, u1)
    return n, frame, partner


def splitting_unchecked(u1, u2):
    n = u1 * u1 + u2 * u2
    factor = Fraction(2, n)
    return (
        factor * u1 * (u1 - u2),
        factor * u2 * (u2 - u1),
        factor * 2 * u1 * u2,
    )


def multiplier(n):
    require(n % 4 in (1, 2), "multiplier on a bad square-length")
    return n if n % 2 else n // 2


def odd(value):
    require(value.denominator == 1, "parity of a non-integral value")
    return int(value) % 2


def evaluate(kind, multiplier_value, frame):
    if kind == "PQ":
        return multiplier_value * frame[2]
    return multiplier_value * (frame[0] + frame[1])


def target_identities():
    rows = targets()
    require(add(add(rows[0], rows[1]), add(rows[2], rows[3])) == FOUR_I,
            "the four targets do not sum to 4I")
    for row in rows:
        require(trace(row) == 2, "a target trace is not 2")
        require(determinant(row) == Fraction(1, 2), "a target determinant is not 1/2")
        require(odd(row[0] + row[1]) == 1 and odd(row[2]) == 1,
                "a target misses a character bit")


def closed_values(u1, u2):
    n = u1 * u1 + u2 * u2
    m = multiplier(n)
    if n % 2:
        pq = 4 * u1 * u2
        ab = 2 * (n - 2 * u1 * u2)
    else:
        pq = 2 * u1 * u2
        ab = n - 2 * u1 * u2
    require(m * 4 * u1 * u2 == pq * n, "PQ closed form disagrees with m c")
    require(2 * m * (n - 2 * u1 * u2) == ab * n, "AB closed form disagrees with m(a+b)")
    require(m % 2 == 1 and pq % 2 == 0 and ab % 2 == 0, "closed values are not odd-m and even")
    return m, pq, ab


def detection(kind, m, frames):
    calls = (A, B, P, Q, frames[0], frames[1])
    detected_calls = sum(odd(evaluate(kind, m, frame)) for frame in calls)
    detected_targets = sum(odd(evaluate(kind, m, row)) for row in targets())
    return detected_calls, detected_targets


def support(frame, partner):
    require(add(frame, partner) == TWO_I, "a splitting does not sum to 2I")
    require(rank_one_nonzero(frame) and rank_one_nonzero(partner),
            "a splitting summand is not nonzero rank one")
    require(trace(frame) == 2 and trace(partner) == 2, "a splitting trace is not 2")
    six = (A, B, P, Q, frame, partner)
    total = six[0]
    for label in six[1:]:
        total = add(total, label)
    require(total == FOUR_I, "the six labels do not sum to 4I")
    pairs = (add(A, P), add(A, Q), add(B, P), add(B, Q))
    require(set(pairs) == set(targets()), "the projector pairs are not the targets")
    five = add(add(add(A, P), Q), add(frame, partner))
    require(five == sub(FOUR_I, B), "the five added frames do not sum to 4I-B")


def one_direction(u1, u2):
    n, frame, partner = splitting(u1, u2)
    m, pq_value, ab_value = closed_values(u1, u2)
    support(frame, partner)
    require(evaluate("PQ", m, frame) == pq_value, "PQ value missed the closed form")
    require(evaluate("AB", m, frame) == ab_value, "AB value missed the closed form")
    if n % 4 == 2:
        for p_bit, s_bit, t_bit in product(range(4), repeat=3):
            kernel = (
                (1 + 2 * p_bit) * u1 * (u1 - u2)
                + (1 + 2 * s_bit) * u2 * (u2 - u1)
                + 4 * t_bit * u1 * u2
            )
            require(kernel % 4 == 0, "AB kernel is not divisible by 4")
    for kind in ("PQ", "AB"):
        calls, goals = detection(kind, m, (frame, partner))
        require(calls == 2 and goals == 4, kind + " count is not 2 against 4")
    cleared = scale(frame, m)
    require(all(value.denominator == 1 for value in cleared), "m X is not integral")
    # Character (1,1) makes the cleared quadric odd, so it cannot vanish.
    both_odd_classes = 0
    for a_bit, b_bit, c_bit in product((0, 1), repeat=3):
        if (a_bit + b_bit) % 2 == 0 or c_bit % 2 == 0:
            continue
        both_odd_classes += 1
        cleared_quadric = 2 * a_bit * b_bit + c_bit * ((a_bit + b_bit) % 2)
        require(cleared_quadric % 2 == 1, "a (1,1) class has even quadric")
    require(both_odd_classes == 2, "the (1,1) residue count changed")
    return n


def coordinate_box():
    checked = 0
    for u1 in range(-BOUND, BOUND + 1):
        for u2 in range(-BOUND, BOUND + 1):
            if gcd(u1, u2) != 1:
                continue
            one_direction(u1, u2)
            checked += 1
    require(checked == BOX_COUNT, "primitive box count " + str(checked))
    return checked


def displayed_frames():
    _n, frame, partner = splitting(1, 2)
    require(frame == (Fraction(-2, 5), Fraction(4, 5), Fraction(8, 5)),
            "t=2 frame changed")
    require(partner == (Fraction(12, 5), Fraction(6, 5), Fraction(-8, 5)),
            "t=2 partner changed")
    chart = (
        Fraction(2 * (1 - 2), 1 + 4),
        Fraction(2 * 2 * (2 - 1), 5),
        Fraction(4 * 2, 5),
    )
    require(frame == chart, "chart formula missed the displayed frame")
    pq_expected = {
        A: 0, B: 0, P: 5, Q: -5, frame: 8, partner: -8,
    }
    ab_expected = {
        A: 5, B: 5, P: 0, Q: 10, frame: 2, partner: 18,
    }
    for label, value in pq_expected.items():
        require(5 * label[2] == value, "displayed PQ value changed")
    for label, value in ab_expected.items():
        require(5 * (label[0] + label[1]) == value, "displayed AB value changed")
    support(frame, partner)


def period_steps():
    # A step of 5 in any coefficient changes an integral value by an even integer.
    require(-4 * 5 == -20 and (-20) % 5 == 0 and (-20 // 5) % 2 == 0, "PQ alpha period")
    require(8 * 5 == 40 and 40 % 5 == 0 and (40 // 5) % 2 == 0, "PQ beta period")
    require(16 * 5 == 80 and 80 % 5 == 0 and (80 // 5) % 2 == 0, "PQ tau period")
    require(-4 * 5 == -20 and (-20) % 5 == 0 and (-20 // 5) % 2 == 0, "AB p period")
    require(8 * 5 == 40 and 40 % 5 == 0 and (40 // 5) % 2 == 0, "AB s period")
    require(16 * 5 == 80 and 80 % 5 == 0 and (80 // 5) % 2 == 0, "AB t period")


def pq_numerator(alpha, beta, tau):
    return -4 * alpha + 8 * beta + 8 + 16 * tau


def ab_numerator(p, s, t):
    return -4 * p + 8 * s + 2 + 16 * t


def substituted_pq_identity():
    # tau = 2 - alpha - 3 beta + 5 k, expanded and compared with the even form.
    # numerator = -4a + 8b + 8 + 16*(2 - a - 3b + 5k) = -20a - 40b + 40 + 80k
    # 5*(-4a - 8b + 8 + 16k) = -20a - 40b + 40 + 80k
    got = {
        "alpha": -4 + 16 * (-1),
        "beta": 8 + 16 * (-3),
        "k": 16 * 5,
        "const": 8 + 16 * 2,
    }
    expected = {"alpha": 5 * -4, "beta": 5 * -8, "k": 5 * 16, "const": 5 * 8}
    require(got == expected, "PQ substitution identity failed")
    require(all(value % 2 == 0 for value in (-4, -8, 16, 8)), "PQ closed form is not even")


def residue_census():
    period_steps()
    substituted_pq_identity()
    pq_integral = 0
    ab_integral = 0
    for alpha, beta, tau in product(range(5), repeat=3):
        numerator = pq_numerator(alpha, beta, tau)
        if numerator % 5 == 0:
            pq_integral += 1
            value = numerator // 5
            require(value % 2 == 0, "a PQ residue is odd on the t=2 frame")
            partner = 4 * alpha + 4 * beta - value
            require(partner % 2 == 0, "a PQ residue is odd on the partner")
        reduced = (alpha + 3 * beta + tau + 3) % 5
        require((numerator % 5) == reduced, "PQ numerator reduction changed")
        require((reduced == 0) == (tau % 5 == (2 - alpha - 3 * beta) % 5),
                "PQ congruence missed a residue")
    for p, s, t in product(range(5), repeat=3):
        numerator = ab_numerator(p, s, t)
        if numerator % 5 == 0:
            ab_integral += 1
            value = numerator // 5
            require(value % 2 == 0, "an AB residue is odd on the t=2 frame")
            # f(2I) = 4(1+p+s), so the partner value is that minus f(X).
            partner = 4 * (1 + p + s) - value
            require(partner % 2 == 0, "an AB residue is odd on the partner")
    require(pq_integral == 25 and ab_integral == 25, "residue solution count changed")
    return pq_integral, ab_integral


def half_projector():
    y = (Fraction(0), Fraction(0), Fraction(1, 2))
    require(rank_one_nonzero(y), "P/2 is not rank one")
    for tau in range(6):
        require(((1 + 2 * tau) * y[2]).denominator != 1, "a PQ shape is integral on P/2")
    # The step in tau is 1, and the value at 0 is 1/2, so every integer tau misses.
    require((1 + 2 * 0) * y[2] == Fraction(1, 2), "PQ value on P/2 changed")
    require((1 + 2 * 1) * y[2] - (1 + 2 * 0) * y[2] == 1, "PQ step on P/2 changed")
    form = lambda frame: frame[0] + 3 * frame[1]  # p=0, s=1, t=0
    frame, partner = splitting(1, 2)[1:]
    labels = (A, B, P, Q, frame, partner, y, scale(y, -1))
    require(ab_numerator(0, 1, 0) % 5 == 0, "a+3b is not a t=2 AB lift")
    detected = []
    for label in labels:
        value = form(label)
        require(value.denominator == 1, "a+3b misses a length-8 label")
        if odd(value):
            detected.append(label)
    require(detected == [A, B], "a+3b does not detect exactly A and B")
    require(sum(odd(form(row)) for row in targets()) == 4, "a+3b misses a target")


def small_extra_multisets():
    characters = ((0, 0), (1, 0), (0, 1))
    repairs = []
    for length in (1, 2, 3):
        for multiset in product(characters, repeat=length):
            ab = sum(bit[0] for bit in multiset)
            pq = sum(bit[1] for bit in multiset)
            if ab >= 2 and pq >= 2 and ab % 2 == 0 and pq % 2 == 0:
                repairs.append(multiset)
    require(repairs == [], "a short character multiset repairs both counts")
    witness = ((1, 0), (1, 0), (0, 1), (0, 1))
    ab = sum(bit[0] for bit in witness)
    pq = sum(bit[1] for bit in witness)
    require(ab == 2 and pq == 2 and ab % 2 == 0 and pq % 2 == 0,
            "the size-4 witness does not repair the counts")


def failure_controls():
    require(determinant((1, 1, 0)) == 1, "det I changed")
    require(not rank_one_nonzero((1, 1, 0)), "I was accepted as rank one")
    require(not rank_one_nonzero((0, 0, 0)), "zero was accepted as rank one")
    frame = splitting(1, 2)[1]
    require((frame[2]).denominator != 1, "the raw c-coordinate of t=2 is integral")
    tampered = add(frame, A)
    partner = splitting(1, 2)[2]
    require(add(tampered, partner) != TWO_I, "adding A preserved the splitting")

    def nonprimitive():
        splitting(2, 2)

    try:
        nonprimitive()
    except SystemExit as exc:
        require(str(exc).startswith("FAIL:"), "non-primitive failure had no marker")
    else:
        raise SystemExit("FAIL: a non-primitive direction was accepted")
    # Integral splittings remain obstructions under the ordinary coefficient.
    for direction in ((1, 0), (1, 1)):
        n, old, old_partner = splitting(*direction)
        require(multiplier(n) == 1, "an integral splitting has a nontrivial multiplier")
        calls, goals = detection("PQ", 1, (old, old_partner))
        require(calls == 2 and goals == 4, "an integral splitting escaped the PQ count")


def main():
    target_identities()
    checked = coordinate_box()
    displayed_frames()
    pq_integral, ab_integral = residue_census()
    half_projector()
    small_extra_multisets()
    failure_controls()
    print(
        "PASS rational-split-p-coefficient"
        + " box=" + str(checked)
        + " pq_residues=" + str(pq_integral)
        + " ab_residues=" + str(ab_integral)
    )


if __name__ == "__main__":
    main()
