"""Exact complex rational arithmetic for coefficient and rounded-gate certificates.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256

TRACK = None


def need(ok, message):
    if not ok:
        raise ValueError(message)


def qheight(value):
    return max(abs(value.numerator).bit_length(), value.denominator.bit_length())


class C:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        need(type(re) in (int, Q) and type(im) in (int, Q), "exact rational components")
        self.re, self.im = Q(re), Q(im)
        if TRACK is not None:
            TRACK["max_observed_height"] = max(TRACK["max_observed_height"],
                                               qheight(self.re), qheight(self.im))

    @staticmethod
    def wrap(value):
        return value if isinstance(value, C) else C(value)

    def __add__(self, other):
        other = C.wrap(other)
        return C(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return C(-self.re, -self.im)

    def __sub__(self, other):
        return self + -C.wrap(other)

    def __rsub__(self, other):
        return C.wrap(other) + -self

    def __mul__(self, other):
        other = C.wrap(other)
        return C(self.re * other.re - self.im * other.im,
                 self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def conjugate(self):
        return C(self.re, -self.im)

    def norm2(self):
        return self.re * self.re + self.im * self.im

    def __truediv__(self, other):
        other = C.wrap(other)
        denominator = other.norm2()
        need(denominator > 0, "nonzero divisor")
        product = self * other.conjugate()
        return C(product.re / denominator, product.im / denominator)

    def __rtruediv__(self, other):
        return C.wrap(other) / self

    def __eq__(self, other):
        if not isinstance(other, C) and type(other) not in (int, Q):
            return False
        other = C.wrap(other)
        return self.re == other.re and self.im == other.im

    def record(self):
        return [str(self.re), str(self.im)]


class Vec(list):
    def __init__(self, values):
        super().__init__(C.wrap(x) for x in values)

    def __mul__(self, other):
        if isinstance(other, C) or type(other) in (int, Q):
            return Vec(x * other for x in self)
        need(len(self) == len(other), "elementwise vector dimensions")
        return Vec(x * y for x, y in zip(self, other))

    __rmul__ = __mul__

    def __sub__(self, other):
        need(len(self) == len(other), "vector subtraction dimensions")
        return Vec(x - y for x, y in zip(self, other))

    def copy(self):
        return Vec(self)

    def __truediv__(self, scalar):
        return Vec(x / scalar for x in self)


class Mat(list):
    def __init__(self, rows):
        super().__init__([C.wrap(x) for x in row] for row in rows)

    def __rmul__(self, scalar):
        return Mat([[scalar * x for x in row] for row in self])

    @property
    def shape(self):
        return (len(self), len(list.__getitem__(self, 0)) if self else 0)

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            return list.__getitem__(self, key)
        row, column = key
        if isinstance(row, slice):
            rows = list.__getitem__(self, row)
            return Mat([r[column] for r in rows]) if isinstance(column, slice) else Vec(r[column] for r in rows)
        selected = list.__getitem__(self, row)
        return Vec(selected[column]) if isinstance(column, slice) else selected[column]


def eye(n):
    return Mat([[int(i == j) for j in range(n)] for i in range(n)])


def adjoint(matrix):
    return Mat([[matrix[j][i].conjugate() for j in range(len(matrix))]
                for i in range(len(matrix[0]))])


def multiply(left, right):
    return Mat([[sum((x * right[k][j] for k, x in enumerate(row)), C())
                 for j in range(len(right[0]))] for row in left])


def unitary(matrix):
    return multiply(adjoint(matrix), matrix) == eye(len(matrix))


def inverse_gate(matrix):
    if unitary(matrix):
        return adjoint(matrix)
    if matrix.shape == (1, 1):
        return Mat([[1 / matrix[0][0]]])
    if matrix.shape == (2, 2) and matrix[0][0] == matrix[1][1] == 1 and matrix[0][1] == 0:
        return Mat([[1, 0], [-matrix[1][0], 1]])
    raise ValueError("unsupported nonunitary inverse gate")


def round_q(value, bits):
    scale = 1 << bits
    shifted = value * scale + Q(1, 2)
    return Q(shifted.numerator // shifted.denominator, scale)


def rounded(value, bits):
    return C(round_q(value.re, bits), round_q(value.im, bits))


def norm2(vector):
    return sum((x.norm2() for x in vector), Q(0))


def component_l1(vector):
    return sum((abs(x.re) + abs(x.im) for x in vector), Q(0))


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive logarithm bound")
    result = value.numerator.bit_length() - value.denominator.bit_length()
    power = Q(1 << result) if result >= 0 else Q(1, 1 << -result)
    while power < value:
        result += 1
        power *= 2
    while power / 2 >= value:
        result -= 1
        power /= 2
    return result


def upper(value, bits=160):
    scale = 1 << bits
    scaled = value * scale
    return Q(-((-scaled.numerator) // scaled.denominator), scale)


def vector_hash(vector):
    digest = sha256()
    for entry in vector:
        for value in (entry.re, entry.im):
            for integer in (value.numerator, value.denominator):
                raw = abs(integer).to_bytes(max(1, (abs(integer).bit_length() + 7) // 8), "big")
                digest.update(bytes([integer < 0]))
                digest.update(len(raw).to_bytes(8, "big"))
                digest.update(raw)
    return digest.hexdigest()


def apply(plan, vector, bits=None):
    global TRACK
    state = Vec(vector)
    old_track = TRACK
    stats = {"max_observed_height": 0, "max_grid_numerator_bits": 0,
             "max_reduced_fractional_bits": 0, "rounded_outputs": 0}
    if bits is not None:
        need(bits >= 1, "positive data precision")
        for entry in state:
            for value in (entry.re, entry.im):
                need((value * (1 << bits)).denominator == 1, "input already on data grid")
        TRACK = stats
    try:
        for layer in plan:
            used = set()
            for ids, gate in layer:
                need(len(ids) == len(gate) in (1, 2), "one- or two-wire gate")
                need(not used.intersection(ids) and len(set(ids)) == len(ids), "disjoint layer")
                need(all(0 <= i < len(state) for i in ids), "wire bounds")
                used.update(ids)
                before = [state[i] for i in ids]
                outputs = [sum((a * x for a, x in zip(row, before)), C()) for row in gate]
                for i, value in zip(ids, outputs):
                    if bits is not None:
                        value = rounded(value, bits)
                        stats["rounded_outputs"] += 1
                        for part in (value.re, value.im):
                            grid_integer = part * (1 << bits)
                            need(grid_integer.denominator == 1, "rounded output grid")
                            stats["max_grid_numerator_bits"] = max(stats["max_grid_numerator_bits"],
                                                                    abs(grid_integer.numerator).bit_length())
                            stats["max_reduced_fractional_bits"] = max(stats["max_reduced_fractional_bits"],
                                                                     part.denominator.bit_length() - 1)
                    state[i] = value
    finally:
        TRACK = old_track
    return state, stats
