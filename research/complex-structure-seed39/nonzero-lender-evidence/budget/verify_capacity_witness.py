#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify finite fractional capacity witnesses for the target-lift cost model.

Actual single-alias profiles are bound to retained formal replay. Larger
profiles remain explicit extrapolations until separately constructed.
Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import price

HERE = Path(__file__).resolve().parent
PINS = {
    "price.py": "76f6b7c9d8fdfbf3c86726e2c34f5a13129717511e04876494bda94979474a1a",
    "../LIFTED-CANDIDATE.json": "f3a328fc259daa9d292a8d2b4ed6a125059ba14e5d10a1d3642763455d75da02",
    "../FOUR-CANDIDATE.json": "71dd95ccf4d8ef2e0122befc14ab17a1703bff3e6f2eafe23068dc7e7ca5e80f",
    "CAPACITY-WITNESSES.json": "d55bc83e642a1867fcecf3543555f781d4fa699413c2cc38f29a949f66e08d9c",
    "HIGH48-CAPACITY-WITNESSES.json": "1e775bbf74c6e2bd3d2444ba81c4d6fbb89349a90efc8793bde161e8ea73d8b0",
}
SAMPLE_PIN = "3f2533b0447fa7166b1008a52dd1f3dc6da3e16e3b87eaa277910bac5291b22c"
Y48 = tuple(map(Q, ("0.0083814601", "0.0167629203", "0.0335258407", "0.0341671924",
                    "-0.0154945984", "-0.0228029209", "-0.0131886139", "-0.0083814604", "-0.0035743069")))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def changed_profile(baseline, aliases, splits):
    h = Counter(baseline)
    h[3] -= aliases
    h[5] -= aliases
    h[1] += splits
    h[7] += splits
    h[8] -= splits
    need(all(n >= 0 for n in h.values()), "negative paid count")
    return {r:n for r,n in h.items() if n}


def check_capacity(rows, widths):
    stock = Counter()
    demand = Counter()
    idle = Counter()
    banks = Q(0)
    for row in rows:
        cap, pat, count = row["capacity"], row["pattern"], Q(row["copies"])
        need(cap in (8,16,32,48,73) and count > 0, "invalid capacity/count")
        need(len(pat) == 5 and all(type(n) is int and n >= 0 for n in pat), "invalid pattern")
        used = sum(w*n for w,n in zip(price.WIDTHS,pat))
        need(used <= cap, "overfilled bin")
        parts = row["padding"]
        need(all(type(r) is int and 1 <= r <= 51 for r in parts) and sum(parts) == cap-used, "incorrect residual padding")
        if cap == 73:
            need(sum(pat) > 0, "empty full bank")
            banks += count
        else:
            stock[cap] += count
        for w,n in zip(price.WIDTHS,pat):
            demand[w] += count*n
        for r in parts:
            idle[r] += count
    need(tuple(stock[r] for r in (8,16,32,48)) == price.STOCK, "stock mismatch")
    need(dict(demand) == {w:666*widths.get(w,0) for w in price.WIDTHS}, "demand mismatch")
    return idle,banks


