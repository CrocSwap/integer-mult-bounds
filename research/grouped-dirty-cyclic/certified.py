"""Exact-rational checks of an all-length real periodic dirty filter.

Scalar matrix preparation can use dyadic rounded binary powering. The solver
is still exact rational Gaussian elimination; its time/space are not free.
This is local research, not a complete multiplication or Clifford compiler.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from real_reference import exact, identity, multiply, poly, power, rounded, solve

P = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def norm(a):
    return max(sum(abs(v) for v in row) for row in a)


def difference(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def companion(q):
    k = len(q) - 1
    return [[-v for v in q[1:]]] + [
        [F(j == i - 1) for j in range(k)] for i in range(1, k)
    ]


def constants(roots):
    require(bool(roots) and all(abs(b) < 1 for b in roots), 'stable roots')
    q = poly(roots)
    c = companion(q)
    k = len(roots)
    K = F(1)
    for b in roots:
        K /= 1 - abs(b)
    # adj(I-zC) = sum B_j z^j. Verify the terminal coefficient too.
    B = identity(k)
    mass = norm(B)
    for j in range(1, k + 1):
        B = multiply(c, B)
        for i in range(k):
            B[i][i] += q[j]
        if j < k:
            mass += norm(B)
        else:
            require(norm(B) == 0, 'Cayley-Hamilton terminal coefficient')
    return q, c, K, K * mass


def rounded_power(c, length, bits):
    """An unfolded tree has length leaves and length-1 rounding nodes."""
    require(length >= 0 and bits >= 0, 'power domain')
    if length == 0:
        return identity(len(c))
    if length == 1:
        return [row.copy() for row in c]
    half = rounded_power(c, length // 2, bits)
    out = [[rounded(v, bits) for v in row] for row in multiply(half, half)]
    if length % 2:
        out = [[rounded(v, bits) for v in row] for row in multiply(out, c)]
    return out


def preparation(q, length, bits, K, S, D, mode='rounded'):
    """Choose scalar precision so closure error contributes at most one ulp."""
    c = companion(q)
    k = len(c)
    u = F(1, 1 << bits)
    if mode == 'exact':
        return power(c, length), F(0), None
    require(mode == 'rounded', 'preparation mode')
    scalar_bits = bits
    while True:
        delta = F(k, 2 << scalar_bits)
        nodes = max(0, length - 1)
        error = 2 * nodes * S * S * delta
        if (nodes * S * delta <= F(1, 2)
                and error <= 1 / (2 * S)
                and 2 * S**3 * error * K * (D + u / 2) <= u):
            break
        scalar_bits += 1
    return rounded_power(c, length, scalar_bits), error, scalar_bits


def apply(x, y, q, bits, M, sign=1, mutation=None):
    k = len(q) - 1
    length = len(x)
    require(k > 0 and length > 0 and len(y) == length and x is not y
            and q[0] == 1 and sign in (-1, 1), 'filter contract')
    require(all(rounded(z, bits) == z for z in x + y), 'fixed grid')
    for i in range(length):
        x[i] += rounded(-sum(q[j] * x[i-j] for j in range(1, min(k, i)+1)), bits)
    tail = [x[length-1-j] if j < length else F(0) for j in range(k)]
    if mutation == 'wrong_tail':
        tail = list(reversed(tail))
    closure_sign = 1 if mutation == 'wrong_closure' else -1
    closure = [[F(i == j) + closure_sign * M[i][j] for j in range(k)]
               for i in range(k)]
    state = [rounded(v, bits if mutation != 'coarse_seed' else 0)
             for v in solve(closure, tail)]
    if mutation == 'omit_seed':
        state = [F(0)] * k
    for i in range(length):
        h = rounded(-sum(a*b for a, b in zip(q[1:], state)), bits)
        y[i] += sign * (x[i] + h)
        state = [h] + state[:-1]
    for i in range(length-1, -1, -1):
        if mutation == 'omit_undo' and i == length-1:
            continue
        x[i] -= rounded(-sum(q[j] * x[i-j] for j in range(1, min(k, i)+1)), bits)


def main():
    root_sets = [
        [F(1, 2)], [F(-3, 4), F(1, 4)], [F(15, 16)]*3,
        [F(0), F(1, 2), F(-1, 2), F(3, 4)], [F(1, 2)]*5,
        [F(-7, 8)]*4, [F(0)]*3,
        [F(4095, 8192), F(-2047, 4096)],
    ]
    rows = []
    controls = {key: [] for key in
                ['wrong_closure', 'wrong_tail', 'omit_seed', 'coarse_seed', 'omit_undo']}
    nonzero_rounding = 0
    for roots in root_sets:
        q, c, K, S = constants(roots)
        for length in [1, 2, 3, 8, 17]:
            for bits in [32, 80]:
                u = F(1, 1 << bits)
                x0 = [F(2*i-7, 8)+u for i in range(length)]
                y0 = [F(11-i, 16)-u for i in range(length)]
                require(all((z/u).denominator == 1 and (z/u).numerator % 2
                            for z in x0+y0), 'arbitrary nonzero low bits')
                want = exact(x0, q)
                D = max(abs(v) for v in x0)
                ideal_M = power(c, length)
                for mode in ['exact', 'rounded']:
                    M, power_bound, scalar_bits = preparation(q, length, bits, K, S, D, mode)
                    matrix_error = norm(difference(M, ideal_M))
                    require(matrix_error <= power_bound, 'rounded binary power bound')
                    nonzero_rounding += bool(matrix_error)
                    bound = (K+2*S)*u/2 + 2*S**3*power_bound*K*(D+u/2)
                    x, y = x0.copy(), y0.copy()
                    apply(x, y, q, bits, M)
                    require(x == x0, 'exact dirty source restoration')
                    error = max(abs(a-b-cv) for a, b, cv in zip(y, y0, want))
                    require(error <= bound, 'all-length output error bound')
                    net = [a-b for a, b in zip(y, y0)]
                    apply(x, y, q, bits, M, -1)
                    require(x == x0 and y == y0, 'exact inverse cancellation')
                    row_id = len(rows)
                    rows.append(dict(id=row_id, roots=list(map(str, roots)), length=length,
                                     bits=bits, mode=mode, scalar_bits=scalar_bits,
                                     K=str(K), S=str(S), error=str(error), bound=str(bound),
                                     power_error=str(matrix_error), power_bound=str(power_bound),
                                     source_restored=True, inverse_cancels=True,
                                     net_sha256=hashlib.sha256(json.dumps(net, default=str).encode()).hexdigest()))
                    if bits == 32 and mode == 'rounded':
                        for mutation in controls:
                            mx, my = x0.copy(), y0.copy()
                            apply(mx, my, q, bits, M, mutation=mutation)
                            bad = (mx != x0 or max(abs(a-b-cv) for a, b, cv in zip(my, y0, want)) > bound)
                            if bad:
                                controls[mutation].append(row_id)
    require(nonzero_rounding > 0, 'nonvacuous rounded matrix preparation')
    require(all(controls.values()), 'every deliberate defect must be detected')
    result = dict(status='PASS', cases=rows, controls=controls,
                  nonzero_matrix_rounding_cases=nonzero_rounding,
                  scope='Real unweighted periodic filter; exact coefficients and rational closure solve. '
                        'Finite checks of the stated uniform error inequalities; no full compiler or kappa claim.')
    print('PASS', len(rows), 'certified cases;', nonzero_rounding,
          'nonzero matrix-rounding cases; controls', {key: len(v) for key, v in controls.items()})
    return result


if __name__ == '__main__':
    main()
