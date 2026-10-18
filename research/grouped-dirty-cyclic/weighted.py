"""Unit-phase higher-order periodic lift with certified rounded closure.

The phase windows and polynomial coefficients are exact Gaussian rationals.
The long phase product and companion power use bounded dyadic precision.
Scalar solve/workspace remain ordinary classical arithmetic, fully charged.
"""
from fractions import Fraction as F
from pathlib import Path
import json
from itertools import chain

from gaussian import G, identity, multiply, norm_upper, power, rounded, solve, solve_dyadic

P = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def constants(roots, radii, wiener_bound=None):
    require(len(roots) > 0 and len(roots) == len(radii), 'root shape')
    require(all(0 <= radius < 1 and root.norm2() <= radius**2
                for root, radius in zip(roots, radii)), 'certified stable radii')
    q = [G(1)]
    K = F(1)
    for root, radius in zip(roots, radii):
        out = [G()]*(len(q)+1)
        for j, v in enumerate(q):
            out[j] += v
            out[j+1] -= root*v
        q = out
        if wiener_bound is None:
            K /= 1-radius
    if wiener_bound is not None:
        # This is an explicit theorem premise, certified by the caller's
        # complete-polynomial/common-operator argument, not inferred here.
        require(wiener_bound >= 1, 'supplied Wiener bound')
        K = wiener_bound
    return constants_from_polynomial(q, K)


def constants_from_polynomial(q, K):
    require(len(q) > 1 and q[0] == G(1) and K >= 1, 'certified polynomial')
    k = len(q)-1
    c = [[-v for v in q[1:]]] + [[G(j == i-1) for j in range(k)] for i in range(1, k)]
    B = identity(k)
    mass = norm_upper(B)
    for j in range(1, k+1):
        # Exploit the companion's subdiagonal, avoiding k dense matrix
        # products when constructing the adjugate coefficient bound.
        B = [[sum((c[0][i]*B[i][col] for i in range(k)), G())
              for col in range(k)]] + [row.copy() for row in B[:-1]]
        for i in range(k):
            B[i][i] += q[j]
        if j < k:
            mass += norm_upper(B)
        else:
            require(norm_upper(B) == 0, 'complex Cayley-Hamilton')
    return q, c, K, K*mass


def round_polynomial(q, K, D, bits):
    """Causal Wiener-algebra Neumann bound; no rounded-root assumptions."""
    k = len(q)-1
    u = F(1, 1 << bits)
    coefficient_bits = bits
    while True:
        delta = F(k, 1 << coefficient_bits)
        if K*delta <= F(1, 2) and 2*K*K*delta*D <= u:
            break
        coefficient_bits += 1
    result = [G(1)] + [rounded(v, coefficient_bits) for v in q[1:]]
    actual_delta = sum((v-w).modulus_upper() for v, w in zip(q, result))
    require(actual_delta <= delta, 'coefficient rounding bound')
    return result, K/(1-K*delta), coefficient_bits, actual_delta


def coefficients(q, phases, i, coefficient_bits=None):
    product = G(1)
    out = []
    for j in range(1, len(q)):
        product *= phases[(i-j+1) % len(phases)]
        if coefficient_bits is not None:
            product = rounded(product, coefficient_bits)
        value = -q[j]*product
        out.append(value if coefficient_bits is None else rounded(value, coefficient_bits))
    return out


def preparation(c, phases, bits, K, S, D, bounded_windows=False):
    k, length = len(c), len(phases)
    u = F(1, 1 << bits)
    scalar_bits = bits
    while True:
        us = F(1, 1 << scalar_bits)
        delta = k*us
        power_error = 2*(length-1)*S*S*delta
        phase_error = length*us
        error = (1+phase_error)*power_error + phase_error*S
        if ((length-1)*S*delta <= F(1, 2) and error <= 1/(2*S)
                and (4 if bounded_windows else 2)*S**3*error*K*(D+u) <= u):
            break
        scalar_bits += 1
    phase = G(1)
    for v in phases:
        phase = rounded(v*phase, scalar_bits)
    M = power(c, length, scalar_bits)
    M = [[phase*v for v in row] for row in M]
    # No final multiplication rounding; these dyadics have <=2*scalar_bits
    # fractional bits, which is charged to the exact rational closure solve.
    return M, error, scalar_bits


