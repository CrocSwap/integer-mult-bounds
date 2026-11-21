# SPDX-License-Identifier: Apache-2.0
"""Bind one complete weighted-exit supplier to its literal 48-call signed application."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
import tarfile
from tempfile import TemporaryDirectory


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    data = dict(pairs)
    check(len(data) == len(pairs), "duplicate key")
    return data


def read(path, expected):
    data = path.read_bytes()
    check(sha256(data).hexdigest() == expected, "digest mismatch in " + path.name)
    return json.loads(data, object_pairs_hook=unique)


def run_files(root, sha):
    record = read(root/"REPLAY.json", sha)
    names = ("BINARY.json", "PHYSICAL.json", "APPLICATION.json")
    check(set(names) == set(record["output_sha256"]), "run inventory")
    return (record, *(read(root/n, record["output_sha256"][n]) for n in names))


def different(a, b):
    return sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))


def physical_invoice(peer, physical, prior, application, previous):
    bank = read(peer/"BANK-FACTORS-RECEIPT.json", "bdb3052152bdd15ae36c30c98877dcebf864fc2c58a7b1fa66f2d5affa149288")
    caller = read(peer/"CALLER-CENSUS.json", "6a685bdc50aeba01a79fa437490190568513d62e0765844e7f3e8fa29a913e16")
    check(different(physical, prior) == ["application"] and
          different(physical["application"], prior["application"]) == ["claim","compiler"],
          "phase, ownership, precision, route, tape, ordinary cost or conservation changed")
    check(different(application, previous) == ["binary_ordinary","claim"], "unexpected change to result summary")
    check(physical["caller"] == physical["caller_proof"]["readback"]["event_stream_sha256"] ==
          "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858", "signed caller")
    native = physical["native"]
    check(native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"]
          and native["same_owner_complete_fixture_outputs"] == native["exact_all_public_rows"] ==
          native["exact_source_columns"] == bank["public"] == 1291, "independent rows and restoration")
    check(all(physical["caller_census"][k] == v for k,v in caller.items()) and caller["calls"] == 48 and
          application["binary_native"]["calls"] == 36, "signed caller counts")
    invoice = {}
    for key, nkey, ckey, bkey, actual in (
        ("T","positive_helper_ranks","fixed_root_targets","productive","targets"),
        ("P","paid_native_ranks","fixed_caller_paid","paid","paid"),
    ):
        total = Counter({r:n*caller["calls"] for r,n in native[nkey].items()})
        total.update(caller[ckey])
        check(total == bank[bkey] == physical["application"]["invoice"][actual], "signed invoice "+key)
        invoice[key] = dict(total)
    return invoice


def signed_gate(peer, base, invoice, previous, app, physical):
    archive = peer/"APPLICATION-SOURCES.tar.gz"
    check(sha256(archive.read_bytes()).hexdigest() == base["source_archive"], "exact gate archive")
    with tarfile.open(archive) as tar:
        source = tar.extractfile("source/research/p104-dual-supplier-lift/complex/supplier_gate.py").read()
    check(sha256(source).hexdigest()=="3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca", "gate")
    with TemporaryDirectory() as work:
        path=Path(work)/"gate.py"
        path.write_bytes(source)
        gate=runpy.run_path(str(path))["gate"]
    tick=Q(1,10**14)
    def calculate(data, weights, cap):
        k=Q(data["claim"])
        gate.__globals__["BIT_PIN"]=str(Q(data["binary_ordinary"]))
        return gate(weights,k,k+7*tick,*data["rational_raw"],cap)
    for data in (base,previous,app):
        result=calculate(data,invoice,Q(data["binary_ordinary"]))
        check(result["H"]==data["H"] and result["outer"]==data["outer"], "signed positive control")
    check(result==physical["application"]["compiler"] and result["outer"]["strict_count"]==54 and
          result["outer"]["functional_count"]==4 and Q(result["outer"]["minimum_margin"])>0,"all signed checks")
    damaged={"T":invoice["T"],"P":dict(invoice["P"])}
    damaged["P"]["1"]+=1
    for weights,cap in ((damaged,Q(app["binary_ordinary"])),(invoice,Q(app["claim"])+7*tick)):
        try:
            calculate(app,weights,cap)
        except (AssertionError,ValueError):
            continue
        raise ValueError("negative signed control accepted")
    return result["outer"]


def ordinary(bit, previous, previous_result, h, J, trial):
    H=299610000000000
    check(bit["peer_finite"]==previous["peer_finite"] and bit["prior_binary_sha256"]==
          previous_result["output_sha256"]["BINARY.json"], "original stock and 36-call binary")
    check(h==1024 and h**128 * 2**(J-1) <= (h+H)**128 < h**128 * 2**J and
          (h+H)*J > 2*H*128, "minimal terminal and tail")
    cover=Q(1,H*2**38)
    check(Q(bit["uniform_loss"])==Q(J,H) and Q(bit["delayed_cover_debit"])==cover==Q(previous["delayed_cover_debit"]),
          "separate uniform and cover charges")
    covered=trial-Q(J,H)-cover
    check(covered==Q(bit["covered"]), "full covered price")
    stage=Q("0.00385248")
    rows=[]
    check(len(bit["candidate_stages"])==4, "all four restored stages")
    for row in bit["candidate_stages"]:
        bound=(249*covered+stage)/250
        admitted=Q((bound*10**15)//1-1,10**15)
        slack=min(bound-admitted,Q(1,250)-admitted,Q(249,250)-admitted)
        check(stage==Q(row["previous"]) and admitted==Q(row["claim"]) and stage<admitted and slack>0 and
              Q(row["envelope"][0])<=bound<=Q(row["envelope"][1]), "complete stage")
        rows.append([str(stage),str(bound),str(admitted),str(slack)])
        stage=admitted
    check(stage==Q(bit["admitted"]), "terminal cap")
    return stage,rows


def moment_guards(independent, finite):
    theta = Q(4,5)
    norm = Q(9,10)
    alpha = Q(independent["source_alpha_lower"])
    gamma = Q(independent["source_gamma_upper"])
    split = Q(independent["total_split_uplift_upper"])
    upper = Q(independent["raw_high_mass_upper"])
    check(Q(223,200)**25 > 15 and gamma/alpha*Q(223,200) <= Q(49,50) and
          upper >= Q(49,50)**768 and 2*(gamma/alpha)**768 <= split, "original paid law and all positive split surplus")
    check(theta**128+upper+split == Q(independent["moment_upper"]) < norm**128 ==
          Q(independent["norm_guard_power"]), "128th moment")
    guards = (((Q(7,20)+norm)/Q(21,10))**128, (norm/Q(51,50))**128)
    eta = Q(finite["uniform"]["eta"]["lower"])
    check(guards == (Q(independent["root_ratio"]),Q(independent["infinite_height_ratio"])) and
          eta == Q(independent["eta_lower"]) and max(guards)<eta, "all-height endpoint comparison")
    return [str(x) for x in guards]


PRIMARY = "4acbb38393550df5b046f125328a67bc344fe592a107556145ac315acf083a34"
REPLAY = "65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d"


def check_source_prices(primary, independent, signed):
    check(primary["result"]=="PASS_WHOLE_TUPLE_PRICE_SIGNED_REPLAY_REQUIRED" and
          primary["case"]["p"]==independent["p"]==128 and primary["L"]==independent["uniform_numerator"],
          "frozen candidate and exact terminal")
    for field in ("cap","tested","claim"):
        check(primary[field]==independent[field]==signed[field], "three-way "+field)
    for field in ("gain","percent","covered","uniform_loss","cover_loss","separation"):
        check(Q(primary[field])==Q(independent[field]), "price "+field)
    for a,b in zip(primary["stages"],independent["stages"],strict=True):
        check(all(Q(a[k])==Q(b[j]) for k,j in (("admitted","cap"),("endpoint","bound"),
                  ("previous","previous"),("charged_minimum_slack","slack"))),"literal charges both price proofs")


def main(args):
    prior_id = "9b00a17913efb76995b01c7b75f5b00aab394a0531e26490ab02a5940adcac3c"
    accepted = read(args.prior_accept, "35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71")
    prior, old_bit, old_physical, previous = run_files(args.prior_run,prior_id)
    check(accepted["outcome"]=="PASS_COMPLETE_INDEPENDENT_NORMALIZED_ACCEPTANCE" and
          accepted["replay_sha256"]==prior_id and accepted["outputs"]==prior["output_sha256"], "independently reproduced reference")
    primary = read(args.primary, PRIMARY)
    independent = read(args.independent, "0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332")
    base=read(args.peer/"APPLICATION.json","587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f")
    signed, bit, physical, app = run_files(args.run, REPLAY)
    check(accepted["peer_head"]==signed["peer_head"]==prior["peer_head"] and independent["decision"]=="ADVANCE_ONE_SIGNED_REPLAY",
          "price admission and original word")
    endpoint_ratios=moment_guards(independent,bit["peer_finite"])
    cap, rows = ordinary(bit,old_bit,prior,independent["h"],independent["uniform_numerator"],
                         Q(bit["peer_finite"]["tested_saving"]))
    for row,checked in zip(rows,independent["stages"],strict=True):
        check(row==[checked[k] for k in ("previous","bound","cap","slack")],"independent stage")
    claim=Q(app["claim"])
    tick=Q(1,10**14)
    tested=claim+7*tick
    check(cap==Q(app["binary_ordinary"])==Q(independent["cap"]) and
          claim==Q(independent["claim"])==(min(cap,Q(base["rational_raw"][0]))//tick-8)*tick
          and tested==Q(independent["tested"])<cap, "complete terminal")
    invoice=physical_invoice(args.peer,physical,old_physical,app,previous)
    outer=signed_gate(args.peer,base,invoice,previous,app,physical)
    prev_k=Q(previous["claim"]);peer_k=Q(base["claim"])
    gap=claim-(Q(base["binary_raw"][1])-Q(23731,299610000000000))
    check(gap==Q(independent["separation"])>Q(1,10**11) and
          claim-prev_k==Q(independent["gain"]), "true previous-proof ceiling and gain")
    check_source_prices(primary,independent,signed)
    return dict(outcome="PASS_COMPLETE_INDEPENDENT_WEIGHTED_ACCEPTANCE",peer_head=signed["peer_head"],prior_replay_sha256=prior_id,
                replay_sha256=REPLAY,outputs=signed["output_sha256"],invoice=invoice,caller=physical["caller"],native_calls=[36,48],
                cap=app["binary_ordinary"],claim=app["claim"],tested=signed["tested"],gain_vs_previous=str(claim-prev_k),
                percent_vs_previous=str(100*(claim-prev_k)/prev_k),gain_vs_peer=str(claim-peer_k),percent_vs_peer=str(100*(claim-peer_k)/peer_k),
                previous_ceiling_separation=str(gap),ordinary_stages=rows,moment_endpoints=endpoint_ratios,outer=outer,
                known_good=["8027","normalized_uniform"],rejections=["terminal_numerator_minus_one","extra_paid_rank_one","cap_equals_tested"],
                premises=app["premises"])


if __name__=="__main__":
    check(sys.implementation.name=="cpython" and sys.version_info[:2]==(3,12) and __debug__,"CPython 3.12 with assertions")
    parser=ArgumentParser()
    for k in ("peer","prior-accept","prior-run","run","primary","independent","out"):
        parser.add_argument("--"+k,type=Path,required=True)
    a=parser.parse_args()
    result=main(a)
    with a.out.open("x") as f:
        json.dump(result,f,sort_keys=True,indent=2)
        f.write("\n")
    print(result["outcome"],result["claim"],result["gain_vs_previous"])
