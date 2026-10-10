import sys
from pathlib import Path
import json,collections,itertools
import sympy as S
p=Path(sys.argv[1]).resolve();D=json.loads((p/'baseline-candidates.json').read_text());P=json.loads((p/'ranked-pairs.json').read_text());sel=json.loads((p/'baseline-descent-selection.json').read_text());excluded={r for z in sel['entries'] for r in z['scalar'][:2]}
piv={x['a'] for x in D};don={d for x in D for d in x['partners']}; uses=collections.defaultdict(list)
for z in D:
 for b in z['partners']:uses[b].append(z)
chosen=[];reject=collections.Counter()
def sub(U,V):return S.Matrix.vstack(U,V).rank()==V.rows
for z in P:
 a=z['a'];b=z['partners'][0]
 if z['moment_numerator_delta']>=0:continue
 if a in piv or a in don or b in piv:reject['support']+=1;continue
 if a in excluded or b in excluded:reject['descent']+=1;continue
 U=S.Matrix(z['basis']);ok=True
 for q in uses[b]:
  V=S.Matrix(q['basis'])
  if z['cut']<q['cut']:ok &= sub(U,V)
  elif z['cut']>q['cut']:ok &= sub(V,U)
  else:ok &= sub(U,V) or sub(V,U)
 if not ok:reject['geometry']+=1;continue
 chosen.append(z);piv.add(a);don.add(b);uses[b].append(z)
mod=sum(x['dim'] for x in chosen)%3
if mod:
 # Remove cheapest one or two entries sufficient to normalize integral bank count.
 opts=[]
 for i,z in enumerate(chosen):
  if z['dim']%3==mod:opts.append((abs(z['moment_numerator_delta']),[i]))
 for i,j in itertools.combinations(range(len(chosen)),2):
  if (chosen[i]['dim']+chosen[j]['dim'])%3==mod:opts.append((abs(chosen[i]['moment_numerator_delta'])+abs(chosen[j]['moment_numerator_delta']),[i,j]))
 _,ix=min(opts);chosen=[z for i,z in enumerate(chosen) if i not in ix]
out=p/'greedy';out.mkdir(exist_ok=True);(out/'candidates.json').write_text(json.dumps(D+chosen));(out/'new-entrances.json').write_text(json.dumps(chosen,indent=2));print('new pivots',len(chosen),'new rank',sum(x['dim'] for x in chosen),'kind',dict(collections.Counter(x['kind'] for x in chosen)),'total score',sum(x['moment_numerator_delta'] for x in chosen),'reject',dict(reject))
