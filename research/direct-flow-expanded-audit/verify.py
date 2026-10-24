#!/usr/bin/env python3
"""Independent expanded accounting, not native or exponent admission.

Dillon with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
# Compile package sources directly: -B alone would still read preexisting pyc.
def source_module(name):
    import types
    module = types.ModuleType(name)
    module.__file__ = str(PACKAGE / (name + ".py"))
    sys.modules[name] = module
    exec(compile((PACKAGE / (name + ".py")).read_bytes(), module.__file__, "exec"),
         module.__dict__)
    return module

forest_module = source_module("forest")
accounting = source_module("accounting")
literal = source_module("literal")
need = accounting.need


def read(name):
    return json.loads((PACKAGE / name).read_text())


def authenticate():
    manifest = read("SOURCE-EXPORT.json")
    checked = {}
    for row in manifest["files"]:
        data = (PACKAGE / row["path"]).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(digest == row["sha256"] and blob == row["git_blob"],
             "source bytes: " + row["path"])
        checked[row["path"]] = digest
    return checked


def integer_receipt(value):
    need(type(value) is int and value >= 0, "unsigned receipt integer")
    data = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")
    return {"bits": value.bit_length(), "unsigned_big_endian_sha256": hashlib.sha256(data).hexdigest()}


def count_receipt(counts):
    return {key: integer_receipt(value) for key, value in sorted(counts.items())}


def int_hist(hist):
    return {int(k): v for k, v in hist.items()}


def source_comparisons():
    saved = read("vendor/PR4436-RESULT.json")
    fixtures = []
    for entry in saved["finite_flows"]:
        targets, paid = int_hist(entry["targets"]), int_hist(entry["paid"])
        original = entry["flow"]
        actual = forest_module.forest(targets, paid, original["n"])
        need(actual == forest_module.forest(targets, paid, original["n"], literal=True),
             "individual ordered-word forest")
        for ours, theirs in (("sources", "sources"), ("exits", "exits"),
                            ("boundary_exits", "boundary_exits")):
            need(actual[ours] == int_hist(original[theirs]), "source flow " + ours)
        for ours, theirs in (("units", "units"), ("column_mass", "column_mass"),
                            ("matched_jobs", "matched_jobs"), ("height", "height")):
            need(actual[ours] == original[theirs], "source flow " + ours)
        fixtures.append({"rule": entry["rule"], "n": original["n"]})
    return saved, fixtures


def compare_recorded(counts, saved):
    names = {"B": "productive_width", "P": "paid_rank_one_leaves",
             "U": "raw_instances", "Q": "column_mass", "routes": "routing_slots"}
    for ours, theirs in names.items():
        need(integer_receipt(counts[ours]) == saved[theirs], "expanded predecessor " + theirs)


def reject(label, thunk, substring):
    try:
        thunk()
    except ValueError as exc:
        need(substring in str(exc), "wrong rejection for " + label + ": " + str(exc))
        return label
    raise ValueError("accepted mutant: " + label)


def controls():
    rejected = []
    # This tiny physical-rank invoice has a necessary positive complement.
    targets, paid, n = {2: 1}, {1: 1}, 3
    nodes, values, _ = accounting.compile_dag(targets, paid, n, forest_module.forest)
    need(values[n] == {"B": 1, "P": 2, "U": 1, "Q": 1, "routes": 4},
         "hand-calibrated complement example")
    for label, alter in (
        ("omitted_source_complement", lambda node: node.update(calls=[c for c in node["calls"] if c["kind"] != "complement"])),
        ("omitted_exit", lambda node: node.update(calls=[c for c in node["calls"] if c["kind"] != "exit"])),
        ("duplicated_child_batch", lambda node: node["calls"][0].update(batches=2)),
        ("omitted_raw_instance", lambda node: node.update(raw=[])),
        ("wrong_raw_column", lambda node: node.update(raw=[(2, 1)])),
    ):
        mutant = copy.deepcopy(nodes)
        alter(mutant[n])
        value, _ = accounting.reverse_expand(mutant, n)
        rejected.append(reject(label, lambda v=value: accounting.check_expanded(n, v, 1, 2),
                               "expanded rank mass"))
    for delta in (0, -1):
        rejected.append(reject("division_bound_delta_" + str(delta),
                               lambda d=delta: accounting.require_positive_surplus_bound(d),
                               "positive surplus required"))
    # A source-sensitive local mutation must reach the mass predicate.
    bad = copy.deepcopy(forest_module.forest({2: 1, 5: 1}, {1: 2, 4: 1}, 20))
    boundary = next(iter(bad["boundary_exits"]))
    bad["exits"][boundary] -= bad["boundary_exits"][boundary]
    if not bad["exits"][boundary]:
        del bad["exits"][boundary]
    rejected.append(reject("omitted_premature_exit", lambda: accounting.validate_flow(
        bad, {2: 1, 5: 1}, {1: 2, 4: 1}, 20), "local rank mass"))
    # Mutate a separately constructed, literally visited batch plan. These
    # faults enter after source authentication and leave input hashes intact.
    plan = literal.build_plan({2: 4, 3: 1}, {1: 6, 2: 2}, 6)
    bad = copy.deepcopy(plan)
    child = next(c for c in bad["nodes"][6]["children"] if c["width"] > 1)
    child["jobs"] += 1
    rejected.append(reject("nonintegral_child_batch", lambda: literal.walk_plan(bad),
                           "whole child batch divisibility"))
    for label in ("deduplicated_child_instances", "missing_replication", "collapsed_raw_columns",
                  "missing_base_leaf"):
        bad = copy.deepcopy(plan)
        if label == "deduplicated_child_instances":
            for child in bad["nodes"][6]["children"]:
                if child["copies"]:
                    child["copies"] = 1
                    child["jobs"] = child["width"]
        elif label == "missing_replication":
            bad["nodes"][6]["replication"] = 1
        elif label == "collapsed_raw_columns":
            bad["nodes"][6]["raw_columns"] = {1: sum(bad["nodes"][6]["raw_columns"].values())}
        else:
            bad["nodes"][1]["base_leaves"] = 0
        walked = literal.walk_plan(bad)
        value = {key: walked[field] for key, field in
                 (("B", "width"), ("P", "leaves"), ("U", "raw_units"),
                  ("Q", "raw_columns"), ("routes", "routing_slots"))}
        rejected.append(reject(label, lambda v=value: accounting.check_expanded(6, v, 1, 13),
                               "expanded rank mass"))
    rejected.append(reject("nondecreasing_paid_rank", lambda: forest_module.forest(
        {2: 1}, {2: 1}, 3), "strict recursive rank contract"))
    return rejected


def verify():
    sources = authenticate()
    saved, fixtures = source_comparisons()
    summary = []
    rules = [({2: 1, 5: 1}, {1: 2, 4: 1}), ({2: 4, 3: 1}, {1: 6, 2: 2})]
    for (targets, paid), recorded in zip(rules, saved["exact_toy_compilations"]):
        nodes, values, flows = accounting.compile_dag(targets, paid, 100, forest_module.forest)
        compare_recorded(values[100], recorded)
        for rank in range(101):
            reversed_counts, _ = accounting.reverse_expand(nodes, rank)
            need(reversed_counts == values[rank], "reverse counted expansion")
        summary.append({"targets": targets, "paid": paid, "n": 100,
                        "expanded_counts": count_receipt(values[100]),
                        "nonbase_ranks": len(flows), "reverse_expansions": 101})
    raw = read("vendor/PR4436-p7-RESULT.json")["strictification"]["native_inventory"]
    targets, paid = int_hist(raw["targets"]), int_hist(raw["paid"])
    need(accounting.inventory_mass(targets) - accounting.inventory_mass(paid) == 608,
         "p7 source surplus")
    nodes, values, flows = accounting.compile_dag(targets, paid, 1000, forest_module.forest)
    compare_recorded(values[1000], saved["exact_p7_direct_compilation"])
    reverse, invocations = accounting.reverse_expand(nodes, 1000)
    need(reverse == values[1000], "p7 reverse counted expansion")
    p7 = {"n": 1000, "nonbase_ranks": len(flows), "surplus": 608,
          "expanded_counts": count_receipt(values[1000]),
          "positive_invocation_rank_classes": len(invocations),
          "scope": "Counted DAG, not literal enumeration of the enormous program."}
    return {"status": "PASS_DIRECT_FLOW_EXPANDED_ACCOUNTING", "schema_version": 1,
            "source_sha256": sources, "source_flow_fixtures": fixtures,
            "toy_counted_expansions": summary, "p7_counted_expansion": p7,
            "literal_expansions": literal_checks(), "semantic_rejections": controls(),
            "new_kappa": False,
            "scope": "Independent finite expanded accounting and a conditional induction proof; native, physical, all-size exponent and precision admission remain outside scope."}


def literal_checks():
    receipts = []
    cases = [({2: 1}, {1: 1}, 8), ({2: 1, 5: 1}, {1: 2, 4: 1}, 13),
             ({2: 4, 3: 1}, {1: 6, 2: 2}, 6), ({3: 1, 4: 1}, {1: 1, 2: 2}, 13)]
    for targets, paid, maximum in cases:
        _, values, _ = accounting.compile_dag(targets, paid, maximum, forest_module.forest)
        for rank in range(maximum + 1):
            walked = literal.compile_counts(targets, paid, rank, max_events=300000, mode="literal")
            actual = {key: walked[field] for key, field in
                      (("B", "width"), ("P", "leaves"), ("U", "raw_units"),
                       ("Q", "raw_columns"), ("routes", "routing_slots"))}
            need(actual == values[rank], "literal full expansion")
        receipts.append({"targets": targets, "paid": paid, "ranks": [0, maximum],
                         "last_counts": values[maximum], "last_literal_events": walked["events"]})
    # Distinct target words can have the same product (2*8 == 4*4).
    # The literal enumeration retains both before comparing with convolution.
    collision_ranks = [8, 16, 32, 64, 128]
    for rank in collision_ranks:
        args = ({2: 1, 4: 1, 8: 1}, {1: 2, 3: 1}, rank)
        need(forest_module.forest(*args) == forest_module.forest(*args, literal=True),
             "equal-product word multiplicities")
    return {"full_call_tree_cases": receipts, "equal_product_flow_ranks": collision_ranks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="recompute and print a candidate receipt")
    args = parser.parse_args()
    receipt = json.loads(json.dumps(verify(), sort_keys=True))
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        need(receipt == read("RESULT.json"), "saved receipt agrees with recomputation")
        print(receipt["status"])


if __name__ == "__main__":
    main()
