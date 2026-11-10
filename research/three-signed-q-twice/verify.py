"""Character exclusion for the seven-call profile (1,1,0,2)/(1,1,1).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The proof is PROOF.md. This file checks the polynomial identities, the
exhaustive mod-8 discriminant lemma, the mod-4 axis obstruction, the
quadratic valuation of this residual, explicit characters on declared
frames, and failure controls. The finite boxes are not the proof.
"""

from fractions import Fraction as F
from itertools import product
from math import gcd


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

    def scale(self, factor):
        return Poly({key: factor * value for key, value in self.terms.items()})


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

    B(x,y) = 2 x1 y1 - x1 y2 - x2 y1 + 2 x2 y2 and
    q(x) = 2 x1^2 - 2 x1 x2 + 2 x2^2. These belong to the residual
    [[2,1],[1,2]], not to diag(1,3) or diag(3,1).
    """
    width = 6
    u1, u2, v1, v2, w1, w2 = (var(i, width) for i in range(width))
    two = const(2, width)

    def bilinear(x1, x2, y1, y2):
        return (
            two.mul(x1).mul(y1)
            .add(x1.mul(y2), scale=-1)
            .add(x2.mul(y1), scale=-1)
            .add(two.mul(x2).mul(y2))
        )

    def cross(x1, x2, y1, y2):
        return x1.mul(y2).add(x2.mul(y1), scale=-1)

    def quad(x1, x2):
        return (
            two.mul(x1).mul(x1)
            .add(two.mul(x1).mul(x2), scale=-1)
            .add(two.mul(x2).mul(x2))
        )

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

    def quad(x1, x2):
        return (
            two.mul(x1).mul(x1)
            .add(two.mul(x1).mul(x2), scale=-1)
            .add(two.mul(x2).mul(x2))
        )

    row11 = two.mul(kay).mul(u1).mul(two.mul(v1).add(v2, scale=-1)).add(gee.mul(u2))
    row12 = two.mul(kay).mul(u1).mul(two.mul(v2).add(v1, scale=-1)).add(gee.mul(u1), scale=-1)
    row21 = two.mul(ell).mul(v1).mul(two.mul(u1).add(u2, scale=-1)).add(hhh.mul(v2))
    row22 = two.mul(ell).mul(v1).mul(two.mul(u2).add(u1, scale=-1)).add(hhh.mul(v1), scale=-1)
    matrix_det = row11.mul(row22).add(row12.mul(row21), scale=-1)
    delta = u1.mul(v2).add(u2.mul(v1), scale=-1)
    closed = (
        delta.mul(gee).mul(hhh)
        .add(two.mul(ell).mul(gee).mul(v1).mul(quad(u1, u2)))
        .add(two.mul(kay).mul(hhh).mul(u1).mul(quad(v1, v2)), scale=-1)
        .add(const(12, width).mul(kay).mul(ell).mul(u1).mul(v1).mul(delta), scale=-1)
    )
    require(matrix_det.terms == closed.terms, "determinant polynomial mismatch")


def check_axis_numerator():
    """Clearing w from the vertical scale formulas gives the displayed numerator.

    c_u = 2(-α Q + 3 l v1^2) / (v1^2 (4l-α)), with Q = v1^2 - v1 v2 + v2^2.
    """
    width = 4
    alpha, ell, v1, v2 = (var(i, width) for i in range(width))
    two = const(2, width)
    four = const(4, width)
    gap = four.mul(ell).add(alpha, scale=-1)
    den_w = two.mul(ell).mul(v1).add(alpha.mul(v2), scale=-1)
    left = two.mul(v1).add(v2, scale=-1).mul(v1).mul(gap).add(
        den_w.mul(two.mul(v2).add(v1, scale=-1))
    )
    quad = v1.mul(v1).add(v1.mul(v2), scale=-1).add(v2.mul(v2))
    right = two.mul(alpha).mul(quad).add(
        two.mul(const(3, width)).mul(ell).mul(v1).mul(v1), scale=-1
    )
    # right was built as 2αQ - 6 l v1^2; the displayed numerator is the negative.
    require(left.add(right).terms == {}, "axis numerator identity failed")


def check_axis_rearrangement():
    """k c_u = (αβ-γ^2)/(2α) rearranges to the displayed axis equation."""
    width = 7
    alpha, beta, gamma, kay, ell, v1, v2 = (var(i, width) for i in range(width))
    two = const(2, width)
    four = const(4, width)
    three = const(3, width)
    quad = v1.mul(v1).add(v1.mul(v2), scale=-1).add(v2.mul(v2))
    numer = two.mul(alpha).mul(quad).add(two.mul(three).mul(ell).mul(v1).mul(v1), scale=-1).scale(-1)
    gap = four.mul(ell).add(alpha, scale=-1)
    den = v1.mul(v1).mul(gap)
    disc = alpha.mul(beta).add(gamma.mul(gamma), scale=-1)
    scale_cleared = two.mul(alpha).mul(kay).mul(numer).add(disc.mul(den), scale=-1)
    displayed = den.mul(disc).add(four.mul(alpha).mul(kay).mul(alpha.mul(quad).add(three.mul(ell).mul(v1).mul(v1), scale=-1)))
    require(scale_cleared.add(displayed).terms == {}, "axis rearrangement is not an identity")


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


def check_axis_mod4():
    """The cleared axis sides cannot agree: left is 2 mod 4, right is 0 mod 4."""
    odds = (1, 3, 5, 7)
    seen = 0
    for alpha in odds:
        for four_l in (0, 4):
            gap = (four_l - alpha) % 8
            require(gap % 2 == 1, "4l-α became even")
            for det_mod in (2, 6):
                for v1 in odds:
                    seen += 1
                    left = (v1 * v1 * gap * det_mod) % 8
                    require(left in (2, 6), "axis left residue " + str(left))
                    require(left % 4 == 2, "axis left lost exact valuation 1")
    require(seen == 64, "expected 64 axis residue classes, found " + str(seen))
    for kay in range(-6, 7):
        for block in range(-6, 7):
            right = 4 * kay * block
            require(right % 4 == 0, "factor 4 failed to clear mod 4")


def check_quadratic_valuation():
    """Every primitive vector has q ≡ 2 (mod 4). The mod-2 classes are exhaustive."""
    seen = 0
    for u1 in (0, 1):
        for u2 in (0, 1):
            if (u1, u2) == (0, 0):
                continue
            seen += 1
            parenthesis = u1 * u1 - u1 * u2 + u2 * u2
            require(parenthesis % 2 == 1, "primitive parenthesis even " + str((u1, u2)))
            require((2 * parenthesis) % 4 == 2, "q lost valuation 1")
    require(seen == 3, "expected 3 primitive mod-2 classes")
    for u1, u2 in product(range(-8, 9), repeat=2):
        if gcd(abs(u1), abs(u2)) != 1:
            continue
        value = 2 * (u1 * u1 - u1 * u2 + u2 * u2)
        require(value % 4 == 2, "primitive q not 2 mod 4 " + str((u1, u2, value)))
        require(value != 0, "primitive q vanished")


def valuation_gap(shift, orientation):
    """Lower bounds in the Cramer case stay strictly above the constant term."""
    if orientation == "axial-diagonal":
        constant = 1 + shift
        l_term = 3 + shift
        k_term = 2 + shift
        kl_term = 2 + shift
    elif orientation == "diagonal-axial":
        constant = 1 + shift
        l_term = 2 + shift
        k_term = 3 + shift
        kl_term = 2 + shift
    else:
        raise ValueError("unknown orientation")
    require(l_term > constant and k_term > constant and kl_term > constant,
            "valuation gap collapsed at " + orientation + " " + str(shift))


def check_valuation_gaps():
    for shift in range(0, 12):
        valuation_gap(shift, "axial-diagonal")
        valuation_gap(shift, "diagonal-axial")


def egcd(a, b):
    if b == 0:
        if a >= 0:
            return 1, 0, a
        return -1, 0, -a
    x, y, g = egcd(b, a % b)
    return y, x - (a // b) * y, g


def cong_basis(c1, c2, modulus):
    """Z-basis of {(z1,z2): c1 z1 + c2 z2 ≡ 0 mod modulus}."""
    if modulus == 1:
        return [(1, 0), (0, 1)]
    c1 %= modulus
    c2 %= modulus
    g = gcd(gcd(c1, c2), modulus)
    c1 //= g
    c2 //= g
    modulus //= g
    if modulus == 1:
        return [(1, 0), (0, 1)]
    g2 = gcd(c1, c2)
    require(g2 != 0, "congruence basis divided by zero")
    c1 //= g2
    c2 //= g2
    x_bez, y_bez, g_bez = egcd(c1, c2)
    require(g_bez == 1, "bezout failed")
    return [(c2, -c1), (modulus * x_bez, modulus * y_bez)]


def intersect_congruence(basis, c1, c2, modulus):
    b1, b2 = basis
    d1 = c1 * b1[0] + c2 * b1[1]
    d2 = c1 * b2[0] + c2 * b2[1]
    z_basis = cong_basis(d1, d2, modulus)
    return [
        (z1 * b1[0] + z2 * b2[0], z1 * b1[1] + z2 * b2[1])
        for z1, z2 in z_basis
    ]


def check_congruence_basis():
    """The congruence basis matches brute force on a finite rectangle."""
    checked = 0
    for modulus in range(1, 7):
        for c1 in range(0, 9):
            for c2 in range(0, 9):
                basis = cong_basis(c1, c2, modulus)
                g = gcd(gcd(c1, c2), modulus)
                det = basis[0][0] * basis[1][1] - basis[0][1] * basis[1][0]
                require(abs(det) == modulus // g, "congruence index " + str((c1, c2, modulus)))
                for vector in basis:
                    require((c1 * vector[0] + c2 * vector[1]) % modulus == 0, "generator misses congruence")
                for kay in range(modulus):
                    for ell in range(modulus):
                        if (c1 * kay + c2 * ell) % modulus:
                            continue
                        checked += 1
                        z1 = kay * basis[1][1] - ell * basis[1][0]
                        z2 = -kay * basis[0][1] + ell * basis[0][0]
                        require(z1 % det == 0 and z2 % det == 0,
                                "brute solution outside the basis")
    require(checked > 100, "congruence self-test checked too little")


def bilinear(left, right):
    return F(
        2 * left[0] * right[0]
        - left[0] * right[1]
        - left[1] * right[0]
        + 2 * left[1] * right[1]
    )


def diag13_bilinear(left, right):
    return F(3 * left[0] * right[0] + left[1] * right[1])


def diag31_bilinear(left, right):
    return F(left[0] * right[0] + 3 * left[1] * right[1])


def cross(left, right):
    return F(left[0] * right[1] - left[1] * right[0])


def solve_scales(first, second, third, form=bilinear):
    return (
        form(second, third) / (cross(first, second) * cross(first, third)),
        form(third, first) / (cross(second, third) * cross(second, first)),
        form(first, second) / (cross(third, first) * cross(third, second)),
    )


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
    for direction in primitive_directions(8):
        first, second = direction
        diagonal = first % 2 == 1 and second % 2 == 1
        axial = (first % 2 == 0) ^ (second % 2 == 0)
        require(diagonal or axial, "primitive vector is axial or diagonal")
        for numerator in range(-8, 9):
            if numerator == 0:
                continue
            for denominator in range(1, 9):
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
    """On a finite box, the vertical scale formulas match the general formula."""
    checked = 0
    for sign in (1, -1):
        vertical = (0, sign)
        for left in primitive_directions(6):
            if left[0] == 0:
                continue
            for right in primitive_directions(6):
                if right[0] == 0 or cross(left, right) == 0:
                    continue
                if cross(vertical, left) == 0 or cross(vertical, right) == 0:
                    continue
                if bilinear(left, right) == 0 or bilinear(vertical, left) == 0 or bilinear(vertical, right) == 0:
                    continue
                scales = solve_scales(vertical, left, right)
                reduced_u = bilinear(left, right) / (F(left[0]) * F(right[0]))
                reduced_v = (2 * right[1] - right[0]) / (F(left[0]) * cross(left, right))
                require(scales[0] == reduced_u, "axis c_u reduction " + str((left, right, sign)))
                require(scales[1] == reduced_v, "axis c_v reduction " + str((left, right, sign)))
                checked += 1
    require(checked > 100, "axis-reduction box checked too little")


def parity_image(left, right):
    modulus = 1
    for entry in left + right:
        modulus = modulus // gcd(modulus, entry.denominator) * entry.denominator
    numer_left = [entry.numerator * (modulus // entry.denominator) for entry in left]
    numer_right = [entry.numerator * (modulus // entry.denominator) for entry in right]
    basis = [(1, 0), (0, 1)]
    for a_coef, b_coef in zip(numer_left, numer_right):
        basis = intersect_congruence(basis, a_coef, b_coef, modulus)
    images = {(0, 0)}
    phis = []
    for kay, ell in basis:
        combined = tuple(kay * left[i] + ell * right[i] for i in range(3))
        require(all(entry.denominator == 1 for entry in combined), "lattice generator was not integral")
        parity = ((int(combined[0]) + int(combined[1])) & 1, int(combined[2]) & 1)
        phis.append(parity)
        images.add(parity)
    images.add(((phis[0][0] + phis[1][0]) & 1, (phis[0][1] + phis[1][1]) & 1))
    return images


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
            modulus = modulus // gcd(modulus, entry.denominator) * entry.denominator
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
H = (F(1), F(1), F(2))
DIAG13 = (F(1), F(3), F(0))
DIAG31 = (F(3), F(1), F(0))
TARGETS = (
    (F(1), F(0), F(1)),
    (F(2), F(1), F(-1)),
    (F(0), F(1), F(1)),
    (F(1), F(2), F(-1)),
)
CALLS = (
    (1, A),
    (1, B),
    (0, P),
    (2, Q),
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
    require(total == H, label + " does not solve R+S+T=(1,1,2)")
    require(total != DIAG13 and total != DIAG31, label + " solved a diagonal sibling residual")
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
    directions = ((1, 0), (0, 1), (1, 1))
    scales = solve_scales(*directions)
    require(scales == (F(1), F(1), F(1)), "rational solution scales changed " + str(scales))
    solutions.append(("rational-rank-one", tuple(
        coeffs(direction, scale) for direction, scale in zip(directions, scales)
    )))
    directions = ((0, 1), (1, -3), (1, -2))
    scales = solve_scales(*directions)
    require(any(scale < 0 for scale in scales), "negative fixture has no negative scale")
    solutions.append(("negative-frame", tuple(
        coeffs(direction, scale) for direction, scale in zip(directions, scales)
    )))
    directions = ((0, 1), (1, -3), (1, -1))
    scales = solve_scales(*directions)
    require(any(scale.denominator != 1 for scale in scales), "fractional fixture is integral")
    solutions.append(("fractional-frame", tuple(
        coeffs(direction, scale) for direction, scale in zip(directions, scales)
    )))
    solutions.append((
        "parallel-opposite",
        (coeffs((1, 1), 2), coeffs((1, 1), F(-1, 2)), coeffs((1, -1), F(1, 2))),
    ))
    solutions.append(("old-label-duplicate", (P, coeffs((1, 1), 1), Q)))
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
    identity = (F(1), F(1), F(0))
    require(matrix_det(identity) == 1, "det I changed")
    require(matrix_det(H) == 3, "residual determinant changed")

    def even_form(vector):
        return 2 * vector[0] + 2 * vector[1] + 2 * vector[2]

    require(even_integer(even_form(A)) and even_integer(even_form(B))
            and even_integer(even_form(P)) and even_integer(even_form(Q)),
            "even-even-even form was not rejected by shape")
    directions = ((1, 0), (0, 1), (1, 1))
    for form, sibling in ((diag13_bilinear, DIAG13), (diag31_bilinear, DIAG31)):
        sibling_frames = tuple(
            coeffs(direction, scale)
            for direction, scale in zip(directions, solve_scales(*directions, form=form))
        )
        sibling_total = tuple(sum(frame[i] for frame in sibling_frames) for i in range(3))
        require(sibling_total == sibling, "diagonal form stopped solving its own residual")
        require(sibling_total != H, "diagonal form solved this residual")
    require(bilinear((1, 0), (0, 1)) == -1, "cross term of this residual vanished")
    require(bilinear((1, 0), (1, 0)) == 2 and bilinear((0, 1), (0, 1)) == 2,
            "diagonal values of q changed")


def main():
    check_bracket_polynomial()
    check_determinant_polynomial()
    check_axis_numerator()
    check_axis_rearrangement()
    check_lemma4()
    check_axis_mod4()
    check_quadratic_valuation()
    check_valuation_gaps()
    check_congruence_basis()
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
        "parallel-opposite",
        "old-label-duplicate",
    ], "fixture list changed")
    check_failures()
    print("PASS three-signed-q-twice character checks")


if __name__ == "__main__":
    main()
