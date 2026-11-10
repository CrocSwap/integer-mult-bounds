#!/usr/bin/env python3
"""Independent certified fixed-grid intervals (80 decimal places).
ln via 2 atanh after binary range reduction; exp(-x) via alternating
Taylor brackets. Uses only integer floor/ceiling, not Decimal transcendents.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import json,argparse
if not __debug__: raise RuntimeError('Run without -O; assertions are proof checks.')
B=10**80

def ceildiv(a,b):return -((-a)//b)
def exact(q):
 q=F(q);return q.numerator*B//q.denominator,ceildiv(q.numerator*B,q.denominator)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def mul(a,b):
 p=[a[i]*b[j] for i in (0,1) for j in (0,1)];return min(p)//B,ceildiv(max(p),B)
def div(a,b):
 assert b[0]>0
 p=[F(a[i]*B,b[j]) for i in (0,1) for j in (0,1)]
 return min(p).__floor__(),max(p).__ceil__()
def smul(a,q):return mul(a,exact(q))
def atanh_log(y):
 yi=exact(y);yy=mul(yi,yi);p=yi;s=(0,0)
 for j in range(100):s=add(s,smul(p,F(2,2*j+1)));p=mul(p,yy)
 # 0 <= tail <= 2 y^201/[201(1-y^2)] < 3*(1/3)^201.
 return s[0],s[1]+ceildiv(3*B,3**201)
@lru_cache(None)
def log(r):
 assert r>=1
 k=r.bit_length()-1;y=F(r-2**k,r+2**k)
 a=atanh_log(y);b=atanh_log(F(1,3));return add(a,smul(b,k))
def expminus(x):
 assert 0<=x[0]<=x[1]<B
 # Lower odd truncation at larger x, upper even truncation at smaller x.
 term=exact(1);s=exact(1);lower=upper=None
 for j in range(1,62):
  term=smul(mul(term,x),F(1,j));s=sub(s,term) if j%2 else add(s,term)
  if j==60:upper=s[1]
  if j==61:lower=s[0]
 return lower,upper
@lru_cache(None)
def power(r,k):return smul(expminus(smul(log(r),F(k))),r)
def moment(hist,k):
 out=(0,0)
 for r,c in hist.items():out=add(out,smul(power(int(r),F(k)),c))
 return out
def show(x):return [str(F(t,B)) for t in x]
def value(x):return [float(F(t,B)) for t in x]
def gate(invoice,claim,tested,lo,hi,bit_pin='.00376669'):
 T=invoice['T'];P=invoice['P'];claim,tested,lo,hi=map(F,(claim,tested,lo,hi));cap=F(bit_pin)
 assert 0<claim<tested<lo<hi and tested<cap
 margins={str(k):sub(moment(T,k),moment(P,k)) for k in (lo,hi,tested)}
 assert margins[str(lo)][0]>0 and margins[str(hi)][1]<0 and margins[str(tested)][0]>0
 target=moment(T,tested);paid=moment(P,tested)
 alpha=div(paid,target)
 # Tail exponent = 1-tested+1/7; argument exp may not be negative.
 # r^(1-tested+1/7)=r^(1-tested)* exp(log(r)/7).
 def exppos(x):
  assert 0<=x[0]<=x[1]<B
  return div(exact(1),expminus(x))
 def shifted(hist):
  out=(0,0)
  for rr,c in hist.items():
   r=int(rr);out=add(out,smul(mul(power(r,tested),exppos(smul(log(r),F(1,7)))),c))
  return out
 gamma=div(shifted(P),mul(exppos(smul(log(11),F(1,7))),target))
 delta=div(exact(sum(T.values())*12),mul(exppos(smul(log(11),tested)),target))
 reserve=F(1,10**27);decay=F(31,32);v=1920
 assert F(alpha[1],B)<1-reserve and F(gamma[1],B)<decay and F(delta[1],B)<decay
 assert 1/(1+v*reserve)+4*decay**v<1
 # exp(v*k*ln153) is large; apply repeated squaring of small factor.
 unit=exppos(smul(log(153),tested));factor=exact(1);z=unit;n=v
 while n:
  if n&1:factor=mul(factor,z)
  n//=2
  if n:z=mul(z,z)
 eta=div(exact(1-tested),factor);lp=1
 while F(eta[0],B)<=F(63,64)**lp:lp+=1
 written=lp+1
 assert F(factor[1],B)<2**written and 11**64<12**63 and 2*(11**v)**64 <= (153**v)**63
 gap=(tested-claim)/7;assert gap>0 and gap.numerator==1;step=gap.denominator
 wins=lambda j:(step*j+1)**written<2**j
 l,h=1,2
 while not wins(h):l,h=h,2*h
 while h-l>1:
  m=(l+h)//2
  if wins(m):h=m
  else:l=m
 assert wins(h) and not wins(h-1)
 # Monotonicity: upper derivative bound on [0, cap].
 derivative=(0,0)
 for rr in T.keys()|P.keys():
  c=T.get(rr,0)-P.get(rr,0);r=int(rr)
  term=mul(power(r,cap if c>=0 else 0),log(r));derivative=add(derivative,smul(term,-c))
 assert derivative[1]<0
 result=dict(claim=str(claim),tested=str(tested),raw_bracket=[str(lo),str(hi)],moment_margins={k:show(v) for k,v in margins.items()},moment_margin_float={k:value(v) for k,v in margins.items()},derivative_upper=float(F(derivative[1],B)),alpha=value(alpha),gamma=value(gamma),delta=value(delta),minimum_log_power=lp,written_log_power=written,compiler_gap=str(gap),H=str(step*h),BIT_pin=str(cap),BIT_margin=str(cap-tested))
 # Outer formulas evaluated independently after algebraically substituting
 # b=k+5g,a=k+4g,q=k+3g,epsilon=1-g,beta=1-3g.
 k=claim;g=gap;b=k+5*g;a=k+4*g;q=k+3*g;ep=1-g;be=1-3*g;r0=g/10;stop=layout=g
 sig=1-b;tau=1-a;internal=tau+(1-stop)*max(sig-tau,0);leaf=sig+stop*(1-sig);lam=1-(q+a)/2;xi=ep*(1+q)-F(3,32)+layout;key=be+1-ep
 M=[ep*q,a,1-ep+q*be,1-ep+a*be,1-ep+be,F(3,32)+xi-ep,xi+F(1,2)-ep,ep,1-(ep+be+48-128+2)]
 checks=[cap-a,b-a,q,b-q,a-q,stop,1-stop,(1-stop)*b-a,1-internal-q,1-leaf-q,lam-tau,lam-sig,lam-internal,1-q-lam,1-q-leaf,ep,1-ep,xi-F(1,2),ep-xi,be,ep-be,1-be,1-(2*xi-2)-r0-be,1-(2*xi-2)-be,1-ep-r0,1-ep,r0,1-key,1-be-2*(1-ep),128-48-be,layout,ep-a,F(1,32)-b,F(2**45-7**16),F(2),2-xi,F(5),1-be,1-be,1-ep,M[2]-M[0],g,k-F('.001730970419199163702738'),1-ep,F(11,2)]+[x-k for x in M]
 functional=[1-be,be*(1-F(3,1000)),128-48-ep-be-1,be*(1-F(1,250))]
 assert len(checks)==54 and len(functional)==4 and min(checks+functional)>0
 result['outer']=dict(strict_count=54,functional_count=4,minimum_margin=str(min(checks+functional)),BIT_just_below_effective_rejected=(a-F(1,10**12))-a<0)
 # Input-lift is only needed on [1-tested_complex,1]. A stronger BIT
 # pin is irrelevant to this interval; the source's crude BIT-wide bound
 # is not imported beyond its valid range.
 pos={7:1,3:1,5:1};neg={9:1,4:1,1:2};d1=(0,0);curvature=(0,0)
 for hist,sign in ((pos,1),(neg,-1)):
  for r,c in hist.items():
   d1=add(d1,smul(log(r),sign*c*r))
   curvature=add(curvature,smul(mul(log(r),log(r)),c*r))
 lift_cap=cap if cap<=F('.00376669') else tested
 assert tested<=lift_cap and F(d1[1],B)+lift_cap*F(curvature[1],B)<0
 lifts={}
 for price in (claim,tested):
  lift=sub(moment(pos,price),moment(neg,price));assert lift[0]>0
  assert price*(-F(d1[1],B))-price*price*F(curvature[1],B)/2>0
  lifts[str(price)]=show(lift)
 result['input_lift']=dict(margins=lifts,interval_kappa_cap=str(lift_cap),derivative_upper_on_required_interval=str(F(d1[1],B)+lift_cap*F(curvature[1],B)),source_BIT_wide_crude_bound_would_be=str(F(d1[1],B)+cap*F(curvature[1],B)))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('audit');p.add_argument('--claim',default='.00362852408');p.add_argument('--tested',default='.00362852408007');p.add_argument('--lower',default='.00362852408398727978896072723289');p.add_argument('--upper',default='.00362852408398727978896072723290');p.add_argument('--out',required=True);p.add_argument('--bit-pin',default='.00376669');a=p.parse_args()
 r=gate(json.loads(Path(a.audit).read_text())['invoice'],a.claim,a.tested,a.lower,a.upper,a.bit_pin);Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
