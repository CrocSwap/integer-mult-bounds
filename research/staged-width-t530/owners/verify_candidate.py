import sys
if not __debug__ or sys.flags.optimize:raise RuntimeError('Enabled assertions required before owner replay')
from pathlib import Path
from collections import Counter,defaultdict
import json,os,importlib.util,hashlib,argparse
P=Path(__file__).resolve().parent
if not os.environ.get('OWNER_SOURCE_REPO'):raise ValueError('explicitOWNER_SOURCE_REPOrequired')
s=importlib.util.spec_from_file_location('actual_owner',P/'source_context.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def need(x,m):
 if not x:raise ValueError(m)
def check(d,kind):
 # Regenerate expectedclock from authenticated actualinputstreams, not candidate fields.
 import gzip
 pins=json.loads((P/'INPUT-PINS.json').read_text())
 for rel,sha in pins.items():need(hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha,'inputpin')
 a=json.loads((P/'ORDER37.json').read_text());b=[[i,j+37]for i,j in json.loads((P/'T16-ORDER.json').read_text())]
 if kind=='concatenated':order=a+b
 else:
  from fractions import Fraction as F
  order=[z[2]for z in sorted([(F(2*i+1,666),0,z)for i,z in enumerate(a)]+[(F(2*i+1,288),1,z)for i,z in enumerate(b)])]
 need(d['order']==order,'actualsourceclock');
 providers=json.loads((P/'PROVIDERS.json').read_text());pins=json.loads((P/'ARTIFACTS.json').read_text());need(hashlib.sha256((P/'PROVIDERS.json').read_bytes()).hexdigest()==pins['PROVIDERS.json'],'providerpin')
 for provider in providers.values():
  need(Counter(provider['widths'])==v.INV,'providerwidths');need({int(k):n for k,n in provider['actual_paid_profile'].items()}==v.LOCAL,'providerlocal')
 c=v.common.context();win=c.owner.windows(c.template,order,53);g=Counter();fw=defaultdict(list)
 for (o,ch),(cap,lo,hi)in win.items():g[cap,lo,hi]+=112;fw[o,c.families[ch]].append((lo,hi))
 need(all(all(max(lo,l)>=min(hi,h)for l,h in rows[i+1:])for rows in fw.values()for i,(lo,hi)in enumerate(rows)),'disjointfamilywindows')
 G=[[*k,n]for k,n in sorted(g.items())];need(d['groups']==G,'actualgroups');S=d['S'];need(type(S)is int and S>0,'positiveintegralS');need(d['widths']==list(v.W),'widths');need({int(k):n for k,n in d['inventory'].items()}==dict(v.INV),'actualinventory')
 xb=Counter();xw=Counter();idle=Counter();seen=set()
 for gi,q,n in d['x']:
  need(type(gi)is int and 0<=gi<len(G) and len(q)==6 and all(type(z)is int and z>=0 for z in q)and type(n)is int and n>0,'patternintegers');need((gi,tuple(q))not in seen,'duplicatepattern');seen.add((gi,tuple(q)))
  used=sum(w*z for w,z in zip(v.W,q));need(used<=G[gi][0]and sum(q)<=S,'patterncapacity');xb[gi]+=n
  for w,z in zip(v.W,q):xw[gi,w]+=z*n
  if used<G[gi][0]:idle[G[gi][0]-used]+=n
 need(all(xb[i]==S*row[3]for i,row in enumerate(G)),'completebins');zw=Counter();gt=Counter();call=Counter();seen=set()
 for gi,t,w,n in d['z']:
  need(all(type(z)is int for z in (gi,t,w,n))and 0<=gi<len(G)and 0<=t<477 and w in v.W and n>0,'flowintegers');need((gi,t,w)not in seen,'duplicateflow');seen.add((gi,t,w));need(G[gi][1]<t<=G[gi][2],'window');zw[gi,w]+=n;gt[gi,t]+=n;call[t,w]+=n
 need(zw==+xw,'widthbalance');need(all(call[t,w]==S*v.INV[w]for t in range(477)for w in v.W),'callinventory');need(all(n<=S*G[g][3]for(g,t),n in gt.items()),'groupdegree')
 profile=Counter({r:n*477*S for r,n in v.LOCAL.items()});profile.update(idle);need(sum(r*n for r,n in profile.items())==65088*53*S,'mass');need(d['profile']=={str(r):n for r,n in sorted(profile.items())},'profile')
 physical=896*53*S+509;sp=2**(36**2)
 for i in range(1,37):sp*=2**(2*i)-1
 bits=(sp*physical).bit_length();stock=(bits+1)//2
 return {'status':'PASS_EXACT_T53_AGGREGATE_ONLY','replicas':53*S,'calls':477*S,'roles':477*S*408,'physical':physical,'stock_l2_bits':stock,'required_reserve':188+stock,'retained_payload':2048,'stock_bound_pass':stock<=1330,'profile':dict(sorted(profile.items())),'scope':'No literalowner or prefixexecution claim; supplier-native sourcebinding and fulladmission remainrequired.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('candidate');p.add_argument('--kind',choices=['concatenated','evenly-interleaved'],required=True);a=p.parse_args();print(json.dumps(check(json.loads(Path(a.candidate).read_text()),a.kind),indent=2))
