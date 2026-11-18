#!/usr/bin/env python3
"""Audit the published physical, caller and outer joins against the independent replay."""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import CALLER, CHILD, HERE, PARENT, SOURCE, SOURCE_HEAD, blocked, current, directed_result
from check import hash_bytes, invoice_counts, require


def evidence(name):
    raw = (HERE / "evidence" / f"{name}.json").read_bytes()
    return hash_bytes(raw), json.loads(raw)


def counts(physical, caller, graph, invoice, side):
    n = len(graph["initial"])
    k = len(graph["moves"])
    terms = sum(len(row) for _, row in graph["forms"])
    homes = n + k + n + 4 + 1
    stages = sum(event[0] == "J" for event in caller["events"])
    roots = sum(len(spec["ports"]) * len(spec["diagonal"]) for spec in caller["types"].values())
    negative_roots = sum(len(spec["ports"]) * sum(row[0] < 0 for row in spec["diagonal"])
                         for spec in caller["types"].values())
    contacts = 2 * stages * 400
    native = physical["native"][side]
    logical = native["selected_logical_operations"]
    require((n, stages, roots, contacts) == (1501, 16, 3536, 12800)
            and native["slots"] == native["max_outstanding_native_senders"] * k
            and native["numerical_homes"] == homes <= physical["inherited_private_home_cap_per_stage"] == 15290
            and native["immutable_entry_banks"] == native["deferred_terminal_banks"] == n
            and native["immutable_paid_return_banks"] == k
            and native["max_outstanding_native_senders"] == native["separate_guide_tracks"]
            == native["guarded_dummy_slots"] == 1
            and native["additional_independent_guarded_streams"] == native["native_scalar_scratch_homes"] == 4
            and native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"],
            "physical ownership or home count")
    require(logical["write_entrance"] == logical["write_terminal"]
            == logical["read_terminal_for_same_owner_install"] == n
            and logical["read_immutable_donor"] == terms
            and logical["initialize_complete_dirty_home"] == logical["retire_complete_home"] == homes
            and all(logical[key] == k for key in ("initialize_empty_sender_before_departure", "stage_full_sender",
                                                 "read_parked_sender", "write_complete_return",
                                                 "clear_full_sender_after_return")),
            "incomplete physical lifecycle")
    require(all(cells == logical[work] * native["fixture_addressed_cells_per_home"]
                for work, cells in native["fixture_addressed_cells_overwritten"].items()), "complete overwrite fixture")
    conversions = 2 * (roots + stages * n)
    resets = 2 * homes + 8 * terms + 10 * k + 12 * n
    copies = 2 * terms + 8 * k + 6 * n
    selector_span = 14 * homes + 9
    selector_constant = 63 * homes - 7 * homes.bit_count() + 27 * homes.bit_length() + 59
    select = [resets*(selector_span+2) + copies*(selector_span+128),
              resets*(selector_constant+3) + copies*(selector_constant+320)]
    uses = physical["caller_exact"]["uses"]
    paid, targets = map(lambda counts: sum(counts.values()), invoice_counts(invoice))
    maps = (2 * (paid + targets) + contacts + 2 * uses["IDLE_ONE"] + 3 * uses["IDLE_ODD"]
            + 3 * uses["QUERY"] + uses["LAMBDA"] + negative_roots)
    scalar = 32 * (stages * (terms + homes + 6*(k+n)) + sum(uses.values()) + conversions)
    output = {"native_numeric_homes": homes, "raw_numeric_homes": stages * homes,
              "separate_guarded_streams_raw": 4 * stages, "odd_conversions": conversions,
              "reset_services_per_native": resets, "typed_selected_transfers_per_native": copies,
              "selected_total_steps_raw_L_and_constant": [stages * x for x in select],
              "ordinary_map_slots": maps, "ordinary_elementary_record_upper": 4 * 154**2 * maps,
              "scalar_services": scalar, "raw_paid_positions": paid, "raw_productive_targets": targets}
    require(all(physical["ordinary"][side][field] == value for field, value in output.items()), "ordinary charge mismatch")
    return output


