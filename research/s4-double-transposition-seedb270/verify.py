#!/usr/bin/env python3
"""Exact F2[S4] radius-three test for a two-target double transposition."""
from __future__ import annotations

import argparse
import hashlib
import json
import itertools
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
NROLE = 3
NBITS = 24
MASK = (1 << NBITS) - 1
PATH_MASK = (1 << 21) - 1
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SEED = "b270b3b52d302ab6281ea2bc042d4aea"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_S4_DOUBLE_TRANSPOSITION: " + message)


def rank_f2(rows: list[int], n: int) -> int:
    rows = rows[:]
    rank = 0
    for col in range(n):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Composition a after b, so words extend by right multiplication."""
    return tuple(a[b[i]] for i in range(4))


def mat_from_perm(p: tuple[int, ...]) -> list[int]:
    # Column i of the permutation matrix is e_{p[i]}.
    rows = [0] * 4
    for col, row in enumerate(p):
        rows[row] |= 1 << col
    return rows


def pack_state(state: tuple[int, ...]) -> bytes:
    return b"".join(x.to_bytes(3, "little") for x in state)


def unpack_state(key: bytes) -> tuple[int, ...]:
    return tuple(int.from_bytes(key[i:i + 3], "little") for i in range(0, 27, 3))


def ring_shift(mask: int, g: int, tables: list[list[list[int]]]) -> int:
    return tables[g][0][mask & 255] | tables[g][1][(mask >> 8) & 255] | tables[g][2][(mask >> 16) & 255]


def encode_path(parent: int, factor_id: int) -> int:
    depth = parent >> 21
    path = parent & PATH_MASK
    return ((depth + 1) << 21) | (path << 7) | factor_id


def decode_path(encoded: int) -> tuple[int, ...]:
    depth = encoded >> 21
    path = encoded & PATH_MASK
    return tuple((path >> (7 * (depth - 1 - i))) & 127 for i in range(depth))


def path_depth(encoded: int) -> int:
    return encoded >> 21


def build_tables(group: list[tuple[int, ...]], index: dict[tuple[int, ...], int], swaps: list[tuple[int, ...]]):
    tables = []
    for s in swaps:
        generator = len(tables)
        chunks = []
        for byte_pos in range(3):
            table = [0] * 256
            for value in range(256):
                out = 0
                for bit in range(8):
                    source_index = byte_pos * 8 + bit
                    if source_index < len(group) and ((value >> bit) & 1):
                        out ^= 1 << index[compose(group[source_index], s)]
                table[value] = out
            chunks.append(table)
        tables.append(chunks)
    return tables


def apply_factor(state: tuple[int, ...], factor: tuple[int, int, int], tables) -> tuple[int, ...]:
    g, u, v = factor
    out = list(state)
    for i in range(NROLE):
        z = 0
        for k in range(NROLE):
            if (u >> k) & 1:
                z ^= state[3 * i + k]
        delta = z ^ ring_shift(z, g, tables)
        if delta:
            for j in range(NROLE):
                if (v >> j) & 1:
                    out[3 * i + j] ^= delta
    return tuple(out)


def apply_word(start: tuple[int, ...], word: tuple[int, ...], factors, tables) -> tuple[int, ...]:
    state = start
    for factor_id in word:
        state = apply_factor(state, factors[factor_id], tables)
    return state


def ball(start: tuple[int, ...], radius: int, factors, tables):
    # The encoded value stores shortest length and the 7-bit factor IDs.
    start_key = pack_state(start)
    seen = {start_key: 0}
    frontier = [start_key]
    layers = [1]
    for _depth in range(1, radius + 1):
        following = []
        for state_key in frontier:
            state = unpack_state(state_key)
            parent_code = seen[state_key]
            for factor_id, factor in enumerate(factors):
                nxt_key = pack_state(apply_factor(state, factor, tables))
                if nxt_key not in seen:
                    seen[nxt_key] = encode_path(parent_code, factor_id)
                    following.append(nxt_key)
        layers.append(len(following))
        frontier = following
    return seen, layers


def digest_ball(states: dict[bytes, int]) -> str:
    h = hashlib.sha256()
    for key in sorted(states):
        h.update(key)
    return h.hexdigest()


def determinant_f2(rows: list[int]) -> int:
    # For a 3x3 binary matrix, sum the six permutation monomials in F2.
    permutations = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))
    value = 0
    for p in permutations:
        term = 1
        for i, j in enumerate(p):
            term &= (rows[i] >> j) & 1
        value ^= term
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic CERTIFICATE.json")
    args = parser.parse_args()
    need((ROOT / "certificates/selected-result.json").is_file(), "repository root not found")
    selected = hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest()
    need(selected == SELECTED_SHA256, "selected record differs from the pinned base")

    group = sorted(itertools.permutations(range(4)))
    index = {p: i for i, p in enumerate(group)}
    identity_perm = (0, 1, 2, 3)
    identity_group = 1 << index[identity_perm]
    swaps = [(1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2)]
    target_perm = (2, 3, 0, 1)  # (13)(24), a double transposition.
    need(compose(target_perm, target_perm) == identity_perm, "target is not an involution")
    # Every paid scalar coupling is a rank-one idempotent uv^T over F2.
    projectors = []
    for u in range(1, 1 << NROLE):
        for v in range(1, 1 << NROLE):
            if ((u & v).bit_count() & 1) == 1:
                projectors.append((u, v))
    need(len(projectors) == 28, "rank-one idempotent count is not 28")
    factors = [(g, u, v) for g in range(3) for u, v in projectors]
    need(len(factors) == 84, "paid alphabet is not 84 factors")
    tables = build_tables(group, index, swaps)

    # Verify rank-one/idempotent and elementary displacement claims exactly.
    for u, v in projectors:
        rows = [sum((((u >> i) & 1) * (((v >> j) & 1) << j)) for j in range(3)) for i in range(3)]
        need(rank_f2(rows, 3) == 1, "scalar coupling is not rank one")
        product = [0] * 3
        for i in range(3):
            for k in range(3):
                if (rows[i] >> k) & 1:
                    product[i] ^= rows[k]
        need(product == rows, "scalar coupling is not idempotent")
    for s in swaps:
        rows = mat_from_perm(s)
        diff = [rows[i] ^ (1 << i) for i in range(4)]
        need(rank_f2(diff, 4) == 1, "adjacent transposition displacement rank is not one")
    qrows = mat_from_perm(target_perm)
    qdiff = [qrows[i] ^ (1 << i) for i in range(4)]
    need(rank_f2(qdiff, 4) == 2, "double-transposition displacement rank is not two")

    identity = tuple(identity_group if i // 3 == i % 3 else 0 for i in range(9))
    target_mask = 1 << index[target_perm]
    target = (target_mask, 0, 0, 0, target_mask, 0, 0, 0, identity_group)

    # Every paid factor is involutive, so the target ball reverses all suffixes.
    for factor in factors:
        need(apply_factor(apply_factor(identity, factor, tables), factor, tables) == identity,
             "a paid factor is not an involution")

    # Find a shortest adjacent-transposition word for q by exact BFS on S4.
    permutation_words = {identity_perm: ()}
    pending = [identity_perm]
    for p in pending:
        for s_id, s in enumerate(swaps):
            nxt = compose(p, s)
            if nxt not in permutation_words:
                permutation_words[nxt] = permutation_words[p] + (s_id,)
                pending.append(nxt)
    q_word = permutation_words[target_perm]
    need(len(q_word) == 4, "the direct Coxeter cost is not four per target")
    factor_lookup = {(g, u, v): fid for fid, (g, u, v) in enumerate(factors)}
    direct = tuple(
        factor_lookup[(s_id, 1 << role, 1 << role)]
        for role in (0, 1)
        for s_id in q_word
    )
    need(len(direct) == 8 and apply_word(identity, direct, factors, tables) == target,
         "direct eight-call construction failed")
    for omitted in range(len(direct)):
        changed = direct[:omitted] + direct[omitted + 1:]
        need(apply_word(identity, changed, factors, tables) != target,
             "an omitted direct call still reaches the target")
    altered_dirty_target = (target_mask, 0, 0, 0, target_mask, 0, 0, 1 << index[swaps[0]], identity_group)
    need(apply_word(identity, direct, factors, tables) != altered_dirty_target,
         "changed dirty-role control was not rejected")

    # Sign quotient F2[S4] -> F2[C2]. For rank-one idempotent N, det(I+(x+1)N)=x.
    # q is even, so target determinant is 1. Since x has order two, call count is even.
    invertible = 0
    for bits in range(1 << 9):
        rows = [(bits >> (3 * i)) & 7 for i in range(3)]
        if rank_f2(rows, 3) == 3:
            invertible += 1
            need(determinant_f2(rows) == 1, "GL3(F2) mixer determinant is not one")
    need(invertible == 168, "unexpected GL3(F2) order")

    left, left_layers = ball(identity, 3, factors, tables)
    right, right_layers = ball(target, 3, factors, tables)
    intersections = []
    for state, left_code in left.items():
        right_code = right.get(state)
        if right_code is not None:
            intersections.append((path_depth(left_code) + path_depth(right_code), state, left_code, right_code))
    intersections.sort(key=lambda entry: entry[0])
    if intersections:
        shortest = intersections[0]
        word = decode_path(shortest[2]) + tuple(reversed(decode_path(shortest[3])))
        need(len(word) == shortest[0] and apply_word(identity, word, factors, tables) == target,
             "meet-in-the-middle witness does not replay")
        exact_minimum = shortest[0] if len(word) % 2 == 0 else None
        need(exact_minimum is not None, "odd-length witness contradicts the sign determinant")
    else:
        word = None
        exact_minimum = 8

    # Count and hash the complete canonical balls. Their size depends only on the
    # Cayley action; hashes bind the exact coefficient states independently.
    expected_layers = [1, 84, 4697, 232692]
    need(left_layers == expected_layers and right_layers == expected_layers,
         f"unexpected complete ball layers: {left_layers} / {right_layers}")
    certificate = {
        "schema_version": 1,
        "track": "bit-mechanisms",
        "seed": SEED,
        "task_id": "bit-new-register-model",
        "base_commit": BASE,
        "selected_result_sha256": SELECTED_SHA256,
        "model": {
            "field": "F2",
            "address_group": "S4",
            "roles": 3,
            "active_targets": 2,
            "target_permutation": "(13)(24)",
            "paid_letters": ["(12)", "(23)", "(34)"],
            "rank_one_idempotents": 28,
            "paid_factor_count": 84,
            "free_scalar_mixing": "all GL3(F2), normalized by augmentation",
            "dirty_roles": "all three arbitrary inputs; third role restored exactly",
            "endpoint_ring": "formal F2[S4]"
        },
        "direct_word": {
            "adjacent_transposition_indices": list(q_word),
            "paid_call_count": len(direct),
            "formal_endpoint_verified": True,
            "all_single_call_omissions_rejected": len(direct)
        },
        "cost_screen": {
            "direct_bill": 8,
            "natural_representation_rank_floor": 4,
            "sign_determinant_forces_even_length": True,
            "best_strict_improvement_bill": 6,
            "call_saving_required": 2
        },
        "meet_in_middle": {
            "radius_each_side": 3,
            "left_layer_counts": left_layers,
            "right_layer_counts": right_layers,
            "left_state_count": len(left),
            "right_state_count": len(right),
            "left_sorted_state_sha256": digest_ball(left),
            "right_sorted_state_sha256": digest_ball(right),
            "intersection_count": len(intersections),
            "shortest_meeting_length": intersections[0][0] if intersections else None,
            "shortest_word_factor_ids": list(word) if word is not None else None,
            "exact_minimum_if_within_six": exact_minimum if exact_minimum is not None else None,
            "exact_minimum": exact_minimum,
            "all_calls_involutive": True
        },
        "controls": {
            "all_84_factor_involutions": True,
            "all_28_idempotents_rank_one": True,
            "all_3_paid_displacements_rank_one": True,
            "target_displacement_rank_two": True,
            "altered_dirty_role_target_rejected": True,
            "gl3_f2_order": invertible,
            "gl3_f2_determinants_one": True
        },
        "selected_frontier": "unchanged; no supplier or kappa claim",
        "runtime_seconds_excluded_from_receipt": True
    }
    cert_path = PACKAGE / "CERTIFICATE.json"
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.write:
        cert_path.write_text(encoded)
    else:
        need(cert_path.is_file(), "CERTIFICATE.json missing; run verify.py --write first")
        need(cert_path.read_text() == encoded, "deterministic certificate differs; regenerate with --write")

    result = "EXACT_8" if exact_minimum == 8 else f"EXACT_{exact_minimum}"
    print(f"PASS_S4_DOUBLE_TRANSPOSITION {result} direct=8 rank_floor=4 parity=even factors=84")
    print(f"balls={len(left)},{len(right)} intersections={len(intersections)} layers={left_layers}")
    print(f"ball_sha256={certificate['meet_in_middle']['left_sorted_state_sha256'][:16]},{certificate['meet_in_middle']['right_sorted_state_sha256'][:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
