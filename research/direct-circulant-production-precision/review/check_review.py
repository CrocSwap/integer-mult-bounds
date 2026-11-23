"""Independent literal-word and cache-lineage audit for the precision theorem.

No author verifier, precision selector or compiler matrix class is imported.
Only the small exact functions under review are extracted from pinned source.
The independent matrix interpreter uses Gaussian rationals; the odometer oracle
uses noncommutative expression trees, so cancellations cannot hide stale data.
"""
import ast
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import prod, comb
from pathlib import Path
import sys

PACKAGE = Path('research/direct-circulant-production-precision')
HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


@dataclass(frozen=True)
class Z:
    re: Q = Q(0)
    im: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, 're', Q(self.re))
        object.__setattr__(self, 'im', Q(self.im))

    @staticmethod
    def lift(z):
        return z if isinstance(z, Z) else Z(Q(z))

    def __add__(self, other):
        other = Z.lift(other)
        return Z(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return Z(-self.re, -self.im)

    def __sub__(self, other):
        return self + (-Z.lift(other))

    def __rsub__(self, other):
        return Z.lift(other) - self

    def __mul__(self, other):
        other = Z.lift(other)
        return Z(self.re * other.re - self.im * other.im,
                 self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = Z.lift(other)
        denominator = other.norm2()
        return Z((self.re * other.re + self.im * other.im) / denominator,
                 (self.im * other.re - self.re * other.im) / denominator)

    def __rtruediv__(self, other):
        return Z.lift(other) / self

    def norm2(self):
        return self.re ** 2 + self.im ** 2

    def component_norm(self):
        return abs(self.re) + abs(self.im)


ZERO, ONE = Z(), Z(Q(1))
IDENTITY = ((ONE, ZERO), (ZERO, ONE))
H = ((ONE, ONE), (ONE, -ONE))
SWAP = ((ZERO, ONE), (ONE, ZERO))


def matmul(a, b):
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(2)), ZERO)
                       for j in range(2)) for i in range(2))


def inverse(a):
    d = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return ((a[1][1] / d, -a[0][1] / d), (-a[1][0] / d, a[0][0] / d))


def bound(a):
    return max(sum(z.component_norm() for z in row) for row in (*a, *zip(*a)))


def authenticated(name):
    pins = json.loads((PACKAGE / 'ORIGINS.json').read_text())['files']
    pin = next(p for p in pins if p['file'] == name)
    raw = (PACKAGE / 'retained' / name).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'source differs: ' + name)
    return raw


def functions(raw, names, namespace):
    module = ast.parse(raw)
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    need({node.name for node in body} == set(names), 'missing literal source function')
    exec(compile(ast.Module(body=body, type_ignores=[]), '<reviewed literal functions>', 'exec'), namespace)
    return namespace


class Diagonal(tuple):
    def __new__(cls, value, primitive):
        result = tuple.__new__(cls, value)
        result.primitive = primitive
        return result


def source_word_namespace(fault=False):
    names = ('diagonal_product', 'chain', 'swap_word', 'upper_three', 'upper_six', 'lower_pair')
    raw = authenticated('root_gate_plan.py')
    if fault:
        raw = raw.replace(b'Fraction(-1, 6)', b'Fraction(1, 6)')
    env = functions(raw, names, {'Fraction': Q})
    for name, label in [('upper_three', 'three-H diagonal'), ('swap_word', 'switch diagonal')]:
        original = env[name]
        def wrap(value, original=original, label=label):
            return [Diagonal(d, [(label, d)]) for d in original(value)]
        env[name] = wrap

    def join(a, b):
        origins_a = a.primitive if isinstance(a, Diagonal) else [('pivot', a)]
        origins_b = b.primitive if isinstance(b, Diagonal) else [('pivot', b)]
        return Diagonal((a[0] * b[0], a[1] * b[1]), origins_a + origins_b)
    env['diagonal_product'] = join
    return env


def execute(diagonals):
    value = IDENTITY
    for i, diagonal in enumerate(diagonals):
        d = ((Z.lift(diagonal[0]), ZERO), (ZERO, Z.lift(diagonal[1])))
        value = matmul(d, value)
        if i + 1 != len(diagonals):
            value = matmul(H, value)
    return value


