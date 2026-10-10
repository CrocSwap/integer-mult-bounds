import sys
from pathlib import Path
import json,collections,itertools,hashlib
p=Path(sys.argv[1]).resolve(); D=json.loads((p/'baseline-candidates.json').read_text()); piv={x['a'] for x in D}; don={d for x in D for d in x['partners']}; used=piv|don
out=[]
for c in [676559,680080,700582,727593]:
 M=json.loads((p/f'meta-{c}.json').read_text());raw=(p/f'response-{c}.bin').read_bytes();width=224
 groups=collections.defaultdict(list)
 for i,m in enumerate(M):groups[raw[i*width:(i+1)*width]].append(m)
 counts=collections.Counter(); new=[]
 for grp in groups.values():
  if len(grp)<2:continue
  for x,y in itertools.combinations(grp,2):
   a,b=x['role'],y['role']
   if a in piv or b in piv:continue
   if a in don and b in don:continue
   if a in don:a,b=b,a;x,y=y,x
   key='reuse' if b in don else 'fresh'
   new.append(dict(cut=c,pivot=a,donor=b,pivot_meta=x,donor_meta=y,kind=key));counts[key]+=1
 out+=new
 print(c,'groups',collections.Counter(len(x) for x in groups.values() if len(x)>1),'new',counts)
(p/'pair-pool.json').write_text(json.dumps(out))
print('total pairs',len(out),'unique',len({(x['pivot'],x['donor']) for x in out}))
