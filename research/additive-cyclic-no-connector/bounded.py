"""Bounded scalar preparation for the additive stable split (research draft)."""
from pathlib import Path
import sys
from fractions import Fraction as F

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import grouped as reference
from gaussian import G, rounded, solve, solve_dyadic
from weighted import require
from algebra import product
from weighted import constants, constants_from_polynomial, coefficients
from precision import round_polynomial, preparation, window_precision, gauge_precision, extra


def decompose(A, B, alpha):
    """R*reverse(A)+S*B=alpha, with strictly separated pole groups."""
    ki, ko = len(A)-1, len(B)-1
    n = ki+ko
    if not n:
        return [alpha], [], dict(dimension=0)
    I = list(reversed(A))
    matrix = [[G() for _ in range(n)] for _ in range(n)]
    for j in range(ko):
        for i, value in enumerate(I):
            matrix[i+j][j] = value
    for j in range(ki):
        for i, value in enumerate(B):
            matrix[i+j][ko+j] = value
    rhs = [alpha]+[G()]*(n-1)
    audit = {}
    answer = solve_dyadic(matrix, rhs, audit)
    require(answer == solve(matrix, rhs), 'independent additive decomposition solve')
    R, S = answer[:ko], answer[ko:]
    lhs = [G()]*n
    if R:
        for j, value in enumerate(product(R, I)):
            lhs[j] += value
    if S:
        for j, value in enumerate(product(S, B)):
            lhs[j] += value
    require(lhs == rhs, 'entire additive polynomial identity')
    return R, [G()]+list(reversed(S)) if S else [], audit


def round_numerator(values, K, D, bits):
    if not values:
        return values, bits, F(0)
    width = bits+extra(len(values)*K*D)
    out = [rounded(value, width) for value in values]
    actual = sum((a-b).modulus_upper() for a, b in zip(values, out))
    require(actual <= len(values)*F(1, 1 << width), 'numerator rounding bound')
    return out, width, actual


def prepare(inside, outside, scale, D, bits, wiener_bound=None):
    """Approximate each polynomial, alpha and both Bezout numerators once."""
    u = F(1, 1 << bits)
    if inside[0]:
        A0, _, KA0, _ = constants(*inside, wiener_bound)
    else:
        A0, KA0 = [G(1)], F(1)
    if outside[0]:
        B0, _, KB0, _ = constants(*outside, wiener_bound)
    else:
        B0, KB0 = [G(1)], F(1)
    alpha = G(scale)
    for b in outside[0]:
        require(bool(b), 'nonzero outside reciprocal')
        alpha *= -b
    amplitude = abs(scale)
    if inside[0]:
        A, KA, width_A, delta_A = round_polynomial(A0, KA0, 2*max(1, amplitude)*KB0*max(1, D), bits)
    else:
        A, KA, width_A, delta_A = A0, KA0, bits, F(0)
    if outside[0]:
        B, KB, width_B, delta_B = round_polynomial(B0, KB0, 2*max(1, amplitude)*KA0*max(1, D), bits)
    else:
        B, KB, width_B, delta_B = B0, KB0, bits, F(0)
    alpha_bits = bits+extra(KA*KB*D)
    approximate_alpha = rounded(alpha, alpha_bits)
    delta_alpha = (approximate_alpha-alpha).modulus_upper()
    polynomial_error = amplitude*(KA*KA0*delta_A*KB0 + KA*KB*KB0*delta_B)*D
    alpha_error = delta_alpha*KA*KB*D
    require(polynomial_error <= 2*u and alpha_error <= u, 'full product preparation error')
    plus, minus, solve_audit = decompose(A, B, approximate_alpha)
    # The two rational summands are exactly the disjoint Laurent projections
    # of alpha*z^-ki/(A(z^-1)*B(z)). Projection contracts the Wiener norm.
    H = (amplitude+F(1, 1 << alpha_bits))*KA*KB
    require(sum(v.upper() for v in plus) <= 2*sum(v.upper() for v in B)*H,
            'positive Laurent numerator norm')
    require(sum(v.upper() for v in minus) <= 2*sum(v.upper() for v in A)*H,
            'negative Laurent numerator norm')
    plus, width_plus, delta_plus = round_numerator(plus, KB, D, bits)
    minus, width_minus, delta_minus = round_numerator(minus, KA, D, bits)
    numerator_error = (delta_plus*KB+delta_minus*KA)*D
    require(numerator_error <= 2*u, 'two rounded numerator errors')
    SA = constants_from_polynomial(A, KA)[3] if len(A) > 1 else F(1)
    SB = constants_from_polynomial(B, KB)[3] if len(B) > 1 else F(1)
    details = dict(width_A=width_A, width_B=width_B, alpha_bits=alpha_bits,
                   width_plus=width_plus, width_minus=width_minus,
                   delta_A=delta_A, delta_B=delta_B, delta_alpha=delta_alpha,
                   delta_plus=delta_plus, delta_minus=delta_minus,
                   polynomial_error=polynomial_error, alpha_error=alpha_error,
                   numerator_error=numerator_error, wiener_bound=H, solver=solve_audit)
    groups = [(False, B, plus, KB, SB), (True, A, minus, KA, SA)]
    return groups, polynomial_error+alpha_error+numerator_error, details


