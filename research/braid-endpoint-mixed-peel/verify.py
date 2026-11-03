#!/usr/bin/env python3
"""Exact checks for the braid-endpoint mixed peel.

Two phi engines are compared on every rank-one projector over F2, F3 and F5.
Method A builds the 24-dimensional operator and counts vectors in H sent back
into H. Method B counts the negative-pair conditions on F^{-1}H. Their
nullities agree because dim(H ∩ M H) = dim(H ∩ M^{-1} H) for invertible M.
The all-field rank claims are row reductions over Q(μ) and F_p(μ).
"""

from __future__ import annotations

from fractions import Fraction

S = (2, 1, 3, 4)
T = (1, 3, 2, 4)
U = (1, 2, 4, 3)
W = (3, 2, 1, 4)
ST = (2, 3, 1, 4)
LABELS = {"s": S, "t": T, "u": U}

PAIRS = [(i, j) for i in range(1, 5) for j in range(1, 5) if i != j]
POS = [pair for pair in PAIRS if pair[0] < pair[1]]
NEG = [pair for pair in PAIRS if pair[0] > pair[1]]
PINDEX = {pair: index for index, pair in enumerate(PAIRS)}

# Hand-listed supports after the first peel. rho_M is w on both sides.
S_PEEL_SUPPORT = {
    "s": (
        {(1, 2), (1, 4), (2, 4), (3, 1), (3, 2), (3, 4)},
        {(1, 4), (2, 1), (2, 4), (3, 1), (3, 2), (3, 4)},
    ),
    "t": (
        {(1, 4), (2, 1), (2, 3), (2, 4), (3, 1), (3, 4)},
        {(1, 4), (2, 1), (2, 4), (3, 1), (3, 2), (3, 4)},
    ),
}


class Check:
    def __init__(self):
        self.count = 0

    def true(self, condition, label):
        self.count += 1
        if not condition:
            raise SystemExit("FAIL " + label)

    def eq(self, got, expected, label):
        self.count += 1
        if got != expected:
            raise SystemExit("FAIL " + label + ": got " + repr(got) + " expected " + repr(expected))


def compose(left, right):
    """left after right. Images are 1-based."""
    return tuple(left[image - 1] for image in right)


def inversions(perm):
    return sum(perm[i] > perm[j] for i in range(4) for j in range(i + 1, 4))


def image_pair(perm, pair):
    return (perm[pair[0] - 1], perm[pair[1] - 1])


def support(perm):
    return {pair for pair in PAIRS if perm[pair[0] - 1] < perm[pair[1] - 1]}


def component(pair, support_l, support_m):
    in_l = pair in support_l
    in_m = pair in support_m
    if in_l and in_m:
        return "A"
    if in_l:
        return "L"
    if in_m:
        return "M"
    return "0"


def peel_table(rho_l, rho_m):
    support_l, support_m = support(rho_l), support(rho_m)
    addresses = {"s": ((1, 2), (2, 1)), "t": ((2, 3), (3, 2)), "u": ((3, 4), (4, 3))}
    return {
        label: (component(alpha, support_l, support_m), component(beta, support_l, support_m))
        for label, (alpha, beta) in addresses.items()
    }


def reading(alpha, beta):
    """Turn one table row into the projector constraint."""
    if (alpha, beta) == ("L", "M"):
        return "I-P"
    if (alpha, beta) == ("M", "L"):
        return "P"
    if (alpha, beta) == ("0", "A"):
        return "any"
    if (alpha, beta) == ("A", "0"):
        return "impossible"
    raise AssertionError((alpha, beta))


def coeff(value, mod):
    if mod is None:
        return value if isinstance(value, Fraction) else Fraction(value)
    return int(value) % mod


def trim(coeffs, mod=None):
    values = [coeff(item, mod) for item in coeffs]
    zero = coeff(0, mod)
    while values and values[-1] == zero:
        values.pop()
    return tuple(values) if values else (zero,)


def poly_add(left, right, mod=None):
    width = max(len(left), len(right))
    return trim(
        [(left[i] if i < len(left) else 0) + (right[i] if i < len(right) else 0) for i in range(width)],
        mod,
    )


