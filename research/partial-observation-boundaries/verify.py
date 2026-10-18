#!/usr/bin/env python3
"""Independent literal search and arbitrary-dirty checks of the finite boundary model.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Normal execution is read-only. --write-result requires a nonexistent output.
No assert statements are used, so optimized Python preserves every check.
"""
import argparse
from collections import Counter, deque
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import model

WIRES = ((2, 3), (3, 2), (0, 2), (0, 3), (1, 2), (1, 3))
IDENTITY = (1, 2, 4, 8)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def xor(rows, destination, source):
    result = list(rows)
    result[destination] ^= result[source]
    return tuple(result)


def apply_adapter(rows, op):
    return xor(rows, *WIRES[op])


def apply_child(rows, spec):
    output, reader, drift = spec
    rows = xor(rows, output, 2 + reader)
    return xor(rows, 2 + drift, 3 - drift)


def eager_boundaries(calls, initial=IDENTITY):
    rows = initial
    result = [rows]
    for spec in calls:
        rows = apply_child(rows, spec)
        rows = xor(rows, 2 + spec[2], 3 - spec[2])
        result.append(rows)
    return tuple(result)


def literal_observed(rows, expected, mask):
    return all(not (mask & (1 << j)) or rows[j] == expected[j] for j in range(2))


@lru_cache(maxsize=None)
def independent_minimum(calls, masks):
    """0-1 BFS on chronological full four-by-four Boolean linear maps.

    Uses neither the 96-state encoding, its edges, nor its optimizer. A child
    edge costs zero because the same fixed child bill is paid by every plan.
    An observation is checked before leaving its layer for the next child.
    """
    eager = eager_boundaries(calls)
    start = (0, IDENTITY)
    target = (len(calls), eager[-1])
    distances = {start: 0}
    queue = deque([(start, 0)])
    while queue:
        node, price = queue.popleft()
        if distances[node] != price:
            continue
        if node == target:
            return price
        layer, rows = node
        if layer < len(calls) and (layer == 0 or literal_observed(rows, eager[layer], masks[layer - 1])):
            next_node = (layer + 1, apply_child(rows, calls[layer]))
            if price < distances.get(next_node, 10**9):
                distances[next_node] = price
                queue.appendleft((next_node, price))
        for destination, source in WIRES:
            next_node = (layer, xor(rows, destination, source))
            if price + 1 < distances.get(next_node, 10**9):
                distances[next_node] = price + 1
                queue.append((next_node, price + 1))
    raise ValueError("independent search failed to reach the eager endpoint")


def check_word(calls, masks, words, cost=None, inputs=None):
    require(len(words) == len(calls) + 1, "wrong boundary word inventory")
    require(all(type(op) is int and 0 <= op < 6 for word in words for op in word), "bad adapter")
    actual_cost = sum(map(len, words))
    if cost is not None:
        require(actual_cost == cost, "undercharged adapter word")
    cases = tuple(product((0, 1), repeat=4)) if inputs is None else tuple(inputs)
    for initial in cases:
        expected = eager_boundaries(calls, initial)
        rows = initial
        for op in words[0]:
            rows = apply_adapter(rows, op)
        for i, spec in enumerate(calls):
            rows = apply_child(rows, spec)
            for op in words[i + 1]:
                rows = apply_adapter(rows, op)
            require(literal_observed(rows, expected[i + 1], masks[i]), "observed output mismatch")
        require(rows == expected[-1], "final dirty-state mismatch")
    return len(cases)


def independent_partition(calls, masks):
    """Enumerate literal returns and partitions without the primary state graph."""
    eager = eager_boundaries(calls)
    best = 10**9
    for optional in product((False, True), repeat=len(calls) - 1):
        cuts = optional + (True,)
        rows, cost = IDENTITY, 0
        for i, spec in enumerate(calls):
            rows = apply_child(rows, spec)
            if cuts[i]:
                if rows[:2] != eager[i + 1][:2]:
                    break
                found = False
                for length in range(4):
                    for ops in product((0, 1), repeat=length):
                        trial = rows
                        for op in ops:
                            trial = apply_adapter(trial, op)
                        if trial == eager[i + 1]:
                            rows, cost, found = trial, cost + length, True
                            break
                    if found:
                        break
                require(found, "workspace return exceeds the GL2 diameter")
            if not literal_observed(rows, eager[i + 1], masks[i]):
                break
        else:
            best = min(best, cost)
    require(best < 10**9, "independent eager partition unreachable")
    return best


