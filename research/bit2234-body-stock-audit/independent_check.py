#!/usr/bin/env python3
"""Independent exact-product arithmetic audit; imports no other package code.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Finite coverage supplements the written proof; it does not establish the
physical caller contracts or extrapolate a universal theorem from a search.
"""
import json
from math import prod

M = 269241600
Q = 15 * 2**78 + 1
CUTOFF = 245773


def require(value, message):
    if not value:
        raise RuntimeError(message)


def depth(n):
    d = 0
    while n >= 64:
        n = 42 * (n // 64)
        d += 1
    return d


def reserve_upper(n, w):
    d = depth(n)
    return 4096 * w * d + (29*d + 79)//80


def feasible_upper(e, k):
    w = 1 if e == 1 else 2  # Used only in [1,2**20), where exact.
    return 0 <= k and 2*k < e and k >= reserve_upper((e-k)//w, w)


def least_upper(e):
    hi = (e-1)//2
    if not feasible_upper(e, hi):
        return None
    lo = 0
    while lo < hi:
        mid = (lo+hi)//2
        if feasible_upper(e, mid):
            hi = mid
        else:
            lo = mid+1
    return lo


require(Q > 2**80, 'prime domain')
require(pow(11, (Q-1)//2, Q) == Q-1, 'order certificate')
require((2**78+1)**2 > Q, 'order certificate exceeds square root')
require(2*Q**5 < M**15 < Q**6, 'boundary logarithmic strip')
require(2*Q**5 < M**16 < Q**6, 'cycle logarithmic strip')
require(32 < Q-1, 'P^16>1/2')

# Direct exact GL comparison, independent of the P/Bernoulli bound used in proof.
# |GL64(Fq)|=q^2016 product_(i=1)^64(q^i-1).
gl_factor = prod(Q**i - 1 for i in range(1,65))
for d in (15,16):
    numerator = (M * gl_factor)**d
    require(Q**(2080*d+5) < numerator < Q**(2080*d+6),
            'direct exact reserve strip')

thresholds=[0,64]
for _ in range(23):
    thresholds.append(64*((thresholds[-1]+41)//42))

# Independently propagated floor recurrence across the bounded width domain.
dynamic=[0]*(2**20)
for n in range(64,len(dynamic)):
    dynamic[n]=1+dynamic[42*(n//64)]
for d,b in enumerate(thresholds):
    if d and b<len(dynamic):
        require(dynamic[b-1]==d-1 and dynamic[b]==d, 'threshold controls')

last_bad=0
for e in range(1,2**20):
    w=1 if e==1 else 2
    k=(e-1)//2
    n=(e-k)//w
    d=dynamic[n]
    U=4096*w*d+(29*d+79)//80
    if U>k:
        last_bad=e
require(last_bad==CUTOFF-1, 'uniform guard cutoff')

starts=[CUTOFF]+[4*thresholds[d]-2 for d in range(16,19)]
ends=[e-1 for e in starts[1:]]+[2**20-1]
intervals=[]
for d,start,end in zip(range(15,19),starts,ends):
    U=8192*d+(29*d+79)//80
    require(dynamic[(start+2)//4]==d==dynamic[(end+2)//4], 'constant depth')
    require(2*U<start, 'strict fit')
    intervals.append([start,end,d,U,start-2*U])

require(least_upper(CUTOFF-1) is None, 'failure below cutoff')
require(least_upper(CUTOFF)==122886, 'least threshold witness')
require(least_upper(273158)==122887, 'jump witness')
require(depth((273158-122886)//2)==16, 'left side of jump')
require(depth((273158-122887)//2)==15, 'right side of jump')
require(depth((273158-131078)//2)==15, 'two cycle')

# Mutant controls: weak fit, a floor in the reserve logarithm, wrong body rounding.
e=CUTOFF-1
require((e//2)==122886 and reserve_upper((e-e//2)//2,2)==122886,
        'weak fit mutant accepts certified failure')
require(8192*15+(29*15)//80==(e-1)//2,
        'log-floor mutant accepts certified failure')
require(depth((300542+2)//4)==16 and depth(300542//4)==15,
        'body-rounding mutant misses threshold')

print(json.dumps({
    'marker':'PASS_INDEPENDENT_BODY_STOCK_AUDIT',
    'q':Q,'prime_certificate':{'base':11,'two_adic_exponent':78,'odd_factor':15},
    'cutoff':CUTOFF,'boundary':CUTOFF-1,'finite_coverage':[1,2**20-1],
    'intervals':intervals,
    'no_equality_example':{'e':273158,'least_feasible':122887,
        'cycle':[122886,131078]},
},sort_keys=True))
