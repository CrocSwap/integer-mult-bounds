#!/usr/bin/env python3
"""Exact three-stage cover moments and retained semantic/bulk assembly.

Copyright 2026 icekylinx. Apache-2.0.
Construction supplied with OpenAI GPT-6 Astra assistance; integration with
Codex assistance. PR117 local DAG: eumemic; PR97 bit word: Zhihao Chen
and Swapnil Jain. Semantic/bulk interfaces: PR23 and RaD. See NOTICE.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, prod
from pathlib import Path
import json
import sys

from certify import require
from partial_gauge_bit import reconstruct
from partial_swap_network import moment
from structured_bulk_assembly import assembly, halving, js

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[1]
COARSE = Q(747,2000000)
ATOM = Q(1,1000)
OLD = Q(384599,10**10)
AB = (1-ATOM)*COARSE+ATOM*OLD
AC = Q(786999,2500000000)
BAD = Q(1,10**16)
PHASE_STOP = Q(1,10**6)
ASSEMBLY_BIT = min(AB,(1-PHASE_STOP)*AC-Q(1,10**10))
KAPPA = Q(3146011,10**10)
GRID = 1 << 120


def up(x):
    return Q((x.numerator*GRID+x.denominator-1)//x.denominator,GRID)


def log_upper(x):
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    def small(y):
        z = (y-1)/(y+1)
        return 2*sum((z**(2*j+1)/(2*j+1) for j in range(32)),Q(0)) + 2*z**65/(65*(1-z*z))
    return up(power*small(Q(2))+small(x))


def exp_upper(u):
    require(0 <= u < 3,'Exponential enclosure')
    return up(1+u+u*u/(2*(1-u/3)))


def bit_certificate(row):
    physical = reconstruct()
    h,v,R = (row[k] for k in ('h','v','R'))
    require((h,v,R) == (23,comb(23,3),28866),'Bit local dimensions')
    for key in ('v','R','local_rank_histograms','exit_nullity_histogram'):
        require(row[key] == physical[key],'Inherited physical bit ledger: '+key)
    ell = row['center_loss']
    require(ell == h*(h-1),'Copied-center loss')
    m,W,H = 3*h-2,2*v+3*R,Counter()
    for part in row['local_rank_histograms'].values():
        for r,n in part.items():
            H[int(r)] += 3*n
    for nullity,n in row['exit_nullity_histogram'].items():
        H[m-int(nullity)] += 3*n
    require(all(0 < r < m and n > 0 for r,n in H.items()),'Proper bit children')
    mass = sum(r*n for r,n in H.items())
    require(W*m-mass == 2*v-3*ell,'Three-stage bit telescoping')
    logs = {r:log_upper(Q(m,r)) for r in H}
    good = sum(Q(r*n,W*m)*exp_upper(COARSE*logs[r]) for r,n in H.items())
    fallback,edges = 32*m*m,sum(H.values())
    extra = BAD*Q(fallback*edges,W*m)*exp_upper(COARSE*log_upper(Q(m)))
    rank_upper = Q(mass)+BAD*fallback*edges
    require(good+extra < 1 and rank_upper < W*m,'Both contaminated moments')
    require(Q(2*m**3,2**80) < BAD,'Fixed-prime bad-class fraction')
    require(ATOM > AB and ATOM < 1-AB,'Subordinate adapter and row-borrowing tolls')
    return dict(m=m,local_dimension=h,roles_per_vertex=W,
        ideal_rank_mass_per_vertex=mass,ideal_deficit=2*v-3*ell,
        ideal_child_multiplicities=dict(sorted(H.items())),maxchild=max(H),
        coarse_saving=COARSE,effective_saving=AB,atom_exponent=ATOM,
        ordinary_leaf_saving=OLD,bad_fraction=BAD,
        fallback_children_per_edge=fallback,edge_count_per_vertex=edges,
        good_moment_upper=good,added_bad_moment_upper=extra,
        strict_gap=1-good-extra,rank_mass_upper_per_vertex=rank_upper,
        log_upper_bounds=logs,rounding_denominator=GRID,
        row_stock='O(w log e) internally borrowed radix-q digits, restored at the outer boundary',
        prime_choice='Fixed odd q > 2^80 avoiding the finite rational denominator and rank-witness primes')


def complex_certificate(row):
    h,v,R,ell = (row[k] for k in ('h','v','R','loss'))
    require((h,v,R,ell) == (24,comb(24,3),28705,552),'Complex local dimensions')
    require(R == row['c']+row['q']-row['matched'],'Compatible roles')
    selected = {int(r):n for r,n in row['selected_rank_histogram'].items()}
    require(sum(selected.values()) == row['selected_roles'] == 4599,'Partial gauges')
    m,w,C = 3*h-2,2*v+3*R,Counter()
    C[m-h] += 3*(R-sum(selected.values()))
    for r,n in selected.items():
        C[m-h+r] += 3*n
    for key in ('source_data_histogram','target_data_histogram'):
        for r,n in row[key].items():
            C[int(r)] += 3*n
    for r,n in enumerate(row['remaining_internal_histogram']):
        if r:
            C[r] += 3*n
    C = dict(sorted((r,n) for r,n in C.items() if r and n))
    require(all(0 < r < m and n > 0 for r,n in C.items()),'Proper complex children')
    rank = sum(r*n for r,n in C.items())
    require(w*m-rank == 2*v-3*ell,'Three-stage complex telescoping')
    n = m//2
    vertices = 2**(m-1+(n-1)**2)*prod(2**(2*i)-1 for i in range(1,n))
    exact = moment(m,w,C,AC,True)
    return dict(m=m,N=vertices*v,W=vertices*w,total_rank=vertices*rank,
        deficit=vertices*(w*m-rank),vertices_per_stage=vertices,maxchild=max(C),
        group_order_bits=vertices.bit_length(),per_vertex=dict(W=w,rank=rank,
            deficit=w*m-rank,child_multiplicities=C),**exact)


def finite_bridge(c,row):
    m,W,s,N,V = (c[k] for k in ('m','W','total_rank','N','vertices_per_stage'))
    h,v,R = (row[k] for k in ('h','v','R'))
    local = 4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    local += 8*R*v*(row['total_M_operations']+16)
    router = 64*(m+1)**3*W**2
    G = N+3*V*local+router
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B,C0,r = s+E,32*m*(s+E)**2,c['maxchild']
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0,'Finite semantic charge')
    dp,wp = halving(m,r),W.bit_length()
    old_coarse,old_atom = 9909,252
    coefficient,degree = dp*wp+old_coarse+old_atom,160000
    require(Q(degree) > Q(51*coefficient,25),'External product row reserve')
    return dict(bit_uniform=dict(coarse_saving=COARSE,atom_beta=ATOM,
            old_atom_saving=OLD,ordinary_saving=AB,
            selector_stock='O(w log e) internal borrowed rows; restored by the uniform old-supplier wrapper',
            external_stock='No q-adic group-size factor is inserted into the external polynomial row stock'),
        conservative_old_coarse_row_reserve=old_coarse,ordinary_leaf_row_degree=old_atom,
        complex=dict(m=m,W=W,s=s,N=N,maxchild=r,invocations_per_stage=V,stages=3,
            halving_degree=dp,wire_bits=wp,scalar_group_upper=G,local_group_upper=local,
            finite_group_router_upper=router,coefficient_bound=h+4,
            coefficient_denominator_divides=2*(h-3)),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,
            B=B,C0=C0,C1=1,induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=h-3,
            exact_grid='One common dyadic grid times 21^(-K), K=G*(D_complex+1); no child rounding'),
        rows=dict(coefficient=coefficient,complex_coefficient=dp*wp,degree=degree,
            suffix_slope=4*degree,degree_gap=Q(degree)-Q(51*coefficient,25),
            contract='Finite complex group role stock plus conservative fixed legacy bit reserves; q-adic selectors borrowed internally and restored; one prefix and one padding; sequential reuse'))


def certificate():
    require(not sys.flags.optimize,'Run without -O')
    def read(name):
        return json.loads((ROOT/'certificates'/name).read_text())
    expected = read('three-stage-cover-input.json')
    bit = bit_certificate(read('three-stage-cover-bit-input.json'))
    row = read('three-stage-cover-complex-input.json')
    phase = complex_certificate(row)
    bridge = finite_bridge(phase,row)
    previous = read('copied-centers-network.json')
    require(Q(previous['bit']['saving']) == OLD,'Retained ordinary leaf')
    result = assembly(ASSEMBLY_BIT,AC,bridge,KAPPA,beta=PHASE_STOP)
    result['parameters']['actual_bit_saving'] = AB
    require(ASSEMBLY_BIT <= AB,'Supported assembly bit saving')
    for actual,key in ((bit['strict_gap'],'bit_moment_gap'),(phase['strict_gap'],'complex_moment_gap'),
                       (result['minimum_margin'],'assembly_minimum'),(result['absorption_gap'],'absorption_gap')):
        require(actual == Q(expected[key]),'Saved exact '+key)
    require(js(bit['ideal_child_multiplicities']) == expected['bit_child_multiplicities'],'Saved bit children')
    require(js(phase['per_vertex']['child_multiplicities']) == expected['complex_child_multiplicities'],'Saved complex children')
    require(phase['vertices_per_stage'] == expected['complex_group_order'],'Finite group order')
    require(bridge['rows']['degree'] == expected['row_degree'] and bridge['rows']['coefficient'] == expected['row_coefficient'],'Saved row bound')
    require(KAPPA == Q(expected['kappa']) and len(result['strict_constraints']) == 47 and len(result['margins']) == 7,'Complete assembly')
    sources = sorted(p for p in (ROOT/'certificates').glob('three-stage-cover-*.json')
                     if p.name != 'three-stage-cover-network.json')
    sources += sorted((ROOT/'scripts').glob('three_stage_cover*.py'))
    sources += sorted(p for folder in ('scripts/three_stage_cover','references/three-stage-cover')
                      for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    sources += sorted((ROOT/'notes').glob('three-stage-cover-*.tex'))+[ROOT/'notes/general-clifford-frames.tex']
    sources += [ROOT/p for p in ('scripts/partial_gauge_bit.py','certificates/partial-gauge-bit-input.json',
        'references/partial-gauge/pr97/SOURCE.json','scripts/partial_swap_network.py',
        'scripts/structured_bulk_assembly.py','certificates/copied-centers-network.json',
        'certificates/stopped-product-network.json','certificates/partial-gauge-network.json',
        'scripts/partial_gauge/binary.py','scripts/partial_gauge/lift.py','scripts/partial_gauge/word.py',
        'scripts/partial_gauge/match.cpp')]
    return dict(status='Conditional three-stage cover multiplication witness',kappa=KAPPA,
        bit=bit,complex=phase,finite_bridge=bridge,assembly=result,
        predecessor_commit='cf60442983c153a3a0f5272ea4713f99eba13c86',
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Exact local inventories, strict moments, contaminated fallback charge and semantic assembly. '
              'Local finite reconstruction is checked separately; group geometry, uniform weighted routing, '
              'borrowed rows and inherited analytic/tape contracts are written proof dependencies.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'certificates/three-stage-cover-network.json')
    args = p.parse_args()
    args.output.write_text(json.dumps(js(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS kappa=3146011/10000000000 = 3.146011e-4; both moments, rare-class fallback, finite router, 47 strict constraints')


if __name__ == '__main__':
    main()
