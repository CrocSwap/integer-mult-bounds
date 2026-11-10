"""Character exclusion for the seven-call profile (0,2,1,1)/(1,1,1).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The proof is PROOF.md. This file checks the polynomial identities, the
exhaustive mod-8 lemmas, the single-line parity lemma on a declared box,
and explicit characters on declared frames. The box is not the proof.
"""

from fractions import Fraction as F
from itertools import product
from math import gcd, lcm


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Poly:
    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for key, value in terms.items():
                if value:
                    self.terms[key] = value

    def add(self, other, scale=1):
        out = dict(self.terms)
        for key, value in other.terms.items():
            out[key] = out.get(key, 0) + scale * value
            if out[key] == 0:
                del out[key]
        return Poly(out)

    def mul(self, other):
        out = {}
        for left, lval in self.terms.items():
            for right, rval in other.terms.items():
                key = tuple(a + b for a, b in zip(left, right))
                out[key] = out.get(key, 0) + lval * rval
                if out[key] == 0:
                    del out[key]
        return Poly(out)


def var(index, width):
    exponents = [0] * width
    exponents[index] = 1
    return Poly({tuple(exponents): 1})


def const(value, width):
    if value == 0:
        return Poly()
    return Poly({tuple([0] * width): value})


def check_bracket_polynomial():
    """δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w) is the zero polynomial."""
    width = 6
    u1, u2, v1, v2, w1, w2 = (var(i, width) for i in range(width))
    three = const(3, width)

    def bilinear(x1, x2, y1, y2):
        return x1.mul(y1).add(three.mul(x2).mul(y2))

    def cross(x1, x2, y1, y2):
        return x1.mul(y2).add(x2.mul(y1), scale=-1)

    def quad(x1, x2):
        return x1.mul(x1).add(three.mul(x2).mul(x2))

    expression = (
        cross(u1, u2, w1, w2).mul(bilinear(u1, u2, v1, v2))
        .add(cross(u1, u2, v1, v2).mul(bilinear(u1, u2, w1, w2)), scale=-1)
        .add(quad(u1, u2).mul(cross(v1, v2, w1, w2)), scale=-1)
    )
    require(expression.terms == {}, "scale bracket polynomial is not identically zero")


def check_determinant_polynomial():
    """Closed form of the (w1,w2) coefficient determinant."""
    width = 8
    k, l, u1, u2, v1, v2, gee, hhh = (var(i, width) for i in range(width))
    two = const(2, width)
    six = const(6, width)
    three = const(3, width)
    row11 = two.mul(k).mul(u1).mul(v1).add(gee.mul(u2))
    row12 = six.mul(k).mul(u1).mul(v2).add(gee.mul(u1), scale=-1)
    row21 = two.mul(l).mul(u1).mul(v1).add(hhh.mul(v2))
    row22 = six.mul(l).mul(v1).mul(u2).add(hhh.mul(v1), scale=-1)
    matrix_det = row11.mul(row22).add(row12.mul(row21), scale=-1)
    delta = u1.mul(v2).add(u2.mul(v1), scale=-1)
    quad_u = u1.mul(u1).add(three.mul(u2).mul(u2))
    quad_v = v1.mul(v1).add(three.mul(v2).mul(v2))
    closed = (
        delta.mul(gee).mul(hhh)
        .add(two.mul(l).mul(gee).mul(v1).mul(quad_u))
        .add(two.mul(k).mul(hhh).mul(u1).mul(quad_v), scale=-1)
        .add(const(12, width).mul(k).mul(l).mul(u1).mul(v1).mul(delta), scale=-1)
    )
    require(matrix_det.terms == closed.terms, "determinant polynomial mismatch")


def check_lemma4():
    """Every eligible odd residue has αβ-γ^2 ≡ 2 or 6 (mod 8). Exhaustive."""
    odds = (1, 3, 5, 7)
    seen = 0
    for alpha in odds:
        for beta in odds:
            if (alpha + beta) % 4 != 0:
                continue
            for gamma in odds:
                seen += 1
                value = (alpha * beta - gamma * gamma) % 8
                require(value in (2, 6), "lemma 4 residue " + str((alpha, beta, gamma, value)))
    require(seen == 32, "expected 32 odd residue classes, found " + str(seen))


def check_axis_mod8():
    """2αk and αβ-γ^2 are each 2 or 6 mod 8, so their difference is not."""
    odds = (1, 3, 5, 7)
    for alpha in odds:
        for kay in odds:
            product = (2 * alpha * kay) % 8
            require(product in (2, 6), "2αk residue")
            for gap in (2, 6):
                difference = (gap - product) % 8
                require(difference in (0, 4), "axis difference residue")
            for second in odds:
                right = (6 * alpha * alpha * kay * second * second) % 8
                require(right in (2, 6), "axis right-hand residue")


