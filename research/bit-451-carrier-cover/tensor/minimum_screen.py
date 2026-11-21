"""R338 prospective: control p20 by its limit, price and screen only p21."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import signal
import sys
import tarfile
from time import monotonic

BIT = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
OLD = "288e194853bb736973600eb51da2983414679a185629c30f769d701f4c55e811"
P, H_SHIFT, HEIGHTS = 21, 1804, 64
A, B, BETA = F(7,6), F(319,100), F(23,20)

def read(path, digest, archive=False):
    if archive and path.suffix != ".json":
        with tarfile.open(path,"r:*") as bundle:
            with bundle.extractfile("package-sanitized/BIT-451.json") as stream:
                blob=stream.read()
    else:
        blob=path.read_bytes()
    if sha256(blob).hexdigest()!=digest:
        raise ValueError("input fingerprint mismatch: "+path.name)
    return json.loads(blob)

def price(data, previous):
    H=data["uniform"]["H"]
    num, den = (H+H_SHIFT)**P,H_SHIFT**P
    J=(num//den).bit_length()
    if not (den<<(J-1)) <= num < (den<<J) or F(J,H)*(H+H_SHIFT) <= 2*P:
        raise ValueError("terminal loss proof fails")
    covered=F(data["separation"]["trial"])-F(J,H)-F(1,H*2**44)
    stock=data["cover_and_stock"]
    rate, rho=F(stock["seed"]), F(stock["rho"])
    stages=[]
    for _ in range(7):
        upper=(1-rho)*covered+rho*rate
        step=F(int(upper*10**24)-1,10**24)
        if not (rate<step<upper<covered and step<min(rho,1-rho)):
            raise ValueError("ordinary stage guard fails")
        stages.append(str(step))
        rate=step
    cap=F(int(rate*10**17),10**17)
    tick=F(1,10**14)
    claim=(cap//tick-8)*tick
    tested=claim+7*tick
    ceiling=F(data["raw_crossing"][1])-F(previous["uniform_J"],H)-7*tick
    old=F(previous["candidate_grid_claim"])
    return {"J":J,"covered":str(covered),"stages":stages,"cap":str(cap),
            "claim":str(claim),"tested":str(tested),"old_relaxed_ceiling":str(ceiling),
            "separation":str(claim-ceiling),"change":str(claim-old),"passes":old<ceiling<claim<tested<cap}

def newton(mu):
    # #4480 partial Bell expansion converted to forward differences by j!.
    shift=[sum(comb(i,k)*A**(i-k)*mu[k] for k in range(i+1)) for i in range(P+1)]
    bell=[[F(0)]*(P+1) for _ in range(P+1)]
    stir=[[0]*(P+1) for _ in range(P+1)]
    bell[0][0]=stir[0][0]=1
    for n in range(1,P+1):
        for j in range(1,n+1):
            stir[n][j]=j*stir[n-1][j]+stir[n-1][j-1]
            bell[n][j]=sum(comb(n-1,k-1)*mu[k]*bell[n-k][j-1] for k in range(1,n-j+2))
    ns,ds=[],[]
    for j in range(P+1):
        ns.append(factorial(j)*sum(comb(P,i)*shift[P-i]*bell[i][j] for i in range(j,P+1)))
        ds.append(factorial(j)*sum(comb(P,i)*B**(P-i)*BETA**i*stir[i][j] for i in range(j,P+1)))
    return ns,ds

def screen(data,prior,out):
    if (prior["p"],prior["h"],prior["uniform_J"],prior["pins"]["BIT-451.json"]) != (23,H_SHIFT,904,BIT):
        raise ValueError("wrong precursor")
    mu=list(map(F,prior["moments"][:P+1]))
    if len(mu)!=P+1 or mu[:2]!=[1,F(3,4)]:
        raise ValueError("wrong moment prefix")
    lo,hi=map(F,data["uniform"]["eta"])
    if lo!=F(prior["eta_lower"]) or not (0 < lo <= hi < 1):
        raise ValueError("wrong eta enclosure")
    q=mu[1]/BETA
    if not 0<q<1:
        raise ValueError("limiting monotonicity missing")
    limit20=q**20
    excluded=limit20>hi
    out.update(eta_lower=str(lo),eta_upper=str(hi),limit_at_20=str(limit20),
               all_positive_p_through_20_excluded_for_this_envelope=excluded)
    limit21=q**P
    out.update(limit_at_21=str(limit21),
               sufficient_base_pass=F(H_SHIFT+(134**451).bit_length()-1,H_SHIFT)**P>F(data["uniform"]["ambient_power"][1]))
    if not out["sufficient_base_pass"]:
        return "fixed sufficient base guard fails at p21"
    if limit21>=hi:
        return "p21 formal envelope fails at its limit"
    if limit21>=lo:
        return "p21 limiting comparison unresolved inside eta enclosure"
    out["price"]=price(data,prior)
    if not out["price"]["passes"]:
        return "p21 complete projected price fails the required old-ceiling separation"
    ns,ds=newton(mu)
    if not (all(n>=0 for n in ns) and all(d>0 for d in ds) and ns[-1]/ds[-1]==limit21):
        raise ValueError("inconsistent Newton coefficients")
    out["initial_coefficient_ratios"]=[str(n/d) for n,d in zip(ns,ds)]
    # All differences are shifted together; these are the same 22 coefficients.
    largest_prefix=F(0)
    for g in range(HEIGHTS):
        point=ns[0]/ds[0]
        peak=max(n/d for n,d in zip(ns,ds))
        out["visited"].append({"g":g,"ratio":str(point),"largest_coefficient_ratio":str(peak)})
        if point>=hi:
            return "p21 formal envelope fails at a finite height, including eta enclosure"
        uniform=max(largest_prefix,peak)
        if uniform<lo:
            out["shift"]=g
            out["uniform_lambda"]=str((uniform+lo)/2)
            return ("p21 is the minimum admissible positive integer for this fixed envelope"
                    if excluded else "p21 is sufficient; minimality unresolved")
        largest_prefix=max(largest_prefix,point)
        ns=[x+y for x,y in zip(ns,ns[1:]+[0])]
        ds=[x+y for x,y in zip(ds,ds[1:]+[0])]
    return "CAPPED after heights 0 through 63; exact uniform comparison unresolved"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-source",type=Path,required=True)
    parser.add_argument("--round337-receipt",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if sys.version_info[:2]!=(3,12) or sys.implementation.name!="cpython":
        parser.error("CPython 3.12 required")
    if args.out.exists():
        parser.error("use a new receipt path")
    out={"candidate_p":P,"limiting_control_p":20,"h":H_SHIFT,"cap_seconds":60,
         "maximum_explicit_heights":HEIGHTS,"coefficients":P+1,"visited":[],
         "inputs":{"BIT-451.json":BIT,"round337/independent/receipt.json":OLD}}
    def stop(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM,stop)
    start=monotonic()
    signal.alarm(60)
    try:
        out["decision"]=screen(read(args.bit_source,BIT,True),read(args.round337_receipt,OLD),out)
    except TimeoutError:
        out["decision"]="CAPPED at 60 seconds; unvisited scope unresolved"
    finally:
        signal.alarm(0)
    out["elapsed_seconds"]=monotonic()-start
    with args.out.open("x") as stream:
        json.dump(out,stream,indent=2)
        stream.write("\n")
    print(out["decision"])
    return 2 if out["decision"].startswith("CAPPED") else 0

if __name__=="__main__":
    raise SystemExit(main())
