#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the literal #7156 application delta and proposed conditional claim."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from moments import certified_price
from word import chart_checks, require, trace


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate():
    index = load(HERE / "INPUTS.json")["sources"]
    files = {p["file"] for p in index}
    require(len(files) == len(index) and files == {p.relative_to(HERE).as_posix() for p in
            (HERE / "inputs").rglob("*") if p.is_file()}, "Complete replay input inventory")
    for p in index:
        raw = (HERE / p["file"]).read_bytes()
        git_blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require((len(raw), sha256(raw).hexdigest(), git_blob) == (p["bytes"], p["sha256"], p["git_blob"]),
                "Exact input bytes for " + p["path"])


def invoice(word, caller, native):
    types = caller["types"]
    require(types["A"]["ports"] == word["hosted"]["Dports"] and
            sorted(types["A"]["ports"] + types["B"]["ports"]) == list(range(104)), "Disjoint exact ports")
    stages = caller["stages"]
    require(stages == 17 and caller["ambient_rank"] == 9 + 8*stages, "Seventeen disjoint stage planes")
    require([(types[t]["offset"], types[t]["roles"]) for t in ("A", "B")] == [(0, 36), (36, 36)],
            "Separate caller role sets")
    stage_order = []
    paid, target, macro = Counter(), Counter(), Counter()
    for e in caller["events"]:
        if e[0] == "J":
            _, s, a, b = e
            require(a == [s, 0, 18, 18+s] and b == [36, 37, "-1", "1/2"], "Exact A/B stage owners")
            stage_order.append(s)
            paid.update(native["paid"])
            target.update(native["helpers"])
            continue
        ty, op = e[:2]
        t = types[ty]
        ports = len(t["ports"])
        macro[op] += ports
        require(op in ("ADD", "SCALE", "SWAP", "LAMBDA", "QUERY", "IDLE_ONE", "IDLE_ODD"), "Caller alphabet")
        if op in ("IDLE_ONE", "IDLE_ODD"):
            slots = e[3]
            require(slots and len(set(slots)) == len(slots) and all(1 <= s <= stages for s in slots), "Valid idle stages")
            if op == "IDLE_ODD":
                require(ty == "B" and len(slots) == 1 and e[4:] == [-1], "One negative odd child")
            paid[8*len(slots)+(op == "IDLE_ODD")] += ports
        elif op == "QUERY":
            require(e[-1] in (-1, 1), "Signed query")
            paid[1] += ports
        elif op == "LAMBDA":
            require(e[-1] in (-1, 1), "Signed whole LAMBDA")
    require(stage_order == list(range(1, stages+1)), "Each stage called once in chronological order")
    for t in types.values():
        require(len(t["diagonal"]) == t["roles"], "All main fields have target rows")
        for sign, spare, *bits in t["diagonal"]:
            require(sign == -1 and spare == 0 and len(bits) == stages and set(bits) <= {0, 1} and any(bits),
                    "Signed nonempty root diagonal")
            target[abs(sign)+8*sum(bits)] += len(t["ports"])
    return paid, target, macro


def whole_lambda_control():
    # With X the exchange of the two coordinates, on v=(1,-1) the
    # Gaussian numerator (1+i)v+(1-i)Xv is 2i*v.
    v = (1, -1)
    numerator = [(v[j]+v[1-j], v[j]-v[1-j]) for j in range(2)]
    require(numerator == [(0, 2*x) for x in v], "One-axis eigenvalue i")

    def eigen_lambda(power_of_i):
        q_squared = 1 if power_of_i % 2 == 0 else -1
        return (1+q_squared)//2, (1-q_squared)//2

    whole, single = eigen_lambda(2), eigen_lambda(1)
    tensor = (single[0]**2-single[1]**2, 2*single[0]*single[1])
    require(whole == (1, 0) and tensor == (-1, 0), "Whole LAMBDA differs at multiplicity two")
    return {"whole": "+1", "axiswise": "-1"}


