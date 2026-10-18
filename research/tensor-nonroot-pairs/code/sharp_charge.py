"""GL-cover sharp fallback; PR465 formula, independent implementation with Codex.

Decimal arithmetic only proposes endpoints. All acceptance uses rational
Mercator/Taylor intervals and is checked by a second base-two engine.
"""
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q

def charges(m):
    n=2*m
    return 6*n*(n-1)+3*n+6*(n-1), Q(2*m**3,2**128)

def moment(engine, profile, m, w, saving):
    lo,hi=engine.moment(profile,m,w,saving,False)
    children,fraction=charges(m)
    a,b=engine.moment({1:children*sum(profile.values())},m,w,saving,False)
    return engine.floor(lo+a*fraction),engine.ceil(hi+b*fraction)

def certify(engine, profile, m, w):
    children,fraction=charges(m)
    assert 2*m**3*10**16 < 2**128
    with localcontext() as ctx:
        ctx.prec=80
        terms=[(Decimal(r*n)/Decimal(m*w),(Decimal(m)/Decimal(r)).ln()) for r,n in profile.items()]
        fallback=Decimal(children*sum(profile.values())*fraction.numerator)/Decimal(m*w*fraction.denominator)
        ln_m=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.01')
        for _ in range(250):
            mid=(lo+hi)/2
            value=sum(a*(mid*b).exp() for a,b in terms)+fallback*(mid*ln_m).exp()
            if value<1:lo=mid
            else:hi=mid
        lower=Q(int((lo*Decimal(10)**24).to_integral_value(rounding=ROUND_FLOOR)),10**24)
    while moment(engine,profile,m,w,lower)[1]>=1:lower-=Q(1,10**24)
    upper=lower+Q(1,10**24)
    assert moment(engine,profile,m,w,lower)[1]<1<moment(engine,profile,m,w,upper)[0]
    return dict(lower=str(lower),upper=str(upper),children=children,bad_fraction=str(fraction),cover='GL')
