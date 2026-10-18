#!/usr/bin/env python3
"""Independent formal-word replay using the four-point permutation model."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POINTS = tuple(range(4))
PERMUTATIONS = tuple(itertools.permutations(POINTS))
PERM_ID = {p: i for i, p in enumerate(PERMUTATIONS)}
GROUP_PRODUCT = tuple(
    tuple(PERM_ID[tuple(g[h[x]] for x in POINTS)] for h in PERMUTATIONS)
    for g in PERMUTATIONS
)
IDENTITY = PERM_ID[POINTS]


def affine_permutation(a: int, b: int) -> tuple[int, ...]:
    images = []
    for x in POINTS:
        x0, x1 = x & 1, (x >> 1) & 1
        y0 = (((a >> 0) & 1) & x0) ^ (((a >> 1) & 1) & x1) ^ (b & 1)
        y1 = (((a >> 2) & 1) & x0) ^ (((a >> 3) & 1) & x1) ^ ((b >> 1) & 1)
        images.append(y0 | (y1 << 1))
    return tuple(images)


def packed_affine(permutation: tuple[int, ...]) -> tuple[int, int]:
    translation = permutation[0]
    col0 = permutation[1] ^ translation
    col1 = permutation[2] ^ translation
    matrix = (
        (col0 & 1)
        | ((col1 & 1) << 1)
        | (((col0 >> 1) & 1) << 2)
        | (((col1 >> 1) & 1) << 3)
    )
    return matrix, translation


PRIMARY_GROUP_IDS = {
    (0b1011, 0): "a",
    (0b1101, 0): "b",
    (0b1001, 0b01): "u",
    (0b1001, 0b10): "v",
}
LABELS = ("a", "b", "u", "v")
LABEL_PERMS = {
    label: affine_permutation(*pair) for pair, label in PRIMARY_GROUP_IDS.items()
}
LABEL_IDS = {label: PERM_ID[permutation] for label, permutation in LABEL_PERMS.items()}
TARGET_PERM = affine_permutation(0b0110, 0b10)
INVERSE_PERM = affine_permutation(0b0110, 0b01)
TARGET_ID = PERM_ID[TARGET_PERM]
INVERSE_ID = PERM_ID[INVERSE_PERM]


def multiply_2x2(a: int, b: int) -> int:
    out = 0
    for i in range(2):
        for j in range(2):
            x = 0
            for k in range(2):
                x ^= ((a >> (2 * i + k)) & 1) & ((b >> (2 * k + j)) & 1)
            out |= x << (2 * i + j)
    return out


def rank_2x2(a: int) -> int:
    cols = ((a & 1) | (((a >> 2) & 1) << 1), ((a >> 1) & 1) | (((a >> 3) & 1) << 1))
    return int(cols[0] != 0) + int(cols[1] != 0 and cols[1] != cols[0])


def idempotents() -> tuple[int, ...]:
    values = set()
    for u in (1, 2, 3):
        for v in (1, 2, 3):
            if ((u & v).bit_count() & 1) == 1:
                n = 0
                for i in range(2):
                    for j in range(2):
                        n |= (((u >> i) & 1) & ((v >> j) & 1)) << (2 * i + j)
                values.add(n)
    result = tuple(sorted(values))
    if len(result) != 6:
        raise AssertionError("outer-product enumeration did not give six idempotents")
    return result


IDEMPOTENTS = idempotents()
FACTORS = tuple((label, LABEL_IDS[label], n) for label in LABELS for n in IDEMPOTENTS)
FACTOR_IDS = {(label, n): i for i, (label, _, n) in enumerate(FACTORS)}
IDENTITY_STATE = (1 << IDENTITY, 0, 0, 1 << IDENTITY)


def shift_poly(poly: int, gid: int) -> int:
    """Left-convolve by one group element using explicit permutation products."""
    result = 0
    remaining = poly
    while remaining:
        bit = remaining & -remaining
        source = bit.bit_length() - 1
        result ^= 1 << GROUP_PRODUCT[gid][source]
        remaining ^= bit
    return result


def left_factor(state: tuple[int, int, int, int], fid: int) -> tuple[int, int, int, int]:
    """Generic 2x2 matrix product using the two formal coefficients of D_N(g)."""
    _, gid, n = FACTORS[fid]
    at_identity = 0b1001 ^ n
    out = []
    for i in range(2):
        for j in range(2):
            value = 0
            for k in range(2):
                entry = 1 << (2 * i + k)
                if at_identity & entry:
                    value ^= state[2 * k + j]
                if n & entry:
                    value ^= shift_poly(state[2 * k + j], gid)
            out.append(value)
    return tuple(out)  # type: ignore[return-value]


def replay(word: bytes) -> tuple[int, int, int, int]:
    state = IDENTITY_STATE
    for fid in word:
        state = left_factor(state, fid)
    return state


def word_for(labels: bytes, n: int) -> bytes:
    return bytes(FACTOR_IDS[(chr(label), n)] for label in labels)


def radius_ball(radius: int) -> dict[tuple[int, int, int, int], bytes]:
    states = {IDENTITY_STATE: b""}
    frontier = [IDENTITY_STATE]
    for _ in range(radius):
        following = []
        for state in frontier:
            for fid in range(len(FACTORS)):
                nxt = left_factor(state, fid)
                if nxt not in states:
                    states[nxt] = states[state] + bytes((fid,))
                    following.append(nxt)
        frontier = following
    return states


def canonical_digest(states: dict[tuple[int, int, int, int], bytes]) -> str:
    # The primary certificate indexes the same formal group by packed (A,b).
    permutation_to_primary = {}
    for gid, permutation in enumerate(PERMUTATIONS):
        pair = packed_affine(permutation)
        if rank_2x2(pair[0]) != 2 or pair[1] not in range(4):
            raise AssertionError("a four-point permutation was not affine")
        permutation_to_primary[gid] = pair
    if len(set(permutation_to_primary.values())) != 24:
        raise AssertionError("the permutation-to-affine map is not bijective")
    # AGL_2(F_2) has 24 affine maps, so this verifies the faithful S4 model.
    # Reconstruct the primary enumeration order without importing its verifier.
    primary_pairs = []
    for a in range(16):
        if rank_2x2(a) != 2:
            continue
        for b in range(4):
            primary_pairs.append((a, b))
    primary_index = {pair: i for i, pair in enumerate(primary_pairs)}
    permutation_to_primary_index = {
        gid: primary_index[pair] for gid, pair in permutation_to_primary.items()
    }
    digest = hashlib.sha256()
    for state in sorted(states, key=lambda s: tuple(remap_poly(p, permutation_to_primary_index) for p in s)):
        mapped = tuple(remap_poly(p, permutation_to_primary_index) for p in state)
        digest.update(" ".join(f"{x:06x}" for x in mapped).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def remap_poly(poly: int, group_map: dict[int, int]) -> int:
    result = 0
    while poly:
        bit = poly & -poly
        source = bit.bit_length() - 1
        result |= 1 << group_map[source]
        poly ^= bit
    return result


def left_target(state: tuple[int, int, int, int], targets: tuple[int, int]) -> tuple[int, int, int, int]:
    return tuple(
        shift_poly(state[2 * i + j], targets[i])
        for i in range(2)
        for j in range(2)
    )  # type: ignore[return-value]


def target_state(targets: tuple[int, int]) -> tuple[int, int, int, int]:
    return (1 << targets[0], 0, 0, 1 << targets[1])


def exact_join(
    targets: tuple[int, int],
    left: dict[tuple[int, int, int, int], bytes],
    right: dict[tuple[int, int, int, int], bytes],
) -> bytes | None:
    best = None
    for state, prefix in left.items():
        inverse = replay(prefix[::-1])
        suffix = right.get(left_target(inverse, targets))
        if suffix is not None:
            candidate = prefix + suffix
            if best is None or (len(candidate), candidate) < (len(best), best):
                best = candidate
    return best


def main() -> None:
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    if len(PERMUTATIONS) != 24 or len(LABEL_IDS) != 4 or len(FACTORS) != 24:
        raise AssertionError("independent permutation model is incomplete")
    if len(set(LABEL_PERMS.values())) != 4:
        raise AssertionError("generator labels are not distinct")
    if rank_2x2(0b1011) != 2 or rank_2x2(0b1101) != 2:
        raise AssertionError("elementary shear matrices were not invertible")

    direct_same = word_for(b"abav", 0b0001) + word_for(b"abav", 0b1000)
    direct_inverse = word_for(b"abav", 0b0001) + word_for(b"abau", 0b1000)
    same_state = target_state((TARGET_ID, TARGET_ID))
    inverse_state = target_state((TARGET_ID, INVERSE_ID))
    if replay(direct_same) != same_state or replay(direct_inverse) != inverse_state:
        raise AssertionError("generic coefficient multiplication rejected a direct word")
    for factor_id in range(len(FACTORS)):
        if replay(bytes((factor_id, factor_id))) != IDENTITY_STATE:
            raise AssertionError("generic factor multiplication found a non-involution")

    left = radius_ball(3)
    right = radius_ball(4)
    primary_same = cert["first_endpoint"]["search"]
    primary_inverse = cert["pivot_endpoint"]["search"]
    if len(left) != primary_same["left_states"] or len(right) != primary_same["right_states"]:
        raise AssertionError("independent ball cardinalities disagree")
    if canonical_digest(left) != primary_same["left_state_sha256"]:
        raise AssertionError("independent radius-three formal states disagree")
    if canonical_digest(right) != primary_same["right_state_sha256"]:
        raise AssertionError("independent radius-four formal states disagree")
    same = exact_join((TARGET_ID, TARGET_ID), left, right)
    inverse = exact_join((TARGET_ID, INVERSE_ID), left, right)
    if (same is None) != (primary_same["minimum_word_length_found"] is None):
        raise AssertionError("independent identical-target join disagrees")
    if (inverse is None) != (primary_inverse["minimum_word_length_found"] is None):
        raise AssertionError("independent inverse-pair join disagrees")
    for word, endpoint in ((same, same_state), (inverse, inverse_state)):
        if word is not None and replay(word) != endpoint:
            raise AssertionError("independent search returned a false witness")
    print("PASS_BIT_AFFINE_GENERATOR_SHARING_INDEPENDENT")
    print(
        f"permutation_group={len(PERMUTATIONS)} factors={len(FACTORS)} "
        f"radius_states={len(left)}/{len(right)} same={None if same is None else len(same)} "
        f"inverse_pair={None if inverse is None else len(inverse)}"
    )


if __name__ == "__main__":
    main()
