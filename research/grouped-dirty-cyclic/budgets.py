"""Integer-exponent audit for the proposed prime-power grouped inverse.

The inequalities are symbolic sufficient conditions, not numerical fitting.
Rows also include non-prime-power r for the deliberately looser phi<=r audit;
only prime-power rows are claimed to inherit the original kernel theorem.
"""
from pathlib import Path
import json

P = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def plan(r, phi, p, incoming, magnitude, length):
    require(r >= 3 and 1 <= phi <= r and min(p, incoming, magnitude) >= 0 and length >= 1,
            'budget domain')
    ell = (r-1).bit_length()
    ell_L = (length-1).bit_length()
    d0 = 1+2*ell+r*(r-1)*phi
    a0 = 2*d0+r+2
    k0 = a0+3*r+ell+2
    s0 = k0+1+r*r+2*ell
    error_log = k0+s0+ell+6
    W = max(incoming, p+error_log+2)
    source_log = magnitude+k0+ell+4
    coefficient = W+2*k0+source_log+ell+3
    window = W+r+ell+4*s0+source_log+7
    scalar = W+ell_L+6*s0+ell+source_log+7
    gauge = W+ell+3*s0+source_log+6
    multiplier = W+ell+s0+source_log+4
    guard = magnitude+2*s0+3*k0+2*ell+r+12
    require(W <= max(incoming, p)+8*r**3, 'working fractional cubic cap')
    require(coefficient <= W+magnitude+12*r**3, 'polynomial coefficient cubic cap')
    require(window <= W+magnitude+16*r**3, 'phase-window cubic cap')
    require(scalar <= W+magnitude+ell_L+24*r**3, 'matrix scalar cubic-plus-log-length cap')
    require(gauge <= window, 'gauge fits window precision')
    require(multiplier <= W+magnitude+8*r**3, 'output multiplier cubic cap')
    require(guard <= magnitude+16*r**3, 'integer guard cubic cap')
    # Logarithmic sufficient bounds used by the proof, keeping the sweep tiny
    # even when r^3 and L are large. No exponential integers are constructed.
    require(error_log-W <= -p-2, 'mixed execution error <= quarter target ulp')
    require(1+2*k0+ell-coefficient+source_log <= -W, 'polynomial perturbation')
    require(r+ell-window+4*s0+source_log+6 <= -W, 'phase-window perturbation')
    require(ell_L+6*s0+ell+source_log+6-scalar <= -W, 'closure perturbation')
    require(ell+3*s0+source_log+5-gauge <= -W, 'initial gauge perturbation')
    require(ell+s0+source_log+3-multiplier <= -W, 'output multiplier perturbation')
    require(ell_L+3*s0+ell+4-scalar <= 0, 'closure Neumann smallness')
    data_cap = max(incoming, p)+2*magnitude+48*r**3
    require(max(W, coefficient, window, gauge, multiplier)+guard <= data_cap,
            'complete data-arithmetic word cap')
    require(scalar+guard <= data_cap+ell_L, 'complete scalar-arithmetic word cap')
    return dict(r=r, phi=phi, p=p, incoming=incoming, magnitude=magnitude, length=length,
                k0=k0, s0=s0, working=W, coefficient=coefficient, window=window,
                scalar=scalar, gauge=gauge, multiplier=multiplier, integer_guard=guard,
                complete_data_cap=data_cap, scalar_cap=data_cap+ell_L)


def main():
    rows = []
    for r in list(range(3, 257))+[512, 1024, 4096]:
        for p, incoming, magnitude in [(0, 0, 0), (128, 32, 20), (32, 256, 4096)]:
            for length in [1, 17, 1 << 40]:
                rows.append(plan(r, r, p, incoming, magnitude, length))
    # Polynomial remainder identities proving the simple caps for all r>=3.
    # Coefficients are ascending powers of t=r-3 and are all nonnegative.
    remainders = {
        'working_8r3': [51, 105, 39, 4],
        'window_16r3': [3, 142, 60, 6],
        'scalar_24r3': [52, 241, 98, 10],
    }
    for r in range(3, 20):
        t = r-3
        expected = [4*r**3+3*r*r-21*r-21,
                    6*r**3+6*r*r-56*r-45,
                    10*r**3+8*r*r-77*r-59]
        for coefficients, value in zip(remainders.values(), expected):
            require(sum(c*t**i for i, c in enumerate(coefficients)) == value, 'all-size polynomial identity')
    result = dict(status='PASS', rows=rows,
        all_size_nonnegative_polynomials=remainders,
        scope='Sufficient arithmetic budgets conditional on the pinned prime-power common-operator bounds. '
              'Non-prime-power rows check algebraic inequalities only; no kernel theorem is asserted for them.')
    print('PASS', len(rows), 'integer budget rows and three all-size polynomial identities')
    return result


if __name__ == '__main__':
    main()
