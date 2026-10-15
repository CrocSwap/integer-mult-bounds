#!/usr/bin/env python3
"""Exact depth-three search in the full formal group algebra F2[A5]."""

from __future__ import annotations

import hashlib
import json
import argparse
from pathlib import Path

IDENTITY_PERMUTATION = (0, 1, 2, 3, 4)
X = (1, 0, 3, 2, 4)  # (12)(34)
Y = (2, 1, 4, 3, 0)  # (135)
MAX_CALLS = 3


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Return a after b, the standard right-to-left permutation composition."""
    return tuple(a[b[i]] for i in range(5))


def make_group():
    seen = {IDENTITY_PERMUTATION}
    frontier = [IDENTITY_PERMUTATION]
    while frontier:
        current = frontier.pop()
        for generator in (X, Y):
            successor = compose(current, generator)
            if successor not in seen:
                seen.add(successor)
                frontier.append(successor)
    elements = sorted(seen)
    index = {element: i for i, element in enumerate(elements)}
    table = [[index[compose(a, b)] for b in elements] for a in elements]
    return elements, index, table


def multiply_binary(a: tuple[int, ...], b: tuple[int, ...], roles: int):
    return tuple(
        sum(a[row * roles + k] * b[k * roles + col] for k in range(roles)) & 1
        for row in range(roles)
        for col in range(roles)
    )


def rank_one_idempotents(roles: int):
    result = []
    for code in range(1 << (roles * roles)):
        matrix = tuple((code >> bit) & 1 for bit in range(roles * roles))
        nonzero_rows = []
        for row in range(roles):
            encoded = sum(matrix[row * roles + col] << col for col in range(roles))
            if encoded:
                nonzero_rows.append(encoded)
        if not nonzero_rows or len(set(nonzero_rows)) != 1:
            continue
        if multiply_binary(matrix, matrix, roles) == matrix:
            result.append((code, matrix))
    return result


def translate_right(poly: int, group_element: int, table: list[list[int]]) -> int:
    """Right-multiply a group-algebra coefficient mask by one group element."""
    result = 0
    remaining = poly
    while remaining:
        bit = remaining & -remaining
        left_element = bit.bit_length() - 1
        result ^= 1 << table[left_element][group_element]
        remaining ^= bit
    return result


def multiply_by_factor(
    state: tuple[int, ...],
    factor: tuple[str, int, int, tuple[int, ...]],
    roles: int,
    table: list[list[int]],
):
    label_index, projector = factor[1], factor[3]
    q_products = [
        state[i] ^ translate_right(state[i], label_index, table)
        for i in range(roles * roles)
    ]
    result = list(state)
    for row in range(roles):
        for col in range(roles):
            entry = state[row * roles + col]
            for inner in range(roles):
                if projector[inner * roles + col]:
                    entry ^= q_products[row * roles + inner]
            result[row * roles + col] = entry
    return tuple(result)


def canonical_state(state: tuple[int, ...]) -> str:
    return ",".join(f"{entry:015x}" for entry in state)


def sha256_lines(lines) -> str:
    return hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()


def order_of(element: int, identity: int, table: list[list[int]]) -> int:
    value = identity
    for power in range(1, 61):
        value = table[value][element]
        if value == identity:
            return power
    raise ValueError("element order exceeds group order")


def run_search(roles: int, xy_index: int, yx_index: int, x_index: int, y_index: int,
               identity_index: int, table: list[list[int]]):
    projectors = rank_one_idempotents(roles)
    factors = [
        (label, label_index, code, projector)
        for label, label_index in (("x", x_index), ("y", y_index))
        for code, projector in projectors
    ]
    identity_state = tuple(
        (1 << identity_index) if row == col else 0
        for row in range(roles)
        for col in range(roles)
    )
    target = tuple(
        (1 << (xy_index if row == 0 else yx_index)) if row == col and row < 2
        else ((1 << identity_index) if row == col else 0)
        for row in range(roles)
        for col in range(roles)
    )
    states_by_depth = [set() for _ in range(MAX_CALLS + 1)]
    states_by_depth[0].add(identity_state)
    raw_words_by_depth = [0] * (MAX_CALLS + 1)
    hits = []

    def walk(state, path, depth):
        if depth == MAX_CALLS:
            return
        for factor_index, factor in enumerate(factors):
            successor = multiply_by_factor(state, factor, roles, table)
            next_path = path + (factor_index,)
            next_depth = depth + 1
            raw_words_by_depth[next_depth] += 1
            states_by_depth[next_depth].add(successor)
            if successor == target:
                hits.append(list(next_path))
            walk(successor, next_path, next_depth)

    walk(identity_state, (), 0)

    code_e11 = 1 << 0
    code_e22 = 1 << (roles + 1)
    direct_word = [["x", "E11"], ["y", "E11"], ["y", "E22"], ["x", "E22"]]
    factor_indices = []
    for label, code in (("x", code_e11), ("y", code_e11),
                        ("y", code_e22), ("x", code_e22)):
        factor_indices.append(next(
            i for i, (factor_label, _g, factor_code, _n) in enumerate(factors)
            if factor_label == label and factor_code == code
        ))
    direct_state = identity_state
    for factor_index in factor_indices:
        direct_state = multiply_by_factor(direct_state, factors[factor_index], roles, table)

    hashes = [
        sha256_lines(sorted(canonical_state(state) for state in layer))
        for layer in states_by_depth
    ]
    return {
        "registers": roles,
        "input_contract": "all scalar registers arbitrary and dirty; every register has the stated exact diagonal endpoint",
        "projector_count": len(projectors),
        "paid_factor_types": len(factors),
        "projectors": [{"code": code, "entries": list(matrix)} for code, matrix in projectors],
        "target": "diag([xy],[yx])" if roles == 2 else "diag([xy],[yx],[e])",
        "direct_paid_calls": len(direct_word),
        "direct_word": direct_word,
        "direct_exact": direct_state == target,
        "search_max_calls": MAX_CALLS,
        "raw_words_by_depth": raw_words_by_depth,
        "distinct_states_by_depth": [len(layer) for layer in states_by_depth],
        "state_layer_sha256": hashes,
        "three_call_hits": hits,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare exact output with CERTIFICATE.json")
    parser.add_argument("--write", action="store_true", help="write deterministic CERTIFICATE.json")
    args = parser.parse_args()
    if args.check and args.write:
        parser.error("choose only one of --check and --write")
    elements, index, table = make_group()
    identity = index[IDENTITY_PERMUTATION]
    x_index, y_index = index[X], index[Y]
    xy_index, yx_index = table[x_index][y_index], table[y_index][x_index]
    if len(elements) != 60:
        raise SystemExit("the generated group is not A5")
    if order_of(x_index, identity, table) != 2:
        raise SystemExit("x order control failed")
    if order_of(y_index, identity, table) != 3:
        raise SystemExit("y order control failed")
    if order_of(xy_index, identity, table) != 5 or order_of(yx_index, identity, table) != 5:
        raise SystemExit("5-cycle order control failed")
    y_inverse = next(i for i in range(len(elements)) if table[y_index][i] == identity)
    if table[table[y_index][xy_index]][y_inverse] != yx_index:
        raise SystemExit("conjugacy relation control failed")

    group_lines = ["".join(map(str, element)) for element in elements]
    searches = [
        run_search(roles, xy_index, yx_index, x_index, y_index, identity, table)
        for roles in (2, 3)
    ]
    if [row["projector_count"] for row in searches] != [6, 28]:
        raise SystemExit("rank-one idempotent census mismatch")
    if [sum(row["raw_words_by_depth"]) for row in searches] != [1884, 178808]:
        raise SystemExit("raw word count mismatch")
    if not all(row["direct_exact"] for row in searches):
        raise SystemExit("direct positive control failed")

    certificate = {
        "status": "SEARCH_COMPLETE",
        "group": "A5=<x,y | x^2=y^3=(xy)^5=e>",
        "generators": {"x": list(X), "y": list(Y)},
        "group_order": len(elements),
        "group_elements_sha256": sha256_lines(group_lines),
        "relations": {
            "x_order": 2,
            "y_order": 3,
            "xy_order": 5,
            "yx_order": 5,
            "yx_is_y_xy_y_inverse": True,
        },
        "paid_factor_definition": "D_N(g)=I+([g]+[e])N over the full formal group algebra F2[A5]",
        "all_rank_one_binary_idempotents_allowed": True,
        "searches": searches,
        "supplier_mapping": "not established; no kappa claim",
    }
    serialized = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    certificate_path = Path(__file__).with_name("CERTIFICATE.json")
    if args.write:
        certificate_path.write_text(serialized, encoding="utf-8")
        print("WROTE_A5_CONJUGATE_5CYCLE_CERTIFICATE")
    elif args.check:
        expected = json.loads(certificate_path.read_text(encoding="utf-8"))
        if expected != certificate:
            raise SystemExit("search output differs from CERTIFICATE.json")
        print("PASS_A5_BITSET_SEARCH r2_words=1884 r3_words=178808 target_hits=0")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
