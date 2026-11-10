#!/usr/bin/env python3
"""Independent exact unrounded-series coefficient cross-check; no package imports.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Separate author-side interval derivation; not independent human review.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import hashlib,json
G=1<<160

def roundi(lo,hi):
 if lo>hi:raise ValueError("unordered interval")
 return F((lo*G).__floor__(),G),F(-((-hi*G).__floor__()),G)
def pt(x):return(F(x),F(x))
def add(a,b):return roundi(a[0]+b[0],a[1]+b[1])
def sub(a,b):return roundi(a[0]-b[1],a[1]-b[0])
def mul(a,b):
 p=[x*y for x in a for y in b];return roundi(min(p),max(p))
def div(a,b):
 if b[0]<=0:raise ValueError('denominator')
 return mul(a,roundi(1/b[1],1/b[0]))
def scale(a,b):return mul(a,pt(b))

@lru_cache(None)
def logi(x):
 x=F(x)
 if x<=0:raise ValueError('log domain')
 k=x.numerator.bit_length()-x.denominator.bit_length()
 factor=F(2)**k
 if x<factor:k-=1;factor/=2
 y=x/factor
 def series(z):
  u=(z-1)/(z+1);v=u;total=F(0)
  for j in range(64):total+=2*v/(2*j+1);v*=u*u
  tail=2*v/(129*(1-u*u))
  return roundi(total,total+tail)
 return add(scale(series(F(2)),k),series(y))

@lru_cache(None)
def expp(x):
 if x<0:
  a=expp(-x);return roundi(1/a[1],1/a[0])
 n=0
 while x>F(1,4):x/=2;n+=1
 term=total=F(1)
 for j in range(1,61):term*=x/j;total+=term
 nxt=term*x/61;tail=nxt/(1-x/62)
 out=roundi(total,total+tail)
 for _ in range(n):out=mul(out,out)
 return out

def power(x,p):
 lo,hi=scale(logi(F(x)),p);return expp(lo)[0],expp(hi)[1]
def ipower(x,p):
 lo,hi=x if p>=0 else (x[1],x[0])
 return power(lo,p)[0],power(hi,p)[1]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def display(v):
 u=10**32
 return {'lower_scaled_1e32':str((v[0]*u).__floor__()),'upper_scaled_1e32':str(-((-v[1]*u).__floor__()))}
C=F(3125809,10**9);t=1-C;u=F(3,20);sig=t+u
a=power(t,1/C)
def turning(q):return sub(scale(sub(ipower(add(pt(q),a),t),div(a,pt(t))),u),pt((sig-1)*q))
def stationary(q,s):
 st=power(s,t);xt=power(q+s,t)
 return add(sub(scale(st,t*q/s+t-sig),pt(sig*q)),scale(xt,u))
def value(q,s):
 x=add(pt(q),s);num=sub(add(pt(q),ipower(s,t)),ipower(x,t));return div(num,ipower(x,sig))
D839,D840=turning(839),turning(840)
need(D839[0]>0>D840[1],'turning root brackets')
brackets={839:(F('0.36735947'),F('0.36735949')),840:(F('0.36729545'),F('0.36729548'))}
vals={}
Hs={}
for q,s in brackets.items():
 hs=(stationary(q,s[0]),stationary(q,s[1]));need(hs[0][0]>0>hs[1][1],'stationary signs')
 Hs[q]=list(map(display,hs));vals[q]=value(q,s)
need(vals[840][0]>vals[839][1],'unique integer maximum')
need(vals[840][1]<F(1937,250000),'claimed rational coefficient')
need(vals[840][0]>F('0.0077475'),'understated coefficient rejected')
need(stationary(840,brackets[839][0])[1]<0,'wrong stationary bracket rejected')
need(D839[0]>0,'turning bracket ending at839 rejected')
full=add(vals[840],ipower(add(pt(840),brackets[840]),-u))
need(full[0]>F(1937,250000),'full charge cannot use net coefficient')
record={'status':'PASS_INDEPENDENT_EXACT_NET_COEFFICIENT','method':'New Fraction atanh log (64 exact terms), unrounded Taylor exp (60 exact terms), explicit geometric tails and 160-bit outward final rounding; no predecessor imports','parameters':{'C':str(C),'t':str(t),'u':str(u),'sigma':str(sig)},'a':display(a),'turning':{'839':display(D839),'840':display(D840)},'stationary_signs':Hs,'values':{q:display(v) for q,v in vals.items()},'rational_upper':'1937/250000','controls':['understated coefficient .0077475','wrong q840 stationary bracket copied from839','turning bracket ending at839','full charge substituted for net tax'],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
print(json.dumps(record,sort_keys=True))
