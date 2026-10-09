#!/usr/bin/env python3
"""Complete shared-core profile from the audited physical source-frame inventory.

Completed-core sharing and signed outer partition: an664 PR128, commit
530588a019b4a74f09180680c9e3961bf649ec89, with OpenAI Codex assistance.
Partition: Xiande Zhang and Gennian Ge, JCD 18 (2010), 209-223.
Generalized physical gauges and compensated reuse composition: eumemic with
OpenAI Codex assistance. Reuse follows jamesyc PR124; original notices remain.
Apache-2.0. This finite profile retains the stated inherited core interfaces.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json,sys
from gauge_phase import inventory_digest,validate_inventory
assert not sys.flags.optimize, 'Assertions must remain enabled'
HERE=Path(__file__).resolve().parent
PARTITION_PIN='9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'

def profile(local,partition,phase,gauge):
    h,v,R,m,N=(local[k]for k in ('h','v','R','m','N'))
    assert(h,v,R,m,N)==(24,2024,26597,576,4096576)
    assert local['virtual_R']==28705 and local['reused_roles']==2108
    inventory=local['physical_auxiliary_source_frames'];counts=validate_inventory(inventory,R,h)
    groups=Counter(map(len,partition['groups']))
    assert groups=={24:83,8:4}
    assert sorted(t for G in partition['groups']for t in G)==list(range(v))
    assert phase['partition_sha256']==gauge['partition_sha256']==PARTITION_PIN
    for key in ('all_triples_once','all_actual_Z4_phase_identities','all_complement_bases_explicit','all_tensor_scalar_phases_one','exact_inverse_direction_identity','exact_gaussian_composition','exact_stage2_gauge','wrong_source_sign_negative_control'):
        assert phase[key]is True, 'Signed outer partition phase contract: '+key
    for key in ('all_local_projectors_exact','all_source_frames_nondegenerate','all_grouped_complement_scalars_one','signed_stage_residuals_equal','exact_physical_source_inventory_bound','wrong_source_sign_rejected'):
        assert gauge[key]is True, 'Physical gauge phase contract: '+key
    assert gauge['R']==R and gauge['physical_auxiliary_source_frames']==inventory
    assert gauge['source_inventory_sha256']==inventory_digest(inventory)
    assert {int(g):n for g,n in gauge['group_sizes'].items()}==dict(groups)
    z=Counter({int(t):n for t,n in local['child_multiplicities'].items()})
    old=Counter();new=Counter()
    for F,n in counts.items():
        old[m-h+len(F)]+=2*v*n
        for g,k in groups.items():
            width=m-g*(h-len(F))
            assert 0<=width<m
            if width:new[width]+=2*k*n
    assert {r:n for r,n in z.items()if r>=m-h}==dict(old), 'Complete local auxiliary exterior inventory'
    assert sum(old.values())==2*v*R
    z.subtract(old);z.update(new);z=Counter({r:n for r,n in z.items()if n})
    assert dict(new)=={int(r):n for r,n in gauge['grouped_exterior_histogram'].items()}, 'Exact gauge complement profile'
    W=2*N+2*sum(groups.values())*R;mass=sum(r*n for r,n in z.items())
    assert all(0<r<m and type(n)is int and n>0 for r,n in z.items())
    assert mass==W*m-N+local['L'] and W*m-mass==local['deficit']
    out=dict(local);out.update(W=W,total_rank=mass,maxchild=max(z),child_multiplicities=dict(sorted(z.items())),
        shared_groups=sum(groups.values()),group_sizes=dict(sorted(groups.items())),
        old_exterior_histogram=dict(sorted(old.items())),grouped_exterior_histogram=dict(sorted(new.items())),
        core_source_inventory_sha256=inventory_digest(inventory),core_pre_exterior_inner_sink_rank=h,
        core_active_rank_formula='24-dim(physical source frame)',unshared_W=local['W'],unshared_rank=local['total_rank'])
    return out

def main():
    lp=HERE/'complex-profile.json';pp=HERE/'inputs/shared-partition.json';gp=HERE/'gauge-phase-audit.json';rp=HERE/'reflection-audit.json'
    assert sha256(pp.read_bytes()).hexdigest()==PARTITION_PIN
    gauge=json.loads(gp.read_text())
    assert gauge['local_profile_sha256']==sha256(lp.read_bytes()).hexdigest()
    assert gauge['reflection_receipt_sha256']==sha256(rp.read_bytes()).hexdigest()
    result=profile(json.loads(lp.read_text()),json.loads(pp.read_text()),json.loads((HERE/'phase_check.json').read_text()),gauge)
    (HERE/'shared-complex-profile.json').write_text(json.dumps(result,indent=1)+'\n')
    print('PASS shared physical-gauge profile',result['R'],result['W'],result['total_rank'],result['maxchild'])
if __name__=='__main__':main()
