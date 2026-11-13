#!/usr/bin/env python3
"""Verify the saved finite-radius orbit-flow and Hall-cut receipts."""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "RESULT.json"
SWEEP_PATH = ROOT / "sweep.py"
sweep = ModuleType("finite_radii_sweep")
sweep.__file__ = str(SWEEP_PATH)
exec(compile(SWEEP_PATH.read_bytes(), str(SWEEP_PATH), "exec"), sweep.__dict__)


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def decode_key(value):
    pattern, sign = value
    return tuple(pattern), sign


def key_set(entries):
    return {decode_key(entry["key"]) for entry in entries}


def active_pairs(data, threshold, inclusive):
    result = set()
    for i, j in data["quotient_edges"]:
        comparison = sweep.compare_pair(data["pair_gap"][(i, j)], threshold)
        if comparison < 0 or (inclusive and comparison == 0):
            result.add((i, j))
    return result


def verify_flow(data, receipt, threshold, inclusive):
    require("flow_certificate" in receipt, "missing positive flow certificate")
    certificate = receipt["flow_certificate"]
    inputs = data["inputs"]
    outputs = data["outputs"]
    source = certificate["input_supplies"]
    loads = certificate["output_loads"]
    require(len(source) == len(inputs), "source supply vector has wrong length")
    require(len(loads) == len(outputs), "output load vector has wrong length")
    require(all(isinstance(value, int) and 0 <= value <= inputs[i]["capacity"]
                for i, value in enumerate(source)),
            "source supply violates an input-orbit capacity")
    require(all(isinstance(value, int) and 0 <= value <= outputs[j]["capacity"]
                for j, value in enumerate(loads)),
            "output load violates an output-orbit capacity")
    active = active_pairs(data, threshold, inclusive)
    row_sums = [0] * len(inputs)
    column_sums = [0] * len(outputs)
    seen = set()
    for triple in certificate["positive_orbit_pair_flows"]:
        require(len(triple) == 3, "malformed orbit-pair flow entry")
        i, j, value = triple
        require(isinstance(i, int) and 0 <= i < len(inputs),
                "flow source orbit index is out of range")
        require(isinstance(j, int) and 0 <= j < len(outputs),
                "flow destination orbit index is out of range")
        require(isinstance(value, int) and value > 0,
                "flow certificate contains a nonpositive amount")
        require((i, j) in active, "positive flow uses an inactive orbit adjacency")
        require((i, j) not in seen, "duplicate orbit-pair flow entry")
        seen.add((i, j))
        row_sums[i] += value
        column_sums[j] += value
    require(row_sums == source, "input-orbit flow conservation failed")
    require(column_sums == loads, "output-orbit flow conservation failed")
    total = sum(source)
    require(total == sum(loads) == receipt["flow"],
            "flow total does not match the receipt")
    require(total <= data["total_inputs"], "flow exceeds total input capacity")
    if receipt["feasible"]:
        require(total == data["total_inputs"], "feasible receipt is not saturated")
        require(source == [orbit["capacity"] for orbit in inputs],
                "saturated receipt omits an input orbit")
    else:
        require(total < data["total_inputs"], "infeasible receipt is saturated")
    require(receipt["active_quotient_adjacencies"] == len(active),
            "active quotient-adjacency count disagrees")
    return total


def verify_cut(data, receipt, threshold, inclusive):
    cut = receipt["maximal_hall_cut"]
    input_map = {orbit["key"]: i for i, orbit in enumerate(data["inputs"])}
    output_map = {orbit["key"]: j for j, orbit in enumerate(data["outputs"])}
    selected_i_keys = key_set(cut["input_orbits"])
    selected_o_keys = key_set(cut["output_orbits"])
    require(selected_i_keys <= set(input_map), "cut contains unknown input orbit")
    require(selected_o_keys <= set(output_map), "cut contains unknown output orbit")
    selected_i = {input_map[key] for key in selected_i_keys}
    selected_o = {output_map[key] for key in selected_o_keys}
    active = active_pairs(data, threshold, inclusive)
    actual_neighbors = {j for i, j in active if i in selected_i}
    require(actual_neighbors == selected_o,
            "cut output set is not the complete lifted neighborhood")
    input_mass = sum(data["inputs"][i]["capacity"] for i in selected_i)
    neighbor_mass = sum(data["outputs"][j]["capacity"] for j in selected_o)
    total = data["total_inputs"]
    cut_capacity = total - input_mass + neighbor_mass
    require(input_mass == cut["input_count"], "cut input capacity disagrees")
    require(neighbor_mass == cut["neighbor_count"], "cut neighbor capacity disagrees")
    require(input_mass - neighbor_mass == cut["deficiency"],
            "Hall deficiency disagrees")
    require(total - cut_capacity == receipt["deficiency"],
            "flow/min-cut duality receipt disagrees")
    if "flow_certificate" in receipt:
        require(cut_capacity == receipt["flow"],
                "verified flow and cut capacities disagree")
    return input_mass, neighbor_mass


