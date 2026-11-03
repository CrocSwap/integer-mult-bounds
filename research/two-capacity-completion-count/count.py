"""Count two-capacity completions from exact quotient dimensions.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The quotient criterion is by ToikY, PR6535. The counting factors are classical.
"""
from functools import lru_cache
from math import isqrt, prod


def need(ok, why):
    if not ok:
        raise ValueError(why)


def prime_power(q):
    if type(q) is not int or q < 2:
        return False
    p = next((p for p in range(2, isqrt(q)+1) if q % p == 0), q)
    while q % p == 0:
        q //= p
    return q == 1


@lru_cache(maxsize=None)
def gaussian(n, k, q):
    if k < 0 or k > n:
        return 0
    k = min(k, n-k)
    numerator = prod(q**(n-i)-1 for i in range(k))
    denominator = prod(q**(k-i)-1 for i in range(k))
    need(numerator % denominator == 0, 'Integral Gaussian coefficient')
    return numerator // denominator


def injections(n, k, q):
    return prod(q**n-q**i for i in range(k)) if 0 <= k <= n else 0


def count_profile(q, n, u, a, b, s, c, d, t, k, ell, ec, ed, ecd, compatible=True):
    """Use dimensions of an actual contract, with all three image tests recorded."""
    need(prime_power(q), 'Finite-field order')
    need(all(type(x) is int and x >= 0 for x in (n,u,a,b,s,c,d,t,k,ell,ec,ed,ecd)), 'Nonnegative dimensions')
    need(type(compatible) is bool and 0 <= u <= n, 'Fixed rank and compatibility flag')
    j, tau = a+b-s, c+d-t
    need(0 <= j <= min(a,b) and s <= n-u and 0 <= tau <= min(c,d) and t <= n-u, 'Quotient dimensions')
    need(0 <= k <= j and 0 <= ell <= tau and 0 <= ecd <= min(ec,ed)
         and max(ec,ed) <= u and ec+ed-ecd <= u, 'Kernel and fixed-image dimensions')
    if not compatible or a > c or b > d or s > t or k > ell:
        return 0
    need(j-k <= tau-ell, 'Rank of the prescribed common quotient')
    h, alpha, beta = tau-j, a-j, b-j
    common = injections(ell,k,q)*q**(ell*(j-k))
    extensions = 0
    for i in range(max(0,alpha-(c-tau)), min(alpha,h)+1):
        extensions += (gaussian(h,i,q)*gaussian(c-tau,alpha-i,q)
                       * q**((h-i)*(alpha-i))*injections(alpha,alpha,q)
                       * injections(d-j-i,beta,q)*q**(i*beta))
    quotient = common * q**(j*(alpha+beta)) * extensions
    lifts = q**(ecd*j+ec*alpha+ed*beta)
    final = prod(q**n-q**i for i in range(u+s,n))
    return quotient*lifts*final


def contract(n, p, fixed, capacities, linear):
    """Extract a profile over a prime field with the retained exact row reducer."""
    need(type(n) is int and n >= 0 and type(p) is int and p >= 2
         and all(p % d for d in range(2,isqrt(p)+1)), 'Prime-field contract')
    need(len(capacities) == 2, 'Exactly two capacities')
    def validate(rows):
        need(all(len(r) == n and all(type(x) is int and 0 <= x < p for x in r) for r in rows), 'Canonical field vectors')
    for pair in fixed:
        need(len(pair) == 2, 'Fixed image pair')
        validate(pair)
    for pair in capacities:
        need(len(pair) == 2, 'Capacity pair')
        for rows in pair:
            validate(rows)
    def basis(rows):
        z = linear['reduce_system'](n,[tuple(r)+(0,) for r in rows],p)
        return tuple(r[:n] for r in z[0])
    def join(a,b):
        return basis(a+b)
    def meet(a,b):
        return linear['annihilator'](n,linear['annihilator'](n,a,p)+linear['annihilator'](n,b,p),p)
    def inside(a,b):
        return len(join(a,b)) == len(b)
    U = basis(tuple(x for x,y in fixed)); E = basis(tuple(y for x,y in fixed))
    need(len(U) == len(E) == len(fixed), 'Independent fixed injection basis')
    def image(rows):
        out=[]
        for v in rows:
            system = [tuple(x[i] for x,y in fixed)+(v[i],) for i in range(n)]
            reduced = linear['reduce_system'](len(fixed),system,p)
            need(reduced is not None, 'Vector belongs to fixed domain')
            coeff=[0]*len(fixed)
            for r,j in zip(*reduced):
                coeff[j]=r[-1]
            out.append(tuple(sum(coeff[j]*fixed[j][1][i] for j in range(len(fixed)))%p for i in range(n)))
        return basis(tuple(out))
    (A,C),(B,D) = [(basis(tuple(a)),basis(tuple(b))) for a,b in capacities]
    UA,UB,U0=meet(U,A),meet(U,B),meet(U,join(A,B))
    EC,ED=meet(E,C),meet(E,D);ECD=meet(EC,ED);Z=join(EC,ED)
    compat=inside(image(UA),C) and inside(image(UB),D) and inside(image(U0),join(C,D))
    if not compat:
        return 0, {'compatible':False}
    a,b=len(A)-len(UA),len(B)-len(UB)
    s=len(join(A,B))-len(U0);c,d=len(C)-len(EC),len(D)-len(ED)
    t=len(join(C,D))-len(meet(E,join(C,D)))
    k=len(meet(A,B))+len(meet(image(U0),Z))-len(UA)-len(UB)
    ell=len(meet(C,D))-len(ECD)
    values=[n,len(U),a,b,s,c,d,t,k,ell,len(EC),len(ED),len(ECD)]
    return count_profile(p,*values),dict(zip(('n','u','a','b','s','c','d','t','k','ell','ec','ed','ecd'),values))
