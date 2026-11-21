# SPDX-License-Identifier: Apache-2.0
"""Bind one authenticated Minkowski supplier proof to the complete signed #8027 consumer."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ADAPTER = "d6dd8f406e4e09377b2539a744ada909d3ab44baefdec17d0af450d6e867f051"
PREVIOUS = "9b00a17913efb76995b01c7b75f5b00aab394a0531e26490ab02a5940adcac3c"
PRIMARY = "4acbb38393550df5b046f125328a67bc344fe592a107556145ac315acf083a34"
INDEPENDENT = "0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332"


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


def pair(primary,independent,s,old_bit,base):
    H=independent["H"];p=independent["p"];h=independent["h"]
    check((H,p,h)==(299610000000000,128,1024),"single registered case")
    L=independent["uniform_numerator"];a=Q(independent["cutoff"]); norm=Q(independent["norm_upper"])
    check(L==4876 and a==Q(4,5) and norm==Q(9,10),"tail, norm and terminal")
    m=Q(independent["moment_upper"]); eta=Q(independent["eta_lower"])
    check(m==a**p+Q(independent["high_mass_upper"]) and m<norm**p
          and Q(independent["high_mass_upper"])==Q(independent["raw_high_mass_upper"])+Q(independent["total_split_uplift_upper"]),
          "entire paid upper tail")
    ratios=((Q(7,20)+norm)/Q(21,10),norm/Q(51,50))
    check(ratios[0]**p==Q(independent["root_ratio"])<eta and ratios[1]**p==Q(independent["infinite_height_ratio"])<eta,
          "both all-height endpoints")
    check(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,"one fewer terminal unit is inadmissible")
    d=Q(old_bit["delayed_cover_debit"]); C=Q(old_bit["peer_finite"]["tested_saving"])
    check(d==Q(1,H*2**38)==Q(independent["cover_loss"]) and Q(L,H)==Q(independent["uniform_loss"]),
          "same physical cover and new whole-carrier uniform charge")
    covered=C-d-Q(L,H)
    cap=price(covered,independent["stages"],Q(".00385248"))
    tick=Q(1,10**14)
    k=(min(cap,Q(base["rational_raw"][0]))//tick-8)*tick
    check(covered==Q(independent["covered"]) and cap==Q(independent["cap"]) and k==Q(independent["claim"])
          and k+7*tick==Q(independent["tested"])<cap,"all complete signed deductions")
    relaxed=Q(base["binary_raw"][1])-Q(23731,H)
    check(k-relaxed==Q(independent["separation"])>Q(1,10**11) and k-Q(s["claim"])==Q(independent["gain"]),
          "relaxed R348 proof separation")
    bind_primary(primary,independent)
    return cap


def main():
    cli=ArgumentParser(description=__doc__)
    for name in ("peer-package","cover-package","prior-run","prior-accept","primary","independent","out"):
        cli.add_argument("--"+name,required=True,type=Path)
    a=cli.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=="cpython" and __debug__,"CPython 3.12")
    old=previous_adapter(a.cover_package/"application/replay.py")
    s=read(a.prior_run/"REPLAY.json",PREVIOUS)
    signed=read(a.prior_accept,"35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71")
    check(signed["outcome"]=="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE" and signed["claim"]==s["claim"],"R348 complete acceptance")
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
        check(prior_cap==Q(s["cap"]) and old.normalize(prior_four)==old_bit["candidate_stages"],"reprice R348 original stock")
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
        print("PASS paid tail, root and infinite-height endpoints, original stock and native 36-call bill",flush=True)
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
        check(control["H"]==prior_app["H"] and control["outer"]==prior_app["outer"],"original #8027 and R348 signed prices")
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
                 percent_gain=independent["percent"],old_relaxed_ceiling=independent["old_relaxed_ceiling"],
                 strict_separation=independent["separation"],outer=new["outer"],caller=physical["caller"],
                 rational_raw=new_app["rational_raw"],premises=new_app["premises"],
                 controls=["original_peer_stock_and_signed_gate","R348_four_stages_and_signed_gate","both_Minkowski_endpoints",
                           "terminal_J_minus_one_rejected","below_effective_cap_rejected","one_extra_rank_one_paid_rejected"],
                 output_sha256={name:sha256((a.out/name).read_bytes()).hexdigest() for name in files}))
        print("PASS_COMPLETE_PAID_TAIL_APPLICATION",independent["claim"],independent["tested"],independent["gain"],flush=True)


def bind_primary(primary,independent):
    check(primary["result"]=="PASS_WHOLE_TUPLE_PRICE_SIGNED_REPLAY_REQUIRED"
          and independent["decision"]=="ADVANCE_ONE_SIGNED_REPLAY","both independently certified inputs")
    check(primary["case"]["top_cut"]==independent["cutoff"] and primary["case"]["Lp_bound"]==independent["norm_upper"]
          and all(primary["case"][k]==independent[k] for k in ("p","h","H"))
          and primary["L"]==independent["uniform_numerator"],"identified price point")
    shared=("cap","claim","tested","uniform_loss","cover_loss","covered","gain","percent","separation","eta_lower")
    check(all(Q(primary[k])==Q(independent[k]) for k in shared) and primary["prior_claim"]==independent["old_claim"],
          "both full prices and signed grid")
    for k,j in (("endpoint_g0","root_ratio"),("endpoint_infinity","infinite_height_ratio"),("relaxed_old_ceiling","old_relaxed_ceiling")):
        check(Q(primary[k])==Q(independent[j]),"matched "+k)
    check(Q(primary["one_label_moment_upper"])<Q(primary["one_label_moment_budget"])==Q(independent["norm_guard_power"]),
          "independent moment enclosures both certify the fixed norm")
    for a,b in zip(primary["stages"],independent["stages"],strict=True):
        for k,j in (("admitted","cap"),("endpoint","bound"),("previous","previous"),("charged_minimum_slack","slack")):
            check(Q(a[k])==Q(b[j]),"both fully charged stage prices")


if __name__=="__main__":
    main()
