#!/usr/bin/env python3
"""Exact integer model for the fixed two-channel reader.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
The rounded four-block mechanism and residue method are inherited from
Ali Romman #1135; see PROOF.md and SOURCE-PINS.json for the full attribution.
"""
from dataclasses import dataclass

Matrix = tuple[tuple[int, int], tuple[int, int]]
A: Matrix = ((1, 2), (-2, 1))
ADJ: Matrix = ((1, -2), (2, 1))
BALANCED: tuple[Matrix, ...] = (
    ((-1, 0), (0, -1)), ((0, -1), (1, 0)),
    ((1, 0), (0, 1)), ((0, 1), (-1, 0)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int


def matrix(value):
    require(len(value) == 2 and all(len(row) == 2 for row in value)
            and all(integer(x) for row in value for x in row),
            'expected a two-by-two integer matrix')
    return tuple(tuple(row) for row in value)


def modulus(b):
    require(integer(b) and b >= 0, 'precision must be a nonnegative integer')
    return 1 << b


def ceil_div(n, m):
    require(integer(n) and n >= 0 and integer(m) and m > 0,
            'ceil_div needs n>=0 and m>0')
    return (n + m - 1) // m


def multiply(left, right):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def residual(lift, b):
    lift, m = matrix(lift), modulus(b)
    product = multiply(A, lift)
    return tuple(tuple(product[i][j] - m * (i == j) for j in range(2))
                 for i in range(2))


def from_residual(d, b):
    d, m = matrix(d), modulus(b)
    target = tuple(tuple(d[i][j] + m * (i == j) for j in range(2))
                   for i in range(2))
    numerator = multiply(ADJ, target)
    require(all(x % 5 == 0 for row in numerator for x in row),
            'residual is outside the attainable lattice')
    return tuple(tuple(x // 5 for x in row) for row in numerator)


def lift_for(b, family):
    m = modulus(b)
    if family == 'balanced':
        d = BALANCED[b % 4]
    elif family == 'concentrated':
        centered = lambda x: (x + 2) % 5 - 2
        d = ((centered(-m), centered(2 * m)), (0, 0))
    else:
        raise ValueError('unknown lift family')
    return from_residual(d, b)


def optimum_squared(b, bound):
    m = modulus(b)
    require(integer(bound) and bound >= 0, 'source bound must be nonnegative')
    return min(ceil_div(3 * bound, m) ** 2,
               2 * ceil_div(bound, m) ** 2)


def optimal_lift(b, bound):
    m = modulus(b)
    optimum_squared(b, bound)
    # Ties use the balanced construction; this is not a word-cost optimizer.
    family = ('concentrated' if ceil_div(3 * bound, m) ** 2
              < 2 * ceil_div(bound, m) ** 2 else 'balanced')
    return family, lift_for(b, family)


@dataclass(frozen=True)
class Gate:
    """Translate dst by sign*view(src,shift), or by a constant when src=None."""
    dst: int
    src: int | None
    shift: int
    amount: int


def inverse(gates):
    return tuple(Gate(g.dst, g.src, g.shift, -g.amount) for g in reversed(gates))


def lift_gates(lift):
    gates = []
    for i, row in enumerate(matrix(lift)):
        for j, coefficient in enumerate(row):
            for bit in range(abs(coefficient).bit_length()):
                if (abs(coefficient) >> bit) & 1:
                    gates.append(Gate(2 + i, j, bit, 1 if coefficient > 0 else -1))
    return tuple(gates)


def reader_gates(b):
    m, gates = modulus(b), []
    c = m // 2
    for dst, other, sign, out in ((2, 3, 1, 4), (3, 2, -1, 5)):
        gates.append(Gate(dst, other, 1, sign))
        if c:
            gates.append(Gate(dst, None, 0, c))
        gates.append(Gate(out, dst, -b, 1))
        if c:
            gates.append(Gate(dst, None, 0, -c))
        gates.append(Gate(dst, other, 1, -sign))
    return tuple(gates)


def compile_word(lift, b):
    first, read = lift_gates(lift), reader_gates(b)
    return first + read + inverse(first) + inverse(read)


def execute(gates, initial, guards=None):
    """Execute gates without wraparound; return endpoint and per-role maxima."""
    require(len(initial) == 6 and all(integer(x) for x in initial),
            'expected six integer role values')
    if guards is not None:
        require(len(guards) == 6 and all(integer(x) and x >= 0 for x in guards),
                'expected six nonnegative headroom guards')
    words = list(initial)
    maxima = [abs(x) for x in words]
    if guards is not None:
        require(all(x <= y for x, y in zip(maxima, guards)), 'initial headroom exceeded')
    for gate in gates:
        require(0 <= gate.dst < 6 and (gate.src is None or
                (0 <= gate.src < 6 and gate.src != gate.dst)), 'invalid gate roles')
        if gate.src is None:
            require(gate.shift == 0, 'a constant has no shift')
            delta = gate.amount
        else:
            require(gate.amount in (-1, 1), 'ADD sign must be +/-1')
            source = words[gate.src]
            view = (source << gate.shift if gate.shift >= 0
                    else source >> -gate.shift)
            delta = gate.amount * view
        words[gate.dst] += delta
        maxima[gate.dst] = max(maxima[gate.dst], abs(words[gate.dst]))
        if guards is not None:
            require(abs(words[gate.dst]) <= guards[gate.dst], 'runtime headroom exceeded')
    return tuple(words), tuple(maxima)


def bill(lift, b):
    modulus(b)
    p = sum(abs(x).bit_count() for row in matrix(lift) for x in row)
    return {'roles': 6, 'clean_words': 0, 'restored_words': 4,
            'word_adds': 2 * p + 12, 'constant_translations': 8 if b else 0,
            'lift_bit_adds': 2 * p, 'reader_shear_adds': 8,
            'quotient_view_adds': 4}


def headroom(lift, b, bound, helper_bounds, output_bounds):
    lift, m = matrix(lift), modulus(b)
    require(integer(bound) and bound >= 0, 'source bound must be nonnegative')
    require(len(helper_bounds) == len(output_bounds) == 2 and
            all(integer(x) and x >= 0 for x in (*helper_bounds, *output_bounds)),
            'dirty-word bounds must be nonnegative integer pairs')
    fine = [helper_bounds[i] + bound * sum(map(abs, lift[i])) for i in range(2)]
    numer = [sum(abs(A[i][j]) * fine[j] for j in range(2)) for i in range(2)]
    helper = [x + m // 2 for x in numer]
    d = residual(lift, b)
    outputs = [output_bounds[i] + max((numer[i] + m // 2) // m,
               bound + ceil_div(bound * sum(map(abs, d[i])), m)) for i in range(2)]
    guards = (bound, bound, *helper, *outputs)
    return {'absolute_guards': guards,
            'signed_widths': tuple(1 + x.bit_length() for x in guards)}
