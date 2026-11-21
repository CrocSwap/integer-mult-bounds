# SPDX-License-Identifier: Apache-2.0
"""One charged paid-tail interval and two all-height Minkowski endpoints."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import runpy
import sys


LAW_CHECKER="e0961b875a7f4db9e53f4f2910cad969ea4bb86f0f453ec6ca13a2cb1d0e7559"
LAW_RECEIPT="0239f7f69dea671a66a37e3bcaae61c16d23dc794812d519d1c020821332ad36"
MEAN_FAILURE="ea84892ef2b2da5572e7cdabe54d228ee74f6671d11f87bd6aa263306fd8ffdc"


def need(test,reason):
    if not test:
        raise ValueError(reason)


def locked(path,sha):
    blob=path.read_bytes()
    need(sha256(blob).hexdigest()==sha,"source hash "+path.name)
    return blob


def upward(q):
    return F((q*10**24).__ceil__(),10**24)


def prove(args):
    old=json.loads(locked(args.law_receipt,LAW_RECEIPT))
    stopped=json.loads(locked(args.failure,MEAN_FAILURE))
    locked(args.law_checker,LAW_CHECKER)
    lawlib=runpy.run_path(str(args.law_checker))
    raw={k:locked(getattr(args,k),pin) for k,pin in lawlib["PINS"].items()}
    peer=json.loads(raw["application"]); prior=json.loads(raw["prior_price"])
    accepted=json.loads(raw["accept"]); binary=json.loads(raw["binary"])
    need(accepted["outcome"]=="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE" and accepted["claim"]==prior["claim"],"R348 accepted")
    need(stopped["failed_index"]==11 and stopped["q"]=="67/100" and old["failed_coefficient"]==8,"frozen pivot")
    finite=binary["peer_finite"]; sep=finite["finite_separation"]; native=peer["binary_native"]
    p,h,H=128,1024,peer["binary_H"]
    C=F(finite["tested_saving"]); t=1-C
    A,J,K=134**768,15**768,16**768
    need(native["calls"]==36 and native["paid_all"]==sep["paid"] and native["productive_all"]==sep["targets"]
         and (C,H)==(F("0.003890115276594"),299610000000000),"fixed physical source and rate")
    P={int(k):n for k,n in native["paid_all"].items()};T={int(k):n for k,n in native["productive_all"].items()}
    need(sum(P.values())==104904 and sum(T.values())==18906 and min(T[64],T[8])>0 and 64**256*8**512==K,
         "complete paid stock and actual floor")
    need(sep["specialized_initial_and_final"]==0 and sep["owned_allocation_records_bound"]=="2*18906^768"
         and sep["construction"]=="chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes"
         and F(sep["strict_normalized_gap"]["lower"])>0,"all ordinary boundaries and full split law")
    need(1<<(20*h)<=J**7 and ((1<<h)*A)**10>=J**21 and K**50>=J**51 and A>128**768 and 7*768>h and 8*768*C<p,
         "log guards and every ordinary base rank")
    law=lawlib["distribution"](T,P,t,sep)
    need(law==old["law"]==stopped["law"],"fresh outward raw moment ratios")
    alpha=F(law["alpha_lower"]); gamma=F(law["gamma_upper"]); quotient=gamma/alpha
    a=F(4,5);z=F(9,10);u=F(1,5)
    need(u*(1-a)==F(1,25) and (F(223,200))**25>15,"power for one-letter tail")
    need(quotient*F(223,200)<=F(49,50) and quotient<1,"directed Markov factor")
    raw_high=upward(F(49,50)**768)
    # For split tuples w/parent > J, total completed t-mass minus raw
    # t-mass is positive and bounded by 2 gamma^768 times T_t^768.
    uplift=F(law["split_uplift_upper"])
    need(uplift==F(1,10**20) and 2*quotient**768<=uplift,"all split positive excess charged")
    tail=raw_high+uplift
    moment=a**p+tail
    need(moment<z**p,"fixed norm gate")
    eta=F(finite["uniform"]["eta"]["lower"])
    endpoint0=((F(7,20)+z)/F(21,10))**p
    endpoint_inf=(z/F(51,50))**p
    passed=[endpoint0<eta, endpoint_inf<eta]
    out={"pins":{**dict(sorted(lawlib["PINS"].items())),"law_checker":LAW_CHECKER,"law_receipt":LAW_RECEIPT,"prior_failed_certificate":MEAN_FAILURE},
         "h":h,"p":p,"H":H,"cutoff":str(a),"norm_upper":str(z),"u":str(u),
         "source_alpha_lower":str(alpha),"source_gamma_upper":str(gamma),"markov_base_upper":"49/50",
         "raw_high_mass_upper":str(raw_high),"total_split_uplift_upper":str(uplift),"high_mass_upper":str(tail),
         "moment_upper":str(moment),"norm_guard_power":str(z**p),"eta_lower":str(eta),
         "root_ratio":str(endpoint0),"infinite_height_ratio":str(endpoint_inf),"pass_endpoints":passed}
    if not all(passed):
        out["decision"]="FIXED_ENDPOINT_EXCLUSION"
        return out
    L=(((H+h)**p)//h**p).bit_length()
    need(h**p*(1<<(L-1))<=(h+H)**p < h**p*(1<<L) and L*(H+h)>2*H*p,"neighboring integer debits, whole upper tail")
    d=F(binary["delayed_cover_debit"]); seed=F(".00385248");rat=F(peer["rational_raw"][0])
    need(d==F(1,H*2**38) and H*d/2==F(64,2**45),"actual cover surcharge")
    oc,ok,ot,_=lawlib["stage"](C,seed,d,23731,H,rat)
    need((oc,ok,ot)==tuple(prior[k] for k in ("cap","claim","tested")),"preceding four-stage price")
    cap,k,tested,rows=lawlib["stage"](C,seed,d,L,H,rat)
    U=F(peer["binary_raw"][1])-F(23731,H)
    need(F(k)>U+F(1,10**11),"fully charged relaxed predecessor separation")
    out.update(decision="ADVANCE_ONE_SIGNED_REPLAY",uniform_numerator=L,cap=cap,claim=k,tested=tested,
               covered=str(C-d-F(L,H)),uniform_loss=str(F(L,H)),cover_loss=str(d),stages=rows,
               old_claim=ok,gain=str(F(k)-F(ok)),percent=str(100*(F(k)-F(ok))/F(ok)),
               old_relaxed_ceiling=str(U),separation=str(F(k)-U))
    return out


if __name__=="__main__":
    cmd=ArgumentParser()
    for key in ("law_checker","law_receipt","failure","accept","application","archive","binary","prior_price","weighted","out"):
        cmd.add_argument("--"+key.replace("_","-"),required=True,type=Path,dest=key)
    a=cmd.parse_args()
    need(sys.version_info[:2]==(3,12) and __debug__,"CPython 3.12")
    result=prove(a)
    with a.out.open("x") as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print(result["decision"],result["pass_endpoints"],result.get("claim"),result.get("cap"))
