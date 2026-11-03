#!/usr/bin/env python3
"""Exact finite corroboration, independent prefixes, and literal dirty calls."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from connector import closed_walk, compile_block, complete_events, require, threshold


def check_sources(root: Path, manifest: dict) -> int:
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == 3, "live source inventory")
    for row in rows:
        actual = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
        require(actual == row["sha256"], "changed source: " + row["path"])
    return len(rows)


def check_prefixes(block) -> int:
    """Rebuild literal integer prefixes without using the walk/compiler logic."""
    k, c = block.dimension, block.characteristic
    require(Counter(block.sources) == Counter({j: c for j in range(k)}), "floor")
    prefixes = [[0] * k]
    for j in block.sources:
        current = prefixes[-1].copy()
        current[j] += 1
        prefixes.append(current)
    for mask in range(1, 1 << k):
        boundaries = block.reads[mask]
        require(len(boundaries) == 2, "depth two")
        for j in range(k):
            coefficient = sum(prefixes[t][j] for t in boundaries) % c
            require(coefficient == (mask >> j) & 1, "wrong read coefficient")
    return (1 << k) - 1


def small_walks() -> tuple[int, int]:
    admitted = checks = 0
    for k in (1, 2):
        for length in range(2, min(8, 2 ** (k + 1)) + 1):
            for labels in product(range(k), repeat=length):
                vertex = 0
                visited = {0}
                counts = Counter(labels)
                for j in labels:
                    vertex ^= 1 << j
                    visited.add(vertex)
                if vertex or len(visited) != 1 << k:
                    continue
                require(max(counts.values()) >= threshold(k), "independent lower bound")
                block = compile_block(k, max(counts.values()), labels)
                checks += check_prefixes(block)
                admitted += 1
    return admitted, checks


def capacity_table() -> list[dict]:
    rows = []
    for c in range(2, 1025):
        allowed = [k for k in range(1, 25) if threshold(k) <= c]
        k = max(allowed)
        require(threshold(k + 1) > c, "threshold inversion")
        b = c.bit_length() - 1
        if c >= 8:
            lower = b + b.bit_length() - 1
            require(lower <= k <= lower + 2, "second-order capacity bound")
        rows.append({"c": c, "k": k, "sources": k * (c // 2) + 2 * (c % 2)})
    selected = {r["c"]: r for r in rows if r["c"] in (58, 64, 256, 512)}
    require([selected[c]["sources"] for c in (58, 64, 256, 512)] ==
            [261, 288, 1408, 3072], "displayed capacities")
    return list(selected.values())


def matvec(matrix: tuple[int, ...], vector: tuple[int, int], c: int) -> tuple[int, int]:
    a, b, d, e = matrix
    x, y = vector
    return ((a * x + b * y) % c, (d * x + e * y) % c)


def add(left: tuple[int, int], right: tuple[int, int], c: int) -> tuple[int, int]:
    return ((left[0] + right[0]) % c, (left[1] + right[1]) % c)


def matrices(k: int, c: int) -> tuple[tuple, tuple]:
    sources = tuple((1, j + 2, j % 3, (j + 2) % c) for j in range(k))
    sources = ((1, 2, 0, 0),) + sources[1:]
    outputs = tuple((m % c, 1, (m // c) % c, 1 + m % 7) for m in range(1 << k))
    return sources, outputs


def execute(events: tuple, c: int, sources: tuple, dirty: tuple[int, int],
            targets: tuple, operators: tuple) -> tuple:
    bmaps, amaps = operators
    z = dirty
    y = list(targets)
    for kind, index in events:
        if kind == "B":
            z = add(z, matvec(bmaps[index], sources[index], c), c)
        else:
            require(kind == "A", "event kind")
            y[index] = add(y[index], matvec(amaps[index], z, c), c)
    return z, tuple(y)


def expected(c: int, sources: tuple, dirty: tuple, targets: tuple, operators: tuple) -> tuple:
    bmaps, amaps = operators
    result = list(targets)
    for mask in range(1, len(targets)):
        combined = (0, 0)
        for j, source in enumerate(sources):
            if mask & (1 << j):
                combined = add(combined, matvec(bmaps[j], source, c), c)
        result[mask] = add(targets[mask], matvec(amaps[mask], combined, c), c)
    return dirty, tuple(result)


def fixtures(k: int, c: int) -> list[tuple]:
    zero = ((0, 0),) * k
    cases = [(zero, (0, 0))]
    for j in range(k):
        for component in range(2):
            values = list(zero)
            values[j] = (1, 0) if component == 0 else (0, 1)
            cases.append((tuple(values), (0, 0)))
    cases.extend(((zero, (1, 0)), (zero, (0, 1))))
    for seed in range(1, 7):
        values = tuple(((seed * (j + 3)) % c, (seed + j * j) % c) for j in range(k))
        cases.append((values, ((3 * seed) % c, (seed + 1) % c)))
    return cases


def literal_checks(block) -> tuple[int, int, tuple]:
    k, c = block.dimension, block.characteristic
    events = complete_events(block)
    prices = Counter(events)
    require(len(prices) == k + (1 << k) - 1, "complete operator inventory")
    require(set(prices.values()) == {c}, "every operator must attain its floor")
    operators = matrices(k, c)
    targets = tuple(((7 * m + 1) % c, (m * m + 3) % c) for m in range(1 << k))
    count = 0
    for sources, dirty in fixtures(k, c):
        actual = execute(events, c, sources, dirty, targets, operators)
        wanted = expected(c, sources, dirty, targets, operators)
        require(actual == wanted, "literal dirty-input execution")
        count += 1
    return count, len(events), (events, operators, targets)


def rejecting_controls(block, transitions: tuple, manifest: dict) -> int:
    count = 0
    attempts = ((0, 58, transitions), (9, 1, transitions), (9, 57, transitions),
                (9, 58, transitions[:-1]), (9, 58, (0, 0)),
                (9, 58, (9,) + transitions[1:]))
    for k, c, word in attempts:
        try:
            compile_block(k, c, word)
        except ValueError:
            count += 1
        else:
            raise ValueError("accepted invalid constructor input")
    changed = json.loads(json.dumps(manifest))
    next(row for row in changed["files"] if row["usage"] == "input")["sha256"] = "0" * 64
    try:
        check_sources(PACKAGE.parents[1], changed)
    except ValueError:
        count += 1
    else:
        raise ValueError("accepted changed source pin")
    altered_reads = list(block.reads)
    altered_reads[1] = (0, 0)
    bad = type(block)(block.dimension, block.characteristic, block.sources, tuple(altered_reads))
    try:
        check_prefixes(bad)
    except ValueError:
        count += 1
    else:
        raise ValueError("accepted wrong read boundaries")
    return count


def call_mutations(block, evidence: tuple) -> int:
    events, operators, targets = evidence
    c, k = block.characteristic, block.dimension
    zero = ((0, 0),) * k
    require(events[0][0] == "A", "padding control setup")
    wanted = expected(c, zero, (1, 1), targets, operators)
    require(execute(events[1:], c, zero, (1, 1), targets, operators) != wanted,
            "unpaid output call not detected")
    position = next(i for i, event in enumerate(events) if event == ("B", 0))
    sources = ((1, 0),) + zero[1:]
    changed = events[:position] + events[position + 1:]
    require(execute(changed, c, sources, (0, 0), targets, operators)[0] != (0, 0),
            "unpaid source call not detected")
    return 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = check_sources(PACKAGE.parents[1], manifest)
    witness = json.loads((PACKAGE / "WITNESS.json").read_text())
    k, c = witness["dimension"], witness["characteristic"]
    require((k, c) == (9, 58), "witness parameters")
    transitions = tuple(witness["transition_sequence"])
    vertices = closed_walk(k, transitions)
    require(len(transitions) == 512 and len(set(vertices[:-1])) == 512, "Hamilton cycle")
    require(sorted(Counter(transitions).values()) == [56] * 5 + [58] * 4, "balance")
    block = compile_block(k, c, transitions)
    masks = check_prefixes(block)
    walks, small_masks = small_walks()
    table = capacity_table()
    cases, events, evidence = literal_checks(block)
    controls = rejecting_controls(block, transitions, manifest) + call_mutations(block, evidence)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    receipt = {"marker": "PASS_CONNECTOR_BALANCED_WALK_THRESHOLD",
               "claim_type": "scoped proof with finite construction corroboration",
               "witness": {"dimension": k, "characteristic": c, "masks": masks,
                           "complete_calls": events, "dirty_fixtures": cases},
               "closed_small_walks": walks, "small_mask_checks": small_masks,
               "capacity_rows": 1023, "displayed_capacities": table,
               "rejected_controls": controls, "live_inputs": inputs, "sha256": hashes}
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        require(PACKAGE not in args.output.resolve().parents, "receipt must be outside package")
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
