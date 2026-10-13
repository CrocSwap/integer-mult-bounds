#!/usr/bin/env python3
"""Independent exact check of the chosen R439 frame-506 two-factor witness.

Direct donor-subset enumeration and backward Bellman; no discovery imports.
Prepared with substantial OpenAI Codex assistance; Apache-2.0. The underlying
word and finite scheduling lineage are credited in this package's NOTICE.md.
"""

import argparse
import copy
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SOURCE_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
FRAME = 506
SOURCE_RANGE = (102, 128)
CUTS = ((102, 114), (114, 128))
REGISTERS = (5, 6, 9, 46, 47, 48, 52, 54, 56, 58)
EXPECTED_MINIMA = (9, 12)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def validate_ops(ops, destination_once=False):
    need(type(ops) is list, "operations must be a list")
    previous = None
    groups = set()
    for operation in ops:
        need(type(operation) is list and len(operation) == 2,
             "operation must be a destination/source pair")
        destination, source = operation
        need(type(destination) is int and type(source) is int,
             "operation operands must be integers")
        need(destination in REGISTERS and source in REGISTERS and destination != source,
             "operation has an invalid operand")
        if destination_once and destination != previous:
            need(destination not in groups, "factor revisits a finished destination")
            groups.add(destination)
            previous = destination


def apply(ops, values, sign=1, boolean=False):
    """Execute actual scalar values, separately from the donor-mask arithmetic."""
    need(len(values) == len(REGISTERS), "input vector has the wrong length")
    state = dict(zip(REGISTERS, values))
    for destination, source in ops:
        if boolean:
            state[destination] ^= state[source]
        else:
            state[destination] += sign * state[source]
    return [state[r] for r in REGISTERS]


