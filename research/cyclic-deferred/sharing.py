#!/usr/bin/env python3
"""Completed-core sharing of independently audited physical frames.

Signed orthogonal outer partition and completed-core allocation: an664 PR128,
530588a019b4a74f09180680c9e3961bf649ec89, with OpenAI Codex assistance.
Partition construction: Xiande Zhang and Gennian Ge, JCD18 (2010),209-223.
Per-operation hull frames and this composition: eumemic with OpenAI Codex.
Inherited producer/compiler notices remain authoritative. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
PARTITION_PIN='9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'

def profile(local,partition,phase):
    h,v,R,m,N=(local[k] for k in ('h','v','R','m','N'))
    assert (h,v,R,m,N)==(24,2024,28705,576,4096576)
    assert local['deferred_roles']==0 and local['deferred_dims']=={}
    groups=Counter(map(len,partition['groups']))
    assert groups=={24:83,8:4}
    assert sorted(t for G in partition['groups']for t in G)==list(range(v))
    assert phase['partition_sha256']==PARTITION_PIN
    for key in ['all_triples_once','all_actual_Z4_phase_identities','all_complement_bases_explicit','all_tensor_scalar_phases_one','exact_inverse_direction_identity','exact_gaussian_composition','exact_stage2_gauge','wrong_source_sign_negative_control']:
        assert phase[key]
    z=Counter({int(t):n for t,n in local['child_multiplicities'].items()})
    assert z[m-h]==2*v*R
    del z[m-h]
    for g,n in groups.items():
        if g<h:z[m-h*g]+=2*R*n
    W=2*N+2*sum(groups.values())*R
    mass=sum(t*n for t,n in z.items())
    assert mass==W*m-N+local['L'] and all(0<t<m and n>0 for t,n in z.items())
    out=dict(local);out.update(W=W,total_rank=mass,maxchild=max(z),child_multiplicities=dict(sorted(z.items())),shared_groups=sum(groups.values()),group_sizes=dict(sorted(groups.items())),core_source_rank=0,core_sink_rank=h,unshared_W=local['W'],unshared_rank=local['total_rank'])
    return out

if __name__=='__main__':
    assert not __import__('sys').flags.optimize
    p=HERE/'inputs/shared-partition.json';assert sha256(p.read_bytes()).hexdigest()==PARTITION_PIN
    result=profile(json.loads((HERE/'complex-profile.json').read_text()),json.loads(p.read_text()),json.loads((HERE/'phase_check.json').read_text()))
    (HERE/'shared-complex-profile.json').write_text(json.dumps(result,indent=1)+'\n')
    print('PASS completed-core shared profile',result['W'],result['total_rank'],result['maxchild'])
