"""Two stable higher-order groups, combined with one dirty connector.

Exact finite reference checks against the original mixed root-factor matrix.
No hidden length-sized source copy is used by the execution path: IndexView
only routes reads and writes to the caller's source, and phases are accessed
through a callable. Dense matrices and snapshots belong to validation only.
"""
from fractions import Fraction as F
from pathlib import Path
import json

from gaussian import G, rounded, solve
from weighted import (apply, coefficients, constants, constants_from_polynomial,
                      gauge_precision, preparation, require, round_polynomial, window_precision)

P = Path(__file__).resolve().parent


class IndexView:
    def __init__(self, length, get, put=None):
        self.length, self.get, self.put = length, get, put

    def __len__(self):
        return self.length

    def __getitem__(self, i):
        if not 0 <= i < self.length:
            raise IndexError(i)
        return self.get(i)

    def __setitem__(self, i, value):
        if self.put is None or not 0 <= i < self.length:
            raise IndexError(i)
        self.put(i, value)


def group(x, y, roots, radii, inside, phases, direction, scale, bits, sign=1,
          mutation=None, audit=False, wiener_bound=None):
    require(x is not y and len(x) == len(y) == len(phases) > 0, 'group arrays')
    require(direction in (-1, 1) and sign in (-1, 1), 'group direction')
    require(inside or all(bool(b) for b in roots), 'outside reciprocal roots must be nonzero')
    length, k = len(x), len(roots)
    alpha = G(scale)
    if not inside:
        for b in roots:
            alpha *= -b
    if not roots:
        for i in range(length):
            y[i] += sign*rounded(alpha*x[i], bits)
        return dict(error_coefficient=F(1), norm=abs(scale), scalar_bits=None, order=0)
    orientation = -direction if inside else direction
    physical = (lambda i: i) if orientation == 1 else (lambda i: length-1-i)
    source = IndexView(length, lambda i: x[physical(i)], lambda i, v: x.__setitem__(physical(i), v))
    if inside:
        local_phases = IndexView(length, lambda i: phases[(physical(i)+direction) % length].conjugate())
    else:
        local_phases = IndexView(length, lambda i: phases[physical(i)])
    q, c, K, S = constants(roots, radii, wiener_bound)
    D = max(v.upper() for v in x)
    original_K = K
    q, rounded_K, coefficient_bits, coefficient_delta = round_polynomial(q, K, D, bits)
    q, c, K, S = constants_from_polynomial(q, rounded_K)
    M, error_M, scalar_bits = preparation(c, local_phases, bits, K, S, D, bounded_windows=True)
    window_bits, window_error_bound = window_precision(q, K, S, D, bits)
    gauge_bits, gauge_error_bound = gauge_precision(k, K, S, D, bits)
    u = F(1, 1 << bits)
    value_bound = K*D + (K+2*S+3)*u
    multiplier_bits = bits
    phase_steps = k if inside else 0
    while (phase_steps+1)*F(1, 1 << multiplier_bits)*value_bound > u:
        multiplier_bits += 1
    rounded_alpha = rounded(alpha, multiplier_bits)
    def destination(i):
        return (physical(i)-k*direction) % length if inside else physical(i)
    def multiplier(i):
        value = rounded_alpha
        if inside:
            for j in range(k):
                value = rounded(value*phases[(physical(i)-j*direction) % length].conjugate(), multiplier_bits)
        return value
    audit_fields = {}
    if audit:
        max_window_error = F(0)
        max_multiplier_error = F(0)
        for i in range(length):
            ideal = coefficients(q, local_phases, i)
            actual = coefficients(q, local_phases, i, window_bits)
            local_error = sum((a-b).modulus_upper() for a, b in zip(ideal, actual))
            require(local_error <= window_error_bound, 'phase-window coefficient error')
            max_window_error = max(max_window_error, local_error)
            ideal_multiplier = alpha
            if inside:
                for j in range(k):
                    ideal_multiplier *= phases[(physical(i)-j*direction) % length].conjugate()
            local_multiplier_error = (multiplier(i)-ideal_multiplier).modulus_upper()
            require(local_multiplier_error <= (phase_steps+1)*F(1, 1 << multiplier_bits), 'output multiplier error')
            max_multiplier_error = max(max_multiplier_error, local_multiplier_error)
        audit_fields = dict(max_window_error=max_window_error, max_multiplier_error=max_multiplier_error)
        exact_gauge, approx_gauge = G(1), G(1)
        max_gauge_error = F(0)
        for j in range(k):
            error = (exact_gauge-approx_gauge).modulus_upper()
            require(error <= gauge_error_bound, 'initial gauge approximation')
            max_gauge_error = max(max_gauge_error, error)
            phase = local_phases[(-1-j) % length].conjugate()
            exact_gauge *= phase
            approx_gauge = rounded(approx_gauge*phase, gauge_bits)
        audit_fields['max_gauge_error'] = max_gauge_error
    if mutation == 'wrong_inner_shift' and inside:
        destination = physical
    if mutation == 'coarse_window':
        window_bits = 0
    if mutation == 'coarse_gauge':
        gauge_bits = 0
    if mutation == 'coarse_multiplier':
        original_multiplier = multiplier
        multiplier = lambda i: rounded(original_multiplier(i), 0)
    solver_audit = {} if audit else None
    apply(source, y, q, local_phases, bits, M, sign,
          destination=destination, multiplier=multiplier, coefficient_bits=window_bits,
          gauge_bits=gauge_bits, solver_audit=solver_audit)
    if audit:
        audit_fields['solver'] = solver_audit
    # |alpha|<=|scale| for either group; all inner phase routing is isometric.
    error_coefficient = abs(scale)*(K+2*S+4)+2
    return dict(error_coefficient=error_coefficient, norm=abs(scale)*original_K,
                scalar_bits=scalar_bits, coefficient_bits=coefficient_bits,
                coefficient_delta=coefficient_delta, window_bits=window_bits,
                window_error_bound=window_error_bound, multiplier_bits=multiplier_bits,
                gauge_bits=gauge_bits, gauge_error_bound=gauge_error_bound,
                order=k, closure_error_bound=error_M, **audit_fields)


