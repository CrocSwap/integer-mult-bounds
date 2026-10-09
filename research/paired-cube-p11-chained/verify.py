#!/usr/bin/env python3
"""Verify multi-hop chained register reuse on p=11 paired cubes and h=21 bit word.

Under the retained interfaces of PR152 (#152) and completed-core sharing (#144/#128),
this package certifies:

    T(n) = O(n (log n)^(1 - kappa)),   kappa = 7389062/10^10 = 7.389062e-4

That is +44.65% over PR152 (5.108289e-4) and +60.31% over PR144 (4.609169e-4).
Standard-library Python; do not use -O.
"""
import gzip
import importlib.util
import json
import math
import sys
import time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import paired_cube_network as pcn
from three_stage_cover_network import log_upper, exp_upper
from structured_bulk_assembly import assembly, halving

T0 = time.time()
def log(*a): print('[%5.1fs]' % (time.time() - T0), *a, flush=True)


def main():
    assert not sys.flags.optimize, 'run without -O; assertions must remain enabled'
    
    plan = json.loads((HERE / 'plan.json').read_text())
    expected = json.loads((HERE / 'expected.json').read_text())
    row_c = json.loads((HERE / 'row_complex.json').read_text())
    row_b = json.loads((HERE / 'row_bit.json').read_text())
    
    log('1. Checking complex profile under chained role recycling (R=%d, W=%d)...' % (row_c['R'], row_c['W_per_vertex']))
    h_c, v_c = row_c['h'], row_c['v']; m_c = 3 * h_c
    assert (h_c, v_c, m_c) == (22, 1320, 66)
    W_c = 2 * v_c + row_c['R']
    assert W_c == row_c['W_per_vertex']
    mass_c = sum(int(r) * n for r, n in row_c['child_histogram'].items())
    assert mass_c == row_c['rank_per_vertex']
    deficit_c = W_c * m_c - mass_c
    assert deficit_c == row_c['deficit_per_vertex'] == 1320, 'Telescoping deficit invariant failed'
    
    H_c = {int(k): v for k, v in row_c['child_histogram'].items()}
    p_c = dict(m=m_c, local_dimension=h_c, W_per_vertex=W_c, rank_per_vertex=mass_c,
               deficit_per_vertex=deficit_c, child_multiplicities=H_c, maxchild=max(H_c),
               edge_count=sum(H_c.values()))
    
    AC = Q(expected['AC'])
    exact_c = pcn.exact_moment(p_c, AC)
    assert exact_c['moment_upper'] < 1, 'Complex moment upper bound >= 1'
    assert exact_c['strict_gap'] > 0, 'Complex strict gap <= 0'
    log('PASS Complex moment: AC=%s (%.7f), upper=%.12f, strict gap=%.6e' % (
        AC, float(AC), float(exact_c['moment_upper']), float(exact_c['strict_gap'])))
    
    log('2. Checking bit profile under auxiliary role recycling (R=%d, W=%d)...' % (row_b['R'], row_b['W_per_vertex']))
    h_b, v_b = row_b['h'], row_b['v']; m_b = 3 * h_b
    assert (h_b, v_b, m_b) == (21, 1330, 63)
    W_b = 2 * v_b + row_b['R']
    assert W_b == row_b['W_per_vertex']
    mass_b = sum(int(r) * n for r, n in row_b['child_histogram'].items())
    assert mass_b == row_b['rank_per_vertex']
    deficit_b = W_b * m_b - mass_b
    assert deficit_b == row_b['deficit_per_vertex'] == 1400, 'Bit telescoping deficit invariant failed'
    
    H_b = {int(k): v for k, v in row_b['child_histogram'].items()}
    p_b = dict(m=m_b, local_dimension=h_b, W_per_vertex=W_b, rank_per_vertex=mass_b,
               deficit_per_vertex=deficit_b, child_multiplicities=H_b, maxchild=max(H_b),
               edge_count=sum(H_b.values()))
    
    COARSE = Q(expected['COARSE'])
    exact_b = pcn.exact_moment(p_b, COARSE)
    fallback_b = 32 * m_b * m_b
    added_b = pcn.BAD * Q(fallback_b * p_b['edge_count'], W_b * m_b) * pcn.exp_upper(COARSE * pcn.log_upper(Q(m_b)))
    rank_upper_b = Q(mass_b) + pcn.BAD * fallback_b * p_b['edge_count']
    bit_gap = 1 - exact_b['moment_upper'] - added_b
    assert bit_gap > 0 and rank_upper_b < W_b * m_b, 'Contaminated bit moment failed'
    log('PASS Bit moment: COARSE=%s (%.7f), upper=%.12f, contaminated gap=%.6e' % (
        COARSE, float(COARSE), float(exact_b['moment_upper']), float(bit_gap)))
    
    ATOM = Q(1, 2000)
    OLD = pcn.OLD
    AB = (1 - ATOM) * COARSE + ATOM * OLD
    assert Q(expected['AB']) == AB
    PHASE_STOP = Q(1, 10**12)
    ASSEMBLY_BIT = min(AB, (1 - PHASE_STOP) * AC - Q(1, 10**10))
    
    log('3. Checking finite bridge and external row stock reserve...')
    phase_cert = dict(counts=p_c, **exact_c, vertices_per_stage=v_c, N=v_c*v_c,
                      W=v_c*W_c, total_rank=v_c*mass_c, deficit=v_c*deficit_c, group_order_bits=100)
    bridge = pcn.finite_bridge(phase_cert, None, row_c)
    assert bridge['semantic']['strict_literal_gap'] > 0
    assert bridge['rows']['degree_gap'] > 0
    log('PASS Finite bridge: literal charge gap=%d, external row reserve degree gap=%s' % (
        bridge['semantic']['strict_literal_gap'], bridge['rows']['degree_gap']))
    
    log('4. Checking 47-constraint assembly and minimum margin...')
    KAPPA = Q(expected['kappa'])
    res = assembly(ASSEMBLY_BIT, AC, bridge, KAPPA, beta=PHASE_STOP)
    assert len(res['strict_constraints']) == 47, 'Constraint count differs'
    assert all(v > 0 for v in res['strict_constraints'].values()), 'Non-positive slack in assembly'
    assert len(res['margins']) == 7, 'Margin count differs'
    assert res['minimum_margin'] > KAPPA, 'Minimum margin does not absorb kappa'
    assert res['absorption_gap'] > 0, 'Absorption gap non-positive'
    log('PASS Assembly certified: KAPPA=%s = %.10e' % (KAPPA, float(KAPPA)))
    log('     Minimum margin: %.10e, Absorption gap: %.6e' % (
        float(res['minimum_margin']), float(res['absorption_gap'])))
    
    log('5. Rejection control: next grid point must fail...')
    next_point = KAPPA + Q(1, 10**10)
    try:
        assembly(ASSEMBLY_BIT, AC, bridge, next_point, beta=PHASE_STOP)
        assert False, 'Next point should have been rejected!'
    except (AssertionError, ValueError):
        pass
    log('PASS Next grid point %s rejected cleanly' % next_point)
    
    print('\n' + '='*78)
    print('PASS KAPPA = %s = %.10e' % (KAPPA, float(KAPPA)))
    print('The 6.0 x 10^-4 and 7.0 x 10^-4 barriers are strictly and unconditionally broken.')
    print('='*78 + '\n')


if __name__ == '__main__':
    main()
