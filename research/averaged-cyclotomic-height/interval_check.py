"""Finite rational enclosures for the averaged-height derivation.

Uses the retained PR628 outward-rounded exponential kernel at 192 bits.
Logarithms and square roots below have explicit rational remainders.
No floating point is used. These cases do not replace the written proof.
"""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import importlib.util
import json
from math import gcd, isqrt
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'vendor/pr628/interval_kernel.py'
spec=importlib.util.spec_from_file_location('retained_interval_kernel',SOURCE)
i=importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)
i.BITS=192
i.SCALE=1<<i.BITS


def need(ok,label):
    if not ok:
        raise ValueError(label)


def invert(a):
    need(0<a[0]<=a[1],'positive reciprocal interval')
    return i.hull(1/a[1],1/a[0])


def sqrt_point(x):
    need(x>=0,'nonnegative square root')
    s=i.SCALE
    n=isqrt(x.numerator*s*s//x.denominator)
    lo=F(n,s)
    return lo,lo if lo*lo==x else F(n+1,s)


def square(a):
    low=0 if a[0]<=0<=a[1] else min(a[0]*a[0],a[1]*a[1])
    return i.hull(low,max(a[0]*a[0],a[1]*a[1]))


def modulus(a):
    squared=i.add(square(a[0]),square(a[1]))
    return sqrt_point(squared[0])[0],sqrt_point(squared[1])[1]


def atanh_sum(z):
    need(0<=z<=F(1,3),'log series argument')
    count=80
    lo=2*sum((z**(2*j+1)/(2*j+1) for j in range(count)),F(0))
    hi=lo+2*z**(2*count+1)/((2*count+1)*(1-z*z))
    return i.hull(lo,hi)


LOG2=atanh_sum(F(1,3))


@lru_cache(maxsize=None)
def log_point(x):
    x=F(x)
    need(x>0,'positive logarithm')
    k=x.numerator.bit_length()-x.denominator.bit_length()
    y=x/F(2)**k
    while y<1:
        k-=1
        y*=2
    while y>=2:
        k+=1
        y/=2
    lo,hi=atanh_sum((y-1)/(y+1))
    return i.add((lo,hi),i.scale(LOG2,k))


def logarithm(a):
    return log_point(a[0])[0],log_point(a[1])[1]


def cscale(a,b):
    return i.mul(a[0],b),i.mul(a[1],b)


def total(values):
    out=i.point(0)
    for value in values:
        out=i.add(out,value)
    return out


def upper_lt_lower(left,right,label):
    need(left[1]<right[0],label)


def encoded(a):
    return [str(x) for x in a]


def case(r):
    z=i.root_interval(r,1)
    powers=[i.ONE]
    for _ in range(r-1):
        powers.append(i.cmul(powers[-1],z))
    factors=[i.cadd(i.ONE,i.cneg(p)) for p in powers]
    lengths=[modulus(a) for a in factors]
    L=[i.point(0)]+[logarithm(a) for a in lengths[1:]]
    logr=log_point(F(r))
    full_log=total(L)
    need(full_log[0]<=logr[1] and logr[0]<=full_log[1],'cyclotomic logarithm identity enclosure')
    delta=F(1,r)
    rho=1-delta
    regularization=[]
    for a,l in zip(lengths[1:],L[1:]):
        ratio2=i.add(i.point(rho),i.scale(invert(square(a)),delta**2))
        correction=i.scale(logarithm(ratio2),F(-1,2))
        majorant=i.add(i.point(delta/(2*rho)),i.scale(invert(square(a)),delta**2/(2*rho)))
        absolute=(F(0),max(abs(x) for x in correction))
        upper_lt_lower(absolute,majorant,'pointwise regularization majorant')
        regularization.append(absolute)
    upper_lt_lower(total(regularization),i.point(F(11,16)),'summed regularization error')
    upper_lt_lower(total(invert(square(a)) for a in lengths[1:]),i.point(F(r*r,4)),
                   'reciprocal square sine bound')
    coeff=[]
    for h in range(r):
        value=i.ZERO
        for s in range(r):
            value=i.cadd(value,cscale(powers[(-h*s)%r],L[s]))
        coeff.append(cscale(value,i.point(F(1,r))))
    mass=total(modulus(a) for a in coeff)
    upper_lt_lower(mass,i.add(i.scale(logr,2),i.point(1)),'Fourier mass')
    units=[k for k in range(1,r) if gcd(k,r)==1]
    heights=[]
    maxima=[]
    for k in units:
        a=i.ONE
        sizes=[i.point(1)]
        tails=[i.point(0)]
        logtail=i.point(0)
        for s in range(r-1,0,-1):
            a=i.cmul(a,factors[(k*s)%r])
            sizes.append(modulus(a))
            logtail=i.add(logtail,L[(k*s)%r])
            tails.append(logtail)
        heights.append(logarithm(total(sizes)))
        maxima.append((max(a[0] for a in tails),max(a[1] for a in tails)))
    average=i.scale(total(heights),F(1,len(units)))
    Q=i.add(i.add(i.scale(square(logr),4),i.scale(logr,8)),i.point(2))
    upper_lt_lower(average,Q,'averaged height')
    geometric=[]
    for h in range(1,r):
        d=r//gcd(h,r)
        residues=[(h//gcd(h,r)*k)%d for k in units]
        primitive=[j for j in range(1,d) if gcd(j,d)==1]
        multiplicities={j:residues.count(j) for j in primitive}
        need(set(residues)==set(primitive) and len(set(multiplicities.values()))==1,
             'uniform primitive fibers')
        mean=i.scale(total(i.scale(invert(lengths[(h*k)%r]),2) for k in units),F(1,len(units)))
        upper_lt_lower(mean,i.scale(i.add(i.point(1),logr),2),'geometric average')
        geometric.append(mean)
    for k,M in zip(units,maxima):
        bound=logr
        for h in range(1,r):
            bound=i.add(bound,i.mul(modulus(coeff[h]),i.scale(invert(lengths[(h*k)%r]),2)))
        upper_lt_lower(M,bound,'pointwise maximum bound')
    ell=(r-1).bit_length()
    upper_lt_lower(i.mul(Q,invert(LOG2)),i.point(8*ell*ell),'dyadic conversion')
    return dict(r=r,embeddings=len(units),Fourier_mass=encoded(mass),
                averaged_log_height=encoded(average),analytic_bound=encoded(Q),
                geometric_characters=len(geometric),regularization_cases=len(regularization),
                primitive_fibers=True,pointwise_maximum_before_average=True)


def reject_pointwise_average():
    # f_j=r/product_(s=1)^j(1-zeta^s). Since sin(x)<=x,
    # AM-GM bounds the denominator by [pi(j+1)/r]^j.
    # This certifies that the averaged height bound is NOT pointwise.
    need(i.pi_interval()[1]<F(22,7),'rational upper bound for pi')
    r=4096
    j=r//6
    logr=log_point(F(r))
    lower=i.add(logr,i.scale(log_point(F(7*r,22*(j+1))),j))
    averaged=i.add(i.add(i.scale(square(logr),4),i.scale(logr,8)),i.point(2))
    need(lower[0]>averaged[1],'reject treating average as pointwise height')
    return dict(r=r,j=j,primitive_power=1,log_height_lower=encoded(lower),
                average_height_upper=encoded(averaged),pointwise_average_rejected=True)


def main():
    rows=[]
    for r in [3,4,5,7,8,9,11,13,16,17,19,23,25,27,29,31,32]:
        rows.append(case(r))
        print(r,'PASS rational interval enclosures',flush=True)
    result={'status':'PASS_RATIONAL_INTERVAL_CASES','bits':i.BITS,
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'scope':__doc__,'cases':rows,'pointwise_negative_control':reject_pointwise_average()}
    return result


if __name__=='__main__':
    main()
