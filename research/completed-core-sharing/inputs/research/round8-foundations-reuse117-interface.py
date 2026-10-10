"""Exact source binding and complete profile for PR117 plus frozen100."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE/'pr117-public/tree'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=read(ROOT/'certificates/deferred-product-complex-input.json')
producer=read(HERE/'round8-optimize-reuse117-producer.json')
assert all(row[k]==v for k,v in producer['matched'].items())
ledger_path=HERE/'round8-foundations-reuse117-ledger.json';ledger=read(ledger_path)
for key in ['all_source_scalar_identity_exact','literal_forward_and_inverse_signed_words',
    'every_carrier_fresh_support_exact','every_piece_target_coefficient_exact','all_centers_exact',
    'every_auxiliary_source_zero_frame','every_auxiliary_pre_exterior_full_frame',
    'histogram_matches_word','all_actual_alternating_Gauss_sums_valid']:
    assert ledger[key]
assert ledger['frame_violations']==ledger['stage_two_breaks']==0
assert ledger['dag_sha256']==producer['dag_sha256']==sha(ROOT/'certificates/deferred-product-complex-dag.json.gz')
assert ledger['word_sha256']==sha(ROOT/'certificates/deferred-product-complex-word.json.gz')
audit=read(HERE/'pr117-public/INHERITED_SOURCE_AUDIT.json')
for record in audit['files']:assert sha(ROOT/record['path'])==record['sha256']
h=row['h'];v=row['v'];R=row['R'];ell=row['loss'];m=h*h;N=v*v
assert (h,v,R,ell)==(24,2024,28705,552)
H=row['histogram'][:];assert sum(r*n for r,n in enumerate(H))==h*R+2*ell
assert H[h]==h;H[h]-=h;H[1]+=h
assert sum(r*n for r,n in enumerate(H))==h*R+ell
hist=Counter({r:2*v*n for r,n in enumerate(H) if r and n})
hist[(h-1)**2]+=2*N;hist[h-1]+=4*N;hist[1]+=N
old=hist.copy();old[m-h]+=2*v*R
word=json.loads(gzip.decompress((ROOT/'certificates/deferred-product-complex-word.json.gz').read_bytes()))
assert dict(old)=={int(r):n for r,n in word['child_list']['rows'].items()}
partition=HERE/'round8-foundations-transversal-frozen37.json'
assert sha(partition)=='218b42e4f59fb04692c2b66ed764a8cc4313706953ad49af27bf5c41ec226342'
groups=read(partition)['groups'];assert len(groups)==100 and sum(map(len,groups))==v
for G in groups:
    if len(G)<h:hist[m-h*len(G)]+=2*R
W=2*N+2*len(groups)*R;s=sum(r*n for r,n in hist.items());D=W*m-s
assert D==N-2*v*ell==1862080 and max(hist)==552
g=4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8;G0=N+2*v*(g+2*h)
out=dict(status='PASS PR117 completed-core transfer and complete frozen100 counts; inherited contracts retained',
    commit='cbb05ce504d571546d9b7794c186a613c659c3bf',producer_receipt_sha256=sha(HERE/'round8-optimize-reuse117-producer.json'),
    physical_scalar_receipt_sha256=sha(ledger_path),partition_sha256=sha(partition),
    R=R,W=W,rank_mass=s,deficit=D,max_child=552,copied_internal_rank_mass=h*R+ell,
    g_h=g,G0=G0,complete_child_multiplicities=dict(sorted(hist.items())),
    scope='Physical and scalar transfer proof is in the accompanying text; exact moment/assembly certificate is separate')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='complete_child_multiplicities'},indent=2))