def compose(x, y, z, inside, outside, phases, direction, scale, bits, sign=1,
            mutation=None, audit=False, wiener_bound=None):
    require(len({id(x), id(y), id(z)}) == 3, 'three distinct data arrays')
    require(len(x) == len(y) == len(z) == len(phases) > 0, 'composition shape')
    in_roots, in_radii = inside
    out_roots, out_radii = outside
    operations = [('B', 1), ('A', 1), ('B', -1), ('A', -1)]
    if sign == -1:
        operations = [(name, -s) for name, s in reversed(operations)]
    require(sign in (-1, 1), 'composition sign')
    stats = []
    for name, s in operations:
        if name == 'B':
            row = group(x, z, out_roots, out_radii, False, phases, direction, scale, bits, s, mutation, audit, wiener_bound)
        else:
            row = group(z, y, in_roots, in_radii, True, phases, direction, 1, bits, s, mutation, audit, wiener_bound)
        stats.append(dict(name=name, sign=s, **row))
    A = [row for row in stats if row['name'] == 'A']
    B = next(row for row in stats if row['name'] == 'B')
    # Precision is chosen from each call's source magnitude. A's two calls
    # therefore need their own certified constants, even on the same roots.
    coefficient = A[0]['norm']*B['error_coefficient'] + sum(row['error_coefficient'] for row in A)
    return stats, coefficient*F(1, 1 << bits)


def exact_mixed(x, inside, outside, phases, direction, scale):
    out = x.copy()
    length = len(x)
    for is_inside, roots in [(True, inside), (False, outside)]:
        for b in roots:
            rho = b if is_inside else G(1)/b
            a = [[G() for _ in x] for _ in x]
            for i in range(length):
                a[i][i] = -rho
                a[i][(i-direction) % length] += phases[i]
            out = solve(a, out)
    return [scale*v for v in out]


