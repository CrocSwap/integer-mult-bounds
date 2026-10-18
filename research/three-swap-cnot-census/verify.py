#!/usr/bin/env python3
"""Exact three-swap census over F2[GL_2(F2)]; standard library only.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. No implementation is imported from a predecessor package.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GROUP = tuple(itertools.permutations(range(3)))
GROUP_INDEX = {p: i for i, p in enumerate(GROUP)}
MUL = tuple(tuple(GROUP_INDEX[tuple(p[q[x]] for x in range(3))]
                  for q in GROUP) for p in GROUP)
E = GROUP_INDEX[(0, 1, 2)]
A = GROUP_INDEX[(0, 2, 1)]
B = GROUP_INDEX[(2, 1, 0)]
S = MUL[MUL[A][B]][A]
IDENTITY = sum(1 << (6 * (3 * i + i) + E) for i in range(3))
TARGET = sum(1 << (6 * (3 * i + i) + S) for i in range(3))
ROW_MASK = (1 << 18) - 1
PROJECTORS = tuple((u, v) for u in range(1, 8) for v in range(1, 8)
                   if (u & v).bit_count() % 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_independent():
    spec = importlib.util.spec_from_file_location(
        "three_swap_independent", PACKAGE / "independent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coefficient_product(x, y):
    result = 0
    for i in range(6):
        for j in range(6):
            if (x >> i) & (y >> j) & 1:
                result ^= 1 << MUL[i][j]
    return result


def formal_product(left, right):
    """Unoptimized full formal matrix multiplication, used for controls."""
    result = 0
    for i in range(3):
        for j in range(3):
            value = 0
            for k in range(3):
                value ^= coefficient_product(
                    (left >> (6 * (3 * i + k))) & 63,
                    (right >> (6 * (3 * k + j))) & 63)
            result |= value << (6 * (3 * i + j))
    return result


def factor(g, u, v, *, validate=True):
    if validate:
        require(g in (A, B), "address label outside a/b alphabet")
        require((u, v) in PROJECTORS, "not a rank-one scalar idempotent")
    result = IDENTITY
    for i in range(3):
        for j in range(3):
            if (u >> i) & (v >> j) & 1:
                result ^= ((1 << E) ^ (1 << g)) << (6 * (3 * i + j))
    return result


def word_product(word):
    result = IDENTITY
    for g, u, v in word:
        result = formal_product(result, factor(g, u, v))
    return result


def direct_word(swaps=3):
    return tuple((g, 1 << i, 1 << i) for i in range(swaps)
                 for g in (A, B, A))


def diagonal_target(swaps):
    return sum(1 << (6 * (3 * i + i) + (S if i < swaps else E))
               for i in range(3))


def permute_coefficient(value, label):
    return sum(((value >> h) & 1) << MUL[h][label] for h in range(6))


def right_target(word, swaps=3):
    """Right multiplication by the complete diagonal swap target."""
    return sum((permute_coefficient((word >> (6 * j)) & 63, S)
                if j % 3 < swaps else (word >> (6 * j)) & 63) << (6 * j)
               for j in range(9))


def transition_tables():
    selectors = {u: bytearray(1 << 18) for u in range(1, 8)}
    for row in range(1 << 18):
        x, y, z = row & 63, (row >> 6) & 63, row >> 12
        for u in range(1, 8):
            selectors[u][row] = ((x if u & 1 else 0)
                                 ^ (y if u & 2 else 0)
                                 ^ (z if u & 4 else 0))
    tables = []
    for g in (A, B):
        for u, v in PROJECTORS:
            delta = []
            for c in range(64):
                d = c ^ permute_coefficient(c, g)
                delta.append(sum(d << (6 * j) for j in range(3)
                                 if (v >> j) & 1))
            tables.append((selectors[u], delta))
    return tables


def apply_table(word, table):
    pick, delta = table
    return (word ^ delta[pick[word & ROW_MASK]]
            ^ (delta[pick[(word >> 18) & ROW_MASK]] << 18)
            ^ (delta[pick[word >> 36]] << 36))


def formal_census(radius=4):
    require(0 <= radius <= 4, "registered census radius must be 0..4")
    tables = transition_tables()
    seen = {IDENTITY}
    levels = [seen.copy()]
    attempts = []
    for _ in range(radius):
        new = set()
        attempts.append(len(levels[-1]) * len(tables))
        for word in levels[-1]:
            r0, r1, r2 = word & ROW_MASK, (word >> 18) & ROW_MASK, word >> 36
            for pick, delta in tables:
                state = (word ^ delta[pick[r0]] ^ (delta[pick[r1]] << 18)
                         ^ (delta[pick[r2]] << 36))
                if state not in seen:
                    new.add(state)
        seen.update(new)
        levels.append(new)
    return levels, attempts


def to_regular_tables():
    """Faithful left regular image, 18 rows of 18 bits (324 bits)."""
    tables = []
    for i in range(3):
        for j in range(3):
            contributions = []
            for c in range(64):
                matrix = 0
                for g in range(6):
                    if (c >> g) & 1:
                        for h in range(6):
                            matrix ^= 1 << (18 * (6 * i + MUL[g][h]) + 6 * j + h)
                contributions.append(matrix)
            tables.append(contributions)
    return tables


def to_regular(word, tables):
    result = 0
    for j in range(9):
        result ^= tables[j][(word >> (6 * j)) & 63]
    return result


def same_states(formal, regular, tables):
    require(len(formal) == len(regular), "independent layer cardinality differs")
    require({to_regular(w, tables) for w in formal} == regular,
            "independent full state sets differ")


def state_digest(states, width):
    digest = hashlib.sha256()
    for value in sorted(states):
        digest.update(value.to_bytes(width, "little"))
    return digest.hexdigest()


def sign(g):
    p = GROUP[g]
    return sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3)) % 2


def augmentation(word):
    return sum((((word >> (6 * j)) & 63).bit_count() % 2) << j
               for j in range(9))


def controls(independent, tables):
    names = []
    word = direct_word()
    require(word_product(word) == TARGET, "nine-call positive witness failed")
    for j in range(9):
        require(word_product(word[:j] + word[j + 1:]) != TARGET,
                "omitted-call mutation accepted")
        names.append(f"omit_call_{j}")
    for j, (g, u, v) in enumerate(word):
        altered = word[:j] + ((B if g == A else A, u, v),) + word[j + 1:]
        require(word_product(altered) != TARGET, "wrong-label mutation accepted")
        names.append(f"wrong_label_{j}")
    require(diagonal_target(2) != TARGET, "third dirty input was ignored")
    names.append("omit_third_target")
    scalar_cnot = IDENTITY ^ (1 << (6 * 1 + E))
    residual = formal_product(TARGET, scalar_cnot)
    require(residual != TARGET and augmentation(residual) != augmentation(TARGET),
            "nonidentity free scalar residue accepted")
    names.append("scalar_residue")
    for bad in ((S, 1, 1), (A, 1, 2)):
        try:
            factor(*bad)
        except ValueError:
            pass
        else:
            raise ValueError("illegal generator accepted")
    names.extend(["expanded_address_alphabet", "nonidempotent_scalar"])
    bulk_a = sum(1 << (6 * (3 * i + i) + A) for i in range(3))
    bulk_b = sum(1 << (6 * (3 * i + i) + B) for i in range(3))
    allowed = {factor(g, u, v) for g in (A, B) for u, v in PROJECTORS}
    require(bulk_a not in allowed and bulk_b not in allowed,
            "rank-three projector underpriced")
    require(formal_product(formal_product(bulk_a, bulk_b), bulk_a) == TARGET,
            "rank-three scope control was not a real counterexample")
    names.append("rank_three_underpricing")
    natural_sum = 0
    for matrix in independent.address_group():
        natural_sum ^= matrix[0] | (matrix[1] << 2)
    require(natural_sum == 0, "natural-image kernel control changed")
    false_identity = IDENTITY ^ (63 << 6)
    require(false_identity != IDENTITY
            and to_regular(false_identity, tables) != to_regular(IDENTITY, tables)
            and augmentation(false_identity) == augmentation(IDENTITY),
            "nonfaithful representation accepted a false formal identity")
    names.append("natural_representation_kernel")
    require(formal_product(factor(A, 1, 1), factor(B, 1, 1))
            != formal_product(factor(B, 1, 1), factor(A, 1, 1)),
            "address multiplication incorrectly commutes")
    names.append("noncommuting_order")
    return names


def check_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    for item in manifest["files"]:
        if item["usage"] == "input":
            require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
                    == item["sha256"], "live source pin mismatch: " + item["path"])
            checked.append(item["path"])
    require(checked, "live source inventory is empty")
    return checked


def compare_receipt(actual, expected):
    require(actual == expected, "computed receipt differs from EXPECTED.json")


def compute():
    check_inputs()
    independent = load_independent()
    tables = to_regular_tables()
    require(len(PROJECTORS) == 28, "projector inventory")
    require(all(sign(MUL[g][h]) == (sign(g) ^ sign(h))
                for g in range(6) for h in range(6)), "sign is not a homomorphism")
    require(all(sign(g) == 1 for g in (A, B, S)), "wrong sign labels")
    require(all((u & v).bit_count() % 2 == 1 for u, v in PROJECTORS), "trace parity")
    require(augmentation(TARGET) == augmentation(IDENTITY), "target augmentation")
    formal, attempts = formal_census()
    regular, regular_attempts, dense_checks = independent.census()
    require(attempts == regular_attempts, "transition attempt coverage differs")
    for x, y in zip(formal, regular, strict=True):
        same_states(x, y, tables)
    require(to_regular(TARGET, tables) == independent.target(), "target binding")
    ball4 = set().union(*formal)
    ball3 = set().union(*formal[:4])
    meet_counts = [sum(right_target(x) in ball4 for x in layer)
                   for layer in formal[:4]]
    require(sum(meet_counts) == 0, "found a word of length at most seven")
    reg_ball4 = set().union(*regular)
    reg_target = independent.target()
    reg_meets = [sum(independent.multiply(x, reg_target) in reg_ball4 for x in layer)
                 for layer in regular[:4]]
    require(reg_meets == meet_counts, "independent target intersections differ")
    minimum_controls = []
    for swaps in (0, 1, 2):
        best = 99
        for d, layer in enumerate(formal[:4]):
            for state in layer:
                other = right_target(state, swaps)
                for f, second in enumerate(formal[:4]):
                    if other in second:
                        best = min(best, d + f)
        require(best == 3 * swaps, "positive minimum control failed")
        require(word_product(direct_word(swaps)) == diagonal_target(swaps),
                "positive formal boundary failed")
        minimum_controls.append(best)
    names = controls(independent, tables)
    return {
        "schema_version": 1,
        "status": "PASS_THREE_SWAP_CNOT_CENSUS",
        "registers": 3,
        "active_swaps": 3,
        "extra_dirty_registers": 0,
        "minimum_paid_calls": 9,
        "formal_group_order": [list(p) for p in GROUP],
        "rank_one_idempotents": len(PROJECTORS),
        "paid_generators": 2 * len(PROJECTORS),
        "exact_distance_layers": [len(x) for x in formal],
        "transition_attempts_by_depth": attempts,
        "ball_radius_three": len(ball3),
        "ball_radius_four": len(ball4),
        "target_intersections_by_left_distance": meet_counts,
        "independent_target_intersections": reg_meets,
        "formal_layer_sha256_7byte_little_endian": [state_digest(x, 7) for x in formal],
        "regular_layer_sha256_41byte_little_endian": [state_digest(x, 41) for x in regular],
        "independent_full_state_sets_equal": True,
        "independent_dense_transition_checks": dense_checks,
        "parity_homomorphism_products": 36,
        "permitted_call_count_parity": "odd",
        "positive_minimum_controls": minimum_controls,
        "semantic_controls": names,
        "scope": "Finite certificate: exactly three registers in the stated formal alphabet; no new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the computed receipt without writing files")
    args = parser.parse_args()
    receipt = compute()
    compare_receipt(receipt, json.loads((PACKAGE / "EXPECTED.json").read_text()))
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print("PASS_THREE_SWAP_CNOT_CENSUS minimum=9 registers=3 "
              f"ball3={receipt['ball_radius_three']} ball4={receipt['ball_radius_four']} "
              f"meet=0 controls={len(receipt['semantic_controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
