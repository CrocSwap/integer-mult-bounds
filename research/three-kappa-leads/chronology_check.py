"""Exact integer primal and source-window verifier for one T37/T8 join swap."""
from pathlib import Path
from collections import Counter,defaultdict
import json,os
from check_inputs import authenticate
from dependency import source,load
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
authenticate();os.environ['OWNER_SOURCE_REPO']=str(ROOT)
DEP=source();v=load('bound_source_context',DEP/'owners/source_context.py')
W=v.W;INV=v.INV;LOCAL=v.LOCAL;common=v.common

def need(x,m):
 if not x:raise ValueError(m)
def check(d):
 original=common.read(DEP/'owners/ORDER37.json')+[[s,r+37]for s,r in common.read(DEP/'owners/T8-ORDER.json')]
 need(original[332]==[8,36]and original[333]==[0,37],'actual interface')
 order=original[:];order[332],order[333]=order[333],order[332]
 need(d['order']==order,'one actual adjacent join swap')
 c=common.context();win=c.owner.windows(c.template,order,45);g=Counter();fw=defaultdict(list)
 for(o,ch),(cap,lo,hi)in win.items():g[cap,lo,hi]+=112;fw[o,c.families[ch]].append((lo,hi))
 need(all(all(max(lo,l)>=min(hi,h)for l,h in rows[j+1:])for rows in fw.values()for j,(lo,hi)in enumerate(rows)),'source family disjoint windows')
 G=[[*k,n]for k,n in sorted(g.items())];need(G==d['groups'],'source-derived groups')
 S=d['S'];need(type(S)is int and S>0,'positive copy count');need(d['widths']==list(W),'width classes')
 providers=common.read(DEP/'owners/PROVIDERS.json')
 for pid,p in providers.items():
  need(Counter(p['widths'])==INV,'actual source widths');need({int(k):n for k,n in p['actual_paid_profile'].items()}==LOCAL,'actual source local profile')
 xb=Counter();xw=Counter();idle=Counter();seen=set()
 for gi,q,n in d['x']:
  need(type(gi)is int and 0<=gi<len(G)and len(q)==6 and all(type(z)is int and z>=0 for z in q)and type(n)is int and n>0,'integer pattern')
  need((gi,tuple(q))not in seen,'duplicate pattern');seen.add((gi,tuple(q)));used=sum(w*z for w,z in zip(W,q))
  need(used<=G[gi][0]and sum(q)<=S,'whole-helper pattern capacity');xb[gi]+=n
  for w,z in zip(W,q):xw[gi,w]+=z*n
  if used<G[gi][0]:idle[G[gi][0]-used]+=n
 need(all(xb[i]==S*row[3]for i,row in enumerate(G)),'all physical bins');zw=Counter();gt=Counter();call=Counter();seen=set()
 for gi,t,w,n in d['z']:
  need(all(type(z)is int for z in (gi,t,w,n))and 0<=gi<len(G)and 0<=t<405 and w in W and n>0,'integer flow')
  need((gi,t,w)not in seen,'duplicate flow');seen.add((gi,t,w));need(G[gi][1]<t<=G[gi][2],'actual source window')
  zw[gi,w]+=n;gt[gi,t]+=n;call[t,w]+=n
 need(+zw==+xw,'exact width balance');need(all(call[t,w]==S*INV[w]for t in range(405)for w in W),'all call inventories');need(all(n<=S*G[gi][3]for(gi,t),n in gt.items()),'group per-call degree')
 profile=Counter({r:n*405*S for r,n in LOCAL.items()});profile.update(idle)
 need(d['profile']=={str(r):n for r,n in sorted(profile.items())},'reconstructed complete paid profile');need(sum(r*n for r,n in profile.items())==65088*45*S,'full mass')
 return {'status':'PASS_EXACT_AGGREGATE_NOT_LITERAL_OR_FULL_RELEASE','replicas':45*S,'calls':405*S,'roles':408*405*S,'profile':dict(sorted(profile.items())),'physical':896*45*S+509}
if __name__=='__main__':print(json.dumps(check(common.read(P/'CHRONOLOGY-CANDIDATE.json')),indent=2))
