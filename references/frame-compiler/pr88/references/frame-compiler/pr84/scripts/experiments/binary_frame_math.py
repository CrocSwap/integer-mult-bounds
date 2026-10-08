"""Exact rational helpers extracted without body changes from pinned PR48 verify.py.
Credits: icekylinx PR32/36, Dominik Scholz PR35, Zhihao Chen PR29/23,
Paureel/Aurel Prosz, Swapnil Jain, Rohan Arun PR25/31, RaD/hipotures,
Chafik Boukhalfa and inherited notices in references/frame-compiler/pr48.
Prepared with OpenAI Codex assistance; no formal theorem claim.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb, factorial, isqrt, prod

def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v)for v in x]
 return x

def require(condition, message):
    if not condition:
        raise ValueError(message)


def mersenne(exponent):
    require(exponent >= 3 and all(exponent % d for d in range(2, isqrt(exponent)+1)),
            'Composite Lucas-Lehmer exponent')
    p = 2**exponent - 1
    s = 4
    for _ in range(exponent - 2):
        s = (s*s-2) % p
    require(s == 0, 'Lucas-Lehmer failed')
    return p


def exactness(h):
    require(h in (23, 25), 'Uncertified dimension')
    primes = [mersenne(e) for e in (61, 31, 19)]
    Z = 3*h-7
    B0 = (4*h-2)*Z + 27*(h+1)
    D = 3*(h+1)*(h-1)**2
    B = 2*(h-1)*B0
    bounds = {r: sum(comb(h,j)*factorial(j)*B**j*D**(r-j)
                     for j in range(r+1)) for r in (2,3,4)}
    require(bounds[2] < primes[0], 'Rank-two minor modulus insufficient')
    require(max(bounds[3],bounds[4]) < prod(primes), 'CRT minor modulus insufficient')
    require(3*(h+1)*(h-1) < min(primes), 'Denominator may vanish')
    return dict(h=h, primes=primes, prime_product=prod(primes),
                single_numerator_bound=B0, common_denominator_bound=D,
                correction_numerator_bound=B, minor_bounds=bounds,
                modulus_gaps={2: primes[0]-bounds[2],
                              3: prod(primes)-bounds[3],4: prod(primes)-bounds[4]})


@lru_cache(None)
def logs(x):
    x = Q(x)
    require(x >= 1, 'Log domain')
    k = 0
    while x > 2:
        x /= 2
        k += 1
    def small(y):
        z = (y-1)/(y+1)
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)), Q())
        return lo, lo+2*z**65/(65*(1-z*z))
    lo,hi = small(x)
    lo2,hi2 = small(Q(2))
    lo,hi = lo+k*lo2,hi+k*hi2
    scale = 10**30
    return Q((lo*scale).numerator//(lo*scale).denominator,scale), \
        Q(-(-(hi*scale).numerator//(hi*scale).denominator),scale)


def moment(m,W,rows,saving):
    require(type(saving) is Q and 0 < saving < 1, 'Exact positive saving required')
    lower,upper = Q(),Q()
    enclosure = {}
    for t,n in sorted(rows.items()):
        require(type(t) is int and type(n) is int and 0<t<m and n>0, 'Invalid child')
        lo,hi = logs(Q(m,t))
        u,v = saving*lo,saving*hi
        require(0 <= u <= v < 1, 'Exponential enclosure domain')
        weight = Q(t*n,m*W)
        lower += weight*(1+u+u*u/2+u*u*u/6)
        upper += weight*(1+v+v*v/(2*(1-v/3)))
        enclosure[t] = dict(lower=lo,upper=hi)
    return dict(saving=saving,exponent=1-saving,lower=lower,upper=upper,
                strict_gap=1-upper,logarithms=enclosure)