def verify_radius(record):
    radius = record["radius"]
    data = sweep.prepare_radius(radius)
    require(data["total_inputs"] == record["domain_and_graph"]["input_count"],
            "input-universe capacity disagrees")
    require(data["total_outputs"] ==
            record["domain_and_graph"]["error_one_candidate_output_count"],
            "output-universe capacity disagrees")
    require(len(data["inputs"]) == record["domain_and_graph"]["input_orbit_count"],
            "input orbit count disagrees")
    require(len(data["outputs"]) ==
            record["domain_and_graph"]["output_candidate_orbit_count"],
            "output orbit count disagrees")
    for side, actual in (("inputs", data["inputs"]),
                         ("candidate_outputs", data["outputs"])):
        saved = record["orbit_capacity_tables"][side]
        actual_by_key = {orbit["key"]: orbit for orbit in actual}
        require(len(saved) == len(actual_by_key), f"{side} table length disagrees")
        for item in saved:
            key = decode_key(item["key"])
            require(key in actual_by_key, f"{side} table has unknown orbit")
            orbit = actual_by_key[key]
            require(orbit["capacity"] == item["capacity"],
                    f"{side} capacity disagrees")
    require(data["error_edge_count"] ==
            record["domain_and_graph"]["error_one_edge_count"],
            "full error-one edge count disagrees")
    target = tuple(record["target_pair"])
    strict_target_edges = sum(
        data["inputs"][i]["capacity"] * data["pair_degree"][(i, j)]
        for i, j in data["quotient_edges"]
        if sweep.compare_pair(data["pair_gap"][(i, j)], target) < 0
    )
    require(strict_target_edges ==
            record["domain_and_graph"]["strict_target_edge_count"],
            "strict target edge count disagrees")
    target_results = record["target_threshold_tests"]
    for name, inclusive in (("inclusive", True), ("strict", False)):
        receipt = target_results[name]
        verify_flow(data, receipt, target, inclusive)
        verify_cut(data, receipt, target, inclusive)
    optimum = record["exact_finite_optimum"]
    require(optimum["exists"], "an exact optimum receipt is required")
    optimum_pair = tuple(optimum["optimum_pair"])
    require(sweep.compare_pair(optimum_pair, optimum_pair) == 0,
            "optimum radical is not exactly comparable")
    require(optimum["optimum_expression"] == sweep.gap_label(optimum_pair),
            "optimum expression disagrees with exact radicands")
    upper = optimum["upper_flow"]
    verify_flow(data, upper, optimum_pair, True)
    require(upper["feasible"], "optimum upper flow is not saturated")
    strict = optimum["strict_lower_cut"]
    verify_cut(data, strict, optimum_pair, False)
    require(not strict["feasible"] and strict["deficiency"] > 0,
            "strict predecessor graph has no Hall obstruction")
    require(optimum["gap_count"] == record["attainable_gap_count"],
            "attainable gap count disagrees")
    return {
        "radius": radius,
        "input_points": data["total_inputs"],
        "output_points": data["total_outputs"],
        "optimum": optimum["optimum_expression"],
        "strict_deficiency": strict["deficiency"],
        "target_feasible": target_results["inclusive"]["feasible"],
    }


def expect_rejection(callable_, explanation):
    try:
        callable_()
    except VerificationError:
        return
    raise VerificationError(f"negative control was accepted: {explanation}")


def negative_controls(record):
    radius = record["radius"]
    data = sweep.prepare_radius(radius)
    optimum = record["exact_finite_optimum"]
    threshold = tuple(optimum["optimum_pair"])
    receipt = json.loads(json.dumps(optimum["upper_flow"]))
    require(receipt["flow_certificate"]["positive_orbit_pair_flows"],
            "cannot mutate an empty positive-flow witness")
    receipt["flow_certificate"]["positive_orbit_pair_flows"][0][2] += 1
    expect_rejection(lambda: verify_flow(data, receipt, threshold, True),
                     "incremented flow edge")

    strict = json.loads(json.dumps(optimum["strict_lower_cut"]))
    require(strict["maximal_hall_cut"]["output_orbits"],
            "cannot mutate an empty cut neighborhood")
    strict["maximal_hall_cut"]["output_orbits"].pop()
    expect_rejection(lambda: verify_cut(data, strict, threshold, False),
                     "deleted cut-neighbor orbit")


def main():
    receipt = json.loads(RESULT.read_text())
    require(receipt["scope"] ==
            "only radii 6, 7, 9, 11 at error cap one for H4/2",
            "saved result scope changed")
    require(receipt["group"]["paired_group_order"] == 192,
            "paired W(D4) action receipt changed")
    group = sweep.graph_group_check()
    require(group == {
        "W4_order": 384,
        "paired_group_order": 192,
        "input_projection_order": 192,
        "output_projection_order": 192,
    }, "paired signed-permutation group recomputation disagrees")
    reports = [verify_radius(record) for record in receipt["completed_radii"]]
    require([item["radius"] for item in reports] == [6, 7, 9, 11],
            "completed radius list expanded or changed")
    for record in receipt["completed_radii"]:
        negative_controls(record)
    print(json.dumps({
        "status": "PASS",
        "verified_radii": reports,
        "negative_controls": [
            "incrementing a positive orbit-pair flow is rejected",
            "deleting a Hall-neighbor orbit is rejected",
        ],
        "untouched_radii": "all radii except 6, 7, 9, 11",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
