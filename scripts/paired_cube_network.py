#!/usr/bin/env python3
"""Exact paired-cube suppliers and shared-core semantic assembly.

Copyright 2026 icekylinx. Apache-2.0.
Developed with substantial OpenAI GPT-6 Astra assistance; integrated with
Codex assistance. Sharing principle: an664 PR128; local words: eumemic
PR117 and Zhihao Chen/Swapnil Jain PR97. Global-optimal bit gauge subset
via exact telescoping interval-min-cut: Prepared by Thomas Marchand with
Google Antigravity assistance. See NOTICE and SOURCES.json.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import prod
from pathlib import Path
import json
import sys

from certify import require
from paired_cube_bit import reconstruct
from three_stage_cover_network import log_upper, exp_upper
from structured_bulk_assembly import assembly, halving, js

if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[1]
AC = Q(4856569,10**10)
COARSE = Q(461877426979,10**15)
ATOM = Q(1,1000)
OLD = Q(384599,10**10)
AB = (1-ATOM)*COARSE+ATOM*OLD
BAD = Q(1,10**16)
PHASE_STOP = Q(1,10**6)
ASSEMBLY_BIT = min(AB,(1-PHASE_STOP)*AC-Q(1,10**10))
KAPPA = Q(461028508707,10**15)


def clean(hist):
    return dict(sorted((int(r),n) for r,n in hist.items() if int(r) and n))


def shared_profile(row,complex_word):
    h,v,R,ell = (row[k] for k in ('h','v','R','loss'))
    m,W,H = 3*h,2*v+R,Counter()
    selected = {int(r):n for r,n in row['selected_rank_histogram'].items()}
    require(sum(selected.values()) == row['selected_roles'],'Selected gauge count')
    for r,n in selected.items():
        require(0 < r < h and n > 0,'Proper local gauges')
        H[3*r] += n
    if complex_word:
        require((h,v,R,ell) == (24,1760,26417,528),'Paired-cube local dimensions')
        require(R == row['c']+row['q']-row['matched'],'Compatible carrier roles')
        require(selected == {20:4840},'Selected rank20 gauges')
        for r,n in enumerate(row['remaining_internal_histogram']):
            H[r] += 3*n
        parts = ('source_data_histogram','target_data_histogram')
    else:
        require((h,v,R,ell) == (23,1771,28866,506),'Retained bit local dimensions')
        parts = ('auxiliary_histogram','source_data_histogram','target_data_histogram','copied_center_histogram')
    for name in parts:
        for r,n in row[name].items():
            H[int(r)] += 3*n
    H[2] += 2*v
    H = clean(H)
    require(all(0 < r < m and n > 0 for r,n in H.items()),'Proper shared-core children')
    mass = sum(r*n for r,n in H.items())
    require(H == clean(row['child_histogram']),'Saved complete child histogram')
    require((m,W,mass,W*m-mass) == (row['m'],row['W_per_vertex'],row['rank_per_vertex'],row['deficit_per_vertex']),
            'Saved sharing dimensions and rank')
    require(W*m-mass == 2*v-3*ell,'Shared-core telescoping deficit')
    return dict(m=m,local_dimension=h,W_per_vertex=W,rank_per_vertex=mass,
        deficit_per_vertex=W*m-mass,child_multiplicities=H,maxchild=max(H),edge_count=sum(H.values()))


def exact_moment(p,saving):
    m,W = p['m'],p['W_per_vertex']
    logs = {r:log_upper(Q(m,r)) for r in p['child_multiplicities']}
    upper = sum(Q(n*r,W*m)*exp_upper(saving*logs[r]) for r,n in p['child_multiplicities'].items())
    require(upper < 1,'Strict ideal characteristic')
    return dict(saving=saving,exponent=1-saving,moment_upper=upper,strict_gap=1-upper,
        log_upper_bounds=logs,rounding_denominator=1 << 120)


def bit_certificate(row):
    p = shared_profile(row,False)
    exact = exact_moment(p,COARSE)
    m,W = p['m'],p['W_per_vertex']
    fallback = 32*m*m
    added = BAD*Q(fallback*p['edge_count'],W*m)*exp_upper(COARSE*log_upper(Q(m)))
    rank_upper = Q(p['rank_per_vertex'])+BAD*fallback*p['edge_count']
    require(1-exact['moment_upper']-added > 0 and rank_upper < W*m,'Both contaminated moments')
    require(Q(2*m**3,2**80) < BAD,'Fixed prime bad-class allowance')
    require(ATOM > AB and ATOM < 1-AB,'Subordinate adapter and row tolls')
    return dict(counts=p,coarse=exact,coarse_saving=COARSE,effective_saving=AB,
        atom_exponent=ATOM,ordinary_leaf_saving=OLD,bad_fraction=BAD,
        fallback_children_per_edge=fallback,added_bad_moment_upper=added,
        strict_gap=1-exact['moment_upper']-added,rank_mass_upper_per_vertex=rank_upper,
        row_stock='O(w log e) internally borrowed radix-q digits; retained stopped wrapper restores them')


def complex_certificate(row):
    p = shared_profile(row,True)
    exact = exact_moment(p,AC)
    m = p['m']
    n = m//2
    vertices = 2**(m-1+(n-1)**2)*prod(2**(2*i)-1 for i in range(1,n))
    return dict(counts=p,**exact,vertices_per_stage=vertices,N=vertices*row['v'],
        W=vertices*p['W_per_vertex'],total_rank=vertices*p['rank_per_vertex'],
        deficit=vertices*p['deficit_per_vertex'],group_order_bits=vertices.bit_length())


def finite_bridge(c,b,row):
    m,W,s,N,V = c['counts']['m'],c['W'],c['total_rank'],c['N'],c['vertices_per_stage']
    h,v,R = (row[k] for k in ('h','v','R'))
    original_X = 32*v
    local = 4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    local += 8*R*v*(row['total_M_operations']+16)+original_X
    logical = 3*V*local+8*W+4*N+8*m*R*V
    G = 64*(m+1)**3*(logical+1)*(W+1)**2
    E = 64*(W+m+G+1)**3
    charge = 2*G*W*W+8*s+4*W+4+32*m
    B,C0,r = s+E,32*m*(s+E)**2,c['counts']['maxchild']
    require(charge < E and 2*B*(m-r) >= s+E and 2*B+18 < C0,'Finite semantic guard')
    dc,wc = halving(m,r),W.bit_length()
    old_coarse,old_atom = 9909,252
    coefficient,degree = dc*wc+old_coarse+old_atom,70000
    require(Q(degree) > Q(51*coefficient,25),'External row reserve')
    return dict(bit_uniform=dict(coarse_saving=COARSE,atom_beta=ATOM,old_atom_saving=OLD,
            ordinary_saving=AB,selector_stock='O(w log e) internal borrowed rows; retained stopped wrapper restores them',
            external_stock='The q-adic group-size factor is not inserted into external polynomial row stock'),
        conservative_old_coarse_row_reserve=old_coarse,ordinary_leaf_row_degree=old_atom,
        complex=dict(m=m,W=W,s=s,N=N,maxchild=r,invocations_per_stage=V,stages=3,
            auxiliary_banks_after_sharing=1,halving_degree=dc,wire_bits=wc,
            original_X_involution_scalar_group_upper=original_X,local_group_upper=local,
            logical_group_upper=logical,finite_group_router_upper=G,scalar_group_upper=G,
            routing_charge='64*(m+1)^3*(K+1)*(W+1)^2; one full W-role permutation per logical group overcharged',
            coefficient_bound=h+4,coefficient_denominator_divides=6),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,
            induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=3,
            exact_grid='One common dyadic grid times 3^(-K), K=G*(D_complex+1); no child rounding'),
        rows=dict(coefficient=coefficient,complex_coefficient=dc*wc,degree=degree,
            suffix_slope=4*degree,degree_gap=Q(degree)-Q(51*coefficient,25),
            contract='Finite complex role stock plus unchanged conservative bit reserves; q-adic selectors internally borrowed and restored; one prefix and one padding; sequential reuse'))


def certificate():
    require(not sys.flags.optimize,'Run without -O')
    def read(name):
        return json.loads((ROOT/'certificates'/name).read_text())
    expected = read('paired-cube-input.json')
    bit_row = reconstruct()
    row = read('paired-cube-complex-input.json')
    bit,phase = bit_certificate(bit_row),complex_certificate(row)
    bridge = finite_bridge(phase,bit,row)
    require(Q(read('copied-centers-network.json')['bit']['saving']) == OLD,'Retained ordinary leaf')
    result = assembly(ASSEMBLY_BIT,AC,bridge,KAPPA,beta=PHASE_STOP)
    result['parameters']['actual_bit_saving'] = AB
    require(ASSEMBLY_BIT <= AB,'Supported bit interface')
    for actual,key in ((bit['strict_gap'],'bit_moment_gap'),(phase['strict_gap'],'complex_moment_gap'),
                       (result['minimum_margin'],'assembly_minimum'),(result['absorption_gap'],'absorption_gap')):
        require(actual == Q(expected[key]),'Saved exact '+key)
    require(js(bit['counts']['child_multiplicities']) == expected['bit_child_multiplicities'],'Saved bit children')
    require(js(phase['counts']['child_multiplicities']) == expected['complex_child_multiplicities'],'Saved complex children')
    require(phase['vertices_per_stage'] == expected['complex_group_order'],'Group order')
    require(bridge['rows']['degree'] == expected['row_degree'] and bridge['rows']['coefficient'] == expected['row_coefficient'],'Saved row stock')
    require(KAPPA == Q(expected['kappa']) and len(result['strict_constraints']) == 47 and len(result['margins']) == 7,'Complete assembly')
    atom_2000 = Q(1,2000)
    ab_2000 = (1-atom_2000)*COARSE+atom_2000*OLD
    kappa_2000 = Q(461239827139,10**15)
    require(atom_2000 > ab_2000 and atom_2000 < 1-ab_2000,'Tightened subordinate adapter and row tolls')
    result_2000 = assembly(ab_2000,AC,bridge,kappa_2000,beta=PHASE_STOP)
    require(len(result_2000['strict_constraints']) == 47 and len(result_2000['margins']) == 7,'Complete tightened assembly')
    sources = sorted(p for p in (ROOT/'certificates').glob('paired-cube-*.json')
                     if p.name != 'paired-cube-network.json')
    sources += sorted((ROOT/'scripts').glob('paired_cube*.py'))
    sources += sorted(p for folder in ('scripts/paired_cube','references/paired-cube')
                      for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    sources += sorted((ROOT/'notes').glob('paired-cube-*.tex'))
    sources += [ROOT/p for p in ('scripts/three_stage_cover_network.py','scripts/structured_bulk_assembly.py',
        'scripts/partial_gauge_bit.py','certificates/partial-gauge-bit-input.json',
        'references/partial-gauge/pr97/SOURCE.json','certificates/copied-centers-network.json',
        'certificates/three-stage-cover-network.json','notes/general-clifford-frames.tex')]
    return dict(status='Conditional paired-cube multiplication witness',kappa=KAPPA,
        kappa_atom_2000=kappa_2000,bit=bit,complex=phase,
        finite_bridge=bridge,assembly=result,
        tightened_atom_2000=dict(atom_exponent=atom_2000,effective_bit_saving=ab_2000,
            kappa=kappa_2000,minimum_margin=result_2000['minimum_margin'],
            absorption_gap=result_2000['absorption_gap']),
        predecessor_commit='6a9970a530119174507904e23592fd59ede19a5d',
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Exact inventories, supplier moments, full fallback/router charge and semantic assembly. '
              'Local scalar/frame verification is separate; paired source scheduling, completed-core sharing '
              'and inherited uniform-recursion/analytic/tape contracts are written proof dependencies.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'certificates/paired-cube-network.json')
    args = p.parse_args()
    args.output.write_text(json.dumps(js(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS kappa=461028508707/1000000000000000 = 4.61028508707e-4 (atom=1/2000: 461239827139/1000000000000000 = 4.61239827139e-4); both moments, shared cores, finite router and 47 strict constraints')


if __name__ == '__main__':
    main()
