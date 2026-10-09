"""Exact log_upper, moment function(s) extracted from icekylinx PR104.
Original: scripts/partial_swap_network.py, commit 948ce1510df750f4c18b96bdaef436a86f8bf834,
SHA-256 acdd81b4dea2815f8838a0c3ea8ac4968f2bc13fd7c99173473d865779096782. Apache-2.0; see NOTICE.
"""
from fractions import Fraction as Q
from common import require

def log_upper(value):
    value = Q(value)
    require(value >= 1, 'Log argument below one')
    power = 0
    while value > 2:
        value /= 2
        power += 1
    def series(x):
        z = (x-1)/(x+1)
        return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)), Q(0)) + 2*z**49/(49*(1-z*z))
    scaled = (power*series(Q(2)) + series(value))*10**12
    return Q(-(-scaled.numerator//scaled.denominator), 10**12)

def moment(m, W, rows, saving, sharp):
    upper = Q(0)
    logs = {}
    for t, count in sorted(rows.items()):
        require(0 < t < m and count >= 0, 'Invalid recursive child')
        ell = log_upper(Q(m, t))
        u = saving*ell
        require(0 <= u < 1, 'Exponential enclosure outside range')
        bound = 1+u+u*u/(2*(1-u/3)) if sharp else 1/(1-u)
        upper += Q(count*t, W*m)*bound
        logs[str(t)] = ell
    require(upper < 1, 'Characteristic moment does not contract')
    return dict(saving=saving, exponent=1-saving, moment_upper=upper,
                strict_gap=1-upper, logarithm_upper_bounds=logs,
                child_width_multiplicities=sorted(rows.items()),
                enclosure='1+u+u^2/(2(1-u/3))' if sharp else '1/(1-u)')
