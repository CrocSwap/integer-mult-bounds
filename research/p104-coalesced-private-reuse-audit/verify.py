#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only exact successor replay. Frozen predecessor files stay unchanged."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import importlib.util
import json
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
R = module("p104_successor_construction", HERE/"construction.py")
require = R.require

def unpack(destination):
    manifest = json.loads((HERE/"inputs/SOURCE-EXPORT.json").read_text(encoding="utf-8"))
    require(manifest["source_head"] == "05f7aad0f08992ee48ec2dd93e896d9a4567847d", "wrong PR2152 head")
    require(manifest["reuse_head"] == "3f913bc17276b68f0c9008a1202b6ce588e77ff6", "wrong PR2219 head")
    require(hashlib.sha256((HERE/"inputs/PR2219-fanout-helper-reuse.patch").read_bytes()).hexdigest()
            == manifest["reuse_patch_sha256"], "PR2219 patch drift")
    expected = manifest["files"]
    with tarfile.open(HERE/"inputs/pr2152-source.tar.gz", "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == len(expected) and {m.name for m in members} == set(expected),
                "source export inventory changed")
        for m in members:
            p = PurePosixPath(m.name)
            require(m.isfile() and not p.is_absolute() and ".." not in p.parts and "\\" not in m.name,
                    "unsafe source member")
            data = archive.extractfile(m).read()
            require(hashlib.sha256(data).hexdigest() == expected[m.name], "source drift: "+m.name)
            target = destination.joinpath(*p.parts)
            require(target.resolve().is_relative_to(destination.resolve()), "source escapes export")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return manifest

def summarize(built):
    report = dict(built["report"])
    report["public_widths_sha256"] = R.digest(report.pop("complete_public_widths"))
    report["total_transport_rank_mass"] = report["public_rank_mass"]+report["private_rank_mass"]
    return report

def combined(built):
    r=built["report"]
    c=Counter({int(k):v for k,v in r["public_profile"].items()})
    c.update({int(k):v for k,v in r["private_profile"].items()})
    return c

def prices(src, base, baseline, retained, released):
    B=module("p104_frozen_budget", src/"budget.py")
    engine, _, _, _=B.load_inputs()
    H=module("p104_frozen_hosting", src/"hosting.py")
    hosting=H.verify(base["report"])
    widths=[retained["report"]["complete_public_widths"][r] for r in hosting["actual_ordinary_registers"]]
    require(hosting["actual_ordinary_widths_sha256"]==R.digest(widths), "conditional owner widths differ")
    idle={int(k):Q(v,144) for k,v in hosting["remaining_idle_profile"].items()}
    require(sum(r*c for r,c in idle.items())==818, "inherited residual invoice differs")
    coverage=(B.M-1)*Q(B.FAMILIES,B.STAGES)+B.CENTRE
    selected_a=B.SELECTED_KAPPA/(1-B.SELECTED_KAPPA)
    target=B.SELECTED_KAPPA*Q(101,100)
    target_a=target/(1-target)
    def price(name,built,concrete):
        profile=combined(built)
        if concrete:
            profile.update(idle)
            require(sum(r*c for r,c in profile.items())==coverage, "local-plus-idle mass mismatch")
        model=engine.model(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE)
        if concrete: require(model["idle_mass"]==0, "unpriced residual mass")
        bracket=engine.ceiling(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE)
        lo=engine.relax(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE,bracket[0])
        hi=engine.relax(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE,bracket[1])
        require(lo[1]<1<hi[0], "uncertified root signs")
        sm=engine.relax(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE,selected_a)
        tm=engine.relax(profile,B.M,B.FAMILIES,B.STAGES,B.CENTRE,target_a)
        require(tm[0]>1, "one-percent target no longer excluded")
        cap=min(bracket[1]/(1+bracket[1]),B.BIT_LOWER/(1+B.BIT_LOWER))
        return {"name":name,"idle_model":"actual inherited window invoice" if concrete else "optimistic fractional rank-51",
                "priced_profile":{str(k):str(v) for k,v in sorted(profile.items())},
                "model":{k:str(v) for k,v in model.items()},
                "root_interval":[str(q) for q in bracket],
                "kappa_upper_bound":str(cap),"kappa_upper_decimal":B.decimal(cap),
                "relative_to_selected_percent":B.decimal(100*(cap/B.SELECTED_KAPPA-1)),
                "moment_at_selected":[str(q) for q in sm],"selected_threshold_excluded":sm[0]>1,
                "moment_at_one_percent_target":[str(q) for q in tm],"one_percent_target_excluded":True}
    costs=[price("baseline_ideal",baseline,False),price("retained_ideal",retained,False),
           price("released_ideal",released,False),price("baseline_hosted",baseline,True),
           price("retained_hosted",retained,True)]
    require(all(c["selected_threshold_excluded"] for c in costs if c["name"].endswith("_hosted")),
            "conditional invoice no longer rejects selected threshold")
    require(Q(costs[3]["moment_at_selected"][0])>Q(costs[4]["moment_at_selected"][1]),
            "billed improvement not separated exactly")
    host={k:hosting[k] for k in ("assigned_roles","total_calls","actual_ordinary_widths_sha256",
                                 "assignment_sha256","remaining_idle_profile")}
    host.update(per_call_idle_rank_mass="818", global_emitter_admitted=False,
                valid_for_variant="boundary_retained only; every public boundary and complete width retained")
    return costs,host,str(B.SELECTED_KAPPA)

