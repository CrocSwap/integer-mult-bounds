"""Sufficient all-radix exponent bounds and exact polynomial cap identities."""
from pathlib import Path
import json
from math import comb


def require(value, message):
    if not value:
        raise ValueError(message)


def plan(r, phi, p, incoming, magnitude, length):
    require(r >= 3 and 1 <= phi <= r and min(p, incoming, magnitude) >= 0 and length >= 1,
            'budget domain')
    ell, ell_L = (r-1).bit_length(), (length-1).bit_length()
    d0 = 1+2*ell+r*(r-1)*phi
    a0 = 2*d0+r+2
    k0 = a0+3*r+ell+2
    s0 = k0+1+r*r+2*ell
    j0 = 2*k0+ell+r+6
    W = max(incoming, p+j0+s0+7)
    polynomial = W+3*k0+2*ell+magnitude+3
    alpha = W+2*k0+magnitude+3
    numerator = W+ell+k0+magnitude+2
    window = W+r+ell+4*s0+magnitude+7
    gauge = W+ell+3*s0+magnitude+6
    scalar = W+ell_L+6*s0+ell+magnitude+7
    fir = W+ell+j0+s0+magnitude+5
    guard = magnitude+2*s0+k0+j0+r+ell+12
    require(k0+1 <= s0, 'rounded Wiener norm fits companion bound')
    require(W >= ell, 'numerator rounding mass at most one')
    require(k0+ell-polynomial <= -1, 'polynomial Neumann smallness')
    require(3*k0+2*ell+magnitude+2-polynomial <= -W,
            'polynomial helper width and both product perturbations')
    require(2*k0+2+magnitude-alpha <= -W, 'alpha perturbation')
    require(ell+k0+1+magnitude-numerator <= -W, 'each numerator perturbation')
    require(r+ell+4*s0+magnitude+6-window <= -W, 'recurrence coefficient forcing')
    require(r+ell+s0-window <= -1, 'recurrence Neumann smallness')
    require(ell+3*s0+magnitude+5-gauge <= -W, 'initial gauge forcing')
    require(ell_L+6*s0+ell+magnitude+6-scalar <= -W, 'rounded closure forcing')
    require(ell_L+3*s0+ell+3-scalar <= 0, 'closure Neumann smallness')
    require(ell_L+s0+ell+1-scalar <= 0, 'matrix product expansion smallness')
    require(ell_L-scalar <= 0, 'phase-product error at most one')
    require(ell+j0+s0+magnitude+4-fir <= -W, 'FIR coefficient forcing')
    require(j0+s0+5-W <= -p-2, 'complete additive error <= quarter target ulp')
    require(W <= max(p, incoming)+12*r**3, 'cubic data precision')
    for value, cap, name in [(polynomial, 12, 'polynomial'), (alpha, 12, 'alpha'),
                              (numerator, 12, 'numerator'), (window, 16, 'window'),
                              (fir, 12, 'FIR')]:
        require(value <= W+magnitude+cap*r**3, name+' cubic width')
    require(gauge <= window, 'gauge within window width')
    require(scalar <= W+magnitude+ell_L+24*r**3, 'cubic scalar width plus log length')
    require(guard <= magnitude+16*r**3, 'cubic integer guard')
    A = max(p, incoming)+2*magnitude+64*r**3
    require(max(W, polynomial, alpha, numerator, window, gauge, fir)+guard <= A, 'full data operand cap')
    require(scalar+guard <= A+ell_L, 'full scalar operand cap')
    return dict(r=r, phi=phi, p=p, incoming=incoming, magnitude=magnitude, length=length,
                k0=k0, s0=s0, j0=j0, working=W, polynomial=polynomial, alpha=alpha,
                numerator=numerator, window=window, gauge=gauge, scalar=scalar, fir=fir,
                integer_guard=guard, data_cap=A, scalar_cap=A+ell_L)


def plus(*polynomials):
    out = [0]*max(map(len, polynomials))
    for polynomial in polynomials:
        for j, value in enumerate(polynomial):
            out[j] += value
    return out


def times(number, polynomial):
    return [number*value for value in polynomial]


def shift_three(polynomial):
    return [sum(value*comb(j, i)*3**(j-i) for j, value in enumerate(polynomial) if j >= i)
            for i in range(len(polynomial))]


def identities():
    # Replace phi and ell by r in monotone expressions, for all r>=3.
    r, one = [0, 1], [1]
    d = [1, 2, -1, 1]  # 1+2r+r(r-1)r
    a = plus(times(2, d), r, [2])
    k = plus(a, times(4, r), [2])
    s = plus(k, [1, 2, 1])
    j = plus(times(2, k), times(2, r), [6])
    expressions = {
        'working': (12, plus(j, s, [7])),
        'polynomial': (12, plus(times(3, k), times(2, r), [3])),
        'alpha': (12, plus(times(2, k), [3])),
        'numerator': (12, plus(r, k, [2])),
        'window': (16, plus(times(2, r), times(4, s), [7])),
        'scalar': (24, plus(times(6, s), r, [7])),
        'fir': (12, plus(r, j, s, [5])),
        'guard': (16, plus(times(2, s), k, j, times(2, r), [12])),
    }
    expected = dict(working=[82, 161, 59, 6], polynomial=[108, 169, 60, 6],
                    alpha=[183, 222, 76, 8], numerator=[250, 272, 92, 10],
                    window=[79, 194, 76, 8], scalar=[128, 293, 114, 12],
                    fir=[81, 160, 59, 6], guard=[25, 157, 62, 6])
    result = {}
    for name, (cap, polynomial) in expressions.items():
        remainder = plus([0, 0, 0, cap], times(-1, polynomial))
        shifted = shift_three(remainder)
        require(shifted == expected[name] and all(value >= 0 for value in shifted),
                'all-size nonnegative coefficient identity: '+name)
        result[name] = dict(cap=cap, upper_polynomial=polynomial,
                            remainder_in_r_minus_three=shifted)
    return result


def main():
    rows = []
    for r in list(range(3, 257))+[512, 1024, 4096, 1 << 20]:
        for p, incoming, magnitude in [(0, 0, 0), (128, 32, 20), (32, 256, 4096)]:
            for length in [1, 17, 1 << 80]:
                rows.append(plan(r, r, p, incoming, magnitude, length))
    result = dict(status='PASS_ADDITIVE_BUDGETS', rows=rows, identities=identities(),
                   scope='All-size sufficient bounds conditional on the inherited prime-power common Wiener premise; '
                         'the sweep includes non-prime-powers only as algebraic checks.')
    print('PASS', len(rows), 'additive budget rows and', len(result['identities']), 'exact coefficient identities')
    return result


if __name__ == '__main__':
    main()
