# SPDX-License-Identifier: Apache-2.0
"""Independent direct enumeration of the single 768-factor fortieth moment."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import runpy
import sys


PINS={
    "law":"e0961b875a7f4db9e53f4f2910cad969ea4bb86f0f453ec6ca13a2cb1d0e7559",
    "old_primary":"4acbb38393550df5b046f125328a67bc344fe592a107556145ac315acf083a34",
    "old_independent":"0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332",
    "accept":"32d40619c37fdcf91f63930e3ebdf1ec0e19210f91e4f1a74617fcc1b3ada10c",
    "signed":"65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d",
    "mean":"ea84892ef2b2da5572e7cdabe54d228ee74f6671d11f87bd6aa263306fd8ffdc",
    "application":"587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
    "binary":"f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4",
    "archive":"d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
    "weighted":"28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7",
}


def need(flag,why):
    if not flag:
        raise ValueError(why)


def enumeration(v,p):
    # Integer numerators under the one common probability denominator.
    mass=first=moment=0
    for k in range(v+1):
        w=comb(v,k)*67**k*83**(v-k)
        mass+=w
        first+=w*k
        moment+=w*k**p
    den=150**v
    need(mass==den and 150*first==67*v*den,"every binomial cell and first moment")
    return Q(3,2*v)**p*Q(moment,den)


def prove(a):
    for key,expected in PINS.items():
        need(sha256(getattr(a,key).read_bytes()).hexdigest()==expected,"input "+key)
    lib=runpy.run_path(str(a.law))
    load=lambda p:json.loads(p.read_bytes())
    prev=load(a.old_independent); signed=load(a.signed); accept=load(a.accept);old_primary=load(a.old_primary)
    peer=load(a.application); binary=load(a.binary); full=binary["peer_finite"]
    need(accept["outcome"]=="PASS_COMPLETE_INDEPENDENT_WEIGHTED_ACCEPTANCE" and all(x["claim"]==prev["claim"] for x in (signed,accept,old_primary)),"R351 independent signed comparator")
    p,h,v=40,1024,768
    H=peer["binary_H"]; C=Q(full["tested_saving"]); t=1-C; A,K,J=134**v,16**v,15**v
    need((H,C)==(299610000000000,Q("0.003890115276594")),"unchanged carrier and trial")
    old_upper=Q(peer["binary_raw"][1])-Q(prev["uniform_numerator"],H)
    need(Q(prev["uniform_numerator"])==4876 and C-Q(1560,H)-Q(2,10**13)>old_upper>Q(signed["claim"]),"entire paid opportunity")
    sep=full["finite_separation"]; native=peer["binary_native"]
    need(native["calls"]==36 and native["paid_all"]==sep["paid"] and native["productive_all"]==sep["targets"]
         and sep["construction"]=="chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes"
         and sep["owned_allocation_records_bound"]=="2*18906^768" and sep["specialized_initial_and_final"]==0
         and Q(sep["strict_normalized_gap"]["lower"])>0,"retained whole paid law")
    P={int(k):n for k,n in native["paid_all"].items()};T={int(k):n for k,n in native["productive_all"].items()}
    need(sum(P.values())==104904 and sum(T.values())==18906 and T[64]*T[8]>0 and 64**256*8**512==K
         and min(P)>=1 and max(P)==56 and 56**2<15**3,"one-letter support and attained floor")
    need((1<<(20*h))<=J**7 and ((1<<h)*A)**10>=J**21 and K**50>=J**51
         and 7*v>h and 128**v<A<256**v and 8*v*C<p,"full rank base and normalized guards")
    lam=Q(7,10);eta=Q(full["uniform"]["eta"]["lower"])
    roots=[((Q(7,20)+lam)/Q(21,10))**p,(lam/Q(51,50))**p]
    need(max(roots)<eta,"both all-height ratios")
    print("PASS full-price shortfall, source, base and two endpoints",flush=True)
    law=lib["distribution"](T,P,t,sep)
    need(law==load(a.mean)["law"] and Q(law["raw_mean_upper"])<=Q(67,100),"fresh one-letter expectation")
    raw_moment=enumeration(v,p)
    gamma_alpha=Q(law["gamma_upper"])/Q(law["alpha_lower"])
    extra=Q(law["split_uplift_upper"])
    need(2*gamma_alpha**v<=extra and extra==Q(1,10**20),"whole split addition")
    bound=raw_moment+extra
    data={"pins":dict(sorted(PINS.items())),"p":p,"h":h,"H":H,"v":v,"norm_upper":str(lam),
          "law":law,"direct_terms":769,"one_letter_maximum":"3/2","one_letter_mean_budget":"67/100",
          "binomial_probability":"67/150","raw_moment":str(raw_moment),"full_split_upper":str(extra),"completed_moment":str(bound),
          "norm_budget":str(lam**p),"eta_lower":str(eta),"root_ratio":str(roots[0]),"infinite_height_ratio":str(roots[1]),
          "relaxed_old_ceiling":str(old_upper)}
    if bound>=lam**p:
        data["decision"]="NORM_GATE_EXCLUDED"; return data
    L=(((H+h)**p)//(h**p)).bit_length()
    need(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,"neighboring terminal integers and tail")
    d=Q(binary["delayed_cover_debit"]);seed=Q(".00385248");rational=Q(peer["rational_raw"][0])
    need(d==Q(1,H*2**38),"original positive cover")
    old,oldk,oldt,_=lib["stage"](C,seed,d,4876,H,rational)
    need((old,oldk,oldt)==tuple(signed[k] for k in ("cap","claim","tested")),"prior complete stage and grid price")
    cap,k,tested,rows=lib["stage"](C,seed,d,L,H,rational)
    need(Q(k)>old_upper>Q(oldk),"strict proof change")
    data.update(decision="ADVANCE_ONE_SIGNED_REPLAY",uniform_numerator=L,cap=cap,claim=k,tested=tested,covered=str(C-d-Q(L,H)),
                uniform_loss=str(Q(L,H)),cover_loss=str(d),stages=rows,old_claim=oldk,
                gain=str(Q(k)-Q(oldk)),percent=str(100*(Q(k)-Q(oldk))/Q(oldk)),separation=str(Q(k)-old_upper))
    return data


if __name__=="__main__":
    parser=ArgumentParser()
    for name in [*PINS,"out"]:
        parser.add_argument("--"+name.replace("_","-"),dest=name,type=Path,required=True)
    args=parser.parse_args()
    need(sys.version_info[:2]==(3,12) and __debug__,"CPython 3.12")
    result=prove(args)
    with args.out.open("x") as f:
        json.dump(result,f,sort_keys=True,indent=2);f.write("\n")
    print(result["decision"],result.get("cap"),result.get("claim"))
