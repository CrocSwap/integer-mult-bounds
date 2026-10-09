#!/usr/bin/env python3
"""Exact deferred-word moments and partial-gauge semantic assembly.

Copyright 2026 icekylinx. Apache-2.0.
Substantial OpenAI GPT-6 Astra and Codex assistance.
PR97 physical bit words: Zhihao Chen, based on Swapnil Jain's witness.
Semantic/bulk assembly: PR23 (Zhihao Chen) and RaD; see SOURCES.json.
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
from copied_centers_network import grid_upper
from partial_swap_network import moment
from partial_gauge_bit import reconstruct
from structured_bulk_assembly import assembly, halving, js

ROOT = Path(__file__).resolve().parents[1]
COARSE = Q(15513, 125000000)
ATOM = Q(1, 1000)
OLD = Q(384599, 10**10)
AB = (1-ATOM)*COARSE+ATOM*OLD
AC = Q(92651, 10**9)
PHASE_STOP = Q(1, 10**6)
ASSEMBLY_BIT = min(AB, (1-PHASE_STOP)*AC-Q(1, 10**10))
KAPPA = Q(7237, 78125000)


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
        require(0 < t < p['m'] and n > 0, 'Shrinking positive bit children')
        logs[t] = log_upper(Q(p['m'],t))
        u = COARSE*logs[t]
        require(0 < u < 3, 'Coarse exponential enclosure')
        total += n*t*grid_upper(1+u+u*u/(2*(1-u/3)))
    upper = total/(p['W']*p['m'])
    mass = Q(p['total_rank'],p['W']*p['m'])
    require(mass < 1 and upper < 1, 'Both stopped-recurrence moments')
    require(0 < OLD <= COARSE < ATOM < 1 and ATOM > AB, 'Stopped-adapter exponents')
    return dict(saving=COARSE, exponent=1-COARSE, moment_upper=upper,
        strict_gap=1-upper, rank_moment=mass, logarithm_upper_bounds=logs,
        rounding_denominator=1 << 100,
        stopped_adapter=dict(atom_exponent=ATOM, base_ordinary_saving=OLD,
            effective_saving=AB, coarse_toll_exponent=1-ATOM,
            coarse_toll_subordinate_gap=ATOM-COARSE))


def complex_profile(row):
    h, v, R, ell = (row[k] for k in ('h','v','R','loss'))
    require((h,v,ell) == (24,comb(24,3),24*23), 'Complex dimensions')
    require(R == row['c']+row['q']-row['matched'], 'Compatible role count')
    selected = {int(r):n for r,n in row['selected_rank_histogram'].items()}
    require(sum(selected.values()) == row['selected_roles'] == 6341, 'Selected partial gauges')
    require(row['copied_centers_already'], 'Copied-center convention')
    require(sum(row['partial_first_transition_histogram'].values()) == sum(selected.values()), 'Charged first residuals')
    m, N, W = h*h, v*v, 2*v*v+2*v*R
    C = Counter({m-h:2*v*(R-sum(selected.values())), (h-1)**2:2*N, 1:N})
    for r,n in selected.items():
        require(0 < r < h and n > 0, 'Nonzero shrinking exterior gauges')
        C[m-h+r] += 2*v*n
    for name in ('source_data_histogram','target_data_histogram'):
        for r,n in row[name].items():
            C[int(r)] += 2*v*n
    for r,n in enumerate(row['remaining_internal_histogram']):
        if r:
            C[r] += 2*v*n
    C = dict(sorted((r,n) for r,n in C.items() if n))
    require(all(0 < r < m and n > 0 for r,n in C.items()), 'Shrinking complex children')
    s = sum(r*n for r,n in C.items())
    require(s == W*m-N+2*v*ell, 'Complete complex rank mass')
    return dict(dimensions=[h,h],m=m,N=N,W=W,L=2*v*ell,total_rank=s,
        deficit=W*m-s,maxchild=max(C),child_multiplicities=C)


def finite_bridge(bit, phase, row, previous):
    m,W,s,N = (phase[k] for k in ('m','W','total_rank','N'))
    h,v,R = (row[k] for k in ('h','v','R'))
    local = 4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    local += 8*R*v*(row['total_M_operations']+16)
    G = N+2*v*local
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B, r = s+E, phase['maxchild']
    C0 = 32*m*B*B
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0, 'Semantic induction and charge')
    dc,dp = halving(bit['m'],bit['maxchild']),halving(m,r)
    wc,wp = bit['W'].bit_length(),W.bit_length()
    old_bit = previous['finite_bridge']['bit']
    old = old_bit['halving_degree']*old_bit['wire_bits']
    require(old == 252, 'Inherited ordinary leaf row stock')
    coeff,degree = wc*dc+old+wp*dp,40000
    require(Q(degree) > Q(coeff*51,25), 'Sufficient product row stock')
    return dict(bit_coarse=dict(m=bit['m'],W=bit['W'],maxchild=bit['maxchild'],
            halving_degree=dc,wire_bits=wc),ordinary_leaf_row_degree=old,
        complex=dict(m=m,W=W,s=s,maxchild=r,halving_degree=dp,wire_bits=wp,
            scalar_group_upper=G,local_group_upper=local,coefficient_bound=h+4,
            coefficient_denominator_divides=2*(h-3)),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,
            B=B,C0=C0,C1=1,induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=h-3,
            exact_grid='One common dyadic grid times the fixed odd divisor to K=G*(D_complex+1); no child rounding'),
        rows=dict(coefficient=coeff,degree=degree,suffix_slope=4*degree,
            degree_gap=Q(degree)-Q(coeff*51,25),
            contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse'))


def certificate():
    require(not sys.flags.optimize, 'Run without -O')
    def read(name):
        return json.loads((ROOT/'certificates'/name).read_text())
    raw = reconstruct()
    row = read('partial-gauge-complex-input.json')
    expected = read('partial-gauge-input.json')
    previous = read('copied-centers-network.json')
    require(Q(previous['bit']['saving']) == OLD, 'Inherited leaf saving')
    C = {int(r):n for r,n in raw['whole_projector_histogram'].items()}
    bit = dict(dimensions=raw['dimensions'],m=raw['m'],W=raw['W'],N=raw['N'],
        total_rank=raw['rank_mass'],deficit=raw['deficit'],maxchild=max(C),child_multiplicities=C)
    require(sum(r*n for r,n in C.items()) == bit['total_rank'], 'Bit rank mass')
    require(bit['W']*bit['m']-bit['total_rank'] == bit['deficit'], 'Bit deficit')
    phase = complex_profile(row)
    bm = coarse_moment(bit)
    cm = moment(phase['m'],phase['W'],phase['child_multiplicities'],AC,True)
    require(bm['strict_gap'] == Q(expected['bit_moment_gap']), 'Saved coarse moment')
    require(cm['strict_gap'] == Q(expected['complex_moment_gap']), 'Saved complex moment')
    require(js(phase['child_multiplicities']) == expected['complex_children'], 'Saved complex children')
    bridge = finite_bridge(bit,phase,row,previous)
    assembled = assembly(ASSEMBLY_BIT,AC,bridge,KAPPA,beta=PHASE_STOP)
    assembled['parameters']['actual_bit_saving'] = AB
    require(ASSEMBLY_BIT <= AB, 'Supported assembly movement saving')
    require(js(bridge) == expected['finite_bridge'], 'Saved finite bridge')
    require(js(assembled) == expected['assembly'], 'Saved exact assembly')
    require(len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7, 'Complete strict constraints')
    sources = sorted(p for p in (ROOT/'certificates').glob('partial-gauge-*.json')
                     if p.name != 'partial-gauge-network.json')
    sources += sorted((ROOT/'scripts').glob('partial_gauge*.py'))
    sources += sorted(p for p in (ROOT/'scripts/partial_gauge').rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts)
    sources += sorted((ROOT/'notes').glob('partial-gauge-*.tex'))
    sources += sorted(p for p in (ROOT/'references/partial-gauge').rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts)
    sources += [ROOT/p for p in ('scripts/copied_centers_network.py',
        'scripts/partial_swap_network.py','scripts/structured_bulk_assembly.py',
        'certificates/copied-centers-network.json','certificates/stopped-product-network.json',
        'scripts/paired_triple_circuit.py','scripts/paired_exclusion_circuit.py')]
    return dict(status='Conditional partial-gauge multiplication witness',kappa=KAPPA,
        bit=dict(counts=bit,**bm),complex=dict(counts=phase,**cm),
        finite_bridge=bridge,assembly=assembled,
        predecessor_commit='948ce1510df750f4c18b96bdaef436a86f8bf834',
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Exact moments, stopped bit saving and semantic assembly. Finite producer/frame checks '
              'are separate; common-basis, fixed-tape and analytic transfer remain written proof dependencies.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'certificates/partial-gauge-network.json')
    args = parser.parse_args()
    args.output.write_text(json.dumps(js(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS kappa=7237/78125000 = 9.26336e-5; both moments, stopped saving, p^40000 stock, 47 strict constraints')


if __name__ == '__main__':
    main()
