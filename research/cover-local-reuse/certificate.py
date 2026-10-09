#!/usr/bin/env python3
"""Exact composition of the PR129 physical local word with PR130's cover.

PR130 Cayley cover and weighted bit interface: icekylinx, with OpenAI
GPT-6 Astra/Codex assistance. Local frames/reuse integration for eumemic
with OpenAI Codex assistance; PR117, PR124 and all source notices retained.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LOCAL=ROOT/'research/cyclic-deferred'
sys.path.insert(0,str(ROOT/'scripts'))
import three_stage_cover_network as inherited
from partial_swap_network import moment
from structured_bulk_assembly import assembly,js
KGRID=10**15
BGRID=10**12
STOP=Q(1,10**6)


def load(name):return json.loads((LOCAL/name).read_text())
def digest(path):return sha256(path.read_bytes()).hexdigest()


def cover_profile():
    local=load('complex-profile.json');audit=load('reflection-audit.json')
    h,v,R=(local[k]for k in('h','v','R'))
    assert (h,v,R)==(24,2024,26597)
    assert local['virtual_R']==28705 and local['reused_roles']==2108
    assert audit['R']==R and audit['virtual_R']==local['virtual_R']
    assert audit['child_multiplicities']==local['child_multiplicities']
    assert audit['physical_auxiliary_source_frames']==local['physical_auxiliary_source_frames']
    for key in ('exact_arbitrary_dirty_cancellation_by_dependency_cut','physical_aliased_numeric_replay','exact_birth_cut_invariants','literal_frame_incidences_both_directions','reflected_residual_rank_histogram_equal','completed_core_source_inventory_bound','completed_core_pre_exterior_frames_full','reflected_core_active_frames_complement_source','bounded_chunk_coefficients'):
        assert audit[key]is True,key
    assert audit['source_sha256']==digest(LOCAL/'complex_deferred.py')
    assert audit['audit_sha256']==digest(LOCAL/'reflection_audit.py')
    inventory=local['physical_auxiliary_source_frames']
    assert sum(row['count']for row in inventory)==R
    N=v*v
    remaining=Counter({int(r):n for r,n in local['child_multiplicities'].items()})
    # Remove exactly the two-stage data bridges, endpoint copies and exterior
    # class. All physical source/target moves and copied centers stay local.
    removed=Counter({(h-1)**2:2*N,1:N})
    for row in inventory:
        removed[h*h-h+len(row['basis'])]+=2*v*row['count']
    remaining.subtract(removed)
    assert all(type(n)is int and n>=0 and n%(2*v)==0 for n in remaining.values())
    H={r:n//(2*v)for r,n in remaining.items()if n}
    assert all(0<r<h for r in H)
    m=3*h-2;w=2*v+3*R;ell=h*(h-1)
    children=Counter({r:3*n for r,n in H.items()})
    exteriors=Counter()
    for row in inventory:
        exteriors[m-h+len(row['basis'])]+=3*row['count']
    children.update(exteriors)
    rank=sum(r*n for r,n in children.items())
    assert w*m-rank==2*v-3*ell==2392
    assert max(children)==68 and all(0<r<m and n>0 for r,n in children.items())
    return dict(h=h,v=v,R=R,virtual_R=local['virtual_R'],reused_roles=local['reused_roles'],
        m=m,roles_per_vertex=w,rank_per_vertex=rank,deficit_per_vertex=w*m-rank,
        maxchild=max(children),center_loss_per_invocation=ell,
        local_child_multiplicities=dict(sorted(H.items())),
        removed_two_stage_child_multiplicities=dict(sorted(removed.items())),
        exterior_child_multiplicities=dict(sorted(exteriors.items())),
        child_multiplicities=dict(sorted(children.items())),
        local_profile_sha256=digest(LOCAL/'complex-profile.json'),
        reflection_receipt_sha256=digest(LOCAL/'reflection-audit.json'))


def exact():
    p=cover_profile();m,w=p['m'],p['roles_per_vertex'];children=p['child_multiplicities']
    def contracts(n):
        try:moment(m,w,children,Q(n,BGRID),True)
        except ValueError:return False
        return True
    lo,hi=0,10**9
    assert contracts(lo)and not contracts(hi)
    while hi-lo>1:
        mid=(lo+hi)//2
        if contracts(mid):lo=mid
        else:hi=mid
    b=Q(lo,BGRID);cm=moment(m,w,children,b,True)
    n=m//2
    vertices=2**(m-1+(n-1)**2)*prod(2**(2*i)-1 for i in range(1,n))
    phase=dict(m=m,N=vertices*p['v'],W=vertices*w,total_rank=vertices*p['rank_per_vertex'],
        deficit=vertices*p['deficit_per_vertex'],vertices_per_stage=vertices,maxchild=p['maxchild'],
        group_order_bits=vertices.bit_length(),per_vertex=p,**cm)
    # Use virtual roles in the source-witness scalar reserve: compensated
    # recipients still have readouts even though they have no persistent bank.
    row=json.loads((ROOT/'certificates/three-stage-cover-complex-input.json').read_text())
    assert row['R']==p['virtual_R']and row['total_M_operations']==118451
    bridge=inherited.finite_bridge(phase,row)
    audit=load('reflection-audit.json')
    assert bridge['complex']['local_group_upper']>=audit['conservative_local_G']>=audit['expanded_scalar_operations_per_stage']
    bridge['complex'].update(physical_R=p['R'],virtual_R=p['virtual_R'],
        independently_audited_local_scalar_operations=audit['expanded_scalar_operations_per_stage'],
        local_scalar_guard_from_reflection=audit['conservative_local_G'],
        scalar_contract='Virtual-role reserve covers all compensated readouts and inverse chronology; actual persistent stock and finite routers use physical roles.')
    bit=inherited.bit_certificate(json.loads((ROOT/'certificates/three-stage-cover-bit-input.json').read_text()))
    a=min(inherited.AB,(1-STOP)*b-Q(1,10**14))
    def accepts(n):
        try:assembly(a,b,bridge,Q(n,KGRID),beta=STOP)
        except AssertionError:return False
        return True
    low,high=0,int(b*KGRID)+1
    assert accepts(low)and not accepts(high)
    while high-low>1:
        mid=(low+high)//2
        if accepts(mid):low=mid
        else:high=mid
    k=Q(low,KGRID);result=assembly(a,b,bridge,k,beta=STOP)
    assert len(result['strict_constraints'])==47 and len(result['margins'])==7
    return dict(status='Conditional PR130 cover with independently audited physical local frames and compensated reuse',
        kappa=k,complex_saving=b,assembly_bit_saving=a,actual_bit_saving=inherited.AB,
        profile=p,complex=phase,bit=bit,finite_bridge=bridge,assembly=result,
        next_grid_rejections=dict(complex='1e-12 enclosure',kappa='1e-15 assembly'),
        scope='Finite local word and complete cover/assembly arithmetic. PR130 group geometry, weighted local-ring compilation, uniform batching and borrowed rows remain explicit written proof dependencies, together with inherited analytic/tape interfaces.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=js(exact());path=HERE/'certificate.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==json.loads(path.read_text()),'Frozen cover certificate mismatch'
    print('PASS kappa',result['kappa'],float(Q(result['kappa'])),'complex',result['complex_saving'],'47 constraints,7 margins',flush=True)
if __name__=='__main__':main()
