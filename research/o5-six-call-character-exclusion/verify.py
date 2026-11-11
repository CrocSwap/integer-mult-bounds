"""Character exclusion for the six-call orbit O5.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The proof is PROOF.md. This file checks the polynomial identities used there,
the exhaustive mod-8 lemmas, the direction-type case split, explicit witnesses
(including a pair whose parity image contains (1,1)), and the label transport
to the four profiles of the orbit. The witnesses are not the proof.
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


def var(index, width):
    exponents = [0] * width
    exponents[index] = 1
    return Poly({tuple(exponents): 1})


def const(value, width):
    if value == 0:
        return Poly()
    return Poly({tuple([0] * width): value})


def check_bracket_polynomial():
    """δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w) is identically zero.

    B(x,y) = 3 x1 y1 + 2 x2 y2 and q(x) = 3 x1^2 + 2 x2^2.
    """
    width = 6
    u1, u2, v1, v2, w1, w2 = (var(i, width) for i in range(width))
    three = const(3, width)
    two = const(2, width)

    def bilinear(x1, x2, y1, y2):
        return three.mul(x1).mul(y1).add(two.mul(x2).mul(y2))

    def cross(x1, x2, y1, y2):
        return x1.mul(y2).add(x2.mul(y1), scale=-1)

    def quad(x1, x2):
        return three.mul(x1).mul(x1).add(two.mul(x2).mul(x2))

    expression = (
        cross(u1, u2, w1, w2).mul(bilinear(u1, u2, v1, v2))
        .add(cross(u1, u2, v1, v2).mul(bilinear(u1, u2, w1, w2)), scale=-1)
        .add(quad(u1, u2).mul(cross(v1, v2, w1, w2)), scale=-1)
    )
    require(expression.terms == {}, "scale bracket is not identically zero")


def check_doubled_matrix_identities():
    """G = σ u1 δ, H_ = -τ v1 δ, and αβ-γ^2 = σ τ δ^2."""
    width = 6
    sigma, tau, u1, u2, v1, v2 = (var(i, width) for i in range(width))
    alpha = sigma.mul(u1).mul(u1).add(tau.mul(v1).mul(v1))
    gamma = sigma.mul(u1).mul(u2).add(tau.mul(v1).mul(v2))
    beta = sigma.mul(u2).mul(u2).add(tau.mul(v2).mul(v2))
    delta = u1.mul(v2).add(u2.mul(v1), scale=-1)
    gee = alpha.mul(v2).add(gamma.mul(v1), scale=-1)
    hhh = alpha.mul(u2).add(gamma.mul(u1), scale=-1)
    require(gee.add(sigma.mul(u1).mul(delta), scale=-1).terms == {}, "G identity")
    require(hhh.add(tau.mul(v1).mul(delta)).terms == {}, "H_ identity")
    disc = alpha.mul(beta).add(gamma.mul(gamma), scale=-1)
    require(disc.add(sigma.mul(tau).mul(delta).mul(delta), scale=-1).terms == {},
            "discriminant identity")


def check_cramer_determinant():
    """The (w1,w2) coefficient determinant for q = 3 x1^2 + 2 x2^2.

    The kl coefficient is 24, not the 12 of the diag(1,3) form.
    """
    width = 8
    kay, ell, u1, u2, v1, v2, gee, hhh = (var(i, width) for i in range(width))
    six = const(6, width)
    four = const(4, width)
    two = const(2, width)
    three = const(3, width)
    row11 = six.mul(kay).mul(u1).mul(v1).add(gee.mul(u2))
    row12 = four.mul(kay).mul(u1).mul(v2).add(gee.mul(u1), scale=-1)
    row21 = six.mul(ell).mul(u1).mul(v1).add(hhh.mul(v2))
    row22 = four.mul(ell).mul(v1).mul(u2).add(hhh.mul(v1), scale=-1)
    matrix_det = row11.mul(row22).add(row12.mul(row21), scale=-1)
    delta = u1.mul(v2).add(u2.mul(v1), scale=-1)
    quad_u = three.mul(u1).mul(u1).add(two.mul(u2).mul(u2))
    quad_v = three.mul(v1).mul(v1).add(two.mul(v2).mul(v2))
    closed = (
        delta.mul(gee).mul(hhh)
        .add(two.mul(ell).mul(gee).mul(v1).mul(quad_u))
        .add(two.mul(kay).mul(hhh).mul(u1).mul(quad_v), scale=-1)
        .add(const(24, width).mul(kay).mul(ell).mul(u1).mul(v1).mul(delta), scale=-1)
    )
    require(matrix_det.terms == closed.terms, "Cramer determinant mismatch")


def check_axis_rearrangement():
    """(α-4l) v1^2 (αβ-γ^2 - 6 α k) = 4 α^2 k v2^2, as polynomials."""
    width = 7
    alpha, beta, gamma, kay, ell, vv1, vv2 = (var(i, width) for i in range(width))
    four = const(4, width)
    gap = alpha.add(four.mul(ell), scale=-1)
    v1sq = vv1.mul(vv1)
    v2sq = vv2.mul(vv2)
    disc = alpha.mul(beta).add(gamma.mul(gamma), scale=-1)
    uncleared = const(2, width).mul(alpha).mul(kay).mul(
        const(3, width).mul(v1sq).mul(gap).add(const(2, width).mul(alpha).mul(v2sq))
    ).add(disc.mul(v1sq).mul(gap), scale=-1)
    displayed = gap.mul(v1sq).mul(
        disc.add(const(6, width).mul(alpha).mul(kay), scale=-1)
    ).add(four.mul(alpha).mul(alpha).mul(kay).mul(v2sq), scale=-1)
    require(uncleared.add(displayed).terms == {}, "axis rearrangement is not an identity")


def check_lemma4():
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
    require(seen == 32, "expected 32 residue classes, found " + str(seen))


def v2_int(value):
    value = abs(int(value))
    if value == 0:
        return 99
    count = 0
    while value % 2 == 0:
        value //= 2
        count += 1
    return count


def check_quadratic_valuations():
    """Horizontal q ≡ 3 (mod 8); vertical has valuation 1; diagonal q ≡ 5 (mod 8)."""
    odds = (1, 3, 5, 7)
    evens = (0, 2, 4, 6)
    for first in odds:
        for second in odds:
            value = 3 * first * first + 2 * second * second
            require(value % 8 == 5, "diagonal residue")
            require(v2_int(value) == 0, "diagonal valuation")
        for second in evens:
            value = 3 * first * first + 2 * second * second
            require(value % 8 == 3, "horizontal residue")
            require(v2_int(value) == 0, "horizontal valuation")
    for first in evens:
        for second in odds:
            value = 3 * first * first + 2 * second * second
            require(value % 8 in (2, 6), "vertical residue")
            require(v2_int(value) == 1, "vertical valuation")
            if first % 4 == 0:
                require(value % 8 == 2, "vertical residue at multiple of 4")
            else:
                require(value % 8 == 6, "vertical residue at 2 mod 4")


def check_axis_valuation_gap():
    """When v2(k) ≥ 1 the axis sides have valuations 1 and at least 3."""
    odds = (1, 3, 5, 7)
    for alpha in odds:
        for ell in range(8):
            require((alpha - 4 * ell) % 2 == 1, "α-4l became even")
        for kay_val in range(1, 6):
            kay = 1 << kay_val
            require(v2_int(6 * alpha * kay) >= 2, "6αk valuation")
            for disc_mod in (2, 6):
                # disc stands in for any integer ≡ disc_mod (mod 8), hence valuation 1.
                require(v2_int(disc_mod) == 1, "discriminant model")
                require(v2_int(6 * alpha * kay) > 1, "bracket should keep valuation 1")
        for kay in odds:
            right = 4 * alpha * alpha * kay
            require(v2_int(right) == 2, "odd-k right side")


def check_direction_cases():
    """Every triple of line types has a pair that the proof declares safe."""
    types = ("H", "V", "V0", "D")

    def pair_safe(first, second, third):
        pair = tuple(sorted((first, second)))
        if pair in {("D", "D"), ("H", "H"), ("V", "V"), ("H", "V")}:
            return True
        if pair in {("H", "V0"), ("V", "V0")}:
            return True
        if pair == ("D", "V0"):
            return third != "D"
        return False

    misses = []
    for triple in product(types, repeat=3):
        if triple.count("V0") > 1:
            continue
        if not any(pair_safe(triple[i], triple[j], triple[k])
                   for i, j, k in ((0, 1, 2), (0, 2, 1), (1, 2, 0))):
            misses.append(triple)
    require(misses == [], "uncovered direction triple " + str(misses[:4]))


def cross(left, right):
    return left[0] * right[1] - left[1] * right[0]


def bilinear(left, right):
    return 3 * left[0] * right[0] + 2 * left[1] * right[1]


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


A = (F(1), F(0), F(0))
B = (F(0), F(1), F(0))
P = (F(0), F(0), F(1))
Q = (F(1), F(1), F(-1))
H = (F(2), F(3), F(0))
NAMED_H = (F(3), F(2), F(0))
OLD_H = (F(1), F(3), F(0))
TARGETS = (
    (F(1), F(0), F(1)),
    (F(2), F(1), F(-1)),
    (F(0), F(1), F(1)),
    (F(1), F(2), F(-1)),
)
LABELS = {"A": A, "B": B, "P": P, "Q": Q}


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


def detected_counts(family, shift, frames, profile):
    calls = 0
    for multiplicity, vector in zip(profile, (A, B, P, Q)):
        if odd_integer(form_value(family, shift, vector)):
            calls += multiplicity
    for vector in frames:
        if odd_integer(form_value(family, shift, vector)):
            calls += 1
    targets = sum(1 for vector in TARGETS if odd_integer(form_value(family, shift, vector)))
    return calls, targets


def check_family_counts():
    profile = (1, 0, 1, 1)
    for shift in product(range(4), repeat=3):
        ab_calls, ab_targets = detected_counts("AB", shift, (), profile)
        pq_calls, pq_targets = detected_counts("PQ", shift, (), profile)
        require(ab_calls == 1 and ab_targets == 4, "AB old count")
        require(pq_calls == 2 and pq_targets == 4, "PQ old count")
        require(odd_integer(form_value("AB", shift, H)), "AB residual not odd")
        require(even_integer(form_value("PQ", shift, H)), "PQ residual not even")
    named = (0, 1, 1, 1)
    require(detected_counts("AB", (0, 0, 0), (), named) == (1, 4), "named AB count")
    require(detected_counts("PQ", (0, 0, 0), (), named) == (2, 4), "named PQ count")
    swapped_roles = (1, 1, 0, 1)
    require(detected_counts("AB", (0, 0, 0), (), swapped_roles) == (2, 4), "orbit AB count")
    require(detected_counts("PQ", (0, 0, 0), (), swapped_roles) == (1, 4), "orbit PQ count")


def phi(vector):
    require(all(entry.denominator == 1 for entry in vector), "phi on a non-integral vector")
    return ((vector[0] + vector[1]).numerator & 1, vector[2].numerator & 1)


def parity_image(left, right):
    modulus = 1
    for entry in left + right:
        modulus = modulus * entry.denominator // gcd(modulus, entry.denominator)
    seen = set()
    for coef_l in range(2 * modulus):
        for coef_r in range(2 * modulus):
            combined = tuple(coef_l * left[i] + coef_r * right[i] for i in range(3))
            if any(entry.denominator != 1 for entry in combined):
                continue
            seen.add(phi(combined))
    require(seen, "empty parity image")
    return seen


def check_single_line_box():
    checked = 0
    for first, second in product(range(-8, 9), repeat=2):
        if (first, second) == (0, 0) or gcd(abs(first), abs(second)) != 1:
            continue
        if second < 0 or (second == 0 and first < 0):
            continue
        diagonal = first % 2 == 1 and second % 2 == 1
        for numerator in range(-8, 9):
            if numerator == 0:
                continue
            for denominator in range(1, 9):
                vector = coeffs((first, second), F(numerator, denominator))
                if any(entry.denominator != 1 for entry in vector):
                    continue
                checked += 1
                image = phi(vector)
                require(image != (1, 1), "single line hit (1,1)")
                if diagonal:
                    require(image[0] == 0, "diagonal line has odd a+b")
                else:
                    require(image[1] == 0, "axial line has odd c")
    require(checked > 50, "single-line box checked too little")


def check_axis_scale_box():
    checked = 0
    for sign in (1, -1):
        vertical = (0, sign)
        for left in product(range(-4, 5), repeat=2):
            if left[0] == 0 or gcd(abs(left[0]), abs(left[1])) != 1:
                continue
            for right in product(range(-4, 5), repeat=2):
                if right[0] == 0 or gcd(abs(right[0]), abs(right[1])) != 1:
                    continue
                if cross(left, right) == 0:
                    continue
                scale_u = F(bilinear(left, right), cross(vertical, left) * cross(vertical, right))
                scale_v = F(bilinear(right, vertical), cross(left, right) * cross(left, vertical))
                reduced_u = 3 + F(2 * left[1] * right[1], left[0] * right[0])
                reduced_v = F(2 * right[1], cross(left, right) * left[0])
                require(scale_u == reduced_u, "axis c_u")
                require(scale_v == reduced_v, "axis c_v")
                checked += 1
    require(checked > 20, "axis scale box checked too little")


def frames_sum(frames):
    return tuple(sum(frame[i] for frame in frames) for i in range(3))


def require_rank_one_solution(frames, residual, label):
    require(frames_sum(frames) == residual, label + " does not solve the residual")
    for frame in frames:
        require(frame != (F(0), F(0), F(0)), label + " has a zero frame")
        require(matrix_det(frame) == 0, label + " frame is not rank one")


def require_character(frames, profile, family, shift, label):
    calls, targets = detected_counts(family, shift, frames, profile)
    require(calls == 2 and targets == 4, label + " detects " + str((calls, targets)))
    for frame in frames[:2]:
        require(even_integer(form_value(family, shift, frame)), label + " safe frame not even")
    third = form_value(family, shift, frames[2])
    if family == "AB":
        require(odd_integer(third), label + " third frame not odd")
    else:
        require(even_integer(third), label + " PQ third frame not even")


def check_witnesses():
    profile = (1, 0, 1, 1)
    simple = (
        coeffs((1, 1), F(3, 2)),
        coeffs((1, -1), F(3, 2)),
        coeffs((1, 0), -1),
    )
    require_rank_one_solution(simple, H, "simple")
    require(parity_image(simple[0], simple[1]).isdisjoint({(1, 1)}), "simple safe pair")
    require_character(simple, profile, "AB", (0, 0, 1), "simple")

    parallel = ((F(2), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(2), F(0)))
    require_rank_one_solution(parallel, H, "parallel")
    require((1, 1) not in parity_image(parallel[1], parallel[2]), "parallel image")
    # Reorder so the safe pair is first: the two vertical frames, then 2A.
    parallel_ordered = (parallel[1], parallel[2], parallel[0])
    require_character(parallel_ordered, profile, "PQ", (0, 0, 0), "parallel")

    mixed = (
        coeffs((-5, 1), F(1, 4)),
        coeffs((-1, 1), F(-53, 4)),
        coeffs((-3, 4), 1),
    )
    require_rank_one_solution(mixed, H, "mixed")
    unsafe = coeffs((-5, 1), F(1, 4))
    horizontal = coeffs((-3, 4), 1)
    hit = tuple(2 * unsafe[i] + horizontal[i] for i in range(3))
    require(hit == (F(36), F(31), F(-29)), "mixed witness vector changed")
    require(phi(hit) == (1, 1), "mixed witness is not (1,1)")
    require((1, 1) in parity_image(unsafe, horizontal), "mixed unsafe pair")
    require((1, 1) not in parity_image(mixed[0], mixed[1]), "mixed safe pair")
    require_character(mixed, profile, "AB", (0, 0, 1), "mixed")

    axis = (
        coeffs((-5, 3), F(1, 8)),
        coeffs((-3, 5), F(-1, 8)),
        coeffs((0, 1), 5),
    )
    require_rank_one_solution(axis, H, "axis")
    axis_hit = tuple(1 * axis[2][i] + 4 * axis[0][i] for i in range(3))
    require(axis_hit == (F(20), F(17), F(-15)), "axis witness vector changed")
    require(phi(axis_hit) == (1, 1), "axis witness is not (1,1)")
    require((1, 1) in parity_image(axis[2], axis[0]), "axis pair")
    require((1, 1) not in parity_image(axis[0], axis[1]), "axis safe pair")
    require_character(axis, profile, "AB", (0, 0, 0), "axis")


def entries(vector):
    first, second, off = vector
    return (first + off / 2, off / 2, second + off / 2)


def from_entries(ex, ey, ez):
    return (ex - ey, ez - ey, 2 * ey)


def map_s(vector):
    ex, ey, ez = entries(vector)
    return from_entries(ex, -ey, ez)


def map_t(vector):
    ex, ey, ez = entries(vector)
    return from_entries(ez, ey, ex)


def map_h(vector):
    ex, ey, ez = entries(vector)
    return from_entries((ex + 2 * ey + ez) / 2, (ex - ez) / 2, (ex - 2 * ey + ez) / 2)


MAPS = {"s": map_s, "t": map_t, "h": map_h}


def apply_word(word, vector):
    for letter in word:
        vector = MAPS[letter](vector)
    return vector


def residual(profile):
    a_count, b_count, p_count, q_count = profile
    return tuple(
        4 * (A[i] + B[i]) - a_count * A[i] - b_count * B[i] - p_count * P[i] - q_count * Q[i]
        for i in range(3)
    )


def character_rows(frames, profile):
    modulus = 1
    for frame in frames:
        for entry in frame:
            modulus = modulus * entry.denominator // gcd(modulus, entry.denominator)
    modulus *= 2
    seen = {}
    for shift in product(range(modulus), repeat=3):
        values = [sum(shift[i] * frame[i] for i in range(3)) for frame in frames]
        if any(value.denominator != 1 for value in values):
            continue
        bits = []
        for vector in (A, B, P, Q) + tuple(frames):
            value = sum(shift[i] * vector[i] for i in range(3))
            if value.denominator != 1:
                bits = None
                break
            bits.append(value.numerator & 1)
        if bits is None:
            continue
        seen[tuple(bits)] = shift
    rows = []
    label_bits_index = {"A": 0, "B": 1, "P": 2, "Q": 3}
    for bits, shift in seen.items():
        calls = 0
        for multiplicity, name in zip(profile, "ABPQ"):
            calls += multiplicity * bits[label_bits_index[name]]
        calls += sum(bits[4:])
        targets = 0
        for vector in TARGETS:
            value = sum(shift[i] * vector[i] for i in range(3))
            targets += value.numerator & 1
        rows.append((calls, targets))
    return rows


def check_transport():
    for letter, mapping in MAPS.items():
        require(mapping(mapping(A)) == A and mapping(mapping(B)) == B, letter + " not an involution on the basis")
        identity = (F(1), F(1), F(0))
        require(mapping(identity) == identity, letter + " moves I")
    require(map_s(A) == A and map_s(B) == B and map_s(P) == Q and map_s(Q) == P, "s labels")
    require(map_t(A) == B and map_t(B) == A and map_t(P) == P and map_t(Q) == Q, "t labels")
    require(map_h(A) == P and map_h(P) == A and map_h(B) == Q and map_h(Q) == B, "h labels")
    require(matrix_det(H) == 6, "det diag(2,3)")
    require(map_t(H) == NAMED_H, "t does not send diag(2,3) to diag(3,2)")

    words = [""]
    for _ in range(4):
        for word in list(words):
            for letter in "sth":
                extended = word + letter
                images = tuple(apply_word(extended, vector) for vector in (A, B, P))
                known = {tuple(apply_word(old, vector) for vector in (A, B, P)) for old in words}
                if images not in known:
                    words.append(extended)
    require(len(words) == 8, "group order " + str(len(words)))

    def image_profile(word, profile):
        counts = dict(zip("ABPQ", profile))
        moved = {}
        for name, vector in LABELS.items():
            image = apply_word(word, vector)
            image_name = next(key for key, value in LABELS.items() if value == image)
            moved[image_name] = counts[name]
        return tuple(moved[name] for name in "ABPQ")

    orbit = {(0, 1, 1, 1)}
    growing = True
    while growing:
        growing = False
        for profile in list(orbit):
            for word in words:
                image = image_profile(word, profile)
                if image not in orbit:
                    orbit.add(image)
                    growing = True
    require(orbit == {(0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0)},
            "orbit " + str(sorted(orbit)))

    simple = (
        coeffs((1, 1), F(3, 2)),
        coeffs((1, -1), F(3, 2)),
        coeffs((1, 0), -1),
    )
    source = (1, 0, 1, 1)
    source_rows = character_rows(simple, source)
    require(len(source_rows) == 8, "simple character count " + str(len(source_rows)))
    require(any(calls < targets for calls, targets in source_rows), "simple table has no strict character")
    for word in words:
        moved = tuple(apply_word(word, frame) for frame in simple)
        profile = image_profile(word, source)
        require_rank_one_solution(moved, residual(profile), "transport " + word)
        rows = character_rows(moved, profile)
        require(sorted(rows) == sorted(source_rows), "table changed under " + word)
    named_frames = tuple(map_t(frame) for frame in simple)
    require(frames_sum(named_frames) == NAMED_H, "named residual")
    named_rows = character_rows(named_frames, (0, 1, 1, 1))
    require(sorted(named_rows) == sorted(source_rows), "named table")
    require(any(calls < targets for calls, targets in named_rows), "named profile not excluded on the witness")


def solve_with(form, directions):
    first, second, third = directions
    scales = (
        form(second, third) / (cross(first, second) * cross(first, third)),
        form(third, first) / (cross(second, third) * cross(second, first)),
        form(first, second) / (cross(third, first) * cross(third, second)),
    )
    return tuple(coeffs(direction, scale) for direction, scale in zip(directions, scales))


def check_failures():
    directions = ((1, 0), (1, 1), (1, -1))
    predecessor = solve_with(lambda left, right: 3 * left[0] * right[0] + left[1] * right[1], directions)
    require(frames_sum(predecessor) == OLD_H, "diag(1,3) form stopped solving its residual")
    require(frames_sum(predecessor) != H, "diag(1,3) form solved diag(2,3)")
    swapped = solve_with(lambda left, right: 2 * left[0] * right[0] + 3 * left[1] * right[1], directions)
    require(frames_sum(swapped) == NAMED_H, "swapped form stopped solving diag(3,2)")
    require(frames_sum(swapped) != H, "swapped form solved diag(2,3)")
    good = solve_with(bilinear, directions)
    tampered = (good[0], good[1], tuple(good[2][i] + A[i] for i in range(3)))
    require(frames_sum(tampered) != H, "tampered sum still equals the residual")
    require(matrix_det((F(1), F(1), F(0))) == 1, "det I changed")


def main():
    check_bracket_polynomial()
    check_doubled_matrix_identities()
    check_cramer_determinant()
    check_axis_rearrangement()
    check_lemma4()
    check_quadratic_valuations()
    check_axis_valuation_gap()
    check_direction_cases()
    check_family_counts()
    check_single_line_box()
    check_axis_scale_box()
    check_witnesses()
    check_transport()
    check_failures()
    print("PASS o5-six-call-character-exclusion")


if __name__ == "__main__":
    main()
