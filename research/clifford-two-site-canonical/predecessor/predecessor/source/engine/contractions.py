"""Exact Clifford contractions with absolute phase. Apache-2.0.

Classical affine-support and quadratic Gauss-sum methods. Prepared by
Ali Romman with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def load_source(name, filename):
    records = json.loads((ROOT / 'INPUTS.json').read_text())
    record = next(x for x in records if x['local'] == filename)
    path = ROOT / 'source' / filename
    if sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('Changed frozen input: ' + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


Q = load_source('contraction_quadratic', 'PR5704-quadratic.py')


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def conjugate(a):
    return a[0], -a[1]


def power(a, exponent):
    Q.need(type(exponent) is int and exponent >= 0, 'Nonnegative integral exponent')
    result = (1, 0)
    while exponent:
        if exponent & 1:
            result = Q.multiply(result, a)
        a = Q.multiply(a, a)
        exponent >>= 1
    return result


def solution(n, equations):
    """Return every binary solution as affine coordinate forms, or None."""
    rows = {}
    for mask, rhs in equations:
        Q.validate_integer(mask, 1 << n, 'Equation variable mask')
        Q.validate_integer(rhs, 2, 'Equation right side')
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = (mask, rhs)
                break
            other, value = rows[pivot]
            mask ^= other
            rhs ^= value
        if not mask and rhs:
            return None
    free = [j for j in range(n) if j not in rows]
    forms = [0] * n
    for k, j in enumerate(free):
        forms[j] = 1 << (k + 1)
    for pivot in sorted(rows):
        mask, rhs = rows[pivot]
        forms[pivot] = rhs
        for j in Q.bits(mask ^ (1 << pivot)):
            forms[pivot] ^= forms[j]
    return len(free), forms


def gauss(n, poly):
    """Return sum_x i**q(x) as an exact Gaussian integer."""
    Q.need(type(n) is int and n >= 0, 'Nonnegative Gauss dimension')
    for mask, coefficient in poly.items():
        Q.validate_integer(mask, 1 << n, 'Phase variable mask')
        Q.need(type(coefficient) is int and 0 < coefficient < 4,
               'Canonical nonzero phase coefficient')
        Q.need(mask.bit_count() <= 2 and (mask.bit_count() != 2 or coefficient == 2),
               'Only even quadratic terms')
    poly = dict(poly)
    scalar = (1, 0)
    while n:
        last = 1 << (n - 1)
        a = poly.pop(last, 0)
        linear = 0
        for mask in list(poly):
            if mask & last:
                linear ^= mask ^ last
                del poly[mask]
        n -= 1
        if a & 1:
            scalar = Q.multiply(scalar, (1, 1 if a == 1 else -1))
            Q.affine(poly, linear << 1, -a)
        elif linear:
            resolved = solution(n, [(linear, a // 2)])
            Q.need(resolved is not None, 'A nonzero linear form takes both values')
            n, forms = resolved
            poly = Q.substitute(poly, forms)
            scalar = (2 * scalar[0], 2 * scalar[1])
        elif a:
            return (0, 0)
        else:
            scalar = (2 * scalar[0], 2 * scalar[1])
    return Q.multiply_i(scalar, poly.get(0, 0))


def inner(left, right):
    """Return the exact inner product of two valid engine states.

    Inputs come from signature or choi. Arbitrary serialized states are not
    admitted without the source engine's construction contract.
    """
    n, offset, cols, terms, a, b, den = left
    m, other, cols2, terms2, c, d, den2 = right
    Q.need(n == m, 'Equal state dimensions')
    r = len(cols)
    allcols = cols + cols2
    equations = [(sum(((v >> i) & 1) << j for j, v in enumerate(allcols)),
                  ((offset ^ other) >> i) & 1) for i in range(n)]
    resolved = solution(len(allcols), equations)
    if resolved is None:
        return Fraction(0), Fraction(0)
    dimension, forms = resolved
    phase = Q.substitute(dict(terms2), forms[r:])
    for mask, coefficient in Q.substitute(dict(terms), forms[:r]).items():
        Q.term(phase, mask, -coefficient)
    total = Q.multiply(Q.multiply((a, -b), (c, d)), gauss(dimension, phase))
    return Fraction(total[0], 1 << (den + den2)), Fraction(total[1], 1 << (den + den2))


def choi(n, circuit):
    """Return a normalized Choi state, retaining one common Bell phase."""
    Q.need(type(n) is int and n >= 0, 'Nonnegative circuit width')
    preparation = [('C', (1 << j) | (1 << (n + j)), 1) for j in range(n)]
    preparation.append(('D', tuple(1 << j if j < n else 0 for j in range(2 * n)),
                        (1,) * n + (0,) * n))
    expanded = []
    for gate in circuit:
        # Validate the original arity and domain before extension.
        Q.signature(n, [gate])
        kind = gate[0]
        if kind == 'P':
            expanded.append(('P', tuple(gate[1]) + tuple(1 << j for j in range(n, 2 * n))))
        elif kind == 'D':
            expanded.append(('D', tuple(gate[1]) + (0,) * n, tuple(gate[2]) + (0,) * n))
        else:
            expanded.append(gate)
    return Q.signature(2 * n, preparation + expanded)


def trace(n, circuit):
    result = inner(choi(n, []), choi(n, circuit))
    return result[0] * (1 << n), result[1] * (1 << n)


def kernel(states):
    """Return normalized trace(U_i^* U_j) for valid equal-width circuits."""
    return [[inner(a, b) for b in states] for a in states]


def residual_norm(gram, coefficients, width):
    """Return ||sum c_i U_i^(tensor width)||_HS^2 / d^width."""
    Q.need(type(width) is int and width > 0, 'Positive tensor width')
    size = len(coefficients)
    Q.need(len(gram) == size and all(len(row) == size for row in gram), 'Gram dimensions')
    result = (Fraction(0), Fraction(0))
    for i, a in enumerate(coefficients):
        for j, b in enumerate(coefficients):
            result = add(result, Q.multiply(Q.multiply(conjugate(a), b), power(gram[i][j], width)))
    Q.need(result[1] == 0 and result[0] >= 0, 'A valid Gram norm is real and nonnegative')
    return result[0]


def decide(n, circuits, coefficients):
    """Apply the credited four-width theorem to one fixed expanded residual."""
    Q.need(len(circuits) == len(coefficients), 'One fixed coefficient per circuit')
    for a in coefficients:
        Q.need(len(a) == 2 and all(type(x) in (int, Fraction) for x in a),
               'Exact rational real and imaginary coefficients')
    gram = kernel([choi(n, c) for c in circuits])
    first = 4 * n + 4 if n else 1
    norms = [residual_norm(gram, coefficients, f) for f in range(first, first + 4)]
    return dict(widths=list(range(first, first + 4)), norms=norms,
                all_positive_widths_zero=all(x == 0 for x in norms))


def divide(a, b):
    scale = b[0] ** 2 + b[1] ** 2
    Q.need(scale != 0, 'Nonzero complex pivot')
    value = Q.multiply(a, conjugate(b))
    return Fraction(value[0]) / scale, Fraction(value[1]) / scale


def best_approximation(states, target, width):
    """Minimize the normalized squared residual in the supplied finite span.

    Coefficients may depend on this width. Dependent columns are permitted.
    This operation does not admit a physical readout or new native queries.
    """
    Q.need(type(width) is int and width > 0, 'Positive tensor width')
    size = len(states)
    gram = kernel(states + [target])
    matrix = [[power(gram[i][j], width) for j in range(size)] +
              [power(gram[i][size], width)] for i in range(size)]
    pivots = []
    for col in range(size):
        row = next((r for r in range(len(pivots), size) if matrix[r][col] != (0, 0)), None)
        if row is None: continue
        k = len(pivots)
        matrix[k], matrix[row] = matrix[row], matrix[k]
        pivot = matrix[k][col]
        matrix[k] = [divide(x, pivot) for x in matrix[k]]
        for r in range(size):
            if r != k:
                factor = matrix[r][col]
                matrix[r] = [add(x, Q.multiply((-factor[0], -factor[1]), y))
                             for x, y in zip(matrix[r], matrix[k])]
        pivots.append(col)
    Q.need(all(row[-1] == (0, 0) for row in matrix[len(pivots):]), 'Consistent Gram normal equations')
    coefficients = [(Fraction(0), Fraction(0))] * size
    for row, col in enumerate(pivots): coefficients[col] = matrix[row][-1]
    residual = residual_norm(gram, [(-x, -y) for x, y in coefficients] + [(1, 0)], width)
    # Orthogonality is an independently inspectable optimum certificate.
    for i in range(size):
        value = (Fraction(0), Fraction(0))
        for j in range(size): value = add(value, Q.multiply(power(gram[i][j], width), coefficients[j]))
        Q.need(value == power(gram[i][size], width), 'Exact residual orthogonality')
    return dict(coefficients=coefficients, squared_residual=residual, span_rank=len(pivots))
