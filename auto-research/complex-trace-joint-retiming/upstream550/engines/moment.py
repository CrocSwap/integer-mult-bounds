"""Independent prospective ordinary five-stage cost, never supplier admission.

Consumes a raw one-invocation ledger made from the actual source/internal/target
paths.  No packed profile is used as an input.  Missing physical/finite/compiler
obligations must remain explicit in the accompanying report.
"""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
import hashlib, json, sys
from pathlib import Path

DYAD = 1 << 224

def floor(x): return F(x.numerator*DYAD//x.denominator, DYAD)
def ceil(x): return -floor(-x)

@lru_cache(None)
def logarithm(x):
    """Mercator bounds after binary reduction; ln(2) via two Mercator sums.

    For 1 <= y < 2, log(y) is an alternating series in z=y-1.
    We instead reduce to 1 <= y < 3/2, and bound log(3/2) and
    log(2) by the same alternating series at z=1/2 and z=1/3,
    using log(2)=log(3/2)+log(4/3). All sums are exact rationals.
    """
    assert x >= 1
    k = 0
    while x >= 2: x /= 2; k += 1
    j = int(x >= F(3, 2))
    if j: x /= F(3, 2)
    def mercator(y):
        z=y-1
        assert 0 <= z <= F(1,2)
        # An even partial sum is below log; the next term bounds its tail.
        t=z; s=F(0)
        for n in range(1, 225):
            s += (t if n & 1 else -t)/n
            t *= z
        return s, s+t/225
    a,b=mercator(x); c,d=mercator(F(3,2)); e,f=mercator(F(4,3))
    return floor(a+(k+j)*c+k*e), ceil(b+(k+j)*d+k*f)

def exponential(l,u):
    assert 0 <= l <= u < F(1,10)
    def poly(x):
        s=t=F(1)
        for j in range(1,25): t=t*x/j; s+=t
        return s,t
    lo,_=poly(l);hi,last=poly(u)
    return floor(lo),ceil(hi+last*u/25/(1-u/26))

def moment(H,m,W,a,bad=False):
    lo=hi=F(0)
    for r,n in H.items():
        assert 0 < r < m and n > 0
        l,u=logarithm(F(m,r)); e,f=exponential(a*l,a*u)
        p=F(r*n,m*W);lo+=p*e;hi+=p*f
    if bad:
        # Existing envelope shape, only conditionally portable to the new cover.
        l,u=logarithm(F(m));e,f=exponential(a*l,a*u)
        p=F(32*m*sum(H.values()),10**16*W)
        lo+=p*e;hi+=p*f
    return floor(lo),ceil(hi)

def decimal(x):
    with localcontext() as c:
        c.prec=70
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def certify(H,m,W,bad=False):
    with localcontext() as c:
        c.prec=70
        terms=[(Decimal(r*n)/Decimal(m*W),(Decimal(m)/Decimal(r)).ln()) for r,n in H.items()]
        fallback=Decimal(32*m*sum(H.values()))/Decimal(10**16*W) if bad else Decimal(0)
        lm=Decimal(m).ln();lo=Decimal(0);hi=Decimal('.003')
        for _ in range(210):
            a=(lo+hi)/2
            if sum(p*(a*l).exp() for p,l in terms)+fallback*(a*lm).exp()<1:lo=a
            else:hi=a
        q=int(((lo+hi)/2*10**24).to_integral_value(rounding=ROUND_FLOOR))
    lo=F(q,10**24);hi=lo+F(1,10**24)
    lv=moment(H,m,W,lo,bad);hv=moment(H,m,W,hi,bad)
    assert lv[1]<1<hv[0],(lo,hi,lv,hv)
    k=F(694782719690783,10**18);required=k/(1-k)
    at=moment(H,m,W,required,bad)
    return dict(lower=decimal(lo),upper=decimal(hi),lower_endpoint_residual_upper=decimal(lv[1]-1),upper_endpoint_residual_lower=decimal(hv[0]-1),strict_rational_signs=True,moment_minus_one_at_current_k_required_rate=[decimal(x-1) for x in at],nominal_k_ceiling_interval=[decimal(lo/(1+lo)),decimal(hi/(1+hi))])

def price(core,gauges,R,v,h):
    core=Counter({int(k):n for k,n in core.items() if n})
    gauges=Counter({int(k):n for k,n in gauges.items() if n})
    m=5*h;W=4*v+R;ell=h*(h-2)  # p = 10 port: was the p = 12 literal 24*22
    assert sum(r*n for r,n in core.items())==h*R+2*v*(h-1)+ell-sum(r*n for r,n in gauges.items())
    idle=Counter({r:2*v for r in (2*h-2,h-1,2*h+2,4)})
    ans={}
    for name,bundled in [('separate_rank_a_corrections',False),('bundled_rank_5a_corrections',True)]:
        H=Counter({r:5*n for r,n in core.items()});H.update(idle)
        for a,n in gauges.items():H[5*a if bundled else a]+=n if bundled else 5*n
        mass=sum(r*n for r,n in H.items());assert m*W-mass==4*v-5*ell
        ans[name]=dict(histogram=dict(sorted(H.items())),calls=sum(H.values()),rank_mass=mass,deficit=m*W-mass,maxchild=max(H),root=certify(H,m,W),root_with_inherited_bad_envelope=certify(H,m,W,True))
    return dict(status='PROSPECTIVE_COST_ONLY_NOT_PHYSICAL_OR_ASSEMBLY_ADMISSION',m=m,W=W,R=R,v=v,h=h,copy_calls_per_invocation=h,copy_rank=h-2,ell=ell,raw_core=dict(sorted(core.items())),auxiliary_entrances=dict(sorted(gauges.items())),idle_histogram=dict(sorted(idle.items())),profiles=ans,interval_method='Independent exact rational alternating Mercator log bounds (224 terms), 24-degree exponential with geometric tail, 224-bit outward dyadic rounding; Decimal only proposes endpoints.',bad_envelope_scope='10^-16 and 32*m^2 rank-one fallback calls per paid child are inherited assumptions, not a new m = 5h admission.')

if __name__=='__main__':
    path=Path(sys.argv[1]);raw=path.read_bytes();data=json.loads(raw)
    core=data['one_stage_helper_histogram_including_copies']
    gauges=data['auxiliary_entrance_rank_histogram']
    result=price(core,gauges,data['physical_R'],data['v'],data['h'])
    result['input_ledger_sha256']=hashlib.sha256(raw).hexdigest()
    result['input_head']=data['head']
    result['one_invocation_parts']={key:data[key] for key in ('physical_internal_excluding_center_copies','paid_center_copy_histogram','physical_source_histogram','physical_target_histogram')}
    print(json.dumps(result,indent=2))
