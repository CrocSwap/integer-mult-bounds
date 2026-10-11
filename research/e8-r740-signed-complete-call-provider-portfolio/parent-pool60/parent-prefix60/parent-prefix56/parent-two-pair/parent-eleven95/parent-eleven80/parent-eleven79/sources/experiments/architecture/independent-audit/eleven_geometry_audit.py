from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/stage-search/pr445-signed79-eleven';g=json.loads((S/'hosted/GEOMETRY.json').read_text());word=json.loads((S/'word.json').read_text())
def dot(a,b):return sum(x*y for x,y in zip(a,b))
checks=0;factors=0
for port in g['ports']:
 t=port['port'];q=port['q'];assert q==word['lines'][t]
 A=[[Q(x) for x in row] for row in port['complement_columns']];rho=[[Q(x) for x in row] for row in port['rho15']];cols=list(zip(*rho))
 assert all(dot(a,b)==int(i==j) for i,a in enumerate(cols) for j,b in enumerate(cols))
 assert rho==list(map(list,zip(*rho)))
 assert all(rho[i][j]==Q(q[i]*q[j],4) for i in range(8) for j in range(8))
 assert [row[8:] for row in rho[:8]]==A
 for stage,r in enumerate(port['routes']):
  assert r['stage']==stage and r['axes']==(list(range(8)) if stage==0 else list(range(8))+list(range(8+7*(stage-1),8+7*stage)))
  if not stage:assert r['identity'];checks+=1;continue
  B=[[Q(i==j) for j in range(15)] for i in range(15)]
  for typ,i,j,c in reversed(r['elementary_inverse_replay']):
   if typ=='swap':B[i],B[j]=B[j],B[i]
   elif typ=='scale':B[i]=[x/Q(c) for x in B[i]]
   else:B[i]=[x-Q(c)*y for x,y in zip(B[i],B[j])]
  assert B==rho;factors=max(factors,len(r['elementary_inverse_replay']));checks+=1
assert checks==1320 and factors==g['max_route_factors']
out={'status':'PASS_INDEPENDENT_ALL1320_ELEVEN_ROUTE_MATRICES_AND_FACTOR_REPLAYS','routes':checks,'ports':120,'dimension':78,'max_route_factors':factors,'scope':'Exact rational compressed15-axis chart, orthogonality/involution, actual root binding and all eleven stage coordinate embeddings. Exterior summands are identity so nested projectors extend without new denominators. Full weighted primitive/compiler precision and all-size interfaces remain conditional.','geometry_sha256':hashlib.sha256((S/'hosted/GEOMETRY.json').read_bytes()).hexdigest()}
(P/'ELEVEN-GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
