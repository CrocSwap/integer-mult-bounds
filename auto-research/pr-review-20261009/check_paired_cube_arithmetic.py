#!/usr/bin/env python3
"""Independent PR144 arithmetic review; Apache-2.0.

Maintainer review with OpenAI Codex assistance. Reads submitted inventories;
does not replace their scalar/frame reconstruction or the written compiler.
Uses the maintainer enclosure implementation already on main.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from collections import Counter
from fractions import Fraction as Q
import json
from math import prod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_community_candidate import moment


def check(candidate):
    cert = json.loads((candidate/'certificates/paired-cube-network.json').read_text())
    gaps = {}
    for axis, saving in (('bit', Q(4617656, 10**10)), ('complex', Q(4856569, 10**10))):
        row = json.loads((candidate/f'certificates/paired-cube-{axis}-input.json').read_text())
        h, v, R, loss = (row[k] for k in ('h', 'v', 'R', 'loss'))
        m, W = 3*h, 2*v+R
        H = Counter()
        if axis == 'complex':
            H.update({r:3*n for r,n in enumerate(row['remaining_internal_histogram']) if r and n})
            parts = ['source_data_histogram', 'target_data_histogram']
            assert (h, v, R, loss) == (24, 1760, 26417, 528)
            assert R == row['c']+row['q']-row['matched']
        else:
            parts = ['auxiliary_histogram', 'source_data_histogram', 'target_data_histogram', 'copied_center_histogram']
        for part in parts:
            H.update({int(r):3*n for r,n in row[part].items() if int(r) and n})
        H.update({3*int(r):n for r,n in row['selected_rank_histogram'].items()})
        H[2] += 2*v
        assert dict(H) == {int(r):n for r,n in cert[axis]['counts']['child_multiplicities'].items()}
        assert sum(r*n for r,n in H.items()) == m*W-2*v+3*loss
        assert (m, W) == (cert[axis]['counts']['m'], cert[axis]['counts']['W_per_vertex'])
        lower, upper = moment(m, W, H.items(), saving)
        assert lower <= upper < 1
        if axis == 'bit':
            # Add the entire fallback, not a net replacement of good children.
            _, fallback = moment(m, W, [(1, 32*m*m*sum(H.values()))], saving)
            upper += fallback/Q(10**16)
            assert upper < 1
            assert Q(2*m**3, 2**80) < Q(1,10**16)
        gaps[axis] = {'certified_lower':str(1-upper), 'approx':float(1-upper)}
    actual = Q(999,1000)*Q(4617656,10**10)+Q(1,1000)*Q(384599,10**10)
    assert actual == Q(4613422943,10**13)
    p = {k:Q(v) for k,v in cert['assembly']['parameters'].items()}
    a,b,beta,eta = (p[k] for k in ('a_bit','a_complex','beta','eta'))
    assert a == actual and (1-beta)*b > a and Q(1,1000) > a
    q = a*(1-2*eta)
    c = q*(1+eta)
    eps = (1-eta)/(1+c+q)
    g = eps*q
    r,delta = (g+1-eps)/2,eta/8
    margins = {'original_prefix':1-eps*(1+c), 'coordinate_movement':a,
               'compact_phase_layer':g, 'bulk_exposure':a,
               'Gaussian_arithmetic':min(1-eps-delta,r-delta),
               'scalar_work':1-eps-delta, 'dimension':eps}
    assert margins == {k:Q(v) for k,v in cert['assembly']['margins'].items()}
    kappa = Q(cert['kappa'])
    assert kappa == Q(4609169,10**10) < min(margins.values()) == g
    assert g < kappa+Q(1,10**10)
    assert len(cert['assembly']['strict_constraints']) == 47
    assert all(Q(v)>0 for v in cert['assembly']['strict_constraints'].values())
    order = 2**1296*prod(2**(2*i)-1 for i in range(1,36))
    assert order == cert['complex']['vertices_per_stage']
    assert order.bit_length() == 2556 and (order*29937).bit_length() == 2571
    assert 72**3 <= 2*60**3 and 72**4 > 2*60**4
    assert 4*2571+9909+252 == 20445
    assert 70000 > Q(51,25)*20445
    return dict(status='PASS', kappa=str(kappa), independent_moment_gaps=gaps,
                absorption_gap=str(g-kappa), absorption_gap_approx=float(g-kappa),
                next_decimal_grid_rejected=True, full_group_order_bits=2556,
                scope='Inventory arithmetic and independent interval moments; no replacement for finite witnesses or all-size proof')


if __name__ == '__main__':
    print(json.dumps(check(Path(sys.argv[1])), indent=2))