def main():
    fixtures = [
        (([G(F(1, 4))], [F(1, 4)]), ([G(F(1, 2))], [F(1, 2)])),
        (([G(F(3, 8), F(1, 4))]*3, [F(1, 2)]*3),
         ([G(F(-1, 2)), G(F(1, 4), F(1, 4))], [F(1, 2)]*2)),
        (([G(), G(F(1, 4), F(1, 2))], [F(0), F(3, 4)]), ([], [])),
        (([], []), ([G(F(4095, 8192))]*3, [F(1, 2)]*3)),
        (([G(F((1 << 80)-1, 1 << 81))]*2, [F(1, 2)]*2),
         ([G(F((1 << 70)-1, 1 << 72))], [F(1, 4)])),
    ]
    units = [G(1), G(0, 1), G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13))]
    rows, shift_controls, dirt_dependence, window_controls = [], [], [], []
    for inside, outside in fixtures:
        for length in [1, 2, 3, 8]:
            for direction in (-1, 1):
                phases = [units[(i*i+3*i+2) % 4] for i in range(length)]
                for dirt in [-13, 0, 7]:
                    bits, scale = 64, 7
                    u = F(1, 1 << bits)
                    x0 = [G(F(i-3, 4)+u, F(2*i-3, 8)-u) for i in range(length)]
                    y0 = [G(F(i+19, 8)-u, F(3-i, 4)+u) for i in range(length)]
                    z0 = [G(F(dirt+2*i, 4)+u, F(dirt-3*i, 8)-u) for i in range(length)]
                    require(all((v/u).denominator == 1 and (v/u).numerator % 2
                                for array in (x0, y0, z0) for value in array for v in (value.re, value.im)),
                            'arbitrary odd low bits in every data coordinate')
                    x, y, z = x0.copy(), y0.copy(), z0.copy()
                    stats, bound = compose(x, y, z, inside, outside, phases, direction, scale, bits, audit=True)
                    require(x == x0 and z == z0, 'source and dirty connector exactly restored')
                    want = exact_mixed(x0, inside[0], outside[0], phases, direction, scale)
                    net = [a-b for a, b in zip(y, y0)]
                    require(all((v-w).norm2() <= bound**2 for v, w in zip(net, want)), 'mixed dense inverse bound')
                    compose(x, y, z, inside, outside, phases, direction, scale, bits, -1)
                    require(x == x0 and y == y0 and z == z0, 'whole commutator exact inverse')
                    mx, my, mz = x0.copy(), y0.copy(), z0.copy()
                    compose(mx, my, mz, inside, outside, phases, direction, scale, bits,
                            mutation='wrong_inner_shift')
                    if any((v-v0-w).norm2() > bound**2 for v, v0, w in zip(my, y0, want)):
                        shift_controls.append(len(rows))
                    mx, my, mz = x0.copy(), y0.copy(), z0.copy()
                    compose(mx, my, mz, inside, outside, phases, direction, scale, bits,
                            mutation='coarse_window')
                    if any((v-v0-w).norm2() > bound**2 for v, v0, w in zip(my, y0, want)):
                        window_controls.append(len(rows))
                    rows.append(dict(inside=list(map(str, inside[0])), outside=list(map(str, outside[0])),
                                     length=length, direction=direction, dirt=dirt, bits=bits, scale=scale,
                                     phases=list(map(str, phases)), stats=stats, error_bound=bound,
                                     max_error_squared=max((v-w).norm2() for v, w in zip(net, want)),
                                     increment=list(map(str, net)), source_restored=True,
                                     connector_restored=True, inverse_cancels=True))
    for i in range(0, len(rows), 3):
        if len({tuple(row['increment']) for row in rows[i:i+3]}) > 1:
            dirt_dependence.append(i)
    require(bool(shift_controls), 'nonvacuous inner shift control')
    require(bool(dirt_dependence), 'test observes nonlinear dependence on connector dirt')
    coefficient_rounding_cases = [i for i, row in enumerate(rows)
                                  if any(stat.get('coefficient_delta', 0) > 0 for stat in row['stats'])]
    require(bool(coefficient_rounding_cases), 'nonvacuous polynomial coefficient rounding')
    require(bool(window_controls), 'nonvacuous coarse phase-window control')
    require(any(stat.get('max_window_error', 0) > 0 for row in rows for stat in row['stats']), 'nonvacuous phase-window rounding')
    require(any(stat.get('max_multiplier_error', 0) > 0 for row in rows for stat in row['stats']), 'nonvacuous output multiplier rounding')
    require(any(stat.get('max_gauge_error', 0) > 0 for row in rows for stat in row['stats']), 'nonvacuous initial gauge rounding')
    result = dict(status='PASS', cases=rows,
        shift_controls=shift_controls, dirt_dependence_cases=dirt_dependence,
        coefficient_rounding_cases=coefficient_rounding_cases,
        window_controls=window_controls,
        scope='Classical mixed cyclic inverse with four grouped calls and one dirty connector. '
              'Certified rounded polynomial coefficients, phase windows and multipliers; all scalar workspace charged; '
              'no bit-reversible, common-label, full transform, or kappa claim.')
    print('PASS', len(rows), 'mixed cases;', len(shift_controls), 'shift controls;',
          len(dirt_dependence), 'dirty nonlinear triples;', len(coefficient_rounding_cases), 'coefficient rounding cases;',
          len(window_controls), 'window controls')
    return result


if __name__ == '__main__':
    main()