def matrix_by_columns(ops, sign=1):
    n = len(REGISTERS)
    columns = [apply(ops, [int(i == j) for i in range(n)], sign)
               for j in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def original(word, start, end):
    need(type(word.get("B")) is list and end <= len(word["B"]),
         "source phase B is missing or too short")
    ops = []
    for gate in word["B"][start:end]:
        need(type(gate) is list and len(gate) == 3, "malformed source gate")
        frame, destination, donors = gate
        need(frame == FRAME and type(donors) is list and len(donors) == 1,
             "source range is not the expected singleton frame block")
        ops.append([destination, donors[0]])
    validate_ops(ops)
    return ops


@lru_cache(maxsize=None)
def _minimum(target):
    """Exhaust the positive-integer destination-once class at the chosen cut.

    These two targets are binary with diagonal one. Every available donor is
    nonzero and binary, and the wanted row is binary. Therefore a donor cannot
    repeat and two chosen donors cannot overlap in any coordinate. Enumerating
    disjoint donor subsets covers every positive integer multiset here. This
    argument is specific to these targets, not an assumption about other cuts.
    """
    n = len(REGISTERS)
    need(len(target) == n and all(len(row) == n for row in target),
         "factor target has the wrong shape")
    need(all(type(x) is int and x in (0, 1) for row in target for x in row),
         "chosen-cut enumeration requires binary target rows")
    need(all(target[i][i] == 1 for i in range(n)),
         "chosen-cut enumeration requires diagonal one")
    row_masks = [sum(x << j for j, x in enumerate(row)) for row in target]
    full = (1 << n) - 1
    transition_cost = {}
    subset_expansions = 0
    for state in range(full + 1):
        for destination in range(n):
            if state & (1 << destination):
                continue
            wanted = row_masks[destination] ^ (1 << destination)
            # Each item is the union of selected donors and its minimum size.
            # The expansion visits every fitting disjoint donor subset; merging
            # equal unions retains the smaller size, which is sufficient for
            # the minimum-cost transition.
            unions = {0: 0}
            for donor in range(n):
                if donor == destination:
                    continue
                bits = row_masks[donor] if state & (1 << donor) else 1 << donor
                if bits & ~wanted:
                    continue
                expanded = dict(unions)
                for used, size in unions.items():
                    subset_expansions += 1
                    if used & bits:
                        continue
                    joined = used | bits
                    if joined not in expanded or expanded[joined] > size + 1:
                        expanded[joined] = size + 1
                unions = expanded
            transition_cost[state, destination] = unions.get(wanted)

    # Backward Bellman visits every subset, including unreachable hybrid states.
    # Only paths from the empty state count as schedules of the original factor.
    distance = [None] * (full + 1)
    orders = [0] * (full + 1)
    minimum_orders = [0] * (full + 1)
    distance[full], orders[full], minimum_orders[full] = 0, 1, 1
    for state in range(full - 1, -1, -1):
        choices = []
        for destination in range(n):
            if state & (1 << destination):
                continue
            cost = transition_cost[state, destination]
            next_state = state | (1 << destination)
            if cost is None or distance[next_state] is None:
                continue
            orders[state] += orders[next_state]
            choices.append((cost + distance[next_state], minimum_orders[next_state]))
        if choices:
            distance[state] = min(value for value, _ in choices)
            minimum_orders[state] = sum(count for value, count in choices
                                        if value == distance[state])
    reachable = {0}
    reachable_edges = 0
    for state in range(full):
        if state not in reachable:
            continue
        for destination in range(n):
            if state & (1 << destination):
                continue
            if transition_cost[state, destination] is not None:
                reachable.add(state | (1 << destination))
                reachable_edges += 1
    return {
        "minimum": distance[0],
        "subset_domain_size": full + 1,
        "examined_state_destination_pairs": len(transition_cost),
        "feasible_edges_all_subsets": sum(c is not None for c in transition_cost.values()),
        "reachable_subsets": len(reachable),
        "reachable_edges": reachable_edges,
        "feasible_orders": orders[0],
        "minimum_cost_orders": minimum_orders[0],
        "donor_union_expansions": subset_expansions,
        "method": "disjoint donor subsets and backward Bellman",
    }


def minimum(target):
    return dict(_minimum(tuple(tuple(row) for row in target)))


def inverse_checks(old_ops, new_ops):
    n = len(REGISTERS)
    old_inverse = matrix_by_columns(list(reversed(old_ops)), -1)
    new_inverse = matrix_by_columns(list(reversed(new_ops)), -1)
    need(old_inverse == new_inverse, "signed inverse matrices disagree")
    for j in range(n):
        basis = [int(i == j) for i in range(n)]
        for ops in (old_ops, new_ops):
            forward = apply(ops, basis)
            restored = apply(list(reversed(ops)), forward, -1)
            need(restored == basis, "signed inverse failed on a dirty basis column")
            backward = apply(list(reversed(ops)), basis, -1)
            need(apply(ops, backward) == basis, "forward-after-inverse failed")
    return n


def run(candidate, word):
    need(candidate.get("source_range") == list(SOURCE_RANGE), "candidate source range differs")
    need(candidate.get("registers") == list(REGISTERS), "candidate register set differs")
    factors = candidate.get("factors")
    need(type(factors) is list and len(factors) == 2, "candidate must have two factors")
    receipts = []
    all_old, all_new = [], []
    for factor, (start, end), expected in zip(factors, CUTS, EXPECTED_MINIMA):
        need(factor.get("start") == start and factor.get("end") == end,
             "candidate selected factor cut differs")
        old_ops = original(word, start, end)
        target = matrix_by_columns(old_ops)
        need(factor.get("original_ops") == old_ops, "candidate original operations differ")
        need(factor.get("target_matrix") == target, "candidate target matrix differs")
        need(type(factor.get("original_additions")) is int and
             factor["original_additions"] == len(old_ops), "false original addition count")
        new_ops = factor.get("new_ops")
        validate_ops(new_ops, destination_once=True)
        need(matrix_by_columns(new_ops) == target, "candidate integer endpoint differs")
        receipt = minimum(target)
        need(receipt["minimum"] == expected, "unexpected exact chosen-factor minimum")
        claimed = factor.get("minimum_additions")
        need(type(claimed) is int and claimed == receipt["minimum"] == len(new_ops),
             "false claimed factor minimum")
        receipt["dirty_columns"] = inverse_checks(old_ops, new_ops)
        receipt["source_range"] = [start, end]
        receipts.append(receipt)
        all_old.extend(old_ops)
        all_new.extend(new_ops)
    need(matrix_by_columns(all_old) == matrix_by_columns(all_new),
         "composed two-factor integer endpoint differs")
    dirty_columns = inverse_checks(all_old, all_new)
    n = len(REGISTERS)
    for bits in range(1 << n):
        values = [(bits >> j) & 1 for j in range(n)]
        left = apply(all_old, values, boolean=True)
        right = apply(all_new, values, boolean=True)
        need(left == right, "Boolean endpoint differs")
        need(apply(list(reversed(all_new)), right, boolean=True) == values,
             "literal Boolean reverse failed to restore an input")
    return {
        "status": "PASS_R439_FRAME506_INDEPENDENT",
        "factor_minima": [r["minimum"] for r in receipts],
        "original_additions": len(all_old),
        "candidate_additions": len(all_new),
        "factors": receipts,
        "composed_dirty_columns": dirty_columns,
        "boolean_inputs": 1 << n,
        "signed_inverse": "both directions on every integer basis column",
    }


def negative_controls(candidate, word):
    mutants = []
    changed_donor = copy.deepcopy(candidate)
    operation = changed_donor["factors"][0]["new_ops"][0]
    operation[1] = next(r for r in REGISTERS if r not in operation)
    mutants.append(("changed donor", changed_donor))
    omitted = copy.deepcopy(candidate)
    omitted["factors"][0]["new_ops"].pop()
    mutants.append(("omitted forward gate", omitted))
    false_minimum = copy.deepcopy(candidate)
    false_minimum["factors"][0]["minimum_additions"] -= 1
    mutants.append(("false smaller minimum", false_minimum))
    wrong_target = copy.deepcopy(candidate)
    wrong_target["factors"][0]["target_matrix"][0][0] += 1
    mutants.append(("altered target matrix", wrong_target))
    wrong_cut = copy.deepcopy(candidate)
    wrong_cut["factors"][0]["end"] -= 1
    mutants.append(("altered selected cut", wrong_cut))
    rejected = []
    for name, mutant in mutants:
        try:
            run(mutant, word)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control was accepted: " + name)
    ops = [op for factor in candidate["factors"] for op in factor["new_ops"]]
    shortened_reverse = list(reversed(ops))[1:]
    zero = [0] * len(REGISTERS)
    need(apply(shortened_reverse, apply(ops, zero), -1) == zero,
         "zero-input control setup unexpectedly fails")
    failed = []
    for j in range(len(REGISTERS)):
        values = [int(i == j) for i in range(len(REGISTERS))]
        if apply(shortened_reverse, apply(ops, values), -1) != values:
            failed.append(REGISTERS[j])
    need(failed, "omitted inverse gate did not fail on a dirty input")
    rejected.append("omitted inverse gate passes zero input but fails dirty basis")
    return {"rejected": rejected, "count": len(rejected),
            "omitted_inverse_failing_input_registers": failed}


def controls(candidate, word):
    """Small API for the owning full-word verifier."""
    return negative_controls(candidate, word)["rejected"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=HERE / "CANDIDATE.json")
    args = parser.parse_args()
    blob = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(blob).hexdigest() == SOURCE_SHA256, "source SHA256 mismatch")
    word = json.loads(gzip.decompress(blob))
    candidate = json.loads(args.candidate.read_text())
    result = run(candidate, word)
    result["negative_controls"] = negative_controls(candidate, word)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
