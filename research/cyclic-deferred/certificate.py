#!/usr/bin/env python3
"""Exact finite assembly for cyclic strips with deferred readouts.

Built on Avi Eisenberg's PR110 (Anthropic Claude assistance), icekylinx's
PR104 stopped-product and copied-center interfaces, and Zhihao Chen's
assembly of the RaD interfaces. Integration for eumemic with OpenAI Codex
assistance. Apache-2.0. General transfer hypotheses remain inherited.
"""
import argparse
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from partial_swap_network import moment
from copied_centers_network import finite_bridge as copied_bridge
from structured_bulk_assembly import assembly, js
ATOM = Q(1, 1000)
OLD = Q(384599, 10**10)
BETA = Q(1, 10**6)
COARSE = Q(129310447, 10**12)
COMPLEX = Q(130696544, 10**12)
KGRID = 10**15

def profile(name):
    p = json.loads((HERE / name).read_text())
    p['child_multiplicities'] = {int(t): c for t, c in p['child_multiplicities'].items()}
    z = p['child_multiplicities']
    assert all(0 < t < p['m'] and c > 0 for t,c in z.items())
    assert sum(t*c for t,c in z.items()) == p['total_rank'] == p['W']*p['m']-p['N']+p['L']
    assert max(z) == p['maxchild']
    return p

def contracts(p, a):
    try: moment(p['m'],p['W'],p['child_multiplicities'],a,True)
    except ValueError: return False
    return True

def exact(bit=None, phase=None):
    bit = profile('shared-bit-profile.json') if bit is None else bit
    phase = profile('shared-complex-profile.json') if phase is None else phase
    assert (bit['h'], phase['h']) == (23,24)
    bm = moment(bit['m'],bit['W'],bit['child_multiplicities'],COARSE,True)
    cm = moment(phase['m'],phase['W'],phase['child_multiplicities'],COMPLEX,True)
    assert not contracts(bit,COARSE+Q(1,10**12))
    assert not contracts(phase,COMPLEX+Q(1,10**12))
    ab = (1-ATOM)*COARSE+ATOM*OLD
    assert 0 < OLD < COARSE < ATOM and ab < ATOM
    a = min(ab,(1-BETA)*COMPLEX-Q(1,10**14))
    row = dict(h=phase['h'],v=phase['v'],c=phase['additions'],central_disjoint=24)
    bridge = copied_bridge(bit,phase,[row,row])
    # Logical readouts are expanded into same-frame shears with |coefficient|<=1.
    # Exact numerators over42 are split into signed42 chunks and a remainder.
    # The independent audit counts every chunk and checks this guard covers it.
    # Each row has <=c+R mixer operations and <=R leaf copies. There are
    # <=R+q readouts, each containing <=h center coefficients and <=v direct
    # coefficients; <=4*v*(h+1) scalar groups suffice per readout. A factor
    # eight covers forward/inverse words, both reflected words, and copies.
    h,v,R,q,c = (phase[k] for k in ('h','v','R','roots','additions'))
    virtual_R = phase.get('virtual_R', R)
    local = 8*(c+2*virtual_R+(virtual_R+q)*v*(h+1)+h*h+h+1)
    core_G = phase['N'] + 2*v*local
    # Gaussian elimination uses at most m^2 elementary binary basis steps;
    # both adapters and the signed phase directions fit in this atom reserve.
    # Binary address atoms remain paid ordinary-bit adapter calls at the
    # inherited exponent, not constant-time tape instructions. Including
    # their number in G also conservatively enlarges the semantic guard.
    sharing_G = 64 * phase['m']**2 * (2 * phase['shared_groups'] * R)
    G = core_G + sharing_G
    m,W,s = (phase[k] for k in ('m','W','total_rank'))
    E=64*(W+m+G+1)**3
    charge=2*G*W*W+8*s+4*W+4+32*m
    B=s+E; C0=32*m*B*B
    assert charge<E and 2*B*(m-phase['maxchild']) >= s+E and 2*B+18<C0
    bridge['complex']['scalar_group_upper']=G
    bridge['complex']['core_scalar_group_upper']=core_G
    bridge['complex']['shared_basis_phase_group_upper']=sharing_G
    bridge['complex']['scalar_terms']=[dict(h=h,v=v,c=c,R=virtual_R,physical_R=R,q=q,invocations=v,
        local_group_upper=local,description='Expanded rational old readouts and forward/inverse/reflected words')]*2
    bridge['semantic'].update(E=E,literal_charge=charge,strict_literal_gap=E-charge,
        B=B,C0=C0,C1=1,induction_gap=2*B*(m-phase['maxchild'])-s-E,
        fixed_odd_divisor=21,exact_grid='2^(-P)*21^(-K), K=G*(D_complex+1); completed children preserve incoming odd denominator; no child rounding')
    coarse_bridge=bridge.pop('bit')
    coarse_bridge['completed_core_groups'] = bit['groups']
    coarse_bridge['paid_projector_adapter_calls'] = bit['paid_projector_calls']
    coarse_bridge['adapter_contract'] = 'Each complete projector and group complement retains paid ordered-affine atom adapters under one common rational basis; choose a fixed odd execution prime avoiding the enlarged finite bad-prime set. O(Vn) local work is absorbed by the stopped adapter gap.'
    previous=json.loads((ROOT/'certificates/copied-centers-network.json').read_text())
    oldbit=previous['finite_bridge']['bit']
    old_degree=oldbit['halving_degree']*oldbit['wire_bits']
    assert old_degree==252
    cp=bridge['complex']
    coeff=coarse_bridge['halving_degree']*coarse_bridge['wire_bits']+old_degree+cp['halving_degree']*cp['wire_bits']
    degree=1000*((51*coeff)//25000+1)
    bridge.update(bit_coarse=coarse_bridge,ordinary_leaf_row_degree=old_degree)
    bridge['rows']=dict(coefficient=coeff,degree=degree,suffix_slope=4*degree,
        degree_gap=Q(degree)-Q(51*coeff,25),contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; prefix and padding; sequential reuse')
    def accepts(k):
        try: assembly(a,COMPLEX,bridge,Q(k,KGRID),beta=BETA)
        except AssertionError: return False
        return True
    lo,hi=0,int(COMPLEX*KGRID)+1
    assert accepts(lo) and not accepts(hi)
    while hi-lo>1:
        mid=(lo+hi)//2
        if accepts(mid): lo=mid
        else: hi=mid
    k=Q(lo,KGRID)
    assembled=assembly(a,COMPLEX,bridge,k,beta=BETA)
    assert len(assembled['strict_constraints'])==47 and len(assembled['margins'])==7
    assert not accepts(lo+1)
    return dict(status='Finite conditional cyclic/deferred witness',kappa=k,
        complex_saving=COMPLEX,coarse_bit_saving=COARSE,actual_bit_saving=ab,
        bit_parameter=a,complex_profile=phase,bit_profile=bit,
        bit_moment_gap=bm['strict_gap'],complex_moment_gap=cm['strict_gap'],
        finite_bridge=bridge,assembly=assembled,
        next_grid_rejections=dict(bit='1e-12',complex='1e-12',kappa='1e-15'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    assert not sys.flags.optimize
    result=js(exact()); path=HERE/'certificate.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==json.loads(path.read_text()),'Frozen exact certificate mismatch'
    print('PASS conditional kappa = %s = %.12e; 47 constraints, 7 margins; expanded scalar charge' % (result['kappa'],float(Q(result['kappa']))))
if __name__=='__main__':main()