def window_precision(q, K, S, D, bits):
    """Bound the forcing from finite-width phase-window coefficients."""
    u = F(1, 1 << bits)
    R = len(q)-1 + sum(j*v.upper() for j, v in enumerate(q))
    width = bits
    # The extra constant covers the separately rounded initial gauge.
    sensitivity = 2*K*K*(D+u) + 8*S**3*K*(D+u) + 8*S*S*u
    while True:
        epsilon = R*F(1, 1 << width)
        if K*epsilon <= F(1, 2) and S*epsilon <= F(1, 2) and epsilon*sensitivity <= u:
            return width, epsilon
        width += 1


def gauge_precision(k, K, S, D, bits):
    u = F(1, 1 << bits)
    width = bits
    while True:
        delta = k*F(1, 1 << width)
        if delta <= 1 and 12*S*S*K*(D+u)*delta <= u:
            return width, delta
        width += 1


def apply(x, y, q, phases, bits, M, sign=1, mutation=None,
          destination=None, multiplier=None, coefficient_bits=None, gauge_bits=None, solver_audit=None):
    k, length = len(q)-1, len(x)
    require(length > 0 and x is not y and len(y) == length and len(phases) == length
            and q[0] == G(1) and k > 0 and sign in (-1, 1), 'weighted filter contract')
    require(all(v.norm2() == 1 for v in phases), 'unit phases')
    require(all(rounded(v, bits) == v for v in chain(x, y)), 'working grid')
    for i in range(length):
        a = coefficients(q, phases, i, coefficient_bits)
        x[i] += rounded(sum((a[j-1]*x[i-j] for j in range(1, min(k, i)+1)), G()), bits)
    # D_{-1} diagonal: 1, phi[-1]^-1, (phi[-1]phi[-2])^-1, ...
    diag, phase = [], G(1)
    for j in range(k):
        diag.append(phase)
        phase *= phases[(-1-j) % length].conjugate()
        if gauge_bits is not None:
            phase = rounded(phase, gauge_bits)
    if mutation == 'omit_gauge':
        diag = [G(1)]*k
    tail = [(x[length-1-j] if j < length else G()) *
            (G(1)/diag[j] if gauge_bits is None else diag[j].conjugate()) for j in range(k)]
    closure = [[G(i == j)-M[i][j] for j in range(k)] for i in range(k)]
    seed = solve(closure, tail) if gauge_bits is None else solve_dyadic(closure, tail, solver_audit)
    if solver_audit is not None:
        require(seed == solve(closure, tail), 'independent rational closure solve')
    state = [rounded(diag[j]*v, bits) for j, v in enumerate(seed)]
    for i in range(length):
        a = coefficients(q, phases, i, coefficient_bits)
        h = rounded(sum((v*z for v, z in zip(a, state)), G()), bits)
        value = x[i]+h
        if multiplier is not None:
            value = rounded(multiplier(i)*value, bits)
        j = i if destination is None else destination(i)
        y[j] += sign*value
        state = [h]+state[:-1]
    for i in range(length-1, -1, -1):
        a = coefficients(q, phases, i, coefficient_bits)
        x[i] -= rounded(sum((a[j-1]*x[i-j] for j in range(1, min(k, i)+1)), G()), bits)


