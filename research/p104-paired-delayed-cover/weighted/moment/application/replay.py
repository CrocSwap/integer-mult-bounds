# SPDX-License-Identifier: Apache-2.0
"""Bind one authenticated source-moment supplier proof to the complete signed #8027 consumer."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ADAPTER = "d6dd8f406e4e09377b2539a744ada909d3ab44baefdec17d0af450d6e867f051"
PREVIOUS = "65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d"
PRIMARY = "8c09bcccce796c9b01efed5d9363af8fe6b8719f588eb6de5148933411a8850d"
INDEPENDENT = "5c9d36bad5d7fca162d135e9d8658ab408a6d89edd262be167747cc164c12229"


def check(flag, message):
    if not flag:
        raise ValueError(message)


def read(path, pin):
    data = path.read_bytes()
    check(sha256(data).hexdigest()==pin, "input SHA-256 "+path.name)
    return json.loads(data)


def previous_adapter(path):
    check(sha256(path.read_bytes()).hexdigest()==ADAPTER,"R347 adapter")
    spec=importlib.util.spec_from_file_location("fixed_cover_adapter",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def price(covered,rows,seed):
    previous=seed
    check(len(rows)==4,"four original ordinary service levels")
    for row in rows:
        envelope=(249*covered+previous)/250
        cap=Q((envelope*10**15).__floor__()-1,10**15)
        check(previous==Q(row["previous"]) and cap==Q(row["cap"]) and envelope==Q(row["bound"])
              and envelope-cap==Q(row["slack"]) and previous<cap<envelope<Q(1,250)<1-envelope,
              "reconstructed strictly charged envelope")
        previous=cap
    return previous


def main():
    cli=ArgumentParser(description=__doc__)
    for name in ("peer-package","cover-package","prior-run","prior-accept","primary","independent","out"):
        cli.add_argument("--"+name,required=True,type=Path)
    a=cli.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=="cpython" and __debug__,"CPython 3.12")
    old=previous_adapter(a.cover_package/"application/replay.py")
    s=read(a.prior_run/"REPLAY.json",PREVIOUS)
    signed=read(a.prior_accept,"32d40619c37fdcf91f63930e3ebdf1ec0e19210f91e4f1a74617fcc1b3ada10c")
    check(signed["outcome"]=="PASS_COMPLETE_INDEPENDENT_WEIGHTED_ACCEPTANCE" and signed["claim"]==s["claim"],"R351 complete acceptance")
    prior_app=read(a.prior_run/"APPLICATION.json",s["output_sha256"]["APPLICATION.json"])
    old_bit=read(a.prior_run/"BINARY.json",s["output_sha256"]["BINARY.json"])
    old_primary=read(a.cover_package/"primary/PRICE.json",old.PRIMARY)
    old_audit=read(a.cover_package/"independent/PRICE.json",old.INDEPENDENT)
    primary=read(a.primary,PRIMARY)
    independent=read(a.independent,INDEPENDENT)
    a.out.mkdir(exist_ok=False)
    with TemporaryDirectory() as tmp:
        work=Path(tmp)
        peer=old.peer_copy(work/"peer-code",a.peer_package)
        base=peer.read("APPLICATION.json")
        check(old.certify(old_primary,old_audit,base)==Q(".003890115176583"),"R347 and #8027 controls")
        cap=pair(primary,independent,s,old_bit,base)
        package=peer.source_tree(work,base)
        original=old.normalize(old.binary(peer,work,package,base,old_primary))
        check(original["peer_finite"]==old_bit["peer_finite"] and original["delayed_cover_debit"]==old_bit["delayed_cover_debit"],
              "fresh original stock and signed 36-call bill")
        engine=sys.modules["binary_price"]
        seed=Q(".00385248")
        prior_cap,prior_four=engine.bootstrap(seed,Q(old_bit["covered"]),[i["claim"] for i in old_bit["candidate_stages"]])
        check(prior_cap==Q(s["cap"]) and old.normalize(prior_four)==old_bit["candidate_stages"],"reprice R351 original stock")
        targets=[]
        for i in independent["stages"]:
            z=Q(i["cap"])*10**15
            check(z.denominator==1,"strict-stage fixed point")
            targets.append(f"0.{int(z):015d}")
        admission,four=engine.bootstrap(seed,Q(independent["covered"]),targets)
        check(admission==cap,"new complete ordinary bootstrap")
        old.save(a.out/"BINARY.json",dict(prior_binary_sha256=s["output_sha256"]["BINARY.json"],
                 peer_finite=original["peer_finite"],delayed_cover_debit=original["delayed_cover_debit"],
                 uniform_loss=independent["uniform_loss"],covered=independent["covered"],candidate_stages=four,admitted=independent["cap"]))
        print("PASS direct and Stirling moments, root and infinite-height endpoints, original stock and native 36-call bill",flush=True)
        new_app=dict(base,binary_ordinary=independent["cap"],claim=independent["claim"])
        word,layout,physical=peer.rational_application(work,package,new_app,cap)
        physical=old.normalize(physical)
        prior_physical=read(a.prior_run/"PHYSICAL.json",s["output_sha256"]["PHYSICAL.json"])
        for key in ("caller","caller_proof","caller_census","native","conversion","compiler_controls","common_root"):
            check(physical[key]==prior_physical[key],"unchanged physical "+key)
        for key in ("invoice","ordinary","bracket"):
            check(physical["application"][key]==prior_physical["application"][key],"unchanged signed "+key)
        check(physical["caller_census"]["calls"]==base["rational_calls"]==48
              and physical["caller_proof"]["readback"]["event_stream_sha256"]==physical["caller"]==s["caller"],
              "signed caller and readback phases")
        del prior_physical
        control=old.outer_prices(peer,work,base,prior_app,physical)
        check(control["H"]==prior_app["H"] and control["outer"]==prior_app["outer"],"original #8027 and R351 signed prices")
        new=old.outer_prices(peer,work,prior_app,new_app,physical)
        new_app.update(H=new["H"],outer=new["outer"])
        peer.audit(work,package,new_app,cap,word,layout,physical)
        check(new["outer"]["BIT_just_below_effective_rejected"] and new["outer"]["strict_count"]==54
              and new["outer"]["functional_count"]==4 and s["premises"]==new_app["premises"],"complete signed controls")
        old.save(a.out/"APPLICATION.json",new_app)
        old.save(a.out/"PHYSICAL.json",physical)
        files=("APPLICATION.json","BINARY.json","PHYSICAL.json")
        old.save(a.out/"REPLAY.json",dict(peer_head=old.HEAD,source_archive=base["source_archive"],source_count=base["source_count"],
                 prior_receipt_sha256=PREVIOUS,prior_adapter_sha256=ADAPTER,primary_sha256=PRIMARY,independent_sha256=INDEPENDENT,
                 cap=independent["cap"],tested=independent["tested"],claim=independent["claim"],old_claim=s["claim"],difference=independent["gain"],
                 percent_gain=independent["percent"],old_relaxed_ceiling=independent["relaxed_old_ceiling"],
                 strict_separation=independent["separation"],outer=new["outer"],caller=physical["caller"],
                 rational_raw=new_app["rational_raw"],premises=new_app["premises"],
                 controls=["original_peer_stock_and_signed_gate","R351_four_stages_and_signed_gate","both_Minkowski_endpoints","769_direct_vs_41_Stirling_terms",
                           "terminal_J_minus_one_rejected","below_effective_cap_rejected","one_extra_rank_one_paid_rejected"],
                 output_sha256={name:sha256((a.out/name).read_bytes()).hexdigest() for name in files}))
        print("PASS_COMPLETE_SOURCE_MOMENT_APPLICATION",independent["claim"],independent["tested"],independent["gain"],flush=True)


def pair(primary,independent,s,prior_bit,base):
    check(primary["result"]=="PASS_FULL_PRICED_MOMENT_SIGNED_REQUIRED"
          and independent["decision"]=="ADVANCE_ONE_SIGNED_REPLAY","dual completed prices")
    H,p,h=(independent[k] for k in ("H","p","h"))
    check((H,p,h)==(299610000000000,40,1024) and all(primary["case"][k]==independent[k] for k in ("H","p","h","v")),"declared case")
    v=independent["v"]; L=independent["uniform_numerator"]; lam=Q(independent["norm_upper"])
    check(v==768 and L==primary["L"]==1524 and lam==Q(primary["case"]["norm_limit"])==Q(7,10),"power, terminal and norm")
    terms=[Q(x) for x in primary["stirling_terms_0_through_40"]]
    direct=Q(independent["raw_moment"])
    check(len(terms)==p+1 and terms[0]==0 and min(terms[1:])>0 and independent["direct_terms"]==769
          and (Q(3,2*v)**p)*sum(terms)==Q(primary["raw_moment_upper"])==direct,
          "exact direct binomial and falling-factor sum agree")
    check(Q(primary["extra_recursive_completion"])==0 and Q(independent["completed_moment"])==direct+Q(independent["full_split_upper"])
          and Q(primary["complete_moment_upper"])==direct+Q(primary["positive_split_uplift_upper"])
          and max(Q(primary["complete_moment_upper"]),Q(independent["completed_moment"]))<lam**p,"full paid moment with both uplifts")
    eta=Q(independent["eta_lower"])
    for value,left,right in [((Q(7,20)+lam)/Q(21,10),"endpoint_zero","root_ratio"),(lam/Q(51,50),"endpoint_infinity","infinite_height_ratio")]:
        check(value**p==Q(primary[left])==Q(independent[right])<eta,"both all-height endpoint costs")
    check(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,"exact terminal plus tail")
    C=Q(prior_bit["peer_finite"]["tested_saving"]);d=Q(prior_bit["delayed_cover_debit"])
    check(d==Q(1,H*2**38) and Q(prior_bit["uniform_loss"])==Q(4876,H),"actual R351 charges")
    for key in ("cap","claim","tested","uniform_loss","cover_loss","covered","gain","percent","separation","eta_lower","relaxed_old_ceiling"):
        check(Q(primary[key])==Q(independent[key]),"complete two-way price "+key)
    covered=C-d-Q(L,H); cap=price(covered,independent["stages"],Q(".00385248"))
    check(Q(independent["covered"])==covered and cap==Q(independent["cap"]) and Q(independent["cover_loss"])==d,"full peer cost admission")
    for a,b in zip(primary["stages"],independent["stages"],strict=True):
        for k,j in (("admitted","cap"),("endpoint","bound"),("previous","previous"),("charged_minimum_slack","slack")):
            check(Q(a[k])==Q(b[j]),"both bootstrap certificates")
    tick=Q(1,10**14);claim=(min(cap,Q(base["rational_raw"][0]))//tick-8)*tick
    ceiling=Q(base["binary_raw"][1])-Q(4876,H)
    check(Q(s["claim"])==Q(independent["old_claim"]) and claim==Q(independent["claim"])
          and claim+7*tick==Q(independent["tested"])<cap and claim-Q(s["claim"])==Q(independent["gain"])
          and ceiling==Q(independent["relaxed_old_ceiling"]) and claim-ceiling==Q(independent["separation"])>0,
          "strict directed R351 separation and complete grid")
    return cap


if __name__=="__main__":
    main()
