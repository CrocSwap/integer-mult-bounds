#!/usr/bin/env python3
"""Exact mixed-rank centre-sharing screen; no production mathematics imported.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
All powers use integer-square-root enclosures and dyadic exponent brackets.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import isqrt
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
GRID = Q(1, 10**24)
BITS, DEPTH = 224, 128
M, W, CAP = 73, 14336, 51


def need(ok, message):
    if not ok:
        raise ValueError(message)


def ceildiv(n, d):
    return -(-n // d)


def ceilroot(n):
    r = isqrt(n)
    return r + (r*r != n)


@lru_cache(None)
def roots(x, bits, depth):
    """Outward grid bounds on x, x^(1/2), ..., x^(1/2^depth)."""
    scale = 1 << bits
    lo = x.numerator * scale // x.denominator
    hi = ceildiv(x.numerator * scale, x.denominator)
    result = [(lo, hi)]
    for _ in range(depth):
        lo, hi = isqrt(lo * scale), ceilroot(hi * scale)
        result.append((lo, hi))
    return tuple(result)


def dyadic_power(chain, k, bits, depth):
    scale = 1 << bits
    lo = hi = scale
    for j in range(depth + 1):
        if k & (1 << (depth - j)):
            low, high = chain[j]
            lo, hi = lo * low // scale, ceildiv(hi * high, scale)
    return Q(lo, scale), Q(hi, scale)


@lru_cache(None)
def power(x, a, bits=BITS, depth=DEPTH):
    """Enclose x^a for rational x>=1, 0<=a<=1 without logarithms."""
    x, a = Q(x), Q(a)
    need(x >= 1 and 0 <= a <= 1, 'power domain')
    need(type(bits) is int and bits >= 4 and type(depth) is int and depth >= 1,
         'power precision domain')
    n = a.numerator * (1 << depth)
    lower, upper = n // a.denominator, ceildiv(n, a.denominator)
    chain = roots(x, bits, depth)
    lo = dyadic_power(chain, lower, bits, depth)[0]
    hi = dyadic_power(chain, upper, bits, depth)[1]
    need(0 < lo <= hi, 'power interval')
    return lo, hi


def residual(hist, m, stock, a, bit=False):
    """Bound sum n*r/(m*stock)*(m/r)^a + surcharge - 1."""
    need(type(m) is int and m > 1 and type(stock) is int and stock > 0,
         'moment dimensions')
    need(all(type(r) is int and 0 < r < m and type(n) is int and n >= 0
             for r, n in hist.items()), 'histogram domain')
    low = high = -Q(1)
    for r, n in sorted(hist.items()):
        lo, hi = power(Q(m, r), a)
        coeff = Q(n*r, m*stock)
        low += coeff * lo
        high += coeff * hi
    if bit:
        lo, hi = power(Q(m), a)
        coeff = Q(32*m*sum(hist.values()), 10**16*stock)
        low += coeff * lo
        high += coeff * hi
    return low, high


def partition(mass, cap=CAP):
    need(type(mass) is int and mass >= 0 and type(cap) is int and cap > 0,
         'partition domain')
    q, r = divmod(mass, cap)
    out = Counter({cap: q}) if q else Counter()
    if r:
        out[r] += 1
    return dict(sorted(out.items()))


def combined(left, right):
    out = Counter(left)
    out.update(right)
    return {r: n for r, n in out.items() if n}


def sharp_added_mass(hist, a, cap):
    """Strict two-sided decisions; failed acceptance never means rejection."""
    def decide(mass):
        lo, hi = residual(combined(hist, partition(mass, cap)), M, W, a)
        if hi < 0:
            return True
        need(lo > 0, 'unresolved mass boundary')
        return False
    low, high = 0, 1
    need(decide(low), 'base histogram must pass')
    while decide(high):
        high *= 2
    while high - low > 1:
        mid = (low + high) // 2
        if decide(mid):
            low = mid
        else:
            high = mid
    return dict(mass=low, partition=partition(low, cap),
                pass_residual=residual(combined(hist, partition(low, cap)), M, W, a),
                next_mass=high, next_partition=partition(high, cap),
                fail_residual=residual(combined(hist, partition(high, cap)), M, W, a))


def check_sources():
    pins = json.loads((PKG/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            data = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: '+row['path'])
            blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            need(blob == row['git_blob'], 'source Git blob: '+row['path'])
    return (json.loads((ROOT/'research/community-frontier1094-audit/ASSEMBLY.json').read_text()),
            json.loads((ROOT/'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_text()))


def kappa_at(b, c):
    """Closed form of seven bootstrap steps, then strict grid floor."""
    e = Q(1, 10**24)
    s = min(c, (1-e)*b) - Q(1, 10**27)
    a = s - (s-Q(384599, 10**10))*s**7
    q = a*(1-2*e)
    g = (1-e)*q/(1+q)
    ticks = g*10**18
    k = Q(ceildiv(ticks.numerator, ticks.denominator)-1, 10**18)
    need(k < g <= k+Q(1, 10**18), 'strict grid floor')
    return k, g, a


def first_bit_endpoint(b, c0, target):
    low, high = int(c0/GRID), int(b/GRID)
    need(kappa_at(b, low*GRID)[0] < target <= kappa_at(b, high*GRID)[0], 'target bracket')
    while high-low > 1:
        mid = (low+high)//2
        if kappa_at(b, mid*GRID)[0] >= target:
            high = mid
        else:
            low = mid
    return high*GRID


def minimum_changes(hist, stock, a, change):
    """First admissible integer number of explicitly prescribed changes."""
    def check(n):
        changed = dict(hist)
        for r, delta in change.items():
            changed[r] = changed.get(r, 0) + n*delta
        return residual(changed, 64, stock, a, bit=True)
    low, high = 0, 1
    need(check(0)[0] > 0, 'unmodified bit profile must fail')
    while check(high)[0] > 0:
        high *= 2
    need(check(high)[1] < 0, 'unresolved bit upper bracket')
    while high-low > 1:
        mid=(low+high)//2
        lo,hi=check(mid)
        if hi < 0:
            high=mid
        else:
            need(lo > 0, 'unresolved bit boundary')
            low=mid
    return dict(changes=high, pass_residual=check(high), previous_changes=low,
                fail_residual=check(low))


def controls():
    # Independent algebraic oracle: raise each interval to denominator q.
    count=0
    for x in (Q(1),Q(5,4),Q(3,2),Q(2),Q(73,51),Q(64),Q(73)):
        for den in range(1,14):
            for num in range(den+1):
                lo,hi=power(x,Q(num,den),bits=72,depth=41)
                need(lo**den <= x**num <= hi**den, 'integer-power oracle')
                count+=1
    x=Q(73)
    lo,hi=power(x,Q(1,3),bits=20,depth=3)
    truncated=dyadic_power(roots(x,20,3),2,20,3)[1]
    need(lo**3 <= 73 <= hi**3 and truncated**3 < 73, 'exponent truncation control')
    bad=Q(isqrt(2*(1<<4)**2),1<<4)
    need(bad*bad < 2, 'root rounding control')
    # Complete small-partition corroboration of the written concavity theorem.
    partitions=0
    def enumerate_parts(total,largest):
        if total==0:
            yield ()
        else:
            for r in range(min(total,largest),0,-1):
                for tail in enumerate_parts(total-r,r):
                    yield (r,)+tail
    for cap in range(2,7):
        for mass in range(1,19):
            optimal=partition(mass,cap)
            _,opt_hi=residual(optimal,73,1,Q(1,2))
            for parts in enumerate_parts(mass,cap):
                h=dict(Counter(parts));partitions+=1
                if h != optimal:
                    lo,_=residual(h,73,1,Q(1,2))
                    need(lo > opt_hi, 'partition extremum')
    return dict(integer_power_comparisons=count, complete_small_partitions=partitions,
                exponent_truncation_detected=True, upper_root_floor_detected=True)


def build():
    asm,bit=check_sources()
    h={int(r):n for r,n in asm['complex_profile'].items()}
    need(sum(r*n for r,n in h.items())==1041408 and M*W-sum(r*n for r,n in h.items())==5120,
         'selected complex ledger')
    need(2*CAP**2 < M*M <= 2*(CAP+1)**2, 'retained halving cap')
    b,c=Q(asm['complex_lower']),Q(asm['bit_lower'])
    hb={int(r):n for r,n in bit['nine']['profile'].items()};wb=bit['nine']['bit']['live']
    need(wb==28416 and 64*wb-sum(r*n for r,n in hb.items())==10272, 'selected bit ledger')
    baseline={}
    for name,hist,m,w,a,surcharge in [('complex',h,M,W,b,False),('bit',hb,64,wb,c,True)]:
        passing=residual(hist,m,w,a,surcharge);failing=residual(hist,m,w,a+GRID,surcharge)
        need(passing[1]<0<failing[0], 'selected strict endpoints: '+name)
        baseline[name]=dict(pass_residual=passing,fail_residual=failing)
    need(h[8]==1152,'selected centre count');h2=dict(h);h2[8]-=576
    targets={}
    for name,a in [('bit_endpoint',c),('next_complex_endpoint',b+GRID)]:
        targets[name]=sharp_added_mass(h2,a,CAP)
        targets[name]['endpoint']=a
        targets[name]['mass_per_call']=Q(targets[name]['mass'],144)
    need(targets['bit_endpoint']['mass']==4445 and targets['next_complex_endpoint']['mass']==4622,
         'mixed mass thresholds')
    equal_mass={51:90,1:18}
    equal_res=residual(combined(h2,equal_mass),M,W,b+GRID)
    need(sum(r*n for r,n in equal_mass.items())==4608 and equal_res[1]<0,'equal-mass gain control')
    need(residual(h,M,W,b+GRID)[0]>0,'restore original histogram control')
    need(2*72**2 >= 73**2 and 2*51**2 < 73**2,'halving-premise control')
    selected_k=Q(asm['kappa']);need(kappa_at(b,c)[0]==selected_k,'selected assembly grid')
    improved_b=b+Q(1,10**8)
    improved_res=residual(combined(h2,partition(4622)),M,W,improved_b)
    improved_k=kappa_at(improved_b,c)[0]
    need(improved_res[1]<0 and improved_k>selected_k,'quantized improvement witness')
    k_ample,g_ample,_=kappa_at(Q(3,1000),c)
    k_equal,g_equal,_=kappa_at(c,c)
    need(k_ample==k_equal==Q(865213734911801,5*10**17),'full gain grid equality')
    target=selected_k*Q(11,10)
    cstar=first_bit_endpoint(Q(3,1000),c,target)
    need(cstar==Q(921658892752012102303,5*10**23),'ten-percent endpoint')
    removal=minimum_changes(hb,wb,cstar,{1:-1})
    need(removal['changes']==649,'pure-removal threshold')
    # Pure-removal premise control: a mass-preserving reblocking can also pass.
    reblock=minimum_changes(hb,wb,cstar,{1:-42,42:1})
    return dict(status='PASS_CENTRE_SHARING_MIXED_OVERHEAD',no_new_kappa=True,
                precision=dict(fixed_bits=BITS,exponent_depth=DEPTH),baseline=baseline,
                mixed_overhead=targets,equal_mass_control=dict(histogram=equal_mass,residual=equal_res),
                quantized_improvement=dict(complex_endpoint=improved_b,residual=improved_res,
                                          conditional_recipe_kappa=improved_k),
                assembly=dict(full_gain=k_equal,equal_endpoint_grid_margin=g_equal-k_equal,
                              ample_endpoint_grid_margin=g_ample-k_ample,
                              target=target,bit_endpoint=cstar),
                bit_pure_removal=removal,bit_zero_mass_reblocking=reblock,controls=controls())


def main():
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0]);ap.add_argument('--write',action='store_true')
    args=ap.parse_args();result=build()
    text=json.dumps(result,indent=2,sort_keys=True,default=str)+'\n'
    path=PKG/'RESULT.json'
    if args.write:
        path.write_text(text)
    else:
        need(path.is_file(),'missing fixed RESULT.json; use --write only to generate')
        need(path.read_text()==text,'fixed RESULT.json mismatch')
    print(result['status'],'mass_full=4445 mass_next=4622 pure_removal=649 no_new_kappa')


if __name__=='__main__':
    main()