def fir_coefficients(numerator, phases, i, width):
    phase, values = G(1), []
    for j, value in enumerate(numerator):
        if j:
            phase = rounded(phase*phases[(i-j+1) % len(phases)], width)
        values.append(rounded(value*phase, width))
    return values


def filtered_add(x, y, q, numerator, phases, bits, K, S, sign=1, mutation=None, audit=False):
    if not numerator or all(not value for value in numerator):
        return F(0), {}
    k, length = len(q)-1, len(x)
    u = F(1, 1 << bits)
    if not k:
        for i in range(length):
            y[i] += sign*rounded(numerator[0]*x[i], bits)
        return u, dict(order=0)
    require(len(numerator) <= k+1, 'bounded FIR history width')
    D = max(v.upper() for v in x)
    c = [[-v for v in q[1:]]] + [[G(j == i-1) for j in range(k)] for i in range(1, k)]
    M, closure_error, scalar_bits = preparation(c, phases, bits, K, S, D, bounded_windows=True)
    window_bits, window_error = window_precision(q, K, S, D, bits)
    gauge_bits, gauge_error = gauge_precision(k, K, S, D, bits)
    filter_error = (K+2*S+3)*u
    value_bound = K*D+filter_error
    numerator_mass = sum(v.upper() for v in numerator)
    fir_sensitivity = len(numerator)+sum(j*v.upper() for j, v in enumerate(numerator))
    fir_bits = bits+extra(fir_sensitivity*value_bound)
    fir_error = fir_sensitivity*F(1, 1 << fir_bits)
    if mutation == 'coarse_fir':
        fir_bits = 0
    if mutation == 'coarse_gauge':
        gauge_bits = 0
    for i in range(length):
        a = coefficients(q, phases, i, window_bits)
        x[i] += rounded(sum((a[j-1]*x[i-j] for j in range(1, min(k, i)+1)), G()), bits)
    diag, phase = [], G(1)
    for j in range(k):
        diag.append(phase)
        phase = rounded(phase*phases[(-1-j) % length].conjugate(), gauge_bits)
    tail = [(x[length-1-j] if j < length else G())*diag[j].conjugate() for j in range(k)]
    closure = [[G(i == j)-M[i][j] for j in range(k)] for i in range(k)]
    solver_audit = {} if audit else None
    seed = solve_dyadic(closure, tail, solver_audit)
    if audit:
        require(seed == solve(closure, tail), 'bounded FIR closure independent solve')
    state = [rounded(diag[j]*v, bits) for j, v in enumerate(seed)]
    max_fir_error, max_window_error, max_past_size = F(0), F(0), F(0)
    for i in range(length):
        a = coefficients(q, phases, i, window_bits)
        if audit:
            exact_a = coefficients(q, phases, i)
            local_error = sum((v-w).modulus_upper() for v, w in zip(a, exact_a))
            if mutation is None:
                require(local_error <= window_error, 'bounded recurrence window')
            max_window_error = max(max_window_error, local_error)
        h = rounded(sum((v*z for v, z in zip(a, state)), G()), bits)
        a_fir = fir_coefficients(numerator, phases, i, fir_bits)
        if audit:
            exact_fir, phase = [], G(1)
            for j, value in enumerate(numerator):
                if j:
                    phase *= phases[(i-j+1) % length]
                exact_fir.append(value*phase)
            local_error = sum((v-w).modulus_upper() for v, w in zip(a_fir, exact_fir))
            if mutation is None:
                require(local_error <= fir_error, 'bounded FIR coefficient window')
            max_fir_error = max(max_fir_error, local_error)
        value = a_fir[0]*(x[i]+h)
        for j in range(1, len(numerator)):
            causal = x[i-j] if i >= j else G()
            past = state[j-1]
            if mutation == 'omit_negative_history' and i < j:
                past = G()
            if audit:
                max_past_size = max(max_past_size, (causal+past).modulus_upper())
            value += a_fir[j]*(causal+past)
        y[i] += sign*rounded(value, bits)
        state = [h]+state[:-1]
    for i in range(length-1, -1, -1):
        a = coefficients(q, phases, i, window_bits)
        x[i] -= rounded(sum((a[j-1]*x[i-j] for j in range(1, min(k, i)+1)), G()), bits)
    if audit and mutation is None:
        require(max_past_size <= value_bound, 'FIR boundary and interior value envelope')
    details = dict(order=k, scalar_bits=scalar_bits, window_bits=window_bits,
                   gauge_bits=gauge_bits, fir_bits=fir_bits, numerator_mass=numerator_mass,
                   max_fir_error=max_fir_error, fir_error_bound=fir_error,
                   max_window_error=max_window_error, window_error_bound=window_error,
                   max_past_size=max_past_size, value_bound=value_bound, solver=solver_audit)
    return numerator_mass*filter_error+2*u, details


