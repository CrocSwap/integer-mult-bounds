import json
from pathlib import Path
r=json.loads(Path(__file__).with_name('two_root_invoice.json').read_text())
def poly(word,compact=False):
 c=[0]*5;R=10 if compact else 11
 for kind,f,p,q,s in word:
  if compact:p=p-1 if p>=8 else p;q=q-1 if q>=8 else q
  c[0]-=2
  if kind=='F':c[4]+=2*f+1;c[3]+=2*R-2*min(p,q)-1;c[1]+=2*(q+1)
  elif kind=='R':
   if p<=q:raise ValueError('only descending root fixture')
   c[2]+=2*(p-q);c[1]+=2*(q+1)
  else:c[1]+=2*(q+1)
 return c
polys={k:poly(w) for k,w in r['literal_words'].items()};polys.update({k+'_compact':poly(w,True) for k,w in r['literal_words'].items() if k!='two_root12'})
for L,rows in r['invoices'].items():
 for k,row in rows.items():
  if sum(c*int(L)**i for i,c in enumerate(polys[k]))!=row['head_moves']:raise ValueError('independent formula mismatch')
delta=[a-b for a,b in zip(polys['two_root12'],polys['dyadic13_compact'])]
print('polynomials ascending',polys,'delta vs compact13',delta)
print('delta by length',[(L,sum(c*L**i for i,c in enumerate(delta))) for L in range(16,25)])
Path(__file__).with_name('two_root_head_formula.json').write_text(json.dumps({'polynomials':polys,'delta_against_compact13':delta,'validated_lengths':list(r['invoices'])},indent=2)+'\n')
