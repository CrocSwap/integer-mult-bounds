"""Freeze the focused PR117/signed-MRP87 evidence and executable closure."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json
P=Path(__file__).resolve().parent
read=lambda name:json.loads((P/name).read_text())
sha=lambda name:hashlib.sha256((P/name).read_bytes()).hexdigest()
j=read('round8-optimize-reuse117-mrp.json');r=j['results'][0]
assert r['status'].startswith('CONDITIONAL CONSTRUCTION')
files=set(j['construction_audit_sha256'])|set(j['source_sha256'])
for name,digest in (j['construction_audit_sha256']|j['source_sha256']).items():assert sha(name)==digest,name
a=r['assemblies'][-1];k=Q(a['kappa']);assert k==Q(12310001053253,10**17)>Q(1,8192)
assert len(a['certificate']['strict_constraints'])==47 and len(a['certificate']['margins'])==7
assert all(Q(x)>0 for x in a['certificate']['strict_constraints'].values())
assert all(Q(x)>k for x in a['certificate']['margins'].values())
assert Q(a['certificate']['minimum_margin'])<k+Q(1,10**17)
assert r['bridge']['rows']['degree']==22000 and Q(r['bridge']['rows']['degree_gap'])==Q(20773,25)
files.update(['round8-optimize-reuse117-mrp.py','round8-optimize-reuse117-mrp.json',
 'round8-optimize-reuse117-mrp.txt','round8-optimize-reuse117-mrp-manifest.py',
 'round8-optimize-reuse117-source-audit.txt',
 'round8-optimize-reuse117-mrp-independent.py','round8-optimize-reuse117-mrp-independent.json',
 'round8-network-physical-ledger.py','round8-network-final-geometry.py','pr-review-network-geometry.json',
 'round8-foundations-minimal-v-word.json.gz','round8-network-minimal-v-ledger/forward-events.i32.gz',
 'round8-network-opposite-profile-proof.txt','pr-network-mrp24-proof.txt',
 'round8-foundations-transversal-frozen37.json',
 'round7-public/tree/certificates/round7/witness_23.json.gz',
 'round7-public/tree/certificates/round7/deferred_23.json.gz',
 'round7-public/tree/independent/deferred-readout/deferred.py',
 'round7-public/tree/independent/deferred-readout/check_lifted.py',
 'round7-public/tree/independent/deferred-readout/linalg.py',
 'round7-public/tree/independent/partial-swap/factor.py',
 'current-public-main/tree/certificates/copied-centers-network.json',
 'pr117-public/tree/scripts/deferred_product/complex_frames.py',
 'pr117-public/tree/certificates/deferred-product-complex-word.json.gz',
 'pr117-public/tree/research/deferred-product/PROOF.md',
 'pr117-public/tree/notes/stopped-product-factorization.tex',
 'pr117-public/tree/notes/stopped-product-interface.tex',
 'pr117-public/tree/notes/stopped-product-assembly.tex'])
for name,digest in read('round8-optimize-reuse117-producer.json')['source_sha256'].items():
 assert sha(name)==digest;files.add(name)
for record in read('pr117-public/INHERITED_SOURCE_AUDIT.json')['files']:
 name='pr117-public/tree/'+record['path'];assert sha(name)==record['sha256'];files.add(name)
op=read('round8-network-opposite-profile.json')
assert sha('round8-foundations-minimal-v-word.json.gz')==op['word_sha256']
assert sha('round8-network-minimal-v-ledger/forward-events.i32.gz')==op['events_sha256']
assert sha('round8-network-minimal-v-ledger/result.json')==op['ledger_sha256']
out=dict(status='PASS focused conditional PR117 plus signed MRP87 construction',kappa=str(k),
 kappa_decimal=a['kappa_decimal'],complex_saving=r['complex_moment']['saving'],
 W=r['profile']['W'],rank_mass=r['profile']['total_rank'],maxchild=529,
 inherited_interfaces_explicit=True,file_sha256={name:sha(name) for name in sorted(files)})
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
Path(__file__).with_name('round8-optimize-reuse117-mrp-bundle-inputs.txt').write_text(
 '\n'.join('research/'+name for name in sorted(files|{'round8-optimize-reuse117-mrp-manifest.json'}))+'\n')
print('PASS',len(files),'inputs; kappa',k)
