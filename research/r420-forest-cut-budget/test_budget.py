"""Exhaustive literal-ADD audit of small subtrees in the frozen cut certificate.

This checks every cut of the 620 recorded ancestor states with at most eight
descendant edges: 7,904 assignments. It does not prove the remaining states or
search other trees. No constructor, verifier, or budget recurrence is imported.
"""

from copy import deepcopy
import gzip
import hashlib
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
import time
import unittest


HERE = Path(__file__).resolve().parent
MAX_DESCENDANT_EDGES = 8
EXPECTED_STATES = 620
EXPECTED_ASSIGNMENTS = 7904
AUDIT_SECONDS = 90


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def unsigned_pass(events, count, reverse=False):
    """Execute binary ADDs and literal temporary COPY/ERASE lifetimes."""
    values, maximum, work_maximum, active = [1] * (count + 1), 1, 1, None
    for operation, destination, source in reversed(events) if reverse else events:
        if reverse:
            operation = {"COPY": "ERASE", "ERASE": "COPY"}.get(operation, operation)
        if operation == "ADD":
            values[destination] += values[source]
            maximum = max(maximum, values[destination])
            if not 120 <= destination < 240:
                work_maximum = max(work_maximum, values[destination])
        elif operation == "COPY":
            require(active is None, "overlapping reverse-boundary copy")
            values[destination], active = values[source], source
        else:
            require(operation == "ERASE" and active == source, "unmatched copy closure")
            values[destination], active = 0, None
    require(active is None, "unclosed temporary")
    return values[:count], maximum, work_maximum