def literal_word_check():
    env = source_word_namespace()
    ratios = [ZERO, Z(Q(1, 2)), Z(Q(-1, 2)), Z(Q(0), Q(1, 2)), Z(Q(0), Q(-1, 2))]
    cases = 0
    pivot_locations = set()
    for x, y, scale, schur_ratio, left_swap, right_swap in product(
            ratios, ratios, [Q(1), Q(1, 2**20), Q(2**20)],
            [Q(1, 4), Q(1, 2**24)], [False, True], [False, True]):
        a, s = Z(scale), Z(scale * schur_ratio)
        gate = ((a, a * x), (a * y, a * y * x + s))
        if left_swap:
            gate = matmul(SWAP, gate)
        if right_swap:
            gate = matmul(gate, SWAP)
        pivot_locations.add(max(product(range(2), repeat=2), key=lambda ij: gate[ij[0]][ij[1]].norm2()))
        word = env['lower_pair'](gate)
        need(len(word) == 17 and execute(word) == gate, 'literal sixteen-H identity')
        primitive = [item for diag in word for item in diag.primitive]
        need(len(primitive) == 23, 'fully expanded primitive diagonal count')
        need(sum(label == 'pivot' for label, _ in primitive) == 1, 'one pivot factor')
        L = max(Q(1), bound(gate), bound(inverse(gate)))
        for label, diagonal in primitive:
            cap = 2 * L if label == 'pivot' else Q(64)
            for entry in diagonal:
                z = Z.lift(entry)
                need(z.norm2() != 0 and z.norm2() <= cap**2 and (ONE / z).norm2() <= cap**2,
                     'primitive and inverse factor bound')
        cases += 1
    mutated = source_word_namespace(fault=True)['lower_pair'](((Z(3), Z(1)), (Z(1), Z(2))))
    need(execute(mutated) != ((Z(3), Z(1)), (Z(1), Z(2))), 'middle-phase mutation escaped')
    return {'cases': cases, 'pivot_locations': sorted(pivot_locations),
            'fully_expanded_diagonals': 23, 'H_factors': 16,
            'nonpivot_factors': 38, 'retained_nonpivot_envelope': 40,
            'negative_control': 'sign in upper_three final diagonal changes endpoint'}


IDENTITY_TREE = ('identity',)


class TreeGrid:
    one = IDENTITY_TREE

    def multiply(self, x, y):
        if x == self.one:
            return y
        if y == self.one:
            return x
        return ('multiply', x, y)


def expected_tree(sides, ordinal):
    coefficient = IDENTITY_TREE
    indices = []
    for size in sides:
        ordinal, digit = divmod(ordinal, size)
        indices.append(digit)
    for axis in reversed(range(len(sides))):
        coefficient = TreeGrid().multiply(('factor', axis, indices[axis]), coefficient)
    return coefficient


def lineage_case(sides, function):
    tables = [[('factor', axis, digit) for digit in range(size)] for axis, size in enumerate(sides)]
    data = [('data', i) for i in range(prod(sides))]
    function(data, tables, TreeGrid())
    for i, actual in enumerate(data):
        expected = ('multiply', expected_tree(sides, i), ('data', i))
        need(actual == expected, 'odometer uses a stale/noncurrent coefficient subtree')
    return len(data)


def lineage_check():
    raw = authenticated('tensor_word.py')
    good = functions(raw, ['product_diagonal'], {'prod': prod})['product_diagonal']
    shapes = [(2,) * d for d in range(1, 9)] + [(2, 4, 8), (8, 2, 4, 2), (4, 4, 2, 8), (2, 8, 2, 4, 2)]
    records = sum(lineage_case(shape, good) for shape in shapes)
    mutant = raw.replace(b'for k in range(j, 0, -1):', b'for k in range(j-1, 0, -1):')
    bad = functions(mutant, ['product_diagonal'], {'prod': prod})['product_diagonal']
    try:
        lineage_case((2, 2), bad)
    except ValueError as error:
        need('stale/noncurrent' in str(error), 'wrong lineage mutation gate')
    else:
        raise ValueError('stale cache mutation survived')
    return {'cases': len(shapes), 'records': records,
            'oracle': 'exact current-coordinate right-associated expression tree, no numeric cancellation',
            'negative_control': 'skip newly changed suffix at a carry'}


def mul_poly(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def source_stage_bound():
    D = [1, 288, 584, 256, 32]
    # Literal matching: 17 diagonals + 16 H; 2*(2ell-1) switches,
    # each with three diagonals + two H. Therefore 20ell+23 steps.
    literal_two_roots = [2 * x for x in mul_poly(D, [23, 20])]
    J = [20000 * comb(6, i) * 2**(6-i) for i in range(7)]
    constant = J.copy()
    constant[0] -= 2
    d_coefficient = [J[i] - (literal_two_roots[i] if i < len(literal_two_roots) else 0)
                     for i in range(len(J))]
    need(all(x > 0 for x in constant + d_coefficient), 'literal stage-count polynomial')
    return {'actual_steps_per_matching': '20*ell+23',
            'literal_two_root_depth_coefficients': literal_two_roots,
            'J_minus_actual_constant_coefficients': constant,
            'J_minus_actual_d_coefficients': d_coefficient}


def main():
    global PACKAGE
    need(len(sys.argv) <= 2, 'usage: check_review.py [package-directory]')
    PACKAGE = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else PACKAGE.resolve()
    result = {'literal_word': literal_word_check(),
              'odometer_lineage': lineage_check(), 'literal_stage_count': source_stage_bound(),
              'scope': 'Independent source/schema checks; universal inequalities are in CROSS-REVIEW.md'}
    print(json.dumps(result, indent=2))
    print('PASS_INDEPENDENT_PRECISION_CROSS_REVIEW')


if __name__ == '__main__':
    main()
