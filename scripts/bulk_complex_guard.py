#!/usr/bin/env python3
"""Exact guard constants for selected whole-residual complex children.

The proof is in notes/bulk-complex-guard.tex. No finite producer is
regenerated; the input is a supplied fixed complex-network count record.
"""
from fractions import Fraction as Q
import json

from certify import require
from prepare_layers import serializable


def bulk_complex_guard(n, beta=Q(1, 1000), zeta=Q(1, 10000)):
    h, m, W, s = n['h'], n['m'], n['W'], n['s']
    q = m+6*h
    ranks = (m-2*h, m-h*h)
    rho = Q(6, 5)
    lower = 160000
    theta = Q(999, 1000)
    require(m == 21952 and h == 28,
            'This explicit rational path enclosure is specialized to h=28')
    require(lower**5 < m**6, 'Lower bound for m^(6/5) failed')
    require(all(2*a > q and a < m for a in ranks),
            'A dependency path could cross two selected bulk edges')
    moments = {'no_bulk': Q(q, lower)}
    for a in ranks:
        t = Q(m-a, m)
        power_upper = 1-Q(6, 5)*t+Q(3, 25)*t*t/(1-t)
        moments['rank_'+str(a)] = Q(q-a, lower)+power_upper
    require(all(x < theta for x in moments.values()),
            'Normalized arithmetic-depth path moment failed')
    E = 64*(W+m+1)**3
    require(36*W**3+4*s+4*W+8*m+4 < E,
            'Additive coefficient-depth enclosure failed')
    dependency_constant = 1000*(E+16*m+1)
    require(dependency_constant*(1-theta) >= E and dependency_constant >= 16*m,
            'Strong-induction constant failed')
    C1 = rho-(rho-1)*beta+zeta
    raw = 128*m*(1+1/zeta)*dependency_constant
    C0 = -(-raw.numerator//raw.denominator)
    require(m*(1+1/zeta)*dependency_constant+18 <= C0,
            'Completed-layer guard constant failed')
    return dict(h=h, m=m, q=q, selected_ranks=ranks,
                at_most_one_selected_edge_per_path=True,
                rho=rho, m_to_rho_lower=lower, path_moment_upper=moments,
                theta_upper=theta, theta_slack=theta-max(moments.values()),
                E=E, dependency_constant=dependency_constant,
                beta=beta, zeta=zeta, C0=C0, C1=C1)


if __name__ == '__main__':
    n = dict(h=28, m=21952, W=2085111546336, s=45772350635112192)
    print(json.dumps(serializable(bulk_complex_guard(n)), indent=2, sort_keys=True))
