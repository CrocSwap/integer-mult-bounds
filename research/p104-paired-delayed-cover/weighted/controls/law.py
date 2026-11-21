# SPDX-License-Identifier: Apache-2.0
"""Check the one frozen paid-exit law using #4480's falling-factorial basis."""
from argparse import ArgumentParser
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import tarfile


PINS = {
    "accept":"35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71",
    "application":"587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
    "archive":"d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
    "binary":"f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4",
    "prior_price":"523d6dc93a7cd34bf6183a66d03b624ab2f0dfcf18b7e95032b7d0ab695fa24f",
    "weighted":"28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7",
}
MEMBER="source/research/paired-query-only-bit/retained/inputs/credited_trim.py"
TRIM="fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9"


def check(ok,what):
    if not ok:
        raise ValueError(what)


def weight(rank,exponent):
    # ln and exp are correctly rounded; outward neighboring results enclose each.
    log=D(rank).ln()
    lo,hi=(log.next_minus(),log.next_plus()) if rank>1 else (D(0),D(0))
    s=D(exponent.numerator)/D(exponent.denominator)
    check(F(s)==exponent and s>=0,"exact exponent")
    bounds=[(s*lo).next_minus().exp().next_minus(),(s*hi).next_plus().exp().next_plus()]
    return F(bounds[0]),F(bounds[1]),F(lo),F(hi)


def out(q,n=20):
    return F((q*10**n).__ceil__(),10**n)


def distribution(T,P,t,old):
    u=F(1,5)
    with localcontext() as ctx:
        ctx.prec=64
        w={r:weight(r,t) for r in T.keys() | P.keys()}
        pt_lo=sum(n*w[r][0] for r,n in P.items())
        tt_hi=sum(n*w[r][1] for r,n in T.items())
        tt_lo=sum(n*w[r][0] for r,n in T.items())
        l15=weight(15,u)
        pu_hi=sum(n*weight(r,t+u)[1] for r,n in P.items())
    raw_hi=out(sum(n*w[r][1]*w[r][3] for r,n in P.items())/(pt_lo*l15[2]))
    alpha_lo=F((pt_lo/tt_hi*10**20).__floor__(),10**20)
    gamma_hi=out(pu_hi/(tt_lo*l15[0]))
    check(alpha_lo>0 and alpha_lo<F(old["alpha"]["upper"]) and gamma_hi>=F(old["gamma"]["lower"]), "original ratios")
    # Enclose the positive excess at a stable rational grid before powering.
    excess=out(2*out(gamma_hi/alpha_lo)**768)
    check(raw_hi+excess<=F(3,4),"completed mean exceeds frozen bound")
    return {"raw_mean_upper":str(raw_hi),"alpha_lower":str(alpha_lo),"gamma_upper":str(gamma_hi),
            "split_uplift_upper":str(excess),"extra_recursive_mass":0,"completed_mean_upper":str(raw_hi+excess)}


def coefficients(p,eta):
    # Independently form S(i,j) on the falling-factor basis. Clear all
    # denominators in the binomial-polynomial numerator and denominator.
    sn=[[1]]
    for i in range(1,p+1):
        prev=sn[-1]
        sn.append([0]+[j*(prev[j] if j<len(prev) else 0)+prev[j-1] for j in range(1,i+1)])
    num=[comb(p,i)*20**i*(3*27**(p-i)+7**(p-i)) for i in range(p+1)]
    den=[comb(p,i)*105**(p-i)*51**i for i in range(p+1)]
    ratios=[]
    for j in range(p+1):
        a=sum(num[i]*sn[i][j] for i in range(j,p+1))
        b=sum(den[i]*sn[i][j] for i in range(j,p+1))
        check(b>0,"positive denominator "+str(j))
        ratio=F(3**j*a*50**p,4**(j+1)*20**p*b)
        ratios.append(ratio)
        if ratio>=eta:
            return ratios,j
    return ratios,None


def decimal(x,n):
    z=x*10**n
    check(z.denominator==1 and 0<z<10**n,"finite decimal")
    return f"0.{int(z):0{n}d}"


def stage(C,seed,d,J,H,rational):
    covered=C-d-F(J,H)
    previous=seed; rows=[]
    for _ in range(4):
        lim=F(249,250)*covered+previous/250
        cap=F((lim*10**15).__floor__()-1,10**15)
        check(previous<cap<lim<F(1,250)<1-lim,"complete stage")
        rows.append({"previous":str(previous),"bound":str(lim),"cap":str(cap),"slack":str(lim-cap)})
        previous=cap
    k=F((min(cap,rational)*10**14).__floor__()-8,10**14)
    return decimal(cap,15),decimal(k,14),decimal(k+F(7,10**14),14),rows


