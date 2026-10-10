import sys
import json,collections,math
from pathlib import Path
p=Path(sys.argv[1]).resolve();D=json.loads((p/'baseline-candidates.json').read_text());P=json.loads((p/'geometric-pairs.json').read_text());F=json.loads((p/'input/frames.json').read_text())['frames'];uses=collections.defaultdict(list)
for z in D:
 for b in z['partners']:uses[b].append((z['cut'],z['dim']))
meta={}
for cut in [676559,680080,700582,727593]:
 for z in json.loads((p/f'meta-{cut}.json').read_text()):meta[z['role']]=z
c=.00071153816501917;tau=1-c
for z in P:
 a=z['a'];b=z['partners'][0];d=z['dim']; fa=F[str(meta[a]['frame'])]['dim'];fb=F[str(meta[b]['frame'])]['dim'];h=collections.Counter();h[fa]-=1;h[fa-d]+=1
 path=[(-1,0)]+sorted(uses[b])+[(meta[b]['first'],fb)]
 # dimension is secondary key within cut because transformer sorts that way
 point=(z['cut'],d);before=max((x for x in path if x<=point),default=(-1,0));after=min((x for x in path if x>=point),default=path[-1]);u,v=before[1],after[1]
 assert u<=d<=v,(a,b,d,path,before,after)
 h[v-u]-=1;h[d-u]+=1;h[v-d]+=1;h.pop(0,None)
 delta=40*sum(n*(r/120)**tau for r,n in h.items())+d/3
 z['delta_histogram']={str(k):v for k,v in h.items() if v};z['moment_numerator_delta']=delta;z['first_dims']=[fa,fb];z['donor_interval']=[u,v]
P.sort(key=lambda z:z['moment_numerator_delta']);(p/'ranked-pairs.json').write_text(json.dumps(P,indent=2))
print('beneficial',sum(z['moment_numerator_delta']<0 for z in P));print('top',[(x['a'],x['partners'][0],x['dim'],x['cut'],x['kind'],x['moment_numerator_delta'],x['first_dims'],x['donor_interval']) for x in P[:30]])
