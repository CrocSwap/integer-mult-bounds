#!/usr/bin/env python3
"""Exact radius-six search for two central commutators in UT_3(F_4)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def f4_mul(a: int, b: int) -> int:
    """Multiply two F4 elements in the basis (1,w), w^2+w+1=0."""
    poly = 0
    for i in range(2):
        if (a >> i) & 1:
            poly ^= b << i
    if poly & 4:
        poly ^= 7
    return poly


F4_MUL = tuple(tuple(f4_mul(a, b) for b in range(4)) for a in range(4))


def gid(a: int, b: int, c: int) -> int:
    return a | (b << 2) | (c << 4)


def coords(g: int) -> tuple[int, int, int]:
    return g & 3, (g >> 2) & 3, (g >> 4) & 3


def gmul(g: int, h: int) -> int:
    a, b, c = coords(g)
    aa, bb, cc = coords(h)
    return gid(a ^ aa, b ^ bb, c ^ cc ^ F4_MUL[a][bb])


GROUP_MUL = tuple(tuple(gmul(g, h) for h in range(64)) for g in range(64))
E = gid(0, 0, 0)
X1 = gid(1, 0, 0)
XW = gid(2, 0, 0)
Y1 = gid(0, 1, 0)
YW = gid(0, 2, 0)
Z1 = gid(0, 0, 1)
ZW = gid(0, 0, 2)
ZW2 = gid(0, 0, 3)
LABELS = (X1, XW, Y1, YW)
LABEL_NAMES = ("X_1", "X_w", "Y_1", "Y_w")


def idempotents() -> tuple[tuple[int, int, int, int], ...]:
    out = set()
    for u in range(1, 4):
        for v in range(1, 4):
            dot = (((u >> 0) & 1) & ((v >> 0) & 1)) ^ (((u >> 1) & 1) & ((v >> 1) & 1))
            if dot:
                u0, u1 = u & 1, (u >> 1) & 1
                v0, v1 = v & 1, (v >> 1) & 1
                out.add((u0 * v0, u0 * v1, u1 * v0, u1 * v1))
    return tuple(sorted(out))


IDEMPOTENTS = idempotents()
IDENTITY = (1 << E, 0, 0, 1 << E)


def idempotents3() -> tuple[tuple[int, ...], ...]:
    out = set()
    for u in range(1, 8):
        for v in range(1, 8):
            if (u & v).bit_count() % 2:
                out.add(tuple(((u >> i) & 1) * ((v >> j) & 1)
                              for i in range(3) for j in range(3)))
    return tuple(sorted(out))


IDEMPOTENTS3 = idempotents3()
IDENTITY3 = tuple((1 << E) if row == col else 0
                  for row in range(3) for col in range(3))
CENTER = (E, Z1, ZW, ZW2)


def build_shift_tables() -> dict[int, tuple[tuple[int, ...], ...]]:
    result = {}
    for g in set(LABELS) | {E, Z1, ZW, ZW2}:
        chunks = []
        for chunk in range(8):
            table = []
            for byte in range(256):
                image = 0
                for bit in range(8):
                    if (byte >> bit) & 1:
                        image |= 1 << GROUP_MUL[chunk * 8 + bit][g]
                table.append(image)
            chunks.append(tuple(table))
        result[g] = tuple(chunks)
    return result


SHIFT_TABLES = build_shift_tables()


def shift(mask: int, g: int) -> int:
    table = SHIFT_TABLES[g]
    out = 0
    for chunk in range(8):
        out |= table[chunk][(mask >> (8 * chunk)) & 255]
    return out


# A factor code is 6 * label_index + idempotent_index.
FACTORS = tuple((label_i, idem_i) for label_i in range(4) for idem_i in range(6))


def step(matrix: tuple[int, int, int, int], code: int) -> tuple[int, int, int, int]:
    label_i, idem_i = FACTORS[code]
    g = LABELS[label_i]
    n = IDEMPOTENTS[idem_i]
    out = []
    for row in range(2):
        for col in range(2):
            value = matrix[2 * row + col]
            for k in range(2):
                if n[2 * k + col]:
                    entry = matrix[2 * row + k]
                    value ^= shift(entry, g) ^ entry
            out.append(value)
    return tuple(out)  # type: ignore[return-value]


def factor_matrix(code: int) -> tuple[int, int, int, int]:
    label_i, idem_i = FACTORS[code]
    g = LABELS[label_i]
    n = IDEMPOTENTS[idem_i]
    gp = (1 << E) | (1 << g)
    return tuple(
        ((1 << E) if i == j else 0) ^ (gp if n[2 * i + j] else 0)
        for i in range(2) for j in range(2)
    )  # type: ignore[return-value]


def ring_mul_generic(left: int, right: int) -> int:
    out = 0
    a = left
    while a:
        bit_a = a & -a
        i = bit_a.bit_length() - 1
        a ^= bit_a
        b = right
        while b:
            bit_b = b & -b
            j = bit_b.bit_length() - 1
            b ^= bit_b
            out ^= 1 << GROUP_MUL[i][j]
    return out


def matrix_mul_generic(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(
        ring_mul_generic(a[2 * row], b[col]) ^ ring_mul_generic(a[2 * row + 1], b[2 + col])
        for row in range(2) for col in range(2)
    )  # type: ignore[return-value]


def product(word: tuple[int, ...] | list[int]) -> tuple[int, int, int, int]:
    matrix = IDENTITY
    for code in word:
        matrix = step(matrix, code)
    return matrix


def target(z_left: int = Z1, z_right: int = ZW) -> tuple[int, int, int, int]:
    return (1 << z_left, 0, 0, 1 << z_right)


def direct_word() -> tuple[int, ...]:
    e11 = IDEMPOTENTS.index((1, 0, 0, 0))
    e22 = IDEMPOTENTS.index((0, 0, 0, 1))
    code = lambda label, idem: 6 * LABELS.index(label) + idem
    return (
        code(X1, e11), code(Y1, e11), code(X1, e11), code(Y1, e11),
        code(XW, e22), code(Y1, e22), code(XW, e22), code(Y1, e22),
    )


def single_word() -> tuple[int, ...]:
    e11 = IDEMPOTENTS.index((1, 0, 0, 0))
    return tuple(6 * LABELS.index(g) + e11 for g in (X1, Y1, X1, Y1))


def build_ball(radius: int = 3):
    words = {IDENTITY: ()}
    frontier = [IDENTITY]
    layers = [1]
    layer_digests = [matrix_digest(frontier)]
    for _depth in range(1, radius + 1):
        next_frontier = []
        for state in frontier:
            prefix = words[state]
            for code in range(len(FACTORS)):
                successor = step(state, code)
                if successor not in words:
                    words[successor] = prefix + (code,)
                    next_frontier.append(successor)
        layers.append(len(next_frontier))
        layer_digests.append(matrix_digest(next_frontier))
        frontier = next_frontier
    return words, layers, layer_digests


def matrix_digest(states) -> str:
    digest = hashlib.sha256()
    for state in sorted(states):
        for coefficient in state:
            digest.update(coefficient.to_bytes(8, "little"))
    return digest.hexdigest()


def required_right(left_inverse: tuple[int, int, int, int], wanted: tuple[int, int, int, int]):
    # wanted is diagonal with one group element in each diagonal slot.
    left_z = wanted[0].bit_length() - 1
    right_z = wanted[3].bit_length() - 1
    return (
        shift(left_inverse[0], left_z), shift(left_inverse[1], right_z),
        shift(left_inverse[2], left_z), shift(left_inverse[3], right_z),
    )


def find_within_six(wanted, words):
    for left, left_word in words.items():
        inverse = product(tuple(reversed(left_word)))
        need_right = required_right(inverse, wanted)
        right_word = words.get(need_right)
        if right_word is not None:
            witness = left_word + right_word
            need(product(witness) == wanted, "meet-in-the-middle witness failed exact endpoint")
            return witness
    return None


def group_checks() -> None:
    need(len({GROUP_MUL[g][h] for g in range(64) for h in range(64)}) == 64,
         "group product table does not cover all encoded elements")
    for a in range(64):
        need(GROUP_MUL[E][a] == a and GROUP_MUL[a][E] == a, "bad group identity")
        for b in range(64):
            for c in range(64):
                need(GROUP_MUL[GROUP_MUL[a][b]][c] == GROUP_MUL[a][GROUP_MUL[b][c]],
                     "UT3(F4) multiplication is not associative")
    need(len(IDEMPOTENTS) == 6, "wrong rank-one idempotent count")
    for n in IDEMPOTENTS:
        a, b, c, d = n
        need((a ^ (b & c), (a & b) ^ (b & d), (c & a) ^ (d & c), (c & b) ^ d) == n,
             "listed matrix is not idempotent")
        need(a ^ d == 1, "rank-one idempotent does not have trace one")
    for g in LABELS:
        need(GROUP_MUL[g][g] == E, "label is not an involution")
    need(GROUP_MUL[GROUP_MUL[X1][Y1]][GROUP_MUL[X1][Y1]] == Z1,
         "[X_1,Y_1] is not Z_1")
    need(GROUP_MUL[GROUP_MUL[XW][Y1]][GROUP_MUL[XW][Y1]] == ZW,
         "[X_w,Y_1] is not Z_w")
    reachable = {E}
    frontier = [E]
    while frontier:
        next_frontier = []
        for state in frontier:
            for label in LABELS:
                successor = GROUP_MUL[state][label]
                if successor not in reachable:
                    reachable.add(successor)
                    next_frontier.append(successor)
        frontier = next_frontier
    need(len(reachable) == 64, "four paid labels do not generate all of UT_3(F_4)")
    need(len({E, Z1, ZW, ZW2}) == 4, "central commutator targets are not independent")


def transition_crosscheck() -> int:
    states = {IDENTITY}
    frontier = [IDENTITY]
    for _ in range(2):
        next_frontier = []
        for state in frontier:
            for code in range(len(FACTORS)):
                successor = step(state, code)
                if successor not in states:
                    states.add(successor)
                    next_frontier.append(successor)
        frontier = next_frontier
    checked = 0
    for state in states:
        for code in range(len(FACTORS)):
            packed = step(state, code)
            generic = matrix_mul_generic(state, factor_matrix(code))
            need(packed == generic, "packed transition differs from generic group-algebra multiplication")
            checked += 1
    return checked


def step3(matrix: tuple[int, ...], g: int, n: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for row in range(3):
        for col in range(3):
            value = matrix[3 * row + col]
            for k in range(3):
                if n[3 * k + col]:
                    entry = matrix[3 * row + k]
                    value ^= shift(entry, g) ^ entry
            out.append(value)
    return tuple(out)


def factor3(g: int, n: tuple[int, ...]) -> tuple[int, ...]:
    gp = (1 << E) | (1 << g)
    return tuple(
        (((1 << E) if row == col else 0) ^
         (gp if n[3 * row + col] else 0))
        for row in range(3) for col in range(3)
    )


def product3(word: tuple[tuple[int, tuple[int, ...]], ...]) -> tuple[int, ...]:
    matrix = IDENTITY3
    for g, n in word:
        matrix = step3(matrix, g, n)
    return matrix


def matrix_mul_generic3(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        ring_mul_generic(a[3 * row], b[col]) ^
        ring_mul_generic(a[3 * row + 1], b[3 + col]) ^
        ring_mul_generic(a[3 * row + 2], b[6 + col])
        for row in range(3) for col in range(3)
    )


def embed_center(matrix: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum((1 << CENTER[c]) for c in range(4) if (entry >> c) & 1)
                 for entry in matrix)


def center_ring_mul(a: int, b: int) -> int:
    out = 0
    for i in range(4):
        if (a >> i) & 1:
            for j in range(4):
                if (b >> j) & 1:
                    out ^= 1 << (i ^ j)
    return out


CENTER_RING_MUL = tuple(tuple(center_ring_mul(a, b) for b in range(16))
                        for a in range(16))


def center_block(z: int, n: tuple[int, ...]) -> tuple[int, ...]:
    delta = 1 | (1 << z)
    return tuple(
        ((1 if row == col else 0) ^
         (delta if n[3 * row + col] else 0))
        for row in range(3) for col in range(3)
    )


def center_matrix_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        CENTER_RING_MUL[a[3 * row]][b[col]] ^
        CENTER_RING_MUL[a[3 * row + 1]][b[3 + col]] ^
        CENTER_RING_MUL[a[3 * row + 2]][b[6 + col]]
        for row in range(3) for col in range(3)
    )


def triple_block_census():
    choices = tuple((z, n, center_block(z, n))
                    for z in (1, 2) for n in IDEMPOTENTS3)
    wanted = tuple((1 << z) if row == col else 0
                   for row, z in enumerate((1, 2, 3)) for col in range(3))
    counts = []
    for depth in range(1, 4):
        candidates = 0
        hit = None
        for word in __import__("itertools").product(range(len(choices)), repeat=depth):
            state = tuple((1 if row == col else 0)
                          for row in range(3) for col in range(3))
            for index in word:
                state = center_matrix_mul(state, choices[index][2])
            candidates += 1
            if state == wanted:
                hit = tuple((choices[index][0], choices[index][1]) for index in word)
                break
        counts.append(candidates)
        if hit is not None:
            return choices, wanted, counts, hit
    return choices, wanted, counts, None


def center_product_crosscheck(choices) -> int:
    checked = 0
    for left in choices:
        for right in choices:
            packed = center_matrix_mul(left[2], right[2])
            generic = matrix_mul_generic3(embed_center(left[2]), embed_center(right[2]))
            need(embed_center(packed) == generic,
                 "central-ring matrix product differs from full group-algebra product")
            checked += 1
    return checked


def triple_direct_word():
    e11 = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    e22 = (0, 0, 0, 0, 1, 0, 0, 0, 0)
    e33 = (0, 0, 0, 0, 0, 0, 0, 0, 1)
    return tuple((g, e11) for g in (X1, Y1, X1, Y1)) + \
           tuple((g, e22) for g in (XW, Y1, XW, Y1)) + \
           tuple((g, e33) for g in (X1, XW, Y1, X1, XW, Y1))


def triple_controls():
    need(len(IDEMPOTENTS3) == 28, "wrong rank-one idempotent count for three roles")
    for n in IDEMPOTENTS3:
        for row in range(3):
            for col in range(3):
                value = 0
                for k in range(3):
                    value ^= n[3 * row + k] & n[3 * k + col]
                need(value == n[3 * row + col], "listed 3x3 matrix is not idempotent")
        need(n[0] ^ n[4] ^ n[8] == 1, "rank-one 3x3 idempotent does not have trace one")

    checked_blocks = 0
    for z, x in ((Z1, X1), (ZW, XW)):
        for n in IDEMPOTENTS3:
            packed = IDENTITY3
            generic = IDENTITY3
            for g in (x, Y1, x, Y1):
                packed = step3(packed, g, n)
                generic = matrix_mul_generic3(generic, factor3(g, n))
            expected = embed_center(center_block(1 if z == Z1 else 2, n))
            need(packed == expected == generic,
                 "four-call commutator block differs from its central block")
            checked_blocks += 1

    choices, wanted_center, counts, hit = triple_block_census()
    need(hit is None, "three-call commutator-block family unexpectedly reaches the dependent triple")
    central_product_checks = center_product_crosscheck(choices)
    direct = triple_direct_word()
    wanted_full = tuple((1 << z) if row == col else 0
                        for row, z in enumerate((Z1, ZW, ZW2)) for col in range(3))
    packed_direct = product3(direct)
    generic_direct = IDENTITY3
    for g, n in direct:
        generic_direct = matrix_mul_generic3(generic_direct, factor3(g, n))
    need(len(direct) == 14 and packed_direct == wanted_full == generic_direct,
         "direct 14-call dependent central triple failed")
    for index in range(len(direct)):
        shortened = direct[:index] + direct[index + 1:]
        need(product3(shortened) != wanted_full,
             "single-factor deletion of the direct central triple unexpectedly passes")
    return {
        "target": [Z1, ZW, ZW2],
        "direct_coordinate_calls": len(direct),
        "block_alphabet_size": len(choices),
        "raw_ordered_block_sequences_checked_by_depth": counts,
        "raw_block_sequences_total": sum(counts),
        "block_family_hit_through_three": False,
        "block_family_scope": "concatenations of at most three D_N(Z_1) or D_N(Z_w) blocks, each expanded to four paid source factors",
        "four_call_block_endpoint_checks": checked_blocks,
        "central_block_pair_product_checks": central_product_checks,
        "direct_word_full_and_generic_endpoints_match": True,
        "all_fourteen_single_deletions_fail": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    group_checks()
    packed_checks = transition_crosscheck()
    identity = IDENTITY
    for code in range(len(FACTORS)):
        one = step(identity, code)
        need(step(one, code) == identity, "paid factor is not involutive")

    one_output = single_word()
    single_target = target(Z1, E)
    need(len(one_output) == 4 and product(one_output) == single_target,
         "four-call one-output positive control failed")
    need(matrix_mul_generic(IDENTITY, IDENTITY) == IDENTITY, "generic identity control failed")
    direct = direct_word()
    wanted = target()
    need(len(direct) == 8 and product(direct) == wanted,
         "direct eight-call construction failed")
    generic_direct = IDENTITY
    for code in direct:
        generic_direct = matrix_mul_generic(generic_direct, factor_matrix(code))
    need(generic_direct == wanted, "generic direct-word endpoint differs")
    for index in range(len(direct)):
        shortened = direct[:index] + direct[index + 1:]
        need(product(shortened) != wanted, "one-factor deletion control unexpectedly reaches target")
    mutated = target(Z1, ZW2)
    need(product(direct) != mutated, "target mutation control unexpectedly passes")
    triple_result = triple_controls()

    words, layers, layer_digests = build_ball(3)
    raw_words = sum(24 ** depth for depth in range(4))
    need(raw_words == 14425, "raw radius-three word count changed")
    found_single = find_within_six(single_target, words)
    need(found_single is not None and len(found_single) == 4,
         "meet-in-the-middle did not find the known four-call positive control")
    found_pair = find_within_six(wanted, words)
    need(found_pair is None, "unexpected shared word of at most six calls; inspect witness")

    cert = {
        "model": "F2[UT3(F4)]",
        "field_polynomial": "w^2+w+1=0",
        "group_order": 64,
        "group_law": "(a,b,c)(a',b',c')=(a+a',b+b',c+c'+ab')",
        "labels": dict(zip(LABEL_NAMES, LABELS)),
        "central_targets": {"Z_1": Z1, "Z_w": ZW},
        "alphabet_factor_count": 24,
        "rank_one_idempotent_count": len(IDEMPOTENTS),
        "radius": 3,
        "raw_words_through_radius": raw_words,
        "distinct_state_layer_sizes": layers,
        "distinct_ball_states": len(words),
        "layer_sha256": layer_digests,
        "ball_sha256": matrix_digest(words),
        "packed_vs_generic_transitions": packed_checks,
        "single_output_positive_word_length": len(found_single),
        "direct_pair_word_length": len(direct),
        "shared_pair_word_through_six": False,
        "minimum_pair_word_length": 8,
        "dependent_three_role_block_pivot": triple_result,
        "parity_lemma": "Every label occurs an even number of times because the target is trivial mod I^2 and each rank-one idempotent has trace one.",
        "controls": {
            "all_factor_involutions": True,
            "single_commutator_positive": True,
            "direct_pair_positive": True,
            "all_eight_single_deletions_fail": True,
            "mutated_Z_w_to_Z_w2_fails": True,
        },
    }
    certificate_path = PACKAGE / "CERTIFICATE.json"
    if args.write_certificate:
        certificate_path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        stored = json.loads(certificate_path.read_text())
        need(stored == cert, "recomputed result differs from CERTIFICATE.json")
    print("PASS_UT3_F4_CENTRAL_PAIR", json.dumps(cert, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