def check_quadratic_valuations():
    """Diagonal q has 2-valuation 2; an axial primitive vector has odd q."""
    odds = (1, 3, 5, 7)
    for first in odds:
        for second in odds:
            square_sum = (first * first + 3 * second * second) % 8
            require(square_sum == 4, "diagonal quadratic residue")
    for u1, u2 in product(range(-12, 13), repeat=2):
        if gcd(abs(u1), abs(u2)) != 1:
            continue
        axial = (u1 % 2 == 0) ^ (u2 % 2 == 0)
        if not axial:
            continue
        value = u1 * u1 + 3 * u2 * u2
        require(value % 2 == 1, "axial quadratic parity " + str((u1, u2)))


def valuation_gap(v2_u1):
    constant = 1 + v2_u1
    l_term = 1 + (1 + v2_u1)  # v2(2) + v2(G), with q(u) and v1 odd
    k_term = 1 + v2_u1 + 2  # v2(2) + v2(u1) + v2(q(v))
    kl_term = 2 + v2_u1  # v2(12) + v2(u1)
    require(l_term > constant and k_term > constant and kl_term > constant,
            "valuation gap collapsed at " + str(v2_u1))


def check_valuation_gaps():
    for shift in range(0, 12):
        valuation_gap(shift)


def coeffs(direction, scale):
    first, second = direction
    scale = F(scale)
    return (
        scale * first * (first - second),
        scale * second * (second - first),
        2 * scale * first * second,
    )


def matrix_det(vector):
    first, second, off = vector
    return first * second + off * (first + second) / 2


def primitive_directions(bound):
    directions = []
    for first, second in product(range(-bound, bound + 1), repeat=2):
        if (first, second) == (0, 0):
            continue
        if second < 0 or (second == 0 and first < 0):
            continue
        if gcd(abs(first), abs(second)) != 1:
            continue
        directions.append((first, second))
    return directions


def check_single_line_box():
    """Corroborate the single-line lemma on a finite box. Not the proof."""
    checked = 0
    for direction in primitive_directions(12):
        first, second = direction
        diagonal = first % 2 == 1 and second % 2 == 1
        axial = (first % 2 == 0) ^ (second % 2 == 0)
        require(diagonal or axial, "primitive vector is axial or diagonal")
        for numerator in range(-12, 13):
            if numerator == 0:
                continue
            for denominator in range(1, 13):
                scale = F(numerator, denominator)
                vector = coeffs(direction, scale)
                if any(entry.denominator != 1 for entry in vector):
                    continue
                checked += 1
                parity_ab = (vector[0] + vector[1]) % 2
                parity_pq = vector[2] % 2
                require((parity_ab, parity_pq) != (1, 1), "single line hit (1,1)")
                if diagonal:
                    require(parity_ab == 0, "diagonal line has odd a+b")
                if axial:
                    require(parity_pq == 0, "axial line has odd c")
                    require(scale.denominator == 1, "axial integral scale is not integral")
    require(checked > 100, "single-line box checked too little")


def bilinear(left, right):
    return F(left[0] * right[0] + 3 * left[1] * right[1])


def cross(left, right):
    return F(left[0] * right[1] - left[1] * right[0])


def solve_scales(first, second, third):
    return (
        bilinear(second, third) / (cross(first, second) * cross(first, third)),
        bilinear(third, first) / (cross(second, third) * cross(second, first)),
        bilinear(first, second) / (cross(third, first) * cross(third, second)),
    )