def main():
    need(__debug__, "Optimized Python unsupported by inherited exact engines")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    for name,pin in PINS.items():
        price.pin(HERE/name,pin)
    for name,pin in price.PINS.items():
        price.pin(price.OLD/name,pin)
    sample_path=price.OLD/"selective-alias-evidence/RESULT.json"
    price.pin(sample_path,SAMPLE_PIN)
    v=price.load(price.OLD/"budget/verify_nine_capacity.py","lift_primal_helpers")
    for name,pin in v.PARENT_PINS.items():
        price.pin(v.PARENT/name,pin)
    plan=price.read(v.PARENT/"new/PLAN.json")
    need(tuple(plan[k] for k in ("K","L","M","T","live","deficit"))==(4,9,73,74,66304,23680),"parent geometry")
    stock=Counter(x[0] for x in plan["windows"].values())
    need(tuple(112*stock[r] for r in (8,16,32,48))==price.STOCK and len(plan["provider_calls"])==666,"parent stock")
    base48=price.read(sample_path)["records"]
    native=price.read(price.OLD/"interface/RESULT.json")["records"]
    baselines={}
    for provider,tag in (("gauge44","base"),("extra","extra")):
        row=base48[provider]["cases"][0]
        need(row["low_aliases"]==[],"wrong high48 baseline")
        baselines[(provider,"high48")]=dict(profile={int(r):n for r,n in row["local_profile"].items()},widths={int(w):n for w,n in row["width_inventory"].items()})
        baselines[(provider,"full80")]=dict(profile={int(r):n for r,n in native[tag]["local_profile"].items()},widths={4:4,5:4,7:36,8:84,9:272})
    actual=price.read(HERE/"../LIFTED-CANDIDATE.json")["cases"]
    bound=[]
    for row in actual:
        key=(row["provider"],row["baseline"])
        need(key in baselines,"unknown single case")
        base=baselines[key]
        expected=changed_profile(base["profile"],1,4)
        widths=dict(base["widths"]);widths[8]-=1
        need({int(r):n for r,n in row["local_profile"].items()}==expected=={int(r):n for r,n in row["replay"]["local_profile"].items()},"single profile delta mismatch")
        need({int(w):n for w,n in row["width_inventory"].items()}==widths,"single width delta mismatch")
        need(row["status"]=="PASS_FORMAL_LIFTED_TARGET_COMPENSATION_NO_NATIVE_OR_GLOBAL_ADMISSION" and row["replay"]["status"]=="PASS_EXACT_FREE_OPERATOR_BORROWING_REPLAY","single replay failed")
        need(row["replay"]["local_mass"]==sum(r*n for r,n in expected.items()),"single replay mass")
        need(price.ledger(expected,widths)["mass_minus_width"]==1856,"single deficit identity")
        bound.append("/".join(key))
    need(len(bound)==len(set(bound))==4,"single case coverage")
    bound_four=[]
    for row in price.read(HERE/"../FOUR-CANDIDATE.json")["cases"]:
        key=(row["provider"],row["baseline"])
        need(key in baselines,"unknown four case")
        base=baselines[key]
        expected=changed_profile(base["profile"],4,4)
        widths=dict(base["widths"]);widths[8]-=4
        need({int(r):n for r,n in row["local_profile"].items()}==expected=={int(r):n for r,n in row["replay"]["local_profile"].items()},"four profile delta mismatch")
        need({int(w):n for w,n in row["width_inventory"].items()}==widths,"four width delta mismatch")
        need(row["status"]=="PASS_FORMAL_FOUR_LIFTED_TARGET_ALIASES_NO_NATIVE_OR_GLOBAL_ADMISSION" and row["replay"]["status"]=="PASS_EXACT_FREE_OPERATOR_BORROWING_REPLAY","four replay failed")
        need(row["replay"]["local_mass"]==sum(r*n for r,n in expected.items()),"four replay mass")
        need(price.ledger(expected,widths)["mass_minus_width"]==1856,"four deficit identity")
        bound_four.append("/".join(key))
    need(len(bound_four)==len(set(bound_four))==4,"four case coverage")
    specimens={}
    for baseline,filename in (("high48","HIGH48-CAPACITY-WITNESSES.json"),("full80","CAPACITY-WITNESSES.json")):
        witness=price.read(HERE/filename)
        need(Q(witness["verification_rate"])==price.B,"witness rate")
        for number,rows in witness["rows"].items():
            aliases=int(number)
            for provider in ("gauge44","extra"):
                base=baselines[(provider,baseline)]
                widths=dict(base["widths"]);widths[8]-=aliases
                idle,banks=check_capacity(rows,widths)
                for splits in ((4,8) if baseline=="high48" else (8,)):
                    h=changed_profile(base["profile"],aliases,splits)
                    account=price.ledger(h,widths)
                    need(account["mass_minus_width"]==1856,"model rank identity")
                    live=Q(66304)+banks
                    mass=666*account["local_mass"]+sum(r*n for r,n in idle.items())
                    need(73*live-mass==23680,"global mass identity")
                    label=f"{provider}/{baseline}/aliases{aliases}/splits{splits}"
                    specimens[label]=dict(profile=h,widths=widths,idle=idle,banks=banks,live=live,aliases=aliases,splits=splits,
                                          actual_single_bound=aliases==1 and splits==4)
    controls=[]
    def rejects(label,fn,reason):
        try:fn()
        except ValueError as exc:need(str(exc)==reason,"wrong control reason")
        else:raise ValueError("mutation accepted")
        controls.append(label)
    honest_rows=price.read(HERE/"HIGH48-CAPACITY-WITNESSES.json")["rows"]["4"]
    w=dict(baselines[("extra","high48")]["widths"]);w[8]-=4
    bad=copy.deepcopy(honest_rows);bad[0]["copies"]=str(Q(bad[0]["copies"])+1)
    rejects("wrong pattern count",lambda:check_capacity(bad,w),"stock mismatch")
    bad=copy.deepcopy(honest_rows);bad[0]["padding"].append(1)
    rejects("unpaid padding",lambda:check_capacity(bad,w),"incorrect residual padding")
    engines={}
    for filename,pin in v.ENGINES.items():
        price.pin(v.INHERITED/filename,pin)
        engine=price.load(v.INHERITED/filename,"lift_primal_"+filename[:-3])
        cost={r:v.E(r,price.B,engine) for r in range(1,52)}
        lower=[Q(0)]
        for total in range(1,74):lower.append(min(lower[total-r]+cost[r][0] for r in range(1,min(51,total)+1)))
        count,slack=v.check_dual(Y48,lower)
        need(count==5927,"high48 dual coverage")
        output={}
        for label,s in specimens.items():
            lo=666*sum(n*cost[r][0] for r,n in s["profile"].items())+sum(n*cost[r][0] for r,n in s["idle"].items())-23680
            hi=666*sum(n*cost[r][1] for r,n in s["profile"].items())+sum(n*cost[r][1] for r,n in s["idle"].items())-23680
            item=dict(excess_minus_deficit=v.iv(lo,hi),moment=v.iv(1+lo/(73*s["live"]),1+hi/(73*s["live"])),
                      below_one=hi<0,actual_single_profile_bound=s["actual_single_bound"],
                      actual_four_profile_bound=s["aliases"]==4 and s["splits"]==4)
            if s["actual_single_bound"]:
                pad=sum(n*y for n,y in zip(price.STOCK,Y48[:4]))+666*sum(s["widths"].get(w,0)*y for w,y in zip(price.WIDTHS,Y48[4:]))
                dual_margin=666*sum(n*cost[r][0] for r,n in s["profile"].items())+pad-23680
                need(dual_margin>0,"actual single not rejected")
                item["certified_rejection_lower_bound"]=str(dual_margin)
            elif s["aliases"]>=4:
                need(hi<0,"extrapolated model capacity witness not favorable")
            output[label]=item
        engines[filename]=dict(cases=output,high48_dual_patterns=count,minimum_dual_slack=v.iv(slack,slack))
    for label in specimens:
        a,b=(engines[k]["cases"][label]["excess_minus_deficit"] for k in v.ENGINES)
        need(max(Q(a["lower"]),Q(b["lower"]))<=min(Q(a["upper"]),Q(b["upper"])),"independent intervals disagree")
    rejects("forged actual-single pin",lambda:price.pin(HERE/"../LIFTED-CANDIDATE.json","0"*64),"source pin mismatch")
    receipt=dict(status="PASS_EXACT_FRACTIONAL_CAPACITY_MODELS_ACTUAL_SINGLE_REJECTED_NO_NEW_KAPPA",
                 base="7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",seed=39,rate=str(price.B),
                 bound_actual_cases=bound,bound_actual_four_cases=bound_four,high48_dual=list(map(str,Y48)),engines=engines,controls=controls,
                 capacity_witnesses={label:dict(full73_banks=str(s["banks"]),live=str(s["live"]),idle={r:str(n) for r,n in s["idle"].items()},local_profile=s["profile"],helper_widths=s["widths"]) for label,s in specimens.items()},
                 pins=PINS,high48_sample_pin=SAMPLE_PIN,baseline_pins=price.PINS,parent_pins=v.PARENT_PINS,engine_pins=v.ENGINES,
                 scope="The one-alias/four-split and four-alias/four-split profiles are bound to actual formal replays here. Larger models assume repeated-H3-H5 savings, shared COPY splits and no extra cost. Fractional capacity feasibility omits timeline/family constraints, native/compiler/physical admission and outer transfer. The dimension<=4 pool supplies only10distinct restored lenders; dimension5 lenders require a separate census. No kappa claim.")
    if args.out:args.out.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"])
    for label in specimens:
        print(label,engines["moment.py"]["cases"][label]["excess_minus_deficit"]["decimal_upper_approx"])


if __name__=="__main__":main()
