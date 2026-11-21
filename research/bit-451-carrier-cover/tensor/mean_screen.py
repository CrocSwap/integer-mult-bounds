"""Prospective R339: one tighter raw/complete mean and exactly one p20 test."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import signal
import sys
from time import monotonic
from types import ModuleType

P, V, H_SHIFT = 20, 451, 1804
Q = F(749,1000)
HELPER = "2df053c036c3bf8c3f4f6deccdcdfa3d4821b3c801c6410fe0e377dba6149d23"
BIT = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
R336 = "69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818"
R338 = "2c7692f263da6ccaacb7054471aff9d8a693371e8dcb3b83390d70a7bcff4d10"

def predecessor(path):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != HELPER:
        raise ValueError("previous screen bytes differ")
    module = ModuleType("pinned_minimum")
    exec(compile(raw,str(path),"exec"),module.__dict__)
    if (module.P,module.H_SHIFT,module.BETA)!=(21,H_SHIFT,F(23,20)):
        raise ValueError("previous screen constants differ")
    # Both borrowed functions use P as their only variable degree; retain the
    # rest of the immutable source and specialize its private module to p=20.
    module.P=P
    return module

def screen(args, out):
    helper=predecessor(args.previous_screen)
    bit=helper.read(args.bit_source,BIT,True)
    grid=helper.read(args.round336_receipt,R336)
    old=helper.read(args.round338_receipt,R338)
    if (old["p"],old["h"],old["uniform_J"],old["pins"]["BIT-451.json"],old["pins"]["grid/RESULT.json"])!=(21,H_SHIFT,825,BIT,R336):
        raise ValueError("incorrect predecessor")
    paid=bit["native"]["paid"]
    if len(paid)!=14 or sum(paid.values())!=107460 or max(map(int,paid))>=11**2:
        raise ValueError("raw source support differs")
    section=bit["separation"]
    if F(section["trial"])!=F("0.003879928046148"):
        raise ValueError("wrong source paid tilt")
    raw_hi=F(grid["mean_upper"])
    eps=F(grid["epsilon_upper"])
    raw_mass=F(section["three_engine_intervals"]["source_1"]["alpha"][0])**V
    if not (eps==F(old["epsilon_upper"]) and 0<=F(section["paid_uplift_upper"][1])<=eps*raw_mass):
        raise ValueError("full paid surcharge mismatch")
    complete_hi=(raw_hi+eps)/(1+eps)
    out.update(raw_mean_upper=str(raw_hi),complete_mean_upper=str(complete_hi),
               full_positive_surcharge_ratio_upper=str(eps))
    if not (0<=raw_hi<Q and complete_hi<Q):
        return "source fails to certify the fixed new raw or completed mean"
    eta_lo,eta_hi=map(F,bit["uniform"]["eta"])
    if (eta_lo,eta_hi)!=(F(old["eta_lower"]),F(old["eta_upper"])):
        raise ValueError("wrong capacity")
    limit=(Q/helper.BETA)**P
    out.update(limiting_ratio=str(limit),eta_lower=str(eta_lo),eta_upper=str(eta_hi))
    if limit>=eta_hi:
        return "fixed p20 upper-moment envelope fails at its limiting ratio"
    if limit>=eta_lo:
        return "p20 limit does not clear directed lower eta; unresolved inside enclosure"
    if F(H_SHIFT+(134**V).bit_length()-1,H_SHIFT)**P<=F(bit["uniform"]["ambient_power"][1]):
        return "fixed sufficient base guard fails"
    out["price"]=helper.price(bit,old)
    if not out["price"]["passes"]:
        return "fully charged projected p20 price does not clear required p21 ceiling"
    # One genuine rational comparison on *raw* factors: 2 times Bernoulli(Q/2).
    # After true clipping and completion, only separate moment upper bounds remain.
    probability=Q/2
    weights=[comb(V,k)*probability.numerator**k*(probability.denominator-probability.numerator)**(V-k)
             for k in range(V+1)]
    weight=probability.denominator**V
    if sum(weights)!=weight:
        raise ValueError("raw factor law mass mismatch")
    mu=[F(1),Q]
    for k in range(2,P+1):
        raw_moment=F(sum(w*(2*i)**k for i,w in enumerate(weights)),weight*V**k)
        mu.append((min(F(1),raw_moment)+eps)/(1+eps))
    out["moments"]=[str(x) for x in mu]
    ns,ds=helper.newton(mu)
    if len(ns)!=P+1 or any(d<=0 for d in ds) or ns[-1]/ds[-1]!=limit:
        raise ValueError("inconsistent coefficient sequence")
    out["coefficient_ratios"]={}
    for j in [P,0]+list(range(1,P)):
        out["coefficient_ratios"][str(j)]=str(ns[j]/ds[j])
        if ns[j]>=eta_lo*ds[j]:
            return "fixed coefficient test fails; formal all-height and actual law unresolved"
    peak=max(n/d for n,d in zip(ns,ds))
    out["uniform_lambda"]=str((peak+eta_lo)/2)
    return "all-height component and projected price pass; independent and complete replay required"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-source",type=Path,required=True)
    parser.add_argument("--round336-receipt",type=Path,required=True)
    parser.add_argument("--round338-receipt",type=Path,required=True)
    parser.add_argument("--previous-screen",type=Path,default=Path(__file__).resolve().parents[1]/"round337"/"next_minimum.py")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if sys.version_info[:2]!=(3,12) or sys.implementation.name!="cpython":
        parser.error("requires CPython 3.12")
    if args.out.exists():
        parser.error("provide a new receipt path")
    out={"p":P,"h":H_SHIFT,"new_mean":str(Q),"maximum_coefficients":P+1,"cap_seconds":60,
         "input_sha256":{"BIT-451.json":BIT,"round336/independent/receipt.json":R336,
                         "round338/independent/receipt.json":R338,"round337/next_minimum.py":HELPER}}
    def stop(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM,stop)
    start=monotonic()
    signal.alarm(60)
    try:
        out["decision"]=screen(args,out)
    except TimeoutError:
        out["decision"]="CAPPED; unvisited inequalities unresolved"
    finally:
        signal.alarm(0)
    out["runner_seconds"]=monotonic()-start
    with args.out.open("x") as stream:
        json.dump(out,stream,indent=2)
        stream.write("\n")
    print(out["decision"])
    return 2 if out["decision"].startswith("CAPPED") else 0

if __name__=="__main__":
    raise SystemExit(main())
