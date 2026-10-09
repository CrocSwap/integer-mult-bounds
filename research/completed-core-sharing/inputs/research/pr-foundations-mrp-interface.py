"""Independently rebuild the complete PR117 signed-MRP87 child profile."""
from pathlib import Path
from collections import Counter
import hashlib,json
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=read(HERE/'pr117-public/tree/certificates/deferred-product-complex-input.json')
core_path=HERE/'round8-foundations-reuse117-interface.json';core=read(core_path)
ledger_path=HERE/'round8-foundations-reuse117-ledger.json'
assert core['physical_scalar_receipt_sha256']==sha(ledger_path)
assert core['producer_receipt_sha256']==sha(HERE/'round8-optimize-reuse117-producer.json')
assert (row['h'],row['v'],row['R'],row['loss'])==(24,2024,28705,552)
phase_path=HERE/'pr-foundations-mrp-phase.json';phase=read(phase_path)
partition=HERE/'pr-network-mrp24-signed.json'
assert phase['partition_sha256']==sha(partition)=='9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'
for key in ['all_triples_once','all_actual_Z4_phase_identities','all_complement_bases_explicit',
    'all_tensor_scalar_phases_one','exact_inverse_direction_identity','exact_gaussian_composition',
    'exact_stage2_gauge','wrong_source_sign_negative_control']:assert phase[key]
h=24;v=2024;R=28705;ell=552;m=h*h;N=v*v
H=row['histogram'][:]
assert sum(r*n for r,n in enumerate(H))==h*R+2*ell
assert H[h]==h;H[h]-=h;H[1]+=h
assert sum(r*n for r,n in enumerate(H))==h*R+ell
hist=Counter({r:2*v*n for r,n in enumerate(H) if r and n})
hist[(h-1)**2]+=2*N;hist[h-1]+=4*N;hist[1]+=N
groups=read(partition)['groups'];assert Counter(map(len,groups))=={24:83,8:4}
for G in groups:
    if len(G)<h:hist[m-h*len(G)]+=2*R
W=2*N+2*len(groups)*R;s=sum(r*n for r,n in hist.items());D=W*m-s
assert D==N-2*v*ell==1862080 and max(hist)==529
assert phase['W']==W and phase['rank_mass']==s and phase['R']==R
assert phase['exterior_histogram']=={'384':229640}
assert core['g_h']==592224 and core['G0']==2401613632
out=dict(status='PASS PR117 signed-MRP87 completed-core transfer and complete physical child list',
    core_interface_receipt_sha256=sha(core_path),physical_scalar_receipt_sha256=sha(ledger_path),
    partition_sha256=sha(partition),phase_receipt_sha256=sha(phase_path),
    h=h,m=m,v=v,R=R,groups=len(groups),W=W,rank_mass=s,deficit=D,max_child=max(hist),
    copied_internal_rank_mass=h*R+ell,exterior_histogram={384:229640},
    g_h=core['g_h'],G0=core['G0'],complete_child_multiplicities=dict(sorted(hist.items())),
    scope='The unchanged PR117 core interface and new signed partition phase proof are bound separately; exact moments/assembly remain separate')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='complete_child_multiplicities'},indent=2))