def short_word_floor(calls, masks):
    """All 385 boundary words with at most two adapters on four boundaries."""
    checked, partial_unit = 0, 0
    for length in range(3):
        for locations in product(range(4), repeat=length):
            if tuple(sorted(locations)) != locations:
                continue
            for ops in product(range(6), repeat=length):
                words = tuple(tuple(op for where, op in zip(locations, ops) if where == j) for j in range(4))
                try:
                    check_word(calls, (3, 3, 3), words)
                except ValueError:
                    checked += 1
                else:
                    raise ValueError("full-observer floor has a short counterexample")
                if length == 1:
                    try:
                        check_word(calls, masks, words)
                    except ValueError:
                        pass
                    else:
                        partial_unit += 1
    require(checked == 385 and partial_unit == 2, "short-word coverage drift")
    return {"full_observation_short_words_rejected": checked, "partial_one_adapter_words": partial_unit}


def source_check():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parents[1]
    checked = []
    for source in sources["files"]:
        if source["usage"] != "input":
            continue
        payload = (root / source["path"]).read_bytes()
        require(sha256(payload).hexdigest() == source["sha256"], "source drift: " + source["path"])
        checked.append(source["path"])
    return checked


def expect_failure(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def controls():
    calls = ((0, 0, 0), (1, 0, 1), (1, 0, 0))
    masks = (3, 1, 3)
    price, words = model.solve(calls, masks, True)
    require(price == 1 and words == ((), (1,), (), ()), "named witness drift")
    check_word(calls, masks, words, price)
    failures = []
    failures.append(expect_failure(lambda: check_word(calls, masks, ((), (), (), ())), "omit_noncanonical_adapter"))
    failures.append(expect_failure(lambda: check_word(calls, masks, ((), (0,), (), ())), "use_eager_inverse_instead"))
    failures.append(expect_failure(lambda: check_word(calls, (3, 3, 3), words), "observe_hidden_second_output"))
    failures.append(expect_failure(lambda: check_word(calls, masks, ((1,), (), (), ())), "move_adapter_before_first_child"))
    failures.append(expect_failure(lambda: check_word(calls, masks, words, 0), "omit_adapter_charge"))
    failures.append(expect_failure(lambda: check_word(calls, masks, ((), (1,), (), (0,))), "data_correct_workspace_wrong"))
    check_word(calls, masks, ((), (), (), ()), inputs=((0, 0, 0, 0), (1, 1, 0, 0)))
    changed_reader = (calls[0], (1, 1, 1), calls[2])
    failures.append(expect_failure(lambda: check_word(changed_reader, masks, words), "change_reader_source"))
    failures.append(expect_failure(lambda: model.solve(calls, (3, 1, 0)), "missing_final_observation"))
    failures.append(expect_failure(lambda: model.solve(calls, (3, 1)), "missing_cut"))
    failures.append(expect_failure(lambda: model.solve(((0, 0, 2),), (3,)), "unknown_child_shear"))
    for op in range(6):
        require(apply_adapter(apply_adapter(IDENTITY, op), op) == IDENTITY, "adapter involution")
    require(apply_adapter(apply_adapter(IDENTITY, 0), 1) != apply_adapter(apply_adapter(IDENTITY, 1), 0), "drifts commute")
    require(independent_minimum(calls, (3, 3, 3)) == 3, "full-observer lower bound")
    return {"negative_controls": failures, "positive_controls": ["attaining_dirty_witness", "clean_only_false_positive", "six_adapter_involutions", "noncommuting_workspace_shears", "independent_full_observation_floor"]}


def certify():
    checked_sources = source_check()
    require(len(model.STATES) == 96 and len(set(model.STATES)) == 96, "state coverage")
    literal_maps = set()
    for p0, p1, q0, q1 in model.STATES:
        literal_maps.add((1 | q0 << 2, 2 | q1 << 2, p0 << 2, p1 << 2))
    require(len(literal_maps) == 96, "noninjective full dirty-map representation")
    for s in model.STATES:
        rows = (1 | s[2] << 2, 2 | s[3] << 2, s[0] << 2, s[1] << 2)
        for op in range(6):
            t = model.gate(s, op)
            require(apply_adapter(rows, op) == (1 | t[2] << 2, 2 | t[3] << 2, t[0] << 2, t[1] << 2), "generator semantics")
    hist = Counter()
    per_length = Counter()
    full_costs = {}
    productive_cases = productive_improvements = partial_improvements = 0
    noncommuting_improvements = partition_improvements = dirty_checks = 0
    digest, witness_digest = sha256(), sha256()
    for calls, masks in model.instances():
        n = len(calls)
        cost, words = model.solve(calls, masks, True)
        require(cost == independent_minimum(calls, masks), "independent shortest-path disagreement")
        if calls not in full_costs:
            full_costs[calls] = model.solve(calls, (3,) * n)
            require(full_costs[calls] == independent_minimum(calls, (3,) * n), "full observation disagreement")
        full = full_costs[calls]
        part, cuts = model.restored_partition(calls, masks)
        require(part == independent_partition(calls, masks), "partition comparator disagreement")
        require(cost <= full <= n and cost <= part <= n, "comparator order")
        dirty_checks += check_word(calls, masks, words, cost)
        q = eager_boundaries(calls)[-1][:2]
        productive = q[0] != 1 and q[1] != 2
        productive_cases += productive
        productive_improvements += productive and cost < full
        partial_improvements += cost < full
        noncommuting_improvements += cost < full and len({c[2] for c in calls}) == 2
        partition_improvements += cost < part
        per_length[n] += 1
        hist[(n, cost, full, part)] += 1
        row = [calls, masks, cost, full, part, cuts]
        digest.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
        witness_digest.update((json.dumps(words, separators=(",", ":")) + "\n").encode())
    check_controls = controls()
    calls, masks = ((0, 0, 0), (1, 0, 1), (1, 0, 0)), (3, 1, 3)
    price, words = model.solve(calls, masks, True)
    return {
        "schema_version": 1, "status": "PASS_PARTIAL_OBSERVATION_BOUNDARIES",
        "scope": "exact finite scalar XOR boundary model; no supplier or kappa claim",
        "states": 96, "generator_edges": 576, "instances": sum(per_length.values()),
        "instances_by_length": {str(k): v for k, v in sorted(per_length.items())},
        "histogram_columns": ["children", "partial_adapter_min", "full_observation_adapter_min", "restored_partition_min", "instances"],
        "histogram": [list(key) + [value] for key, value in sorted(hist.items())],
        "partial_observation_improvements": partial_improvements,
        "noncommuting_partial_improvements": noncommuting_improvements,
        "improvements_over_restored_partition": partition_improvements,
        "both_outputs_nonzero_cases": productive_cases,
        "both_outputs_nonzero_partial_improvements": productive_improvements,
        "literal_dirty_input_replays": dirty_checks,
        "census_sha256": digest.hexdigest(), "attaining_words_sha256": witness_digest.hexdigest(),
        "independent_search": "0-1 BFS over full 4x4 binary maps and chronological layers, all 4808 instances",
        "witness": {"children": calls, "masks": masks, "adapter_words": words,
                    "adapter_cost": price, "fixed_child_xors": 6, "total_xors": 7,
                    "full_observation_min_total_xors": 9, "restored_partition_min_total_xors": 9},
        "source_inputs_checked": checked_sources, **check_controls,
        **short_word_floor(calls, masks),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    parser.add_argument("--result", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args()
    if args.write_result:
        require(not args.write_result.exists(), "refusing to overwrite an existing result")
    result = certify()
    encoded = json.dumps(result, indent=2) + "\n"
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as out:
            out.write(encoded)
    else:
        expected = json.loads(args.result.read_text())
        require(json.loads(encoded) == expected, "receipt mismatch")
    print(f"PASS_PARTIAL_OBSERVATION_BOUNDARIES instances={result['instances']} states=96 "
          f"partial_gains={result['partial_observation_improvements']} "
          f"productive_gains={result['both_outputs_nonzero_partial_improvements']} "
          f"dirty_inputs={result['literal_dirty_input_replays']} "
          f"controls={len(result['negative_controls'])} no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("FAIL_PARTIAL_OBSERVATION_BOUNDARIES:", exc, file=sys.stderr)
        raise SystemExit(1)
