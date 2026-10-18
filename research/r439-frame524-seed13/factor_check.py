#!/usr/bin/env python3
"""Independent finite fixed-factor scheduler check; Python standard library.

This implementation does not import search.py.  It derives both integer factor
matrices from the pinned word, enumerates nonnegative donor multisets by exact
coordinate bounds, and solves a backward Bellman recurrence on update subsets.
Prepared by Ross with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import copy
from functools import lru_cache
import gzip
import json
from pathlib import Path


FRAME = 524
SOURCE_RANGE = (449, 490)
FACTOR_CUTS = ((449, 466), (466, 490))
REGISTERS = (8, 12, 31, 37, 40, 45, 73, 78, 81, 86, 105, 110)
DOMAIN = ("all destination-once positive integer donor schedules of this fixed "
          "integer matrix; identity writes may have no donors")
STOPPING_RULE = ("all reachable subsets processed and all not-yet-written "
                 "destinations tested")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, context):
    need(type(value) is int, context + " must be an integer")
    return value


def derive(word, start, end):
    """Read the actual primitive additions and compose over the integers."""
    rows = [[int(i == j) for j in range(len(REGISTERS))]
            for i in range(len(REGISTERS))]
    index = {r: i for i, r in enumerate(REGISTERS)}
    ops = []
    need(end <= len(word["B"]), "source factor range exceeds phase B")
    for at, gate in enumerate(word["B"][start:end], start):
        need(type(gate) is list and len(gate) == 3, "bad source gate")
        frame, destination, sources = gate
        need(frame == FRAME, f"source B[{at}] has a different frame")
        need(type(sources) is list and len(sources) == 1,
             f"source B[{at}] is not a primitive addition")
        source = sources[0]
        need(destination in index and source in index and destination != source,
             f"source B[{at}] has invalid factor operands")
        d, s = index[destination], index[source]
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
        ops.append([destination, source])
    return rows, ops


def donor_cost(target, mask, destination):
    """Minimize a nonnegative integer donor multiset with exact enumeration.

    A donor is its target row if already updated and its unit row otherwise.
    All entries are nonnegative and each row is nonzero.  For a remaining
    residue v and row r, a coefficient can therefore only be in
    0..min(v[c]//r[c] : r[c]>0).  Those finite intervals enumerate every allowed
    multiset, including when the hybrid row matrix is singular; no matrix
    inverse or unique-coefficient assumption is used.
    """
    n = len(target)
    residue = tuple(x - int(c == destination)
                    for c, x in enumerate(target[destination]))
    need(all(x >= 0 for x in residue), "factor has a negative update residue")
    rows = []
    for donor in range(n):
        if donor == destination:
            continue
        row = tuple(target[donor]) if mask & (1 << donor) else tuple(
            int(c == donor) for c in range(n))
        need(all(x >= 0 for x in row) and any(row),
             "exact-cover method requires nonnegative, nonzero donor rows")
        # If any supported coordinate is absent from the target residue, this
        # row's coefficient is forced to zero before recursion starts.
        if all(v >= x for v, x in zip(residue, row)):
            rows.append(row)
    rows.sort(reverse=True)

    @lru_cache(maxsize=None)
    def cover(position, remaining):
        if not any(remaining):
            return 0
        if position == len(rows):
            return None
        row = rows[position]
        cap = min(v // x for v, x in zip(remaining, row) if x)
        best = None
        for coefficient in range(cap + 1):
            rest = tuple(v - coefficient * x for v, x in zip(remaining, row))
            suffix = cover(position + 1, rest)
            if suffix is not None:
                cost = coefficient + suffix
                if best is None or cost < best:
                    best = cost
        return best

    return cover(0, residue)


@lru_cache(maxsize=None)
def _minimum(target):
    """Exact minimum for the entire destination-once positive donor class."""
    n = len(target)
    need(n == len(REGISTERS) and all(len(row) == n for row in target),
         "wrong target matrix shape")
    need(all(type(x) is int and x >= 0 for row in target for x in row),
         "target matrix must have nonnegative integer entries")
    all_updated = (1 << n) - 1
    remaining_cost = [None] * (all_updated + 1)
    remaining_cost[all_updated] = 0
    feasible_orders = [0] * (all_updated + 1)
    feasible_orders[all_updated] = 1
    minimum_orders = [0] * (all_updated + 1)
    minimum_orders[all_updated] = 1
    costs = {}
    feasible = 0
    for mask in range(all_updated - 1, -1, -1):
        best = None
        best_orders = 0
        for destination in range(n):
            if mask & (1 << destination):
                continue
            cost = donor_cost(target, mask, destination)
            costs[mask, destination] = cost
            if cost is not None:
                feasible += 1
                suffix = remaining_cost[mask | (1 << destination)]
                if suffix is not None:
                    feasible_orders[mask] += feasible_orders[mask | (1 << destination)]
                    total = cost + suffix
                    if best is None or total < best:
                        best = total
                        best_orders = minimum_orders[mask | (1 << destination)]
                    elif total == best:
                        best_orders += minimum_orders[mask | (1 << destination)]
        remaining_cost[mask] = best
        minimum_orders[mask] = best_orders
    # This reachability pass measures completed coverage separately from the
    # backward minimum, and includes zero-cost updates of identity rows.
    reachable = {0}
    reachable_transitions = 0
    for mask in range(all_updated):
        if mask not in reachable:
            continue
        for destination in range(n):
            if mask & (1 << destination):
                continue
            if costs[mask, destination] is not None:
                reachable.add(mask | (1 << destination))
                reachable_transitions += 1
    return {
        "minimum": remaining_cost[0],
        "subset_count": all_updated + 1,
        "examined_transition_count": len(costs),
        "feasible_transition_count": feasible,
        "reachable_subset_count": len(reachable),
        "reachable_transition_count": reachable_transitions,
        "feasible_orders": feasible_orders[0],
        "minimum_cost_orders": minimum_orders[0],
        "method": "nonnegative donor exact-cover and backward Bellman",
    }


def minimum(target):
    # Copy the cached arithmetic receipt because run() adds witness metadata.
    return dict(_minimum(tuple(tuple(row) for row in target)))


def replay(ops):
    """Check actual integer factor action and destination-once write groups."""
    n = len(REGISTERS)
    index = {r: i for i, r in enumerate(REGISTERS)}
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    prior_destination = None
    completed = set()
    for at, operation in enumerate(ops):
        need(type(operation) is list and len(operation) == 2,
             f"candidate operation {at} is not a destination/source pair")
        destination, source = operation
        integer(destination, "candidate destination")
        integer(source, "candidate source")
        need(destination in index and source in index and destination != source,
             f"candidate operation {at} has invalid operands")
        if destination != prior_destination:
            need(destination not in completed,
                 "candidate revisits a completed destination write group")
            completed.add(destination)
            prior_destination = destination
        d, s = index[destination], index[source]
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def donor_witness(factor, target):
    """Validate the reported order and coefficients as a second witness form."""
    order = factor.get("optimal_order")
    need(type(order) is list and len(order) == len(REGISTERS) and
         all(type(r) is int for r in order) and sorted(order) == list(REGISTERS),
         "candidate destination order is not a permutation")
    coefficients = factor.get("donor_coefficients")
    need(type(coefficients) is list and len(coefficients) == len(order),
         "candidate donor coefficient table has wrong height")
    index = {r: i for i, r in enumerate(REGISTERS)}
    n = len(REGISTERS)
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    compiled = []
    for destination, coefficient_row in zip(order, coefficients):
        d = index[destination]
        need(type(coefficient_row) is list and len(coefficient_row) == n and
             all(type(c) is int and c >= 0 for c in coefficient_row),
             "candidate donor coefficients must be nonnegative integers")
        need(coefficient_row[d] == 0, "candidate uses destination as its own donor")
        next_row = [int(c == d) + sum(coefficient_row[j] * rows[j][c]
                                    for j in range(n)) for c in range(n)]
        need(next_row == target[d],
             "candidate donor coefficients do not realize the target row")
        rows[d] = next_row
        compiled.extend([destination, source]
                        for source, count in zip(REGISTERS, coefficient_row)
                        for _ in range(count))
    need(compiled == factor["new_ops"],
         "candidate donor/order metadata does not compile to its operations")
    return compiled


def run(candidate, word):
    """Validate candidate provenance, fixed-factor minima and actual witness."""
    need(candidate.get("source_range") == list(SOURCE_RANGE),
         "candidate source range mismatch")
    need(candidate.get("registers") == list(REGISTERS),
         "candidate register set mismatch")
    factors = candidate.get("factors")
    need(type(factors) is list and len(factors) == len(FACTOR_CUTS),
         "candidate must contain exactly the two fixed factors")
    receipt = []
    all_gates = []
    for factor, (start, end) in zip(factors, FACTOR_CUTS):
        need(factor.get("start") == start and factor.get("end") == end,
             "candidate factor cut mismatch")
        target, original_ops = derive(word, start, end)
        need(factor.get("original_ops") == original_ops,
             "candidate original operations mismatch actual source word")
        declared_target = factor.get("target_matrix")
        need(type(declared_target) is list and
             all(type(row) is list and all(type(x) is int for x in row)
                 for row in declared_target) and declared_target == target,
             "candidate target matrix mismatch")
        need(factor.get("original_additions") == len(original_ops),
             "candidate original addition count mismatch")
        new_ops = factor.get("new_ops")
        need(type(new_ops) is list, "candidate is missing factor operations")
        need(replay(new_ops) == target,
             "candidate has a different exact integer factor action")
        donor_witness(factor, target)
        original_reverse = replay(list(reversed(original_ops)))
        candidate_reverse = replay(list(reversed(new_ops)))
        need(factor.get("original_positive_reverse_matrix") == original_reverse,
             "candidate original positive reverse matrix mismatch")
        need(factor.get("positive_reverse_matrix") == candidate_reverse,
             "candidate positive reverse matrix mismatch")
        dominated = all(new <= old for new_row, old_row in
                        zip(candidate_reverse, original_reverse)
                        for new, old in zip(new_row, old_row))
        need(dominated and factor.get("positive_reverse_entrywise_dominated") is True,
             "candidate positive reverse domination mismatch")
        report = minimum(target)
        need(report["minimum"] is not None, "factor has no allowed schedule")
        need(factor.get("minimum_additions") == report["minimum"],
             "candidate declared minimum differs from independent minimum")
        need(len(new_ops) == report["minimum"],
             "candidate does not attain the independent factor minimum")
        coverage = factor.get("coverage")
        need(type(coverage) is dict, "candidate coverage must be an object")
        need(coverage.get("completed") is True, "candidate coverage is incomplete")
        need(coverage.get("domain") == DOMAIN, "candidate coverage domain mismatch")
        need(coverage.get("stopping_rule") == STOPPING_RULE,
             "candidate coverage stopping rule mismatch")
        expected_coverage = {
            "destination_count": len(REGISTERS),
            "subset_domain_size": report["subset_count"],
            "reachable_subsets": report["reachable_subset_count"],
            "attempted_transitions": report["examined_transition_count"],
            "feasible_transitions": report["feasible_transition_count"],
            "rejected_transitions": report["examined_transition_count"] -
                                    report["feasible_transition_count"],
            "feasible_orders": report["feasible_orders"],
            "minimum_cost_orders": report["minimum_cost_orders"],
        }
        for key, expected in expected_coverage.items():
            need(coverage.get(key) == expected,
                 "candidate coverage mismatch: " + key)
        all_gates.extend([[FRAME, d, [s]] for d, s in new_ops])
        report.update(start=start, end=end, original_additions=len(original_ops),
                      witness_additions=len(new_ops), target_matrix=target,
                      donor_order_metadata_checked=True,
                      positive_reverse_entrywise_dominated=dominated)
        receipt.append(report)
    need(candidate.get("candidate_gates") == all_gates,
         "candidate concatenated gate witness mismatch")
    return {
        "status": "PASS_INDEPENDENT_FIXED_FACTOR_MINIMA",
        "source_range": list(SOURCE_RANGE),
        "registers": list(REGISTERS),
        "original_additions": SOURCE_RANGE[1] - SOURCE_RANGE[0],
        "minimum_additions": sum(item["minimum"] for item in receipt),
        "factors": receipt,
        "scope": "Exact finite destination-once positive-donor schedules of two "
                 "fixed factors only; does not minimize unrestricted whole-block "
                 "circuits or establish a multiplication theorem.",
    }


def controls(candidate, word):
    """Meaningful rejection controls for witness, minimum and search coverage."""
    mutations = []
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["target_matrix"][0][0] += 1
    mutations.append(("corrupted_integer_matrix", damaged,
                      "candidate target matrix mismatch"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["minimum_additions"] -= 1
    mutations.append(("false_minimum", damaged,
                      "candidate declared minimum differs"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["coverage"]["attempted_transitions"] -= 1
    mutations.append(("wrong_transition_coverage", damaged,
                      "candidate coverage mismatch: attempted_transitions"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["coverage"]["completed"] = False
    mutations.append(("incomplete_coverage", damaged,
                      "candidate coverage is incomplete"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["coverage"]["domain"] = "all circuits"
    mutations.append(("wrong_search_domain", damaged,
                      "candidate coverage domain mismatch"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["new_ops"].append(
        list(damaged["factors"][0]["new_ops"][0]))
    mutations.append(("revisited_destination", damaged,
                      "candidate revisits a completed destination write group"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["donor_coefficients"][0][0] += 1
    mutations.append(("corrupted_donor_coefficient", damaged,
                      "candidate donor coefficients do not realize the target row"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["optimal_order"][0] = \
        damaged["factors"][0]["optimal_order"][1]
    mutations.append(("duplicate_destination_order", damaged,
                      "candidate destination order is not a permutation"))
    damaged = copy.deepcopy(candidate)
    damaged["factors"][0]["positive_reverse_matrix"][0][0] += 1
    mutations.append(("corrupted_positive_reverse", damaged,
                      "candidate positive reverse matrix mismatch"))
    results = []
    for name, damaged, expected_error in mutations:
        try:
            run(damaged, word)
        except ValueError as error:
            need(expected_error in str(error), name + " failed for a different reason")
            results.append({"control": name, "status": "REJECTED",
                            "reason": str(error)})
        else:
            raise ValueError(name + " was incorrectly accepted")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path,
                        default=Path(__file__).with_name("CANDIDATE.json"))
    parser.add_argument("--word", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz")
    parser.add_argument("--matrices-only", action="store_true")
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    with gzip.open(args.word, "rt") as stream:
        word = json.load(stream)
    if args.matrices_only:
        result = [{"start": a, "end": b, **minimum(derive(word, a, b)[0])}
                  for a, b in FACTOR_CUTS]
    else:
        candidate = json.loads(args.candidate.read_text())
        result = run(candidate, word)
        if args.controls:
            result["controls"] = controls(candidate, word)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
