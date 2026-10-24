"""Exact finite evidence for unit-ring dirty fanout.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable is imported. Scientific checks survive -O.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
from dataclasses import dataclass
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Ring:
    name: str
    one: int
    add: tuple[tuple[int, ...], ...]
    mul: tuple[tuple[int, ...], ...]
    neg: tuple[int, ...]
    inv: tuple[int, ...]


def finish_ring(name: str, one: int, add: tuple, mul: tuple) -> Ring:
    size = len(add)
    neg = tuple(next(b for b in range(size) if add[a][b] == 0) for a in range(size))
    inv = tuple(
        next((b for b in range(size) if mul[a][b] == one and mul[b][a] == one), -1)
        for a in range(size)
    )
    return Ring(name, one, add, mul, neg, inv)


def cyclic_ring(modulus: int) -> Ring:
    require(2 <= modulus <= 6, "modulus outside fixed verification domain")
    add = tuple(
        tuple((a + b) % modulus for b in range(modulus)) for a in range(modulus)
    )
    mul = tuple(tuple(a * b % modulus for b in range(modulus)) for a in range(modulus))
    return finish_ring(f"Z/{modulus}", 1, add, mul)


def matrix_ring() -> Ring:
    """Encode a 2-by-2 binary matrix in row-major bit order."""
    add = tuple(tuple(a ^ b for b in range(16)) for a in range(16))
    rows = []
    for a in range(16):
        row = []
        for b in range(16):
            value = 0
            for i, j in itertools.product(range(2), repeat=2):
                bit = 0
                for k in range(2):
                    bit ^= ((a >> (2 * i + k)) & 1) & ((b >> (2 * k + j)) & 1)
                value |= bit << (2 * i + j)
            row.append(value)
        rows.append(tuple(row))
    return finish_ring("M2(F2)", 9, add, tuple(rows))


def endpoint(ring: Ring, demand: tuple[int, ...]) -> tuple[int, ...]:
    q = len(demand)
    require(1 <= q <= 5, "row count outside verification domain")
    return tuple(
        ring.one if j == i else demand[i] if j == q else 0
        for i in range(q)
        for j in range(q + 1)
    )


def apply_gate(ring: Ring, state: tuple, gate: tuple, q: int) -> tuple:
    i, j, coefficient = gate
    result = list(state)
    if j == -1:
        index = i * (q + 1) + q
        result[index] = ring.add[result[index]][coefficient]
    else:
        for k in range(q + 1):
            index = i * (q + 1) + k
            value = ring.mul[coefficient][state[j * (q + 1) + k]]
            result[index] = ring.add[result[index]][value]
    return tuple(result)


def forest_depths(parents: tuple[int, ...]) -> tuple[int, ...] | None:
    q = len(parents)
    depths = []
    for start in range(q):
        vertex = start
        for depth in range(q):
            if parents[vertex] == -1:
                depths.append(depth)
                break
            vertex = parents[vertex]
        else:
            return None
    return tuple(depths)


def forests(q: int) -> tuple[tuple[int, ...], ...]:
    require(1 <= q <= 5, "forest bound exceeded")
    choices = [tuple(j for j in range(-1, q) if j != i) for i in range(q)]
    return tuple(p for p in itertools.product(*choices) if forest_depths(p) is not None)


def forest_word(ring: Ring, parents: tuple, demand: tuple) -> tuple:
    require(len(parents) == len(demand), "inconsistent word dimensions")
    require(
        all(0 <= a < len(ring.inv) and ring.inv[a] >= 0 for a in demand),
        "every target coefficient must be a unit",
    )
    depths = forest_depths(parents)
    require(depths is not None, "parent relation contains a cycle")
    order = sorted(range(len(parents)), key=lambda i: (-depths[i], i))
    preparation = tuple(
        (i, parents[i], ring.neg[ring.mul[demand[i]][ring.inv[demand[parents[i]]]]])
        for i in order
        if parents[i] >= 0
    )
    calls = tuple((i, -1, demand[i]) for i in order if parents[i] == -1)
    restoration = tuple((i, j, ring.neg[a]) for i, j, a in reversed(preparation))
    return preparation + calls + restoration


def execute(ring: Ring, q: int, word: tuple) -> tuple:
    state = endpoint(ring, (0,) * q)
    for gate in word:
        state = apply_gate(ring, state, gate, q)
    return state


def check_words(ring: Ring) -> dict:
    units = tuple(a for a, inverse in enumerate(ring.inv) if inverse >= 0)
    count = 0
    digest = hashlib.sha256()
    for q in range(1, 6):
        demands = {
            tuple(units[(i + shift) % len(units)] for i in range(q))
            for shift in range(len(units))
        }
        for parents, demand in itertools.product(forests(q), sorted(demands)):
            word = forest_word(ring, parents, demand)
            value = execute(ring, q, word)
            require(value == endpoint(ring, demand), "arbitrary-dirt endpoint failed")
            inverse = tuple((i, j, ring.neg[a]) for i, j, a in reversed(word))
            for gate in inverse:
                value = apply_gate(ring, value, gate, q)
            require(value == endpoint(ring, (0,) * q), "literal inverse failed")
            digest.update(bytes(execute(ring, q, word)))
            count += 1
    return {"ring": ring.name, "words": count, "endpoint_sha256": digest.hexdigest()}


def modular_distances(modulus: int, prices: tuple[int, ...]) -> dict:
    """Independent full affine-state shortest paths, always exactly two rows."""
    start = (1, 0, 0, 0, 1, 0)
    distances = {start: 0}
    heap = [(0, start)]
    gates = tuple(
        (i, j, a, prices[k])
        for k, (i, j) in enumerate(((0, -1), (1, -1), (0, 1), (1, 0)))
        for a in range(1, modulus)
    )
    capacity = modulus**6
    for _ in range(capacity * len(gates) + 1):
        if not heap:
            return distances
        cost, state = heapq.heappop(heap)
        if distances[state] != cost:
            continue
        for i, j, a, price in gates:
            changed = list(state)
            if j == -1:
                changed[3 * i + 2] = (changed[3 * i + 2] + a) % modulus
            else:
                for k in range(3):
                    changed[3 * i + k] = (
                        state[3 * i + k] + a * state[3 * j + k]
                    ) % modulus
            target = tuple(changed)
            new_cost = cost + price
            if new_cost < distances.get(target, 10**9):
                distances[target] = new_cost
                require(len(distances) <= capacity, "state-capacity bound violated")
                heapq.heappush(heap, (new_cost, target))
    raise ValueError("bounded shortest-path queue failed to exhaust")


def check_shortest_paths() -> dict:
    comparisons = 0
    states = 0
    histogram: dict[str, int] = {}
    for modulus in (3, 4, 6):
        ring = cyclic_ring(modulus)
        units = tuple(a for a, inverse in enumerate(ring.inv) if inverse >= 0)
        for prices in itertools.product((1, 4), repeat=4):
            distances = modular_distances(modulus, prices)
            states += len(distances)
            mu0, mu1, c01, c10 = prices
            expected = min(mu0 + mu1, mu0 + 2 * c10, mu1 + 2 * c01)
            for a, b in itertools.product(units, repeat=2):
                require(
                    distances[(1, 0, a, 0, 1, b)] == expected,
                    "unrestricted ring shortest path beats/misses forest price",
                )
                comparisons += 1
            histogram[f"{modulus}:{','.join(map(str, prices))}"] = len(distances)
    return {
        "tariff_instances": len(histogram),
        "unit_demand_comparisons": comparisons,
        "affine_states_across_instances": states,
        "state_counts": histogram,
    }


def check_boundaries() -> dict:
    ring = matrix_ring()
    units = tuple(a for a, inverse in enumerate(ring.inv) if inverse >= 0)
    order_witness = None
    for parent, child in itertools.product(units, repeat=2):
        right = ring.mul[child][ring.inv[parent]]
        wrong = ring.mul[ring.inv[parent]][child]
        if right != wrong:
            order_witness = (parent, child, right, wrong)
            break
    require(order_witness is not None, "matrix-ring fixture must be noncommutative")
    parent, child, right, wrong = order_witness
    word = forest_word(ring, (-1, 0), (parent, child))
    mutant = tuple((i, j, wrong) if j >= 0 else (i, j, a) for i, j, a in word)
    require(
        execute(ring, 2, mutant) != endpoint(ring, (parent, child)),
        "reversed coefficient-order control failed",
    )
    require(
        execute(ring, 2, word[:-1]) != endpoint(ring, (parent, child)),
        "missing dirt-restoration control failed",
    )
    z4 = cyclic_ring(4)
    distances = modular_distances(4, (1, 9, 1, 1))
    nonunit_cost = distances[(1, 0, 2, 0, 1, 1)]
    require(nonunit_cost == 4, "nonunit boundary must distinguish the formula value 3")
    try:
        forest_word(z4, (-1, 0), (2, 1))
    except ValueError as error:
        require("unit" in str(error), "nonunit rejected for wrong reason")
    else:
        raise ValueError("nonunit demands were accepted")
    require(forest_depths((1, 0)) is None, "cycle must not be a forest")
    first = forest_word(z4, (-1, 0, 1), (3, 1, 3))
    require(execute(z4, 3, first) == endpoint(z4, (3, 1, 3)), "first fixture failed")
    return {
        "noncommuting_units": [parent, child],
        "correct_ratio": right,
        "incorrect_ratio": wrong,
        "nonunit_Z4_cost": nonunit_cost,
        "inapplicable_forest_value": 3,
        "first_Z4_chain_gates": len(first),
        "control_groups": 5,
    }


def reconstruct() -> dict:
    return {
        "claim_type": "scoped proof with exact finite corroboration",
        "new_kappa": False,
        "words": [check_words(cyclic_ring(m)) for m in (3, 4, 6)]
        + [check_words(matrix_ring())],
        "shortest_paths": check_shortest_paths(),
        "boundaries": check_boundaries(),
    }


def bound_hashes() -> dict[str, str]:
    base = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    return {
        name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in names
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create an absent external receipt")
    args = parser.parse_args()
    receipt = {
        "schema_version": 1,
        "file_sha256": bound_hashes(),
        "result": reconstruct(),
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as handle:
            require(handle.write(encoded) == len(encoded), "short receipt write")
    else:
        stored = Path(__file__).with_name("RESULT.json").read_text(encoding="utf-8")
        require(stored == encoded, "source-bound canonical receipt differs")
    print("PASS_UNIT_RING_DIRTY_FANOUT")
    print(json.dumps(receipt["result"], sort_keys=True))


if __name__ == "__main__":
    main()
