#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact necessary cost ledger for the nonzero-entrance lender experiment.

No supplier admission or new kappa. Optional input profiles are accounting
assumptions until separately replayed. Tekalign (@tekuuu), with substantial
OpenAI Codex assistance; builds on PR2226, PR2269 and PR2339.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / "anticipatory-stage-evidence"
B = Q("0.0016971949509017704265940818773")
WIDTHS = (4, 5, 7, 8, 9)
STOCK = (49728, 33152, 33152, 33152)
Y = tuple(map(Q, ("0.0157419492", "0.0314838986", "0.0335258407", "0.0341671924",
                  "-0.0154945984", "-0.0228029209", "-0.0279095922", "-0.0157419495", "-0.0035743069")))
PINS = {
    "budget/verify_nine_capacity.py": "a9a465cfdaca7a12d0b7e93f6e1b8b9badf4269fffe48934dec5c1353c3e36a4",
    "interface/RESULT.json": "714764e6bd7a0c48f0515c0756cf940b3980a8e097547c4bff9958240f1c3f70",
    "interface/base/CANONICAL-WORD.json.gz": "1509ba85b7bd16002845233310e39e1dd79b256deedf17be2ab1e4865f0a9fb8",
    "interface/extra/CANONICAL-WORD.json.gz": "5e041b0a9efcf0e98a87a6a48a57096bf6eb187576ccf11fd5fd71d56650c0bc",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path, expected):
    need(digest(path) == expected, "source pin mismatch")


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ledger(profile, widths):
    need(all(isinstance(r, int) and 1 <= r <= 51 and type(n) is int and n > 0 for r, n in profile.items()), "invalid paid profile")
    need(all(type(n) is int and n >= 0 for n in widths.values()), "invalid helper inventory")
    need(all(w in WIDTHS for w, n in widths.items() if n), "helper width outside dual coverage")
    mass = sum(r*n for r, n in profile.items())
    width = sum(w*n for w, n in widths.items())
    delta = mass - width - 1856
    return dict(local_mass=mass, helper_width_sum=width, mass_minus_width=mass-width,
                extra_mass_per_call=delta, global_deficit=23680-666*delta)


