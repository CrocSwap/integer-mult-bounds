"""Independent rational characteristic checker; Python 3.11+, no dependencies.

Input: a certificate with bit.{m,W,child_multiplicities} and bit_saving.
This checks supplied finite distributions, NOT their physical provenance.
The bounds follow positive atanh/Taylor series with explicit geometric tails.
No contributor's arithmetic code is imported. No float enters a proof check.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from math import factorial
import argparse
import json

SCALE = 10**60

def require(b, message):
    if not b:
        raise ValueError(message)

def floor_grid(x):
    return Q((x*SCALE).numerator//(x*SCALE).denominator, SCALE)

def ceil_grid(x):
    return -floor_grid(-x)

@lru_cache(None)
def small_log(x):
    require(1 <= x <= 2, 'range reduction')
    z = (x-1)/(x+1)
    terms = 72
    lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q())
    hi = lo + 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return lo, hi

@lru_cache(None)
def logarithm(x):
    require(x >= 1, 'log domain')
    k = 0
    while x > 2:
        k += 1
        x /= 2
    a,b = small_log(x)
    c,d = small_log(Q(2))
    return floor_grid(a+k*c), ceil_grid(b+k*d)

def exponential(x, terms=12):
    require(0 <= x < 1, 'exp domain')
    lo = sum((x**j/factorial(j) for j in range(terms+1)), Q())
    # For j >= N+1, successive Taylor terms have ratio <= x/(N+2).
    hi = lo + x**(terms+1)/factorial(terms+1)/(1-x/Q(terms+2))
    return floor_grid(lo), ceil_grid(hi)

def moment(m, W, rows, a):
    require(m>1 and W>0 and 0<a<1, 'positive profile and saving')
    lo = hi = Q()
    for t,n in sorted(rows.items()):
        require(isinstance(t,int) and isinstance(n,int) and 0<t<m and n>0, 'child contract')
        l,u = logarithm(Q(m,t))
        weight = Q(t*n,m*W)
        lo += weight*exponential(a*l)[0]
        hi += weight*exponential(a*u)[1]
    return lo,hi

def root_bracket(m,W,rows,digits=22):
    scale = 10**digits
    left,right = 1,scale//100
    require(moment(m,W,rows,Q(left,scale))[1] < 1, 'left endpoint not certified')
    require(moment(m,W,rows,Q(right,scale))[0] > 1, 'right endpoint not excluded')
    while right-left>1:
        mid=(left+right)//2
        lo,hi=moment(m,W,rows,Q(mid,scale))
        if hi<1:
            left=mid
        elif lo>1:
            right=mid
        else:
            raise ValueError('ambiguous enclosure: increase precision')
    return Q(left,scale),Q(right,scale)

def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x

def run(path, search=True):
    raw=path.read_bytes()
    c=json.loads(raw)
    p=c['bit']; m,W=p['m'],p['W']
    rows={int(t):n for t,n in p['child_multiplicities'].items()}
    mass=sum(t*n for t,n in rows.items())
    require(mass==p['total_rank'], 'rank mass mismatch')
    require(m*W-mass==p['deficit'], 'rank deficit mismatch')
    a=Q(c['bit_saving'])
    lo,hi=moment(m,W,rows,a)
    require(hi<1, 'published bit saving not certified')
    result=dict(source=path.name,source_sha256=sha256(raw).hexdigest(),
        m=m,W=W,rank_mass=mass,deficit=m*W-mass,child_max=max(rows),
        published_a=a,published_kappa=Q(c['kappa']),published_moment=[lo,hi],
        certified_published_gap=1-hi,
        scope='Exact arithmetic on supplied profile; physical construction and global transfer require independent verification')
    if search:
        low,high=root_bracket(m,W,rows)
        ml,mh=moment(m,W,rows,low)[1],moment(m,W,rows,high)[0]
        require(ml<1<mh,'root enclosure')
        result.update(root_bracket=[low,high],lower_endpoint_gap=1-ml,
            upper_endpoint_excess=mh-1,
            balanced_supremum_bracket=[low/(1+low),high/(1+high)],
            root_uniqueness_reason='All children lie strictly between 0 and m; every positive summand strictly increases with a')
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('certificate',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--no-search',action='store_true')
    args=ap.parse_args()
    result=run(args.certificate,not args.no_search)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode({k:v for k,v in result.items() if k in
        ('m','W','rank_mass','deficit','root_bracket','balanced_supremum_bracket','scope')}),indent=2))

if __name__=='__main__':main()
