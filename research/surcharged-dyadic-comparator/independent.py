"""Certificate checks from direct moment values; no compiler/GCD imports."""
from fractions import Fraction as F


def demand(ok, message):
    if not ok: raise ValueError(message)


def residual(counts,m,W,t):
    # Direct source equation, including child count, not mass, in the surcharge.
    total=F(-m*W)
    for rank,count in counts.items():
        ratio=m//rank;power=0
        while ratio>1: ratio//=2;power+=1
        total+=count*rank*t**power
    exponent=0;size=m
    while size>1: size//=2;exponent+=1
    return total+F(32*m*m*sum(counts.values()),10**16)*t**exponent


def evaluate(poly,x):
    return sum(F(c)*x**i for i,c in enumerate(poly))


def check(a,b,m,W,certificate):
    demand(type(m) is int and m>=2 and m&(m-1)==0 and type(W) is int and W>0,'independent dimension and stock')
    for profile in (a,b):
        demand(isinstance(profile,dict) and profile and
               all(type(r) is int and 1<=r<=m and r&(r-1)==0 and type(n) is int and n>=0
                   for r,n in profile.items()) and sum(profile.values())>0,'independent profile domain')
        demand(residual(profile,m,W,F(1))<0,'independent positive-root contract')
    order=certificate['order']
    demand(type(order) is int and order in (-1,0,1),'independent exact status')
    if order==0:
        demand(certificate['status']=='EXACT_EQUAL','independent equality status')
        g=certificate['gcd'];quotients=certificate['quotients']
        k=m.bit_length()-1
        demand(1<len(g)<=k+1 and F(g[-1])==1 and evaluate(g,F(1))<0,'independent common factor sign')
        demand(len(quotients)==2,'independent two quotients')
        for profile,h in zip((a,b),quotients):
            demand(h and len(g)+len(h)-2<=k,'independent degree bound')
            # k+1 exact samples prove equality of degree <=k polynomials.
            for t in map(F,range(1,k+2)):
                demand(evaluate(g,t)*evaluate(h,t)==residual(profile,m,W,t),
                       'independent complete polynomial binding')
    else:
        demand(certificate['status']=='EXACT_ORDER','independent order status')
        intervals=[[F(x) for x in row] for row in certificate['intervals']]
        demand(len(intervals)==2 and all(len(row)==2 for row in intervals),'independent bracket shape')
        for profile,(lo,hi) in zip((a,b),intervals):
            demand(F(1)<=lo<=hi and residual(profile,m,W,lo)<=0<=residual(profile,m,W,hi),
                   'independent root enclosure')
        demand(intervals[0][1]<intervals[1][0] if order==-1 else intervals[1][1]<intervals[0][0],
               'independent strict separation')
    return order
