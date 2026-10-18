"""Literal Gaussian-integer physical fixture, without predecessor imports.

This checks a whole-word column, not the native compiler or every input column.
Arham Tahir, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() % 2


def multiply(rows, x):
    return sum(parity(r & x) << j for j, r in enumerate(rows))


@lru_cache(None)
def chart(frame):
    # Direct span construction and a complete permutation inverse table;
    # no predecessor Gaussian elimination or circuit interpreter is used.
    columns, space = [], {0}
    for x in frame + tuple(1 << j for j in range(9)):
        if x not in space:
            columns.append(x)
            space |= {y ^ x for y in space}
    need(len(columns) == 9, 'physical basis extension')
    matrix = tuple(sum(((columns[j] >> i) & 1) << j for j in range(9)) for i in range(9))
    permutation = tuple(multiply(matrix, x) for x in range(512))
    inverse = [0] * 512
    for x, y in enumerate(permutation):
        inverse[y] = x
    inv_columns = [inverse[1 << j] for j in range(9)]
    quadratic = [(1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(inv_columns))
                 for i, a in enumerate(inv_columns)]
    phases = []
    for x in range(512):
        exponent = sum((quadratic[i] >> i) & 1 for i in range(9) if x >> i & 1)
        exponent += 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1)))
                            for i in range(9) if x >> i & 1)
        phases.append(exponent % 4)
    return permutation, tuple(inverse), tuple(phases)


ZERO = ((0, 0),) * 512


def normalize(values, denominator):
    if not any(a or b for a, b in values):
        return ZERO, 0
    while denominator and all(not ((a | b) & 1) for a, b in values):
        values = tuple((a // 2, b // 2) for a, b in values)
        denominator -= 1
    return values, denominator


def phase(values, exponents, sign):
    out = []
    for (a, b), e in zip(values, exponents):
        out.append(((a, b), (-b, a), (-a, -b), (b, -a))[sign * e % 4])
    return tuple(out)


def permute(values, permutation):
    out = [(0, 0)] * 512
    for x, y in enumerate(permutation):
        out[y] = values[x]
    return tuple(out)


def apply_chart(state, frame, inverse=False):
    """Delta_F or its inverse, in literal canonical chart order."""
    values, denominator = state
    if values == ZERO or not frame:
        return state
    rank = len(frame)
    if rank != 9:
        p, pi, d = chart(tuple(frame))
        # Delta = conjugate(K C K^-1), K = D P in matrix order.
        values = permute(phase(values, d, 1), pi)
    sign = 1 if inverse else -1
    for j in range(rank):
        direction = 1 << j
        out = []
        for x, (a, b) in enumerate(values):
            c, d2 = values[x ^ direction]
            out.append((a - sign*b + c + sign*d2,
                        b + sign*a + d2 - sign*c))
        values, denominator = normalize(tuple(out), denominator + 1)
    if rank != 9:
        values = phase(permute(values, p), d, -1)
    return values, denominator


def add(left, right, scalar):
    a, da = left
    b, db = right
    q = Fraction(scalar)
    need(q.denominator & (q.denominator - 1) == 0, 'physical dyadic ADD')
    db += q.denominator.bit_length() - 1
    d = max(da, db)
    out = tuple(((ar << (d-da)) + q.numerator*(br << (d-db)),
                 (ai << (d-da)) + q.numerator*(bi << (d-db)))
                for (ar, ai), (br, bi) in zip(a, b))
    return normalize(out, d)


def execute(word, fractional_budget=11):
    # The credited PR2551/2586 witness is an integer physical input.
    unit = ((1, 0),) + ZERO[1:]
    states = {r: (unit if r == 'Y2' else ZERO, 0) for r in word['initial_frames']}
    max_d, max_component = 0, Fraction(0)
    witness_d, witness_m, witness_value = None, None, None
    erases, observations = 0, 0

    def observe(cut, role):
        nonlocal max_d, max_component, witness_d, witness_m, witness_value, observations
        observations += 1
        values, d = states[role]
        need(d <= fractional_budget, 'physical fixture leaves claimed grid')
        magnitude = Fraction(max(max(abs(a), abs(b)) for a, b in values), 1 << d)
        need(magnitude < 2048, 'physical fixture component overflow')
        if d > max_d:
            max_d, witness_d = d, [cut, role]
            address = next(i for i, (a, b) in enumerate(values) if (a | b) & 1)
            a, b = values[address]
            witness_value = {'address': address, 'real': str(Fraction(a, 1 << d)),
                             'imag': str(Fraction(b, 1 << d))}
        if magnitude > max_component:
            max_component, witness_m = magnitude, [cut, role]

    for r in states:
        observe(0, r)
    for cut, e in enumerate(word['program'], 1):
        op, r = e[:2]
        if op == 'transport':
            states[r] = apply_chart(apply_chart(states[r], tuple(e[2]), True), tuple(e[3]))
        elif op == 'add':
            states[r] = add(states[r], states[e[2]], e[3])
        elif op == 'sign':
            v, d = states[r]
            states[r] = tuple((-a, -b) for a, b in v), d
        elif op == 'zero':
            need(r not in states, 'physical private allocation')
            states[r] = ZERO, 0
        elif op == 'erase':
            need(states[r] == (ZERO, 0), 'physical strict ideal erasure')
            del states[r]
            erases += 1
            continue
        else:
            raise ValueError('physical event type')
        observe(cut, r)
    v, d = states['X0']
    need((Fraction(v[0][0], 1 << d), Fraction(v[0][1], 1 << d)) ==
         (Fraction(-1, 64), Fraction(1, 64)), 'full-word physical separating value')
    need(erases == 8, 'physical private erasures')
    final_d = max(d for _, d in states.values())
    return {'input': 'Y2=delta_0; every other physical input zero',
            'events': len(word['program']), 'observations': observations,
            'max_fractional_bits': max_d, 'fractional_witness': witness_d,
            'fractional_witness_value': witness_value, 'final_max_fractional_bits': final_d,
            'max_component': str(max_component), 'component_witness': witness_m,
            'ideal_zero_erases': erases, 'final_X0_at_0': ['-1/64', '1/64']}