def parity_image(left, right):
    modulus = 1
    for entry in left + right:
        modulus = lcm(modulus, entry.denominator)
    require(modulus <= 48, "fixture denominator too large for the direct image")
    left_int = [int(entry * modulus) for entry in left]
    right_int = [int(entry * modulus) for entry in right]
    seen = set()
    span = 2 * modulus
    for coef_l in range(span):
        for coef_r in range(span):
            combined = [coef_l * left_int[i] + coef_r * right_int[i] for i in range(3)]
            if any(entry % modulus != 0 for entry in combined):
                continue
            reduced = tuple((entry // modulus) % 2 for entry in combined)
            seen.add(((reduced[0] + reduced[1]) & 1, reduced[2]))
    require(seen, "empty parity image")
    return seen


def form_value(family, shift, vector):
    first, second, off = vector
    p_shift, s_shift, t_shift = shift
    if family == "AB":
        return (1 + 2 * p_shift) * first + (1 + 2 * s_shift) * second + (2 * t_shift) * off
    return (2 * p_shift) * first + (2 * s_shift) * second + (1 + 2 * t_shift) * off


def even_integer(value):
    return value.denominator == 1 and value.numerator % 2 == 0


def odd_integer(value):
    return value.denominator == 1 and value.numerator % 2 == 1


def find_extension(family, frames):
    modulus = 2
    for vector in frames:
        for entry in vector:
            modulus = lcm(modulus, entry.denominator)
    require(modulus <= 18, "extension search modulus too large")
    for shift in product(range(modulus), repeat=3):
        if all(even_integer(form_value(family, shift, vector)) for vector in frames):
            return shift
    return None


A = (F(1), F(0), F(0))
B = (F(0), F(1), F(0))
P = (F(0), F(0), F(1))
Q = (F(1), F(1), F(-1))
H = (F(3), F(1), F(0))
TARGETS = (
    (F(1), F(0), F(1)),   # A+P
    (F(2), F(1), F(-1)),  # A+Q
    (F(0), F(1), F(1)),   # B+P
    (F(1), F(2), F(-1)),  # B+Q
)
CALLS = (
    (0, A),
    (2, B),
    (1, P),
    (1, Q),
)


def detected_counts(family, shift, frames):
    calls = 0
    for multiplicity, vector in CALLS:
        if odd_integer(form_value(family, shift, vector)):
            calls += multiplicity
    for vector in frames:
        if odd_integer(form_value(family, shift, vector)):
            calls += 1
    targets = sum(1 for vector in TARGETS if odd_integer(form_value(family, shift, vector)))
    return calls, targets


def check_solution(frames, label):
    require(len(frames) == 3, label)
    total = tuple(sum(frame[i] for frame in frames) for i in range(3))
    require(total == H, label + " does not solve R+S+T=3A+B")
    for frame in frames:
        require(frame != (F(0), F(0), F(0)), label + " has a zero frame")
        require(matrix_det(frame) == 0, label + " frame is not rank one")
    image = parity_image(frames[0], frames[1])
    require((1, 1) not in image, label + " parity image contains (1,1)")
    vanished = []
    if all(bit[0] == 0 for bit in image):
        vanished.append("AB")
    if all(bit[1] == 0 for bit in image):
        vanished.append("PQ")
    require(vanished, label + " loses both coordinate functionals")
    for family in ("AB", "PQ"):
        shift = find_extension(family, frames)
        if family in vanished:
            require(shift is not None, label + " missing " + family + " extension")
            require(even_integer(form_value(family, shift, H)), label + " residual not even")
            calls, targets = detected_counts(family, shift, frames)
            require(calls == 2 and targets == 4,
                    label + " " + family + " detects " + str((calls, targets)))
        else:
            require(shift is None, label + " " + family + " extended without vanishing")


def explicit_frames():
    solutions = []
    # Integral nonparallel: 2A + P + Q = 3A+B.
    solutions.append((
        "integral-nonparallel",
        (coeffs((1, 0), 2), coeffs((1, 1), F(1, 2)), coeffs((1, -1), F(1, 2))),
    ))
    # Negative third frame: 5A + 2 vv^T - ww^T.
    directions = ((1, 0), (1, 1), (2, 1))
    scales = solve_scales(*directions)
    solutions.append(("negative-frame", tuple(coeffs(direction, scale)
                                              for direction, scale in zip(directions, scales))))
    # Denominator in the coefficient vector.
    directions = ((2, 1), (1, 1), (1, -1))
    scales = solve_scales(*directions)
    solutions.append(("fractional-frame", tuple(coeffs(direction, scale)
                                                for direction, scale in zip(directions, scales))))
    # Parallel opposite scales on A, with T = B.
    solutions.append(("parallel-negative", (coeffs((1, 0), 4), coeffs((1, 0), -1), B)))
    # One added label equal to the old matrix B.
    solutions.append(("old-label-duplicate", (B, A, coeffs((1, 0), 2))))
    return solutions


def check_failures():
    good = explicit_frames()[0][1]
    tampered = (good[0], good[1], tuple(good[2][i] + A[i] for i in range(3)))
    total = tuple(sum(frame[i] for frame in tampered) for i in range(3))
    require(total != H, "tampered sum still equals the residual")
    require(matrix_det((F(1), F(1), F(0))) != 0, "I was accepted as rank one")
    identity = (F(1), F(1), F(0))
    require(matrix_det(identity) == 1, "det I changed")
    # (2a+2b+2c) is even on A, B and P, so it is neither the AB nor the PQ shape.
    def even_form(vector):
        return 2 * vector[0] + 2 * vector[1] + 2 * vector[2]
    require(even_integer(even_form(A)) and even_integer(even_form(B))
            and even_integer(even_form(P)),
            "even-even-even form was not rejected by shape")


def main():
    check_bracket_polynomial()
    check_determinant_polynomial()
    check_lemma4()
    check_axis_mod8()
    check_quadratic_valuations()
    check_valuation_gaps()
    check_single_line_box()
    labels = []
    for label, frames in explicit_frames():
        check_solution(frames, label)
        labels.append(label)
    require(labels == [
        "integral-nonparallel",
        "negative-frame",
        "fractional-frame",
        "parallel-negative",
        "old-label-duplicate",
    ], "fixture list changed")
    check_failures()
    print("PASS three-signed-b-twice character checks")


if __name__ == "__main__":
    main()
