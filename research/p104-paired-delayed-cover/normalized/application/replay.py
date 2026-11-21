# SPDX-License-Identifier: Apache-2.0
"""Replay a certified normalized supplier against the original signed #8027 application."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ADAPTER = "d6dd8f406e4e09377b2539a744ada909d3ab44baefdec17d0af450d6e867f051"
PREVIOUS = "419d4bdfb95c4484d0ddc81f34c89ee45bdefc0955a85dd496c1043396260e37"
PRIMARY = "ef3f829625b03c09f1cdff2440ef92b9869b4cb4d0821bf9c0fd5910c9d6ad3c"
INDEPENDENT = "523d6dc93a7cd34bf6183a66d03b624ab2f0dfcf18b7e95032b7d0ab695fa24f"


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


def pair(primary, independent, prior, historical, baseline):
    case=independent["case"]
    case_keys=("p","h","J","H","theta")
    check(all(case[k]==primary[k] for k in case_keys),"both source certificates")
    p,h,J,H=(case[k] for k in case_keys[:4])
    check((p,h,J,H,case["v"],case["theta"])==(623,1024,23731,299610000000000,768,"42/43"),"frozen case")
    trial=Q(primary["trial"])
    debit=Q(historical["delayed_cover_debit"])
    loss=Q(J,H)
    cap=Q(primary["candidate"]["cap"])
    covered=trial-loss-debit
    check(trial==Q(case["C"])==Q(historical["peer_finite"]["tested_saving"])
          and debit==Q(1,H*2**38)==Q(primary["cover_loss"])==Q(independent["cover_loss"])
          and loss==Q(primary["uniform_loss"])==Q(independent["uniform_loss"])
          and covered==Q(primary["candidate"]["covered"])==Q(independent["covered"]),"only uniform debit changed")
    need=(H+h)**p
    check(h**p*2**(J-1)<=need<h**p*2**J, "exact terminal and cheaper-debit control")
    generous=Q(baseline["binary_raw"][1])-Q(1,10**10)
    check((H+512)**p > 512**p*2**(39*p)
          and trial-Q(39*p,H)<generous+Q(1,10**11),"h=512 optimistic exclusion")
    check(Q(primary["old_relaxed_ceiling"])==Q(independent["old_relaxed_ceiling"])==generous,"old relaxed proof ceiling")
    check(prior["cap"]==independent["old_cap"]==primary["comparator"]["cap"]
          and prior["claim"]==independent["old_claim"]==primary["comparator"]["claim"],"old signed control")
    c=primary["candidate"]
    check(all(c[k]==independent[k] for k in ("cap","claim","tested")), "dual complete price")
    old=Q(primary["seed"]);rho=Q(1,250)
    for a,b in zip(c["stages"],independent["new_stages"],strict=True):
        envelope=(1-rho)*covered+rho*old
        admitted=Q((envelope*10**15).__floor__()-1,10**15)
        check(old==Q(a["old"])==Q(b["previous"]) and envelope==Q(a["envelope"])==Q(b["bound"])
              and admitted==Q(a["admitted"])==Q(b["cap"])
              and envelope-admitted==Q(a["slack"])==Q(b["slack"])
              and old<admitted<envelope<rho<1-envelope,"two independent entire stage prices")
        old=admitted
    check(len(c["stages"])==4 and old==cap,"four stage ordinary cap")
    tick=Q(1,10**14)
    claim=(min(Q(baseline["rational_raw"][0]),cap)//tick-8)*tick
    check(claim==Q(c["claim"]) and claim+7*tick==Q(c["tested"])<cap
          and claim-generous==Q(independent["separation"])>Q(1,10**11)
          and claim-Q(prior["claim"])==Q(independent["gap_vs_old"])==Q(primary["absolute_gain"]),
          "signed grid and previous ceiling")
    return cap


def main():
    cli=ArgumentParser(description=__doc__)
    for name in ("peer-package","prior-package","prior-run","primary","independent","out"):
        cli.add_argument("--"+name,required=True,type=Path)
    a=cli.parse_args()
    check(sys.version_info[:2]==(3,12) and sys.implementation.name=="cpython" and __debug__,"CPython 3.12")
    old=previous_adapter(a.prior_package/"application/replay.py")
    s=read(a.prior_run/"REPLAY.json",PREVIOUS)
    old_app=read(a.prior_run/"APPLICATION.json",s["output_sha256"]["APPLICATION.json"])
    old_bit=read(a.prior_run/"BINARY.json",s["output_sha256"]["BINARY.json"])
    old_primary=read(a.prior_package/"primary/PRICE.json",old.PRIMARY)
    old_audit=read(a.prior_package/"independent/PRICE.json",old.INDEPENDENT)
    primary=read(a.primary,PRIMARY)
    independent=read(a.independent,INDEPENDENT)
    a.out.mkdir(exist_ok=False)
    with TemporaryDirectory() as tmp:
        work=Path(tmp)
        peer=old.peer_copy(work/"peer-code",a.peer_package)
        base=peer.read("APPLICATION.json")
        check(old.certify(old_primary,old_audit,base)==Q(s["cap"]),"R347 and #8027 control prices")
        cap=pair(primary,independent,s,old_bit,base)
        package=peer.source_tree(work,base)
        original=old.normalize(old.binary(peer,work,package,base,old_primary))
        check(original==old_bit,"fresh original stock, signed 36-call bill, prior four-stage bootstrap")
        c=primary["candidate"]
        engine=sys.modules["binary_price"]
        admission,four=engine.bootstrap(Q(primary["seed"]),Q(c["covered"]),[i["admitted"] for i in c["stages"]])
        check(admission==cap,"full peer bootstrap on new certified covered price")
        old.save(a.out/"BINARY.json",dict(prior_binary_sha256=s["output_sha256"]["BINARY.json"],
                 peer_finite=original["peer_finite"], delayed_cover_debit=original["delayed_cover_debit"],
                 uniform_loss=primary["uniform_loss"], covered=c["covered"], candidate_stages=four, admitted=c["cap"]))
        print("PASS normalized source, stock and native 36-call bill",flush=True)
        new_app=dict(base,binary_ordinary=c["cap"],claim=c["claim"])
        word,layout,physical=peer.rational_application(work,package,new_app,cap)
        physical=old.normalize(physical)
        old_physical=read(a.prior_run/"PHYSICAL.json",s["output_sha256"]["PHYSICAL.json"])
        for key in ("caller","caller_proof","caller_census","native","conversion","compiler_controls","common_root"):
            check(physical[key]==old_physical[key],"unchanged physical "+key)
        for key in ("invoice","ordinary","bracket"):
            check(physical["application"][key]==old_physical["application"][key],"unchanged signed "+key)
        check(physical["caller_census"]["calls"]==base["rational_calls"]==48
              and physical["caller_proof"]["readback"]["event_stream_sha256"]==physical["caller"]==s["caller"],
              "signed caller and all readback phases")
        del old_physical
        control=old.outer_prices(peer,work,base,old_app,physical)
        check(control["H"]==old_app["H"] and control["outer"]==old_app["outer"],"original #8027 and R347 outer bills")
        new=old.outer_prices(peer,work,old_app,new_app,physical)
        new_app.update(H=new["H"],outer=new["outer"])
        peer.audit(work,package,new_app,cap,word,layout,physical)
        check(new["outer"]["BIT_just_below_effective_rejected"] and new["outer"]["strict_count"]==54
              and new["outer"]["functional_count"]==4 and s["premises"]==new_app["premises"],"complete signed controls")
        old.save(a.out/"APPLICATION.json",new_app)
        old.save(a.out/"PHYSICAL.json",physical)
        files=("APPLICATION.json","BINARY.json","PHYSICAL.json")
        old.save(a.out/"REPLAY.json",dict(peer_head=old.HEAD,source_archive=base["source_archive"],source_count=base["source_count"],
                 prior_receipt_sha256=PREVIOUS,prior_adapter_sha256=ADAPTER,primary_sha256=PRIMARY,independent_sha256=INDEPENDENT,
                 cap=c["cap"],tested=c["tested"],claim=c["claim"],old_claim=s["claim"],difference=primary["absolute_gain"],
                 percent_gain=primary["relative_percent"],old_relaxed_ceiling=primary["old_relaxed_ceiling"],
                 strict_separation=primary["separation"],outer=new["outer"],caller=physical["caller"],
                 rational_raw=new_app["rational_raw"],premises=new_app["premises"],
                 controls=["original_peer_stock_and_signed_gate","R347_four_stages_and_signed_gate","h512_optimistic_price_excluded",
                           "terminal_J_minus_one_rejected","below_effective_cap_rejected","one_extra_rank_one_paid_rejected"],
                 output_sha256={name:sha256((a.out/name).read_bytes()).hexdigest() for name in files}))
        print("PASS_COMPLETE_NORMALIZED_768_APPLICATION",c["claim"],c["tested"],primary["absolute_gain"],flush=True)


if __name__=="__main__":
    main()
