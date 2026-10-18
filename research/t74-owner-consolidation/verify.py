#!/usr/bin/env python3
"""Bounded construction and directed moment replay; full admission is separate."""
import argparse,hashlib,json,tempfile
from fractions import Fraction as Q
from pathlib import Path
from build import HERE,build,read,need
S=1<<256
cd=lambda a,b:-(-a//b)
def unitlog(p,q):
 need(q<=p<=2*q,'unit log range');pn,qd=p-q,p+q
 lo=pn*S//qd;hi=cd(pn*S,qd);sl=sh=0
 for j in range(100):
  sl+=lo//(2*j+1);sh+=cd(hi,2*j+1)
  lo=lo*pn*pn//(qd*qd);hi=cd(hi*pn*pn,qd*qd)
 tail=cd(2*hi*qd*qd,201*(qd*qd-pn*pn))
 return 2*sl,2*sh+tail
L2=unitlog(2,1)
def logs(p,q):
 k=0
 while p>2*q:q*=2;k+=1
 a,b=unitlog(p,q);return a+k*L2[0],b+k*L2[1]
def exponential(lo,hi):
 need(0<=lo<=hi<S//100,'exp range');tl=th=sl=sh=S
 for j in range(1,96):
  tl=tl*lo//(S*j);th=cd(th*hi,S*j);sl+=tl;sh+=th
 return sl,sh+2*cd(th*hi,S*96)
def moment(profile,a,W):
 lo=hi=Q(0)
 for rank,count in profile.items():
  rank=int(rank);ll,lu=logs(73,rank);el,eu=exponential(ll*a.numerator//a.denominator,cd(lu*a.numerator,a.denominator))
  lo+=Q(rank*count*el,73*W*S);hi+=Q(rank*count*eu,73*W*S)
 return lo,hi

def verify(p):
 need(read(p/'new/borrow-fill/FILL.json.gz')==read(HERE/'FILL.json.gz'),'regenerated complete fill payload')
 profile=read(p/'PROFILE.json');need(profile==read(HERE/'CLAIM.json')['profile'],'claim profile binding');old=read(p.parents[1]/'source/PROFILE.json')
 # The local words stay fixed; only the literal idle remainders change.
 expected={int(k):v for k,v in old.items()}
 for r,n in {1:-2,3:-1,5:1}.items():expected[r]=expected.get(r,0)+n
 expected={str(k):v for k,v in sorted(expected.items()) if v}
 need(profile==expected,'independently derived consolidated profile')
 need(sum(int(r)*n for r,n in profile.items())==73*66304-23680,'exact rank-mass deficit')
 a=Q('0.001698511924002761437757');upper=a+Q(1,10**24)
 low=moment(profile,a,66304);high=moment(profile,upper,66304)
 need(low[1]<1<high[0],'strict directed endpoint bracket')
 need(moment(old,a,66304)[0]>1,'old fill must reject the new endpoint')
 need(moment(profile,Q('0.001698511343697629330'),66304)[1]<1,'exceeds PR2435 claimed endpoint')
 controls=[]
 for name,bad in [('omit_one_idle48',{**profile,'48':profile['48']-1}),('omit_one_idle5',{**profile,'5':profile['5']-1})]:
  need(sum(int(r)*n for r,n in bad.items())!=73*66304-23680,'mass mutation rejected');controls.append(name)
 return dict(status='PASS_OWNER_CONSOLIDATION_OWNERS_AND_EXACT_MOMENT',scope='Literal whole-owner/window/family construction, retained parent lift and exact moment bracket. Full native/global/outer admission requires full_replay.py.',
  replicas=74,calls=666,roles=289044,live=66304,profile=profile,complex_lower=str(a),complex_upper=str(upper),
  lower_residual_upper=str(low[1]-1),upper_residual_lower=str(high[0]-1),controls=controls+['old_fill_rejects_new_endpoint'])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--built',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
 if args.built:r=verify(args.built.resolve())
 else:
  with tempfile.TemporaryDirectory(prefix='kappa-owner-consolidation-') as d:r=verify(build(Path(d)/'build'))
 if args.output:args.output.write_text(json.dumps(r,indent=2)+'\n')
 print(r['status'],r['complex_lower'])