def scalars(word, caller, native_scale, caller_scale):
    engine = runpy.run_path(str(ROOT / "docs/research/pr-intake-evidence/pr7000-application/check_exact_scalar.py"))
    rational = engine["rational"]
    stages = caller["stages"]
    coefficients = Counter()
    for e in word["program"]:
        if e[0] in ("ADD", "COPY", "SCALE"):
            coefficients[Q(e[-2])] += stages
    for e in caller["events"]:
        if e[0] == "J":
            coefficients.update({Q(e[3][2]): len(caller["types"]["B"]["ports"]),
                                 Q(e[3][3]): len(caller["types"]["B"]["ports"])})
        elif e[1] in ("ADD", "SCALE"):
            coefficients[Q(e[-1])] += len(caller["types"][e[0]]["ports"])
        elif e[1] == "LAMBDA":
            # Real and imaginary components of the complete Gaussian factors.
            ports = len(caller["types"][e[0]]["ports"])
            coefficients[Q(1, 2)] += 2*ports
            coefficients[Q(1, 2)*e[-1]] += ports
            coefficients[-Q(1, 2)*e[-1]] += ports
    for scale, fields in [(native_scale, stages*word["public"]),
                          (caller_scale, sum(t["roles"]*len(t["ports"]) for t in caller["types"].values()))]:
        coefficients[Q(scale)] += fields
        coefficients[Q(1, scale)] += fields
    coefficients.update({Q(-1): 1, Q(1): 1})  # real/imaginary signs and unit phases
    num_bits = max(abs(q.numerator).bit_length() for q in coefficients)
    div_bits = max(q.denominator.bit_length() for q in coefficients)
    require((num_bits, div_bits) == (24, 20) and word["program"][2322][-2] == "-97039/655360",
            "Literal numerator and divisor bounds")
    valid = invalid = 0
    for q in sorted(coefficients):
        b = q.denominator
        for width in (1, 7, 25, 65):
            limit = (2**width-1)//b
            for m in {0, min(1, limit), limit//2, limit, -limit}:
                x = m*b
                require(rational(x, q, width) == x*q and abs(x*q.numerator) < 2**(width+24),
                        "All literal fixed coefficients and padded product bound")
                valid += 1
        if b > 1:
            try:
                rational(1, q, b.bit_length())
            except ValueError as error:
                require(str(error) == "nonzero exact-division remainder", "Expected exact-division guard")
                invalid += 1
            else:
                raise ValueError("Nonexact quotient accepted")
    return dict(distinct=len(coefficients), exact_cases=valid, remainder_controls=invalid,
                numerator_bits=num_bits, divisor_bits=div_bits, wide_divisor_example="-97039/655360")


def finite_bill(word, caller, paid, target, macro, result, native, numeric):
    checks = result["checks"]
    geometry = checks["ODD-PHYSICAL-BINDING.json"]["occurrence_and_geometry"]
    fixed = checks["ODD-FIXED-TAPE-COUNTS.json"]
    precision = checks["ODD-PRECISION.json"]
    stages = caller["stages"]
    n = caller["ambient_rank"]
    main = sum(len(t["ports"])*t["roles"] for t in caller["types"].values())
    native_helpers = stages*sum(native["helpers"].values())
    contacts = 4*stages*(len(caller["types"]["A"]["ports"]) + sum(len(t["ports"]) for t in caller["types"].values()))
    banks = stages*native["labels"]
    surplus = sum(r*(target.get(r, 0)-paid.get(r, 0)) for r in paid.keys() | target.keys())
    signed_idle = macro["IDLE_ODD"]
    require((n, sum(paid.values()), sum(target.values()), surplus, contacts, native_helpers, banks) ==
            (145, 110502, 22410, 1424, 13600, 18666, 1037), "Exact physical size and surplus")
    require((contacts, native_helpers, banks) ==
            (geometry["native_contact_boundaries"], geometry["fresh_helpers"], geometry["reserved_native_banks"])
            and geometry["reserved_serial_query_lambda_bank"] == 1 and native_helpers + main == sum(target.values()),
            "Physical receipt and stocks")
    require(macro["QUERY"] == geometry["query_uses"] and macro["LAMBDA"] == geometry["lambda_uses"]
            and macro["IDLE_ONE"]+signed_idle == geometry["idle_uses"], "Every paid or ordinary outer macro counted")
    native_admin = stages*(len(word["program"])-sum(native["paid"].values()))
    conversions = 2*(stages*word["public"]+main)
    services = 32*(native_admin+sum(macro.values())+conversions)
    maps = 2*(sum(paid.values())+sum(target.values())) + contacts + 2*geometry["idle_uses"]
    maps += 3*macro["QUERY"] + macro["LAMBDA"] + signed_idle
    records = maps*4*(n+1)**2
    require((services, services*2**20, maps, records) ==
            (fixed["scalar_services_upper"], fixed["scalar_steps_coefficient"],
             fixed["monomial_map_slots"], fixed["elementary_records_upper"]), "Full finite-tape tariff")
    require(fixed["common_grid"] == dict(fractional="p+D", signed_width="p+h+2D+3", temp_padding=26),
            "One common field and padded format")
    H = numeric["H"]
    context = precision["context_c"]
    K_star = 1920*153**1920*(H+1)**2
    require(context == fixed["context_c"] == 2430 <= 4096 and (4096*K_star).bit_length() < H,
            "Precision context fits funded carrier")
    require(all(v["strict_power_of_two"] < H for v in precision["rounded_caller"]["bounds"].values()),
            "Rounded caller envelope")
    ordinary = checks["ODD-ADMISSION-PARTIAL.json"]["ordinary"]
    source_units = sum(ordinary[k] for k in ("raw_upper", "per_input_conversion", "lambda_second_charge",
                                             "all_caller_scalar_surcharge", "charged_caller_odd_conversions"))
    require(source_units == ordinary["conservative_total"] == 781880696 < 10**9, "Complete source-unit ordinary bill")
    return dict(ambient=n, compiler_cap=153, paid=sum(paid.values()), productive=sum(target.values()), surplus=surplus,
                main=main, native_helpers=native_helpers, native_contacts=contacts, native_banks=banks,
                serial_scratch=1, ordinary=source_units, scalar_services=services, scalar_coefficient=services*2**20,
                monomial_maps=maps, elementary_records=records, precision_c=context)


def outer_claim(gate, selected, sources):
    outer = runpy.run_path(str(ROOT / "research/final4610-independent-admission/checks/outer.py"))
    k, C = Q(gate["claim"]), Q(gate["tested"])
    params = outer["parameters"](k, C)
    params["bit_saving"] = Q(gate["BIT_pin"])
    bit = Q(selected["admitted_BIT_saving"])
    require(params["bit_saving"] == Q(selected["complex_BIT_premise"]) and bit > params["bit_saving"] > C,
            "Exact retained BIT supplies the weaker premise")
    checks = outer["evaluate"](params)
    require(checks["all_positive"] and len(checks["strict_checks"]) == 54 and
            len(checks["functional_checks"]) == 4, "All strict and functional outer guards")
    effective = params["a"]
    for cap in (effective, effective-Q(1, 10**12)):
        reject = outer["evaluate"](params | {"bit_saving": cap})
        require(not reject["all_positive"] and reject["strict_checks"]["actual_bit_above_effective"] == cap-effective,
                "Actual outer gate rejects BIT at or below effective price")
    before = Q(selected["kappa"])
    previous = Q(".003644267085400")
    require(before < previous < k, "Both exact comparisons")
    limiting = min(checks["margins"].values())
    return dict(schema="conditional-frontier-proposal/1", source_heads=sources, kappa=k,
                delta_over_selected=k-before, delta_over_pr7155=k-previous,
                tested_complex_price=C, complex_uniform=dict(saving=params["complex_uniform_saving"],
                    rank_encoding="2^"+gate["H"], actual_raw_ambient=145, compiler_raw_ambient_cap=153),
                retained_bit_before_cover=selected["uniform_templates"][1], admitted_bit_saving=bit,
                complex_bit_premise=params["bit_saving"], outer_parameters=params,
                nine_outer_savings=checks["margins"], strict_limiting_slack=limiting-k,
                strict_count=54, functional_count=4, minimum_guard=min(
                    *checks["strict_checks"].values(), *checks["functional_checks"].values()),
                bit_at_and_below_effective_rejected=True, assumptions=selected["assumptions"])


def main():
    authenticate()
    word, parent = [load(HERE / "inputs" / pr / "WORD.json.gz") for pr in ("pr7156", "pr7155")]
    caller_file = HERE / "inputs/pr7113/CALLER.json"
    caller = load(caller_file)
    receipt = load(HERE / "inputs/pr7156/RESULT.json")
    native_receipt = load(HERE / "inputs/pr7156/NATIVE-RESULT.json")
    require(sha256(caller_file.read_bytes()).hexdigest() == receipt["caller_sha256"] and
            sha256(canonical(word)).hexdigest() == native_receipt["word_canonical_sha256"] == receipt["price"]["new_native"]
            and sha256(canonical(parent)).hexdigest() == receipt["price"]["old_native"], "Complete input and receipt bindings")
    native, base = trace(word), trace(parent)
    require((len(word["program"]), word["public"], native["labels"], native["lifetimes"], native["owned_peak"],
             native["owned_ascent_mass"]) == (76220, 1498, 61, 64, 47, 56), "Native census")
    chart = chart_checks(parent, word, load(HERE / "inputs/pr7156/WITNESS.json"),
                         load(HERE / "inputs/pr7156/PATHS.json"))
    paid, target, macro = invoice(word, caller, native)
    old_paid, old_target, _ = invoice(parent, caller, base)
    mutant = deepcopy(caller)
    row = next(e for e in mutant["events"] if e[0] == "J")
    row[2][0] = row[2][1]
    try:
        invoice(word, mutant, native)
    except ValueError as error:
        require(str(error) == "Exact A/B stage owners", "Expected aliased owner rejection")
    else:
        raise ValueError("Aliased main owners accepted")
    for p, t, name in [(paid, target, "after"), (old_paid, old_target, "before")]:
        price = receipt["price"][name]
        require(price["empty_root_credits"] == 0 and json.loads(canonical(p)) == price["P"]
                and json.loads(canonical(t)) == price["T"], "Complete "+name+" signed rank invoice")
    prior = old_target.copy()
    prior.subtract(old_paid)
    gate = receipt["price"]["gate"]
    num = certified_price(paid, target, prior, Counter({r: caller["stages"]*q for r, q in native["paid"].items()}),
                          caller["ambient_rank"], gate)
    grid = receipt["checks"]["ODD-FIXED-TAPE-COUNTS.json"]["caller_odd_scale"]
    native_grid = native_receipt["derived_grid"]
    require((grid, native_grid["odd_scale"], native_grid["fractional_bits"]) == (675, 1125, 25), "Two exact grids")
    scalar = scalars(word, caller, native_grid["odd_scale"], grid)
    bill = finite_bill(word, caller, paid, target, macro, receipt, native, num)
    sources = {f"pr{x['pr']}": x["commit"] for x in load(HERE / "INPUTS.json")["sources"]}
    selected = load(ROOT / "certificates/frontier7000/CLAIM.json")
    proposed = outer_claim(gate, selected, sources)
    report = dict(status="PASS_SOURCE_BOUND_7156_APPLICATION_REVIEW", chart=chart, numeric=num,
                  exact_scalars=scalar, finite_bill=bill, whole_lambda=whole_lambda_control(),
                  aliased_main_rejected=True, proposed=proposed)
    normalized = json.loads(json.dumps(report, default=str, sort_keys=True))
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT.json").write_text(json.dumps(normalized, indent=2, sort_keys=True)+"\n")
    else:
        require(not sys.argv[1:] and normalized == load(HERE / "RESULT.json"), "Full frozen review receipt")
    print(report["status"], str(proposed["kappa"]), "54+4", len(chart["collateral"]), scalar["divisor_bits"])


if __name__ == "__main__":
    main()
