"""Exact shortest-path oracle for two-row dirty fanout over Z/qZ.

This module intentionally implements the finite state graph directly. It does
not import a tariff formula or any other project code.

Rows are flattened as ``(a00, a01, p0, a10, a11, p1)``. An ``add`` edge
performs one elementary row operation; a ``source`` edge changes exactly one
row's coefficient of the distinguished source ``p``. Every nonzero residue
is an available coefficient, including the additive inverse of every gate
coefficient. Positive edge prices make Dijkstra's algorithm exact. The search
has no depth bound: it expands complete legal outgoing transitions from each
settled state and stops only after all q^2 pure-translation targets settle.

Attribution: "Krzysztof Wójt with substantial OpenAI Codex assistance"
License: Apache-2.0
"""

from __future__ import annotations

import heapq
import time
from typing import Tuple, Union


State = Tuple[int, int, int, int, int, int]
Action = Union[Tuple[str, int, int], Tuple[str, int, int, int]]
Demand = Tuple[int, int]

_START: State = (1, 0, 0, 0, 1, 0)


def _validate_inputs(
    modulus: int,
    source_prices: tuple[int, int],
    add_prices: tuple[int, int],
    include_paths: bool,
) -> None:
    if type(modulus) is not int:
        raise TypeError("modulus must be an int (bool is not accepted)")
    if modulus < 2:
        raise ValueError("modulus must be at least 2")
    if type(source_prices) is not tuple or len(source_prices) != 2:
        raise TypeError("source_prices must be a 2-tuple of positive ints")
    if type(add_prices) is not tuple or len(add_prices) != 2:
        raise TypeError("add_prices must be a 2-tuple of positive ints")
    for name, prices in (("source_prices", source_prices), ("add_prices", add_prices)):
        for price in prices:
            if type(price) is not int:
                raise TypeError(f"{name} entries must be ints (bool is not accepted)")
            if price <= 0:
                raise ValueError(f"{name} entries must be positive")
    if type(include_paths) is not bool:
        raise TypeError("include_paths must be bool")


def _apply_action(state: State, action: Action, modulus: int) -> State:
    """Apply one already validated operation, returning a fresh exact state."""
    kind = action[0]
    if kind == "source":
        _, dst, beta = action
        offset = 3 * dst + 2
        result = list(state)
        result[offset] = (result[offset] + beta) % modulus
        return tuple(result)  # type: ignore[return-value]

    _, dst, src, alpha = action
    dst_offset = 3 * dst
    src_offset = 3 * src
    result = list(state)
    for column in range(3):
        result[dst_offset + column] = (
            state[dst_offset + column] + alpha * state[src_offset + column]
        ) % modulus
    return tuple(result)  # type: ignore[return-value]


def _operation_price(
    action: Action,
    source_prices: tuple[int, int],
    add_prices: tuple[int, int],
) -> int:
    if action[0] == "source":
        return source_prices[action[1]]
    return add_prices[action[1]]


def _target_state(demand: Demand) -> State:
    return (1, 0, demand[0], 0, 1, demand[1])


def _replay_path(
    modulus: int,
    source_prices: tuple[int, int],
    add_prices: tuple[int, int],
    path: tuple[Action, ...],
) -> tuple[State, int]:
    """Independently replay a returned operation sequence and sum its prices."""
    state = _START
    total = 0
    for action in path:
        if not isinstance(action, tuple) or not action:
            raise AssertionError("path contains a malformed action")
        if action[0] == "source":
            if len(action) != 3:
                raise AssertionError("source action must be ('source', dst, beta)")
            _, dst, beta = action
            if type(dst) is not int or dst not in (0, 1):
                raise AssertionError("source destination must be row 0 or 1")
            if type(beta) is not int or beta % modulus == 0:
                raise AssertionError("source coefficient must be nonzero modulo q")
            normalized: Action = ("source", dst, beta % modulus)
        elif action[0] == "add":
            if len(action) != 4:
                raise AssertionError("add action must be ('add', dst, src, alpha)")
            _, dst, src, alpha = action
            if (
                type(dst) is not int
                or type(src) is not int
                or dst not in (0, 1)
                or src not in (0, 1)
                or dst == src
            ):
                raise AssertionError("add rows must be distinct members of {0, 1}")
            if type(alpha) is not int or alpha % modulus == 0:
                raise AssertionError("add coefficient must be nonzero modulo q")
            normalized = ("add", dst, src, alpha % modulus)
        else:
            raise AssertionError(f"unknown path action: {action[0]!r}")
        state = _apply_action(state, normalized, modulus)
        total += _operation_price(normalized, source_prices, add_prices)
    return state, total


