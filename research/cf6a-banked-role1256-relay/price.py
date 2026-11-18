#!/usr/bin/env python3
"""Join the exact supplied-word relay, physical costs and directed outer bound."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

if not __debug__:
    raise RuntimeError("Directed compiler checks require Python assertions")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from caller import (
    CALLER, CANDIDATE, DATA, ENGINE, INVOICE, PARENT, PAID_DELTA, PHASE_DIGEST, PUBLIC,
    SOURCE_HEAD, SOURCE_WORD, STATUS as CALLER_STATUS, check_sources, digest, load, need,
    signed_delta, write,
)


CLAIM = "0.0037300417"
TARGET = "0.00372935"
BIT_FLOOR = "0.00376669"
GAP = Fraction(1, 10**14)
CARRIER_POWER = 1920
AMBIENT_CAP = 153
PHYSICAL_STATUS = "PASS_CF6A_RELAY_BANK_PHYSICAL"
STATUS = "PASS_CF6A_RELAY_DIRECTED_PRICE_OUTER"
COMPARATOR_7697 = {
    "head": "f55fc1434436ffa1c6d064a29fc56812044b3157",
    "graph": "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b",
    "caller_receipt": "cbef124e8b495b4bec9a1343500766af33b245121a486fff4a619c8eb284f2ad",
    "signed_invoice_sha256": "6e8229022ef7c9a13a33a8df5e591114eb9de49bb5b7b20628bbe56c3fa2c3a7",
    "lower": "0.0037266288769", "upper": "0.0037266288770",
}
PARENT_LOWER, PARENT_UPPER = "0.00372934317806", "0.00372934317807"
ASSUMPTIONS = ("native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery")
PINS = {
    "directed_price.py": "446c8ebddf5b1e56d43b8d7f2ad3c1c9ba018a18105b207a0ac9e30386878a10",
    "interval_gate.py": "60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5",
    "selected-claim.json": "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2",
    "selected-bit-ambient.json": "437ad2f9e7956e7f2b477b546f53a6c8cfa0567e207024300e9a7e58d3c0202c",
    "selected-validation.json": "e1374a98b240d7f9f2cca2a1e74b93f240b1bfc94b8cc4b94a385a50281d494e",
}


def selected_bit():
    check_sources()
    for name, pin in PINS.items():
        need(digest((ENGINE / name).read_bytes()) == pin, f"fixed directed price or selected input {name}")
    claim = load(ENGINE / "selected-claim.json", PINS["selected-claim.json"])
    repair = load(ENGINE / "selected-bit-ambient.json", PINS["selected-bit-ambient.json"])
    validation = load(ENGINE / "selected-validation.json", PINS["selected-validation.json"])
    bit = next(row for row in claim["uniform_templates"] if row["family"] == "BIT before cover")
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
         and repair["exit_code"] == 0 and repair["source_unchanged"]
         and validation["status"] == "admitted_conditional" and validation["registered_replays_complete"],
         "selected ambient-corrected BIT anchor")
    need(tuple(row["id"] for row in claim["assumptions"]) == ASSUMPTIONS
         and Fraction(bit["saving"]) > Fraction("0.00385248") > Fraction(BIT_FLOOR),
         "retained five named assumptions and conservative independently justified BIT saving")
    return {"ambient": bit["ambient"], "rank_encoding": bit["rank_encoding"],
            "source_template_saving": bit["saving"], "retained_completed_saving": "0.00385248",
            "outer_floor": BIT_FLOOR, "assumptions": claim["assumptions"],
            "selected_source_pins": {k: v for k, v in PINS.items() if k.startswith("selected-")}}


def checked_histograms(invoice, totals):
    p = Counter({int(k): n for k, n in invoice["paid"].items()})
    t = Counter({int(k): n for k, n in invoice["targets"].items()})
    need(invoice["schema"] == "integer-mult-recursive-invoice/v1"
         and invoice["contract"]["ambient_rank"] == 137
         and all(1 <= rank <= 137 and type(n) is int and n > 0 for h in (p, t) for rank, n in h.items())
         and (sum(p.values()), sum(t.values())) == totals,
         "each positive paid placement and productive target in the fixed complete invoice")
    coeff = {r: t[r] - p[r] for r in t.keys() | p.keys()}
    need(sum(r * n for r, n in coeff.items()) == 1328, "complete conserved signed rank mass")
    return p, t, coeff


def checked_bills(application):
    need(application["status"] == CALLER_STATUS and application["source_head"] == SOURCE_HEAD
         and application["source_word_sha256"] == SOURCE_WORD
         and application["graphs"] == {"parent": PARENT, "candidate": CANDIDATE}
         and application["caller_sha256"] == CALLER
         and application["published_parent_invoice_sha256"] == INVOICE
         and application["source_phase"]["phase_digest"] == PHASE_DIGEST
         and application["source_phase"]["contacts"] == 12800
         and application["signed"]["calls"] == 16 and application["signed"]["root_owners"] == 3536
         and application["owners"]["fresh_helpers"] == 17616, "actual supplied 16-call receipt and frozen fingerprints")
    invoices = application["invoices"]
    old = load(DATA / "PR7697-INVOICE.json", COMPARATOR_7697["signed_invoice_sha256"])
    source = load(DATA / "SOURCE-INVOICE.json", INVOICE)
    need(invoices["parent"] == source
         and all(invoice["contract"] == source["contract"] for invoice in (invoices["candidate"], old)),
         "supplied original and prior banked comparator use the same signed invoice model")
    base = checked_histograms(source, (101856, 21152))
    alternate = checked_histograms(old, (101824, 21168))
    child = checked_histograms(invoices["candidate"], (101840, 21152))
    need(signed_delta(base[0], child[0]) == PAID_DELTA and base[1] == child[1]
         and {int(k): n for k, n in application["signed_paid_delta"].items()} == PAID_DELTA
         and application["signed_target_delta"] == {}, "only −32 rank-three and +16 rank-six whole-caller charges")
    return {"pr7697": alternate, "parent": base, "candidate": child}


def directed_sign(coeff, point, sign):
    from directed_price import moment
    from interval_gate import B, moment as fixed_moment

    point = Fraction(point)
    first = moment(coeff, point, point)
    second = tuple(Fraction(bound, B) for bound in fixed_moment(coeff, point))
    for bounds in (first, second):
        need(bounds[0] > 0 if sign > 0 else bounds[1] < 0, f"two strict directed prices at {point}")
    common = (max(first[0], second[0]), min(first[1], second[1]))
    need(common[0] <= common[1], "the independent directed intervals intersect")
    return {"sign": sign, "binary_rational_log_exp": list(map(str, first)),
            "decimal_fixed_grid": list(map(str, second)), "intersection": list(map(str, common)),
            "display": list(map(float, common))}


def decimal_tick(tick, digits):
    integral, fractional = divmod(tick, 10**digits)
    return f"{integral}.{fractional:0{digits}d}"


def bisect_crossing(coeff):
    from directed_price import moment

    steps = 10**13
    lo, hi = int(Fraction(TARGET) * steps), int(Fraction(BIT_FLOOR) * steps)
    directed_sign(coeff, Fraction(lo, steps), 1)
    directed_sign(coeff, Fraction(hi, steps), -1)
    while hi - lo > 1:
        tick = (lo + hi) // 2
        point = Fraction(tick, steps)
        L, U = moment(coeff, point, point)
        if L > 0:
            lo = tick
        elif U < 0:
            hi = tick
        else:
            raise ValueError("directed root bracket cannot resolve a tick")
    return decimal_tick(lo, 13), decimal_tick(hi, 13)


def price_calculations(bills):
    from directed_price import moment
    from interval_gate import gate

    old, parent, candidate = (bills[kind][2] for kind in ("pr7697", "parent", "candidate"))
    high_old, low_old = COMPARATOR_7697["upper"], COMPARATOR_7697["lower"]
    lo, hi = bisect_crossing(candidate)
    probe = Fraction(CLAIM) + 7 * GAP
    need(Fraction(low_old) < Fraction(high_old) < Fraction(PARENT_LOWER) < Fraction(PARENT_UPPER)
         < Fraction(TARGET) < Fraction(CLAIM) < probe < Fraction(lo) < Fraction(hi) < Fraction(BIT_FLOOR),
         "strict chain from the two comparator upper bounds to the new reporting and BIT points")
    checks = {
        "pr7697": {p: directed_sign(old, p, sign) for p, sign in
                   ((low_old, 1), (high_old, -1), (PARENT_UPPER, -1), (CLAIM, -1), (BIT_FLOOR, -1))},
        "parent": {p: directed_sign(parent, p, sign) for p, sign in
                    ((high_old, 1), (PARENT_LOWER, 1), (PARENT_UPPER, -1), (TARGET, -1),
                     (CLAIM, -1), (BIT_FLOOR, -1))},
        "candidate": {},
    }
    for point, sign in ((high_old, 1), (PARENT_UPPER, 1), (TARGET, 1), (CLAIM, 1),
                        ("0.00373004170007", 1), (lo, 1), (hi, -1), (BIT_FLOOR, -1)):
        checks["candidate"][point] = directed_sign(candidate, point, sign)
    derivatives = {}
    for kind, (p, t, coeff) in bills.items():
        result = moment(coeff, Fraction(), Fraction(BIT_FLOOR), derivative=True)
        need(result[1] < 0, f"strictly decreasing {kind} moment on the whole admitted bracket")
        derivatives[kind] = list(map(str, result))
    p, t, _ = bills["candidate"]
    compiler = gate({"P": p, "T": t}, CLAIM, probe, lo, hi, BIT_FLOOR)
    outer = compiler["outer"]
    need(outer["strict_count"] == 54 and outer["functional_count"] == 4
         and Fraction(outer["minimum_margin"]) > 0 and outer["BIT_just_below_effective_rejected"],
         "54 strict and four functional selected outer predicates")
    root_fee_mutant = dict(candidate)
    root_fee_mutant[1] -= 1
    extra_fee = directed_sign(root_fee_mutant, PARENT_UPPER, -1)
    credit = directed_sign({r: -n for r, n in PAID_DELTA.items()}, CLAIM, 1)
    k = Fraction(CLAIM)
    need(probe == Fraction("0.00373004170007"), "literal compiled right-probe position")
    return {"candidate_directed_conditional_lower": CLAIM, "candidate_raw_bracket": [lo, hi],
            "signed_paid_delta": PAID_DELTA, "signed_target_delta": {},
            "published_comparator_7697": COMPARATOR_7697,
            "supplied_comparator_7700_raw_bracket": [PARENT_LOWER, PARENT_UPPER],
            "strict_gap_over_7697_upper": str(k - Fraction(high_old)),
            "strict_gap_over_7700_raw_upper": str(k - Fraction(PARENT_UPPER)),
            "directed_checks": checks, "directed_derivatives": derivatives,
            "additional_raw_rank_one_rejected_at_7700_upper": extra_fee, "relay_credit_at_claim": credit,
            "compiler": compiler, "recurrence_anchors": {
                "carrier_power": CARRIER_POWER, "conservative_ambient_cap": AMBIENT_CAP,
                "paid_cutoff": 11, "target_floor": 12, "tail_power_offset": "1/7",
                "tail_ratio_upper": "31/32", "alpha_reserve": str(Fraction(1, 10**27)),
                "claim_and_probe_increment": str(GAP), "test_increment_count": 7,
                "b": str(k + 5*GAP), "a": str(k + 4*GAP), "q": str(k + 3*GAP),
                "epsilon": str(1 - GAP), "beta": str(1 - 3*GAP)}}


def verify_ordinary(kind, physical, application, bills):
    stats = physical["native"][kind]
    replay = application["native"][kind]
    work = physical["ordinary"][kind]
    actual = application["ordinary_occurrences"][kind]
    n, k, terms, homes = (stats[field] for field in ("public", "slots", "terms", "numerical_homes"))
    paid, target = (sum(hist.values()) for hist in bills[kind][:2])
    need(all(stats[field] == replay[field] for field in ("public", "slots", "terms"))
         and n == PUBLIC and k == (6144 if kind == "parent" else 6143)
         and stats["coefficient_products"] == replay["checked_products"]
         and stats["path_grid"] == int(replay["grid"])
         and stats["path_grid_odd"] == replay["odd"] and stats["path_grid_height"] == replay["dyadic_height"]
         and stats["exact_all_public_rows"] == stats["same_owner_complete_fixture_outputs"]
         == stats["exact_odd_unscale_outputs"] == n,
         "all normalized endpoint rows, exact products, and complete same-owner physical installs")
    need(homes == 2*n+k+5 <= 15290 and work["native_numeric_homes"] == homes
         and work["raw_numeric_homes"] == 16*homes and work["raw_numeric_homes_plus_dummy"] == 16*(homes+1)
         and stats["max_outstanding_native_senders"] == stats["guarded_dummy_slots"] == stats["separate_guide_tracks"] == 1
         and stats["additional_independent_guarded_streams"] == work["separate_guarded_streams_per_native"] == 4
         and work["separate_guarded_streams_raw"] == 64 and work["separate_guarded_guide_tracks_raw"] == 16
         and stats["retired_and_guards_restored"] and stats["all_public_inputs_preserved_until_final_installs"],
         "complete owned bank, serialized sender, full CLEAR, dummy, guides and separately charged streams")
    resets = 2*homes + 8*(terms+k+n) + 4*n + 2*k
    transfers = 2*terms + 2*(k+n) + 6*k + 4*n
    selector_l = 14*homes + 9
    selector_const = 63*homes - 7*homes.bit_count() + 27*homes.bit_length() + 59
    selected = [resets*(selector_l+2) + transfers*(selector_l+128),
                resets*(selector_const+3) + transfers*(selector_const+320)]
    need(work["reset_services_per_native"] == resets and work["typed_selected_transfers_per_native"] == transfers
         and sum(work["reset_services_by_kind_per_native"].values()) == resets
         and sum(work["typed_transfer_legs_by_kind_per_native"].values()) == transfers
         and work["selected_total_steps_per_native_L_and_constant"] == selected
         and work["selected_total_steps_raw_L_and_constant"] == [16*n for n in selected]
         and all(work["layout"][field] for field in ("aggregate_owned_tuple_M", "guide_setup_and_retirement",
                                                      "complete_view_step_bound", "shadow_cells_upper")),
         "actual full-width reset, overwrite, selected copy, guide and return formulas")
    uses = application["signed"]["uses"]
    conversions = 2*(3536 + 16*n)
    scalar = 32*(16*(terms + 4*(k+n) + 2*n + homes + 2*k) + sum(uses.values()) + conversions)
    maps = (2*(paid + target + 16*400) + 2*(uses["IDLE_ONE"] + uses["IDLE_ODD"])
            + 3*uses["QUERY"] + uses["LAMBDA"] + uses["IDLE_ODD"] + actual["root_head_translations"])
    scalar_bits = physical["scalar_services"]["coefficient_bits"]
    need(work["raw_paid_positions"] == paid and work["raw_productive_targets"] == target
         and work["native_paid_wrappers"] == 16*k and work["native_productive_wrappers"] == actual["fresh_helper_owners"]
         and work["ordinary_main_pair_slots"]*2 == actual["main_phase_contacts"]
         and work["root_negative_q_translations"] == actual["root_head_translations"] == 3536
         and work["odd_conversions"] == actual["odd_boundary_conversions"] == conversions
         and work["ordinary_map_slots"] == maps and work["ordinary_elementary_record_upper"] == maps*4*(AMBIENT_CAP+1)**2
         and work["scalar_services"] == scalar and 0 < scalar_bits <= 24
         and work["scalar_step_rate"] == 2**max(20, scalar_bits+8),
         "all physical scalar, conversion, chart-contact, wrapper and charged ordinary occurrences")
    return {"native": {"public": n, "slots": k, "terms": terms, "grid": stats["path_grid"],
                       "checked_basis_products": stats["coefficient_products"], "stock_trace": stats["trace_sha256"]},
            "ordinary": work}


def physical_join(path, application, bills, compiler):
    physical = load(path)
    need(physical["status"] == PHYSICAL_STATUS and physical["graphs"] == application["graphs"]
         and physical["caller_sha256"] == CALLER and physical["source_word_sha256"] == SOURCE_WORD
         and physical["source_head"] == SOURCE_HEAD and physical["inherited_private_home_cap_per_stage"] == 15290
         and physical["raw_stage_count"] == 16 and physical["both_graphs_respect_historical_numeric_homes_and_streams"]
         and physical["relay"]["new_recursive_charges_outside_replacement"] == 0,
         "physical qualification of the exact graphs, source and actual 16 signed occurrences")
    common = physical["common_exact_root"]
    c = common["context_c"]
    h = int(compiler["H"])
    depth_bits = (c*CARRIER_POWER * AMBIENT_CAP**CARRIER_POWER * (h+1)**2).bit_length()
    guard = physical["bit_guard"]
    need(c == 2*max(common["context_mass_bits"], common["context_binary_bits"])
         and common["caller_odd"] == application["signed"]["odd_scale"] == 2025
         and Fraction(common["context_mass_bound"]) > 0 and common["signed_width"] == "W=p+h+2D+3"
         and guard["compiler_H"] == h and guard["argument_bit_length"] == depth_bits < h
         and guard["strict_guard_passed"],
         "common exact rooted precision and depth bound use the freshly computed actual H")
    pair = {kind: verify_ordinary(kind, physical, application, bills) for kind in ("parent", "candidate")}
    delta = {key: pair["candidate"]["ordinary"][key] - pair["parent"]["ordinary"][key]
             for key in ("native_numeric_homes", "odd_conversions", "ordinary_map_slots", "scalar_services",
                         "reset_services_per_native", "typed_selected_transfers_per_native")}
    need(delta["native_numeric_homes"] == -1 and delta["odd_conversions"] == 0
         and delta["ordinary_map_slots"] == -32, "the two wrapper maps on the removed call disappear at each stage")
    return {"sha256": digest(path.read_bytes()), "compiler_H": h, "c": c, "depth_guard_bits": depth_bits,
            "paired": pair, "candidate_minus_parent_ordinary": delta,
            "inherited_private_home_cap_per_native": 15290,
            "ordinary_substitution": {
                "W": "p+h+2D+3", "Z": "W_p+O", "E_0": "64(Z+N+P+G+1)^3",
                "B_0": "P+E_0", "C_0": "32*N*B_0^2", "N": "2^H",
                "G": "Complete addressed selector, reset, copy, overwrite, exact scalar, phase, guide, view and return work with stored signed budgets.",
                "O": "Complete simultaneous typed payload, guide, selector, independent stream, child, compiler and BIT spaces and all parked parent contexts."}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--caller-proof", "--caller", type=Path, required=True)
    parser.add_argument("--physical", type=Path, required=True)
    parser.add_argument("--out", "--output", type=Path, required=True)
    args = parser.parse_args()
    bit = selected_bit()
    application = load(args.caller_proof)
    bills = checked_bills(application)
    numerics = price_calculations(bills)
    joined = physical_join(args.physical, application, bills, numerics["compiler"])
    result = {"status": STATUS, "graphs": application["graphs"], "caller_sha256": CALLER,
              "source_head": SOURCE_HEAD, "source_word_sha256": SOURCE_WORD,
              "caller_proof_sha256": digest(args.caller_proof.read_bytes()),
              "invoices": application["invoices"], "selected_BIT": bit, "physical_join": joined, **numerics}
    write(args.out, result)
    print(STATUS, CLAIM, *numerics["candidate_raw_bracket"], numerics["strict_gap_over_7700_raw_upper"], flush=True)


if __name__ == "__main__":
    main()
