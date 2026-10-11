"""Exact actual signed95 target-control functional screen at matched prefix cuts."""
from pathlib import Path
import json,struct,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/stage-search/pr445-signed95-eleven/signed';rd=lambda p:json.loads(p.read_text());w=rd(S/'word.json');F={int(k):v for k,v in rd(S/'records/frames.json')['frames'].items()};E=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()));cs=rd(R/'experiments/architecture/independent-audit/TARGET-PREFIX-SIGNED.json')['candidates'];keys={(e['donor'],e['frame'])for e in cs};source=[{i:1}if i<120 else{}for i in range(981)];snap={}
def add(a,b,c):
 for k,v in list(b.items()):
  q=a.get(k,0)+c*v
  if q:a[k]=q
  elif k in a:del a[k]
for op,a,b,c,f,z in E:
 if op==1:
  add(source[a],source[b],c)
  if z==4 and(a,f)in keys:snap[a,f]=dict(source[a])
 elif op==2:source[b]=dict(source[a])
 elif op==3:source[b]={}
rows=[]
for e in cs:
 m=snap[e['donor'],e['frame']];G=F[e['frame']];vec=[sum(c*w['lines'][k][j]for k,c in m.items())for j in range(8)];ann=[sum(x*y for x,y in zip(vec,v))for v in G['A']];bad=[k for k in m if any(sum(x*y for x,y in zip(w['lines'][k],v))for v in G['A'])]
 rows.append({**e,'actual_source_terms':len(m),'bad_individual_support_count':len(bad),'aggregate_pairings':ann,'aggregate_compatible':not any(ann),'individual_support_compatible':not bad})
r=dict(status='ACTUAL_SIGNED95_TARGET_PREFIX_NEW_CONTROL_SOURCE_SCREEN',pairs=len(rows),aggregate_compatible=sum(e['aggregate_compatible']for e in rows),individual_compatible=sum(e['individual_support_compatible']for e in rows),rows=rows,source_signed_sha256=hashlib.sha256((S/'signed-records.bin').read_bytes()).hexdigest(),scope='Necessary candidate normal-source tests for newly used target controls, not a complete operator admission. Aggregate containment is weaker than inherited literal independent source support; no equivalence is assumed.')
(P/'SOURCE-SCREEN.json').write_text(json.dumps(r,indent=2)+'\n');print(r['pairs'],r['aggregate_compatible'],r['individual_compatible']);print([e for e in rows if e['aggregate_compatible']][:5])
