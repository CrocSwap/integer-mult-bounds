"""Two fixed nested-frame reductions after the pinned PR378/two-helper chain.
No scalar coefficients, operations, order, copied totals or boundary frames change.
Prepared with OpenAI Codex assistance. PR378 and inherited notices apply.
"""
import copy,json
from collections import Counter
from hashlib import sha256
import candidate_from378,two_alias
FINAL='3df4c637c69840d53a0137eadbe16e25add617984bbe4da099d059f026192f1e'
def build(raw):
 c=json.loads(candidate_from378.build(raw));old=copy.deepcopy(c)
 assert sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()==candidate_from378.FINAL
 for index,before,after in [(343,663,949),(369,676,948)]:
  assert c['B'][index][1]==before
  assert (len(c['frames'][before]),len(c['frames'][after]))==(6,5)
  c['B'][index][1]=after
 assert all(g[:1]+g[2:]==z[:1]+z[2:]for g,z in zip(c['A']+c['B'],old['A']+old['B']))
 cur=list(c['start']);H={k:Counter()for k in 'xysc'}
 def climb(r,f):
  assert two_alias.inside(tuple(c['frames'][cur[r]]),tuple(c['frames'][f]))
  d=len(c['frames'][f])-len(c['frames'][cur[r]])
  if d:H['x'if r<c['v']else'y'if r<2*c['v']else's'][d]+=1
  cur[r]=f
 for phase in ['A','B']:
  if phase=='B':
   for _,r,f in c['ret']:assert cur[r]==f;H['c'][len(c['frames'][f])]+=1
  for g in c[phase]:
   assert g[0]=='in'and len(g)==4
   for r in [g[2]]+[q[0]for q in g[3]]:climb(r,g[1])
 for r,f in enumerate(c['final']):climb(r,f)
 c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()}
 assert sum(r*n for h in H.values()for r,n in h.items())==c['N']
 raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode();assert sha256(raw).hexdigest()==FINAL
 return raw
