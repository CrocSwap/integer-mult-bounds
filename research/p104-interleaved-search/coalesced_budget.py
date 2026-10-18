#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact necessary cost screens for the coalesced finite P104 word.

The actual profile comes from coalesced.verify(). Fractional rank-51 idle
packing and the optional old-gather credit are favorable relaxations, not an
owner construction. Both fixed profiles exclude the requested one-percent
kappa gain. A positive ceiling below that target is not an achieved gain.

Run from any directory, standard library only:
  python3 -I -B research/p104-interleaved-search/coalesced_budget.py
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location("p104_coalesced_budget_" + name,
                                                 HERE / (name + ".py"))
    if spec is None or spec.loader is None:
        raise ValueError("cannot load " + name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


B = module("budget")
NB = module("natural_budget")
require = B.require


def price(report, hosted_report=None):
    engine, word, _, _ = B.load_inputs()
    require(report["full_735_column_identity_verified"], "missing complete finite scalar identity")
    require(report["ordinary_fanout_helpers"] == 31, "reassess changed helper inventory")
    require(report["public_registers"] == 2 * word["v"] + word["R"] + 31 == 735,
            "public register inventory differs")
    binding_keys = ("source_scalar_operations_sha256", "frame_changes_sha256",
                    "scalar_operation_word_sha256", "transport_occurrences_sha256")
    bindings = {key: report[key] for key in binding_keys}
    require(all(isinstance(value, str) and len(value) == 64 and
                all(character in "0123456789abcdef" for character in value)
                for value in bindings.values()), "missing exact scalar/frame source binding")
    require(bindings["frame_changes_sha256"] == hashlib.sha256(
        (HERE / "COALESCED-FRAMES.json").read_bytes()).hexdigest(),
        "priced report uses a different coalesced frame certificate")
    frame_input = json.loads((HERE / "COALESCED-FRAMES.json").read_text())
    require(bindings["source_scalar_operations_sha256"] == frame_input["source_scalar_operations_sha256"],
            "priced report uses a different original scalar word")
    public = NB.integers(report["candidate_public_profile"])
    private = NB.integers(report["private_COPY_profile"])
    require(private == {7: 8} and B.mass(private) == B.CENTRE == 56,
            "actual eight rank-seven private seed invoice")
    require(B.profile_json(public) == frame_input["expected_public_profile"],
            "priced public invoice differs from the checked frame certificate")
    local = B.changed(public, private)
    retained = B.retained_profile()
    old_width_increase = B.mass(local) - B.mass(retained) - 31 * 9
    require(old_width_increase >= 0, "unexpected existing-public width reduction")
    credit, omissions = NB.gather_credit(word)
    width = Q(B.FAMILIES, B.STAGES)
    total = (B.M - 1) * width + B.CENTRE
    selected_a = B.SELECTED_KAPPA / (1 - B.SELECTED_KAPPA)
    target_kappa = B.SELECTED_KAPPA * Q(101, 100)
    target_a = target_kappa / (1 - target_kappa)
    bit_cap = B.BIT_LOWER / (1 + B.BIT_LOWER)
    require(engine.max_idle_rank(B.M) == 51, "idle-rank cap changed")

    def describe(name, profile, optional_credit, actual_idle=None):
        effective = Counter(profile)
        if actual_idle is not None:
            effective.update(actual_idle)
            require(B.mass(effective) == total, "actual selected-window mass does not cover the complete call")
        model = engine.model(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(model["local_mass"] + model["idle_mass"] == total, "complete paid mass identity")
        if actual_idle is not None:
            require(model["idle_mass"] == 0, "unpriced idle mass after explicit owner invoice")
        zero = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, Q(0))
        require(zero[0] <= total / (B.M * width) <= zero[1], "zero-saving coverage moment")
        root = engine.ceiling(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[0])[1] < 1,
                "uncertified lower saving bracket")
        require(engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[1])[0] > 1,
                "uncertified upper saving bracket")
        selected_moment = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, selected_a)
        target_moment = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, target_a)
        require(target_moment[0] > 1, "one-percent target is no longer excluded")
        require(target_moment[0] > selected_moment[1], "target moments are not separated and increasing")
        complex_cap = root[1] / (1 + root[1])
        cap = min(complex_cap, bit_cap)
        require(cap < target_kappa, "one-percent kappa cap is not excluded")
        margin = ((1 - target_moment[1]) * width, (1 - target_moment[0]) * width)
        return {
            "name": name, "status": "SCOPED_ONE_PERCENT_COST_REJECTION",
            "optional_gather_credit_assumed": optional_credit,
            "idle_invoice": "conditional_selected_window_packing" if actual_idle is not None else "fractional_rank51_relaxation",
            "local_profile": B.profile_json(profile),
            "finite_word_local_rank_mass": str(B.mass(profile)),
            "explicit_per_call_idle_rank_mass": str(B.mass(actual_idle)) if actual_idle is not None else None,
            "model": {key: str(value) for key, value in model.items()},
            "complex_saving_root_interval": B.interval(root),
            "complex_kappa_upper_bound": str(complex_cap),
            "fixed_bit_capped_kappa_upper_bound": str(cap),
            "kappa_upper_bound_decimal": B.decimal(cap),
            "relative_gain_upper_percent_decimal": B.decimal(100 * (cap / B.SELECTED_KAPPA - 1)),
            "moment_at_selected_kappa": B.interval(selected_moment),
            "selected_kappa_excluded": selected_moment[0] > 1,
            "moment_at_one_percent_target": B.interval(target_moment),
            "per_call_margin_at_one_percent_target": B.interval(margin),
            "one_percent_target_excluded": True,
            "positive_upper_bound_is_not_an_achieved_gain": True,
        }

    scenarios = [describe("actual_coalesced_fanout", local, False),
                 describe("same_with_optional_old_four_gather_credit",
                          B.changed(local, credit), True)]
    require(scenarios[0]["model"]["local_mass"] == scenarios[1]["model"]["local_mass"],
            "optional credit changes paid rank mass")
    hosted = None
    if hosted_report is not None:
        require(hosted_report["total_calls"] == 144, "selected T16 call count changed")
        require(hosted_report["ordinary_helpers"] == 527 and
                hosted_report["assigned_roles"] == 144 * 527, "complete ordinary owner inventory")
        require(not hosted_report["global_emitter_admitted"], "conditional packing promoted to global admission")
        removed = sorted(module("query_construction").REMOVED)
        ordinary_registers = (list(range(224, 704)) + removed +
                              [112 + r for r in removed] + list(range(704, 735)))
        require(hosted_report["actual_ordinary_registers"] == ordinary_registers,
                "selected-window invoice uses different ordinary roles")
        widths = [report["complete_public_widths"][r] for r in ordinary_registers]
        widths_digest = hashlib.sha256(json.dumps(widths, sort_keys=True,
                                                  separators=(",", ":")).encode()).hexdigest()
        require(widths_digest == hosted_report["actual_ordinary_widths_sha256"],
                "selected-window invoice uses different coalesced boundary widths")
        idle_global = NB.integers(hosted_report["remaining_idle_profile"])
        require(all(0 < rank <= 51 and count > 0 for rank, count in idle_global.items()),
                "invalid explicit idle-child profile")
        require(B.mass(idle_global) == hosted_report["idle_rank_mass"], "global idle rank mass differs")
        idle = {rank: Q(count, 144) for rank, count in idle_global.items()}
        require(B.mass(idle) == Q(hosted_report["per_call_idle_rank_mass"]), "per-call idle mass differs")
        require(B.mass(local) + B.mass(idle) == total, "actual local plus idle coverage mismatch")
        hosted_scenarios = [describe("coalesced_word_with_selected_window_invoice", local, False, idle),
                            describe("same_with_conditional_old_four_gather_credit",
                                     B.changed(local, credit), True, idle)]
        require(all(item["selected_kappa_excluded"] for item in hosted_scenarios),
                "actual selected-window invoice is no longer a selected-kappa rejection")
        hosted = {
            "scope": "Conditional complete-window owner invoice; no global emitter, backward supplier, or recursive admission is asserted.",
            "total_calls": 144, "ordinary_helpers": 527, "assigned_roles": 144 * 527,
            "sources": hosted_report["sources"],
            "actual_ordinary_widths_sha256": widths_digest,
            "assignment_sha256": hosted_report["assignment_sha256"],
            "global_remaining_idle_profile": B.profile_json(idle_global),
            "global_idle_rank_mass": B.mass(idle_global),
            "per_call_idle_rank_mass": str(B.mass(idle)),
            "exact_actual_local_plus_idle_mass_binding": True,
            "both_selected_threshold_moments_strictly_above_one": True,
            "scenarios": hosted_scenarios,
            "global_emitter_admitted": False,
        }
    return {
        "status": "SCOPED_ONE_PERCENT_COST_REJECTION",
        "scope": "The two stated fixed-profile relaxations exclude a one-percent kappa gain under the retained m73/P104/COPY56 model. They do not establish a positive gain or exclude other words, profile changes, coverage laws, or outer recipes.",
        "sources": [{"path": path, "sha256": digest} for path, digest in B.INPUTS.values()],
        "actual_profile_source": "coalesced.verify()",
        "actual_scalar_and_native_frame_binding": bindings,
        "selected_kappa": str(B.SELECTED_KAPPA),
        "one_percent_target_kappa": str(target_kappa),
        "necessary_complex_saving_for_target": str(target_a),
        "actual_public_profile": B.profile_json(public),
        "actual_private_COPY_profile": B.profile_json(private),
        "ordinary_fanout_helpers": 31,
        "new_helper_rank_mass": 31 * 9,
        "existing_public_lifetime_width_increase": old_width_increase,
        "hypotheses": [
            "Keep m73, nine stages, four pairs, 104 live ports, and COPY rank56.",
            "Use the actual complete public transport profile and all eight private rank-seven seeds.",
            "Allow every remaining unit of paid mass to be a fractional rank51 idle child, without constructing such owners.",
            "For the second scenario only, grant the old four-unused-gather profile credit without assembling it with the changed charts and cleanup.",
            "Use the retained necessary complex and fixed-bit balanced-transfer inequalities.",
        ],
        "optional_old_gather_credit": {"profile_delta": B.profile_json(credit),
                                       "A_event_indices": omissions,
                                       "joint_coalesced_word_verified": False},
        "scenarios": scenarios,
        "conditional_selected_window_invoice": hosted,
        "controls": {"actual_full_735_column_receipt_required": True,
                     "eight_private_rank7_children_charged": True,
                     "complete_mass_and_zero_moment_identities": True,
                     "both_exact_root_brackets_certified": True,
                     "both_one_percent_threshold_moments_strictly_above_one": True},
        "global_owner_packing_constructed": False,
        "new_kappa_gain_certified": False,
    }


def verify(coalesced_report=None, hosted_report=None):
    if coalesced_report is None:
        coalesced_report = module("coalesced").verify()
    if hosted_report is None:
        hosted_report = module("hosting").verify(coalesced_report)
    return price(coalesced_report, hosted_report)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
