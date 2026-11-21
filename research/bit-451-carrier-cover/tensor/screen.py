"""One prospective p=23 coefficient certificate. CPython 3.12, standard library."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import signal
import sys
import tarfile
from time import monotonic

V, P, H0 = 451, 23, 1804
A, B, SLOPE = F(7,6), F(319,100), F(23,20)
BIT_PIN = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
PRIOR_PIN = "69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818"

def pinned(path,pin,archive=False):
    if archive and path.suffix != ".json":
        with tarfile.open(path,"r:*") as bundle:
            with bundle.extractfile("package-sanitized/BIT-451.json") as stream:
                data = stream.read()
    else:
        data = path.read_bytes()
    if sha256(data).hexdigest()!=pin:
        raise ValueError("incorrect pinned input: "+path.name)
    return json.loads(data)

def screen(bit,prior,receipt):
    eta = F(bit["uniform"]["eta"][0])
    eps = F(prior["epsilon_upper"])
    sep = bit["separation"]
    eps_required = F(sep["paid_uplift_upper"][1])/F(sep["three_engine_intervals"]["source_1"]["alpha"][0])**V
    paid = bit["native"]["paid"]
    if not (len(paid)==14 and sum(paid.values())==107460 and max(map(int,paid)) <= 11**2
            and eps>=eps_required>=0 and F(sep["trial"])==F("0.003879928046148")
            and 0 <= F(prior["mean_upper"]) < F(3,4)
            and (F(prior["mean_upper"])+eps)/(1+eps) <= F(3,4)):
        raise ValueError("raw support, full uplift, tilt or mean certificate mismatch")
    if not (prior["p_minimum"]==27 and int(prior["uniform_J"])==1061 and int(prior["h"])==H0):
        raise ValueError("wrong predecessor comparison")
    receipt["base_guard"] = F(H0+(134**V).bit_length()-1,H0)**P > F(bit["uniform"]["ambient_power"][1])
    receipt["limiting_upper"] = str((F(3,4)/SLOPE)**P)
    if not receipt["base_guard"] or F(receipt["limiting_upper"]) >= eta:
        return "fixed sufficient base or limiting comparison fails"
    # Price the invariant terminal, cover and seven-stage costs before building moments.
    horizon = bit["uniform"]["H"]
    loss = (((H0+horizon)**P)//(H0**P)).bit_length()
    if F(loss,horizon)*(horizon+H0) <= 2*P:
        return "terminal carrier conversion unresolved"
    covered = F(sep["trial"])-F(loss,horizon)-F(1,horizon*2**44)
    rho = F(bit["cover_and_stock"]["rho"])
    rate = F(bit["cover_and_stock"]["seed"])
    for _ in range(7):
        upper = (1-rho)*covered+rho*rate
        step = F(int(upper*10**24)-1,10**24)
        if not (rate < step < upper < covered and step < min(rho,1-rho)):
            return "ordinary stage could not be admitted"
        rate=step
    tick=F(1,10**14)
    cap = F(int(rate*10**17),10**17)
    claim = (cap//tick-8)*tick
    ceiling = F(bit["raw_crossing"][1])-F(int(prior["uniform_J"]),horizon)-7*tick
    receipt["prospective_price"] = {"loss":loss,"cap":str(cap),"claim":str(claim),
                                   "old_relaxed_ceiling":str(ceiling),"separation":str(claim-ceiling)}
    if claim <= ceiling or claim+7*tick >= cap:
        return "single-case directed price fails required separation"
    stir = [[0]*(P+1) for _ in range(P+1)]
    stir[0][0] = 1
    fall = [1]
    for n in range(1,P+1):
        fall.append(fall[-1]*(V+1-n))
        for j in range(1,n+1):
            stir[n][j] = j*stir[n-1][j]+stir[n-1][j-1]
    mu = [F(1)]
    for k in range(1,P+1):
        m = F(2,V)**k * sum(stir[k][j]*fall[j]*F(3,8)**j for j in range(1,k+1))
        mu.append((min(1,m)+eps)/(1+eps))
    mu[1] = min(mu[1],F(3,4))
    receipt["moments"] = [str(x) for x in mu]
    shift = [sum(comb(i,k)*A**(i-k)*mu[k] for k in range(i+1)) for i in range(P+1)]
    bell = [[F(0)]*(P+1) for _ in range(P+1)]
    bell[0][0]=1
    for n in range(1,P+1):
        for j in range(1,n+1):
            bell[n][j] = sum(comb(n-1,i-1)*mu[i]*bell[n-i][j-1] for i in range(1,n-j+2))
    receipt["ratios"] = {}
    for j in [0,P]+list(range(1,P)):
        num = sum(comb(P,i)*shift[P-i]*bell[i][j] for i in range(j,P+1))
        den = sum(comb(P,i)*B**(P-i)*SLOPE**i*stir[i][j] for i in range(j,P+1))
        receipt["ratios"][str(j)] = str(num/den)
        if num >= eta*den:
            return "single coefficient certificate fails; all-height and native feasibility unresolved"
    return "all-height component and projected price pass; independent proof and complete consumer required"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-source",type=Path,required=True)
    parser.add_argument("--round336-receipt",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if sys.version_info[:2]!=(3,12) or sys.implementation.name!="cpython":
        parser.error("CPython 3.12 required")
    if args.out.exists():
        parser.error("provide a new output path")
    receipt={"p":P,"h":H0,"cap_seconds":60,"max_coefficients":P+1,
             "source_sha256":{"BIT-451.json":BIT_PIN,"round336/independent/receipt.json":PRIOR_PIN}}
    def stop(*_):
        raise TimeoutError("60-second cap")
    signal.signal(signal.SIGALRM,stop)
    start=monotonic()
    signal.alarm(60)
    try:
        receipt["decision"]=screen(pinned(args.bit_source,BIT_PIN,True),pinned(args.round336_receipt,PRIOR_PIN),receipt)
    except TimeoutError:
        receipt["decision"]="CAPPED; unresolved"
    finally:
        signal.alarm(0)
    receipt["elapsed_seconds"]=monotonic()-start
    with args.out.open("x") as stream:
        json.dump(receipt,stream,indent=2)
        stream.write("\n")
    print(receipt["decision"])
    return 2 if receipt["decision"].startswith("CAPPED") else 0

if __name__=="__main__":
    raise SystemExit(main())
