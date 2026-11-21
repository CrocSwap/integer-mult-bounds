# SPDX-License-Identifier: Apache-2.0
"""Use one previously certified paid-law ceiling in the fixed p=128 basis test."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import runpy
import sys

METHOD="e0961b875a7f4db9e53f4f2910cad969ea4bb86f0f453ec6ca13a2cb1d0e7559"
RECEIPT="0239f7f69dea671a66a37e3bcaae61c16d23dc794812d519d1c020821332ad36"


def check(flag, label):
    if not flag:
        raise ValueError(label)


def solve(args):
    check(sha256(args.predecessor_checker.read_bytes()).hexdigest()==METHOD,"predecessor checker")
    check(sha256(args.predecessor_price.read_bytes()).hexdigest()==RECEIPT,"predecessor exclusion")
    prev=json.loads(args.predecessor_price.read_bytes())
    auditor=runpy.run_path(str(args.predecessor_checker))
    for key,pin in auditor["PINS"].items():
        check(sha256(getattr(args,key).read_bytes()).hexdigest()==pin,"pinned source "+key)
    # Run the unmodified paid-law calculation only. Its prior coefficient scan
    # is separately authenticated; every new candidate comparison uses q=67/100.
    read=lambda p:json.loads(p.read_bytes())
    peer=read(args.application);prior=read(args.prior_price);signed=read(args.accept);b=read(args.binary)
    check(signed["outcome"]=="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE" and signed["claim"]==prior["claim"],"complete R348 control")
    native=peer["binary_native"]; P={int(r):n for r,n in native["paid_all"].items()};T={int(r):n for r,n in native["productive_all"].items()}
    sep=b["peer_finite"]["finite_separation"]
    check(native["paid_all"]==sep["paid"] and native["productive_all"]==sep["targets"]
          and 64**256*8**512==16**768 and min(T[64],T[8])>0,"signed product labels")
    C=F(b["peer_finite"]["tested_saving"]);t=1-C
    law=auditor["distribution"](T,P,t,sep)
    check(law==prev["law"] and F(law["completed_mean_upper"])<=F(67,100),"exact reusable mean")
    case=prev["case"];p,h,H=(case[k] for k in ("p","h","H"))
    check((p,h,H)==(128,1024,299610000000000) and case["q"]=="3/4"
          and prev["failed_coefficient"]==8 and len(prev["ratios"])==9,"scope of original failure")
    v=768;J=15**v;K=16**v;A=134**v
    check((1<<(20*h))<=J**7 and ((1<<h)*A)**10>=J**21 and K**50>=J**51 and 7*v>h and 8*v*C<p,"inherited uniform guards")
    old_ceiling=F(peer["binary_raw"][1])-F(23731,H)
    check(C-F(4992,H)-F(2,10**13)>old_ceiling+F(1,10**11),"fixed fully charged shortfall")
    eta=F(prev["eta_lower"])
    check(eta==F(b["peer_finite"]["uniform"]["eta"]["lower"])
          and F(prev["ratios"][8])>F(b["peer_finite"]["uniform"]["eta"]["upper"]),"known failure against upper capacity")
    S=[[1]]
    for i in range(1,p+1):
        last=S[-1]
        S.append([0]+[j*(last[j] if j<len(last) else 0)+last[j-1] for j in range(1,i+1)])
    num=[comb(p,i)*20**i*(67*27**(p-i)+33*7**(p-i)) for i in range(p+1)]
    den=[comb(p,i)*105**(p-i)*51**i for i in range(p+1)]
    schedule=[8]+[j for j in range(p+1) if j!=8]
    ratios={};failure=None
    for j in schedule:
        a=sum(num[i]*S[i][j] for i in range(j,p+1))
        z=sum(den[i]*S[i][j] for i in range(j,p+1))
        check(z>0,"positive denominator")
        ratio=F(67**j*a*50**p,100**(j+1)*20**p*z)
        ratios[j]=ratio
        if ratio>=eta:
            failure=j
            break
    tested=list(ratios)
    peak=max(tested,key=ratios.__getitem__)
    print("COEFFICIENTS",len(tested),"peak",peak,"first failed",failure,flush=True)
    data={"pins":{**dict(sorted(auditor["PINS"].items())),"previous_checker":METHOD,"previous_receipt":RECEIPT},
          "h":h,"q":"67/100","p":p,"H":H,"law":law,"eta_lower":str(eta),"tested_indices":tested,
          "ratios":{str(j):str(ratios[j]) for j in tested},"unresolved_indices":[j for j in range(p+1) if j not in ratios],
          "peak_index":peak,"peak":str(ratios[peak]),"failed_index":failure,"old_relaxed_ceiling":str(old_ceiling)}
    if failure is not None:
        data["decision"]="FIXED_COEFFICIENT_EXCLUSION"
        return data
    L=(((H+h)**p)//h**p).bit_length()
    check(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,"terminal, preceding debit and all larger widths")
    d=F(b["delayed_cover_debit"]); seed=F(".00385248"); rational=F(peer["rational_raw"][0])
    check(d==F(1,H*2**38),"positive cover unchanged")
    old,old_claim,old_test,_=auditor["stage"](C,seed,d,23731,H,rational)
    check((old,old_claim,old_test)==tuple(prior[k] for k in ("cap","claim","tested")),"full predecessor control")
    cap,k,tested,rows=auditor["stage"](C,seed,d,L,H,rational)
    check(F(k)>old_ceiling+F(1,10**11),"strict directed improvement")
    data.update(decision="ADVANCE_ONE_SIGNED_REPLAY",uniform_numerator=L,cap=cap,claim=k,tested=tested,
                covered=str(C-d-F(L,H)),uniform_loss=str(F(L,H)),cover_loss=str(d),stages=rows,
                old_claim=old_claim,gain=str(F(k)-F(old_claim)),percent=str(100*(F(k)-F(old_claim))/F(old_claim)),
                separation=str(F(k)-old_ceiling))
    return data


if __name__=="__main__":
    ap=ArgumentParser()
    for key in ("predecessor_checker","predecessor_price","accept","application","archive","binary","prior_price","weighted","out"):
        ap.add_argument("--"+key.replace("_","-"),required=True,type=Path,dest=key)
    args=ap.parse_args()
    check(sys.version_info[:2]==(3,12) and __debug__,"CPython 3.12 non-optimized")
    result=solve(args)
    with args.out.open("x") as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print(result["decision"],result.get("claim"))
