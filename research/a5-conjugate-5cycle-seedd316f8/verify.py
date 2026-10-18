#!/usr/bin/env python3
"""Independent tuple/set replay of the complete A5 depth-three search."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
X = (1, 0, 3, 2, 4)
Y = (2, 1, 4, 3, 0)
E = (0, 1, 2, 3, 4)


def compose(a, b):
    return tuple(a[b[i]] for i in range(5))


def even_permutation(p):
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return inversions % 2 == 0


def generated_group():
    elements = sorted(p for p in itertools.permutations(range(5)) if even_permutation(p))
    index = {p: i for i, p in enumerate(elements)}
    table = [[index[compose(a, b)] for b in elements] for a in elements]
    return elements, index, table


def order(element, index, table):
    identity = index[E]
    value = identity
    for power in range(1, 61):
        value = table[value][index[element]]
        if value == identity:
            return power
    raise AssertionError("unexpected element order")


def rank_one_idempotents_by_uv(roles):
    """Enumerate N=u v^T with v^T u=1, independently of matrix squaring."""
    result = []
    for u in range(1, 1 << roles):
        for v in range(1, 1 << roles):
            if ((u & v).bit_count() & 1) != 1:
                continue
            matrix = tuple(
                ((u >> row) & 1) & ((v >> col) & 1)
                for row in range(roles)
                for col in range(roles)
            )
            result.append(matrix)
    assert len(set(result)) == (6 if roles == 2 else 28)
    return sorted(set(result))


def translate_right(poly, g, table):
    return frozenset(table[h][g] for h in poly)


def step(state, factor, roles, table):
    _label, g, projector = factor
    q_products = [
        state[i].symmetric_difference(translate_right(state[i], g, table))
        for i in range(roles * roles)
    ]
    result = list(state)
    for row in range(roles):
        for col in range(roles):
            entry = set(state[row * roles + col])
            for inner in range(roles):
                if projector[inner * roles + col]:
                    entry.symmetric_difference_update(q_products[row * roles + inner])
            result[row * roles + col] = frozenset(entry)
    return tuple(result)


def idempotent_from_code(code, roles):
    return tuple((code >> bit) & 1 for bit in range(roles * roles))


def state_mask(state):
    return tuple(sum(1 << g for g in entry) for entry in state)


def canonical(mask_state):
    return ",".join(f"{entry:015x}" for entry in mask_state)


def sha256_lines(lines):
    return hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()


def run_role_search(roles, group_index, table, xy, yx, identity, expected):
    projectors = rank_one_idempotents_by_uv(roles)
    factors = []
    for label, g in (("x", group_index[X]), ("y", group_index[Y])):
        for projector in projectors:
            factors.append((label, g, projector))

    initial = tuple(
        frozenset((identity,)) if row == col else frozenset()
        for row in range(roles)
        for col in range(roles)
    )
    target = tuple(
        frozenset((xy if row == 0 else yx,)) if row == col and row < 2
        else (frozenset((identity,)) if row == col else frozenset())
        for row in range(roles)
        for col in range(roles)
    )

    frontier = [initial]
    distinct = [{initial}]
    raw_by_depth = [0]
    hits = 0
    for depth in range(1, 4):
        next_frontier = []
        layer = set()
        for state in frontier:
            for factor in factors:
                successor = step(state, factor, roles, table)
                if successor == target:
                    hits += 1
                layer.add(successor)
                if depth < 3:
                    next_frontier.append(successor)
        raw_by_depth.append(len(frontier) * len(factors))
        distinct.append(layer)
        frontier = next_frontier

    masks = [
        sorted(canonical(state_mask(state)) for state in layer)
        for layer in distinct
    ]
    hashes = [sha256_lines(layer) for layer in masks]

    e11 = idempotent_from_code(1, roles)
    e22 = idempotent_from_code(1 << (roles + 1), roles)
    direct_spec = [("x", e11), ("y", e11), ("y", e22), ("x", e22)]
    label_index = {"x": group_index[X], "y": group_index[Y]}
    direct_factors = [(label, label_index[label], projector)
                      for label, projector in direct_spec]
    direct_state = initial
    for factor in direct_factors:
        direct_state = step(direct_state, factor, roles, table)

    # Four deletion and four label-switch controls are exact formal products.
    omission_controls = []
    for omitted in range(4):
        state = initial
        for i, factor in enumerate(direct_factors):
            if i != omitted:
                state = step(state, factor, roles, table)
        omission_controls.append(state != target)
    label_controls = []
    for switched in range(4):
        state = initial
        for i, (label, projector) in enumerate(direct_spec):
            changed = ("y" if label == "x" else "x") if i == switched else label
            state = step(state, (changed, label_index[changed], projector), roles, table)
        label_controls.append(state != target)

    expected_rows = [r for r in expected["searches"] if r["registers"] == roles]
    assert len(expected_rows) == 1
    expected_row = expected_rows[0]
    assert len(projectors) == expected_row["projector_count"]
    assert set(projectors) == {
        tuple(item["entries"]) for item in expected_row["projectors"]
    }
    assert len(factors) == expected_row["paid_factor_types"]
    assert raw_by_depth == expected_row["raw_words_by_depth"]
    assert [len(layer) for layer in distinct] == expected_row["distinct_states_by_depth"]
    assert hashes == expected_row["state_layer_sha256"]
    assert hits == 0 and expected_row["three_call_hits"] == []
    assert direct_state == target and expected_row["direct_exact"]
    assert all(omission_controls) and all(label_controls)

    return {
        "registers": roles,
        "factors": len(factors),
        "raw_words": sum(raw_by_depth),
        "distinct_states": [len(layer) for layer in distinct],
        "target_hits": hits,
        "direct_positive_control": True,
        "omission_controls": sum(omission_controls),
        "label_switch_controls": sum(label_controls),
    }


def main():
    elements, group_index, table = generated_group()
    assert len(elements) == 60 and all(even_permutation(p) for p in elements)
    assert order(X, group_index, table) == 2
    assert order(Y, group_index, table) == 3
    identity = group_index[E]
    x, y = group_index[X], group_index[Y]
    xy, yx = table[x][y], table[y][x]
    assert order(elements[xy], group_index, table) == 5
    assert order(elements[yx], group_index, table) == 5
    y_inv = next(i for i in range(60) if table[y][i] == identity)
    assert table[table[y][xy]][y_inv] == yx

    expected = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
    assert expected["group_order"] == 60
    assert expected["relations"]["yx_is_y_xy_y_inverse"] is True
    assert expected["group_elements_sha256"] == sha256_lines(
        "".join(map(str, p)) for p in elements
    )
    results = [
        run_role_search(roles, group_index, table, xy, yx, identity, expected)
        for roles in (2, 3)
    ]
    assert expected["supplier_mapping"] == "not established; no kappa claim"
    print(
        "PASS_A5_CONJUGATE_5CYCLE_BOUND "
        + " ".join(
            f"r{r['registers']}={r['raw_words']}words/{r['target_hits']}hits"
            for r in results
        )
        + " direct_calls=4 controls="
        + str(sum(r["omission_controls"] + r["label_switch_controls"] for r in results))
        + " exact_full_group_algebra=1 no_kappa"
    )


if __name__ == "__main__":
    main()