def poly_mul(left, right, mod=None):
    zero = (coeff(0, mod),)
    if trim(left, mod) == zero or trim(right, mod) == zero:
        return zero
    out = [coeff(0, mod)] * (len(left) + len(right) - 1)
    for i, ca in enumerate(left):
        for j, cb in enumerate(right):
            out[i + j] += ca * cb
    return trim(out, mod)


def fdiv(num, den, mod):
    if mod is None:
        return coeff(num, None) / coeff(den, None)
    return (int(num) * pow(int(den) % mod, -1, mod)) % mod


def poly_divmod(numer, denom, mod=None):
    zero = coeff(0, mod)
    if trim(denom, mod) == (zero,):
        raise ZeroDivisionError("polynomial divisor is zero")
    quotient = [zero] * max(1, len(numer) - len(denom) + 1)
    remainder = [coeff(item, mod) for item in numer]
    lead = coeff(denom[-1], mod)
    while len(trim(remainder, mod)) >= len(denom) and trim(remainder, mod) != (zero,):
        current = trim(remainder, mod)
        degree = len(current) - len(denom)
        scale = fdiv(current[-1], lead, mod)
        if degree >= len(quotient):
            quotient.extend([zero] * (degree + 1 - len(quotient)))
        quotient[degree] = scale
        for index, term in enumerate(denom):
            remainder[degree + index] = coeff(remainder[degree + index], mod) - scale * coeff(term, mod)
        remainder = list(trim(remainder, mod))
    return trim(quotient, mod), trim(remainder, mod)


def poly_gcd(left, right, mod=None):
    zero = coeff(0, mod)
    while trim(right, mod) != (zero,):
        left, right = right, poly_divmod(left, right, mod)[1]
    lead = trim(left, mod)[-1]
    return trim([fdiv(item, lead, mod) for item in trim(left, mod)], mod)


class RF:
    """Rational function in μ, over Q or over F_p."""

    def __init__(self, num, den=(1,), mod=None):
        self.mod = mod
        zero = coeff(0, mod)
        one = coeff(1, mod)
        num, den = trim(num, mod), trim(den, mod)
        if den == (zero,):
            raise ZeroDivisionError("zero denominator")
        if num == (zero,):
            self.num, self.den = (zero,), (one,)
            return
        common = poly_gcd(num, den, mod)
        num, _ = poly_divmod(num, common, mod)
        den, _ = poly_divmod(den, common, mod)
        if mod is None and den[-1] < 0:
            num = trim([-item for item in num])
            den = trim([-item for item in den])
        elif mod is not None:
            inverse = pow(int(den[-1]) % mod, -1, mod)
            num = trim([int(item) * inverse for item in num], mod)
            den = trim([int(item) * inverse for item in den], mod)
        self.num, self.den = num, den

    def __repr__(self):
        return f"{self.num}/{self.den}" + (f" mod {self.mod}" if self.mod else "")

    def __eq__(self, other):
        if isinstance(other, int):
            other = RF((other,), mod=self.mod)
        return isinstance(other, RF) and self.num == other.num and self.den == other.den and self.mod == other.mod

    def __bool__(self):
        return self.num != (coeff(0, self.mod),)

    def __neg__(self):
        return RF(trim([-item for item in self.num], self.mod), self.den, self.mod)

    def __add__(self, other):
        if isinstance(other, int):
            other = RF((other,), mod=self.mod)
        numer = poly_add(poly_mul(self.num, other.den, self.mod), poly_mul(other.num, self.den, self.mod), self.mod)
        return RF(numer, poly_mul(self.den, other.den, self.mod), self.mod)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return RF((other,), mod=self.mod) - self

    def __mul__(self, other):
        if isinstance(other, int):
            other = RF((other,), mod=self.mod)
        return RF(poly_mul(self.num, other.num, self.mod), poly_mul(self.den, other.den, self.mod), self.mod)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, int):
            other = RF((other,), mod=self.mod)
        if not other:
            raise ZeroDivisionError("division by zero rational function")
        return RF(poly_mul(self.num, other.den, self.mod), poly_mul(self.den, other.num, self.mod), self.mod)

    def __rtruediv__(self, other):
        return RF((other,), mod=self.mod) / self


