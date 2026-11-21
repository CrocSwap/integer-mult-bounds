#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One normalized majorant on the authenticated 768-factor compiler."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

PINS = {
    "ordinary/BINARY.json": "f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4",
    "ordinary/REPLAY.json": "419d4bdfb95c4484d0ddc81f34c89ee45bdefc0955a85dd496c1043396260e37",
    "peer/APPLICATION.json": "587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
    "peer/APPLICATION-SOURCES.tar.gz": "d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
    "peer/BINARY-CANDIDATE.json.gz": "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
}


def check(cond, what):
    if not cond:
        raise ValueError(what)


def decimal(q, places):
    n = q * 10**places
    check(n.denominator == 1 and n > 0, "decimal not on declared grid")
    a, b = divmod(n.numerator, 10**places)
    return f"{a}.{b:0{places}d}"


def price(covered, seed, rho, rational):
    previous = seed
    rows = []
    for _ in range(4):
        bound = (1-rho)*covered + rho*previous
        admitted = Q((bound*10**15).__floor__() - 1, 10**15)
        check(previous < admitted < bound < rho < 1-bound, "all strict paid stage terms")
        rows.append({"old":str(previous), "envelope":str(bound),
                     "admitted":decimal(admitted,15), "slack":str(bound-admitted)})
        previous = admitted
    grid = (min(rational, previous)*10**14).__floor__() - 8
    claim, tested = Q(grid,10**14), Q(grid+7,10**14)
    check(claim < tested < previous < rational, "complete signed grid and binding limit")
    return {"stages":rows, "covered":str(covered), "cap":decimal(previous,15),
            "claim":decimal(claim,14), "tested":decimal(tested,14)}


def solve(args):
    raw = {}
    for key, expected in sorted(PINS.items()):
        namespace, name = key.split("/")
        data = (getattr(args, namespace) / name).read_bytes()
        check(sha256(data).hexdigest() == expected, key)
        if name.endswith(".json"):
            raw[key] = json.loads(data)
    binary = raw["ordinary/BINARY.json"]
    signed = raw["ordinary/REPLAY.json"]
    peer = raw["peer/APPLICATION.json"]
    base = binary["peer_finite"]
    comp = base["independent_directed_compiler"]
    sep = base["finite_separation"]
    H,p,h = comp["H"],comp["logarithm_power"],1024
    theta, C = Q(comp["theta"]),Q(comp["trial"])
    t, v = 1-C,comp["product_exponent"]
    a,r,k = comp["ambient_base"],comp["cutoff"],comp["productive_floor"]
    check((H,p,theta,v,a,r,k,C)==(299610000000000,623,Q(42,43),768,134,15,16,Q("0.003890115276594")), "fixed case")
    check(base["uniform"]["H"]==H and base["uniform"]["logarithm_power"]==p and Q(base["uniform"]["theta"])==theta, "both source compilers")
    check(signed["source_archive"]==PINS["peer/APPLICATION-SOURCES.tar.gz"] and signed["source_count"]==134, "signed closure")
    check(comp["N"]==f"2^{H}" and Q(sep["strict_normalized_gap"]["lower"])>0, "separated moment and exact carrier")
    check(sep["targets"]["64"]>0 and sep["targets"]["8"]>0 and 256+512==v and 64**256*8**512==k**v, "literal productive floor")
    check(r**43 < k**42 and (1<<h)*r**(43*v) <= a**(42*v), "all-exit and normalized shift")
    # Bound A^C by one small rational integer power. This also validates
    # the exit capacity without relying on the producer's transcendental code.
    u = (v*C*10000).__ceil__()
    base_upper = 2267000
    check(0<v*C<=Q(u,10000) and a**u < base_upper**10000, "directed ordinary base upper")
    check(theta**p < t/base_upper, "directed exit capacity for all sources")
    check(2**(7*v)<a**v and (1+Q(7*v,h))**p>base_upper, "all ordinary base ranks by concavity")
    num,den=(H+h)**p,h**p
    J = (num//den).bit_length()
    check(den*(1<<(J-1))<=num<den*(1<<J), "adjacent terminal integers")
    check((H+h)*J>2*H*p, "positive derivative for every log-rank at least H")
    loss=Q(J,H)
    old_loss=Q(base["uniform_loss"])
    d=Q(binary["delayed_cover_debit"])
    check(d==Q(1,H*2**38) and H*d/2==Q(64,2**45) and base["cover_prime_condition"].startswith("odd q > 2^45*N^5"), "unchanged strict cover")
    seed=Q(base["ordinary_bootstrap"][0]["previous"])
    rho=Q(base["rho"])
    raw_low,raw_high=map(Q,peer["binary_raw"])
    rational=Q(peer["rational_raw"][0])
    check(seed==Q(".00385248") and rho==Q(1,250) and C==raw_low-Q(1,10**11) and old_loss==Q(1,10**10), "stock and original trial")
    old=price(C-old_loss-d,seed,rho,rational)
    check([x["admitted"] for x in old["stages"]]==[x["claim"] for x in binary["candidate_stages"]], "unchanged original four stages")
    check(all(old[field]==signed[field] for field in ("claim","tested","cap")), "reproduce full R347 control")
    new=price(C-loss-d,seed,rho,rational)
    old_upper=raw_high-old_loss
    diff=Q(new["claim"])-Q(old["claim"])
    check(0 < d < loss < old_loss and Q(new["claim"]) > old_upper+Q(1,10**11), "fixed whole-price target")
    return {"decision":"ADVANCE_ONE_COMPLETE_SIGNED_REPLAY", "pins":dict(sorted(PINS.items())),
            "peer_head":signed["peer_head"],"word":peer["binary_word"],"caller":signed["caller"],
            "h":h,"p":p,"theta":str(theta),"H":H,"J":J,"base_upper":base_upper,
            "base_exponent_upper":str(Q(u,10000)), "eta_lower":str(t/base_upper),
            "trial":str(C),"seed":str(seed),"rho":str(rho),"uniform_loss":str(loss),
            "cover_loss":str(d),"floor_factors":{"8":512,"64":256}, "comparator":old,
            "candidate":new,"old_relaxed_ceiling":str(old_upper),
            "separation":str(Q(new["claim"])-old_upper),"absolute_gain":str(diff),
            "relative_percent":str(100*diff/Q(old["claim"]))}


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--peer",type=Path,required=True)
    a.add_argument("--ordinary",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    check(sys.version_info[:2]==(3,12), "CPython 3.12 required")
    result=solve(args)
    with args.out.open("x") as f:
        json.dump(result,f,indent=2,sort_keys=True)
        f.write("\n")
    print("PASS_NORMALIZED_768_PRICE",result["J"],result["candidate"]["cap"],result["candidate"]["claim"],result["candidate"]["tested"])


if __name__=="__main__":
    main()
