#!/usr/bin/env python3
"""Exact audit of PR647's tensor paid profile. Standard library; Python 3.9+."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_DEPTH = 66
BITS = 180
DEN = 1 << BITS


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parameters(n):
    require(type(n) is int and n >= 1, 'positive integer depth required')
    h, v, r = 9**n, 120**n, 8**n
    R = (885*v-1081*r)//14
    return h, v, r, R, R+2*v, 3*h, 2*v-3*h*r


def lifetime_profile(n, *, centers=True, endpoints=True):
    """Aggregate chronological moves; multiplicity replaces identical siblings.

    A register move is charged abs(end-start). No source histogram is imported.
    This checks dimension accounting, not the frame inclusions or scalar word.
    """
    h, v, r, _, _, _, _ = parameters(n)
    local, allocations = Counter(), 0

    def path(count, *dimensions):
        for start, end in zip(dimensions, dimensions[1:]):
            rank = abs(end-start)
            if rank:
                local[rank] += count

    def core(k, d, copies):
        nonlocal allocations
        ports, tails = 120**k, 120**(k-1)
        # Output helpers, pair helpers, and gather helpers are distinct roles.
        allocations += copies*(ports + 6720*tails + 8*tails)
        path(copies*ports, 0, h-d)                 # outputs, held at cap
        path(copies*6720*tails, 0, d, h-d, h)     # pair route
        path(copies*ports, d, 9*d, h)             # consumed inputs
        path(copies*8*tails, 0, 9*d)              # new gathers
        if k > 1:
            allocations += copies*ports           # decoder helpers
            core(k-1, 9*d, 8*copies)
            path(copies*ports, 0, h-9*d, h-d, h)
            path(copies*8*tails, h-9*d, h)        # child outputs after use

    allocations += v                              # root input helpers
    core(n, 1, 1)
    path(v, 0, 1)                                 # root input load
    path(v, h-1, h)                               # root output finish
    path(v, 1, h)                                 # data source
    path(v, 0, h-1)                               # data target
    if centers:
        path(r, h, 0)                             # private copied centers
    global_hist = Counter({s: 3*c for s, c in local.items()})
    if endpoints:
        global_hist[2] += 2*v                      # final two pivot lines
    return global_hist, allocations


def closed_profile(n):
    """Independent level-sum formula, with the terminal level separate."""
    h, v, r, _, _, _, _ = parameters(n)
    out = Counter()
    def add(rank, count):
        if rank:
            out[rank] += count
    for j in range(n-1):
        d, c = 9**j, v//15**j
        for s, a, b in [(h-d,1,1),(d,113,1),(h-2*d,56,1),
                        (8*d,2,1),(h-9*d,2,1),(9*d,2,15)]:
            add(s, 3*c*a//b)
    d, c = 9**(n-1), v//15**(n-1)
    for s, a, b in [(d,112,1),(7*d,56,1),(8*d,2,1),(h,1,15)]:
        add(s, 3*c*a//b)
    for s, c in [(1,6*v),(h-1,6*v),(h,3*r),(2,2*v)]:
        add(s,c)
    return out


@lru_cache(None)
def log_bounds(x):
    """atanh series after binary reduction, with a rational geometric tail."""
    x = Q(x)
    require(x >= 1, 'log argument below one')
    exponent = x.numerator.bit_length()-x.denominator.bit_length()
    if x < 2**exponent:
        exponent -= 1
    y = x / 2**exponent
    require(1 <= y < 2, 'log reduction failed')

    def unit(a):
        u = (a-1)/(a+1)
        term, total = u, Q(0)
        for j in range(64):
            total += term/(2*j+1)
            term *= u*u
        lower = 2*total
        upper = lower + 2*term/(129*(1-u*u))
        return lower, upper
    a,b = unit(y)
    c,d = unit(Q(2))
    lo,hi = a+exponent*c, b+exponent*d
    # Common dyadic endpoints keep later exact arithmetic small.
    return (Q((lo.numerator*DEN)//lo.denominator,DEN),
            Q(-((-hi.numerator*DEN)//hi.denominator),DEN))


def derivative_bounds(n, hist):
    h,v,_,_,_,m,_ = parameters(n)
    lo = hi = Q(0)
    for s,c in hist.items():
        a,b = log_bounds(Q(m,s))
        lo += s*c*a
        hi += s*c*b
    return lo/(m*v), hi/(m*v)


def quantitative_bounds(n):
    """Universal error envelopes around L=(913/14) log(3); see PROOF.md."""
    h,_,_,_,_,_,_ = parameters(n)
    t = Q(3,5)
    series = (1-t**(n-1))/(1-t)
    ell_lo,ell_hi = log_bounds(Q(3))
    _,U = log_bounds(Q(3*h))
    high = (131*series+113*t**(n-1)+2)/h + Q(87,14)*ell_hi/15**(n-1)
    low = (Q(651,5)*series+Q(603,5)*t**(n-1)+Q(10,3))*U/h + ell_hi/15**n
    return Q(913,14)*ell_lo-high, Q(913,14)*ell_hi+low


def rational(x):
    return str(x.numerator)+'/'+str(x.denominator)


def decimal(x, digits=36):
    scale = 10**digits
    z = x.numerator*scale//x.denominator
    return str(z//scale)+'.'+str(z%scale).zfill(digits)


def audit(n):
    h,v,r,R,W,m,D = parameters(n)
    H,helpers = lifetime_profile(n)
    require(H == closed_profile(n), f'depth {n}: profile constructions differ')
    require(helpers == R, f'depth {n}: helper count')
    S = (1334*v-1726*r)//7
    require(sum(H.values()) == 3*S+2*v == (4016*v-5178*r)//7,
            f'depth {n}: child count')
    require(sum(s*c for s,c in H.items()) == m*W-D,
            f'depth {n}: paid rank mass')
    require(0 < D < m*W and 0 < min(H) <= max(H) <= h,
            f'depth {n}: moment domain')
    require(sum(H.values()) > W, f'depth {n}: unique root endpoint')
    Mlo,Mhi = derivative_bounds(n,H)
    Jlo,Jhi = quantitative_bounds(n)
    require(Jlo <= Mlo <= Mhi <= Jhi, f'depth {n}: analytic derivative envelope')
    _,U = log_bounds(Q(m))
    A = Q(D,3*v)                    # h*(W-Phi(0))/v
    lower = A/(Mhi+(A/h)*U)
    upper = A/Mlo
    require(0 < lower < upper < Q(h,2), f'depth {n}: root bracket')
    # The proof bounds the actual root, not just a finite numerical search.
    data = {'depth':n,'h':h,'v':v,'helpers':R,'W':W,'m':m,'deficit':D,
            'children':sum(H.values()),'histogram_sha256':hashlib.sha256(
                json.dumps(sorted(H.items()),separators=(',',':')).encode()).hexdigest(),
            'normalized_derivative':[rational(Mlo),rational(Mhi)],
            'scaled_root_bounds':[rational(lower),rational(upper)],
            'scaled_root_decimal_floor':[decimal(lower),decimal(upper)],
            'center_factor':rational(1-Q(3,2)*Q(3,5)**n)}
    return data


def negative_controls():
    names = []
    for n in (1,2,6,66):
        h,v,_,_,W,m,D = parameters(n)
        for kwargs,name in [({'centers':False},'omit_center_copies'),
                            ({'endpoints':False},'omit_rank_two_endpoints')]:
            H,_ = lifetime_profile(n,**kwargs)
            require(sum(s*c for s,c in H.items()) != m*W-D,
                    'negative control escaped: '+name)
            names.append(f'{name}_depth_{n}')
    # Same number of calls and identical mass, but changed moment geometry.
    H,_ = lifetime_profile(2)
    mutated = H.copy()
    mutated[1] -= 1; mutated[9] -= 1
    mutated[2] += 1; mutated[8] += 1
    require(sum(mutated.values()) == sum(H.values()), 'control call count changed')
    require(sum(s*c for s,c in mutated.items()) == sum(s*c for s,c in H.items()),
            'control mass changed')
    a,b = derivative_bounds(2,H)
    c,d = derivative_bounds(2,mutated)
    require(b < c or d < a, 'same-mass mutant escaped derivative check')
    require(mutated != closed_profile(2), 'same-mass mutant escaped histogram')
    names.append('same_mass_same_count_wrong_moment')
    return names


def receipt():
    results = [audit(n) for n in range(1,MAX_DEPTH+1)]
    l,u = log_bounds(Q(3))
    constant = [Q(28,2739)/u,Q(28,2739)/l]
    # At seed-selected endpoint, certify relative error below 4e-15.
    lo,hi = map(Q,results[-1]['scaled_root_bounds'])
    require(lo > constant[1]*(1-Q(4,10**15)) and hi < constant[0],
            'depth 66 convergence target failed')
    return {'schema':1,'base_commit':'66849e1475c930fd7732b1a0067ffee7e1e95f60',
            'source_pr':647,'source_head':'956bb581e7f97328e1b53baa5aca3d2490f2f607',
            'seed':66,'domain':'all integer depths 1 through 66; no search',
            'limit_bounds':[rational(x) for x in constant],
            'limit_decimal_floor':[decimal(x) for x in constant],
            'depth_66_relative_shortfall_less_than':'4/1000000000000000',
            'depths':results,'negative_controls':negative_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',type=Path)
    args = parser.parse_args()
    result = receipt()
    payload = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.check:
        require(args.check.read_bytes() == payload.encode(), 'receipt mismatch')
    if args.output:
        args.output.write_text(payload)
    print('PASS_TENSOR_E8_RATE_AUDIT: 66 depths; 9 negative controls; exact rational bounds')

if __name__ == '__main__':
    main()
