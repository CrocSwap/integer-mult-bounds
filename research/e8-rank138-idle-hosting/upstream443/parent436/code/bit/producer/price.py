# Dylan Crow, with Anthropic Claude assistance; Apache-2.0.
import math
from collections import Counter
def price(steps, R, v=120, h=8, L=72, ncent=9, exact=True):
    """steps: Counter of step ranks over x, y, helpers for ONE invocation (centres added here).
    Five-stage: H5 = 5*(steps + centres) + 2v*(2h-2,h-1,2h+2,4); W = 4v+R; m=5h."""
    m=5*h
    H=Counter()
    for r,n in steps.items(): H[r]+=5*n
    H[h]+=5*ncent  # centres at full frame (rank = frame dim = h)
    for r in (2*h-2,h-1,2*h+2,4): H[r]+=2*v
    W=4*v+R
    mass=sum(r*n for r,n in H.items())
    g=lambda r:r*math.log(m/r)
    D=sum(n*g(r) for r,n in H.items())
    s1=(W*m-mass)/D
    if not exact: return s1,W*m-mass,D
    lo,hi=0.0,0.01
    for _ in range(80):
        s=(lo+hi)/2
        if sum(n*(r/m)**(1-s) for r,n in H.items())>W: hi=s
        else: lo=s
    return lo,W*m-mass,D
