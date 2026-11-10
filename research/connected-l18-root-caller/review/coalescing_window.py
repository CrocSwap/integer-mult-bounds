#!/usr/bin/env python3
"""Independent fixed-invoice negativity over an interval; no author imports."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import combinations
if not __debug__:raise RuntimeError('Assertions required')

def certify(v,T,P,lo,hi):
 assert 0<lo<hi<1
 endpoint=v.sub(v.moment(T,lo),v.moment(P,lo));upper=(0,0)
 for r in T.keys()|P.keys():
  c=T[r]-P[r]
  # Positive c has negative derivative, largest at hi; negative c has
  # positive derivative, largest at lo. Sum interval upper endpoints.
  term=v.mul(v.power(r,hi if c>=0 else lo),v.log(r))
  upper=v.add(upper,v.smul(term,-c))
 assert endpoint[1]<0 and upper[1]<0,'Nonnegative endpoint or derivative bound'
 return endpoint,upper

def audit(root,caller,invoice,engine):
 spec=importlib.util.spec_from_file_location('iv',engine);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 raw=Path(root).read_bytes();native_raw=Path(invoice).read_bytes();caller_raw=Path(caller).read_bytes();R=json.loads(raw);N=json.loads(native_raw);C=json.loads(caller_raw)
 assert hashlib.sha256(raw).hexdigest()=='be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34'
 assert hashlib.sha256(native_raw).hexdigest()=='87a41b13bdd9248d538805f76a970f51335567845dfc0070698b6979a08b70d6'
 assert hashlib.sha256(Path(engine).read_bytes()).hexdigest()=='60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5'
 assert hashlib.sha256(caller_raw).hexdigest()=='f4090329f219edd493b4ca592128521e867a355fb528556b15201e759783568b'
 masks=[set(s['mask'])for s in R['stages']];assert len(masks)==18 and R['n']==38
 eligibility=[{s for s,m in enumerate(masks)if r in m}for r in range(38)]
 assert C['roles']==38 and C['stages']==18 and C['masks']==[sum(1<<s for s in E)for E in eligibility]
 census=Counter(e[0]for e in C['events']);assert census['HOST']==18 and census['IDLE_ONE']==181 and census['QUERY']==3
 allowed=[[set(h)for h in combinations(sorted(m),2)if all(not(eligibility[j]<eligibility[i])or j in h for i in h for j in m)]for m in masks]
 assert [len(z)for z in allowed]==[1]*8+[2]+[1]*9 and allowed[8]==[{16,37},{19,37}]
 degrees=[]
 for bridge in allowed[8]:
  host=[z[0]for z in allowed];host[8]=bridge
  degrees.append([sum(r in m-h for m,h in zip(masks,host))for r in range(38)])
 d,e=degrees;assert sum(d)==sum(e)==181
 assert [(r,d[r],e[r])for r in range(38)if d[r]!=e[r]]==[(16,1,2),(19,3,2)]
 # For every 0<k<1, strict concavity gives f(1)+f(3)<2f(2).
 # Eligibility union/intersection compression and its finite increasing
 # potential establish that these are the only compressed optimum cases.
 ports=104;calls=18;T=Counter();P=Counter()
 for E in eligibility:T[1+8*len(E)]+=ports
 for degree in d:
  if degree:P[8*degree]+=ports
 P[1]+=3*ports+calls*ports
 for r,c in N['helpers'].items():T[int(r)]+=calls*c
 for r,c in N['local_paid'].items():P[int(r)]+=calls*c
 lo=F('.00362701882');hi=F('.01')
 endpoint,upper=certify(v,T,P,lo,hi)
 assert endpoint[1]<-F('38.95')*v.B and upper[1]<-198383*v.B
 surplus=sum(r*(T[r]-P[r])for r in T.keys()|P.keys());assert surplus==760
 bad=P.copy();bad[1]-=calls*ports
 for label,args in [('omitted_paid_adapter',(T,bad,lo,hi)),('reversed_interval',(T,P,hi,lo))]:
  try:certify(v,*args)
  except AssertionError:pass
  else:raise AssertionError('Negative control accepted: '+label)
 return dict(status='PASS_UNIFORM_NEGATIVITY',root_sha256=hashlib.sha256(raw).hexdigest(),native_invoice_sha256=hashlib.sha256(native_raw).hexdigest(),engine_sha256=hashlib.sha256(Path(engine).read_bytes()).hexdigest(),interval=[str(lo),str(hi)],T=dict(sorted(T.items())),P=dict(sorted(P.items())),rank_surplus=surplus,optimal_degrees=d,left_endpoint_margin=v.show(endpoint),left_endpoint_margin_float=v.value(endpoint),uniform_derivative_upper_interval=v.show(upper),uniform_derivative_upper_float=v.value(upper),scope='Fixed104-port F+H1 supplier,18 full paid/helper invoices,3thinH1 perport,and181 idle incidences optimally coalesced in the fixed38 coordinate-role relaxation. Ordinary implementation work is optimistically free. Not a general root/native obstruction.')

if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--caller',required=True);p.add_argument('--invoice',required=True);p.add_argument('--engine',required=True);p.add_argument('--out',default='-');p.add_argument('--receipt');a=p.parse_args();result=audit(a.root,a.caller,a.invoice,a.engine);s=json.dumps(result,indent=2)+'\n'
 if a.receipt:assert json.loads(Path(a.receipt).read_text())==json.loads(s),'Frozen interval receipt differs'
 if a.out!='-':Path(a.out).write_text(s)
 print(s)
 print('PASS_UNIFORM_NEGATIVITY_AND_TWO_CONTROLS')