def shortest_prices(
    modulus: int,
    source_prices: tuple[int, int],
    add_prices: tuple[int, int],
    *,
    include_paths: bool = False,
) -> dict[str, object]:
    """Return exact optimum prices for every translation demand pair.

    The finite graph has at most ``modulus**6`` row-coefficient states. A
    state is settled with its exact shortest distance; every available nonzero
    coefficient is considered for both source additions and both directed
    row additions. Since every supplied price is positive, ordinary Dijkstra
    is valid even when the modulus is composite and some nonzero coefficients
    are not units.

    ``costs`` maps ``(lambda0, lambda1)`` to its exact integer optimum. When
    ``include_paths`` is true, ``paths`` maps the same keys to operation tuples
    accepted by the internal exact replay checker.
    """
    _validate_inputs(modulus, source_prices, add_prices, include_paths)

    operations: list[tuple[Action, int]] = []
    for dst in (0, 1):
        for beta in range(1, modulus):
            action: Action = ("source", dst, beta)
            operations.append((action, source_prices[dst]))
        src = 1 - dst
        for alpha in range(1, modulus):
            action = ("add", dst, src, alpha)
            operations.append((action, add_prices[dst]))

    target_demands: tuple[Demand, ...] = tuple(
        (lambda0, lambda1)
        for lambda0 in range(modulus)
        for lambda1 in range(modulus)
    )
    target_by_state = {_target_state(demand): demand for demand in target_demands}
    remaining = set(target_demands)

    distances: dict[State, int] = {_START: 0}
    predecessors: dict[State, tuple[State, Action]] | None = (
        {} if include_paths else None
    )
    settled: set[State] = set()
    settled_costs: dict[Demand, int] = {}
    heap: list[tuple[int, State]] = [(0, _START)]

    transition_scans = 0
    successful_relaxations = 0
    heap_pushes = 1
    stale_heap_pops = 0
    started = time.perf_counter()

    while remaining:
        distance, state = heapq.heappop(heap)
        if distance != distances.get(state):
            stale_heap_pops += 1
            continue
        if state in settled:
            stale_heap_pops += 1
            continue
        settled.add(state)

        demand = target_by_state.get(state)
        if demand is not None and demand in remaining:
            settled_costs[demand] = distance
            remaining.remove(demand)

        # Expanding every settled state's complete operation list means the
        # search has no depth or branch cap. We stop after all target distances
        # are final; states beyond the largest settled target distance cannot
        # improve any requested answer.
        for action, edge_price in operations:
            transition_scans += 1
            successor = _apply_action(state, action, modulus)
            candidate = distance + edge_price
            previous = distances.get(successor)
            if previous is None or candidate < previous:
                distances[successor] = candidate
                if predecessors is not None:
                    predecessors[successor] = (state, action)
                heapq.heappush(heap, (candidate, successor))
                successful_relaxations += 1
                heap_pushes += 1

    elapsed = time.perf_counter() - started
    result: dict[str, object] = {
        "modulus": modulus,
        "costs": {demand: settled_costs[demand] for demand in target_demands},
        "stats": {
            "target_count": len(target_demands),
            "settled_targets": len(settled_costs),
            "settled_states": len(settled),
            "discovered_states": len(distances),
            "transition_scans": transition_scans,
            "successful_relaxations": successful_relaxations,
            "heap_pushes": heap_pushes,
            "stale_heap_pops": stale_heap_pops,
            "max_target_cost": max(settled_costs.values()),
            "elapsed_seconds": elapsed,
        },
    }

    if include_paths:
        if predecessors is None:
            raise RuntimeError("path predecessors were not recorded")
        paths: dict[Demand, tuple[Action, ...]] = {}
        for demand in target_demands:
            state = _target_state(demand)
            reversed_path: list[Action] = []
            while state != _START:
                previous, action = predecessors[state]
                reversed_path.append(action)
                state = previous
            paths[demand] = tuple(reversed(reversed_path))
        result["paths"] = paths

    return result


