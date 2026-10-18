#!/usr/bin/env python3
"""Exact D8 central-pair search with three arbitrary dirty registers."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def group_mul(a: int, b: int) -> int:
    """UT3(F2): (a,b,c)(a',b',c')=(a+a',b+b',c+c'+a b')."""
    return (a ^ b) ^ (((a & 1) & ((b >> 1) & 1)) << 2)


TABLE = tuple(tuple(group_mul(a, b) for b in range(8)) for a in range(8))
GENERATORS = tuple(
    (g, u, v)
    for g in (1, 2)
    for u in range(1, 8)
    for v in range(1, 8)
    if (u & v).bit_count() & 1
)


def left_permutation(g: int) -> tuple[int, ...]:
    result = [0] * 256
    for value in range(256):
        moved = 0
        for j in range(8):
            if (value >> j) & 1:
                moved ^= 1 << TABLE[g][j]
        result[value] = moved
    return tuple(result)


LEFT = {g: left_permutation(g) for g in (1, 2)}
DELTA = {g: tuple(value ^ LEFT[g][value] for value in range(256)) for g in (1, 2)}


def fast_step(state: bytes, gate: tuple[int, int, int]) -> bytes:
    """Apply (I+([g]+[1])uv^T) on the left to a 3x3 F2[G] matrix."""
    g, u, v = gate
    out = bytearray(state)
    for col in range(3):
        value = 0
        for row in range(3):
            if (v >> row) & 1:
                value ^= state[3 * row + col]
        delta = DELTA[g][value]
        for row in range(3):
            if (u >> row) & 1:
                out[3 * row + col] ^= delta
    return bytes(out)


IDENTITY = bytes((1, 0, 0, 0, 1, 0, 0, 0, 1))
TARGET = bytes((16, 0, 0, 0, 16, 0, 0, 0, 1))


def ball(start: bytes, depth: int) -> tuple[set[bytes], list[bytes], list[int]]:
    seen = {start}
    frontier = [start]
    layers = [1]
    for _ in range(depth):
        next_frontier: list[bytes] = []
        for state in frontier:
            for gate in GENERATORS:
                candidate = fast_step(state, gate)
                if candidate not in seen:
                    seen.add(candidate)
                    next_frontier.append(candidate)
        frontier = next_frontier
        layers.append(len(frontier))
    return seen, frontier, layers


def conv(a: int, b: int) -> int:
    """Independent coefficient convolution in the full eight-element algebra."""
    out = 0
    for i in range(8):
        if (a >> i) & 1:
            for j in range(8):
                if (b >> j) & 1:
                    out ^= 1 << TABLE[i][j]
    return out


def matrix_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for row in range(3):
        for col in range(3):
            value = 0
            for k in range(3):
                value ^= conv(a[3 * row + k], b[3 * k + col])
            out.append(value)
    return tuple(out)


def gate_matrix(gate: tuple[int, int, int]) -> tuple[int, ...]:
    g, u, v = gate
    out = []
    for row in range(3):
        for col in range(3):
            value = int(row == col)
            if ((u >> row) & 1) and ((v >> col) & 1):
                value ^= 1 ^ (1 << g)
            out.append(value)
    return tuple(out)


def slow_apply(word: tuple[int, ...], initial: tuple[int, ...]) -> tuple[int, ...]:
    state = initial
    gates = tuple(map(gate_matrix, GENERATORS))
    for index in word:
        state = matrix_mul(gates[index], state)
    return state


def sha_states(states: set[bytes]) -> str:
    return hashlib.sha256(b"".join(sorted(states))).hexdigest()


def run() -> dict:
    # Check all declared predecessor pins before using their model and baseline.
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] != "input":
            continue
        raw = (ROOT / item["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError(f"source pin changed: {item['path']}")

    if len(GENERATORS) != 56:
        raise ValueError("the complete two-label/rank-one-idempotent alphabet has size 56")
    idempotents = {
        tuple(((u >> row) & 1) & ((v >> col) & 1) for row in range(3) for col in range(3))
        for u in range(1, 8)
        for v in range(1, 8)
        if (u & v).bit_count() & 1
    }
    if len(idempotents) != 28:
        raise ValueError("the rank-one idempotent parameterization is not complete and duplicate-free")
    if group_mul(1, 1) != 0 or group_mul(2, 2) != 0:
        raise ValueError("x and y must be involutions")
    z = group_mul(group_mul(group_mul(1, 2), 1), 2)
    if z != 4 or any(group_mul(z, h) != group_mul(h, z) for h in range(8)):
        raise ValueError("the declared xyxy label must be the central commutator")
    for a, b, c in itertools.product(range(8), repeat=3):
        if TABLE[TABLE[a][b]][c] != TABLE[a][TABLE[b][c]]:
            raise ValueError("the group table is not associative")

    # The direct word uses four paid factors per duplicated central target.
    direct = tuple(
        GENERATORS.index((g, 1 << row, 1 << row))
        for row in (0, 1)
        for g in (1, 2, 1, 2)
    )
    expected = (16, 0, 0, 0, 16, 0, 0, 0, 1)
    changed_target = (16, 0, 0, 0, 16, 0, 0, 0, 16)
    identity_matrix = (1, 0, 0, 0, 1, 0, 0, 0, 1)
    if len(direct) != 8 or slow_apply(direct, identity_matrix) != expected:
        raise ValueError("the eight-call direct upper bound failed")
    if any(slow_apply(direct[:i] + direct[i + 1 :], identity_matrix) == expected for i in range(8)):
        raise ValueError("an omitted direct call unexpectedly retains the target")
    if slow_apply(direct, identity_matrix) == changed_target:
        raise ValueError("the direct word unexpectedly matches the changed third target")
    for index in range(len(GENERATORS)):
        if matrix_mul(gate_matrix(GENERATORS[index]), gate_matrix(GENERATORS[index])) != identity_matrix:
            raise ValueError("a paid gate is not an involution")

    # Cross-check the compact transition against full coefficient convolution.
    rng = random.Random(0xD8_3)
    for _ in range(5):
        state = bytes(rng.randrange(256) for _ in range(9))
        for index, gate in enumerate(GENERATORS):
            fast = fast_step(state, gate)
            slow = matrix_mul(gate_matrix(gate), tuple(state))
            if fast != bytes(slow):
                raise ValueError(f"transition disagreement at gate {index}")

    left, _, left_layers = ball(IDENTITY, 3)
    right, right_frontier, right_layers = ball(TARGET, 3)
    radius_three_meet = left & right
    radius_four_edges = len(right_frontier) * len(GENERATORS)
    radius_four_hits = 0
    for state in right_frontier:
        for gate in GENERATORS:
            if fast_step(state, gate) in left:
                radius_four_hits += 1

    hit = bool(radius_three_meet or radius_four_hits)
    if hit:
        raise ValueError("a word of at most seven paid factors exists; update the claim and witness")
    if radius_four_edges != 2_543_744:
        raise ValueError("unexpected exact radius-four edge coverage")

    return {
        "status": "PASS_D8_THIRD_REGISTER",
        "seed": "89dea4bc3a42ef85f785169cd2b6977e",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "group": "UT3(F2)",
        "target": "diag([xyxy],[xyxy],[1])",
        "registers": 3,
        "rank_one_idempotents": len(idempotents),
        "generators": 56,
        "identity_layers": left_layers,
        "target_layers": right_layers,
        "identity_states_radius3": len(left),
        "target_states_radius3": len(right),
        "identity_ball_sha256": sha_states(left),
        "target_ball_sha256": sha_states(right),
        "radius3_intersection_states": len(radius_three_meet),
        "target_radius4_edges_checked": radius_four_edges,
        "radius4_intersection_edges": radius_four_hits,
        "maximum_paid_word_searched": 7,
        "direct_upper_bound_calls": len(direct),
        "exact_minimum_in_model": 8,
        "free_gl3_mixing": "normalized by augmentation into the complete 56-generator alphabet",
        "controls": {
            "full_group_associativity": True,
            "all_generators_involutive": True,
            "direct_word_exact": True,
            "all_eight_single_omissions_rejected": True,
            "compact_transition_matches_full_algebra": True,
            "changed_third_target_rejected": slow_apply(direct, identity_matrix) != changed_target,
        },
        "new_kappa": False,
    }


if __name__ == "__main__":
    result = run()
    receipt = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        receipt.write_text(json.dumps(result, indent=2) + "\n")
    elif json.loads(receipt.read_text()) != result:
        raise SystemExit("receipt differs; use --write after reviewing the regenerated evidence")
    print(
        result["status"],
        "min=" + str(result["exact_minimum_in_model"]),
        "identity_layers=" + ",".join(map(str, result["identity_layers"])),
        "right_radius4_edges=" + str(result["target_radius4_edges_checked"]),
    )
