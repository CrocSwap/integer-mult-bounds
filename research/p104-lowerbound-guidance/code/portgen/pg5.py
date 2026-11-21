from pg1 import *
# monotonicity in h of ceiling at fixed rho (U k=inf, X+HS), and rho=0 tail
prev=None; bad=[]
for rho in (D(0), D(56)/104, D('0.8')):
    prev=None
    for h in list(range(4,41))+[48,64,81,100,128,200,400,729]:
        c=ceiling(rung(h,rho),False)[0]
        if prev is not None and c>prev: bad.append((float(rho),h))
        prev=c
    print('rho',float(rho),'last',h,float(c),'violations so far',bad); sys.stdout.flush()
# first-order closed form check
import math
def k1(h,rho):
    u=h-1; a=(2*u+1)*math.log(2*u+1)-2*u*math.log(u); b=h*math.log(h)-u*math.log(u); c=u*math.log(u)-(u-1)*math.log(u-1)
    return (2-2*rho)/(2*a-2*rho*b+c)
for h in (5,9,13,20): print('first-order kappa h',h,'rho 7/13',round(k1(h,56/104),6),'exact',float(ceiling(rung(h,D(56)/104),False)[0]))