def mu_var(mod=None):
    return RF((0, 1), mod=mod)


def one_rf(mod=None):
    return RF((1,), mod=mod)


def rref(rows):
    """Elimination with the first nonzero entry in the column as pivot."""
    if not rows:
        return 0, []
    matrix = [list(row) for row in rows]
    rank = 0
    pivots = []
    row = 0
    for col in range(len(matrix[0])):
        pivot = next((index for index in range(row, len(matrix)) if matrix[index][col]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][col]
        pivots.append(scale)
        for index in range(len(matrix)):
            if index == row or not matrix[index][col]:
                continue
            factor = matrix[index][col] / scale
            matrix[index] = [left - factor * right for left, right in zip(matrix[index], matrix[row])]
        row += 1
        rank += 1
    return rank, pivots


def pivot_factors_are_mu_or_mu_minus_one(entry):
    """A pivot ±μ^a(μ-1)^b has no other zero or pole."""

    def linear_ok(poly):
        zero = coeff(0, entry.mod)
        poly = trim(poly, entry.mod)
        if poly == (zero,):
            return False
        if entry.mod is None:
            if len(poly) == 1:
                return poly[0] in (Fraction(1), Fraction(-1))
            if len(poly) != 2:
                return False
            c0, c1 = poly
            if c1 not in (Fraction(1), Fraction(-1)):
                return False
            return -c0 / c1 in (Fraction(0), Fraction(1))
        if len(poly) == 1:
            return int(poly[0]) % entry.mod in (1, entry.mod - 1)
        if len(poly) != 2:
            return False
        c0, c1 = [int(item) % entry.mod for item in poly]
        if c1 not in (1, entry.mod - 1):
            return False
        root = (-c0 * pow(c1, -1, entry.mod)) % entry.mod
        return root in (0, 1)

    return linear_ok(entry.num) and linear_ok(entry.den)


class Prime:
    def __init__(self, value, mod):
        self.v = value % mod
        self.mod = mod

    def __repr__(self):
        return str(self.v)

    def __eq__(self, other):
        other_value = other.v if isinstance(other, Prime) else other
        return self.v == other_value % self.mod

    def __bool__(self):
        return self.v != 0

    def __neg__(self):
        return Prime(-self.v, self.mod)

    def __add__(self, other):
        return Prime(self.v + (other.v if isinstance(other, Prime) else other), self.mod)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return Prime(self.v - (other.v if isinstance(other, Prime) else other), self.mod)

    def __rsub__(self, other):
        return Prime(other, self.mod) - self

    def __mul__(self, other):
        return Prime(self.v * (other.v if isinstance(other, Prime) else other), self.mod)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other_value = other.v if isinstance(other, Prime) else other % self.mod
        return Prime(self.v * pow(other_value, -1, self.mod), self.mod)

    def __rtruediv__(self, other):
        return Prime(other, self.mod) / self


class QFrac:
    def __init__(self, value):
        self.v = value if isinstance(value, Fraction) else Fraction(value)

    def __repr__(self):
        return str(self.v)

    def __eq__(self, other):
        other_value = other.v if isinstance(other, QFrac) else other
        return self.v == other_value

    def __bool__(self):
        return self.v != 0

    def __neg__(self):
        return QFrac(-self.v)

    def __add__(self, other):
        return QFrac(self.v + (other.v if isinstance(other, QFrac) else other))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return QFrac(self.v - (other.v if isinstance(other, QFrac) else other))

    def __rsub__(self, other):
        return QFrac(other) - self

    def __mul__(self, other):
        return QFrac(self.v * (other.v if isinstance(other, QFrac) else other))

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return QFrac(self.v / (other.v if isinstance(other, QFrac) else other))

    def __rtruediv__(self, other):
        return QFrac(other) / self


def zeros(sample, count):
    return [sample * 0 for _ in range(count)]


def matmul(left, right):
    width = len(left)
    zero = left[0][0] * 0
    return [
        [sum((left[i][k] * right[k][j] for k in range(width)), zero) for j in range(width)]
        for i in range(width)
    ]


def mat_add(left, right):
    return [[x + y for x, y in zip(row_l, row_r)] for row_l, row_r in zip(left, right)]


def mat_sub(left, right):
    return [[x - y for x, y in zip(row_l, row_r)] for row_l, row_r in zip(left, right)]


def identity(field, dim=24):
    zero, one = field(0), field(1)
    return [[one if i == j else zero for j in range(dim)] for i in range(dim)]


def coord(pair, scalar):
    return scalar * 12 + PINDEX[pair]


def permutation_matrix(perm, field):
    zero, one = field(0), field(1)
    columns = []
    for scalar in (0, 1):
        for pair in PAIRS:
            column = [zero] * 24
            column[coord(image_pair(perm, pair), scalar)] = one
            columns.append(column)
    return [[columns[j][i] for j in range(24)] for i in range(24)]


def scalar_matrix(projector, field):
    zero = field(0)
    columns = []
    for scalar in (0, 1):
        for pair in PAIRS:
            column = [zero] * 24
            for out_scalar in (0, 1):
                column[coord(pair, out_scalar)] = projector[out_scalar][scalar]
            columns.append(column)
    return [[columns[j][i] for j in range(24)] for i in range(24)]


def paid(label, projector, field):
    """D_label(N) = I + ([label] - I) N."""
    reflected = permutation_matrix(LABELS[label], field)
    operator = scalar_matrix(projector, field)
    return mat_add(mat_sub(identity(field), operator), matmul(reflected, operator))


def split_operator(rho_l, rho_m, field):
    zero, one = field(0), field(1)
    columns = []
    for scalar, perm in ((0, rho_l), (1, rho_m)):
        for pair in PAIRS:
            column = [zero] * 24
            column[coord(image_pair(perm, pair), scalar)] = one
            columns.append(column)
    return [[columns[j][i] for j in range(24)] for i in range(24)]


def phi_of(operator, field):
    """12 minus the dimension of {z in H: operator z in H}."""
    domain = [(pair, scalar) for pair in POS for scalar in (0, 1)]
    rows = []
    for negative in NEG:
        for scalar in (0, 1):
            row = [operator[coord(negative, scalar)][coord(pair, in_scalar)] for pair, in_scalar in domain]
            rows.append(row)
    rank, _ = rref(rows)
    return rank


def method_b_rows(rho_l, rho_m, label, projector, field):
    support_l, support_m = support(rho_l), support(rho_m)
    free = []
    for pair in PAIRS:
        if pair in support_l:
            free.append((pair, 0))
        if pair in support_m:
            free.append((pair, 1))
    if len(free) != 12:
        raise AssertionError(len(free))
    complement = [
        [field(1) - projector[0][0], field(0) - projector[0][1]],
        [field(0) - projector[1][0], field(1) - projector[1][1]],
    ]
    index = {item: position for position, item in enumerate(free)}
    perm = LABELS[label]
    rows = []
    for negative in NEG:
        for out_scalar in (0, 1):
            row = [field(0)] * 12
            for source, block in ((negative, complement), (image_pair(perm, negative), projector)):
                for in_scalar in (0, 1):
                    key = (source, in_scalar)
                    if key in index:
                        row[index[key]] = row[index[key]] + block[out_scalar][in_scalar]
            rows.append(row)
    return rows


def axis_p(field):
    zero, one = field(0), field(1)
    return [[one, zero], [zero, zero]]


def axis_q(field):
    zero, one = field(0), field(1)
    return [[zero, zero], [zero, one]]


def normal_forms(field):
    zero, one = field(0), field(1)
    return {
        "P": axis_p(field),
        "I-P": axis_q(field),
        "imL_ker11": [[one, -one], [zero, zero]],
        "imM_ker11": [[zero, zero], [-one, one]],
        "im11_kerL": [[zero, one], [zero, one]],
        "im11_kerM": [[one, zero], [one, zero]],
    }


def open_projector(parameter):
    den = parameter - 1
    return [[parameter / den, -1 / den], [parameter / den, -1 / den]]


def square_ok(projector):
    return matmul(projector, projector) == projector


def complement_of(projector, field):
    zero, one = field(0), field(1)
    return [[one - projector[0][0], zero - projector[0][1]], [zero - projector[1][0], one - projector[1][1]]]


def line_key(vector):
    x, y = vector
    if not x and not y:
        raise AssertionError("zero vector")
    if not x:
        return ("inf",)
    return ("slope", (y / x).v)


def all_projectors(field, mod):
    """Every rank-one idempotent, keyed by image and kernel line ids."""
    raw = {}
    raw[("e1",)] = (field(1), field(0))
    for slope in range(mod):
        raw[("s", slope)] = (field(slope), field(1))
    out = []
    for im_key, im in raw.items():
        for ker_key, ker in raw.items():
            if im_key == ker_key:
                continue
            a, b = im
            c, d = ker
            det = a * d - b * c
            scale_e1 = d / det
            scale_e2 = -c / det
            projector = [[scale_e1 * a, scale_e2 * a], [scale_e1 * b, scale_e2 * b]]
            out.append((im, ker, projector))
    return out


def mul2(left, right):
    return [
        [left[0][0] * right[0][0] + left[0][1] * right[1][0], left[0][0] * right[0][1] + left[0][1] * right[1][1]],
        [left[1][0] * right[0][0] + left[1][1] * right[1][0], left[1][0] * right[0][1] + left[1][1] * right[1][1]],
    ]


def projector_from_lines(im, ker):
    a, b = im
    c, d = ker
    det = a * d - b * c
    scale_e1 = d / det
    scale_e2 = -c / det
    return [[scale_e1 * a, scale_e2 * a], [scale_e1 * b, scale_e2 * b]]


def word_matrix(factors, field):
    """factors are left to right; the rightmost factor is applied first."""
    acc = identity(field)
    for label, projector in reversed(factors):
        acc = matmul(paid(label, projector, field), acc)
    return acc


def expected_open_pivots(side, label, mod=None):
    parameter = mu_var(mod)
    unit = one_rf(mod)
    if (side, label) == ("s", "t"):
        return [unit / (parameter - unit), -parameter, unit / parameter, -(unit / (parameter - unit))]
    if (side, label) == ("t", "s"):
        gap = -(unit / (parameter - unit))
        return [gap, gap, unit, unit]
    if (side, label) == ("s", "u"):
        gap = -(unit / (parameter - unit))
        return [unit, gap, unit, gap, unit, parameter / (parameter - unit)]
    if (side, label) == ("t", "u"):
        return [
            unit,
            unit,
            -(unit / (parameter - unit)),
            unit,
            unit / (parameter - unit),
            parameter / (parameter - unit),
        ]
    raise AssertionError((side, label))


def field_of(mod):
    return lambda value, mod=mod: Prime(value, mod)


def main():
    check = Check()
    check.eq(compose(S, T), ST, "st one-line")
    check.eq(compose(compose(S, T), S), W, "sts")
    check.eq(compose(compose(T, S), T), W, "tst")
    check.eq(inversions(W), 3, "inv w")
    check.eq(compose(W, S), ST, "w s")
    check.eq(inversions(compose(W, S)), 2, "inv w s")
    check.eq(compose(W, T), (3, 1, 2, 4), "w t one-line")
    check.eq(inversions(compose(W, T)), 2, "inv w t")
    check.eq(compose(W, U), (3, 2, 4, 1), "w u one-line")
    check.eq(inversions(compose(W, U)), 4, "inv w u")
    check.eq(inversions(ST), 2, "inv st")

    paper = peel_table(S, ST)
    check.eq(paper, {"s": ("M", "L"), "t": ("L", "M"), "u": ("A", "0")}, "st table")
    check.eq(reading(*paper["s"]), "P", "st forces s to P")
    check.eq(reading(*paper["t"]), "I-P", "st forces t to I-P")
    check.eq(reading(*paper["u"]), "impossible", "st forbids u")

    rho = {"s": compose(W, S), "t": compose(W, T)}
    tables = {side: peel_table(rho[side], W) for side in ("s", "t")}
    check.eq(tables["s"], {"s": ("L", "M"), "t": ("0", "A"), "u": ("A", "0")}, "braid table after s")
    check.eq(tables["t"], {"s": ("0", "A"), "t": ("L", "M"), "u": ("A", "0")}, "braid table after t")
    check.true(tables["s"]["s"] != paper["s"], "st s-row does not transfer to this endpoint")
    check.eq(reading(*tables["s"]["s"]), "I-P", "repeated s forces the complement")
    check.eq(reading(*tables["s"]["t"]), "any", "adjacent t is free")
    check.eq(reading(*tables["s"]["u"]), "impossible", "u is forbidden after s")
    check.eq(reading(*tables["t"]["t"]), "I-P", "repeated t forces the complement")
    check.eq(reading(*tables["t"]["s"]), "any", "adjacent s is free")
    check.eq(reading(*tables["t"]["u"]), "impossible", "u is forbidden after t")
    for side in ("s", "t"):
        check.eq((support(rho[side]), support(W)), S_PEEL_SUPPORT[side], "hand-listed support " + side)

    parameter = mu_var()
    generic = open_projector(parameter)
    check.true(square_ok(generic), "open family is a projector over Q(mu)")
    for side, label, expect_rank in (("s", "t", 4), ("t", "s", 4), ("s", "u", 6), ("t", "u", 6)):
        rank, pivots = rref(method_b_rows(rho[side], W, label, generic, lambda value: RF((value,))))
        check.eq(rank, expect_rank, f"Q(mu) rank {side}/{label}")
        check.eq(pivots, expected_open_pivots(side, label), f"Q(mu) pivots {side}/{label}")
        check.true(all(pivot_factors_are_mu_or_mu_minus_one(pivot) for pivot in pivots), f"pivot factors {side}/{label}")
    for mod in (2, 3, 5, 7):
        family = open_projector(mu_var(mod))
        check.true(square_ok(family), f"open family projector mod {mod}")
        maker = lambda value, mod=mod: RF((value,), mod=mod)
        for side, label, expect_rank in (("s", "t", 4), ("t", "s", 4), ("s", "u", 6), ("t", "u", 6)):
            rank, pivots = rref(method_b_rows(rho[side], W, label, family, maker))
            check.eq(rank, expect_rank, f"F{mod}(mu) rank {side}/{label}")
            check.eq(pivots, expected_open_pivots(side, label, mod), f"F{mod}(mu) pivots {side}/{label}")

    q = lambda value: QFrac(value)
    forms = normal_forms(q)
    for name, projector in forms.items():
        check.true(square_ok(projector), "normal form projector " + name)
        for side, free in (("s", "t"), ("t", "s")):
            rank, pivots = rref(method_b_rows(rho[side], W, free, projector, q))
            check.eq((rank, len(pivots)), (4, 4), f"normal {name} free {free}")
            check.true(all(pivot in (1, -1) for pivot in pivots), f"unit pivots {name} {free}")
            rank_u, pivots_u = rref(method_b_rows(rho[side], W, "u", projector, q))
            check.eq((rank_u, len(pivots_u)), (6, 6), f"normal {name} u after {side}")
            check.true(all(pivot in (1, -1) for pivot in pivots_u), f"unit u pivots {name} {side}")
        rank_repeat, _ = rref(method_b_rows(rho["s"], W, "s", projector, q))
        check.eq(rank_repeat == 4, name == "I-P", "only the complement is a tight repeated s factor: " + name)

    # Dense rational witnesses, independent of the rational-function eliminator.
    split_s = split_operator(rho["s"], W, q)
    samples = {
        "open2": open_projector(q(2)),
        "open3": open_projector(q(3)),
        "bad": [[q(0), q(0)], [q(1), q(-1)]],
        "imM": forms["imM_ker11"],
        "P": forms["P"],
        "I-P": forms["I-P"],
    }
    check.true(not square_ok(samples["bad"]), "rejection matrix is not a projector")
    check.eq(phi_of(matmul(split_s, paid("t", samples["bad"], q)), q), 5, "nonprojector does not drop phi")
    check.eq(phi_of(matmul(split_s, paid("t", samples["imM"], q)), q), 4, "projector onto M along span(1,1)")
    check.eq(phi_of(matmul(split_s, paid("t", samples["open2"], q)), q), 4, "dense phi at mu=2")
    check.eq(phi_of(matmul(split_s, paid("t", samples["open3"], q)), q), 4, "dense phi at mu=3")
    check.eq(phi_of(matmul(split_s, paid("u", samples["open2"], q)), q), 6, "dense u phi at mu=2")
    check.eq(phi_of(matmul(split_s, paid("s", samples["P"], q)), q), 6, "wrong repeated projector raises phi")
    check.eq(phi_of(matmul(split_s, paid("s", samples["I-P"], q)), q), 4, "complement repeated projector")
    forced = word_matrix([("s", samples["P"]), ("s", samples["I-P"])], q)
    # The two-factor word is the right end: T times that word equals [st].
    reached = matmul(permutation_matrix(W, q), word_matrix([("s", samples["P"]), ("s", samples["I-P"])], q))
    check.eq(reached, permutation_matrix(ST, q), "forced s continuation is the pure permutation st")
    check.eq(phi_of(permutation_matrix(W, q), q), 6, "phi of the plane endpoint")
    check.eq(phi_of(permutation_matrix(S, q), q), 2, "phi of a pure transposition")
    check.eq(phi_of(paid("t", samples["open2"], q), q), 1, "one open paid factor has phi 1")
    check.eq(forced, permutation_matrix(S, q), "complement pair is the pure transposition")

    for mod in (2, 3, 5):
        field = field_of(mod)
        projectors = all_projectors(field, mod)
        check.eq(len(projectors), mod * (mod + 1), f"projector count F{mod}")
        split = {side: split_operator(rho[side], W, field) for side in ("s", "t")}
        pure = {name: permutation_matrix(perm, field) for name, perm in {"w": W, "s": S, "t": T, "u": U, "st": ST, "wt": compose(W, T)}.items()}
        counts = {side: {"s": 0, "t": 0, "u": 0} for side in ("s", "t")}
        u_phi = {side: set() for side in ("s", "t")}
        unique = {side: [] for side in ("s", "t")}
        repeated = {"s": "s", "t": "t"}
        for _im, _ker, projector in projectors:
            comp = complement_of(projector, field)
            for label in ("s", "t", "u"):
                factor = paid(label, projector, field)
                check.eq(matmul(factor, factor), identity(field), f"D^2 F{mod} {label}")
                check.eq(phi_of(factor, field), 1, f"factor phi F{mod} {label}")
                check.eq(matmul(paid(label, projector, field), paid(label, comp, field)), pure[label], f"doubled generator F{mod} {label}")
            for side in ("s", "t"):
                for label, expect in (("s", 5), ("t", 5), ("u", 7)):
                    first = matmul(pure["w"], paid(label, projector, field))
                    check.eq(phi_of(first, field), expect, f"first peel F{mod} {label}")
                for label in ("s", "t", "u"):
                    composed = matmul(split[side], paid(label, projector, field))
                    phi_a = phi_of(composed, field)
                    rank_b, _ = rref(method_b_rows(rho[side], W, label, projector, field))
                    check.eq(phi_a, rank_b, f"engines F{mod} {side} {label}")
                    if phi_a == 4:
                        counts[side][label] += 1
                        if label == repeated[side]:
                            unique[side].append(projector)
                    if label == "u":
                        u_phi[side].add(phi_a)
            sts = [("s", projector), ("s", comp), ("t", projector), ("t", comp), ("s", projector), ("s", comp)]
            tst = [("t", projector), ("t", comp), ("s", projector), ("s", comp), ("t", projector), ("t", comp)]
            check.eq(word_matrix(sts, field), pure["w"], f"doubled sts F{mod}")
            check.eq(word_matrix(tst, field), pure["w"], f"doubled tst F{mod}")
            reached_s = matmul(pure["w"], word_matrix([("s", projector), ("s", comp)], field))
            reached_t = matmul(pure["w"], word_matrix([("t", projector), ("t", comp)], field))
            check.eq(reached_s, pure["st"], f"forced remainder st F{mod}")
            check.eq(reached_t, pure["wt"], f"forced remainder wt F{mod}")
        check.eq(counts["s"], {"s": 1, "t": len(projectors), "u": 0}, f"census after s F{mod}")
        check.eq(counts["t"], {"s": len(projectors), "t": 1, "u": 0}, f"census after t F{mod}")
        check.eq(u_phi, {"s": {6}, "t": {6}}, f"u phi F{mod}")
        check.eq(unique["s"], [axis_q(field)], f"unique s projector F{mod}")
        check.eq(unique["t"], [axis_q(field)], f"unique t projector F{mod}")

        # Every projector is the diagonal transport of one checked normal form.
        seen = {"P": 0, "I-P": 0, "imL": 0, "imM": 0, "kerL": 0, "kerM": 0, "open": 0}
        for im, ker, projector in projectors:
            im_key, ker_key = line_key(im), line_key(ker)
            if im_key == ("slope", 0) and ker_key == ("inf",):
                seen["P"] += 1
                check.eq(projector, axis_p(field), f"monomial P F{mod}")
            elif im_key == ("inf",) and ker_key == ("slope", 0):
                seen["I-P"] += 1
                check.eq(projector, axis_q(field), f"monomial I-P F{mod}")
            elif im_key == ("slope", 0) and ker_key[0] == "slope" and ker_key[1] != 0:
                seen["imL"] += 1
                check.eq(projector, transport_line("imL", ker_key[1], field), f"transport imL F{mod}")
            elif im_key == ("inf",) and ker_key[0] == "slope" and ker_key[1] != 0:
                seen["imM"] += 1
                check.eq(projector, transport_line("imM", ker_key[1], field), f"transport imM F{mod}")
            elif ker_key == ("slope", 0) and im_key[0] == "slope" and im_key[1] != 0:
                seen["kerL"] += 1
                check.eq(projector, transport_line("kerL", im_key[1], field), f"transport kerL F{mod}")
            elif ker_key == ("inf",) and im_key[0] == "slope" and im_key[1] != 0:
                seen["kerM"] += 1
                check.eq(projector, transport_line("kerM", im_key[1], field), f"transport kerM F{mod}")
            elif im_key[0] == "slope" and ker_key[0] == "slope" and im_key[1] not in (0,) and ker_key[1] not in (0, im_key[1]):
                seen["open"] += 1
                check.eq(projector, transport_open(im_key[1], ker_key[1], field), f"transport open F{mod}")
            else:
                check.true(False, f"unclassified projector F{mod} {im_key} {ker_key}")
        tilted = mod - 1
        check.eq(seen["P"], 1, f"one P F{mod}")
        check.eq(seen["I-P"], 1, f"one I-P F{mod}")
        check.eq(seen["imL"], tilted, f"imL orbits F{mod}")
        check.eq(seen["imM"], tilted, f"imM orbits F{mod}")
        check.eq(seen["kerL"], tilted, f"kerL orbits F{mod}")
        check.eq(seen["kerM"], tilted, f"kerM orbits F{mod}")
        check.eq(seen["open"], tilted * (tilted - 1), f"open orbits F{mod}")

    # The literal non-example from the derivation: [[0,0],[1,-1]] is not the
    # projector onto the second axis along span(1,1).
    check.eq(forms["imM_ker11"], [[q(0), q(0)], [q(-1), q(1)]], "honest projector onto M")

    print(
        "PASS_BRAID_ENDPOINT_MIXED_PEEL"
        f" checks={check.count}"
        " endpoint=3214 phi=6"
        " first=s|t every rank-one projector, u phi=7"
        " second repeated label only I-P"
        " free label every rank-one projector phi=4"
        " u phi=6"
        " open pivots in the group generated by mu and mu-1"
        " normal pivots units"
        " no kappa"
    )


def transport_open(im_slope, ker_slope, field):
    ratio = field(ker_slope) / field(im_slope)
    base = open_projector(ratio)
    scale = field(im_slope)
    change = [[field(1), field(0)], [field(0), scale]]
    inverse = [[field(1), field(0)], [field(0), field(1) / scale]]
    return mul2(change, mul2(base, inverse))


def transport_line(kind, slope, field):
    forms = normal_forms(field)
    base = {
        "imL": forms["imL_ker11"],
        "imM": forms["imM_ker11"],
        "kerL": forms["im11_kerL"],
        "kerM": forms["im11_kerM"],
    }[kind]
    scale = field(slope)
    change = [[field(1), field(0)], [field(0), scale]]
    inverse = [[field(1), field(0)], [field(0), field(1) / scale]]
    return mul2(change, mul2(base, inverse))


if __name__ == "__main__":
    main()
