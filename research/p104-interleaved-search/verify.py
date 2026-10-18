#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the bounded P104 checkpoint; never assert an improved exponent."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    spec = importlib.util.spec_from_file_location("p104_checkpoint_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def construct():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for source in sources["files"]:
        if source["usage"] == "input":
            require(hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"],
                    "source drift: " + source["path"])
    query_sources = load("query_construction").verify()
    actual_queries = load("actual_queries").verify()
    natural_module = load("natural_delivery")
    natural_delivery = natural_module.verify()
    native_witness = natural_module.native_witness()
    native = load("native_checks").verify(native_witness)
    natural_cost = load("natural_budget").price(natural_delivery, assume_seven_free_deliveries=True)
    fanout_module = load("fanout")
    fanout = fanout_module.verify()
    fanout_witness = fanout_module.native_witness()
    fanout_native = load("native_checks").verify(fanout_witness)
    fanout_cost = load("fanout_budget").price(fanout)
    coalesced_module = load("coalesced")
    coalesced = coalesced_module.verify()
    coalesced_witness = coalesced_module.native_witness()
    coalesced_native = load("native_checks").verify(coalesced_witness)
    hosting = load("hosting").verify(fanout)
    coalesced_cost = load("coalesced_budget").price(coalesced, hosted_report=hosting)
    scalar = load("scalar_surgery").verify()
    delivery = load("delivery").verify()
    budget = load("budget").verify(include_copy_table=True)

    require(scalar["removed_selected_positions"] == delivery["removed_selected_positions"],
            "scalar and delivery punctures differ")
    by_pair = {tuple(row["pair_hamming_root_indices"]): row for row in delivery["chains"]}
    require(len(by_pair) == 2, "expected two independently replayed delivery fragments")
    query_scales = dict(zip(map(tuple, scalar["decoder_hamming_root_pairs"]),
                            scalar["query_scale_for_delivery_output_dot_a"]))
    require(set(by_pair) <= set(query_scales), "delivery and scalar decoder orientations differ")
    require(all(Fraction(query_scales[pair]) == Fraction(1, 8) for pair in by_pair),
            "delivery source normalization changed")
    for row in budget["chain_profile_inputs"]:
        actual = by_pair[(row["a_root"], row["b_root"])]
        require(row["injections"] == actual["contact_count"], "budget injection count drift")
        require(row["descent"] == actual["private_descent_profile"], "budget descent profile drift")
        require(row["local_tail_cleanup_delta"] == actual["local_B_tail_endpoint_cleanup_profile_delta"],
                "budget local profile differs from actual delivery replay")
        require(row["residual_width_delta"] == actual["residual_width_profile_delta"],
                "budget residual profile differs from actual delivery replay")
    joint = delivery["combined_two_query_channel"]
    for source_key, joint_key in (
        ("local_tail_cleanup_delta", "local_B_tail_endpoint_cleanup_profile_delta"),
        ("residual_width_delta", "residual_width_profile_delta"),
    ):
        total = Counter()
        for row in budget["chain_profile_inputs"]:
            total.update(row[source_key])
        total = {key: count for key, count in total.items() if count}
        require(total == joint[joint_key], "priced sum differs from joint chronological replay")
    require(joint["query_count"] == joint["peak_simultaneous_private_copies"] == 2,
            "simultaneous private-copy contract changed")
    require(not joint["global_owner_hosting_verified"], "this checkpoint must not assert global hosting")
    centres = budget["selected_private_centre_stock"]["selected_private_centre_families"]
    require(joint["peak_simultaneous_private_copies"] <= centres, "fragment exceeds selected private-centre stock")

    require(query_sources["B_permutation_sha256"] == actual_queries["B_permutation_sha256"],
            "actual query scalar recipe uses a different B schedule")
    require(query_sources["punctured_selected_positions"] == scalar["removed_selected_positions"],
            "actual query sources use a different P104 puncture")
    require([(r["a_root"], r["b_root"]) for r in actual_queries["sources"]] ==
            list(map(tuple, scalar["decoder_hamming_root_pairs"])),
            "actual query recipe uses a different decoder")

    for source in actual_queries["sources"]:
        bank = query_sources["all_sixteen_source_banks"][str(source["b_root"])]
        require(all(source[key] == bank[key] for key in
                    ("register", "raw_query_coefficient", "full_704_column_row_sha256")),
                "actual source scalar recipe differs from the source bank proof")
    qc = load("query_construction")
    word = qc.load_inputs()["word"]
    for i, normal in enumerate(word["ports"]):
        if i in qc.REMOVED:
            continue
        require(qc.span(word["frames"][word["start"][i]]) == frozenset({0, normal}),
                "intrinsic entry adapter does not bind actual source boundary")
        require(qc.span(word["frames"][word["final"][word["v"] + i]]) ==
                frozenset(x for x in range(512) if not (x & normal).bit_count() % 2),
                "intrinsic exit adapter does not bind actual target boundary")
    require(native_witness["ports"] == [q for i, q in enumerate(word["ports"]) if i not in qc.REMOVED],
            "native ports differ from the pinned P104 puncture")
    require(native_witness["public_profile"] == natural_delivery["candidate_public_profile"] and
            native_witness["private_profile"] == natural_delivery["private_COPY_profile"],
            "native occurrence witness differs from the scalar/frame replay")
    total_profile = Counter(native_witness["public_profile"])
    total_profile.update(native_witness["private_profile"])
    require(dict(total_profile) == native["paid_profile"], "native compiler occurrence recount differs")
    require(native_witness["private_transports"] ==
            [e for e in native_witness["transports"] if e["private"]],
            "native private path differs from literal chronology")
    require([e["occurrence"] for e in native_witness["transports"]] ==
            list(range(len(native_witness["transports"]))), "native occurrence index coverage")
    require(not actual_queries["unframed_scalar_scatter"]["native_frame_certificate"] and
            not natural_delivery["complete_eight_term_supplier"], "partial results were promoted to a supplier")
    require(fanout_witness["ports"] == native_witness["ports"], "full fanout native port mismatch")
    require(all(fanout_witness[key] == fanout[key] for key in
                ("scalar_operation_word_sha256", "transport_occurrences_sha256")),
            "full fanout native witness uses a different literal word")
    require(fanout_witness["public_profile"] == fanout["candidate_public_profile"] and
            fanout_witness["private_profile"] == fanout["private_COPY_profile"],
            "full fanout native witness differs from scalar/frame replay")
    fanout_profile = Counter(fanout_witness["public_profile"])
    fanout_profile.update(fanout_witness["private_profile"])
    require(dict(fanout_profile) == fanout_native["paid_profile"], "full native occurrence recount differs")
    require([e for path in fanout_witness["private_paths"] for e in path] ==
            [e for e in fanout_witness["transports"] if e["private"]],
            "eight private paths differ from literal chronology")
    require([e["occurrence"] for e in fanout_witness["transports"]] ==
            list(range(len(fanout_witness["transports"]))), "full fanout occurrence index coverage")
    require(fanout_native["private_paths"] == 8 and fanout_native["private_path_gaussian_columns"] == 4096,
            "incomplete eight-path native check")
    require(fanout["full_735_column_identity_verified"] and
            fanout_cost["actual_public_profile"] == fanout["candidate_public_profile"] and
            fanout_cost["actual_private_COPY_profile"] == fanout["private_COPY_profile"],
            "full cost invoice differs from verified forward identity")
    require(all(row["selected_kappa_excluded"] for row in fanout_cost["scenarios"]),
            "cost rejection changed")
    require(not fanout["global_hosting_verified"] and not fanout["completed_full_multiplication_supplier"],
            "finite forward word was promoted to a global supplier")
    require(coalesced["source_scalar_operations_sha256"] == fanout["scalar_operation_word_sha256"] and
            coalesced["complete_public_widths"] == fanout["complete_public_widths"],
            "recharting changed the scalar word or public boundary widths")
    require(coalesced_witness["ports"] == fanout_witness["ports"], "recharting changed native ports")
    require(all(coalesced_witness[key] == coalesced[key] for key in
                ("scalar_operation_word_sha256", "transport_occurrences_sha256")),
            "coalesced native witness uses a different literal word")
    require(coalesced_witness["public_profile"] == coalesced["candidate_public_profile"] and
            coalesced_witness["private_profile"] == coalesced["private_COPY_profile"],
            "coalesced native witness differs from scalar/frame replay")
    coalesced_profile = Counter(coalesced_witness["public_profile"])
    coalesced_profile.update(coalesced_witness["private_profile"])
    require(dict(coalesced_profile) == coalesced_native["paid_profile"], "coalesced native occurrence recount")
    require([e for path in coalesced_witness["private_paths"] for e in path] ==
            [e for e in coalesced_witness["transports"] if e["private"]], "coalesced private occurrence coverage")
    require([e["occurrence"] for e in coalesced_witness["transports"]] ==
            list(range(len(coalesced_witness["transports"]))), "coalesced occurrence index coverage")
    require(coalesced_native["private_paths"] == 8 and coalesced_native["private_path_gaussian_columns"] == 4096,
            "incomplete coalesced private native replay")
    require(coalesced_cost["actual_public_profile"] == coalesced["candidate_public_profile"] and
            coalesced_cost["actual_private_COPY_profile"] == coalesced["private_COPY_profile"],
            "coalesced cost differs from verified word")
    require(all(row["one_percent_target_excluded"] for row in coalesced_cost["scenarios"]),
            "coalesced one-percent cost rejection changed")
    require(hosting["complete_public_widths_sha256"] == fanout_module.digest(coalesced["complete_public_widths"]),
            "owner packing does not bind the coalesced lifetime widths")
    hosted_cost = coalesced_cost["conditional_selected_window_invoice"]
    require(hosted_cost["assignment_sha256"] == hosting["assignment_sha256"] and
            all(row["selected_kappa_excluded"] for row in hosted_cost["scenarios"]),
            "concrete selected-window invoice is not the checked cost rejection")

    return {
        "schema_version": 3,
        "status": "VERIFIED_FINITE_FORWARD_WORD_COST_REJECTED_NOT_A_SUPPLIER",
        "requested_verified_kappa_gain_achieved": False,
        "base_commit": sources["base_commit"],
        "selected_kappa_unchanged": budget["selected_kappa"],
        "chain_input_sha256": hashlib.sha256((HERE / "CHAINS.json").read_bytes()).hexdigest(),
        "query_construction": query_sources,
        "actual_query_scalar_identity": actual_queries,
        "natural_source_delivery": natural_delivery,
        "natural_delivery_native_lowering": native,
        "natural_delivery_optimistic_cost": natural_cost,
        "complete_fanout_forward_word": fanout,
        "complete_fanout_native_lowering": fanout_native,
        "complete_fanout_cost_rejection": fanout_cost,
        "coalesced_forward_word": coalesced,
        "coalesced_native_lowering": coalesced_native,
        "conditional_owner_window_packing": hosting,
        "coalesced_cost_screen": coalesced_cost,
        "scalar_surgery": scalar,
        "delivery": delivery,
        "budget": budget,
        "cross_checks": {
            "same_exact_104_port_puncture": True,
            "actual_query_sources_and_scalar_recipe_share_B_permutation": True,
            "actual_eight_source_registers_match_decoder": True,
            "actual_query_rows_equal_source_bank_rows": True,
            "native_transport_occurrences_equal_scalar_frame_replay": True,
            "native_ports_equal_pinned_p104_puncture": True,
            "eight_fanout_private_paths_partition_literal_private_occurrences": True,
            "complete_fanout_profile_binds_scalar_native_and_cost_replays": True,
            "full_forward_identity_is_not_global_supplier_admission": True,
            "coalesced_scalar_word_and_boundaries_bind_original_fanout": True,
            "coalesced_native_and_cost_profiles_bind_full_identity": True,
            "delivery_pairs_belong_to_scalar_decoder": True,
            "retained_delivery_sources_need_raw_query_divided_by_eight": True,
            "priced_single_chain_deltas_equal_replayed_deltas": True,
            "priced_sum_equals_joint_chronological_replay": True,
            "private_copy_peak_fits_selected_eight_centre_stock": True,
            "no_oracle_or_optimistic_ceiling_claimed_as_supplier": True,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="explicitly regenerate the checked receipt")
    args = parser.parse_args()
    result = construct()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(path.read_text()), "recorded result differs from exact replay")
    print("PASS_P104_INTERLEAVED_CHECKPOINT: exact 735-column forward word, native operators and cost rejection; no improved kappa")


if __name__ == "__main__":
    main()
