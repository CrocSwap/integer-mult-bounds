#!/usr/bin/env python3
"""Exact additional-H1 budget of an explicitly unrealized target relaxation.

Reuses the prior independently written p19 interval engine, not Astra's author
engine. It is independent arithmetic relative to the design receipt, not an
independent native or caller proof. Apache-2.0; OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import ast
import importlib.util
import json
import re

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def require_profile(actual, expected):
    need(actual == expected, "Profile does not match frozen source-derived offer and declared p2 incidence")


def require_unrealized_status(status):
    need(status == "AUTHOR_DESIGN_OPTIMISM_ONLY_UNREALIZED_TARGET_GRANT", "Unrealized target status lost")


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
    for item in sources:
        need(sha256((HERE / item["snapshot"]).read_bytes()).hexdigest() == item["sha256"], "Source bytes changed")
    author = json.loads((HERE / "frozen/AUTHOR-OPTIMISTIC-SCREEN.json").read_text())
    require_unrealized_status(author["status"])
    proposal = (HERE / "frozen/FAILED-PREDECESSOR-PROPOSAL.md").read_text()
    base_paid = ast.literal_eval(re.search(r"`P=(\{[^\n]+\})`", proposal).group(1))
    targets = ast.literal_eval(re.search(r"`T=(\{[^\n]+\})`", proposal).group(1))
    need("required h endpoint fails" in proposal, "Failed predecessor boundary must be retained")
    paid = dict(base_paid)
    paid[8] += 2  # One hypothetical newly paid H8 per FULL; no H1 removed.
    need(base_paid == {1:4754,2:824,3:1020,4:254,5:80,8:224}, "Original p2 conditional invoice")
    need(paid == {int(r):n for r,n in author["conditional_paid_minimum"].items()}, "Design invoice must equal old+2H8")
    need(targets == {int(r):n for r,n in author["target_grant"].items()}, "Target grant changed")
    producer = json.loads((HERE / "frozen/SOURCE-DERIVED-PRODUCER.json").read_text())
    need(producer["source_head"] == "86e474038e05f99a76d41f71d81946ad2327e4a4", "Producer source pin")
    need(producer["status"] == "SOURCE_DERIVED_ONE_CENTRE_RESTORE_ALL_EIGHT_RANK1_REPAIRS_RETAINED", "Corrected producer only")
    local = {int(r):n for r,n in producer["paid_profile"].items()}
    need(local == {int(r):n for r,n in producer["backward"]["paid_profile"].items()}, "Both local orientations carry same complete rank profile")
    reconstructed = {r:2*n for r,n in local.items()}
    reconstructed[1] += 3*112
    reconstructed[8] += 224
    require_profile(paid,reconstructed)
    helpers = {4:56,7:14,8:94,9:652}
    rebuilt = dict(helpers)
    rebuilt[9] += 224
    rebuilt[17] = 224
    need(targets == rebuilt and sum(helpers.values()) == 816 and sum(targets.values()) == 1264, "Helpers once and448unproved main grants")
    need(paid[1] == 2 * (2201 + 8) + 3 * 112, "All8H1repairs perFULL retained; three thin banks")
    a, b = map(Q, author["C_domain"])
    need(a == Q(".0030217758") and b == Q(".00339999"), "Declared exact domain")
    need(0 <= a <= b <= Q(17,5000), "Interval engine domain")
    need(all(1 <= r <= 17 and isinstance(n,int) and n >= 0 for hist in (targets,paid) for r,n in hist.items()), "Rank/multiplicity bound")
    # ln r <= ln17<3 because a finite positive exp(3) partial sum exceeds17.
    term, exp3_lower = Q(1), Q(1)
    for j in range(1, 6):
        term *= Q(3,j)
        exp3_lower += term
    need(exp3_lower > 17 and 3*b < Q(1,50), "Reused alternating-series range explicitly checked")
    path = HERE / "frozen/independent_engine.py"
    spec = importlib.util.spec_from_file_location("frozen_independent_p19", path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)  # Its main never runs.
    values = {}
    for c in (a,b):
        tl,tu = engine.moment(targets,c)
        pl,pu = engine.moment(paid,c)
        lo,hi = tl-pu,tu-pl
        old = author["points"][str(c)]
        need(lo <= Q(old["exact_lower"]) <= Q(old["exact_upper"]) <= hi, "Author point enclosed independently")
        values[str(c)] = engine.interval(lo,hi)
        if c == b:
            right_lo,right_hi = lo,hi
    # M'=sum P[r] H_r ln r - sum T[r] H_r ln r.
    # Positive factors decrease in C; bound paid at a, targets at b.
    derivative_upper = sum((n*engine.rankpower(r,a)[1]*engine.logint(r)[1] for r,n in paid.items()),Q(0))
    derivative_upper -= sum((n*engine.rankpower(r,b)[0]*engine.logint(r)[0] for r,n in targets.items()),Q(0))
    need(derivative_upper < 0, "Uniform derivative sign; not point extrapolation")
    need(12 < right_lo <= right_hi < 13, "Sharp uniform integerH1budget")
    need(right_lo - 12 > 0 and right_hi - 13 < 0, "Twelve pass,thirteen fails at included endpoint")
    rank12_upper = engine.rankpower(12,a)[1]
    rank13_lower = engine.rankpower(13,b)[0]
    need(rank12_upper < right_lo, "One extra rank12 child fits throughout domain")
    need(rank13_lower > right_hi, "One extra rank13 child fails at right endpoint")
    # Mutated invoices/status must be rejected against independently bound inputs.
    wrong_paid = dict(paid)
    wrong_paid[1] -= 16
    rejected = []
    for name,bad in [("omit2H8",base_paid),("subtract16H1",wrong_paid)]:
        try:
            require_profile(bad,reconstructed)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Failed invoice rejection:"+name)
    try:
        require_unrealized_status("ADMITTED_PHYSICAL_TARGETS")
    except ValueError:
        rejected.append("promote_unrealized_target_grant")
    else:
        raise ValueError("Failed target status rejection")
    result = {
        "status":"PASS_INDEPENDENT_ARITHMETIC_FOR_UNREALIZED_TARGET_RELAXATION",
        "C_domain":[str(a),str(b)],"targets_unrealized_grant":targets,"paid_conditional_minimum":paid,
        "helpers_credited_once":816,"unproved_independent_main_grant":448,
        "added_paid_H8":2,"removed_H1":0,
        "source_derived_local_profile_matches":True,
        "point_enclosures":values,
        "uniform_derivative_strict_upper":engine.interval(derivative_upper,derivative_upper)["outward_upper"],
        "uniform_minimum_at":"included right endpoint by strict negative derivative",
        "maximum_additional_integer_H1_calls_uniformly":12,
        "maximum_number_of_positive_rank_additional_calls":12,
        "maximum_rank_of_one_additional_child_uniformly":12,
        "rank12_uniform_margin_lower":engine.interval(right_lo-rank12_upper,right_lo-rank12_upper)["outward_lower"],
        "rank13_right_endpoint_margin_upper":engine.interval(right_hi-rank13_lower,right_hi-rank13_lower)["outward_upper"],
        "uniform_margin_after12_H1":engine.interval(right_lo-12,right_hi-12),
        "right_endpoint_margin_after13_H1":engine.interval(right_lo-13,right_hi-13),
        "additional_general_bill_gate":"K(C)<M(C); H1budget is not a finite-work/routing/precision budget",
        "compiler_reserve_epsilon":None,"both_paid_tails_funded":False,
        "source_invoice_of_actual_corrected_caller_bound":False,
        "native_or_caller_run":False,"compiler_or_Lean_run":False,"new_kappa":None,
        "engine_provenance":"Source-reused independently written p19 rational engine; author-design engine not imported",
        "sources":sources,
        "rejected_controls":rejected
    }
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
