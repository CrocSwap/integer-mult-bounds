"""Exact dyadically scaled Stein generators over Q(i).

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. The construction refines the retained rational Gram-Schmidt route.
"""
from fractions import Fraction as Q

MAX_HEIGHT = 0


def need(ok, message):
    if not ok:
        raise ValueError(message)


def observe(x):
    global MAX_HEIGHT
    x = Q(x)
    MAX_HEIGHT = max(MAX_HEIGHT, abs(x.numerator).bit_length(), x.denominator.bit_length())
    return x


class C:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        need(type(re) in (int, Q) and type(im) in (int, Q), "exact complex rational components")
        self.re, self.im = observe(re), observe(im)

    @staticmethod
    def wrap(x):
        return x if isinstance(x, C) else C(x)

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
        return observe(self.re ** 2 + self.im ** 2)

    def __truediv__(self, other):
        other = C.wrap(other)
        denominator = other.norm2()
        need(denominator != 0, "nonzero complex divisor")
        product = self * other.conjugate()
        return C(product.re / denominator, product.im / denominator)

    def __rtruediv__(self, other):
        return C.wrap(other) / self

    def __bool__(self):
        return bool(self.re or self.im)

    def __eq__(self, other):
        if not isinstance(other, C) and type(other) not in (int, Q):
            return False
        other = C.wrap(other)
        return self.re == other.re and self.im == other.im

    def record(self):
        return [str(self.re), str(self.im)]


class Vector(list):
    def __truediv__(self, scalar):
        return Vector(C.wrap(x) / scalar for x in self)


class Matrix(list):
    def __init__(self, rows):
        super().__init__([[C.wrap(x) for x in row] for row in rows])

    def __rmul__(self, scalar):
        return Matrix([[C.wrap(x) * scalar for x in row] for row in self])


def inner(left, right):
    return sum((C.wrap(x).conjugate() * C.wrap(y) for x, y in zip(left, right)), C())


def norm2(vector):
    return observe(sum((C.wrap(x).norm2() for x in vector), Q(0)))


def component_l1(vector):
    return observe(sum((abs(C.wrap(x).re) + abs(C.wrap(x).im) for x in vector), Q(0)))


def pow2(exponent):
    return Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)


def norm_scale(squared):
    need(squared > 0, "positive residual squared norm")
    exponent = (squared.numerator.bit_length() - squared.denominator.bit_length()) // 2
    scale = pow2(exponent)
    while scale * scale < squared:
        exponent += 1
        scale *= 2
    while scale * scale / 4 >= squared:
        exponent -= 1
        scale /= 2
    need(squared <= scale * scale < 4 * squared, "dyadic norm bracket")
    observe(scale)
    return scale, exponent


def upper_dyadic(value):
    need(value > 0, "positive dyadic upper target")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    result = pow2(exponent)
    while result < value:
        result *= 2
    while result / 2 >= value:
        result /= 2
    return observe(result)


def height(matrix):
    return max([1] + [max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                      for row in matrix for entry in row
                      for x in (C.wrap(entry).re, C.wrap(entry).im)])


def generators(displacement):
    """Return column g, explicit coefficient ROW r, and a dyadic admission scale."""
    global MAX_HEIGHT
    displacement = Matrix(displacement)
    size = len(displacement)
    need(size > 0 and all(len(row) == size for row in displacement), "nonempty square displacement")
    input_height = height(displacement)
    MAX_HEIGHT = input_height
    columns = [[displacement[i][j] for i in range(size)] for j in range(size)]
    residuals, result = [], []
    for column_index, column in enumerate(columns):
        residual = list(column)
        for old, squared in residuals:
            factor = inner(old, residual) / squared
            residual = [x - factor * y for x, y in zip(residual, old)]
        squared = norm2(residual)
        if squared == 0:
            continue
        scale, exponent = norm_scale(squared)
        g = Vector(x / scale for x in residual)
        row = Vector(inner(residual, c) * (scale / squared) for c in columns)
        gamma = upper_dyadic(max(Q(1), 2 * component_l1(row)))
        need(norm2(g) <= 1 and 2 * component_l1(row) <= gamma, "bounded generator admission")
        residuals.append((residual, squared))
        result.append({"column": column_index, "residual": residual, "squared_norm": squared,
                       "scale": scale, "scale_exponent": exponent, "g": g, "row": row,
                       "gamma": gamma})
    return result, {"input_height": input_height, "max_observed_height": MAX_HEIGHT}


def lower(vector):
    return Matrix([[vector[i - j] if i >= j else C() for j in range(len(vector))]
                   for i in range(len(vector))])


def transpose(matrix):
    return Matrix(zip(*matrix))


def frobenius2(matrix):
    return observe(sum((C.wrap(x).norm2() for row in matrix for x in row), Q(0)))


def norm_bound(matrix):
    """Rational upper bound for the induced 2-norm."""
    return max(max(component_l1(row) for row in matrix),
               max(component_l1(column) for column in zip(*matrix)))


def exact_record(matrix):
    return [[C.wrap(x).record() for x in row] for row in matrix]
