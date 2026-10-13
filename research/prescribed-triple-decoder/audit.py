#!/usr/bin/env python3
"""Independent targetwise audit of PR966's pinned prescribed-triple certificate.

Apache-2.0. Eva Ayala, with substantial OpenAI Codex assistance.
Only independent_check is imported; no predecessor or partition verifier is used.
"""
import argparse
from collections import Counter
import copy
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from independent_check import check_p

SOURCE_SHA256 = "ab75a0a3506f66053ad0b7f693738e45db06ff9befdeed4484b9dffaa7f687dc"
SOURCE_COMMIT = "7eaf5665ac246310293fda06a3cf245fe72f6012"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(raw):
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source SHA256 mismatch")
    return json.loads(raw)


def graph(p):
    return tuple((u, v) for u, v in combinations(range(2 * p), 2)
                 if u // 2 != v // 2)


def port_set(values, ports, message):
    result = [tuple(edge) for edge in values]
    require(all(edge in ports for edge in result), message + ": nonport")
    require(len(result) == len(set(result)), message + ": duplicate")
    return set(result)


def validate_witness(p, row):
    ports = set(graph(p))
    targets = [tuple(edge) for edge in row["targets"]]
    require(len(targets) == 3 and len(set(targets)) == 3 and set(targets) <= ports,
            "invalid targets")
    budget = row["minimum_deletions"]
    if budget is None:
        require(len(set(v for edge in targets for v in edge)) == 3,
                "unproved nontriangle impossibility")
        return 0
    witness = row["witness"]
    deleted = port_set(witness["deleted_edges"], ports, "deleted edges")
    require(not deleted & set(targets), "target deleted")
    require(len(deleted) == budget, "wrong deletion count")
    require(witness["surviving_inputs"] == len(ports) - len(deleted),
            "surviving input inventory mismatch")
    vertex_sets = witness["decoder_vertex_sets"]
    require(len(vertex_sets) == 3, "wrong decoder count")
    for target, vertices in zip(targets, vertex_sets):
        require(len(vertices) == len(set(vertices)) and
                all(isinstance(v, int) and 0 <= v < 2 * p for v in vertices),
                "invalid decoder vertices")
        chosen = set(vertices)
        support = {edge for edge in ports if (edge[0] in chosen) != (edge[1] in chosen)}
        require(support - deleted == {target}, "decoder support mismatch")
    labels = witness["partition"]
    require(len(labels) == 2 * p and set(labels) == {0, 1, 2, 3},
            "partition inventory mismatch")
    bits = [tuple(v in vertices for vertices in vertex_sets) for v in range(2 * p)]
    require(all((labels[u] == labels[v]) == (bits[u] == bits[v])
                for u, v in combinations(range(2 * p), 2)),
            "partition does not describe decoder label blocks")
    return 3 * (len(ports) - len(deleted))


def validate_inventory(case):
    p = case["p"]
    ports = len(graph(p))
    triples = ports * (ports - 1) * (ports - 2) // 6
    require(case["ports"] == ports and case["triples_checked"] == triples,
            "port or target inventory mismatch")
    n = 2 * p
    require(case["partitions_checked"] == (4 ** n - 4 * 3 ** n + 6 * 2 ** n - 4) // 24,
            "partition inventory mismatch")


def expand_case(case):
    validate_inventory(case)
    p = case["p"]
    ports = graph(p)
    lookup = {}
    class_counts = Counter()
    equations = 0
    # Explicit full group, independent of first-occurrence canonicalization.
    mappings = [tuple(2 * pair_map[v // 2] + ((v % 2) ^ flips[v // 2])
                      for v in range(2 * p))
                for pair_map in permutations(range(p))
                for flips in product((0, 1), repeat=p)]
    for row in case["orbits"]:
        equations += validate_witness(p, row)
        targets = [tuple(edge) for edge in row["targets"]]
        orbit = {tuple(sorted(tuple(sorted((mapping[u], mapping[v])))
                              for u, v in targets)) for mapping in mappings}
        require(len(orbit) == row["multiplicity"], "orbit multiplicity mismatch")
        require(not lookup.keys() & orbit, "orbit overlap")
        class_counts[row["kind"]] += len(orbit)
        lookup.update((target, row["minimum_deletions"]) for target in orbit)
    require(set(lookup) == set(combinations(ports, 3)), "incomplete target coverage")
    require(dict(class_counts) == case["class_counts"], "class inventory mismatch")
    return lookup, {"p": p, "ports": len(ports), "labelled_target_triples": len(lookup),
                    "orbits": len(case["orbits"]), "group_elements": len(mappings),
                    "retained_decoder_equations": equations}


def compare_targetwise(p, lookup, independent):
    ports = [tuple(edge) for edge in independent["edges"]]
    require(ports == list(graph(p)), "independent graph mismatch")
    for row in independent["targets"]:
        target = tuple(ports[i] for i in row["edge_indices"])
        require(lookup[target] == row["minimum_deletions"],
                "targetwise minimum mismatch: " + repr(target))


def rejected(action, name):
    try:
        action()
    except (ValueError, KeyError, IndexError, TypeError):
        return name
    raise ValueError("negative control was accepted: " + name)


def controls(raw, source, lookups, independent):
    results = [rejected(lambda: load_source(raw + b" "), "source_sha256")]
    case = source["cases"][0]
    original = case["orbits"][0]
    for name in ("zero_decoder", "wrong_target_decoder", "delete_target", "nonport",
                 "duplicate_deletion", "surviving_inventory", "collapse_partition"):
        row = copy.deepcopy(original)
        witness = row["witness"]
        if name == "zero_decoder":
            witness["decoder_vertex_sets"][0] = []
        elif name == "wrong_target_decoder":
            witness["decoder_vertex_sets"][0] = witness["decoder_vertex_sets"][1]
        elif name == "delete_target":
            witness["deleted_edges"][0] = row["targets"][0]
        elif name == "nonport":
            witness["deleted_edges"][0] = [0, 1]
        elif name == "duplicate_deletion":
            witness["deleted_edges"].append(witness["deleted_edges"][0])
        elif name == "surviving_inventory":
            witness["surviving_inputs"] += 1
        else:
            witness["partition"] = [0] * (2 * case["p"])
        results.append(rejected(lambda row=row: validate_witness(case["p"], row), name))
    bad_case = copy.deepcopy(case)
    bad_case["ports"] += 1
    results.append(rejected(lambda: validate_inventory(bad_case), "port_inventory"))
    for p in (3, 4):
        bad = dict(lookups[p])
        ordinary = next(target for target, value in bad.items() if value == 6 * p - 12)
        exceptional = next(target for target, value in bad.items() if value == 6 * p - 11)
        bad[ordinary], bad[exceptional] = bad[exceptional], bad[ordinary]
        require(Counter(bad.values()) == Counter(lookups[p].values()),
                "swap changed the histogram")
        results.append(rejected(lambda p=p, bad=bad: compare_targetwise(p, bad, independent[p]),
                                "histogram_preserving_target_swap_p%d" % p))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "vendor" / "PR966-CERTIFICATE.json")
    parser.add_argument("--write", action="store_true", help="write deterministic AUDIT.json receipt")
    args = parser.parse_args()
    raw = args.source.read_bytes()
    source = load_source(raw)
    require(source["schema"] == "prescribed-three-two-port-v1" and source["field"] == "F2"
            and source["empty_star"] is False, "observation model mismatch")
    require([case["p"] for case in source["cases"]] == [2, 3, 4, 5, 6], "case domain mismatch")
    lookups, cases = {}, []
    for case in source["cases"]:
        lookup, receipt = expand_case(case)
        lookups[case["p"]] = lookup
        cases.append(receipt)
    independent = {}
    for p in (3, 4):
        independent[p] = check_p(p)
        compare_targetwise(p, lookups[p], independent[p])
    receipt = {"format": "pr966-targetwise-independent-audit-v1",
               "source_commit": SOURCE_COMMIT, "source_sha256": SOURCE_SHA256,
               "cases": cases,
               "independent_rref": [{"p": p, "subspaces": independent[p]["subspaces_checked"],
                                     "target_triples": independent[p]["target_triples_checked"]}
                                    for p in (3, 4)],
               "negative_controls": controls(raw, source, lookups, independent)}
    receipt_path = ROOT / "AUDIT.json"
    if args.write:
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(receipt_path.read_text()) == receipt,
                "committed audit receipt differs from fresh replay")
    print(json.dumps(receipt, sort_keys=True))
    print("PASS PR966 targetwise audit: %d triples; %d orbits; %d witnesses; %d targetwise minima; %d controls" % (
        sum(case["labelled_target_triples"] for case in cases),
        sum(case["orbits"] for case in cases),
        sum("witness" in row for case in source["cases"] for row in case["orbits"]),
        sum(result["target_triples_checked"] for result in independent.values()),
        len(receipt["negative_controls"])))


if __name__ == "__main__":
    main()
