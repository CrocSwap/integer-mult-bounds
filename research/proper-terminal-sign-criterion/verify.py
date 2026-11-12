#!/usr/bin/env python3
"""Exact rational-power corroboration; the all-real theorem is in PROOF.md.

apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def nthroot(n, q):
    """Floor n**(1/q), by integer bisection only."""
    lo, hi = 0, 1 << ((n.bit_length() + q - 1) // q)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** q <= n:
            lo = mid
        else:
            hi = mid
    return hi if hi ** q <= n else lo


@lru_cache(None)
def power(x, t):
    require(x >= 0 and 0 < t < 1, 'power domain')
    p, q = t.numerator, t.denominator
    scale = 1 << 100
    value = x ** p
    n = value.numerator * scale ** q // value.denominator
    k = nthroot(n, q)
    lo = F(k, scale)
    if k ** q * value.denominator == value.numerator * scale ** q:
        return lo, lo
    return lo, F(k + 1, scale)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[1], a[1] - b[0]


def mul(a, b):
    v = [x * y for x in a for y in b]
    return min(v), max(v)


def h(a, b, x, t):
    return sub(add(power(x-a,t), power(b-x,t)), power(b-a,t))


def bill(T, paths, x, t):
    total = h(F(0),T,x,t)
    for a,b in paths:
        total = sub(total,h(a,b,x,t))
    return total


def positive(interval, label):
    require(interval[0] > 0, label + ': not certified strictly positive')


def valid(T, paths, t):
    require(T > 0 and 0 < t < 1 and len(paths) >= 1, 'bill domain')
    require(all(0 <= a <= T <= b for a,b in paths), 'terminal order')


def normalized_difference(T, paths, x, y, t):
    # G(x)/H0T(x) > G(y)/H0T(y), without interval division.
    return sub(mul(bill(T,paths,x,t),h(0,T,y,t)),
               mul(bill(T,paths,y,t),h(0,T,x,t)))


def main():
    counts = dict(root_controls=0, ratio_comparisons=0,
                  normalized_bill_comparisons=0, zero_start_bills=0,
                  endpoint_bills=0, domain_rejections=0)
    for q in range(2,8):
        for k in range(1,20):
            for n in [k**q-1,k**q,k**q+1]:
                v=nthroot(n,q)
                require(v**q <= n < (v+1)**q,'integer root bracket')
                counts['root_controls'] += 1
    exponents = [F(1,4),F(1,3),F(1,2),F(2,3),F(3,4)]
    for t in exponents:
        for T in map(F,[1,2,5]):
            for a in [0,T/4,T/2,3*T/4]:
                for b in [T,5*T/4,2*T,4*T]:
                    points=[a+(T-a)*F(j,8) for j in range(1,8)]
                    for x,y in zip(points,points[1:]):
                        delta=sub(mul(h(a,b,y,t),h(0,T,x,t)),
                                  mul(h(a,b,x,t),h(0,T,y,t)))
                        if a == 0 and b == T:
                            require(delta[0] <= 0 <= delta[1], 'identity ratio')
                        else:
                            positive(delta, 'ordered interval ratio')
                        counts['ratio_comparisons'] += 1
            for m in range(1,6):
                paths=[(T*F(i+1,2*m+2),T*(1+F(i+1,4))) for i in range(m)]
                valid(T,paths,t)
                A=max(a for a,b in paths)
                points=[A+(T-A)*F(j,8) for j in range(1,8)]
                for x,y in zip(points,points[1:]):
                    positive(normalized_difference(T,paths,x,y,t), 'normalized bill order')
                    counts['normalized_bill_comparisons']+=1
                positive((-bill(T,paths,T,t)[1],-bill(T,paths,T,t)[0]), 'crossing terminal negative')
                counts['endpoint_bills']+=1
                zeros=[(F(0),b) for a,b in paths]
                for x in [T/4,T/2,3*T/4]:
                    require(bill(T,zeros,x,t)[1] < 0,'zero-start exclusion')
                    counts['zero_start_bills']+=1
            # Positive bill at left, crossing to negative before terminal.
            paths=[(T/2,2*T)]
            positive(bill(T,paths,T/2,t),'positive left endpoint')
            counts['endpoint_bills']+=1
            # Exact zero family and degenerate feasible interval.
            for x in [F(0),T/3,T]:
                z=bill(T,[(F(0),T)],x,t)
                require(z[0]<=0<=z[1], 'zero family')
            z=bill(T,[(T,T)],T,t)
            require(z[0] <= 0 <= z[1], 'singleton interval enclosure')
    bad=[(F(0),[(0,1)],F(1,2)),(F(1),[],F(1,2)),
         (F(1),[(0,1)],F(0)),(F(1),[(0,1)],F(1)),
         (F(1),[(F(-1),F(2))],F(1,2)),
         (F(1),[(0,F(1,2))],F(1,2)),
         (F(1),[(F(2),F(3))],F(1,2))]
    for args in bad:
        try:
            valid(*args)
        except ValueError:
            counts['domain_rejections']+=1
        else:
            raise ValueError('invalid domain admitted')
    # Test the strict inequality gate itself with a reversed exact interval.
    try:
        positive((F(-2),F(-1)), 'reversed inequality control')
    except ValueError:
        counts['domain_rejections']+=1
    else:
        raise ValueError('reversed inequality admitted')
    pins=json.loads((ROOT/'SOURCE-PINS.json').read_text(encoding='utf-8'))
    require(pins['predecessor_head']=='e5383f5c2973c9520918cbe6ebe9c6e6867e5771','source head')
    raw=(ROOT/'sources/pr7331-PROOF.md').read_bytes()
    require(sha256(raw).hexdigest()==pins['proof_sha256'],'retained predecessor bytes')
    print(json.dumps({'status':'PASS_PROPER_TERMINAL_SIGN_CRITERION',
                     'counts':counts,'exponents':[str(t) for t in exponents],
                     'scope':'finite exact corroboration, not the universal proof'},sort_keys=True))


if __name__=='__main__':
    main()
