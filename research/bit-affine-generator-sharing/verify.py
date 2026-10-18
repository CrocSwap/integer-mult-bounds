#!/usr/bin/env python3
"""Exact radius-seven search in F2[AGL_2(F2)] for two affine targets."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ID_MATRIX = 0b1001
IDENTITY_AFFINE = (ID_MATRIX, 0)
GENERATORS = {
    "a": (0b1011, 0),  # x0 <- x0 + x1
    "b": (0b1101, 0),  # x1 <- x1 + x0
    "u": (ID_MATRIX, 0b01),  # x0 <- x0 + 1
    "v": (ID_MATRIX, 0b10),  # x1 <- x1 + 1
}
TARGET = (0b0110, 0b10)  # h(x0,x1) = (x1, x0+1)
MUTATED_TARGET = (0b0110, 0b01)  # h'(x0,x1) = (x1+1, x0)
DIRECT_LABELS = b"abav"
DIRECT_MUTATED_LABELS = b"abau"


def matrix_product(a: int, b: int) -> int:
    """Multiply packed row-major 2x2 matrices over F2."""
    out = 0
    for i in range(2):
        for j in range(2):
            value = 0
            for k in range(2):
                value ^= ((a >> (2 * i + k)) & 1) & ((b >> (2 * k + j)) & 1)
            out |= value << (2 * i + j)
    return out


def matrix_rank(a: int) -> int:
    rows = [a & 0b11, (a >> 2) & 0b11]
    rank = 0
    for col in (1, 0):
        pivot = next((r for r in range(rank, 2) if (rows[r] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(2):
            if r != rank and ((rows[r] >> col) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def compose(g: tuple[int, int], h: tuple[int, int]) -> tuple[int, int]:
    """Return g after h for affine maps x -> A*x+b."""
    ag, bg = g
    ah, bh = h
    a = matrix_product(ag, ah)
    b = 0
    for i in range(2):
        value = (bg >> i) & 1
        for j in range(2):
            value ^= ((ag >> (2 * i + j)) & 1) & ((bh >> j) & 1)
        b |= value << i
    return a, b


def affine_elements() -> tuple[tuple[int, int], ...]:
    return tuple(
        (a, b)
        for a in range(16)
        if matrix_rank(a) == 2
        for b in range(4)
    )


GROUP = affine_elements()
GROUP_ID = {g: i for i, g in enumerate(GROUP)}
GROUP_PRODUCT = tuple(
    tuple(GROUP_ID[compose(g, h)] for h in GROUP) for g in GROUP
)
UNIT = GROUP_ID[IDENTITY_AFFINE]
TARGET_ID = GROUP_ID[TARGET]
MUTATED_TARGET_ID = GROUP_ID[MUTATED_TARGET]


def idempotents() -> tuple[int, ...]:
    found = []
    for n in range(16):
        if n and matrix_rank(n) == 1 and matrix_product(n, n) == n:
            found.append(n)
    return tuple(found)


IDEMPOTENTS = idempotents()
FACTORS = tuple(
    (label, GROUP_ID[GENERATORS[label]], n)
    for label in GENERATORS
    for n in IDEMPOTENTS
)
FACTOR_ID = {(label, n): i for i, (label, _, n) in enumerate(FACTORS)}


def make_shift_table(gid: int) -> tuple[tuple[int, ...], ...]:
    table = []
    for chunk in range(6):
        values = []
        for nibble in range(16):
            out = 0
            for offset in range(4):
                source = 4 * chunk + offset
                if source < len(GROUP) and ((nibble >> offset) & 1):
                    out |= 1 << GROUP_PRODUCT[gid][source]
            values.append(out)
        table.append(tuple(values))
    return tuple(table)


SHIFT_TABLES = {
    gid: make_shift_table(gid)
    for gid in {
        UNIT,
        TARGET_ID,
        MUTATED_TARGET_ID,
        *(GROUP_ID[g] for g in GENERATORS.values()),
    }
}


def shift_left(poly: int, gid: int) -> int:
    table = SHIFT_TABLES[gid]
    return (
        table[0][poly & 0xF]
        | table[1][(poly >> 4) & 0xF]
        | table[2][(poly >> 8) & 0xF]
        | table[3][(poly >> 12) & 0xF]
        | table[4][(poly >> 16) & 0xF]
        | table[5][(poly >> 20) & 0xF]
    )


IDENTITY_STATE = (1 << UNIT, 0, 0, 1 << UNIT)


def left_factor(state: tuple[int, int, int, int], factor_id: int) -> tuple[int, int, int, int]:
    """Compute D_N(g) * state exactly in M_2(F2[G])."""
    _, gid, n = FACTORS[factor_id]
    out = []
    for i in range(2):
        for j in range(2):
            mixed = 0
            for k in range(2):
                if (n >> (2 * i + k)) & 1:
                    mixed ^= state[2 * k + j]
            out.append(state[2 * i + j] ^ mixed ^ shift_left(mixed, gid))
    return tuple(out)  # type: ignore[return-value]


def replay(word: bytes) -> tuple[int, int, int, int]:
    state = IDENTITY_STATE
    for factor_id in word:
        state = left_factor(state, factor_id)
    return state


def word_for_labels(labels: bytes, n: int) -> bytes:
    return bytes(FACTOR_ID[(chr(label), n)] for label in labels)


DIRECT_WORD = word_for_labels(DIRECT_LABELS, 0b0001) + word_for_labels(
    DIRECT_LABELS, 0b1000
)
MUTATED_DIRECT_WORD = word_for_labels(DIRECT_MUTATED_LABELS, 0b0001) + word_for_labels(
    DIRECT_MUTATED_LABELS, 0b1000
)
PIVOT_DIRECT_WORD = word_for_labels(DIRECT_LABELS, 0b0001) + word_for_labels(
    DIRECT_MUTATED_LABELS, 0b1000
)


def diagonal_target(hid: int) -> tuple[int, int, int, int]:
    return (1 << hid, 0, 0, 1 << hid)


TARGET_STATE = diagonal_target(TARGET_ID)
MUTATED_TARGET_STATE = diagonal_target(MUTATED_TARGET_ID)
PIVOT_TARGETS = (TARGET_ID, MUTATED_TARGET_ID)
PIVOT_TARGET_STATE = (1 << TARGET_ID, 0, 0, 1 << MUTATED_TARGET_ID)
REVERSED_PIVOT_STATE = (1 << MUTATED_TARGET_ID, 0, 0, 1 << TARGET_ID)


def target_left_times(
    state: tuple[int, int, int, int], targets: tuple[int, int]
) -> tuple[int, int, int, int]:
    """Multiply diag([h0],[h1]) by state on the left."""
    return tuple(
        shift_left(state[2 * row + col], targets[row])
        for row in range(2)
        for col in range(2)
    )  # type: ignore[return-value]


def radius_ball(radius: int) -> dict[tuple[int, int, int, int], bytes]:
    """Shortest witness to every exact group-algebra state within radius."""
    seen = {IDENTITY_STATE: b""}
    frontier = [IDENTITY_STATE]
    for _ in range(radius):
        next_frontier = []
        for state in frontier:
            prefix = seen[state]
            for factor_id in range(len(FACTORS)):
                nxt = left_factor(state, factor_id)
                if nxt not in seen:
                    seen[nxt] = prefix + bytes((factor_id,))
                    next_frontier.append(nxt)
        frontier = next_frontier
    return seen


def state_digest(states: dict[tuple[int, int, int, int], bytes]) -> str:
    digest = hashlib.sha256()
    for state in sorted(states):
        digest.update(" ".join(f"{x:06x}" for x in state).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def factor_name(factor_id: int) -> str:
    label, _, n = FACTORS[factor_id]
    entries = "".join(str((n >> i) & 1) for i in range(4))
    return f"{label}:N={entries}"


def word_names(word: bytes) -> list[str]:
    return [factor_name(fid) for fid in word]


def displacement_rank(h: tuple[int, int]) -> int:
    a, b = h
    columns = []
    for j in range(2):
        columns.append(
            (((a >> j) & 1) ^ int(j == 0))
            | ((((a >> (2 + j)) & 1) ^ int(j == 1)) << 1)
        )
    columns.append(b)
    basis: list[int] = []
    for col in columns:
        x = col
        for y in basis:
            x = min(x, x ^ y)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def shortest_address_word(target: tuple[int, int]) -> tuple[int, bytes]:
    distances = {IDENTITY_AFFINE: (0, b"")}
    queue = deque([IDENTITY_AFFINE])
    labels = tuple(GENERATORS)
    while queue:
        current = queue.popleft()
        distance, word = distances[current]
        for label in labels:
            nxt = compose(GENERATORS[label], current)
            if nxt not in distances:
                distances[nxt] = (distance + 1, word + label.encode("ascii"))
                queue.append(nxt)
    return distances[target]


def exact_join(
    targets: tuple[int, int],
    left: dict[tuple[int, int, int, int], bytes],
    right: dict[tuple[int, int, int, int], bytes],
    radius_left: int = 3,
    radius_right: int = 4,
) -> tuple[dict, bytes | None]:
    best: bytes | None = None
    best_length: int | None = None
    for prefix_state, prefix_word in left.items():
        inverse_state = replay(prefix_word[::-1])
        needed_suffix = target_left_times(inverse_state, targets)
        suffix_word = right.get(needed_suffix)
        if suffix_word is None:
            continue
        candidate = prefix_word + suffix_word
        if best_length is None or (len(candidate), candidate) < (best_length, best):
            best = candidate
            best_length = len(candidate)
    details = {
        "left_radius": radius_left,
        "right_radius": radius_right,
        "left_states": len(left),
        "right_states": len(right),
        "left_state_sha256": state_digest(left),
        "right_state_sha256": state_digest(right),
        "left_states_examined": len(left),
        "endpoint_reachable_within_7": best is not None,
        "minimum_word_length_found": best_length,
    }
    return details, best


def build_certificate() -> tuple[dict, bytes | None]:
    if len(GROUP) != 24 or len(IDEMPOTENTS) != 6 or len(FACTORS) != 24:
        raise AssertionError("the declared AGL2 group/factor alphabet is incomplete")
    for g in (GROUP_ID[x] for x in GENERATORS.values()):
        if GROUP_PRODUCT[g][g] != UNIT:
            raise AssertionError("each paid address generator must be an involution")
    for n in IDEMPOTENTS:
        if matrix_product(n, n) != n or matrix_rank(n) != 1:
            raise AssertionError("bad rank-one idempotent enumeration")
    for g in range(len(GROUP)):
        if GROUP_PRODUCT[UNIT][g] != g or GROUP_PRODUCT[g][UNIT] != g:
            raise AssertionError("the affine group identity table is inconsistent")
        for h in range(len(GROUP)):
            for k in range(len(GROUP)):
                if GROUP_PRODUCT[GROUP_PRODUCT[g][h]][k] != GROUP_PRODUCT[g][GROUP_PRODUCT[h][k]]:
                    raise AssertionError("the affine multiplication table is not associative")
    for factor_id in range(len(FACTORS)):
        if left_factor(left_factor(IDENTITY_STATE, factor_id), factor_id) != IDENTITY_STATE:
            raise AssertionError("a paid factor is not a formal involution")

    direct_distance, direct_address_word = shortest_address_word(TARGET)
    mutated_distance, mutated_address_word = shortest_address_word(MUTATED_TARGET)
    target_rank = displacement_rank(TARGET)
    if direct_distance != 4 or direct_address_word != b"abav":
        raise AssertionError("the pinned target direct-distance calculation changed")
    if mutated_distance != 4 or mutated_address_word != b"abau":
        raise AssertionError("the changed-target direct-distance control changed")
    if target_rank != 2 or displacement_rank(MUTATED_TARGET) != 2:
        raise AssertionError("the displacement-rank accounting changed")
    if replay(DIRECT_WORD) != TARGET_STATE:
        raise AssertionError("the eight-call direct positive control failed")
    if replay(MUTATED_DIRECT_WORD) != MUTATED_TARGET_STATE:
        raise AssertionError("the changed-target direct control failed")
    if TARGET_STATE == MUTATED_TARGET_STATE or replay(DIRECT_WORD) == MUTATED_TARGET_STATE:
        raise AssertionError("the changed-target negative control failed")
    for i in range(len(DIRECT_WORD)):
        if replay(DIRECT_WORD[:i] + DIRECT_WORD[i + 1 :]) == TARGET_STATE:
            raise AssertionError(f"omitting direct call {i} unexpectedly preserves the endpoint")

    if compose(TARGET, MUTATED_TARGET) != IDENTITY_AFFINE:
        raise AssertionError("the pivot target is not the inverse affine map")
    if compose(MUTATED_TARGET, TARGET) != IDENTITY_AFFINE:
        raise AssertionError("the pivot target is not a two-sided inverse")
    if replay(PIVOT_DIRECT_WORD) != PIVOT_TARGET_STATE:
        raise AssertionError("the eight-call inverse-pair control failed")
    if replay(PIVOT_DIRECT_WORD) == REVERSED_PIVOT_STATE:
        raise AssertionError("the target-order mutation was not distinguished")
    for i in range(len(PIVOT_DIRECT_WORD)):
        if replay(PIVOT_DIRECT_WORD[:i] + PIVOT_DIRECT_WORD[i + 1 :]) == PIVOT_TARGET_STATE:
            raise AssertionError(f"omitting pivot direct call {i} preserves the endpoint")

    left = radius_ball(3)
    right = radius_ball(4)
    same_join, same_witness = exact_join((TARGET_ID, TARGET_ID), left, right)
    pivot_join, pivot_witness = exact_join(PIVOT_TARGETS, left, right)
    if same_witness is not None and replay(same_witness) != TARGET_STATE:
        raise AssertionError("the same-target short witness failed full formal replay")
    if pivot_witness is not None and replay(pivot_witness) != PIVOT_TARGET_STATE:
        raise AssertionError("the inverse-pair short witness failed full formal replay")
    for target_state, witness in (
        (TARGET_STATE, same_witness),
        (PIVOT_TARGET_STATE, pivot_witness),
    ):
        if witness is not None:
            for i in range(len(witness)):
                if replay(witness[:i] + witness[i + 1 :]) == target_state:
                    raise AssertionError("a returned short witness was not minimal")
    if (
        same_join["left_state_sha256"] != pivot_join["left_state_sha256"]
        or same_join["right_state_sha256"] != pivot_join["right_state_sha256"]
    ):
        raise AssertionError("the shared exhaustive state sets changed between endpoints")

    result = {
        "schema_version": 1,
        "model": {
            "address_group": "AGL_2(F_2)",
            "formal_ring": "F_2[AGL_2(F_2)]",
            "registers": 2,
            "workspace": "none",
            "free_scalar_mixing": "GL_2(F_2), normalized into the six paid idempotents by augmentation",
            "paid_labels": {
                label: {"matrix_row_major": f"{g[0]:04b}", "translation": f"{g[1]:02b}"}
                for label, g in GENERATORS.items()
            },
            "calls_per_label_per_idempotent": 1,
            "rank_one_idempotents": [f"{n:04b}" for n in IDEMPOTENTS],
            "paid_factor_count": len(FACTORS),
            "factor": "D_N(g)=I+([g]+[1])N",
        },
        "first_endpoint": {
            "map_per_target": "h(x0,x1)=(x1,x0+1)",
            "formal_endpoint": "diag([h],[h])",
            "direct_word_per_target": direct_address_word.decode("ascii"),
            "direct_calls_total": 2 * direct_distance,
            "rank_floor": 2 * target_rank,
            "search": same_join,
            "short_witness": None
            if same_witness is None
            else {"length": len(same_witness), "factors": word_names(same_witness)},
            "minimum": 8 if same_witness is None else len(same_witness),
        },
        "pivot_endpoint": {
            "maps": [
                "h(x0,x1)=(x1,x0+1)",
                "h_inverse(x0,x1)=(x1+1,x0)",
            ],
            "formal_endpoint": "diag([h],[h_inverse])",
            "direct_words": [
                direct_address_word.decode("ascii"),
                mutated_address_word.decode("ascii"),
            ],
            "direct_calls_total": direct_distance + mutated_distance,
            "rank_floor": target_rank + displacement_rank(MUTATED_TARGET),
            "search": pivot_join,
            "short_witness": None
            if pivot_witness is None
            else {"length": len(pivot_witness), "factors": word_names(pivot_witness)},
            "minimum": 8 if pivot_witness is None else len(pivot_witness),
        },
        "direct_controls": {
            "same_target_word": word_names(DIRECT_WORD),
            "inverse_pair_word": word_names(PIVOT_DIRECT_WORD),
            "all_8_single_call_omissions_rejected": True,
            "changed_target_and_target_order_rejected": True,
        },
        "conclusion": (
            "both fixed two-register endpoints require 8 calls"
            if same_witness is None and pivot_witness is None
            else "bounded exact minima recorded for both endpoints"
        ),
        "controls": {
            "all_24_formal_group_elements_enumerated": len(GROUP) == 24,
            "all_6_rank_one_idempotents_enumerated": len(IDEMPOTENTS) == 6,
            "all_24_paid_factors_included": len(FACTORS) == 24,
            "direct_formal_endpoint_passes": True,
            "omitted_call_mutations_rejected": True,
            "changed_affine_target_mutation_rejected": True,
            "inverse_target_pair_verified": True,
            "two_endpoints_share_identical_complete_state_balls": True,
        },
    }
    return result, pivot_witness


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="write the deterministically recomputed certificate during development",
    )
    args = parser.parse_args()
    actual, witness = build_certificate()
    path = ROOT / "CERTIFICATE.json"
    encoded = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.write_certificate:
        path.write_text(encoded)
        print("WROTE_BIT_AFFINE_GENERATOR_SHARING_CERTIFICATE")
    else:
        expected = json.loads(path.read_text())
        if actual != expected:
            raise SystemExit("FAIL_BIT_AFFINE_GENERATOR_SHARING_CERTIFICATE_MISMATCH")
        print("PASS_BIT_AFFINE_GENERATOR_SHARING")
    print(actual["conclusion"])
    first = actual["first_endpoint"]
    pivot = actual["pivot_endpoint"]
    print(
        "radius_states="
        f"{pivot['search']['left_states']}/"
        f"{pivot['search']['right_states']} "
        f"examined={pivot['search']['left_states_examined']} "
        f"same_target_min={first['minimum']} "
        f"inverse_pair_min={pivot['minimum']} "
        f"pivot_witness_length={None if witness is None else len(witness)}"
    )


if __name__ == "__main__":
    main()
