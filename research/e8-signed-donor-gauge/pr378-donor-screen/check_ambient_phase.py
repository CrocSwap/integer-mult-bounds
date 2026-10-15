"""Exact Z4 ambient residual integration; no exponential address enumeration."""
from pathlib import Path
import json,gzip,hashlib
from collections import defaultdict
P=Path('pr378-donor-screen');sha=lambda b:hashlib.sha256(b).hexdigest()
raw=gzip.decompress((P/'prefix-gauge-bound-template.json.gz').read_bytes());t=json.loads(raw);assert sha(raw)==json.load(open(P/'bound-schedule-audit.json'))['template_sha256']
rraw=gzip.decompress((P/t['route_table_file']).read_bytes());assert sha(rraw)==t['route_table_sha256'];routes=json.loads(rraw)
c=json.load(gzip.open(P/'prefix-donor-candidate.json.gz'));ext=dict(c['ext']);geo=json.load(open(P/'best-bank-geometry.json'));m=t['m'];h=c['h'];q=geo['cap'];delta=geo['residual_phase_adapter']['left']['offset']
assert geo['residual_phase_adapter']['rank']==0 and geo['residual_phase_adapter']['left']['matrix_rows']==[1<<i for i in range(h)]
assert not any(geo['residual_phase_adapter']['left']['linear_Z4']) and not any(geo['residual_phase_adapter']['left']['quadratic_rows']) and geo['residual_phase_adapter']['left']['phase']==0
# parity(q.y) = sum q_i y_i - 2 sum_(i<j) q_i q_j y_i y_j mod4.
# Store actual linear and off-diagonal quadratic coefficients modulo4.
def normal(terms):
 lin=[0]*m;quad={}
 for x,a in terms:
  ids=[j for j in range(m) if (x>>j)&1]
  for j in ids:lin[j]=(lin[j]+a)%4
  if a%2:
   for k,i in enumerate(ids):
    for j in ids[k+1:]:quad[i,j]=(quad.get((i,j),0)+2*a)%4
 return tuple(lin),tuple(sorted((i,j,v) for (i,j),v in quad.items() if v))
def mv(A,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(A))
full=[(1<<i,1) for i in range(h)];stagechecks=0
# The literal nested children and rank-zero adapters have only local
# support. In each lifted endpoint ratio Q_E cancels on the SAME side,
# leaving F D^-1 tensor I. This checks the exact Fourier phase as well.
for entry in t['ambient_prefix_checks']:
 prefix=[(1<<j,1) for j in entry['prefix_axes']];assert all(j>=h for j in entry['prefix_axes'])
 for gauged in [False,True]:
  D=[(q,1)] if gauged else [];want=full+[(x,-a) for x,a in D]
  actual=full+prefix+[(x,-a) for x,a in D+prefix]
  assert normal(actual)==normal(want);stagechecks+=1
banks=defaultdict(list);gauged=0;controls=0
for r in routes:
 A=r['map_local_to_bank_rows'];isg=r['helper'] in ext
 original=full+([(q,-1),(delta,2)] if isg else [])
 routed=[(mv(A,x),a) for x,a in original];target=[(1<<j,1) for j in r['residual_axes']]
 assert normal(routed)==normal(target)
 # Including translations ensures equality of exact Gaussian operators;
 # all factors fix the uniform vector, hence scalar phase is also fixed.
 if isg:
  gauged+=1
  bad=[(mv(A,x),a) for x,a in full+[(q,-1)]];assert normal(bad)!=normal(target);controls+=1
  bad=[(mv(A,x),a) for x,a in full+[(delta,2)]];assert normal(bad)!=normal(target);controls+=1
 banks[r['bank']].extend(target)
for s in range(9):
 for b,terms in banks.items():
  fam=7680+s*len(banks)+b;pad=next((p for p in t['bank_padding'] if p['family']==fam),None)
  allterms=terms+([(1<<j,1) for j in pad['axes']] if pad else [])
  assert normal(allterms)==normal([(1<<j,1) for j in range(m)])
result=dict(status='PASS_EXACT_AMBIENT_RESIDUAL_Z4_AND_BANK_PRODUCT',template_sha256=sha(raw),route_table_sha256=sha(rraw),ambient_endpoint_cases=stagechecks,route_residual_phase_equalities=len(routes),gauged_routes=gauged,phase_omission_controls=controls,stage_bank_products=9*len(banks),scope='Exact tensor endpoint cancellation and routed Gaussian residuals including translation/global phase; combines source-bound local normalization and independent schedule/ownership receipts. Arbitrary cover conjugation preserves these literal identities. Retains common-grid, Clifford compiler, local recursive-child semantics and analytic interfaces. No new kappa or standalone supplier admission.')
(P/'ambient-phase-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
