#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact cost rejection of the complete finite P104 fanout profile.

Uses the actual public and private invoices returned by fanout.verify(), the
pinned selected result, and the attributed exact interval engine in budget.py.
Even fractional rank-51 residual packing fails to improve the selected kappa.
The optional old-gather credit is a further favorable, unassembled relaxation.
No global owner construction is needed for this model-specific cost rejection.

Run from any directory, standard library only:
  python3 -I -B research/p104-interleaved-search/fanout_budget.py
"""

from __future__ import annotations

from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location("p104_fanout_budget_" + name,
                                                 HERE / (name + ".py"))
    if spec is None or spec.loader is None:
        raise ValueError("cannot load " + name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


B = module("budget")
NB = module("natural_budget")
require = B.require


def price(fanout_report):
    """Price a verified finite-word receipt, without promoting it to a supplier."""
    engine, word, _, stock = B.load_inputs()
    require(fanout_report["full_735_column_identity_verified"], "missing complete scalar identity")
    require(fanout_report["ordinary_fanout_helpers"] == 31, "reassess changed helper count")
    require(fanout_report["public_registers"] == 2 * word["v"] + word["R"] + 31 == 735,
            "public register and helper inventory differ")
    public = NB.integers(fanout_report["candidate_public_profile"])
    private = NB.integers(fanout_report["private_COPY_profile"])
    require(private == {7: 8}, "eight actual rank-seven private seeds required")
    require(B.mass(private) == B.CENTRE == 56, "private COPY coverage mass")
    total_profile = B.changed(public, private)
    retained = B.retained_profile()
    helper_mass = 9 * fanout_report["ordinary_fanout_helpers"]
    public_width_increase = B.mass(total_profile) - B.mass(retained) - helper_mass
    require(public_width_increase >= 0, "unexpected public lifetime reduction")
    credit, omissions = NB.gather_credit(word)
    width = Q(B.FAMILIES, B.STAGES)
    coverage_mass = (B.M - 1) * width + B.CENTRE
    selected_a = B.SELECTED_KAPPA / (1 - B.SELECTED_KAPPA)
    target_kappa = B.SELECTED_KAPPA * Q(101, 100)
    target_a = target_kappa / (1 - target_kappa)
    bit_cap = B.BIT_LOWER / (1 + B.BIT_LOWER)
    require(engine.max_idle_rank(B.M) == 51, "outer idle-rank cap changed")

    def describe(name, profile, with_credit):
        model = engine.model(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(model["local_mass"] + model["idle_mass"] == coverage_mass,
                "complete paid mass identity")
        zero = engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, Q(0))
        require(zero[0] <= coverage_mass / (B.M * width) <= zero[1],
                "zero-saving coverage moment")
        root = engine.ceiling(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[0])[1] < 1,
                "uncertified lower saving bracket")
        require(engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[1])[0] > 1,
                "uncertified upper saving bracket")
        selected_moment = engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, selected_a)
        target_moment = engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, target_a)
        require(selected_moment[0] > 1, "cost rejection no longer excludes selected kappa")
        require(target_moment[0] > selected_moment[1], "saving moment is not separated and increasing")
        complex_cap = root[1] / (1 + root[1])
        cap = min(complex_cap, bit_cap)
        require(cap < B.SELECTED_KAPPA, "profile is no longer a selected-kappa rejection")
        margin = ((1 - target_moment[1]) * width, (1 - target_moment[0]) * width)
        return {
            "name": name,
            "status": "SCOPED_COST_REJECTION",
            "optional_gather_credit_assumed": with_credit,
            "local_profile": B.profile_json(profile),
            "model": {key: str(value) for key, value in model.items()},
            "complex_saving_root_interval": B.interval(root),
            "complex_kappa_upper_bound": str(complex_cap),
            "fixed_bit_capped_kappa_upper_bound": str(cap),
            "kappa_upper_bound_decimal": B.decimal(cap),
            "relative_gain_upper_percent_decimal": B.decimal(100 * (cap / B.SELECTED_KAPPA - 1)),
            "moment_at_selected_kappa": B.interval(selected_moment),
            "moment_at_one_percent_target": B.interval(target_moment),
            "per_call_margin_at_one_percent_target": B.interval(margin),
            "selected_kappa_excluded": True,
        }

    scenarios = [describe("actual_31_helper_fanout", total_profile, False),
                 describe("same_with_optional_four_unused_gather_credit",
                          B.changed(total_profile, credit), True)]
    require(scenarios[0]["model"]["local_mass"] == scenarios[1]["model"]["local_mass"],
            "optional gather credit must preserve rank mass")
    return {
        "status": "SCOPED_COST_REJECTION",
        "scope": "This actual finite-word profile cannot improve selected kappa under the retained m73/P104/COPY56 hosted coverage and balanced-transfer model. Other words, coverage laws, and outer recipes are not excluded.",
        "sources": [{"path": path, "sha256": digest} for path, digest in B.INPUTS.values()],
        "actual_profile_source": "fanout.verify()",
        "selected_kappa": str(B.SELECTED_KAPPA),
        "selected_complex_saving_threshold": str(selected_a),
        "one_percent_target_kappa": str(target_kappa),
        "one_percent_complex_saving_threshold": str(target_a),
        "actual_public_profile": B.profile_json(public),
        "actual_private_COPY_profile": B.profile_json(private),
        "ordinary_fanout_helpers": fanout_report["ordinary_fanout_helpers"],
        "new_helper_rank_mass": helper_mass,
        "existing_public_lifetime_width_increase": public_width_increase,
        "retained_16_local_profile": B.profile_json(retained),
        "hypotheses": [
            "Keep m73, nine stages, four pairs, 104 live ports, and COPY rank56.",
            "Retain the complete actual public and private transport histogram; no omitted rank-seven delivery remains.",
            "All remaining paid mass is allowed to form fractional rank51 idle children, regardless of whether such a packing exists.",
            "The second scenario additionally grants the old four-unused-gather credit without proving its joint cleanup compatibility.",
            "Use the retained necessary complex and fixed-bit balanced-transfer inequalities.",
        ],
        "optional_old_gather_credit": {"profile_delta": B.profile_json(credit),
                                       "A_event_indices": omissions,
                                       "joint_fanout_cleanup_verified": False},
        "scenarios": scenarios,
        "controls": {"complete_mass_and_zero_moment_identities": True,
                     "eight_private_rank7_children_charged": True,
                     "both_exact_root_brackets_certified": True,
                     "both_selected_threshold_moments_strictly_above_one": True,
                     "both_kappa_caps_strictly_below_selected": True},
        "selected_private_centre_stock": stock,
        "global_hosting_constructed_by_this_module": False,
        "new_kappa_gain_certified": False,
    }


def verify(fanout_report=None):
    if fanout_report is None:
        fanout_report = module("fanout").verify()
    return price(fanout_report)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
