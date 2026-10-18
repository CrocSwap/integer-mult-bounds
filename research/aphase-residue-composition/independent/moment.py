# SPDX-License-Identifier: Apache-2.0
"""Directed rational moment certificate for a checked literal owner profile.
Standard atanh/Taylor enclosures follow the retained independent-moment lineage.
Floating arithmetic only nominates an initial bracket; acceptance is exact.
This certificate is finite pricing; root owns native/global/outer admission.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter
import argparse,hashlib,json,math,sys
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
def need(v,msg):
 if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
@lru_cache(None)
def logarithm(x):
 need(x>=1,'positive reduced logarithm');e=0;y=x
 while y>=2:y/=2;e+=1
 def core(z):
  z=(z-1)/(z+1);need(0<=z<=Q(1,3),'atanh range');lo=2*sum((z**(2*j+1)/(2*j+1)for j in range(36)),Q(0));return lo,lo+2*z**73/(73*(1-z*z))
 a,b=core(y);c,d=core(Q(2));return a+e*c,b+e*d
def exponential(x):
 need(0<=x<Q(1,100),'small positive exponential');term=total=Q(1)
 for n in range(1,21):term=term*x/n;total+=term
 return total,total+(term*x/21)/(1-x/22)
def moment(hist,q,live):
 need(0<q<Q(1,500),'saving range');a=b=Q(0)
 for r,n in sorted(hist.items()):
  ll,lh=logarithm(Q(73,r));el,_=exponential(q*ll);_,eh=exponential(q*lh);w=Q(n*r,73*live);a+=w*el;b+=w*eh
 return a,b
def display(a,b):
 S=1<<160;f=lambda x:x.numerator//x.denominator
 return dict(lower_numerator=f(a*S),upper_numerator=-f(-b*S),denominator=S)
def write_receipt(out,result):
 out.parent.mkdir(parents=True,exist_ok=True);lock=out.with_name(out.name+'.lock');handle=lock.open('x')
 try:
  with out.open('x',encoding='utf8',newline='\n')as target:target.write(json.dumps(result,sort_keys=True,indent=2)+chr(10))
 finally:handle.close();lock.unlink()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline-profile',type=Path,default=Path(__file__).resolve().parent/'provider/PROFILE.json');ap.add_argument('--owner-receipt',type=Path,required=True);ap.add_argument('--best-claim',type=Path,default=Path(__file__).resolve().parent/'provider/OUTER-CLAIM.json');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();need(not a.out.exists(),'fresh moment output')
 files=[a.owner_receipt,a.best_claim];before={str(p.resolve()):sha(p)for p in files};owner=json.loads(a.owner_receipt.read_text());best=json.loads(a.best_claim.read_text());need(sha(a.best_claim)=='eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa','exact PR2853 outer headline pin');need('headline_kappa_source' not in best and Q(best['kappa'])==Q(best['kappa_rational']),'untruncated headline rational equality');need(owner['status']=='PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS','verified literal owner input');T=owner['replicas'];live=896*T;hist={int(k):v for k,v in owner['profile'].items()};need(owner['live']==live and owner['physical']==live+490,'literal normalization and charged private stock');need(sum(r*n for r,n in hist.items())==65088*T,'actual rank mass');need(all(0<r<73 and type(n)is int and n>0 for r,n in hist.items()),'positive paid profile')
 # Binary floats nominate only a wide initial rational grid interval.
 lo,hi=0.0,0.002
 for _ in range(60):
  q=(lo+hi)/2;v=sum(n*r*math.exp(q*math.log(73/r))for r,n in hist.items())/(73*live)
  if v<1:lo=q
  else:hi=q
 G=10**24;unit=10**12;mid=int(((lo+hi)/2)*10**12)*unit;L=mid-unit;H=mid+2*unit
 while moment(hist,Q(L,G),live)[1]>=1:L-=unit
 while moment(hist,Q(H,G),live)[0]<=1:H+=unit
 while H-L>1:
  m=(L+H)//2;ml,mh=moment(hist,Q(m,G),live)
  if mh<1:L=m
  elif ml>1:H=m
  else:raise ValueError('enclosure too wide for adjacent rational bracket')
 lower,upper=Q(L,G),Q(H,G);ll,lh=moment(hist,lower,live);ul,uh=moment(hist,upper,live);need(lh<1<ul,'strict adjacent root bracket')
 target=lower-Q(1,10**46)-Q(1,10**70);previous=Q(best['kappa']);need(target>previous,'strict gain over full exact comparison rational')
 rejected=[]
 def reject(name,fn,reason):
  try:fn()
  except ValueError as e:need(str(e)==reason,'wrong control reason '+name);rejected.append(dict(name=name,reason=reason))
  else:raise ValueError('accepted control '+name)
 def accepts(h,q,W=live):
  need(W==live,'source-bound normalization');need(moment(h,q,W)[1]<1,'strict moment admission')
 def bracket(x,y):need(x<y,'ordered bracket');need(moment(hist,x,live)[1]<1<moment(hist,y,live)[0],'strict bracket')
 reject('reversed_bracket',lambda:bracket(upper,lower),'ordered bracket')
 reject('upper_endpoint_as_admissible_lower',lambda:accepts(hist,upper),'strict moment admission')
 reject('wrong_live_denominator',lambda:accepts(hist,target,live+1),'source-bound normalization')
 bad=dict(hist);bad[1]=bad.get(1,0)+1;reject('one_unpaid_rank_one_child',lambda:accepts(bad,target),'strict moment admission')
 basepath=a.baseline_profile;basehash=sha(basepath);need(basehash=='d034034b6cb5dd82ae4fa69467a58b2b39f2987e8d109e1001b094e56a688bd8','pinned actual PR2853 T74 profile');baseline={int(k):v for k,v in json.loads(basepath.read_text()).items()};need(moment(baseline,target,66304)[0]>1,'old actual profile fails improved target');rejected.append(dict(name='actual_PR2853_T74_profile_at_improved_target',reason='exact lower moment above one'))
 need(logarithm(Q(1))==(0,0)and exponential(Q(0))==(1,1),'exact elementary controls');l2=logarithm(Q(2));need(logarithm(Q(4))==(2*l2[0],2*l2[1]),'exact logarithm scaling')
 need(before=={str(p.resolve()):sha(p)for p in files}and sha(basepath)==basehash,'input drift')
 result=dict(status='PASS_INDEPENDENT_EXACT_CANDIDATE_MOMENT',replicas=T,live=live,profile=hist,complex_lower=str(lower),complex_upper=str(upper),proposed_outer_target=str(target),strictly_above_full_comparison=True,best_claim_sha256=sha(a.best_claim),best_kappa_rational=best['kappa'],lower_moment_minus_one=display(ll-1,lh-1),upper_moment_minus_one=display(ul-1,uh-1),target_gain_over_comparison=display(target-previous,target-previous),controls=rejected,input_sha256={'owner_receipt':sha(a.owner_receipt),'best_claim':sha(a.best_claim)},baseline_profile_sha256=basehash,scope='Exact finite moment admission and comparison only; proposed outer target still requires all actual outer/native/global checks.')
 write_receipt(a.out,result);print(json.dumps({k:result[k]for k in['status','replicas','live','complex_lower','complex_upper','proposed_outer_target','strictly_above_full_comparison']}),flush=True)
if __name__=='__main__':main()