def compose(x, y, inside, outside, phases, direction, scale, bits, sign=1, mutation=None, audit=False,
            wiener_bound=None):
    require(x is not y and len(x) == len(y) == len(phases) > 0, 'two-array contract')
    require(all(fixed is not array for fixed in (phases, inside[0], outside[0]) for array in (x, y)),
            'fixed coefficient and phase arrays distinct from mutable data')
    require(direction in [-1, 1] and sign in [-1, 1], 'direction and sign')
    require(type(bits) is int and bits >= 0, 'working precision')
    require(all(v.norm2() == 1 for v in phases), 'unit input phases')
    require(all(rounded(v, bits) == v for array in (x, y) for v in array), 'incoming working grid')
    D = max(v.upper() for v in x)
    groups, error, prep = prepare(inside, outside, scale, D, bits, wiener_bound)
    if sign == -1:
        groups.reverse()
    calls = []
    for is_inside, q, numerator, K, S in groups:
        orientation = -direction if is_inside else direction
        physical = (lambda i: i) if orientation == 1 else (lambda i: len(x)-1-i)
        source = reference.IndexView(len(x), lambda i: x[physical(i)], lambda i, v: x.__setitem__(physical(i), v))
        target = reference.IndexView(len(y), lambda i: y[physical(i)], lambda i, v: y.__setitem__(physical(i), v))
        if is_inside:
            local_phases = reference.IndexView(len(x), lambda i: phases[(physical(i)+direction) % len(x)].conjugate())
        else:
            local_phases = reference.IndexView(len(x), lambda i: phases[physical(i)])
        local_error, leaf_audit = filtered_add(source, target, q, numerator, local_phases, bits, K, S, sign, mutation, audit)
        calls.append(dict(inside=is_inside, K=K, S=S, error_bound=local_error, **leaf_audit))
        error += local_error
    return error, dict(preparation=prep, calls=calls)
