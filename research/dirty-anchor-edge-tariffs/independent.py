#!/usr/bin/env python3
"""Independent finite audit of source-dependent dirty-row tariffs.

Only the Python standard library is imported. No executable code from the
primary verifier or its predecessors is used. States contain all coefficients
of the q original dirt symbols and one independent common symbol p. Exhaustive
state construction and unrestricted Dijkstra paths are compared with a separate
parent-function enumeration of rooted forests. Every check remains active with
python -O. Default execution only reads files; --output creates an absent file.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import heapq
import itertools
import json
from pathlib import Path


class AuditFailure(RuntimeError):
    """A mathematical or coverage check failed."""


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise AuditFailure(explanation)


def fingerprint(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def alphabet(q: int) -> tuple[tuple[int, ...], ...]:
    # (0,dst) inserts p; (1,dst,src) performs dst ^= src.
    return tuple((0, i) for i in range(q)) + tuple(
        (1, i, j) for i in range(q) for j in range(q) if i != j
    )


def step(state: tuple[int, ...], gate: tuple[int, ...]) -> tuple[int, ...]:
    rows = list(state)
    if gate[0] == 0:
        rows[gate[1]] ^= 1 << len(rows)
    else:
        rows[gate[1]] ^= rows[gate[2]]
    return tuple(rows)


def evaluate(q: int, word: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    state = tuple(1 << i for i in range(q))
    for gate in word:
        state = step(state, gate)
    return state


def determinant_mod_two(rows: tuple[int, ...]) -> int:
    # Direct Leibniz expansion, independent of elementary-row reachability.
    result = 0
    q = len(rows)
    for permutation in itertools.permutations(range(q)):
        term = 1
        for i, column in enumerate(permutation):
            term &= (rows[i] >> column) & 1
        result ^= term
    return result


def full_graph(q: int) -> dict[str, object]:
    gates = alphabet(q)
    start = tuple(1 << i for i in range(q))
    target = tuple((1 << i) | (1 << q) for i in range(q))
    found = {start}
    pending = deque([start])
    while pending:
        state = pending.popleft()
        for gate in gates:
            successor = step(state, gate)
            if successor not in found:
                found.add(successor)
                pending.append(successor)

    matrices = tuple(
        matrix
        for matrix in itertools.product(range(1 << q), repeat=q)
        if determinant_mod_two(matrix) == 1
    )
    independently_enumerated = {
        tuple(matrix[i] | (((common >> i) & 1) << q) for i in range(q))
        for matrix in matrices
        for common in range(1 << q)
    }
    require(found == independently_enumerated, f"q={q}: reachable affine-state coverage")
    gl_formula = 1
    for i in range(q):
        gl_formula *= (1 << q) - (1 << i)
    require(len(matrices) == gl_formula, f"q={q}: independently enumerated GL size")
    expected = {1: 2, 2: 24, 3: 1344}[q]
    require(len(found) == expected, f"q={q}: actual Cayley graph size")
    require(len(found) == len(matrices) * (1 << q), f"q={q}: affine-state factorization")

    states = tuple(sorted(found))
    indices = {state: index for index, state in enumerate(states)}
    transitions = tuple(tuple(indices[step(state, gate)] for gate in gates) for state in states)
    for i, row in enumerate(transitions):
        for gate_index, successor in enumerate(row):
            require(transitions[successor][gate_index] == i, "every literal generator is involutive")
    require(target in indices, f"q={q}: target is present")
    return {
        "q": q,
        "gates": gates,
        "states": states,
        "transitions": transitions,
        "start": indices[start],
        "target": indices[target],
        "gl_size": len(matrices),
    }


def shortest_cost(graph: dict[str, object], weights: tuple[int, ...]) -> int:
    transitions = graph["transitions"]
    require(len(weights) == len(graph["gates"]), "one independent tariff per generator")
    require(all(type(weight) is int and weight > 0 for weight in weights), "positive exact tariffs")
    # A simple path costs at most max(weights)*(number of states-1).
    unreachable = max(weights) * len(transitions) + 1
    distances = [unreachable] * len(transitions)
    start = graph["start"]
    distances[start] = 0
    queue = [(0, start)]
    settled = 0
    while queue:
        distance, vertex = heapq.heappop(queue)
        if distance != distances[vertex]:
            continue
        settled += 1
        for gate_index, successor in enumerate(transitions[vertex]):
            candidate = distance + weights[gate_index]
            if candidate < distances[successor]:
                distances[successor] = candidate
                heapq.heappush(queue, (candidate, successor))
    require(settled == len(transitions), "Dijkstra settled the full finite state graph")
    require(all(distance < unreachable for distance in distances), "all states have finite exact distance")
    return distances[graph["target"]]


def is_rooted_forest(parents: tuple[int | None, ...]) -> bool:
    if not any(parent is None for parent in parents):
        return False
    for vertex in range(len(parents)):
        visited = set()
        current = vertex
        while parents[current] is not None:
            if current in visited:
                return False
            visited.add(current)
            current = parents[current]
    return True


def all_forests(q: int) -> tuple[tuple[int | None, ...], ...]:
    choices = tuple(tuple([None] + [j for j in range(q) if i != j]) for i in range(q))
    forests = tuple(parents for parents in itertools.product(*choices) if is_rooted_forest(parents))
    require(len(forests) == (q + 1) ** (q - 1), f"q={q}: independently enumerated rooted forest count")
    return forests


def split_prices(q: int, gates: tuple[tuple[int, ...], ...], weights: tuple[int, ...]) -> tuple[tuple[int, ...], dict[tuple[int, int], int]]:
    oracle = tuple(weights[i] for i in range(q))
    edges = {gate[1:]: weights[k] for k, gate in enumerate(gates) if gate[0] == 1}
    return oracle, edges


def forest_bill(parents: tuple[int | None, ...], oracle: tuple[int, ...], edges: dict[tuple[int, int], int]) -> int:
    # This evaluation is also used on one deliberately invalid cycle control.
    return sum(oracle[i] if parent is None else 2 * edges[i, parent] for i, parent in enumerate(parents))


def forest_echo(parents: tuple[int | None, ...]) -> tuple[tuple[int, ...], ...]:
    require(is_rooted_forest(parents), "echo requires a genuine rooted forest")
    depths = []
    for vertex in range(len(parents)):
        depth, current = 0, vertex
        while parents[current] is not None:
            depth += 1
            current = parents[current]
        depths.append(depth)
    destinations = sorted((i for i, parent in enumerate(parents) if parent is not None), key=lambda i: (-depths[i], i))
    preparation = tuple((1, i, parents[i]) for i in destinations)
    roots = tuple((0, i) for i, parent in enumerate(parents) if parent is None)
    return preparation + roots + tuple(reversed(preparation))


def best_forest(forests: tuple[tuple[int | None, ...], ...], oracle: tuple[int, ...], edges: dict[tuple[int, int], int]) -> int:
    return min(forest_bill(parents, oracle, edges) for parents in forests)


def weights_from_prices(graph: dict[str, object], oracle: tuple[int, ...], edges: dict[tuple[int, int], int]) -> tuple[int, ...]:
    return tuple(oracle[gate[1]] if gate[0] == 0 else edges[gate[1], gate[2]] for gate in graph["gates"])


def defect_controls(graph: dict[str, object], forests: tuple[tuple[int | None, ...], ...]) -> dict[str, object]:
    q = 3
    identity = (1, 2, 4)
    target = (9, 10, 12)
    dirt_mask = 7

    one_wave = evaluate(q, ((0, 0), (1, 1, 0), (1, 2, 0)))
    one_wave_common = tuple((row >> q) & 1 for row in one_wave)
    one_wave_dirt = tuple(row & dirt_mask for row in one_wave)
    require(one_wave_common == (1, 1, 1), "one-wave defect preserves the desired common map")
    require(one_wave_dirt != identity and one_wave != target, "one-wave defect is rejected for unrestored dirt")

    wrong_order = evaluate(q, ((1, 1, 0), (1, 2, 1), (0, 0), (1, 2, 1), (1, 1, 0)))
    wrong_common = tuple((row >> q) & 1 for row in wrong_order)
    require(tuple(row & dirt_mask for row in wrong_order) == identity, "wrong-order defect restores dirt")
    require(wrong_common == (1, 1, 0) and wrong_order != target, "wrong-order defect misses the deepest product")

    oracle = (1, 100, 100)
    chain_prices = {(i, j): 100 for i in range(q) for j in range(q) if i != j}
    chain_prices[1, 0] = 1
    chain_prices[2, 1] = 1
    exact = shortest_cost(graph, weights_from_prices(graph, oracle, chain_prices))
    forest = best_forest(forests, oracle, chain_prices)
    single_root_stars = tuple(
        parents for parents in forests
        if sum(parent is None for parent in parents) == 1
        and all(parent is None or parents[parent] is None for parent in parents)
    )
    multiple_root_height_one = tuple(
        parents for parents in forests
        if sum(parent is None for parent in parents) >= 2
        and all(parent is None or parents[parent] is None for parent in parents)
    )
    star = best_forest(single_root_stars, oracle, chain_prices)
    height_one = best_forest(multiple_root_height_one, oracle, chain_prices)
    direct = sum(oracle)
    require((exact, forest, star, height_one, direct) == (5, 5, 203, 103, 201), "directed chain and charged comparator optima")
    correct_word = forest_echo((None, 0, 1))
    require(evaluate(q, correct_word) == target, "directed chain echo is an exact full affine map")

    reversed_prices = {(i, j): chain_prices[j, i] for i, j in chain_prices}
    wrong_direction_cost = best_forest(forests, oracle, reversed_prices)
    wrong_direction_dijkstra = shortest_cost(graph, weights_from_prices(graph, oracle, reversed_prices))
    require(wrong_direction_cost == wrong_direction_dijkstra == 103, "reversed lookup solves the wrong model")
    require(wrong_direction_cost != exact, "directed-cost lookup defect changes the certified answer")

    cycle_prices = {(i, j): 100 for i in range(q) for j in range(q) if i != j}
    cycle_prices[1, 2] = 1
    cycle_prices[2, 1] = 1
    fake = (None, 2, 1)
    require(not is_rooted_forest(fake), "a disconnected directed cycle must be rejected")
    fake_bill = forest_bill(fake, oracle, cycle_prices)
    cycle_exact = shortest_cost(graph, weights_from_prices(graph, oracle, cycle_prices))
    cycle_forest = best_forest(forests, oracle, cycle_prices)
    require((fake_bill, cycle_exact, cycle_forest) == (5, 103, 103), "cycle relaxation produces a false strict saving")

    return {
        "one_wave_unrestored_dirt": {
            "detected": True, "common_coefficients": one_wave_common,
            "dirt_rows": one_wave_dirt, "full_affine_rows": one_wave,
        },
        "wrong_tree_order": {
            "detected": True, "common_coefficients": wrong_common,
            "dirt_rows": identity, "full_affine_rows": wrong_order,
        },
        "directed_chain": {
            "unrestricted_optimum": exact, "forest_optimum": forest,
            "best_single_root_star": star, "best_multi_root_height_one": height_one,
            "all_direct": direct, "echo_word": correct_word,
        },
        "reversed_directed_cost_lookup": {
            "detected": True, "correct_optimum": exact,
            "incorrect_transposed_optimum": wrong_direction_cost,
        },
        "cycle_accepted_as_forest": {
            "detected": True, "invalid_parent_function": fake,
            "incorrect_relaxed_bill": fake_bill,
            "genuine_forest_optimum": cycle_forest, "unrestricted_optimum": cycle_exact,
        },
    }


def audit() -> dict[str, object]:
    domains = []
    all_case_rows = []
    graphs = {}
    forest_sets = {}
    total_echoes = 0
    for q in (1, 2, 3):
        graph = full_graph(q)
        forests = all_forests(q)
        graphs[q] = graph
        forest_sets[q] = forests
        target = tuple((1 << i) | (1 << q) for i in range(q))
        for parents in forests:
            word = forest_echo(parents)
            require(evaluate(q, word) == target, f"q={q}: complete forest echo")
            multiplicities = Counter(word)
            for vertex, parent in enumerate(parents):
                if parent is None:
                    require(multiplicities[(0, vertex)] == 1, "each root uses exactly one common call")
                else:
                    require(multiplicities[(1, vertex, parent)] == 2, "each directed forest edge is paid twice")
            total_echoes += 1

        cases = []
        strictly_below_direct = 0
        sharing_optimum_possible = 0
        mixed_roots_possible = 0
        mixed_roots_required = 0
        tariff_axes = tuple((1, 7) if gate[0] == 0 else (1, 3) for gate in graph["gates"])
        for weights in itertools.product(*tariff_axes):
            oracle, edges = split_prices(q, graph["gates"], weights)
            unrestricted = shortest_cost(graph, weights)
            candidate = best_forest(forests, oracle, edges)
            require(unrestricted == candidate, f"q={q}, prices={weights}: unrestricted optimum differs from forest")
            optimal_root_counts = {
                sum(parent is None for parent in parents)
                for parents in forests
                if forest_bill(parents, oracle, edges) == candidate
            }
            strictly_below_direct += unrestricted < sum(oracle)
            sharing_optimum_possible += any(roots < q for roots in optimal_root_counts)
            mixed_roots_possible += any(1 < roots < q for roots in optimal_root_counts)
            mixed_roots_required += all(1 < roots < q for roots in optimal_root_counts)
            cases.append((weights, unrestricted, candidate))
            all_case_rows.append((q, weights, unrestricted, candidate))
        expected_cases = {1: 2, 2: 16, 3: 512}[q]
        require(len(cases) == expected_cases, f"q={q}: complete independent price cube")
        if q >= 2:
            require(strictly_below_direct > 0, f"q={q}: tariff cube actually exercises sharing")
        if q == 3:
            require(mixed_roots_required > 0, "tariff cube actually forces some mixed-root optima")
        domains.append({
            "q": q, "linear_group_size": graph["gl_size"],
            "affine_states": len(graph["states"]), "generators": len(graph["gates"]),
            "directed_transition_occurrences": len(graph["states"]) * len(graph["gates"]),
            "state_set_sha256": fingerprint(graph["states"]),
            "generator_order": graph["gates"],
            "valid_rooted_forests": len(forests),
            "forests_by_root_count": dict(sorted(Counter(sum(parent is None for parent in parents) for parents in forests).items())),
            "price_assignments": len(cases),
            "oracle_price_values": [1, 7], "directed_ADD_price_values": [1, 3],
            "cases_strictly_below_all_direct": strictly_below_direct,
            "cases_with_shared_optimal_forest": sharing_optimum_possible,
            "cases_with_mixed_root_optimal_forest": mixed_roots_possible,
            "cases_requiring_mixed_roots": mixed_roots_required,
            "optimum_histogram": dict(sorted(Counter(row[1] for row in cases).items())),
            "complete_case_result_sha256": fingerprint(cases),
            "all_unrestricted_optima_equal_forest_optima": True,
        })
    require(len(all_case_rows) == 530, "all 530 independent complete-tariff assignments checked")
    require(total_echoes == 20, "all 20 enumerated forest echoes checked")
    controls = defect_controls(graphs[3], forest_sets[3])
    return {
        "status": "pass",
        "proof_level": "exact finite exhaustive coefficient-state audit; not formal-kernel or human verification",
        "q_domain": [1, 2, 3],
        "width_scope": "coefficient maps act coordinatewise for every w>=1 within the stated exact XOR alphabet",
        "complete_tariff_assignments_checked": len(all_case_rows),
        "oracle_price_values": [1, 7],
        "directed_ADD_price_values": [1, 3],
        "cases_strictly_below_all_direct": sum(domain["cases_strictly_below_all_direct"] for domain in domains),
        "cases_with_shared_optimal_forest": sum(domain["cases_with_shared_optimal_forest"] for domain in domains),
        "cases_with_mixed_root_optimal_forest": sum(domain["cases_with_mixed_root_optimal_forest"] for domain in domains),
        "cases_requiring_mixed_roots": sum(domain["cases_requiring_mixed_roots"] for domain in domains),
        "complete_case_result_sha256": fingerprint(all_case_rows),
        "forest_echoes_checked": total_echoes,
        "private_oracle_exhaustion": False,
        "physical_tariff_binding": False,
        "new_kappa": False,
        "domains": domains,
        "defect_controls": controls,
        "independent_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create this absent file with the same deterministic JSON as stdout")
    arguments = parser.parse_args()
    record = audit()
    rendered = json.dumps(record, sort_keys=True, indent=2) + "\n"
    if arguments.output is not None:
        with arguments.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
