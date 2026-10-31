#!/usr/bin/env python3
"""Independent numerical corroboration; NOT an acceptance certificate.

Prepared for @CubeJerry by a separate OpenAI Codex review worker, with
substantial AI assistance. Apache-2.0. Uses no imports from the interval
certificate or its implementation. Decimal supplies an independent 80-digit
moment calculation; libm beta/lGamma and subunit series supply a separate
complete-complement diagnostic. No rigorous error bound is asserted here.
"""
print("INDEPENDENT_DIAGNOSTICS_ONLY_NOT_EXACT_CERTIFICATE")

from decimal import Decimal, localcontext
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
T={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
with localcontext() as ctx:
 ctx.prec=80
 D=Decimal; logs={r:D(r).ln() for r in set(P)|set(T)}
 def M(H,s,d=0):return sum(D(c)*(s*logs[r]).exp()*logs[r]**d for r,c in H.items()) if d else sum(D(c)*(s*logs[r]).exp() for r,c in H.items())
 def bisect(fn,lo,hi):
  lo,hi=D(lo),D(hi);f=fn(lo)
  for _ in range(250):
   m=(lo+hi)/2;fm=fn(m)
   if (f>0)==(fm>0):lo=m;f=fm
   else:hi=m
  return (lo+hi)/2
 alpha=bisect(lambda s:M(P,s,1)-logs[5]*M(P,s),'.98','1')
 raw=bisect(lambda s:M(T,s)-M(P,s),'.99','1')
 A,B=M(P,alpha),M(T,alpha)
 def sides(s):
  Sn=sum(D(pr*tk)*((alpha*logs[r]+s*logs[k]).exp()-(alpha*logs[k]+s*logs[r]).exp()) for r,pr in P.items() for k,tk in T.items() if k>r)
  En=sum(D(pr*tk)*((alpha*logs[k]+s*logs[r]).exp()-(alpha*logs[r]+s*logs[k]).exp()) for r,pr in P.items() for k,tk in T.items() if r>k)
  return Sn,En
 def ratio(s):
  Sn,En=sides(s);return ((A-B)*M(P,s)+En)/Sn
 def gate(s):return ratio(s)-s*((s-1)*logs[121]).exp()
 cross=bisect(gate,'0.9974','0.9975')
 Sn,En=sides(raw)
 print('alpha',alpha)
 print('raw_exponent',raw)
 print('A_minus_B',A-B)
 print('target_paid_tilt_ratio',B/A)
 print('leaf_share',(A-B)*M(P,raw)/Sn)
 print('g_infinity',A*(M(T,raw,1)-M(P,raw,1))/Sn)
 print('cross_exponent',cross)
 print('cross_saving',1-cross)
 for s in map(D,['0.996','0.99731351095115','0.9974','0.9975','0.999','1']):
  Sn,En=sides(s)
  print('s',s,'R',ratio(s),'gate',gate(s),'identity_error',(Sn-En)-(A*M(T,s)-B*M(P,s)))

import math
P={1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}
T={5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}
m=121
alpha=.9898143824459775583296295009
A=sum(p*r**alpha for r,p in P.items()); B=sum(p*r**alpha for r,p in T.items())
U={};L={}
for r,pr in P.items():
 for k,wk in T.items():
  if k>r:
   w=pr*wk*(r*k/m)**alpha
   U[k]=U.get(k,0)+w;L[r]=L.get(r,0)+w

def integral(x,s):
 if x==1:
  beta=math.exp(math.lgamma(1-alpha)+math.lgamma(s)-math.lgamma(s+1-alpha))
  return (s*beta-1)/alpha
 a=s;power=x**(1-alpha);terms=[]
 for j in range(1,300):
  terms.append(a*power/(j-alpha));power*=x;a*=((j-s)/(j+1))
 return math.fsum(terms)

def deficit(s):
 J=math.fsum(w*integral(k/m,s) for k,w in U.items())-math.fsum(w*integral(r/m,s) for r,w in L.items())
 E=math.fsum(pr*wk*(k**alpha*r**s-r**alpha*k**s) for r,pr in P.items() for k,wk in T.items() if r>k)
 E+=(A-B)*math.fsum(pr*r**s for r,pr in P.items())
 return J-E/((s-alpha)*m**s)
lo=.9973;hi=.9975
for _ in range(50):
 mid=(lo+hi)/2
 if deficit(mid)<0:lo=mid
 else:hi=mid
print('alpha',alpha,'A-B',A-B,'U1',U[m])
print('critical_exponent',(lo+hi)/2,'saving',1-(lo+hi)/2,'residual',deficit((lo+hi)/2))
for s in [.99731351095115,.99738855,.99738857,.99743801996335,1.]:print(s,deficit(s))
