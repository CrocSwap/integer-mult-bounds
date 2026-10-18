#!/usr/bin/env python3
"""Replay the finite Dic_3 search and exercise exact positive/negative controls."""

from __future__ import annotations

import json
from pathlib import Path

import search


ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_DIC3: " + message)


def check_group() -> None:
    table = search.GROUP_TABLE
    u, v = search.GENERATORS
    powers = [0]
    for _ in range(6):
        powers.append(table[powers[-1]][u])
    require(powers[-1] == 0 and all(p != 0 for p in powers[1:6]) and
            len(set(powers[:6])) == 6, "u must have exact order six")
    u3 = table[table[u][u]][u]
    require(table[v][v] == u3, "v^2 must equal u^3")
    vinv = search.GROUP_INVERSE[v]
    conjugate = table[table[v][u]][vinv]
    require(conjugate == search.GROUP_INVERSE[u],
            "vuv^-1 must equal u^-1")
    for g, labels in search.SHORTEST_WORD.items():
        value = 0
        for label in labels:
            value = table[value][search.GENERATORS[0 if label == "u" else 1]]
        require(value == g and len(labels) == search.DIST[g],
                "positive-generator distance certificate is invalid")
    for a in range(search.N_GROUP):
        for b in range(search.N_GROUP):
            for c in range(search.N_GROUP):
                require(table[table[a][b]][c] == table[a][table[b][c]],
                        "group table is not associative")


def check_idempotents_and_paid_alphabet() -> None:
    require(len(search.PROJECTORS) == 28, "wrong idempotent count")
    for n in search.PROJECTORS:
        square = tuple(sum(n[3 * i + k] * n[3 * k + j] for k in range(3)) & 1
                       for i in range(3) for j in range(3))
        require(square == n, "enumerated frame is not idempotent")
        rows = [sum(n[3 * i + j] << j for j in range(3)) for i in range(3)]
        rank = 0
        for col in range(3):
            pivot = next((r for r in range(rank, 3) if (rows[r] >> col) & 1), None)
            if pivot is None:
                continue
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            for r in range(3):
                if r != rank and ((rows[r] >> col) & 1):
                    rows[r] ^= rows[rank]
            rank += 1
        require(rank == 1, "enumerated idempotent is not rank one")
    require(len(search.OPS) == 56, "paid alphabet must have 2 * 28 operations")
    for op, inv in zip(search.OP_MATS, search.OP_INVS):
        require(search.mat_mul(op, inv) == search.IDENTITY and
                search.mat_mul(inv, op) == search.IDENTITY,
                "algebraic inverse used by the exact join is incorrect")


def coordinate_projector(i: int) -> tuple[int, ...]:
    return tuple(1 if r == i and c == i else 0
                 for r in range(3) for c in range(3))


def direct_coordinate_word(target: tuple[int, int, int]) -> tuple[int, ...]:
    out = []
    for coordinate, g in enumerate(target):
        label_word = search.SHORTEST_WORD[g]
        proj = coordinate_projector(coordinate)
        for label in label_word:
            out.append(search.OP_INDEX[(label, proj)])
    return tuple(out)


def check_positive_and_negative_controls() -> None:
    # A direct paid call is a positive fixture for the model and endpoint convention.
    u, v = search.GENERATORS
    p0 = coordinate_projector(0)
    iu = search.OP_INDEX[("u", p0)]
    iv = search.OP_INDEX[("v", p0)]
    require(search.word_product((iu,)) == search.target_matrix((u, 0, 0)),
            "one-call positive fixture failed")

    # Directly routed calls reproduce a heterogeneous monomial endpoint.
    direct_target = (u, v, 0)
    direct_word = direct_coordinate_word(direct_target)
    require(len(direct_word) == sum(search.DIST[g] for g in direct_target),
            "coordinate baseline does not match shortest positive generator bills")
    require(search.word_product(direct_word) == search.target_matrix(direct_target),
            "separate coordinate implementation failed")

    # Order and endpoint mutations are meaningful negative controls.
    uv = search.GROUP_TABLE[u][v]
    vu = search.GROUP_TABLE[v][u]
    require(uv != vu, "the chosen generators must not commute")
    ordered = search.word_product((iu, iv))
    require(ordered == search.target_matrix((uv, 0, 0)),
            "ordered two-call fixture failed")
    require(ordered != search.target_matrix((vu, 0, 0)),
            "reversed group product was not rejected")
    require(ordered != search.target_matrix((uv, v, 0)),
            "mutated target endpoint was not rejected")


def check_pair_census() -> int:
    # An explicit raw 0/1/2-word census independently confirms the state-set
    # quotient used by the search before its depth-four and depth-five joins.
    observed = {search.IDENTITY}
    for left in search.OP_MATS:
        observed.add(left)
        for right in search.OP_MATS:
            observed.add(search.mat_mul(left, right))
    generated, _ = search.all_products(2)
    require(observed == set(generated), "pair-product census disagrees with raw words")
    return len(observed)


def check_triple_census() -> int:
    # Raw 56^3 ordered words provide an independent coverage check for the
    # shortest-state transition table used as the depth-three suffix inventory.
    observed = {search.IDENTITY}
    for first in search.OP_MATS:
        observed.add(first)
        for second in search.OP_MATS:
            pair = search.mat_mul(first, second)
            observed.add(pair)
            for third in search.OP_MATS:
                observed.add(search.mat_mul(pair, third))
    generated, _ = search.all_products(3)
    require(observed == set(generated), "triple-product census disagrees with raw words")
    return len(observed)


def main() -> None:
    check_group()
    check_idempotents_and_paid_alphabet()
    check_positive_and_negative_controls()
    pair_states = check_pair_census()

    expected = json.loads((ROOT / "EXPECTED.json").read_text())
    actual = search.search()
    triple_states = check_triple_census()
    require(actual == expected, "complete search result differs from EXPECTED.json")
    require(actual["depth_four_stage"]["endpoint_count"] == 1482,
            "depth-four endpoint layer changed")
    require(actual["depth_four_stage"]["eligible_targets_with_word"] == 0,
            "depth-four stage must record its full no-hit result")
    require(actual["depth_five_pivot"]["endpoint_count"] == 1230,
            "depth-five endpoint layer changed")
    require(actual["depth_five_pivot"]["eligible_targets_with_word"] == 0,
            "depth-five stage must record its full no-hit result")

    print("PASS_DIC3_BOUNDED_DIAGONAL_SEARCH "
          f"ops={len(search.OPS)} pair_states={pair_states} triple_states={triple_states} "
          f"depth4_endpoints={actual['depth_four_stage']['endpoint_count']} "
          f"depth5_endpoints={actual['depth_five_pivot']['endpoint_count']} "
          f"depth4_hits=0 depth5_hits=0 "
          f"coverage4={actual['depth_four_stage']['coverage_sha256']} "
          f"coverage5={actual['depth_five_pivot']['coverage_sha256']}")


if __name__ == "__main__":
    main()
