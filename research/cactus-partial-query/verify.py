"""Finite corroboration of the cactus partial-acquisition theorem.

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimizer import check, optimize


def insist(condition, message):
    if not condition:
        raise RuntimeError(message)


def closure(vectors):
    space = {0}
    for vector in vectors:
        space |= {x ^ vector for x in tuple(space)}
    return frozenset(space)


def subspaces(vectors):
    ambient = closure(vectors)
    spaces = {frozenset({0})}
    for _ in range(len(vectors) + 1):
        extended = set(spaces)
        for space in spaces:
            for vector in ambient - space:
                extended.add(space | frozenset(x ^ vector for x in space))
        if extended == spaces:
            break
        spaces = extended
    insist(all(s <= ambient for s in spaces), "subspace outside query span")
    return sorted(spaces, key=lambda s: (len(s), tuple(sorted(s))))


def basis(space):
    result, generated = [], frozenset({0})
    for v in sorted(space):
        if v not in generated:
            result.append(v)
            generated = generated | frozenset(x ^ v for x in generated)
    insist(generated == space, "literal basis did not reconstruct space")
    return result


def literal_cactus(n, edges):
    memberships = [0] * len(edges)
    cycles = []
    for mask in range(1, 1 << len(edges)):
        degrees = [0] * n
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                degrees[u] += 1
                degrees[v] += 1
        active = {i for i, degree in enumerate(degrees) if degree}
        if not active or any(degrees[v] != 2 for v in active):
            continue
        reached = {min(active)}
        for _ in range(n):
            for i, (u, v) in enumerate(edges):
                if mask >> i & 1 and (u in reached or v in reached):
                    reached.update((u, v))
        if reached != active:
            continue
        cycles.append(mask)
        for i in range(len(edges)):
            memberships[i] += mask >> i & 1
    return max(memberships, default=0) <= 1, cycles


def purchase_table(edges, costs):
    vectors = [(1 << u) | (1 << v) for u, v in edges]
    rows = []
    for mask in range(1 << len(edges)):
        chosen = [i for i in range(len(edges)) if mask >> i & 1]
        rows.append((closure(vectors[i] for i in chosen),
                     sum(costs[i] for i in chosen)))
    return rows


def literal_delivery(n, edges, targets, result):
    selected = result["selected"]
    for x in range(1 << n):
        answers = [((x >> u) ^ (x >> v)) & 1 for u, v in edges]
        for j, target in enumerate(targets):
            delivered = sum(answers[i] for i in selected
                            if result["rows"][i] >> j & 1) % 2
            insist(delivered == (x & target).bit_count() % 2,
                   "literal source/query reconstruction")


def exhaustive():
    counts = dict(graphs=0, cacti=0, noncacti=0, optima=0,
                  purchase_subsets=0, cycle_blocks=0, target_bases=0)
    digest = hashlib.sha256()
    for n in range(1, 6):
        possible = list(itertools.combinations(range(n), 2))
        for graph in range(1 << len(possible)):
            edges = [e for i, e in enumerate(possible) if graph >> i & 1]
            counts["graphs"] += 1
            cactus, cycles = literal_cactus(n, edges)
            if not cactus:
                expect_rejection(n, edges, [1] * len(edges), [])
                counts["noncacti"] += 1
                continue
            counts["cacti"] += 1
            counts["cycle_blocks"] += len(cycles)
            vectors = [(1 << u) | (1 << v) for u, v in edges]
            spaces = subspaces(vectors)
            counts["target_bases"] += len(spaces)
            for prices in ([1] * len(edges), list(range(1, len(edges) + 1)),
                           [i % 3 for i in range(len(edges))]):
                table = purchase_table(edges, prices)
                counts["purchase_subsets"] += len(table)
                for space in spaces:
                    targets = basis(space)
                    expected = min(c for s, c in table if space <= s)
                    result = optimize(n, edges, prices, targets)
                    insist(result["cost"] == expected, "subset oracle optimum")
                    insist(check(n, edges, prices, targets, result), "certificate")
                    literal_delivery(n, edges, targets, result)
                    counts["optima"] += 1
                    digest.update(json.dumps([n, edges, prices, targets, result],
                                             sort_keys=True).encode())
    counts["corpus_sha256"] = digest.hexdigest()
    return counts


def expect_rejection(n, edges, costs, targets, result=None):
    try:
        if result is None:
            optimize(n, edges, costs, targets)
        else:
            check(n, edges, costs, targets, result)
    except (ValueError, TypeError, KeyError):
        return
    raise RuntimeError("invalid input/certificate was accepted")


def fixtures_and_controls():
    edges, prices, targets = [(0, 1), (1, 2), (0, 2)], [4, 3, 2], [3]
    answer = optimize(3, edges, prices, targets)
    insist(answer["cost"] == 4 and answer["selected"] == [0], "partial pilot")
    whole = optimize(3, edges, prices, [3, 6])
    insist(whole["cost"] == 5, "whole-span comparison")
    for field in ("cost", "rows", "selected", "base_rows", "cycles",
                  "shifts", "savings", "bridge_bill"):
        corrupted = json.loads(json.dumps(answer))
        if field in ("cost", "bridge_bill"):
            corrupted[field] += 1
        elif field == "cycles":
            corrupted[field][0].pop()
        else:
            corrupted[field] = []
        expect_rejection(3, edges, prices, targets, corrupted)
    bad_shift = dict(whole, rows=[1, 2, 0], shifts=[2], savings=[3])
    expect_rejection(3, edges, prices, [3, 6], bad_shift)
    nonoptimal = dict(answer, rows=[0, 1, 1], shifts=[1], savings=[4],
                      selected=[1, 2], cost=5)
    expect_rejection(3, edges, prices, targets, nonoptimal)
    invalid = [(0, [], [], []), (129, [], [], []), (2, [(0, 0)], [1], []),
               (2, [(1, 0)], [1], []), (2, [(0, 1)] * 2, [1, 2], []),
               (2, [(0, 1)], [-1], []), (2, [(0, 1)], [True], []),
               (2, [(0, 1)], [], []), (2, [(0, 1)], [1], [1]),
               (3, [(0, 1)], [1], [5]), (2, [], [], [4]),
               (2, [], [], [True]), (2, [], [], [0] * 129),
               (2, [(0, 1)], [10**12 + 1], [])]
    for args in invalid:
        expect_rejection(*args)
    return {"semantic_controls": 10, "input_controls": len(invalid),
            "pilot_partial_cost": answer["cost"], "pilot_whole_cost": whole["cost"]}


def larger_fixtures():
    total, max_edges, max_targets = 0, 0, 0
    for cycles in range(1, 33):
        n = 1 + 2 * cycles
        edges = []
        for k in range(cycles):
            a, b = 2 * k + 1, 2 * k + 2
            edges.extend([(0, a), (a, b), (0, b)])
        prices = [(i * 11) % 17 for i in range(len(edges))]
        targets = [(1 << u) | (1 << v) for u, v in edges[::2]]
        targets += [targets[0], 0, 0]
        result = optimize(n, edges, prices, targets)
        insist(check(n, edges, prices, targets, result), "multi-cycle fixture")
        insist(len(result["cycles"]) == cycles, "cycle count fixture")
        total += 1
        max_edges, max_targets = max(max_edges, len(edges)), max(max_targets, len(targets))
    n = 128
    edges = [(i, i + 1) for i in range(n - 1)]
    targets = [(1 << i) | (1 << (i + 1)) for i in range(n - 1)] + [0]
    result = optimize(n, edges, [10**12] * len(edges), targets)
    insist(result["cost"] == 127 * 10**12, "maximum-domain forest")
    return {"larger_fixtures": total + 1, "max_cycle_fixture_edges": max_edges,
            "max_cycle_fixture_targets": max_targets, "max_domain_vertices": n}


def main():
    result = exhaustive()
    result.update(fixtures_and_controls())
    result.update(larger_fixtures())
    names = ["README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "optimizer.py", "verify.py"]
    files = {}
    for name in names:
        path = Path(__file__).resolve().parent / name
        insist(path.stat().st_size <= 262144, "package file capacity")
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"marker": "PASS_CACTUS_PARTIAL_QUERY", "result": result,
                      "package_sha256": files}, sort_keys=True))


if __name__ == "__main__":
    main()