def main():
    need(__debug__, "Optimized Python unsupported by inherited exact engines")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--case", type=Path, help="JSON with complete local_profile and width_inventory; may include additional paid children, but do not omit them")
    args = parser.parse_args()
    for name, expected in PINS.items():
        pin(OLD / name, expected)
    v = load(OLD / "budget/verify_nine_capacity.py", "nonzero_lender_capacity")
    for name, expected in v.PARENT_PINS.items():
        pin(v.PARENT / name, expected)
    plan = read(v.PARENT / "new/PLAN.json")
    need(tuple(plan[k] for k in ("K", "L", "M", "T", "live", "deficit")) == (4, 9, 73, 74, 66304, 23680), "parent geometry")
    stock = Counter(x[0] for x in plan["windows"].values())
    need(tuple(112*stock[r] for r in (8,16,32,48)) == STOCK and len(plan["provider_calls"]) == 666, "parent stock")
    need(73*66304 - sum(r*n for r,n in zip((8,16,32,48),STOCK)) - 666*1856 == 23680, "baseline deficit identity")
    native = read(OLD / "interface/RESULT.json")
    cases = {}
    for tag in ("base", "extra"):
        c = read(OLD / f"interface/{tag}/CANONICAL-WORD.json.gz")
        widths = Counter(len(c["frames"][c["final"][r]]) - len(c["frames"][c["start"][r]]) for r in range(2*c["v"],2*c["v"]+c["R"]))
        profile = {int(r):n for r,n in c["local_profile"].items()}
        need(c["local_profile"] == native["records"][tag]["local_profile"], "native profile mismatch")
        need(widths == {4:4,5:4,7:36,8:84,9:272}, "baseline width inventory")
        need(ledger(profile,widths)["mass_minus_width"] == 1856, "baseline local identity")
        cases[tag] = dict(profile=profile, widths=dict(widths))
    if args.case:
        supplied = read(args.case)
        proposed = supplied.get("cases", {"single": supplied})
        for name, row in proposed.items():
            cases["supplied/"+name] = dict(profile={int(r):n for r,n in row["local_profile"].items()},
                                         widths={int(w):n for w,n in row["width_inventory"].items()})
    controls = []

    def rejects(label, fn, reason):
        try:
            fn()
        except ValueError as exc:
            need(str(exc) == reason, "wrong negative control reason")
        else:
            raise ValueError("negative control accepted")
        controls.append(label)

    bad = dict(cases["extra"]["widths"]); bad[3] = -1
    rejects("cannot remove nonexistent width3 helper", lambda: ledger(cases["extra"]["profile"],bad), "invalid helper inventory")
    paid = dict(cases["extra"]["profile"]); paid[1] += 2
    need(ledger(paid,cases["extra"]["widths"])["global_deficit"] == 22348, "paid pair mass penalty")
    controls.append("two additional rank1 children decrease deficit by1332")
    reports = {}
    fixed = sum(n*y for n,y in zip(STOCK,Y[:4]))
    for filename, expected in v.ENGINES.items():
        pin(v.INHERITED / filename, expected)
        engine = load(v.INHERITED / filename,"nonzero_"+filename[:-3])
        cost = {r:v.E(r,B,engine) for r in range(1,52)}
        lower = [Q(0)]
        for total in range(1,74):
            lower.append(min(lower[total-r]+cost[r][0] for r in range(1,min(51,total)+1)))
        count, slack = v.check_dual(Y,lower)
        need(count == 5927,"pattern coverage")
        output = {}
        for tag, case in cases.items():
            account = ledger(case["profile"],case["widths"])
            padding = fixed+666*sum(case["widths"].get(w,0)*y for w,y in zip(WIDTHS,Y[4:]))
            lo = 666*sum(n*cost[r][0] for r,n in case["profile"].items())
            hi = 666*sum(n*cost[r][1] for r,n in case["profile"].items())
            margin_lo,margin_hi = lo+padding-account["global_deficit"],hi+padding-account["global_deficit"]
            item = dict(accounting=account, certified_padding_excess_lower_bound=str(padding),
                        lower_bound_margin=v.iv(margin_lo,margin_hi),
                        conclusion="REJECTED_BY_NECESSARY_BOUND" if margin_lo > 0 else "NOT_REJECTED_BY_THIS_DUAL_NOT_AN_ADMISSION")
            if tag in ("base", "extra"):
                need(margin_lo > 0,"baseline calibration")
                threshold=[]
                for n in (1,16):
                    for pairs in sorted({0,1,n}):
                        # Conditional accounting only: delete n width8 helpers,
                        # remove 8n local rank mass, then add 2*pairs rank1 calls.
                        # The required saving is measured before these paid calls.
                        tlo=margin_lo/666-n*Y[7]+pairs*(2+2*cost[1][0])
                        thi=margin_hi/666-n*Y[7]+pairs*(2+2*cost[1][1])
                        threshold.append(dict(aliases=n,additional_rank1_down_up_pairs=pairs,
                                              global_deficit=23680-1332*pairs,
                                              required_gross_local_excess_saving_per_call=v.iv(tlo,thi)))
                item["conditional_break_even_requirements"] = threshold
            output[tag]=item
        bad=list(Y);bad[0]+=1
        rejects(filename+" infeasible dual",lambda:v.check_dual(bad,lower),"infeasible dual")
        need(v.E(1,Q(0),engine)==(0,0),"zero-rate positive control")
        controls.append(filename+" zero exponent gives zero excess")
        reports[filename]=dict(patterns=count, minimum_dual_slack=v.iv(slack,slack),cases=output,
                               exact_rank1_pair_cost_per_call=v.iv(2+2*cost[1][0],2+2*cost[1][1]))
    for tag in cases:
        a,z=(reports[name]["cases"][tag]["lower_bound_margin"] for name in v.ENGINES)
        need(max(Q(a["lower"]),Q(z["lower"])) <= min(Q(a["upper"]),Q(z["upper"])),"engine interval disagreement")
    rejects("forged baseline pin",lambda:pin(OLD/"interface/RESULT.json","0"*64),"source pin mismatch")
    receipt=dict(status="PASS_NONZERO_LENDER_NECESSARY_COST_ACCOUNTING_NO_CONSTRUCTION_CLAIM",
                 base="7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",seed=39,comparison_rate=str(B),
                 comparison_scope="Primitive comparison rate quoted from PR2374; no independent frontier or outer-conversion claim.",
                 dual=list(map(str,Y)),cases=cases,engines=reports,controls=controls,pins=PINS,
                 parent_pins=v.PARENT_PINS,engine_pins=v.ENGINES,
                 supplied_case_sha256=digest(args.case) if args.case else None,
                 conditional_table_scope="Necessary break-even only if each alias deletes one width8 helper and removes8 local rank mass before paid corrections. No such complete profile is asserted. Paid rank1 pairs may not actually be shareable.",
                 scope="Fixed nine-stage geometry; whole helper widths4,5,7,8,9; arbitrary full73banks and padding partitions rank<=51. This prices accounting assumptions, not new lender legality or native/global admission. Extra physical storage, source access and compiler work remain obligations; omitted costs are favorable.")
    if args.out:
        args.out.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"])
    for tag in cases:
        row=reports["moment.py"]["cases"][tag]
        print(tag,row["conclusion"],row["lower_bound_margin"]["decimal_lower_approx"])


if __name__ == "__main__":
    main()