def _self_test() -> None:
    # With q=2 and ADD prices well above every direct-source route, the direct
    # one-operation-per-nonzero-demand construction is a positive control.
    # A route that transfers a source coefficient between rows requires at
    # least two expensive ADDs to restore both first-two-column coefficients.
    control = shortest_prices(2, (1, 2), (100, 100), include_paths=True)
    expected = {(0, 0): 0, (1, 0): 1, (0, 1): 2, (1, 1): 3}
    if control["costs"] != expected:
        raise AssertionError(
            f"q=2 direct-cost control failed: {control['costs']!r} != {expected!r}"
        )
    control_paths = control["paths"]
    if not isinstance(control_paths, dict):
        raise AssertionError("q=2 control did not return paths")
    for demand, expected_cost in expected.items():
        final_state, replayed_cost = _replay_path(
            2, (1, 2), (100, 100), control_paths[demand]
        )
        if final_state != _target_state(demand):
            raise AssertionError(f"q=2 path missed target {demand}: {final_state!r}")
        if replayed_cost != expected_cost:
            raise AssertionError(
                f"q=2 path for {demand} costs {replayed_cost}, expected {expected_cost}"
            )

    composite = shortest_prices(4, (25, 26), (1, 1), include_paths=True)
    composite_costs = composite["costs"]
    composite_paths = composite["paths"]
    if not isinstance(composite_costs, dict) or not isinstance(composite_paths, dict):
        raise AssertionError("q=4 composite control did not return costs and paths")
    for demand, path in composite_paths.items():
        final_state, replayed_cost = _replay_path(4, (25, 26), (1, 1), path)
        if final_state != _target_state(demand):
            raise AssertionError(f"q=4 path missed target {demand}: {final_state!r}")
        if replayed_cost != composite_costs[demand]:
            raise AssertionError(
                f"q=4 path for {demand} costs {replayed_cost}, "
                f"expected {composite_costs[demand]}"
            )

    summaries = [
        (2, (1, 2), (100, 100)),
        (3, (25, 26), (1, 1)),
        (4, (25, 26), (1, 1)),
        (5, (25, 26), (1, 1)),
    ]
    print("positive control q=2 direct costs and path replay: PASS")
    print("composite q=4 all-demand path replay: PASS")
    for modulus, source_prices, add_prices in summaries:
        result = shortest_prices(modulus, source_prices, add_prices)
        costs = result["costs"]
        stats = result["stats"]
        if not isinstance(costs, dict) or len(costs) != modulus**2:
            raise AssertionError(
                f"q={modulus} returned {len(costs) if isinstance(costs, dict) else 'no'} "
                f"demand costs; expected {modulus**2}"
            )
        if not isinstance(stats, dict):
            raise AssertionError(f"q={modulus} did not return search statistics")
        print(
            f"q={modulus}: targets={stats['settled_targets']}, "
            f"settled={stats['settled_states']}, "
            f"discovered={stats['discovered_states']}, "
            f"scans={stats['transition_scans']}, "
            f"max_cost={stats['max_target_cost']}, "
            f"time={stats['elapsed_seconds']:.3f}s"
        )

    for bad_args in (
        (True, (1, 1), (1, 1)),
        (1, (1, 1), (1, 1)),
        (2, (True, 1), (1, 1)),
        (2, (1, 1), (0, 1)),
    ):
        try:
            shortest_prices(*bad_args)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid inputs were accepted: {bad_args!r}")
    print("input validation controls: PASS")


if __name__ == "__main__":
    _self_test()