def depth_guard(physical, price):
    envelope = physical["caller_hereditary_envelope"]
    native = physical["native"].values()
    a = max(envelope["binary_height_at_all_completed_cuts_and_products"],
            *(envelope["binary_height_at_native_entrances"] + row["path_grid_height"] for row in native))
    before_joint = Q(envelope["scaled_mass_at_native_entrances"])
    mass = max(Q(envelope["scaled_mass_at_all_cuts_and_products"]),
               *(before_joint * row["path_grid_odd"] * Q(row["positive_path_mass_bound_unscaled"]) for row in native))
    b = mass.numerator.bit_length() - mass.denominator.bit_length()
    if mass > 2**b:
        b += 1
    context = physical["common_exact_root"]
    c = 2 * max(a, b)
    h = int(price["compiler"]["H"])
    carrier, ambient = (price["recurrence_anchors"][field] for field in ("carrier_power", "conservative_ambient_cap"))
    bits = (c * carrier * ambient**carrier * (h+1)**2).bit_length()
    guard = physical["bit_guard"]
    require((carrier, ambient) == (1920, 153) and (a, b, c) == (338, 578, 1156)
            and (context["context_binary_bits"], context["context_mass_bits"], context["context_c"]) == (a, b, c)
            and Q(context["context_mass_bound"]) == mass and context["signed_width"] == "W=p+h+2D+3"
            and context["temporary_width"] == "W+26" and context["exact_grid"] == "2^(-p-D)"
            and guard["strict_guard_passed"] and guard["argument_bit_length"] == bits < h
            and guard["compiler_H"] == h, "fresh compiler and context depth guard mismatch")
    return {"H": h, "binary_height": a, "mass_bits": b, "c": c, "guard_bits": bits}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    require(not args.out.exists(), "exclusive review output")
    records = {key: evidence(key) for key in ("INDEPENDENT", "CALLER", "PHYSICAL", "PRICE")}
    audit, caller_receipt, physical, price = (records[key][1] for key in records)
    caller = current(HERE/"data/CALLER.json.gz", CALLER)
    graphs = {"parent": current(HERE/"data/PARENT-GRAPH.json.gz", PARENT),
              "candidate": current(HERE/"data/CANDIDATE-GRAPH.json.gz", CHILD)}
    require((audit["source_head"], audit["source"], audit["parent_graph"], audit["changed_graph"], audit["signed_caller"])
            == (SOURCE_HEAD, SOURCE, PARENT, CHILD, CALLER), "independent evidence belongs to these exact inputs")
    for receipt in (caller_receipt, physical, price):
        require(receipt["graphs"] == {"parent": PARENT, "candidate": CHILD}
                and (receipt["source_head"], receipt["source_word_sha256"], receipt["caller_sha256"])
                == (SOURCE_HEAD, SOURCE, CALLER), "joined source, graph and caller pins")
    require(price["caller_proof_sha256"] == records["CALLER"][0]
            and price["physical_join"]["sha256"] == records["PHYSICAL"][0]
            and price["invoices"] == caller_receipt["invoices"], "exact author evidence bytes joined to price")
    independent = audit["price"]
    for side, pay_key in (("parent", "input_paid_counts"), ("candidate", "output_paid_counts")):
        require(price["invoices"][side]["paid"] == independent[pay_key]
                and price["invoices"][side]["targets"] == independent["whole_targets"], "entire independently grouped bill")
    ordinary = {side: counts(physical, caller, graphs[side], price["invoices"][side], side) for side in graphs}
    compiler = depth_guard(physical, price)
    require(compiler["H"] == price["physical_join"]["compiler_H"]
            and compiler["c"] == price["physical_join"]["c"]
            and compiler["guard_bits"] == price["physical_join"]["depth_guard_bits"]
            and all(price["physical_join"]["paired"][side]["ordinary"] == physical["ordinary"][side]
                    for side in graphs), "outer uses entire replayed ordinary budgets")
    assumption_ids = [a["id"] for a in price["selected_BIT"]["assumptions"]]
    require(assumption_ids == ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"],
            "selected assumptions changed")
    require(price["compiler"]["outer"] == {"BIT_just_below_effective_rejected": True, "functional_count": 4,
                                            "minimum_margin": "1/1000000000000000", "strict_count": 54},
            "selected production outer predicates")
    lower = Q(price["candidate_directed_conditional_lower"])
    tested = Q(price["compiler"]["tested"])
    high_7700 = Q(price["supplied_comparator_7700_raw_bracket"][1])
    high_7697 = Q(price["published_comparator_7697"]["upper"])
    p0, p1 = map(lambda result: Q(result["point"]), independent["checks"]["candidate_crossing"])
    b0, b1 = map(Q, price["candidate_raw_bracket"])
    require((lower, high_7700, high_7697) == (Q(".0037300417"), Q(".00372934317807"), Q(".0037266288770"))
            and lower - high_7700 == Q(price["strict_gap_over_7700_raw_upper"])
            and lower - high_7697 == Q(price["strict_gap_over_7697_upper"])
            and max(high_7697, high_7700) < lower < tested < b0 < p0 < p1 < b1,
            "conditional quote, upper comparators and compatible raw intervals")
    candidate = invoice_counts(price["invoices"]["candidate"])
    own_moment = directed_result(candidate, tested, 1)
    paid, productive = candidate
    paid[1] += 1
    fee_control = directed_result((paid, productive), high_7700, -1)
    wrong_compiler = {**price, "compiler": {**price["compiler"], "H": compiler["H"]+1}}
    wrong_bank = {**physical, "ordinary": {**physical["ordinary"], "candidate": {**physical["ordinary"]["candidate"],
                                                        "typed_selected_transfers_per_native": 0}}}
    controls = [blocked(lambda: depth_guard(physical, wrong_compiler), "fresh compiler and context depth guard mismatch"),
                blocked(lambda: counts(wrong_bank, caller, graphs["candidate"], price["invoices"]["candidate"],
                                       "candidate"), "ordinary charge mismatch")]
    result = {"status": "PASS_INDEPENDENT_ACTUAL_PHYSICAL_CALLER_AND_OUTER_JOIN", "candidate": CHILD,
              "evidence_sha256": {key: value[0] for key, value in records.items()}, "ordinary": ordinary,
              "precision_and_depth": compiler, "assumption_ids": assumption_ids,
              "accepted_conditional_bound": str(lower), "independent_moment_at_outer_probe": own_moment,
              "one_rank_one_fee_at_7700_upper": fee_control, "controls": controls,
              "scope": "Independent finite invoice, stock and receipt join review. Production outer predicates are joined by evidence."}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(result["status"])


if __name__ == "__main__":
    main()
