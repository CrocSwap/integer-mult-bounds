#!/usr/bin/env python3
"""Independent reverse formal Q4/Gaussian-rational review of the emitted connected L18 caller.
OpenAI Codex-assisted review; no imports from the primary builder/replayer.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse,copy,hashlib,json,time
if not __debug__:raise RuntimeError('Independent replay requires assertions')
ONE=(F(1),F(0));ZERO=(F(0),F(0))
def cadd(a,b):return(a[0]+b[0],a[1]+b[1])
def cmul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def add(a,b):
 out=a.copy()
 for mon,v in b.items():
  z=cadd(out.get(mon,ZERO),v)
  if z!=ZERO:out[mon]=z
  elif mon in out:del out[mon]
 return out
def scale(a,c):return{m:z for m,v in a.items()if(z:=cmul(v,c))!=ZERO}
def shift(a,qe=0,ds=(),modulus=4):
 out={}
 for mon,v in a.items():
  m=list(mon);m[0]=(m[0]+qe)%modulus
  for d in ds:m[d+1]+=1
  m=tuple(m);z=cadd(out.get(m,ZERO),v)
  if z!=ZERO:out[m]=z
  elif m in out:del out[m]
 return out

def replay(w,modulus=4,wrong_host_index=None,stop_on_failure=False):
 zero=(0,)*(w['stages']+1);bad=[];peak=0;checks=0
 for output in range(w['roles']):
  a=[{}for _ in range(w['roles'])];a[output]={zero:ONE}
  for event_index,e in reversed(list(enumerate(w['events']))):
   op=e[0]
   if op=='ADD':a[e[2]]=add(a[e[2]],scale(a[e[1]],(F(e[3]),F(0))))
   elif op=='SCALE':a[e[1]]=scale(a[e[1]],(F(e[2]),F(0)))
   elif op=='SWAP':a[e[1]],a[e[2]]=a[e[2]],a[e[1]]
   elif op=='QUERY':a[e[2]]=add(a[e[2]],shift(a[e[1]],qe=e[3],modulus=modulus))
   elif op=='LAMBDA':
    z=a[e[1]];s=e[2];assert s in(-1,1)
    a[e[1]]=add(scale(z,(F(1,2),F(s,2))),shift(scale(z,(F(1,2),F(-s,2))),qe=2,modulus=modulus))
   elif op=='IDLE_ONE':a[e[1]]=shift(a[e[1]],ds=e[2],modulus=modulus)
   elif op=='HOST':
    x,y,d=e[1:4];left,right=a[x],a[y]
    a[x]=shift(add(left,scale(shift(right,qe=-1,modulus=modulus),(F(1 if event_index==wrong_host_index else -1),F(0)))),ds=(d,),modulus=modulus)
    a[y]=shift(left,qe=1,ds=(d,),modulus=modulus)
   else:raise ValueError(op)
   peak=max(peak,sum(len(p)for p in a))
  expected=(1,)+tuple(int(w['masks'][output]>>d&1)for d in range(w['stages']))
  for j,z in enumerate(a):
   checks+=1
   if z!=({expected:ONE}if output==j else{}):
    bad.append([output,j])
    if stop_on_failure:return dict(bad=bad,coefficients=checks,peak_terms=peak)
 return dict(bad=bad,coefficients=checks,peak_terms=peak)

def factor(n):
 out=[];d=2
 while d*d<=n:
  if n%d==0:
   out.append(d)
   while n%d==0:n//=d
  d+=1
 if n>1:out.append(n)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--out',required=True);ap.add_argument('--write',action='store_true');args=ap.parse_args();h=Path(args.package);started=time.monotonic()
 p=h/'caller_L18.json';blob=p.read_bytes();w=json.loads(blob);root_blob=(h/'root_L18.json').read_bytes();root=json.loads(root_blob)
 caller_sha=hashlib.sha256(blob).hexdigest();root_sha=hashlib.sha256(root_blob).hexdigest()
 assert caller_sha=='f4090329f219edd493b4ca592128521e867a355fb528556b15201e759783568b'
 assert root_sha=='be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34'
 assert(w['roles'],w['stages'],root['n'],len(root['stages']))==(38,18,38,18)
 masks=[sum(1<<j for j,s in enumerate(root['stages'])if r in s['mask'])for r in range(38)];assert w['masks']==masks
 result=replay(w);assert not result['bad'],result;assert result['coefficients']==1444
 print('PASS_ALL_1444_FORMAL_COEFFICIENTS',result['peak_terms'],flush=True)
 controls={}
 for op in('HOST','QUERY','IDLE_ONE','LAMBDA'):
  bad=copy.deepcopy(w);at=next(i for i,e in enumerate(bad['events'])if e[0]==op);del bad['events'][at];r=replay(bad,stop_on_failure=True);assert r['bad'],op;controls['missing_'+op]=dict(event=at,witness=r['bad'][0]);print('REJECT',op,flush=True)
 at=next(i for i,e in enumerate(w['events'])if e[0]=='HOST');r=replay(w,wrong_host_index=at,stop_on_failure=True);assert r['bad'];controls['wrong_HOST_lower_left_sign']=dict(event=at,witness=r['bad'][0])
 for op in('QUERY','LAMBDA','IDLE_ONE'):
  bad=copy.deepcopy(w);at=next(i for i,e in enumerate(bad['events'])if e[0]==op)
  if op=='QUERY':bad['events'][at][3]*=-1
  elif op=='LAMBDA':bad['events'][at][2]*=-1
  else:bad['events'][at][2].append(bad['events'][at][2][0])
  r=replay(bad,stop_on_failure=True);assert r['bad'],('wrong',op);controls['wrong_'+op]=dict(event=at,witness=r['bad'][0])
 counts=Counter(e[0]for e in w['events']);assert counts==Counter({'ADD':1041,'SCALE':189,'SWAP':858,'LAMBDA':80,'HOST':18,'QUERY':3,'IDLE_ONE':181})
 assert[e[3]for e in w['events']if e[0]=='HOST']==list(range(18));assert all(len(e[2])==1 for e in w['events']if e[0]=='IDLE_ONE')
 targets=Counter(1+8*m.bit_count()for m in masks);paid=Counter({1:3,8:181});assert sum(r*c for r,c in targets.items())==1774
 fractions=[F(e[-1])for e in w['events']if e[0]in('ADD','SCALE')];assert max(q.denominator for q in fractions)==2 and max(abs(q)for q in fractions)==F(5,2)
 ordinary=sum(counts[op]for op in('ADD','SCALE','SWAP','LAMBDA'));assert ordinary==2168
 report=dict(status='PASS_INDEPENDENT_CONNECTED_L18_CALLER',caller_sha256=caller_sha,root_sha256=root_sha,
  formal_ring='Q(i)[Q,D0,...,D17]/(Q^4-1); unrestricted tuple D powers; direct reverse covectors, no evaluation of Q or D',
  coefficients=result['coefficients'],peak_reverse_polynomial_terms=result['peak_terms'],event_counts=dict(counts),ordinary_events=ordinary,
  target_histogram=dict(sorted(targets.items())),target_rank_mass=1774,paid_non_native=dict(paid),native_contract_calls=18,
  native_contract='HOST(x,y,s): D_s*(x+Q*y,-Q^-1*x), t=-1; supplied macro only, no native implementation or tariff verified',
  scalar_max_denominator=2,scalar_max_magnitude='5/2',controls=controls,
  scope='Exact finite caller and root-mask binding, event and symbolic profile audit only. No HOST native construction, physical/routing or ordinary-tariff admission, finite supplier, kappa or general root theorem.',seconds=time.monotonic()-started)
 report=json.loads(json.dumps(report));out=Path(args.out)
 if args.write:out.write_text(json.dumps(report,indent=2)+'\n')
 else:
  frozen=json.loads(out.read_text());assert{k:v for k,v in frozen.items()if k!='seconds'}=={k:v for k,v in report.items()if k!='seconds'},'frozen review differs'
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
