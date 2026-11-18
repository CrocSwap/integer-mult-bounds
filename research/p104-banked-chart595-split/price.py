#!/usr/bin/env python3
"""Certify the signed crossing, compiler and outer predicates of the chart-595 split."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from caller import CALLER, CANDIDATE, ENGINE, INVOICE, PARENT, PARENT_HEAD, HERE, load, need


PARENT_UPPER = "0.0037261023901"
PARENT_LOWER = "0.0037261023900"
PARENT_CLAIM = "0.0037261023899"
TARGET = "0.00372611"
BIT_FLOOR = "0.00376669"
GAP = Fraction(1, 10**14)
CARRIER_POWER = 1920
AMBIENT_CAP = 153
ASSUMPTIONS = (
    "native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery",
)
PINS = {
    "directed_price.py": "446c8ebddf5b1e56d43b8d7f2ad3c1c9ba018a18105b207a0ac9e30386878a10",
    "interval_gate.py": "60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5",
    "selected-claim.json": "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2",
    "selected-bit-ambient.json": "437ad2f9e7956e7f2b477b546f53a6c8cfa0567e207024300e9a7e58d3c0202c",
    "selected-validation.json": "e1374a98b240d7f9f2cca2a1e74b93f240b1bfc94b8cc4b94a385a50281d494e",
}


def standing_bit_and_assumptions():
    for name, expected in PINS.items():
        need(sha256((ENGINE / name).read_bytes()).hexdigest() == expected, f"fixed pricing or selected input {name}")
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    claim = load(ENGINE / "selected-claim.json", PINS["selected-claim.json"])
    repair = load(ENGINE / "selected-bit-ambient.json", PINS["selected-bit-ambient.json"])
    validation = load(ENGINE / "selected-validation.json", PINS["selected-validation.json"])
    bit = next(x for x in claim["uniform_templates"] if x["family"] == "BIT before cover")
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
         and repair["exit_code"] == 0 and repair["source_unchanged"]
         and validation["status"] == "admitted_conditional"
         and validation["registered_replays_complete"], "selected ambient-corrected BIT anchor")
    need(tuple(x["id"] for x in claim["assumptions"]) == ASSUMPTIONS
         and Fraction(bit["saving"]) > Fraction("0.00385248") > Fraction(BIT_FLOOR),
         "five exact standing assumptions and conservative BIT floor")
    return {"ambient": bit["ambient"], "rank_encoding": bit["rank_encoding"],
            "source_template_saving": bit["saving"], "retained_completed_saving": "0.00385248",
            "outer_floor": BIT_FLOOR, "assumptions": claim["assumptions"],
            "selected_source_pins": {k: v for k, v in PINS.items() if k.startswith("selected-")}}


def histograms(invoice, targets):
    p = {int(k): v for k, v in invoice["paid"].items()}
    t = {int(k): v for k, v in invoice["targets"].items()}
    need(invoice["schema"] == "integer-mult-recursive-invoice/v1"
         and invoice["contract"]["ambient_rank"] == 137
         and all(1 <= rank <= 137 and type(count) is int and count > 0
                 for hist in (p, t) for rank, count in hist.items())
         and sum(p.values()) == 101824 and sum(t.values()) == targets,
         "complete paid and productive invoice input")
    diff = {k: t.get(k, 0) - p.get(k, 0) for k in p.keys() | t.keys()}
    need(sum(k * v for k, v in diff.items()) == 1328, "full rank-mass surplus")
    return p, t, diff


def checked_bills(application):
    need(application["status"] == "PASS_CHART595_ACTUAL16_CALLER"
         and application["parent_head"] == PARENT_HEAD
         and application["graphs"] == {"peer": PARENT, "candidate": CANDIDATE}
         and application["caller_sha256"] == CALLER
         and application["published_parent_invoice_sha256"] == INVOICE
         and application["signed"]["calls"] == 16 and application["signed"]["root_owners"] == 3536,
         "actual 16-call proof binds exactly #7682 and chart-595 child")
    invoice = load(HERE / "data/PARENT-INVOICES.json", INVOICE)["candidate"]
    need(application["invoices"]["peer"] == invoice
         and application["invoices"]["candidate"]["contract"] == invoice["contract"],
         "shared actual recursion model and frozen #7682 comparator")
    peer = histograms(invoice, 21152)
    child = histograms(application["invoices"]["candidate"], 21168)
    need(peer[0] == child[0] and {k: child[1].get(k, 0) - peer[1].get(k, 0)
                                 for k in child[1].keys() | peer[1].keys()
                                 if child[1].get(k, 0) != peer[1].get(k, 0)}
         == {1: 16, 8: 16, 9: -16},
         "an exact rank-nine debit with the two productive replacements and no new paid edge")
    return {"peer": peer, "candidate": child}


def decimal_tick(k, places):
    divisor = 10**places
    return f"{k // divisor}.{k % divisor:0{places}d}"


def find_crossing(coeff):
    from directed_price import moment

    ticks = 10**13
    low = int(Fraction(TARGET) * ticks)
    high = int(Fraction(BIT_FLOOR) * ticks)
    need(moment(coeff, Fraction(low, ticks), Fraction(low, ticks))[0] > 0
         and moment(coeff, Fraction(high, ticks), Fraction(high, ticks))[1] < 0, "strict new crossing bracket")
    while high - low > 1:
        mid = (high + low) // 2
        point = Fraction(mid, ticks)
        left, right = moment(coeff, point, point)
        if left > 0:
            low = mid
        elif right < 0:
            high = mid
        else:
            raise ValueError("directed root enclosure overlaps zero at a bracket tick")
    lower = decimal_tick(low, 13)
    upper = decimal_tick(high, 13)
    claim_ticks = int(Fraction(lower) * 10**10)
    if Fraction(claim_ticks, 10**10) + 7 * GAP >= Fraction(lower):
        claim_ticks -= 1
    claim = decimal_tick(claim_ticks, 10)
    need(Fraction(claim) > Fraction(TARGET) > Fraction(PARENT_UPPER), "strict conservative chosen lower")
    return claim, lower, upper


def check_numerics(bill, triple, kind):
    from directed_price import moment
    from interval_gate import gate, moment as second_moment, B

    paid, targets, coeff = bill
    claim, lower, upper = triple
    k = Fraction(claim)
    probe = k + 7 * GAP
    points = {claim: 1, str(probe): 1, lower: 1, upper: -1, BIT_FLOOR: -1,
              PARENT_UPPER: -1 if kind == "peer" else 1, TARGET: -1 if kind == "peer" else 1}
    verified = {}
    for point, sign in points.items():
        first = moment(coeff, Fraction(point), Fraction(point))
        second = tuple(Fraction(bound, B) for bound in second_moment(coeff, Fraction(point)))
        for interval in (first, second):
            need(interval[0] > 0 if sign > 0 else interval[1] < 0, f"two strict directed signs at {point}")
        need(max(first[0], second[0]) <= min(first[1], second[1]), "independent directed intervals intersect")
        verified[point] = {"sign": sign, "binary_log_exp": list(map(str, first)),
                           "decimal_fixed_grid": list(map(str, second)),
                           "display": list(map(float, first))}
    derivative = moment(coeff, Fraction(), Fraction(BIT_FLOOR), derivative=True)
    need(derivative[1] < 0, "strictly decreasing moment up to the independent BIT floor")
    compiler = gate({"P": paid, "T": targets}, claim, probe, lower, upper, BIT_FLOOR)
    outer = compiler["outer"]
    need(outer["strict_count"] == 54 and outer["functional_count"] == 4
         and Fraction(outer["minimum_margin"]) > 0
         and outer["BIT_just_below_effective_rejected"], "all strict and functional outer predicates")
    return {"decimal_claim": claim, "bracket": [lower, upper],
            "directed_checks": verified, "derivative": list(map(str, derivative)), "compiler": compiler,
            "recurrence_anchors": {
                "carrier_power": CARRIER_POWER, "conservative_ambient_cap": AMBIENT_CAP,
                "paid_cutoff": 11, "target_floor": 12, "tail_power_offset": "1/7",
                "tail_ratio_upper": "31/32", "alpha_reserve": str(Fraction(1, 10**27)),
                "claim_and_probe_increment": str(GAP), "test_increment_count": 7,
                "b": str(k + 5 * GAP), "a": str(k + 4 * GAP), "q": str(k + 3 * GAP),
                "epsilon": str(1 - GAP), "beta": str(1 - 3 * GAP)}}


def check_physical(path, application, calculations):
    physical = load(path)
    need(physical["status"] == "PASS_CHART595_BANK_PHYSICAL"
         and physical["graphs"] == application["graphs"] and physical["caller_sha256"] == CALLER,
         "ordinary and exact grid are bound to the actual same graph and caller")
    common = physical["common_exact_root"]
    c = common["context_c"]
    need(type(c) is int and c >= 2 * max(common["context_mass_bits"], common["context_binary_bits"])
         and common["caller_odd"] == application["signed"]["odd_scale"] == 2025,
         "certificate branch-depth and magnitude bound")
    reported = {}
    for kind, homes in (("peer", 9149), ("candidate", 9151)):
        stats = physical["native"][kind]
        replayed = application["native"][kind]
        work = physical["ordinary"][kind]
        expected = application["ordinary_occurrences"][kind]
        need(all(stats[k] == replayed[k] for k in ("public", "slots", "terms"))
             and stats["path_grid"] == int(replayed["grid"])
             and stats["path_grid_odd"] == replayed["odd"]
             and stats["path_grid_height"] == replayed["dyadic_height"]
             and work["root_negative_q_translations"] == expected["root_head_translations"]
             and work["odd_conversions"] == expected["odd_boundary_conversions"]
             and work["native_numeric_homes"] == stats["numerical_homes"] == homes <= 15290
             and work["raw_numeric_homes"] == 16 * homes
             and work["separate_guarded_streams_per_native"] == 4,
             "complete bank stock, helper conversions and four separately movable streams")
        h = int(calculations[kind]["compiler"]["H"])
        k_star = CARRIER_POWER * AMBIENT_CAP**CARRIER_POWER * (h + 1)**2
        guard = (c * k_star).bit_length()
        need(guard < h, "exact depth guard with this calibrated outer exponent")
        reported[kind] = {"H": h, "c": c, "depth_guard_bits": guard, "ordinary": work,
                          "native_grid": {k: v for k, v in stats.items() if k.startswith("path_grid")}}
    new_maps = (physical["ordinary"]["candidate"]["ordinary_map_slots"]
                - physical["ordinary"]["peer"]["ordinary_map_slots"])
    helper_maps = (application["ordinary_occurrences"]["candidate"]["native_helper_boundary_maps"]
                   - application["ordinary_occurrences"]["peer"]["native_helper_boundary_maps"])
    need(new_maps == helper_maps == 32, "both complete boundary maps of each added stage-tagged owner")
    return {"sha256": sha256(path.read_bytes()).hexdigest(), "paired": reported,
            "inherited_private_home_cap_per_native": 15290, "additional_ordinary_helper_boundary_maps": new_maps,
            "final_substitution": {
                "W": "p+h+2D+3", "Z": "W_p+O", "E_0": "64(Z+N+P+G+1)^3",
                "B_0": "P+E_0", "C_0": "32*N*B_0^2", "N": "2^H",
                "ordinary": "Finite signed root, phase, coefficient, typed selector, copy, overwrite and complete return costs are included in G and full simultaneous owned backing in O."}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--caller-proof", type=Path, required=True)
    parser.add_argument("--physical", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    bit = standing_bit_and_assumptions()
    application = load(args.caller_proof)
    bills = checked_bills(application)
    claim, lo, hi = find_crossing(bills["candidate"][2])
    runs = {"peer": check_numerics(bills["peer"], (PARENT_CLAIM, PARENT_LOWER, PARENT_UPPER), "peer"),
            "candidate": check_numerics(bills["candidate"], (claim, lo, hi), "candidate")}
    from directed_price import moment

    comparator = Fraction(PARENT_UPPER)
    extra_fee = dict(bills["candidate"][2])
    extra_fee[1] -= 1
    fees = moment(extra_fee, comparator, comparator)
    gain = moment({1: 16, 8: 16, 9: -16}, Fraction(claim), Fraction(claim))
    need(fees[1] < 0 and gain[0] > 0, "one additional rank-one charge kills the gain")
    result = {"status": "PASS_CHART595_DIRECTED_PRICE_OUTER" if args.physical else
                        "PASS_CHART595_NUMERICAL_PRICE_OUTER",
              "graphs": application["graphs"], "caller_sha256": CALLER, "parent_head": PARENT_HEAD,
              "caller_proof_sha256": sha256(args.caller_proof.read_bytes()).hexdigest(),
              "candidate_directed_conditional_lower": claim, "candidate_raw_bracket": [lo, hi],
              "published_peer_upper": PARENT_UPPER, "strict_gap": str(Fraction(claim) - comparator),
              "signed_paid_delta": {}, "signed_target_delta": {"1": 16, "8": 16, "9": -16},
              "split_moment_credit_at_claim": list(map(str, gain)),
              "extra_paid_rank_one_at_parent_upper": list(map(str, fees)),
              "numerics": runs, "compiler": runs["candidate"]["compiler"], "selected_BIT": bit,
              "physical_join": check_physical(args.physical, application, runs) if args.physical else None}
    with args.out.open("x") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(result["status"], claim, lo, hi, result["strict_gap"], flush=True)


if __name__ == "__main__":
    main()
