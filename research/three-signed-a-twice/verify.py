"""Character exclusion for the seven-call profile (2,0,1,1)/(1,1,1).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The proof is PROOF.md. This file checks the polynomial identities, the
exhaustive mod-8 lemmas, the axis-reduction box, the single-line parity
lemma on a declared box, and explicit characters on declared frames.
The boxes are not the proof.
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
    """δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w) is the zero polynomial.

    B(x,y) = 3 x1 y1 + x2 y2 and q(x) = 3 x1^2 + x2^2. These belong to
    the residual diag(1,3), not to diag(3,1).
    """
    width = 6
    u1, u2, v1, v2, w1, w2 = (var(i, width) for i in range(width))
    three = const(3, width)

    def bilinear(x1, x2, y1, y2):
        return three.mul(x1).mul(y1).add(x2.mul(y2))

    def cross(x1, x2, y1, y2):
        return x1.mul(y2).add(x2.mul(y1), scale=-1)

    def quad(x1, x2):
        return three.mul(x1).mul(x1).add(x2.mul(x2))

    expression = (
        cross(u1, u2, w1, w2).mul(bilinear(u1, u2, v1, v2))
        .add(cross(u1, u2, v1, v2).mul(bilinear(u1, u2, w1, w2)), scale=-1)
        .add(quad(u1, u2).mul(cross(v1, v2, w1, w2)), scale=-1)
    )
    require(expression.terms == {}, "scale bracket polynomial is not identically zero")


def check_determinant_polynomial():
    """Closed form of the (w1,w2) coefficient determinant for this residual."""
    width = 8
    kay, ell, u1, u2, v1, v2, gee, hhh = (var(i, width) for i in range(width))
    two = const(2, width)
    six = const(6, width)
    three = const(3, width)
    row11 = six.mul(kay).mul(u1).mul(v1).add(gee.mul(u2))
    row12 = two.mul(kay).mul(u1).mul(v2).add(gee.mul(u1), scale=-1)
    row21 = six.mul(ell).mul(u1).mul(v1).add(hhh.mul(v2))
    row22 = two.mul(ell).mul(v1).mul(u2).add(hhh.mul(v1), scale=-1)
    matrix_det = row11.mul(row22).add(row12.mul(row21), scale=-1)
    delta = u1.mul(v2).add(u2.mul(v1), scale=-1)
    quad_u = three.mul(u1).mul(u1).add(u2.mul(u2))
    quad_v = three.mul(v1).mul(v1).add(v2.mul(v2))
    closed = (
        delta.mul(gee).mul(hhh)
        .add(two.mul(ell).mul(gee).mul(v1).mul(quad_u))
        .add(two.mul(kay).mul(hhh).mul(u1).mul(quad_v), scale=-1)
        .add(const(12, width).mul(kay).mul(ell).mul(u1).mul(v1).mul(delta), scale=-1)
    )
    require(matrix_det.terms == closed.terms, "determinant polynomial mismatch")


def check_axis_rearrangement():
    """The cleared axis equation is the scale condition, as polynomials.

    With D = α-2l and c_u = 3 + α v2^2 / (v1^2 D), the condition
    k c_u = (αβ-γ^2)/(2α) rearranges to
    (α-2l) v1^2 (αβ-γ^2 - 6α k) = 2 α^2 k v2^2.
    """
    width = 7
    alpha, beta, gamma, kay, ell, vv1, vv2 = (var(i, width) for i in range(width))
    two = const(2, width)
    three = const(3, width)
    six = const(6, width)
    gap = alpha.add(two.mul(ell), scale=-1)
    v1sq = vv1.mul(vv1)
    v2sq = vv2.mul(vv2)
    discriminant = alpha.mul(beta).add(gamma.mul(gamma), scale=-1)
    scale_condition = two.mul(alpha).mul(kay).mul(
        three.mul(v1sq).mul(gap).add(alpha.mul(v2sq))
    ).add(discriminant.mul(v1sq).mul(gap), scale=-1)
    displayed = gap.mul(v1sq).mul(
        discriminant.add(six.mul(alpha).mul(kay), scale=-1)
    ).add(two.mul(alpha).mul(alpha).mul(kay).mul(v2sq), scale=-1)
    require(scale_condition.add(displayed).terms == {},
            "axis rearrangement is not an identity")


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
    """6αk and the right-hand side are 2 or 6 mod 8 when every factor is odd."""
    odds = (1, 3, 5, 7)
    for alpha in odds:
        for kay in odds:
            product = (6 * alpha * kay) % 8
            require(product in (2, 6), "6αk residue")
            for gap in (2, 6):
                difference = (gap - product) % 8
                require(difference in (0, 4), "axis difference residue")
            for second in odds:
                right = (2 * alpha * alpha * kay * second * second) % 8
                require(right in (2, 6), "axis right-hand residue")
        for ell in range(8):
            require((alpha - 2 * ell) % 2 == 1, "α-2l became even")


def check_quadratic_valuations():
    """Diagonal q ≡ 4 (mod 8); an axial primitive vector has odd q."""
    odds = (1, 3, 5, 7)
    for first in odds:
        for second in odds:
            square_sum = (3 * first * first + second * second) % 8
            require(square_sum == 4, "diagonal quadratic residue")
    for u1, u2 in product(range(-12, 13), repeat=2):
        if gcd(abs(u1), abs(u2)) != 1:
            continue
        axial = (u1 % 2 == 0) ^ (u2 % 2 == 0)
        if not axial:
            continue
        value = 3 * u1 * u1 + u2 * u2
        require(value % 2 == 1, "axial quadratic parity " + str((u1, u2)))
        require(value != 0, "axial quadratic vanished")


def valuation_gap(shift, orientation):
    """Lower bounds used in Section 6 are strictly above the constant term."""
    if orientation == "axial-diagonal":
        constant = 1 + shift
        l_term = 2 + shift
        k_term = 3 + shift
        kl_term = 2 + shift
    elif orientation == "diagonal-axial":
        constant = 1 + shift
        l_term = 3 + shift
        k_term = 2 + shift
        kl_term = 2 + shift
    else:
        raise ValueError("unknown orientation")
    require(l_term > constant and k_term > constant and kl_term > constant,
            "valuation gap collapsed at " + orientation + " " + str(shift))


def check_valuation_gaps():
    for shift in range(0, 12):
        valuation_gap(shift, "axial-diagonal")
        valuation_gap(shift, "diagonal-axial")


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


def bilinear(left, right):
    return F(3 * left[0] * right[0] + left[1] * right[1])


def old_bilinear(left, right):
    return F(left[0] * right[0] + 3 * left[1] * right[1])


def cross(left, right):
    return F(left[0] * right[1] - left[1] * right[0])


def solve_scales(first, second, third, form=bilinear):
    return (
        form(second, third) / (cross(first, second) * cross(first, third)),
        form(third, first) / (cross(second, third) * cross(second, first)),
        form(first, second) / (cross(third, first) * cross(third, second)),
    )


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


def check_axis_reduction_box():
    """On a finite box, the u1=0 scale formulas match the general formula."""
    checked = 0
    for sign in (1, -1):
        vertical = (0, sign)
        for left in primitive_directions(8):
            if left[0] == 0:
                continue
            for right in primitive_directions(8):
                if right[0] == 0 or cross(left, right) == 0:
                    continue
                if cross(vertical, left) == 0 or cross(vertical, right) == 0:
                    continue
                scales = solve_scales(vertical, left, right)
                reduced_u = 3 + F(left[1] * right[1], left[0] * right[0])
                reduced_v = F(right[1], cross(left, right) * left[0])
                require(scales[0] == reduced_u, "axis c_u reduction " + str((left, right, sign)))
                require(scales[1] == reduced_v, "axis c_v reduction " + str((left, right, sign)))
                checked += 1
    require(checked > 100, "axis-reduction box checked too little")


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
    modulus *= 2
    require(modulus <= 36, "extension search modulus too large")
    for shift in product(range(modulus), repeat=3):
        if all(even_integer(form_value(family, shift, vector)) for vector in frames):
            return shift
    return None


A = (F(1), F(0), F(0))
B = (F(0), F(1), F(0))
P = (F(0), F(0), F(1))
Q = (F(1), F(1), F(-1))
H = (F(1), F(3), F(0))
OLD_H = (F(3), F(1), F(0))
TARGETS = (
    (F(1), F(0), F(1)),    # A+P
    (F(2), F(1), F(-1)),   # A+Q
    (F(0), F(1), F(1)),    # B+P
    (F(1), F(2), F(-1)),   # B+Q
)
CALLS = (
    (2, A),
    (0, B),
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
    require(total == H, label + " does not solve R+S+T=A+3B")
    require(total != OLD_H, label + " solved the sibling residual instead")
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
    # One rational solution named by the question: 2B + P + Q = A+3B.
    solutions.append((
        "rational-rank-one",
        (coeffs((0, 1), 2), coeffs((1, 1), F(1, 2)), coeffs((1, -1), F(1, 2))),
    ))
    directions = ((1, 0), (1, 1), (2, 1))
    scales = solve_scales(*directions)
    solutions.append(("negative-frame", tuple(coeffs(direction, scale)
                                              for direction, scale in zip(directions, scales))))
    directions = ((2, 1), (1, 1), (1, -1))
    scales = solve_scales(*directions)
    solutions.append(("fractional-frame", tuple(coeffs(direction, scale)
                                                for direction, scale in zip(directions, scales))))
    # Parallel opposite scales on B, with the third frame equal to A.
    solutions.append(("parallel-negative", (coeffs((0, 1), 4), coeffs((0, 1), -1), A)))
    # One added label equal to the old matrix A.
    solutions.append(("old-label-duplicate", (A, B, coeffs((0, 1), 2))))
    return solutions


def check_label_counts():
    """Every integer shift detects two old calls and four targets, before frames."""
    for shift in product(range(4), repeat=3):
        for family, expected in (("AB", 2), ("PQ", 2)):
            calls, targets = detected_counts(family, shift, ())
            require(calls == expected and targets == 4,
                    "old-label count " + family + " " + str((shift, calls, targets)))
            require(even_integer(form_value(family, shift, H)),
                    "residual parity depends on the shift")


def check_failures():
    good = explicit_frames()[0][1]
    tampered = (good[0], good[1], tuple(good[2][i] + A[i] for i in range(3)))
    total = tuple(sum(frame[i] for frame in tampered) for i in range(3))
    require(total != H, "tampered sum still equals the residual")
    require(matrix_det((F(1), F(1), F(0))) != 0, "I was accepted as rank one")
    identity = (F(1), F(1), F(0))
    require(matrix_det(identity) == 1, "det I changed")

    def even_form(vector):
        return 2 * vector[0] + 2 * vector[1] + 2 * vector[2]

    require(even_integer(even_form(A)) and even_integer(even_form(B))
            and even_integer(even_form(P)),
            "even-even-even form was not rejected by shape")
    directions = ((1, 0), (1, 1), (2, 1))
    old_scales = solve_scales(*directions, form=old_bilinear)
    old_frames = tuple(coeffs(direction, scale)
                       for direction, scale in zip(directions, old_scales))
    old_total = tuple(sum(frame[i] for frame in old_frames) for i in range(3))
    require(old_total == OLD_H, "old bilinear form stopped solving diag(3,1)")
    require(old_total != H, "old bilinear form solved this residual")


def main():
    check_bracket_polynomial()
    check_determinant_polynomial()
    check_axis_rearrangement()
    check_lemma4()
    check_axis_mod8()
    check_quadratic_valuations()
    check_valuation_gaps()
    check_single_line_box()
    check_axis_reduction_box()
    check_label_counts()
    labels = []
    for label, frames in explicit_frames():
        check_solution(frames, label)
        labels.append(label)
    require(labels == [
        "rational-rank-one",
        "negative-frame",
        "fractional-frame",
        "parallel-negative",
        "old-label-duplicate",
    ], "fixture list changed")
    check_failures()
    print("PASS three-signed-a-twice character checks")


if __name__ == "__main__":
    main()
