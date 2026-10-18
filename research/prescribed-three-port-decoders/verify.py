#!/usr/bin/env python3
"""Exact prescribed-target cut-code experiment; Python standard library only.

Copyright 2026 woklerx. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. No physical supplier claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from itertools import combinations, permutations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def edges(p):
    return [(u, v) for u, v in combinations(range(2 * p), 2) if u // 2 != v // 2]


def canonical(targets):
    """Orbit under matched-pair permutations/flips and target permutations.

    For every ordering/orientation of the three edges, first occurrences give
    the unique normalized pair labels and signs. The least tuple is canonical.
    """
    candidates = []
    for order in permutations(targets):
        for flips in product((0, 1), repeat=3):
            mapping, sequence = {}, []
            for edge, flip in zip(order, flips):
                for v in edge[::(-1 if flip else 1)]:
                    pair, sign = divmod(v, 2)
                    if pair not in mapping:
                        mapping[pair] = (len(mapping), sign)
                    index, origin = mapping[pair]
                    sequence.append(2 * index + (sign ^ origin))
            candidates.append(tuple(sequence))
    return min(candidates)


def orbit_inventory(p):
    counts = Counter(canonical(t) for t in combinations(edges(p), 3))
    return [(tuple(zip(key[::2], key[1::2])), count) for key, count in sorted(counts.items())]


def partitions4(n):
    """All unlabeled four-block set partitions as restricted-growth strings."""
    labels = [0] * n

    def visit(pos, largest):
        if pos == n:
            if largest == 3:
                yield tuple(labels)
            return
        if largest + n - pos < 3:
            return
        for label in range(min(largest + 1, 3) + 1):
            labels[pos] = label
            yield from visit(pos + 1, max(largest, label))

    yield from visit(1, 0)


def tree_on_blocks(labels, targets):
    parent = list(range(4))

    def root(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for u, v in targets:
        a, b = root(labels[u]), root(labels[v])
        if a == b:
            return False
        parent[a] = b
    return True


def predicted(p, targets):
    degree = Counter(v for edge in targets for v in edge)
    vertices = set(degree)
    if len(vertices) == 3:
        return "triangle", None
    if sorted(degree.values()) == [1, 1, 2, 2] and len({v // 2 for v in vertices}) == 2:
        return "two_pair_path", 6 * p - 11
    return "ordinary_forest", 6 * p - 12


def witness(p, targets, labels):
    graph = edges(p)
    target_set = {tuple(sorted(e)) for e in targets}
    deleted = [e for e in graph if labels[e[0]] != labels[e[1]] and e not in target_set]
    survivors = [e for e in graph if e not in deleted]
    decoders = []
    for index in range(3):
        desired = [int(j == index) for j in range(3)]
        choices = []
        for coefficients in product((0, 1), repeat=4):
            if coefficients[0] != 0:
                continue
            if [coefficients[labels[u]] ^ coefficients[labels[v]] for u, v in targets] == desired:
                choices.append([v for v in range(2 * p) if coefficients[labels[v]]])
        require(len(choices) == 1, "quotient tree must have unique normalized decoder")
        decoders.append(choices[0])
    record = {"partition": list(labels), "deleted_edges": [list(e) for e in deleted],
              "decoder_vertex_sets": decoders, "surviving_inputs": len(survivors)}
    check_witness(p, targets, len(deleted), record)
    return record


def check_witness(p, targets, cost, record):
    graph = edges(p)
    target_set = {tuple(sorted(e)) for e in targets}
    deleted = [tuple(e) for e in record["deleted_edges"]]
    require(len(deleted) == len(set(deleted)) == cost, "deletion count/uniqueness")
    require(set(deleted) <= set(graph), "deleted item is not a port")
    require(not (set(deleted) & target_set), "deleted a target")
    labels = record["partition"]
    require(len(labels) == 2 * p and set(labels) == set(range(4)), "four-block partition")
    require(tree_on_blocks(labels, targets), "target quotient not a tree")
    expected = {e for e in graph if labels[e[0]] != labels[e[1]]} - target_set
    require(set(deleted) == expected, "partition support mismatch")
    survivors = [e for e in graph if e not in deleted]
    require(record["surviving_inputs"] == len(survivors), "surviving count")
    require(len(record["decoder_vertex_sets"]) == 3, "three decoders required")
    for i, vertices in enumerate(record["decoder_vertex_sets"]):
        require(len(set(vertices)) == len(vertices) and set(vertices) <= set(range(2 * p)), "invalid vertex set")
        coefficients = set(vertices)
        # Literal coefficients on EVERY surviving independent source symbol.
        for edge in survivors:
            coefficient = (edge[0] in coefficients) ^ (edge[1] in coefficients)
            require(coefficient == (edge == tuple(sorted(targets[i]))), "decoder source coefficient")


def census(p):
    graph = edges(p)
    orbits = orbit_inventory(p)
    best = [None] * len(orbits)
    chosen = [None] * len(orbits)
    partitions = 0
    for labels in partitions4(2 * p):
        partitions += 1
        cost = sum(labels[u] != labels[v] for u, v in graph) - 3
        for i, (targets, _) in enumerate(orbits):
            if best[i] is not None and cost >= best[i]:
                continue
            if tree_on_blocks(labels, targets):
                best[i], chosen[i] = cost, labels
    records = []
    totals = Counter()
    for i, (targets, multiplicity) in enumerate(orbits):
        kind, expected = predicted(p, targets)
        require(best[i] == expected, f"classification failed p={p} targets={targets}: {best[i]} != {expected}")
        totals[kind] += multiplicity
        record = {"targets": [list(e) for e in targets], "multiplicity": multiplicity,
                  "kind": kind, "minimum_deletions": best[i]}
        if best[i] is not None:
            record["witness"] = witness(p, targets, chosen[i])
        records.append(record)
    require(sum(totals.values()) == len(list(combinations(graph, 3))), "triple coverage")
    return {"p": p, "ports": len(graph), "partitions_checked": partitions,
            "triples_checked": sum(totals.values()), "class_counts": dict(sorted(totals.items())),
            "orbits": records}


def negative_controls(report):
    case = next(x for x in report["cases"] if x["p"] == 5)
    record = next(x for x in case["orbits"] if x["kind"] == "ordinary_forest")
    p, targets, cost = 5, record["targets"], record["minimum_deletions"]
    rejected = []

    def reject(name, edit):
        bad = deepcopy(record["witness"])
        edit(bad)
        try:
            check_witness(p, targets, cost, bad)
        except (ValueError, IndexError, TypeError):
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    reject("omit_required_deletion", lambda w: w["deleted_edges"].pop())
    reject("duplicate_deletion", lambda w: w["deleted_edges"].__setitem__(0, w["deleted_edges"][1]))
    reject("delete_target", lambda w: w["deleted_edges"].__setitem__(0, list(targets[0])))
    reject("admit_nonport_mate_edge", lambda w: w["deleted_edges"].__setitem__(0, [0, 1]))
    reject("zero_decoder", lambda w: w["decoder_vertex_sets"].__setitem__(0, []))
    reject("copy_wrong_target_decoder", lambda w: w["decoder_vertex_sets"].__setitem__(0, w["decoder_vertex_sets"][1]))
    reject("collapse_partition", lambda w: w.__setitem__("partition", [0] * (2 * p)))
    # Algebraic controls: the forbidden extension by a global total changes the model.
    triangle = [(0, 2), (0, 4), (2, 4)]
    rows = [sum((int(v in e) << i) for i, e in enumerate(triangle)) for v in range(10)]
    span = {0}
    for row in rows:
        span |= {x ^ row for x in tuple(span)}
    require(1 not in span and 2 not in span and 4 not in span, "triangle unexpectedly decodable")
    augmented = span | {x ^ 7 for x in span}
    require(len(augmented) == 8, "empty-star boundary control must decode isolated triangle")
    # A mate-pair path must be charged the extra deletion.
    exceptional = next(x for x in case["orbits"] if x["kind"] == "two_pair_path")
    require(exceptional["minimum_deletions"] == 19 and exceptional["minimum_deletions"] != 18,
            "exceptional-path cost control")
    return rejected + ["triangle_cut_rank_obstruction", "empty_star_changes_model", "extra_deletion_required"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate")
    args = parser.parse_args()
    report = {"schema": "prescribed-three-two-port-v1", "field": "F2", "empty_star": False,
              "domain": "all distinct target triples for p=2,...,6, modulo exact matched-pair symmetry",
              "cases": [census(p) for p in range(2, 7)]}
    report["controls"] = negative_controls(report)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    certificate = HERE / "CERTIFICATE.json"
    if args.write:
        certificate.write_text(encoded, encoding="utf-8")
    else:
        require(json.loads(certificate.read_text(encoding="utf-8")) == report, "certificate mismatch")
    print("PASS_PRESCRIBED_THREE_PORT_DECODERS"
          f" triples={sum(c['triples_checked'] for c in report['cases'])}"
          f" orbits={sum(len(c['orbits']) for c in report['cases'])}"
          f" partitions={sum(c['partitions_checked'] for c in report['cases'])}"
          f" controls={len(report['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
