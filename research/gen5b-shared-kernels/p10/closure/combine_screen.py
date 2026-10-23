"""Deterministic disjoint unions of the already completed190-line screen only."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collections import Counter,defaultdict
from itertools import product
import json,hashlib
from support import OUTPUT
R=OUTPUT/'closure'
rows=json.loads((R/'positive-candidates.json').read_text());groups=defaultdict(list)
for z in rows:
 k=tuple(z['line']);signature=sorted((p['pivot'],tuple(p['donors']))for p in z['relations'])
 if not any(signature==sorted((p['pivot'],tuple(p['donors']))for p in old['relations'])for old in groups[k]):groups[k].append(z)
assert set(groups)=={(8,9),(12,13),(16,17)}
candidates=[]
for choices in product(*[[None]+groups[k]for k in sorted(groups)]):
 selected=[x for x in choices if x]
 if not selected:continue
 active=set();okay=True;H=Counter()
 for z in selected:
  roles={p['pivot']for p in z['relations']}|{d for p in z['relations']for d in p['donors']}
  if active&roles:okay=False;break
  active|=roles;H.update({int(k):v for k,v in z['local_histogram_delta'].items()})
 if not okay:continue
 n=sum(z['pivots']for z in selected);donors=sum(z['donors']for z in selected);score=sum(z['finite_exponent_surrogate_delta']for z in selected)
 assert sum(k*v for k,v in H.items())==-n
 candidates.append(dict(pivots=n,donors=donors,members=len(active),mod5=n%5,finite_exponent_surrogate_delta=score,local_histogram_delta={k:v for k,v in sorted(H.items())if v},setup_pairs=sum(z['setup_pairs']for z in selected),groups=selected))
candidates.sort(key=lambda z:(z['finite_exponent_surrogate_delta'],z['setup_pairs'],z['pivots']))
(R/'disjoint-union-candidates.json').write_text(json.dumps(candidates,indent=2)+'\n')
best={str(k):next((z for z in candidates if z['mod5']==k),None)for k in range(5)}
(R/'best-residue-unions.json').write_text(json.dumps(best,indent=2)+'\n')
print(json.dumps({'declared_positive_lines':len(groups),'disjoint_combinations':len(candidates),'best':{k:({a:b for a,b in v.items()if a!='groups'}if v else None)for k,v in best.items()}},indent=2))
