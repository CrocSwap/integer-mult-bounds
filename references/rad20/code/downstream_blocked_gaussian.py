#!/usr/bin/env python3
"""Exact prototype and finite checks for local chirp Gaussian convolution.

The complexity theorem uses a known unconditional fast integer multiplier;
Python's built-in multiplier here is only an exact finite witness backend.
No floating-point arithmetic is used for acceptance or error thresholds.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import isqrt, lcm
from pathlib import Path
import time

from downstream_gaussian import BASELINE_KAPPA, assembly_witness, ceil_q, require


def floor_q(x: Q) -> int:
    return x.numerator//x.denominator


def ceil_sqrt_q(x: Q) -> int:
    r = isqrt(x.numerator//x.denominator)
    return r if r*r*x.denominator == x.numerator else r+1


def pow2(x: int) -> Q:
    return Q(2**x) if x >= 0 else Q(1,2**(-x))


def chirp_exponents(A: Q, B: Q, gamma: Q, c: Q,
                    h: int, v: int) -> tuple[Q,Q,Q,Q]:
    mu = A*B
    U = c*((A*A-mu)*h*h+2*gamma*A*h+gamma*gamma)
    V = c*((B*B-mu)*v*v-2*gamma*B*v)
    K = c*mu*(h-v)**2
    direct = c*(gamma+A*h-B*v)**2
    require(U+V+K == direct, "Chirp factorization failed")
    require(K >= 0, "Toeplitz kernel exceeds one")
    return U,V,K,direct


def nonnegative_convolution(a: list[int], b: list[int]) -> tuple[list[int],int]:
    require(a and b and min(a+b) >= 0, "Invalid nonnegative polynomial")
    slot = max(1,max(a).bit_length()+max(b).bit_length()+min(len(a),len(b)).bit_length()+1)
    pa = sum(x << (slot*i) for i,x in enumerate(a))
    pb = sum(x << (slot*i) for i,x in enumerate(b))
    pc = pa*pb
    mask = (1 << slot)-1
    result = [(pc >> (slot*i)) & mask for i in range(len(a)+len(b)-1)]
    return result,slot


def signed_integer_convolution(a: list[int], b: list[int]) -> tuple[list[int],dict]:
    ap,an = [max(x,0) for x in a],[max(-x,0) for x in a]
    bp,bn = [max(x,0) for x in b],[max(-x,0) for x in b]
    pp,s1 = nonnegative_convolution(ap,bp)
    nn,s2 = nonnegative_convolution(an,bn)
    pn,s3 = nonnegative_convolution(ap,bn)
    np,s4 = nonnegative_convolution(an,bp)
    result = [x+y-z-w for x,y,z,w in zip(pp,nn,pn,np)]
    reference = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            reference[i+j] += x*y
    require(result == reference, "Packed convolution disagrees with direct reference")
    return result,{"max_slot_bits":max(s1,s2,s3,s4),
                   "max_integer_coefficient_bits":max(abs(x).bit_length() for x in result)}


def dyadic_convolution(a: list[Q], b: list[Q]) -> tuple[list[Q],dict]:
    for x in a+b:
        require(x.denominator & (x.denominator-1) == 0, "Non-dyadic coefficient")
    af = max(x.denominator.bit_length()-1 for x in a)
    bf = max(x.denominator.bit_length()-1 for x in b)
    ai = [int(x*2**af) for x in a]
    bi = [int(x*2**bf) for x in b]
    values,metadata = signed_integer_convolution(ai,bi)
    return [Q(x,2**(af+bf)) for x in values],metadata


def surrogate_block(A: Q, B: Q, gamma: Q, c: Q,
                    hlo: int, hhi: int, outputs: int) -> dict:
    hs,vs = list(range(hlo,hhi+1)),list(range(outputs))
    u = {h:Q((7*h+5)%13-6,8) for h in hs}
    triples = [chirp_exponents(A,B,gamma,c,h,v) for h in hs for v in vs]
    denominator = lcm(*(x.denominator for row in triples for x in row))
    def weight(f: Q) -> Q:
        exponent = -denominator*f
        require(exponent.denominator == 1, "Surrogate exponent is not integral")
        return pow2(int(exponent))
    input_sequence = [weight(chirp_exponents(A,B,gamma,c,h,0)[0])*u[h] for h in hs]
    dmin,dmax = -hhi,outputs-1-hlo
    kernel = [weight(c*A*B*d*d) for d in range(dmin,dmax+1)]
    product,metadata = dyadic_convolution(input_sequence,kernel)
    result = []
    for v in vs:
        output_weight = weight(chirp_exponents(A,B,gamma,c,0,v)[1])
        actual = output_weight*product[v-hlo-dmin]
        expected = sum((weight(c*(gamma+A*h-B*v)**2)*u[h] for h in hs),Q(0))
        require(actual == expected, "Blocked surrogate differs from exact Gaussian reference")
        result.append(actual)
    payload = "\n".join(str(x) for x in result).encode()
    return {"A":str(A),"B":str(B),"gamma":str(gamma),"c":str(c),
            "h_range":[hlo,hhi],"outputs":outputs,"exponent_multiplier":denominator,
            "output_sha256":hashlib.sha256(payload).hexdigest(),"packing":metadata,
            "status":"PASS exact dyadic Gaussian-surrogate block"}


def interval_round(lo: Q, hi: Q, bits: int) -> tuple[Q,Q]:
    denominator = 2**bits
    return Q(floor_q(lo*denominator),denominator),Q(ceil_q(hi*denominator),denominator)


def atan_interval(x: Q, bits: int) -> tuple[Q,Q]:
    require(0 < x < 1, "Invalid Machin argument")
    total,power,n = Q(0),x,0
    tolerance = Q(1,2**bits)
    while True:
        total += (-1)**n*power/Q(2*n+1)
        n += 1
        power *= x*x
        next_term = (-1)**n*power/Q(2*n+1)
        if abs(next_term) < tolerance:
            return min(total,total+next_term),max(total,total+next_term)


def pi_interval(bits: int) -> tuple[Q,Q]:
    l1,h1 = atan_interval(Q(1,5),bits+8)
    l2,h2 = atan_interval(Q(1,239),bits+8)
    lo,hi = 16*l1-4*h2,16*h1-4*l2
    require(3 < lo < hi < 4, "Machin pi enclosure failed")
    return interval_round(lo,hi,bits)


def exp_interval(x: Q, bits: int) -> tuple[Q,Q]:
    if x == 0:
        return Q(1),Q(1)
    if x < 0:
        if -x > bits+8:
            return Q(0),Q(1,2**floor_q(-x))
        lo,hi = exp_interval(-x,bits+8+4*ceil_q(-x))
        return interval_round(1/hi,1/lo,bits)
    reduction = 0
    y = x
    while y > Q(1,8):
        reduction += 1
        y /= 2
    work_bits = bits+32+2*reduction+4*ceil_q(x)
    total,term,n = Q(1),Q(1),0
    while True:
        n += 1
        term *= y/n
        total += term
        next_term = term*y/(n+1)
        tail = next_term/(1-y/(n+2))
        if tail < Q(1,2**(work_bits+8)):
            break
    lo,hi = interval_round(total,total+tail,work_bits)
    for _ in range(reduction):
        lo,hi = interval_round(lo*lo,hi*hi,work_bits)
    lo,hi = interval_round(lo,hi,bits)
    require(hi-lo <= Q(2,2**bits), "Exponential enclosure too wide")
    return lo,hi


def gaussian_interval(f: Q, pi_bounds: tuple[Q,Q], bits: int,
                      scale: int = 0) -> tuple[Q,Q]:
    pl,ph = pi_bounds
    xl,xh = sorted([-pl*f,-ph*f])
    low,_ = exp_interval(xl,bits+8)
    _,high = exp_interval(xh,bits+8)
    return low/2**scale,high/2**scale


def interval_block(A: Q, B: Q, gamma: Q, c: Q,
                   hlo: int, hhi: int, outputs: int, target_bits: int) -> dict:
    hs,vs = list(range(hlo,hhi+1)),list(range(outputs))
    exponents = [chirp_exponents(A,B,gamma,c,h,v) for h in hs for v in vs]
    max_growth = max(Q(0),*[-row[i] for row in exponents for i in (0,1)])
    sigma = ceil_q(8*max_growth)+1
    P = 2*sigma+target_bits+(100*len(hs)**2).bit_length()+24
    maximum_f = max(abs(f) for row in exponents for f in row)
    pi_bounds = pi_interval(P+8*ceil_q(maximum_f)+32)
    u = {h:Q((7*h+5)%13-6,8) for h in hs}
    epsilon = Q(1,2**P)
    cache = {}
    def rounded_weight(f: Q, scaled: bool) -> Q:
        key = (f,scaled)
        if key not in cache:
            lo,hi = gaussian_interval(f,pi_bounds,P,scale=sigma if scaled else 0)
            require(hi-lo < epsilon, "Factor interval has insufficient precision")
            cache[key] = Q(floor_q(lo/epsilon),2**P)
        return cache[key]
    input_sequence = [rounded_weight(chirp_exponents(A,B,gamma,c,h,0)[0],True)*u[h] for h in hs]
    dmin,dmax = -hhi,outputs-1-hlo
    kernel = [rounded_weight(c*A*B*d*d,False) for d in range(dmin,dmax+1)]
    product,metadata = dyadic_convolution(input_sequence,kernel)
    max_error = Q(0)
    for v in vs:
        V = rounded_weight(chirp_exponents(A,B,gamma,c,0,v)[1],True)
        actual = V*product[v-hlo-dmin]*2**(2*sigma)
        lower,upper = Q(0),Q(0)
        for h in hs:
            lo,hi = gaussian_interval(c*(gamma+A*h-B*v)**2,pi_bounds,P)
            endpoints = sorted([u[h]*lo,u[h]*hi])
            lower += endpoints[0]
            upper += endpoints[1]
        error = max(abs(actual-lower),abs(actual-upper))
        require(error < Q(1,2**(target_bits+8)), "Rigorous Gaussian block accuracy failed")
        max_error = max(max_error,error)
    return {"status":"PASS rigorous rational-interval Gaussian block",
            "A":str(A),"B":str(B),"gamma":str(gamma),"c":str(c),
            "h_range":[hlo,hhi],"outputs":outputs,"target_bits":target_bits,
            "work_bits":P,"input_output_scale_bits":sigma,
            "max_error_upper":str(max_error),"factor_evaluations":len(cache),"packing":metadata}


def check_bounds() -> dict:
    cases,identities,max_ratio = 0,0,Q(0)
    for p in [101,127,128,255,256,1024,1025]:
        for alpha in sorted({2,3,max(2,isqrt(p)-1)}):
            require(alpha*alpha < p, "Invalid sample Gaussian width")
            for s,t in [(97,98),(97,129),(97,193),(99991,99992)]:
                rho,kappa = Q(t,s),Q(s,t)
                for mode in ["S","T"]:
                    block = ceil_sqrt_q(Q(p))*alpha if mode == "S" else ceil_sqrt_q(Q(p,alpha*alpha))
                    for k0 in sorted({0,min(t-1,block),max(0,t-block),t-1}):
                        if mode == "S":
                            j0 = floor_q(kappa*k0)
                            gamma = Q(j0)-kappa*k0
                            hlo = floor_q(kappa*k0)-block-1-j0
                            hhi = ceil_q(kappa*(k0+block-1))+block+1-j0
                            A,B,c = Q(1),kappa,Q(1,alpha*alpha)
                        else:
                            j0 = floor_q(Q(k0)/rho)
                            gamma = rho*j0-k0
                            radius = block+2
                            hlo = floor_q(Q(k0-radius)/rho)-1-j0
                            hhi = ceil_q(Q(k0+block-1+radius)/rho)+1-j0
                            A,B,c = rho,Q(1),Q(alpha*alpha)
                        hs = sorted({hlo,hhi,0,max(hlo,min(hhi,-1)),max(hlo,min(hhi,1))})
                        vs = sorted({0,block-1,block//2})
                        for h in hs:
                            for v in vs:
                                U,V,K,_ = chirp_exponents(A,B,gamma,c,h,v)
                                # Fold D into the T input diagonal: worst-case
                                # beta^2 <= 1/4.  This only enlarges this bound.
                                bound_values = [abs(U),abs(V),K]
                                if mode == "T":
                                    bound_values.append(abs(U)+Q(alpha*alpha,4))
                                ratio = max(bound_values)/p
                                require(ratio <= 512, "Scalar exponent exceeds universal work-precision bound")
                                max_ratio = max(max_ratio,ratio)
                                identities += 1
                        require(hhi-hlo+1 <= 16*p, "Block input span is not O(p)")
                        cases += 1
    for p in [101,128,1024,2**40]:
        sigma,work = 4096*p,32768*p
        require((128*p*p).bit_length() < work-2*sigma-p-10,
                "Universal error-amplification margin failed")
    return {"status":"PASS exact exponent and precision comparisons",
            "blocks":cases,"identity_checks":identities,
            "maximum_abs_exponent_without_pi_over_p":str(max_ratio),
            "universal_bound_without_pi":512,"sigma_per_p":4096,"work_precision_per_p":32768,
            "scope":"Selected boundary cases support the universal bounds derived in the report."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--skip-interval",action="store_true")
    args = parser.parse_args()
    start = time.monotonic()
    result = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
              "campaign_deadline":"2026-10-08T08:25:21Z",
              "exact_bounds":check_bounds(),
              "surrogate_blocks":[surrogate_block(Q(1),Q(3,4),Q(-1,4),Q(1,4),-2,3,3),
                                  surrogate_block(Q(4,3),Q(1),Q(-1,3),Q(9),-2,3,3),
                                  surrogate_block(Q(1),Q(9,10),Q(-1,10),Q(1,9),-3,4,4)],
              "interval_blocks":[],
              "assembly_witnesses":[
                  assembly_witness(509194,Q(296,10**11),"blocked chirp with unchanged upstream paired graph",
                                   epsilon=Q(499,1000),kappa=Q(5,2**60),gaussian_model="blocked-chirp"),
                  assembly_witness(494250,Q(305,10**11),"blocked chirp plus aligned global pair ordering",
                                   epsilon=Q(499,1000),kappa=Q(266,100)*BASELINE_KAPPA,gaussian_model="blocked-chirp")]}
    if not args.skip_interval:
        result["interval_blocks"] = [interval_block(Q(1),Q(3,4),Q(-1,4),Q(1,4),-2,3,3,16),
                                     interval_block(Q(4,3),Q(1),Q(-1,3),Q(9),-2,3,3,16)]
    result["elapsed_seconds"] = time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS",result["exact_bounds"]["identity_checks"],"chirp identities")
    print("PASS",len(result["surrogate_blocks"]),"exact dyadic convolutions")
    print("PASS",len(result["interval_blocks"]),"rigorous Gaussian interval blocks")


if __name__ == "__main__":
    main()
