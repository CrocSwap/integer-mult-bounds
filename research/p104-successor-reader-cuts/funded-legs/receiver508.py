#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the smallest chart-3 donor bank after releasing its earliest reader."""

import argparse
from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path

from replay import load_support


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", type=Path)
    parser.add_argument("--support", type=Path, default=Path(__file__).resolve().parent.parent /
                        "all-outputs" / "replay.py")
    parser.add_argument("--public-cone", action="store_true")
    args = parser.parse_args()
    S = load_support(args.support)
    word = S.load_word(args.word)
    control = S.compensated(word, True)
    old_donor, partner = 95681, 99128
    first, second = control.readers(old_donor)
    later, = control.readers(partner)
    bank = [s for s in control.stock[508] if s not in (old_donor, partner)]
    S.require(control.before(first) == [old_donor, partner], "first reader stock")
    S.require(first == 97760 and later == 99131 and second == 98212,
              "all direct reads of replaced or recoded slots")

    equations = S.Equations()
    for s in bank:
        equations.add(control.pullback(s), (Q(0), Q(0)))
    trace = [len(equations.rows)]
    equations.add(control.pullback(second), (Q(1), Q(0)))
    trace.append(len(equations.rows))
    equations.add(control.pullback(later), (Q(0), Q(1)))
    trace.append(len(equations.rows))
    S.require(trace == [4, 5, 6], "two fixed receiver directions remain after releasing first")
    pulses = equations.inputs_for_right_sides(2)
    for axis, pulse in enumerate(pulses):
        forward = word.evaluate(pulse)
        S.require(all(forward[s] == 0 for s in bank), "pulse annuls all fixed 508 ingresses")
        S.require([forward[second], forward[later]] == [int(i == axis) for i in range(2)],
                  "the two fixed 508 readers are distinguished on the forward word")

    impulse = word.evaluate({}, {old_donor: Q(1)})
    terminals = [t for t in word.schedule if t in word.terminals and impulse[t]]
    S.require(terminals == [155434, 155662, 155815], "exact original public impact of donor impulse")

    first_receiver_delay = control.readers(first)[0]
    result = {
        "released_first_reader": S.event(word, first),
        "first_read_of_released_reader": S.event(word, first_receiver_delay),
        "funded_donor": S.event(word, old_donor),
        "candidate_same_grade_recoded_508_arrival": S.event(word, partner),
        "stock_before_released_first_reader": [S.event(word, s) for s in control.before(first)],
        "other_508_paid_ingress_bank": [
            S.event(word, s) | {"grade": word.grade(word.routes[s])} for s in bank
        ],
        "protected_reader_order": [S.event(word, s) for s in (second, later)],
        "protected_reader_old_operands": {
            str(s): {i: str(q) for i, q in control.forms[s].items()} for s in (second, later)
        },
        "rank_trace_after_freeing_97760": trace,
        "pulses": [sorted((i, str(q)) for i, q in pulse.items()) for pulse in pulses],
        "public_terminals_affected_by_uncompensated_withdrawal": [
            S.event(word, s) | {"response_to_unit_withdrawn_slot_impulse": str(impulse[s])}
            for s in terminals
        ],
    }
    if not args.public_cone:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    # Generously release every subsequent output from the old receiver
    # and every chart causally reached by any released output.
    reached, affected = {508}, set()
    for slot in control.schedule[control.clock[old_donor] + 1:]:
        if control.source(slot) in reached:
            affected.add(slot)
            if slot in control.routes:
                reached.add(control.routes[slot][1])

    def boundary(target):
        pending = [target]
        seen, outer = set(), set()
        while pending:
            row = pending.pop()
            if row in seen:
                continue
            seen.add(row)
            for operand in control.before(row):
                if operand == old_donor:
                    continue
                if operand in affected:
                    pending.append(operand)
                else:
                    outer.add(operand)
        return outer, seen

    vectors = S.all_public_rows(control)
    public = {}
    for target in terminals:
        fixed, seen = boundary(target)
        freq = Counter(axis for slot in fixed for axis in vectors[slot][1])
        order = sorted(range(len(control.inputs)),
                       key=lambda axis: (freq[axis], axis))
        eq = S.IntegerElimination({axis: index for index, axis in enumerate(order)})
        for slot in sorted(fixed, key=lambda slot: (len(vectors[slot][1]), slot)):
            eq.add(vectors[slot][1])
        rank = len(eq.rows)
        increases = eq.add(vectors[target][1])
        public[target] = {
            "fixed_boundary_count": len(fixed),
            "retimed_or_recoded_event_count": len(seen),
            "fixed_boundary_rank": rank,
            "rank_with_required_terminal": len(eq.rows),
            "required_terminal_outside_span": increases,
        }
    result["public_only_generous_full_physical_cone"] = public
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
