"""Independent count-vector and Taylor/Bernstein interval certificate.

No imports from the primary checker or PR795's implementation.
"""
from fractions import Fraction as F
from itertools import product
from math import comb, factorial
from pathlib import Path
import argparse
import json

SCALE = 1 << 160
ORDER = 24
LIMIT = F(1, 3)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def log_bounds(x):
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def series(z):
        s = sum((2*z**(2*j+1)/(2*j+1) for j in range(64)), F(0))
        return s, s+2*z**129/(129*(1-z*z))
    a,b=series((x-1)/(x+1));c,d=series(F(1,3))
    return F(((a+k*c)*SCALE).__floor__(),SCALE), F(((b+k*d)*SCALE).__ceil__(),SCALE)


def bernstein(counts, limit=LIMIT):
    # D(b)/b after multiplication by 48^b. Mass cancellation removes k=0.
    require(sum(r*c for r,c in counts.items()) == 0, 'mass')
    logs={r:log_bounds(F(48,r)) for r in counts}
    coefficients=[]
    for k in range(1,ORDER+1):
        lower=sum(c*r*logs[r][0 if c>0 else 1]**k for r,c in counts.items())/factorial(k)
        coefficients.append(F((lower*SCALE).__floor__(),SCALE))
    tail=F(0)
    for r,c in counts.items():
        if c < 0:
            u=logs[r][1]
            require(limit*u < ORDER+2, 'tail ratio')
            tail += (-c)*r*u**(ORDER+1)*limit**ORDER/factorial(ORDER+1)/(1-limit*u/(ORDER+2))
    tail=F((tail*SCALE).__ceil__(),SCALE)
    # b = limit*t. Power-to-Bernstein conversion on the complete interval.
    degree=ORDER-1
    beta=[sum(coefficients[k]*limit**k*F(comb(j,k),comb(degree,k))
              for k in range(j+1))-tail for j in range(degree+1)]
    require(min(beta)>0, 'uniform Bernstein positivity')
    return dict(lower_bernstein=str(min(beta)), tail=str(tail), degree=degree)


def partitions(total, cap):
    if total == 0:
        yield ()
    else:
        for x in range(min(total,cap),0,-1):
            for rest in partitions(total-x,x):
                yield (x,)+rest


def packing():
    widths=(4,5,7,8,9);prices=(-1,-20,-8,-2,4)
    cap_bonus={8:2,16:4,32:8,48:-13}
    upper={}; patterns=0
    for cap,bonus in cap_bonus.items():
        for counts in product(*(range(cap//w+1) for w in widths)):
            fill=sum(c*w for c,w in zip(counts,widths))
            if fill<=cap:
                patterns+=1
                r=cap-fill;score=bonus+sum(c*p for c,p in zip(counts,prices))
                upper[r]=max(upper.get(r,-10**9),score)
    require(upper[0]==0 and 2397*upper[48]<-31136,'all48 exclusion')
    checked=eligible=0
    for parts in partitions(48,44):
        checked+=1
        if any(r not in upper for r in parts):
            continue
        if 2396*upper[48]+sum(upper[r] for r in parts)<-31136:
            continue
        eligible+=1
        require(len(parts)>=2,'one-part residual')
        if len(parts)==2:
            require(parts[0]<=32,'two-part bound')
        else:
            require(parts[0]<=44 and parts[0]+parts[1]<=47,'majorization')
    require(eligible>0,'nonempty relaxed class')
    return dict(width_patterns=patterns, partitions_checked=checked,
                dual_eligible_partitions=eligible, upper=upper)


def intervals():
    cases=[{16:1,32:1,44:-1,3:-1,1:-1}]
    # Construct competitors from remaining mass, independently of primary cases().
    for mass in range(96,577,48):
        q,rem=divmod(mass,44)
        c={44:q,48:2397-mass//48}
        if rem:c[rem]=c.get(rem,0)+1
        for r,n in ((48,2396),(44,1),(3,1),(1,1)):
            c[r]=c.get(r,0)-n
        cases.append({r:n for r,n in c.items() if n})
    require(len(cases)==12,'case coverage')
    return [dict(coefficients=c,**bernstein(c)) for c in cases]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    result=dict(status='PASS_INDEPENDENT_UNIFORM_OWNER', packing=packing(), intervals=intervals())
    if args.out:
        require(not args.out.exists(),'existing output')
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_INDEPENDENT_UNIFORM_OWNER count_vectors+partitions+Bernstein interval=(0,1/3]')

if __name__=='__main__':
    main()