def load_inputs():
    budget = json.loads((HERE / "data/budget.json").read_text())
    recipe = json.loads((HERE / "data/optimum-recipe.json").read_text())
    with gzip.open(HERE.parents[1] / "research/e8-bit-r420/data/bitE8mut-r420.json.gz", "rt") as stream:
        word = json.load(stream)
    canonical = json.dumps(word, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode("ascii")
    require(hashlib.sha256(canonical).hexdigest() == budget["source_canonical_sha256"] ==
            recipe["source"]["canonical_sha256"], "source canonical identity")
    require((word["v"], word["R"]) == (120, 420), "expected pinned R420 dimensions")
    kernels = [None] * 120
    for frame, destination, sources in word["D"]:
        require(frame == 0 and 120 <= destination < 240 and
                all(240 <= source < 660 for source in sources), "original D shape")
        require(kernels[destination - 120] is None, "duplicate original D target")
        kernels[destination - 120] = frozenset(sources)
    require(all(kernel is not None for kernel in kernels), "missing original D target")

    def additions(gates):
        return [("ADD", destination, source)
                for _, destination, sources in gates for source in sources]

    tail = additions(word["A"])
    for index, helper in enumerate(word["ret"]):
        tail.append(("COPY", 660, helper))
        tail.extend(("ADD", 120 + target, 660)
                    for target, row in enumerate(word["scatter"]) if index in row)
        tail.append(("ERASE", 660, helper))
    tail += additions(word["B"]) + additions(word["C"])
    boundary, tail_maximum, _ = unsigned_pass(tail, 660, reverse=True)
    _, _, fixed_forward = unsigned_pass(additions(word["D"]) + tail, 660)
    require(fixed_forward == budget["forward_maximum_for_every_cut_subset"], "fixed forward bound")
    cap = isqrt(((1 << 104) - 1) // (64 * fixed_forward ** 3))
    require(cap == budget["reverse_maximum_allowed"] and tail_maximum <= cap,
            "unchanged reverse-tail allowance")
    require(boundary[120:240] == budget["reverse_boundary_target_norms"] and
            boundary[240:] == budget["reverse_boundary_helper_norms"], "reverse-boundary magnitudes")
    return budget, recipe["mst_parents"], kernels, boundary, cap


def tree_shape(parents):
    require(len(parents) == 120 and all(type(p) is int and 0 <= p <= 120 for p in parents),
            "parent domain")
    children, depths = [[] for _ in range(121)], []
    for vertex, parent in enumerate(parents):
        children[parent].append(vertex)
        node, depth = vertex, 0
        for _ in range(121):
            if node == 120:
                break
            node, depth = parents[node], depth + 1
        require(node == 120, "parent cycle")
        depths.append(depth)
    subtrees = []
    for vertex in range(120):
        nodes = [vertex]
        for position in range(120):
            if position == len(nodes):
                break
            nodes.extend(children[nodes[position]])
        require(len(nodes) <= 120 and len(set(nodes)) == len(nodes), "invalid subtree")
        subtrees.append(frozenset(nodes))
    return depths, subtrees


def enumerate_state(record, parents, depths, subtree, kernels, boundary, cap):
    """Use actual gates, charging only destinations inside the tested subtree."""
    vertex, root = record["vertex"], record["root"]
    path, node = [], vertex
    for _ in range(120):
        path.append(node)
        if node == root:
            break
        node = parents[node]
        require(node != 120, "state root is not an ancestor")
    require(node == root, "ancestor path limit")
    order = sorted(subtree | set(path), key=lambda i: (-depths[i], i))
    descendants = sorted(subtree - {vertex})
    root_sources = {i: sorted(kernels[i]) for i in order}
    edge_sources = {i: sorted(kernels[i] ^ kernels[parents[i]]) for i in order if i != root}
    feasible_costs, endpoint = {}, None
    assignments = 0
    for cut_count in range(len(descendants) + 1):
        for cuts in combinations(descendants, cut_count):
            assignments += 1
            cut_set = set(cuts)
            prepare = [(i, parents[i]) for i in order if i != root and i not in cut_set]
            values, cost = list(boundary), 0
            for child, parent in prepare:
                values[120 + child] += values[120 + parent]
                cost += child in subtree
            for target in order:
                sources = root_sources[target] if target == root or target in cut_set else edge_sources[target]
                for helper in sources:
                    values[120 + target] += values[helper]
                    cost += target in subtree
            for child, parent in reversed(prepare):
                values[120 + child] += values[120 + parent]
                cost += child in subtree
            if endpoint is None:
                endpoint = values[120 + vertex]
            require(endpoint == values[120 + vertex], "descendant cut changed ancestor endpoint")
            # Every literal ADD is nonnegative, so final values bound all prefixes.
            if max(values[120 + target] for target in order) <= cap:
                feasible_costs[cuts] = cost
    return {"minimum": min(feasible_costs.values(), default=None), "costs": feasible_costs,
            "endpoint": endpoint, "assignments": assignments}


def check_record(record, result):
    state = (record["vertex"], record["root"])
    require(record["norm"] == result["endpoint"], f"state {state}: incorrect endpoint")
    require(record["cost"] == result["minimum"], f"state {state}: incorrect minimum cost")
    if result["minimum"] is None:
        require(record["cuts"] is None, f"state {state}: infeasible cuts")
    else:
        # Childwise tie choices need not give the globally lexicographically first tuple.
        cuts = tuple(record["cuts"])
        require(result["costs"].get(cuts) == result["minimum"],
                f"state {state}: recorded cuts do not attain the minimum")


class BudgetAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        deadline = time.monotonic() + AUDIT_SECONDS
        budget, parents, kernels, boundary, cap = load_inputs()
        depths, subtrees = tree_shape(parents)
        cls.rows = []
        for record in budget["states"]:
            subtree = subtrees[record["vertex"]]
            if len(subtree) - 1 <= MAX_DESCENDANT_EDGES:
                require(time.monotonic() < deadline, "bounded budget audit exceeded 90 seconds")
                result = enumerate_state(record, parents, depths, subtree, kernels, boundary, cap)
                cls.rows.append((record, result))
        cls.assignments = sum(result["assignments"] for _, result in cls.rows)

    def test_exhaustive_literal_subtree_costs(self):
        self.assertEqual(len(self.rows), EXPECTED_STATES)
        self.assertEqual(self.assignments, EXPECTED_ASSIGNMENTS)
        self.assertEqual(sum(result["minimum"] is None for _, result in self.rows), 44)
        self.assertEqual(sum(bool(record["cuts"]) for record, _ in self.rows), 62)
        for record, result in self.rows:
            with self.subTest(vertex=record["vertex"], root=record["root"]):
                check_record(record, result)

    def test_underpriced_feasible_state_is_rejected(self):
        record, result = next(pair for pair in self.rows if pair[0]["cuts"])
        damaged = deepcopy(record)
        damaged["cost"] -= 1
        with self.assertRaisesRegex(AssertionError, "incorrect minimum cost"):
            check_record(damaged, result)

    def test_false_infeasibility_is_rejected(self):
        record, result = next(pair for pair in self.rows if pair[0]["cuts"])
        damaged = deepcopy(record)
        damaged["cost"], damaged["cuts"] = None, None
        with self.assertRaisesRegex(AssertionError, "incorrect minimum cost"):
            check_record(damaged, result)

    def test_nonattaining_cut_witness_is_rejected(self):
        record, result = next(pair for pair in self.rows if pair[0]["cuts"] and
                              pair[1]["costs"].get(()) != pair[1]["minimum"])
        damaged = deepcopy(record)
        damaged["cuts"] = []
        with self.assertRaisesRegex(AssertionError, "recorded cuts do not attain"):
            check_record(damaged, result)


if __name__ == "__main__":
    run = unittest.main(exit=False)
    if run.result.wasSuccessful():
        print(f"PASS_R420_BUDGET_EXHAUSTIVE states={EXPECTED_STATES} "
              f"cut_assignments={EXPECTED_ASSIGNMENTS} max_descendant_edges={MAX_DESCENDANT_EDGES}")
    raise SystemExit(not run.result.wasSuccessful())