def construct(root, *, native=True):
    src=root/"research/p104-interleaved-search"
    C=module("p104_frozen_coalesced",src/"coalesced.py")
    original=C.F.construct()
    base=C.construct(baseline=original)
    live=set(range(112))-set(C.QC.REMOVED)
    original_scalar, coalesced_scalar=R.scalar_events(original),R.scalar_events(base)
    require(len(original_scalar)==len(coalesced_scalar), "predecessor scalar lengths differ")
    changes=[]
    for k,(a,b) in enumerate(zip(original_scalar,coalesced_scalar)):
        require({x:v for x,v in a.items() if x!="frame"}=={x:v for x,v in b.items() if x!="frame"},
                "coalescing changed scalar semantics")
        if a["frame"]!=b["frame"]: changes.append(k)
    require(len(changes)==339, "expected 339 predecessor frame changes")
    baseline=R.replay(coalesced_scalar,base["initial"],base["final"],live)
    require(baseline["report"]["public_profile"]==base["report"]["candidate_public_profile"]
            and baseline["report"]["private_profile"]==base["report"]["private_COPY_profile"],
            "independent baseline replay disagrees")
    events,lineage=R.transform(base)
    require(set(changes).isdisjoint(lineage["removed_scalar_indices"])
            and set(changes)<=set(lineage["retained_scalar_indices"]), "lost coalesced frame change")
    retained=R.replay(events,base["initial"],base["final"],live)
    released_final=list(base["final"]);released_final[R.HELPER]=R.ZERO
    released=R.replay(events,base["initial"],released_final,live)
    require(retained["report"]["complete_public_widths"]==baseline["report"]["complete_public_widths"],
            "retained-boundary candidate changed lifetime widths")
    require(combined(retained)==combined(baseline)-Counter({2:1,7:1})+Counter({9:1}),
            "H2+H7 to H9 invoice changed")
    require(combined(released)==combined(baseline)-Counter({2:1,7:1}), "H2+H7 removal changed")
    require(retained["report"]["scalar_adds"]==released["report"]["scalar_adds"]==20947
            and baseline["report"]["scalar_adds"]==20956, "nine-ADD delta changed")
    old_events,_=R.transform(original)
    old_final=list(original["final"]);old_final[R.HELPER]=R.ZERO
    old_reuse=R.replay(old_events,base["initial"],old_final,live)
    require(combined(old_reuse)==Counter({1:2611,2:513,3:378,4:132,5:81,6:15,7:13})
            and old_reuse["report"]["public_rank_mass"]+56==5885, "PR2219 replication differs")
    controls={}
    for fault in ("omit_contact","contact_coefficient","ascending_private","retain_dirty_compensation"):
        bad,_=R.transform(base,fault=fault)
        try: R.replay(bad,base["initial"],released_final,live)
        except ValueError as error:
            if fault in ("omit_contact", "contact_coefficient", "retain_dirty_compensation"):
                require(str(error).startswith("exact endpoint mismatch"),
                        "semantic control did not reach the endpoint check: "+fault)
            controls[fault]=str(error)
        else: raise ValueError("semantic negative control accepted: "+fault)
    try: R.replay(events,base["initial"],released_final,live,fault="missing_private_init")
    except ValueError as error: controls["missing_private_init"]=str(error)
    else: raise ValueError("missing private initialization accepted")
    native_reports={}
    if native:
        N=module("p104_frozen_native_checker",src/"native_checks.py")
        for name,built in (("boundary_retained",retained),("helper_released",released)):
            print("Checking native operators:",name,flush=True)
            nr=N.verify(R.native_witness(built,base["ports"]))
            require(nr["paid_profile"]=={str(k):v for k,v in sorted(combined(built).items())},
                    "native profile does not bind new word")
            require(nr["private_paths"]==8 and nr["private_path_gaussian_columns"]==4096,
                    "native private Gaussian coverage incomplete")
            native_reports[name]=nr
    costs,host,selected=prices(src,base,baseline,retained,released)
    for path,digest in json.loads((HERE/"inputs/SOURCE-EXPORT.json").read_text())["files"].items():
        require(hashlib.sha256((root/path).read_bytes()).hexdigest()==digest, "frozen source modified")
    return {"status":"PASS_P104_COALESCED_PRIVATE_REUSE",
            "scope":"Finite exact forward composition plus native operators and conditional local+idle invoices; no admitted supplier or new kappa.",
            "predecessors":{"2152":"05f7aad0f08992ee48ec2dd93e896d9a4567847d","2219":"3f913bc17276b68f0c9008a1202b6ce588e77ff6"},
            "baseline":summarize(baseline),"original_word_reuse_control":summarize(old_reuse),
            "boundary_retained":summarize(retained),"helper_released":summarize(released),
            "composition":{"retained_coalesced_frame_changes":339,"removed_by_phase":lineage["removed_by_phase"],
                           "private_contacts":lineage["contact_frames"],"private_source":133,"private_register":738,"unused_helper":711,
                           "retained_boundary_delta":{"2":-1,"7":-1,"9":1},"released_boundary_delta":{"2":-1,"7":-1},
                           "strict_cost_comparison":"For 0<a<1, (2/m)^(1-a)+(7/m)^(1-a)>(9/m)^(1-a); equal at a=0."},
            "negative_controls":controls,"native_checks":native_reports,"costs":costs,"selected_kappa":selected,
            "conditional_hosting":host,"frozen_sources_unchanged":True,
            "full_selected_cold_replay":False,"new_kappa_claimed":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-result",action="store_true")
    args=ap.parse_args();start=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="p104-coalesced-reuse-") as tmp:
        root=Path(tmp);unpack(root)
        result=construct(root,native=True)
    if args.write_result:
        (HERE/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    else:
        require(result==json.loads((HERE/"RESULT.json").read_text(encoding="utf-8")), "stored receipt differs")
    for row in result["costs"]:
        print(row["name"],"kappa upper",row["kappa_upper_decimal"],"relative %",row["relative_to_selected_percent"],flush=True)
    print(result["status"],"columns=735 coalesced_changes=339 semantic_controls=5",
          "native=True","seconds="+str(round(time.perf_counter()-start,3)),flush=True)

if __name__=="__main__": main()
