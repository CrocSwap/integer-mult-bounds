#!/usr/bin/env python3
"""Exact stopped product-ring moments, rational-center guard and assembly.

Copyright 2026 icekylinx. Apache-2.0.
Developed with substantial OpenAI GPT-6 Astra and Codex assistance.
Retains the copied-center two-stage construction, Paureel/PR29 topology,
PR23 semantic assembly and RaD analytic interfaces; see SOURCES.json.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import sys

from certify import require
from copied_centers.physical import copied_histogram
from copied_centers_network import finite_bridge as copied_bridge, grid_upper
from partial_swap_network import moment
from structured_bulk_assembly import assembly, js

ROOT = Path(__file__).resolve().parents[1]
COARSE = Q(4019, 50000000)
ATOM = Q(1, 1000)
OLD = Q(384599, 10**10)
AB = (1-ATOM)*COARSE+ATOM*OLD
AC = Q(1949, 25000000)
PHASE_STOP = Q(1, 10**6)
ASSEMBLY_BIT = min(AB, (1-PHASE_STOP)*AC-Q(1, 10**10))
KAPPA = Q(194869, 2500000000)


def profile(row):
    h, v, R, ell = (row[k] for k in ('h', 'v', 'R', 'loss'))
    require(v == comb(h, 3), 'Triple count')
    H = copied_histogram(row)['histogram']
    m, N, B = h*h, v*v, v*R
    W, L = 2*N+2*B, 2*v*ell
    z = Counter({m-h:2*B, (h-1)**2:2*N, h-1:4*N, 1:N})
    for r, n in enumerate(H):
        if r and n:
            z[r] += 2*v*n
    z = dict(sorted((t,n) for t,n in z.items() if n))
    s = W*m-N+L
    require(all(0 < t < m and n > 0 for t,n in z.items()), 'Shrinking children')
    require(sum(t*n for t,n in z.items()) == s, 'Complete rank mass')
    return dict(dimensions=[h,h], m=m, N=N, B1=B, B2=B, W=W, L=L,
                total_rank=s, deficit=N-L, maxchild=max(z),
                copied_histogram=H, child_multiplicities=z)


def coarse_moment(p):
    def log_upper(x):
        power = 0
        while x >= 2:
            x /= 2
            power += 1
        def small(y):
            z = (y-1)/(y+1)
            return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)), Q(0)) + 2*z**49/(49*(1-z*z))
        return grid_upper(power*small(Q(2))+small(x))
    total, logs = Q(0), {}
    for t, n in p['child_multiplicities'].items():
        logs[t] = log_upper(Q(p['m'],t))
        u = COARSE*logs[t]
        require(0 < u < 3, 'Coarse exponential enclosure')
        total += n*t*grid_upper(1+u+u*u/(2*(1-u/3)))
    upper = total/(p['W']*p['m'])
    mass = Q(p['total_rank'],p['W']*p['m'])
    require(mass < 1 and upper < 1, 'Both stopped-recurrence moments')
    require(0 < OLD <= COARSE < ATOM < 1, 'Stopped-adapter exponents')
    require(ATOM > AB, 'Adapter toll subordinate to the stopped saving')
    return dict(saving=COARSE, exponent=1-COARSE, moment_upper=upper,
                strict_gap=1-upper, rank_moment=mass,
                logarithm_upper_bounds=logs, rounding_denominator=1 << 100,
                stopped_adapter=dict(atom_exponent=ATOM, base_ordinary_saving=OLD,
                    effective_saving=AB, coarse_toll_exponent=1-ATOM,
                    coarse_toll_subordinate_gap=ATOM-COARSE))


def finite_bridge(bit, phase, row, previous):
    bridge = copied_bridge(bit, phase, [row,row])
    old_bit = previous['finite_bridge']['bit']
    old_degree = old_bit['halving_degree']*old_bit['wire_bits']
    require(old_degree == 252, 'Inherited ordinary leaf row stock')
    coarse = bridge.pop('bit')
    c = bridge['complex']
    coefficient = (coarse['halving_degree']*coarse['wire_bits']+old_degree+
                   c['halving_degree']*c['wire_bits'])
    degree = 4000
    require(Q(degree) > Q(51*coefficient,25), 'Product stock strictly sufficient')
    bridge.update(bit_coarse=coarse, ordinary_leaf_row_degree=old_degree)
    bridge['rows'] = dict(coefficient=coefficient, degree=degree, suffix_slope=4*degree,
        degree_gap=Q(degree)-Q(51*coefficient,25),
        contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse')
    require(row['h'] == row['central_disjoint'] == 24, 'Selected all-disjoint centers')
    divisor = row['h']-3
    require(divisor == 21, 'Selected fixed odd divisor')
    bridge['semantic'].update(fixed_odd_divisor=divisor,
        exact_grid='One common dyadic grid times the fixed odd divisor to K=G*(D_complex+1); no child rounding')
    return bridge


def certificate():
    require(not sys.flags.optimize, 'Run without -O')
    def read(name):
        return json.loads((ROOT/'certificates'/name).read_text())
    bit_row = read('stopped-product-bit-axis.json')
    complex_row = read('stopped-product-complex-input.json')
    expected = read('stopped-product-input.json')
    previous = read('copied-centers-network.json')
    require(Q(previous['bit']['saving']) == OLD, 'Certified ordinary leaf saving')
    require(bit_row['h'] == 23, 'Selected bit dimension')
    bit, phase = profile(bit_row), profile(complex_row)
    for label,p in (('bit',bit),('complex',phase)):
        for key,value in expected[label].items():
            require(js(p[key]) == value, label+' saved '+key)
    bm = coarse_moment(bit)
    cm = moment(phase['m'],phase['W'],phase['child_multiplicities'],AC,True)
    require(bm['strict_gap'] == Q(expected['bit_moment_gap']), 'Saved coarse moment')
    require(cm['strict_gap'] == Q(expected['complex_moment_gap']), 'Saved complex moment')
    bridge = finite_bridge(bit,phase,complex_row,previous)
    assembled = assembly(ASSEMBLY_BIT,AC,bridge,KAPPA,beta=PHASE_STOP)
    require(ASSEMBLY_BIT <= AB, 'Assembly saving supported by actual bit interface')
    assembled['parameters']['actual_bit_saving'] = AB
    require(js(bridge) == expected['finite_bridge'], 'Saved semantic and product bridge')
    require(js(assembled) == expected['assembly'], 'Saved exact assembly')
    require(len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7,
            'Complete assembly constraints')
    sources = sorted(p for p in (ROOT/'certificates').glob('stopped-product-*.json')
                     if p.name != 'stopped-product-network.json')
    sources += sorted((ROOT/'scripts').glob('stopped_product*.py'))
    sources += sorted(p for p in (ROOT/'scripts/stopped_product').rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts)
    sources += sorted((ROOT/'notes').glob('stopped-product-*.tex'))
    sources += [ROOT/path for path in (
        'scripts/copied_centers/physical.py','scripts/copied_centers_network.py',
        'scripts/partial_swap_network.py','scripts/structured_bulk_assembly.py',
        'certificates/copied-centers-network.json','certificates/copied-centers-bit-axes.json')]
    return dict(status='Conditional stopped product-ring multiplication witness',kappa=KAPPA,
        bit=dict(counts=bit,**bm),complex=dict(counts=phase,**cm),
        finite_bridge=bridge,assembly=assembled,
        base_commit='56b66d58297deca1d7dd130247d720e960f77a37',
        proof_predecessor_commit='11817ccacb564bb7f98789c20dc11d3fece207e3',
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Exact finite moments, stopped savings and assembly; the new complex producer is checked separately. '
              'Opposite-bank factorization, atom streaming, ordinary conversion, common exact grid and retained analytic/tape interfaces are written proof dependencies.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'certificates/stopped-product-network.json')
    args = parser.parse_args()
    result = certificate()
    args.output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n')
    print('PASS kappa=194869/2500000000 = 7.79476e-5')
    print('Coarse and complex moments; stopped bit saving; exact rational-center guard; p^4000 stock; 47 strict constraints')


if __name__ == '__main__':
    main()