def solve(a):
    for key,pin in PINS.items():
        check(sha256(getattr(a,key).read_bytes()).hexdigest()==pin,"pin "+key)
    with tarfile.open(a.archive) as tar:
        check(sha256(tar.extractfile(MEMBER).read()).hexdigest()==TRIM,"peer paid compiler")
    read=lambda path:json.loads(path.read_bytes())
    previous=read(a.prior_price);peer=read(a.application);past=read(a.accept);binary=read(a.binary)
    check(previous["claim"]==past["claim"]=="0.00389011519729" and previous["case"]["J"]==23731 and past["outcome"]=="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE","signed R348")
    b=binary["peer_finite"]; sep=b["finite_separation"]; native=peer["binary_native"]
    check(native["calls"]==36 and native["paid_all"]==sep["paid"] and native["productive_all"]==sep["targets"],"paid/productive orientation")
    P={int(r):n for r,n in native["paid_all"].items()};T={int(r):n for r,n in native["productive_all"].items()}
    check(sum(P.values())==104904 and sum(T.values())==18906 and T[64]>0 and T[8]>0 and 64**256*8**512==16**768,"complete positions, attained floor")
    check(sep["specialized_initial_and_final"]==0 and sep["owned_allocation_records_bound"]=="2*18906^768"
          and sep["construction"]=="chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes"
          and F(sep["strict_normalized_gap"]["lower"])>0,"full paid stock incl. boundary work")
    C=F(b["tested_saving"]); t=1-C;H=peer["binary_H"]; h,p,v=1024,128,768
    check((H,C)==(299610000000000,F("0.003890115276594")),"trial and carrier")
    J=15**v; K=16**v; A=134**v
    check((1<<(20*h))<=J**7 and ((1<<h)*A)**10>=J**21 and K**50>=J**51,"signed natural-log ratios")
    check(7*v>h and 128**v < A < 256**v and 8*v*C<p,"all ordinary base ranks")
    eta=F(b["uniform"]["eta"]["lower"])
    check(F(3,4)**p < eta*F(51,50)**p,"limiting coefficient once")
    relaxed=F(peer["binary_raw"][1])-F(23731,H)
    check(C-F(4992,H)-F(2,10**13)>relaxed+F(1,10**11),"whole-construction shortfall")
    print("PASS source and whole-word feasibility",flush=True)
    law=distribution(T,P,t,sep)
    print("PASS weighted full split law",flush=True)
    ratios,failure=coefficients(p,eta)
    peak=max(range(len(ratios)),key=ratios.__getitem__)
    data={"pins":dict(sorted(PINS.items())),"member_pins":{MEMBER:TRIM},"case":{"H":H,"p":p,"h":h,"q":"3/4"},
          "law":law,"old_relaxed_ceiling":str(relaxed),"eta_lower":str(eta),
          "ratios":[str(x) for x in ratios],"peak_index":peak,"peak":str(ratios[peak]),
          "failed_coefficient":failure,"unvisited_coefficients":p+1-len(ratios),"g0_ratio":str(ratios[0])}
    if failure is not None:
        data["decision"]="FIXED_COEFFICIENT_EXCLUSION"
        return data
    L=(((H+h)**p)//h**p).bit_length()
    check(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,"terminal, preceding debit and all larger widths")
    d=F(binary["delayed_cover_debit"]); seed=F(".00385248"); rational=F(peer["rational_raw"][0])
    check(d==1/F(H*2**38),"positive cover unchanged")
    old,old_claim,old_test,_=stage(C,seed,d,23731,H,rational)
    check((old,old_claim,old_test)==tuple(previous[k] for k in ("cap","claim","tested")),"old signed price")
    cap,k,tested,rows=stage(C,seed,d,L,H,rational)
    check(F(k)>relaxed+F(1,10**11),"directed separation")
    data.update(decision="ADVANCE_ONE_SIGNED_REPLAY",uniform_numerator=L,cap=cap,claim=k,tested=tested,
                covered=str(C-d-F(L,H)),uniform_loss=str(F(L,H)),cover_loss=str(d),stages=rows,
                old_claim=old_claim,gain=str(F(k)-F(old_claim)),percent=str(100*(F(k)-F(old_claim))/F(old_claim)),
                separation=str(F(k)-relaxed))
    return data


if __name__=="__main__":
    ap=ArgumentParser()
    for key in PINS:
        ap.add_argument("--"+key.replace("_","-"),required=True,type=Path,dest=key)
    ap.add_argument("--out",required=True,type=Path);args=ap.parse_args()
    result=solve(args)
    with args.out.open("x") as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print(result["decision"],result["peak_index"],result.get("claim"))
