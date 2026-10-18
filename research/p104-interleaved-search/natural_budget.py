#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Conditional cost screen for the actual-source, one-term delivery fragment.

The actual one-term invoice is replayed by natural_delivery.verify(). Seven
missing deliveries are priced as bare H7 descents with every other requirement
free. Fractional rank-51 residual packing and the optional old-gather saving
are optimistic assumptions, not a complete supplier or a kappa improvement.

Uses the pinned selected profile and attributed interval engine from budget.py.
Run from any directory, standard library only:
  python3 -I -B research/p104-interleaved-search/natural_budget.py
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location("p104_natural_budget_" + name,
                                                 HERE / (name + ".py"))
    if spec is None or spec.loader is None:
        raise ValueError("cannot load " + name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


B = module("budget")
N = module("natural_delivery")
require = B.require


def integers(profile):
    return {int(rank): int(count) for rank, count in profile.items() if count}


def gather_credit(word):
    """Recount old full frame paths, not the changed fragment's cleanup.

    The source-construction verifier proves deletion of the four unused gathers
    preserves its query rows and live-Y rows. Here only their old full-path
    invoice is checked. Applying this credit jointly to the new delivery and
    its required final restoration is an explicitly unproved assumption.
    """
    frames = [N.D.span(frame) for frame in word["frames"]]
    inputs = N.S.load_inputs()
    coordinates = inputs["coordinates"]
    tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    hyperplane = lambda x: frozenset(y for y in range(512)
                                    if not (x & y).bit_count() % 2)
    axes = {frame: next(axis for axis in range(8)
                        if frames[frame] == hyperplane(tau(coordinates["binary_ports"][axis])))
            for frame in word["center_frames"]}
    retained_axes = {0, 5, 6, 7}
    omitted = [k for k, event in enumerate(word["A"])
               if k >= len(word["A"]) - 48 and axes[event[-1]] not in retained_axes]
    require(len(omitted) == 24, "four unused coordinate gathers")

    def replay(skip):
        current = [frames[index] for index in word["start"]]
        paid = Counter()

        def climb(register, target):
            require(current[register] <= target, "nonmonotone old gather path")
            rank = N.D.dimension(target) - N.D.dimension(current[register])
            if rank:
                paid[rank] += 1
            current[register] = target

        for phase in ("A", "B", "tail"):
            for k, event in enumerate(word[phase]):
                if phase == "A" and k in skip:
                    continue
                for register in event[1:3] if event[0] == "add" else event[1:2]:
                    climb(register, frames[event[-1]])
        for register, index in enumerate(word["final"]):
            climb(register, frames[index])
        for event in word["cleanup"]:
            for register in event[1:3] if event[0] == "add" else event[1:2]:
                climb(register, frames[event[-1]])
        # The comparison includes the eight old private H8 children.
        paid[8] += len(word["center_frames"])
        return dict(paid)

    old, new = replay(set()), replay(set(omitted))
    require(old == B.SELECTED_PROFILE, "old gather replay does not bind selected profile")
    delta = {rank: new.get(rank, 0) - old.get(rank, 0)
             for rank in new.keys() | old.keys() if new.get(rank, 0) != old.get(rank, 0)}
    require(delta == {1: -28, 4: -28, 5: 28}, "old gather credit changed")
    require(B.mass(delta) == 0, "gather omission changes total rank mass")
    return delta, omitted


def price(delivery, *, assume_seven_free_deliveries=False):
    """Require an explicit relaxation; this function never certifies a supplier."""
    require(assume_seven_free_deliveries,
            "incomplete fragment: explicitly assume seven otherwise-free H7 deliveries")
    engine, word, _, stock = B.load_inputs()
    require(delivery["full_704_column_increment_verified"], "unverified one-term increment")
    require(delivery["pair_hamming_root_indices"] == [3, 113], "wrong delivered term")
    require(not delivery["complete_eight_term_supplier"], "review scope before pricing complete supplier")
    require(delivery["additional_public_query_registers"] == 0, "unpriced external query register")
    require(delivery["private_copies_created"] == delivery["peak_private_copies"] == 1,
            "one-copy fragment changed")

    retained = B.retained_profile()
    baseline = integers(delivery["baseline_profile"])
    require(B.changed(retained, {7: -8}) == baseline,
            "actual baseline is not pinned retained-16 public profile")
    public_delta = integers(delivery["public_profile_delta"])
    private = integers(delivery["private_COPY_profile"])
    residual_delta = integers(delivery["residual_width_delta"])
    require(B.changed(baseline, public_delta) == integers(delivery["candidate_public_profile"]),
            "candidate public invoice differs from its replay delta")
    require(B.mass(private) == 7, "actual private descent is not rank seven")
    require(B.mass(public_delta) == delivery["public_rank_mass_delta"], "public mass mismatch")
    require(B.mass(residual_delta) == delivery["residual_rank_mass_delta"], "residual mass mismatch")
    require(B.mass(public_delta) + B.mass(residual_delta) == 0,
            "public increase does not replace the reported residual width")
    delta = Counter(public_delta)
    delta.update(private)
    delta[7] -= 1
    local = B.changed(retained, delta)
    require(B.mass(local) - B.mass(retained) == -B.mass(residual_delta),
            "actual private replacement or residual cancellation is inconsistent")
    credit, omissions = gather_credit(word)
    target_kappa = B.SELECTED_KAPPA * Q(101, 100)
    target_a = target_kappa / (1 - target_kappa)
    bit_cap = B.BIT_LOWER / (1 + B.BIT_LOWER)
    width = Q(B.FAMILIES, B.STAGES)
    h1 = engine.child_cost(1, B.M, target_a)
    total = (B.M - 1) * width + B.CENTRE
    require(engine.max_idle_rank(B.M) == 51, "optimistic idle rank changed")

    def describe(name, profile, with_credit):
        model = engine.model(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(model["local_mass"] + model["idle_mass"] == total, "full coverage mass identity")
        zero = engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, Q(0))
        require(zero[0] <= total / (B.M * width) <= zero[1], "zero-saving moment identity")
        root = engine.ceiling(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        require(engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[0])[1] < 1,
                "uncertified lower root bracket")
        require(engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[1])[0] > 1,
                "uncertified upper root bracket")
        moment = engine.relax(profile, B.M, B.FAMILIES, B.STAGES, B.CENTRE, target_a)
        margin = ((1 - moment[1]) * width, (1 - moment[0]) * width)
        require(margin[0] > 0, "one-percent target already excluded")
        counts = (margin[0] // h1[1], margin[1] // h1[0])
        require(counts[0] == counts[1], "excess-H1 count not resolved by exact intervals")
        # Excess travel must be added to the moment, never silently substituted
        # for one unit of the already covered idle mass.
        excess_moment = tuple(moment[i] + h1[i] / width for i in (0, 1))
        after_one = (margin[0] - h1[1], margin[1] - h1[0])
        require((excess_moment[1] < 1) if with_credit else (excess_moment[0] > 1),
                "one true excess H1 must fit only with optional gather credit")
        require(int(counts[0]) == int(with_credit), "unexpected excess-H1 headroom")
        complex_cap = root[1] / (1 + root[1])
        cap = min(complex_cap, bit_cap)
        return {
            "name": name, "status": "CEILING_NOT_SUPPLIER",
            "optional_gather_credit_assumed": with_credit,
            "local_profile": B.profile_json(profile),
            "model": {key: str(value) for key, value in model.items()},
            "complex_saving_root_interval": B.interval(root),
            "complex_kappa_upper_bound": str(complex_cap),
            "fixed_bit_capped_kappa_upper_bound": str(cap),
            "kappa_upper_bound_decimal": B.decimal(cap),
            "relative_gain_upper_percent_decimal": B.decimal(100 * (cap / B.SELECTED_KAPPA - 1)),
            "moment_at_one_percent_target": B.interval(moment),
            "per_call_margin_at_one_percent_target": B.interval(margin),
            "true_excess_H1_upper_count": int(counts[0]),
            "one_true_excess_H1_moment": B.interval(excess_moment),
            "per_call_margin_after_one_true_excess_H1": B.interval(after_one),
        }

    return {
        "status": "CEILING_NOT_SUPPLIER",
        "scope": "Conditional pricing of one actual-source term; seven deliveries and final completion remain unproved. No kappa improvement is certified.",
        "sources": [{"path": path, "sha256": digest} for path, digest in B.INPUTS.values()],
        "selected_kappa": str(B.SELECTED_KAPPA),
        "target_kappa": str(target_kappa),
        "necessary_complex_saving_for_target": str(target_a),
        "retained_16_local_profile": B.profile_json(retained),
        "actual_public_profile_delta": B.profile_json(public_delta),
        "actual_private_COPY_profile": B.profile_json(private),
        "actual_residual_width_delta": B.profile_json(residual_delta),
        "missing_deliveries": 7,
        "assumptions": [
            "Retain m=73, nine stages, four pairs, 104 ports, and COPY rank56.",
            "Retain all sixteen deleted X/Y roles as dirty helpers with the pinned public baseline.",
            "Use the actual source-formed one-term invoice; no external public Q bank is added.",
            "Each of the other seven terms costs only one H7 child; all its delivery overhead, dirty correction, and interactions are free.",
            "Completion of the comparison baseline's punctured-Y restoration costs no additional paid transport; no complete eight-term endpoint proof is supplied.",
            "All residual mass is fractionally packed at rank51; actual owners, chronology, backward admission, and primitive bounds remain unproved.",
            "Only the second scenario assumes the old four-unused-gather saving remains valid jointly with the changed delivery and its rederived cleanup.",
            "The fixed-bit and complex caps use the retained necessary balanced-transfer inequalities.",
        ],
        "optional_old_gather_credit": {
            "profile_delta": B.profile_json(credit), "A_event_indices": omissions,
            "full_old_paths_recounted": True, "joint_changed_cleanup_verified": False,
        },
        "true_excess_H1_cost_at_target": B.interval(h1),
        "scenarios": [describe("one_actual_term_seven_free_H7_deliveries", local, False),
                      describe("same_with_optional_four_unused_gather_credit",
                               B.changed(local, credit), True)],
        "selected_private_centre_stock": stock,
        "controls": {"full_mass_and_zero_moment_identities": True,
                     "actual_public_plus_residual_mass_is_zero": True,
                     "actual_private_mass_is_seven": True,
                     "one_excess_H1_fits_only_with_conditional_credit": True},
    }


def verify():
    delivery = N.verify()
    try:
        price(delivery)
    except ValueError as error:
        rejected = str(error)
    else:
        raise ValueError("incomplete fragment silently priced without its optimistic assumption")
    report = price(delivery, assume_seven_free_deliveries=True)
    report["controls"]["missing_optimistic_assumption_rejected"] = rejected
    report["delivery_negative_controls"] = delivery["negative_controls"]
    return report


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
