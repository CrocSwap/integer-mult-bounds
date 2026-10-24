"""Solve a dyadic cyclic band system with an explicit variable-gap budget.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Classical diagonal-dominance and elimination credit is in PROOF.md.
"""
from fractions import Fraction as Q


def need(value, message):
    if not value:
        raise ValueError(message)


def trunc(a, b):
    need(b > 0, 'positive divisor required')
    return a//b if a >= 0 else -((-a)//b)


def budget(n, delta, norm, rhs_bound, tolerance, input_bits):
    delta, norm, rhs_bound, tolerance = map(Q, (delta, norm, rhs_bound, tolerance))
    need(n > 0 and 0 < delta <= norm and rhs_bound > 0 and tolerance > 0 and input_bits >= 0,
         'invalid budget')
    k = max(Q(1), 2*norm)
    ceiling = min(delta/(2*n*k), tolerance*delta**2/(2*n*k*rhs_bound+4*delta+12*norm**2))
    bits = input_bits
    while Q(1, 1 << bits) > ceiling:
        bits += 1
    h = Q(1, 1 << bits)
    eta = n*k*h
    lower_norm, upper_norm = 2*norm/delta, Q(3, 2)*norm
    solve_residual = 2*h*(1+3*norm**2/delta)
    z_bound = 3*norm/delta*(rhs_bound+2*h)
    x_bound = 2/delta*(rhs_bound+solve_residual)
    accumulator = max(Q(1), norm+lower_norm*upper_norm,
                      rhs_bound+lower_norm*z_bound, z_bound+upper_norm*x_bound,
                      lower_norm, upper_norm, rhs_bound, z_bound, x_bound)
    magnitude_bits = 0
    while 1 << magnitude_bits < accumulator:
        magnitude_bits += 1
    return {'bits': bits, 'word_bits': 2*bits+magnitude_bits+2, 'delta': delta,
            'norm': norm, 'rhs_bound': rhs_bound, 'tolerance': tolerance,
            'factor_residual': eta, 'solve_residual': solve_residual,
            'error': (eta*rhs_bound+delta*solve_residual)/(delta*(delta-eta)),
            'lower_norm': lower_norm, 'upper_norm': upper_norm,
            'z_bound': z_bound, 'x_bound': x_bound, 'accumulator_bound': accumulator}


class Guard:
    def __init__(self, bits):
        self.limit = (1 << (bits-1))-1
        self.peak = 0

    def __call__(self, value):
        need(type(value) is int and abs(value) <= self.limit, 'integer word overflow')
        self.peak = max(self.peak, abs(value))
        return value


def factor(rows, input_bits, width, delta, norm, rhs_bound, tolerance):
    n = len(rows)
    need(type(width) is int and 0 <= width < n and type(input_bits) is int and input_bits >= 0,
         'invalid shape or input grid')
    scale_in = 1 << input_bits
    delta, norm = Q(delta), Q(norm)
    for i, row in enumerate(rows):
        need(all(type(j) is int and 0 <= j < n and type(x) is int for j, x in row.items()), 'invalid coefficient')
        need(all(min(abs(i-j), n-abs(i-j)) <= width for j, x in row.items() if x), 'outside cyclic band')
        diagonal = row.get(i, 0)
        off = sum(abs(x) for j, x in row.items() if j != i)
        need(diagonal > 0 and diagonal-off >= delta*scale_in, 'row gap violated')
        need(diagonal+off <= norm*scale_in, 'row norm violated')
    plan = budget(n, delta, norm, rhs_bound, tolerance, input_bits)
    need(plan['factor_residual'] <= delta/2 and plan['error'] <= tolerance, 'precision gate failed')
    bits = plan['bits']; scale = 1 << bits; checked = Guard(plan['word_bits'])
    shift = bits-input_bits
    active = [{j: checked((x << shift)*scale) for j, x in row.items() if x} for row in rows]
    columns = [set() for _ in range(n)]
    for i, row in enumerate(active):
        for j in row: columns[j].add(i)
    lower, upper = [dict() for _ in rows], [dict() for _ in rows]
    products = divisions = max_front = 0
    for k in range(n):
        upper[k] = {j: checked(trunc(value, scale)) for j, value in active[k].items() if j >= k}
        divisions += len(upper[k])
        pivot = upper[k].get(k, 0)
        need(pivot >= delta*scale/2, 'pivot bound failed')
        successors = sorted(i for i in columns[k] if i > k)
        outgoing = [j for j in upper[k] if j > k]
        max_front = max(max_front, len(successors), len(outgoing))
        need(len(successors) <= 2*width and len(outgoing) <= 2*width, 'cyclic fill bound failed')
        for i in successors:
            multiplier = checked(trunc(active[i].pop(k), pivot))
            divisions += 1
            lower[i][k] = multiplier
            for j in outgoing:
                product = checked(multiplier*upper[k][j]); products += 1
                active[i][j] = checked(active[i].get(j, 0)-product)
                columns[j].add(i)
        for j in active[k]: columns[j].discard(k)
        active[k].clear(); columns[k].clear()
    need(products <= 4*n*width**2, 'factor product budget failed')
    records = sum(map(len, lower))+sum(map(len, upper))
    need(records <= (4*width+1)*n, 'factor storage bound failed')
    return {'lower': lower, 'upper': upper, 'plan': plan, 'width': width,
            'statistics': {'products': products, 'divisions': divisions, 'factor_records': records,
                           'maximum_front': max_front, 'peak_integer_bits': checked.peak.bit_length()}}


def solve(factors, rhs, rhs_bits):
    lower, upper, plan = factors['lower'], factors['upper'], factors['plan']
    n, bits = len(lower), plan['bits']; scale = 1 << bits
    need(type(rhs_bits) is int and 0 <= rhs_bits <= bits and len(rhs) == n, 'invalid RHS grid or length')
    need(all(len(x) == 2 and all(type(t) is int for t in x) for x in rhs), 'integer complex pairs required')
    need(all(sum(abs(t) for t in x) <= plan['rhs_bound']*(1 << rhs_bits) for x in rhs), 'RHS bound violated')
    checked = Guard(plan['word_bits']); products = divisions = 0
    z = [[0, 0] for _ in rhs]; result = [[0, 0] for _ in rhs]
    for i in range(n):
        for c in (0, 1):
            accumulator = checked((rhs[i][c] << (bits-rhs_bits))*scale)
            for j, value in lower[i].items():
                accumulator = checked(accumulator-checked(value*z[j][c])); products += 1
            z[i][c] = checked(trunc(accumulator, scale)); divisions += 1
    for i in reversed(range(n)):
        for c in (0, 1):
            accumulator = checked(z[i][c]*scale)
            for j, value in upper[i].items():
                if j > i:
                    accumulator = checked(accumulator-checked(value*result[j][c])); products += 1
            result[i][c] = checked(trunc(accumulator, upper[i][i])); divisions += 1
    need(products <= 8*n*factors['width'], 'solve product budget failed')
    for pair in z: pair[:] = [0, 0]
    return result, {'products': products, 'divisions': divisions,
                    'cleared_scratch_cells': 2*n, 'peak_integer_bits': checked.peak.bit_length()}
