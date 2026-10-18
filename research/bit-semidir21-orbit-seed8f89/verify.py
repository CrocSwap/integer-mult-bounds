#!/usr/bin/env python3
"""Exact paid-word search in F2[C7 semidirect C3] on three registers."""
from __future__ import annotations

import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path


K = 3
IDENTITY = (0, 0)
GROUP = tuple((i, j) for i in range(7) for j in range(3))
GROUP_INDEX = {g: i for i, g in enumerate(GROUP)}
ID = GROUP_INDEX[IDENTITY]
BASIS_E = 1 << ID


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def mul_group(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    """(a^i b^j)(a^k b^l)=a^(i+2^j k)b^(j+l)."""
    i, j = x
    k, ell = y
    return ((i + pow(2, j, 7) * k) % 7, (j + ell) % 3)


GROUP_MUL = tuple(
    tuple(GROUP_INDEX[mul_group(x, y)] for y in GROUP) for x in GROUP
)


@lru_cache(maxsize=None)
def mul_algebra(x: int, y: int) -> int:
    """Multiply two F2[G] elements encoded as 21-bit coefficient masks."""
    out = 0
    left = x
    while left:
        li_bit = left & -left
        i = li_bit.bit_length() - 1
        right = y
        while right:
            rj_bit = right & -right
            j = rj_bit.bit_length() - 1
            out ^= 1 << GROUP_MUL[i][j]
            right ^= rj_bit
        left ^= li_bit
    return out


def bitvec(mask: int) -> tuple[int, ...]:
    return tuple((mask >> i) & 1 for i in range(K))


def idempotents():
    """All 28 rank-one N=xy^T over F2 with y^T x=1."""
    out = []
    for x in range(1, 1 << K):
        for y in range(1, 1 << K):
            if ((x & y).bit_count() & 1) == 0:
                continue
            xb, yb = bitvec(x), bitvec(y)
            n = tuple(xb[i] & yb[j] for i in range(K) for j in range(K))
            out.append((n, x, y))
    return tuple(out)


IDEMPOTENTS = idempotents()
MATRIX_ID = tuple(BASIS_E if i == j else 0 for i in range(K) for j in range(K))


def paid_call(g_index: int, n: tuple[int, ...]):
    """I + ([g]+[e])N over F2[G], with g != e."""
    g_mask = 1 << g_index
    delta = g_mask ^ BASIS_E
    return tuple(
        (BASIS_E if i == j else 0) ^ (delta if n[i * K + j] else 0)
        for i in range(K)
        for j in range(K)
    )


def matmul(a: tuple[int, ...], b: tuple[int, ...]):
    out = []
    for i in range(K):
        for j in range(K):
            value = 0
            for k in range(K):
                value ^= mul_algebra(a[i * K + k], b[k * K + j])
            out.append(value)
    return tuple(out)


def diagonal(g_indices: tuple[int, ...]):
    return tuple(
        (1 << g_indices[i]) if i == j and g_indices[i] is not None
        else (BASIS_E if i == j and g_indices[i] is None else 0)
        for i in range(K)
        for j in range(K)
    )


def render_call(call):
    g_index, n, x, y, matrix = call
    return {
        "address": list(GROUP[g_index]),
        "x_mask": x,
        "y_mask": y,
        "idempotent_rows": [list(n[i * K : (i + 1) * K]) for i in range(K)],
    }


def make_calls():
    calls = []
    for g_index, g in enumerate(GROUP):
        if g == IDENTITY:
            continue
        for n, x, y in IDEMPOTENTS:
            calls.append((g_index, n, x, y, paid_call(g_index, n)))
    return tuple(calls)


def canonical_state(state: tuple[int, ...]) -> bytes:
    return b"".join(value.to_bytes(3, "little") for value in state)


def search_length_two(target: tuple[int, ...], calls):
    witnesses = []
    digest = hashlib.sha256()
    distinct = set()
    pair_count = 0
    for first in calls:
        for second in calls:
            state = matmul(first[4], second[4])
            pair_count += 1
            digest.update(canonical_state(state))
            distinct.add(state)
            if state == target:
                witnesses.append((first, second))
    return {
        "pairs": pair_count,
        "distinct_products": len(distinct),
        "ordered_pair_stream_sha256": digest.hexdigest(),
        "witnesses": witnesses,
    }


def find_length_one(target, calls):
    return [call for call in calls if call[4] == target]


def validate_group_and_alphabet(calls):
    require(len(GROUP) == 21 and len(set(GROUP)) == 21, "wrong group order")
    for x in range(len(GROUP)):
        require(GROUP_MUL[ID][x] == x and GROUP_MUL[x][ID] == x,
                "group identity check failed")
        require(len(set(GROUP_MUL[x])) == len(GROUP), "left multiplication is not bijective")
        require(any(GROUP_MUL[x][y] == ID and GROUP_MUL[y][x] == ID
                    for y in range(len(GROUP))), "group inverse missing")
        for y in range(len(GROUP)):
            for z in range(len(GROUP)):
                require(GROUP_MUL[GROUP_MUL[x][y]][z]
                        == GROUP_MUL[x][GROUP_MUL[y][z]], "group table is not associative")
    require(GROUP_MUL[GROUP_INDEX[(0, 1)]][GROUP_INDEX[(1, 0)]]
            != GROUP_MUL[GROUP_INDEX[(1, 0)]][GROUP_INDEX[(0, 1)]],
            "the address group is unexpectedly abelian")
    a = GROUP_INDEX[(1, 0)]
    b = GROUP_INDEX[(0, 1)]
    binv = GROUP_INDEX[(0, 2)]
    a2 = GROUP_INDEX[(2, 0)]
    a4 = GROUP_INDEX[(4, 0)]
    require(GROUP_MUL[a][a] == a2 and GROUP_MUL[a2][a2] == a4,
            "rotation powers are wrong")
    require(GROUP_MUL[GROUP_MUL[b][a]][binv] == a2,
            "b a b^-1 is not a^2")
    require(GROUP_MUL[GROUP_MUL[binv][a]][b] == a4,
            "b^2 a b^-2 is not a^4")
    require(len(IDEMPOTENTS) == 28, "wrong rank-one idempotent count")
    require(len(calls) == 560, "wrong complete paid-call alphabet size")
    for n, x, y in IDEMPOTENTS:
        require(x != 0 and y != 0 and (x & y).bit_count() % 2 == 1,
                "idempotent parameter condition failed")
        # Verify N^2=N over F2.
        for i in range(K):
            for j in range(K):
                value = 0
                for k in range(K):
                    value ^= n[i * K + k] & n[k * K + j]
                require(value == n[i * K + j], "N^2 != N")


def main():
    calls = make_calls()
    validate_group_and_alphabet(calls)
    a = GROUP_INDEX[(1, 0)]
    a2 = GROUP_INDEX[(2, 0)]
    a4 = GROUP_INDEX[(4, 0)]
    target = diagonal((a, a2, a4))

    # Direct three-call witness, using one coordinate idempotent per target.
    e_calls = []
    for register, g in enumerate((a, a2, a4)):
        n = tuple(int(i == register and j == register) for i in range(K) for j in range(K))
        e_calls.append(paid_call(g, n))
    direct = matmul(matmul(e_calls[0], e_calls[1]), e_calls[2])
    require(direct == target, "direct three-call witness failed")

    # The no-call and one-call controls are exact.
    require(MATRIX_ID != target, "target unexpectedly equals the identity")
    one_call = find_length_one(target, calls)

    # Positive search control: a target with only two nonidentity outputs is
    # reachable by two coordinate calls and must be found in the full alphabet.
    control = diagonal((a, a2, None))
    control_result = search_length_two(control, calls)
    require(control_result["pairs"] == 560 * 560, "control search coverage mismatch")
    require(bool(control_result["witnesses"]), "two-call positive control was missed")

    result = search_length_two(target, calls)
    require(result["pairs"] == 560 * 560, "target search did not cover every ordered pair")
    expected_path = "witness" if result["witnesses"] else "excluded-through-two"
    expected = json.loads(Path(__file__).with_name("EXPECTED.json").read_text())
    require(expected["two_call_status"] == expected_path, "two-call status differs from EXPECTED")
    require(expected["target_ordered_pairs"] == result["pairs"], "ordered-pair count differs")
    require(expected["distinct_target_products"] == result["distinct_products"],
            "distinct product count differs")
    require(expected["ordered_pair_stream_sha256"] == result["ordered_pair_stream_sha256"],
            "ordered-pair stream digest differs")
    require(expected["length_one_witnesses"] == len(one_call), "length-one count differs")
    require(expected["positive_control_witnesses"] == len(control_result["witnesses"]),
            "positive-control witness count differs")
    if result["witnesses"]:
        witness = result["witnesses"][0]
        require(matmul(witness[0][4], witness[1][4]) == target, "reported witness fails")
        rendered = [render_call(witness[0]), render_call(witness[1])]
        require(expected["witness"] == rendered, "witness differs from EXPECTED")
    else:
        require(expected["witness"] is None, "unexpected expected witness")

    print(
        f"PASS_SEMIDIRECT21_THREE_REGISTER target={expected_path} "
        f"calls={len(calls)} ordered_pairs={result['pairs']} "
        f"distinct_products={result['distinct_products']} "
        f"length1={len(one_call)} direct_calls=3 "
        f"control_witnesses={len(control_result['witnesses'])} "
        f"pair_stream_sha256={result['ordered_pair_stream_sha256']}"
    )


if __name__ == "__main__":
    main()