def exact(x, q, phases):
    """Build F(U) independently by dense matrix powers, including L<k."""
    length = len(x)
    U = [[G() for _ in x] for _ in x]
    for i in range(length):
        U[i][(i-1) % length] = phases[i]
    A = [[G() for _ in x] for _ in x]
    V = identity(length)
    for coefficient in q:
        for i in range(length):
            for j in range(length):
                A[i][j] += coefficient*V[i][j]
        V = multiply(U, V)
    return solve(A, x)


def main():
    units = [G(1), G(0, 1), G(F(3, 5), F(4, 5)), G(F(-5, 13), F(12, 13))]
    root_sets = [([G(F(1, 2))], [F(1, 2)]),
                 ([G(F(3, 8), F(1, 4))]*3, [F(1, 2)]*3),
                 ([G(), G(F(1, 4), F(1, 2)), G(F(-3, 4))], [F(0), F(3, 4), F(3, 4)]),
                 ([G(F(4095, 8192), F(1, 16)), G(F(-2047, 4096))], [F(3, 4), F(1, 2)])]
    rows, rejected_gauge = [], []
    for roots, radii in root_sets:
        q, c, K, S = constants(roots, radii)
        for length in [1, 2, 3, 8, 17]:
            for direction in (-1, 1):
                phases = [units[(i*i+3*i+2) % len(units)] for i in range(length)]
                if direction == -1:
                    phases = [v.conjugate() for v in reversed(phases)]
                bits = 64
                u = F(1, 1 << bits)
                x0 = [G(F(2*i-7, 8)+u, F(i-3, 8)-u) for i in range(length)]
                y0 = [G(F(11-i, 16)-u, F(i+3, 16)+u) for i in range(length)]
                D = max(v.upper() for v in x0)
                M, error_M, scalar_bits = preparation(c, phases, bits, K, S, D)
                eta = G(1)
                for phase in phases:
                    eta *= phase
                true_M = [[eta*v for v in row] for row in power(c, length)]
                actual_M = max(sum((v-w).modulus_upper() for v, w in zip(row, tr))
                               for row, tr in zip(M, true_M))
                require(actual_M <= error_M, 'rounded weighted closure bound')
                bound = (K+2*S)*u + 2*S**3*error_M*K*(D+u)
                x, y = x0.copy(), y0.copy()
                want = exact(x0, q, phases)
                apply(x, y, q, phases, bits, M)
                require(x == x0, 'weighted dirty restoration')
                errors = [a-b-cv for a, b, cv in zip(y, y0, want)]
                require(all(v.norm2() <= bound**2 for v in errors), 'weighted all-length error bound')
                apply(x, y, q, phases, bits, M, -1)
                require(x == x0 and y == y0, 'weighted exact inverse cancellation')
                mx, my = x0.copy(), y0.copy()
                apply(mx, my, q, phases, bits, M, mutation='omit_gauge')
                if any((a-b-cv).norm2() > bound**2 for a, b, cv in zip(my, y0, want)):
                    rejected_gauge.append(len(rows))
                rows.append(dict(roots=list(map(str, roots)), phases=list(map(str, phases)),
                                 length=length, direction_fixture=direction, bits=bits, scalar_bits=scalar_bits,
                                 K=str(K), S=str(S), bound=str(bound),
                                 closure_error_upper=str(actual_M), closure_error_bound=str(error_M),
                                 output_error_squared_max=str(max(v.norm2() for v in errors)),
                                 source_restored=True, inverse_cancels=True))
    require(bool(rejected_gauge), 'nonvacuous gauge defect control')
    require(any(F(row['closure_error_upper']) > 0 for row in rows), 'nonvacuous closure rounding')
    result = dict(status='PASS', cases=rows,
        rejected_gauge_cases=rejected_gauge,
        scope='Complex unit-phase periodic local filter. Direction fixture varies phases; '
              'This component tests the local filter; grouped.py separately checks full routing. '
              'No bit-reversible arithmetic claim.')
    print('PASS', len(rows), 'weighted cases;', len(rejected_gauge), 'gauge defects detected')
    return result


if __name__ == '__main__':
    main()
