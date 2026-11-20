#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test redirecting one existing chart-3 payment after the #7795 retargets.

Uses the S14 authenticated literal reader, constructive compensation and
directed tariff calculation. Each failed stock test has a forward-checked
public input that vanishes on the complete remaining receiver stock.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


def load_support(path):
    spec = importlib.util.spec_from_file_location("public_cut", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def certify(S, graph, application):
    control = S.compensated(graph, True)
    shadow, = control.routes.keys() - graph.routes.keys()
    source, receiver = graph.routes[S.OBSERVER]
    requested_route = (source, receiver)
    requested_grade = graph.grade(requested_route)

    reads = defaultdict(list)
    for slot in control.schedule:
        for operand in control.forms[slot]:
            reads[operand].append(slot)

    first_read, *later_reads = graph.readers(S.OBSERVER)
    all_receiving_events = [slot for slot in graph.schedule if graph.source(slot) == receiver]
    first_receiver_event = all_receiving_events[0]
    S.require(graph.clock[first_receiver_event] <= graph.clock[first_read], "consumer clock order")
    S.require(sum(slot in control.routes and control.routes[slot][1] == receiver
                  for slot in control.schedule if slot != shadow) == 4,
              "compensated control retains four arrivals plus the added control")

    observation = graph.forms[S.OBSERVER]
    S.require(set(observation) <= set(graph.inputs) and
              all(graph.inputs[axis] == source for axis in observation),
              "old observer supported on initial chart-3 public axes")
    S.require(graph.pullback(S.OBSERVER) == {~field: q for field, q in observation.items()},
              "old observer public input identity")

    def event(slot):
        if slot < 0:
            return {"input_axis": ~slot, "chart": graph.inputs[slot]}
        route = control.routes.get(slot)
        result = {
            "slot": slot,
            "native_clock": graph.clock.get(slot),
            "control_clock": control.clock[slot],
        }
        if route is not None:
            result.update(route=list(route), grade=graph.grade(route))
        else:
            result["public_terminal_chart"] = control.terminals[slot]
        return result

    def orientation(route):
        a, b = route
        return len(graph.frames[b]) - len(graph.frames[a])

    roster = []
    for slot in graph.schedule:
        original_route = graph.routes.get(slot)
        if original_route is None or original_route[0] != source:
            continue
        row = {
            "slot": slot,
            "native_clock": graph.clock[slot],
            "original_route": list(original_route),
            "original_grade": graph.grade(original_route),
            "orientation_unchanged": (orientation(original_route) > 0) ==
                                     (orientation(requested_route) > 0),
            "arrives_before_first_use": graph.clock[slot] < graph.clock[first_read],
            "old_observer_locally_available": True,
        }
        same_grade = row["original_grade"] == requested_grade
        row["same_grade"] = same_grade
        if not row["arrives_before_first_use"]:
            row["disposition"] = "late"
        elif slot in (S.RETARGET, S.OBSERVER):
            row["disposition"] = "already_committed_retarget"
            row["committed_route"] = list(control.routes[slot])
        elif row["original_grade"] < requested_grade:
            row["disposition"] = "insufficient_existing_grade"
        else:
            reader_slots = reads[slot]
            row["all_old_reader_slots"] = [event(reader) for reader in reader_slots]
            if not reader_slots:
                row["disposition"] = "receiver_has_no_old_reader"
                roster.append(row)
                continue

            first = reader_slots[0]
            stock = [operand for operand in control.before(first) if operand != slot]
            S.require(control.source(first) == original_route[1], "reader at former destination")
            # The first direct use also implies that no earlier computed other
            # stock can have depended on the withdrawn row in this control.
            original_row = control.pullback(slot)
            equations = S.Equations()
            for operand in stock:
                equations.add(control.pullback(operand), (Q(0),))
            stock_rank = len(equations.rows)
            independent = equations.add(original_row)
            row.update(
                first_old_reader=event(first),
                old_reader_donor_coefficient=str(control.forms[first][slot]),
                causal_stock_at_first_old_reader=[event(operand) for operand in stock],
                stock_rank=stock_rank,
                stock_plus_old_donor_rank=len(equations.rows),
                disposition="first_old_reader_fails" if independent else "first_old_reader_span_passed",
            )
            if independent:
                witness = S.Equations()
                for operand in stock:
                    witness.add(control.pullback(operand), (Q(0),))
                witness.add(original_row, (Q(1),))
                pulse, = witness.inputs_for_right_sides(1)
                forward = control.evaluate(pulse)
                original = graph.evaluate(pulse)
                S.require(all(forward.get(operand, Q(0)) == 0 for operand in stock),
                          f"forward pulse vanishes on former receiver stock at {slot}")
                S.require(forward[slot] == original[slot] == 1, "forward pulse separates old donor")
                S.require(forward[first] == original[first] == control.forms[first][slot] != 0,
                          "forward pulse separates first retained reader")
                row["public_pulse"] = [[axis, str(q)] for axis, q in sorted(pulse.items())]
                row["forward_first_old_reader_value"] = str(forward[first])
                if shadow in stock:
                    S.require(forward[shadow] == original[S.OBSERVER], "shadow preserves original observation")
        roster.append(row)

    early_grade = [row for row in roster if row["arrives_before_first_use"]
                   and row["original_grade"] >= requested_grade]
    screened = [row for row in early_grade if row["disposition"] != "already_committed_retarget"]
    grade_preserving = [row for row in screened if row["same_grade"] and row["orientation_unchanged"]]
    screened_survivors = [row["slot"] for row in screened
                          if row["disposition"] != "first_old_reader_fails"]
    S.require(not screened_survivors, f"unexpected first-reader survivor {screened_survivors}")

    bill = S.pricing(graph, application)
    baseline = Counter(bill["complete_published_baseline_paid"])
    hypothetical = {grade: count + bill["nominal_paid_delta"].get(grade, 0)
                    for grade, count in baseline.items()}
    calls = bill["native_calls"]
    deficit_low, deficit_high = map(Q, bill["baseline_deficit"])
    credit_low, credit_high = map(Q, bill["nominal_credit"])

    bill.update(
        unchanged_grade_transfer_delta={},
        hypothetical_same_grade_paid=hypothetical,
        hypothetical_same_grade_targets=bill["complete_published_baseline_targets"],
        hypothetical_same_grade_signed_margin=S.decimal_enclosure(
            credit_low - deficit_high, credit_high - deficit_low),
        maximum_repair_cost_after_nominal_credit=S.decimal_enclosure(
            credit_low - deficit_high, credit_high - deficit_low),
        new_direct_grade_three_paid={
            grade: count + (calls if grade == requested_grade else 0)
            for grade, count in hypothetical.items()
        },
    )
    return {
        "goal": S.GOAL,
        "step": "s15-rational-funded-fifth",
        "decision": "stopped_at_first_old_receiver",
        "source": {
            "pr": 7830, "head": S.HEAD, "word_sha256": S.WORD,
            "application_sha256": S.APPLICATION, "layout_sha256": S.LAYOUT, "caller": S.CALLER,
        },
        "scope": {
            "orientation": "forward rational",
            "clock_semantics": "zero-based original #7830 schedule ordinal",
            "preservation": (
                "Keep the other delivered payloads and every old reader demand at the former "
                "destination. Retain the four chart-282 arrivals and the two retargets. "
                "Permit any rational-linear formula on the former receiver's available stock."
            ),
            "retargets": [
                {"slot": slot, "original_route": list(graph.routes[slot]), **event(slot)}
                for slot in (S.RETARGET, S.OBSERVER, S.OUTLET)
            ],
            "retired_slot": S.RETIRED,
            "requested_route": list(requested_route),
            "requested_grade": requested_grade,
            "first_chart_282_event": event(first_receiver_event),
            "first_old_90369_reader": event(first_read),
            "all_old_90369_readers": [event(slot) for slot in (first_read, *later_reads)],
            "old_90369_available_before_first_scheduled_event": True,
            "old_90369_public_axes": sorted(~axis for axis in observation),
            "old_90369_term_count": len(observation),
            "chart_3_frame_basis": graph.frames[source],
            "chart_282_frame_basis": graph.frames[receiver],
        },
        "roster_summary": {
            "all_chart_3_paid_sends": len(roster),
            "early_grade_at_least_three": len(early_grade),
            "early_grade_at_least_three_by_grade": dict(Counter(row["original_grade"] for row in early_grade)),
            "already_committed_retargets": [row["slot"] for row in early_grade
                                           if row["disposition"] == "already_committed_retarget"],
            "screened_at_first_old_reader": len(screened),
            "same_grade_and_orientation": len(grade_preserving),
            "screened_survivors": screened_survivors,
            "earliest_same_grade_falsification": grade_preserving[0]["slot"],
            "smallest_same_grade_receiver_bank": min(grade_preserving, key=lambda row: row["stock_rank"])["slot"],
        },
        "roster": roster,
        "signed_price": bill,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", type=Path)
    parser.add_argument("application", type=Path)
    parser.add_argument("--support", type=Path, default=Path(__file__).resolve().parent.parent /
                        "all-outputs" / "replay.py")
    args = parser.parse_args()
    support = load_support(args.support)
    result = certify(support, support.load_word(args.word), support.load_application(args.application))
    result["support_sha256"] = sha256(args.support.read_bytes()).hexdigest()
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
