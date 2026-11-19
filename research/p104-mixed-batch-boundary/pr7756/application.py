"""Price the frozen parent, both changes in isolation, and the finite combined caller."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, need, owner_stages, physical, provenance, read, receipt
from native import verify as verify_native
from mixed_application import (check_components, comparison_invoice, ordinary_for_batch,
                               verify_caller)
from caller16 import signed_caller
from interval_gate_signed import gate

sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from compare_recursive_invoices import compare_invoices
from evaluate_recursive_power import evaluate

PREVIOUS_UPPER = "0.00378751509487"
PREVIOUS_GAIN = "0.00002437823416"
BIT = "0.00385248"


def invoice(native, signed, contract):
    def total(local, fixed):
        result = Counter({int(r): n * signed["calls"] for r, n in local.items()})
        result.update({int(r): n for r, n in fixed.items()})
        return {str(r): n for r, n in sorted(result.items())}
    return dict(schema="integer-mult-recursive-invoice/v1", contract=contract,
                paid=total(native["paid_native_ranks"], signed["fixed_caller_paid"]),
                targets=total(native["positive_helper_ranks"], signed["fixed_root_targets"]))


def directed(bill, point, sign):
    zero = dict(bill, paid={}, targets={})
    result = evaluate(zero, bill, 1 - Fraction(point), 256)
    need(result["classification"] == "new_cost_" + sign, "directed price at " + point)
    return dict(kappa=point, paid_minus_productive=result["new_minus_old"])


def price(bill, points, compiler):
    lo, hi = points["bracket"]
    signs = [directed(bill, lo, "lower"), directed(bill, hi, "higher")]
    result = dict(bracket=[lo, hi], signs=signs)
    if compiler:
        claim, probe = points["claim"], points["probe"]
        weights = {side: {int(r): n for r, n in bill[k].items()}
                   for side, k in (("P", "paid"), ("T", "targets"))}
        result.update(claim=claim, probe=probe, compiler=gate(weights, claim, probe, lo, hi, BIT),
                      inner_points=[directed(bill, point, "lower") for point in (claim, probe)])
        need(Fraction(claim) - Fraction(PREVIOUS_UPPER) > Fraction(PREVIOUS_GAIN),
             "larger increment than the preceding proposal")
    return result


def verify():
    source_files = provenance()
    layout, result = verify_native()
    native = result["physical"]["native"]
    caller = read("data/CALLER.json.gz")
    legacy = signed_caller(caller, layout, 2025, 9)
    hosted = layout["hosted"]
    mains = (set(layout["live"]) | {x+112 for x in layout["live"]} |
             set(hosted["X2"]) | set(hosted["Y2"]))
    legacy_stages = owner_stages(layout, mains, caller)
    points = read("PRICE.json")
    calls = points["calls"]
    signed, envelope, word_proof = verify_caller(caller, layout, calls, legacy,
                                                  read("data/CALLER-PHASE-BASES.json"))
    parent = read("data/COMPARATOR-APPLICATION.json")
    need(parent["bracket"][1] == PREVIOUS_UPPER and parent["physical"]["native"]["public"] == 1260,
         "pinned complete PR 7726 invoice")
    old_bill = parent["invoice"]
    comparison = comparison_invoice(old_bill, calls)
    bill = invoice(native, signed, comparison["contract"])
    old_native = parent["physical"]["native"]
    need(invoice(old_native, legacy, old_bill["contract"]) == old_bill, "rebuild parent invoice")
    old_caller = invoice(native, legacy, old_bill["contract"])
    old_circuit = invoice(old_native, signed, comparison["contract"])
    full = price(bill, points["combined"], True)
    native_only = price(old_caller, points["native_only"], True)
    caller_only = price(old_circuit, points["caller_only"], False)

    components = check_components(caller, physical, result["physical"]["scalars"]["coefficient_bits"])
    ordinary = ordinary_for_batch(native, signed, components["coefficient_bits"])
    paid, productive = sum(bill["paid"].values()), sum(bill["targets"].values())
    need((paid, productive) == (ordinary["raw_paid_positions"], ordinary["raw_productive_targets"]),
         "full physical and recursive denominators")
    need(productive == signed["root_owners"] + calls * (layout["public"] - 400), "independent owners")
    root = physical.root_envelope({"candidate": native}, envelope)
    depth = physical.check_depth_guard(root, int(full["compiler"]["H"]))

    old_shifts = sum(len(t["ports"]) * sum(row[0] < 0 for row in t["diagonal"])
                     for t in caller["types"].values())
    legacy_ordinary = physical.ordinary_budget(native, legacy, old_shifts,
                                                result["physical"]["scalars"]["coefficient_bits"])
    need((sum(old_caller["paid"].values()), sum(old_caller["targets"].values())) ==
         (legacy_ordinary["raw_paid_positions"], legacy_ordinary["raw_productive_targets"]),
         "original caller complete charge")
    old_envelope = physical.caller_envelope(caller)
    need(old_envelope["uses"] == legacy["uses"], "original caller count")
    old_root = physical.root_envelope({"candidate": native}, old_envelope)
    old_depth = physical.check_depth_guard(old_root, int(native_only["compiler"]["H"]))

    result.update(calls=calls, paid=paid, productive=productive, invoice=bill, **full,
                  previous_upper=PREVIOUS_UPPER, previous_increment=PREVIOUS_GAIN,
                  parent_upper_check=directed(old_bill, PREVIOUS_UPPER, "higher"),
                  gain_over_previous_upper=str(Fraction(full["claim"]) - Fraction(PREVIOUS_UPPER)),
                  comparison=compare_invoices(comparison, bill), source_files=source_files,
                  isolated_native=dict(invoice=old_caller, stages=legacy_stages, **native_only,
                                       guard=old_depth, ordinary=legacy_ordinary),
                  isolated_caller=dict(invoice=old_circuit, **caller_only), caller=signed)
    result["physical"].update(caller_envelope=envelope, caller_word=word_proof, components=components,
                              common_root=root, depth_guard=depth, ordinary=ordinary)
    return result


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "retained compiler assertions enabled")
    output = verify()
    receipt("application", output)
    print("PASS_PARALLEL_BANK_APPLICATION", output["claim"], output["paid"], output["productive"])
