#!/usr/bin/env python3
"""Independent set-based replay of the finite F2[Q8] exclusion."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CORE_PATH = PACKAGE / "core.py"
SPEC = importlib.util.spec_from_file_location("q8_core_for_verifier", CORE_PATH)
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


# Literal Cayley table in the label order 1,i,j,k,-1,-i,-j,-k.
Q8 = (
    (0, 1, 2, 3, 4, 5, 6, 7),
    (1, 4, 3, 6, 5, 0, 7, 2),
    (2, 7, 4, 1, 6, 3, 0, 5),
    (3, 2, 5, 4, 7, 6, 1, 0),
    (4, 5, 6, 7, 0, 1, 2, 3),
    (5, 0, 7, 2, 1, 4, 3, 6),
    (6, 3, 0, 5, 2, 7, 4, 1),
    (7, 6, 1, 0, 3, 2, 5, 4),
)


def xor_sets(left: set[int], right: set[int]) -> set[int]:
    return left.symmetric_difference(right)


def reference_factor(N: tuple[int, ...], group_label: int) -> tuple[frozenset[int], ...]:
    entries = []
    for row in range(3):
        for col in range(3):
            terms = {0} if row == col else set()
            if N[3 * row + col]:
                terms.symmetric_difference_update((0, group_label))
            entries.append(frozenset(terms))
    return tuple(entries)


def reference_product(A: tuple[frozenset[int], ...],
                      B: tuple[frozenset[int], ...]) -> tuple[frozenset[int], ...]:
    out = []
    for row in range(3):
        for col in range(3):
            entry: set[int] = set()
            for pivot in range(3):
                for a in A[3 * row + pivot]:
                    for b in B[3 * pivot + col]:
                        entry.symmetric_difference_update((Q8[a][b],))
            out.append(frozenset(entry))
    return tuple(out)


def masks(matrix: tuple[frozenset[int], ...]) -> tuple[int, ...]:
    return tuple(sum(1 << label for label in entry) for entry in matrix)


def idempotent_family() -> list[tuple[int, ...]]:
    family = []
    for x in range(1, 8):
        for y in range(8):
            if (x & y).bit_count() & 1:
                family.append(tuple(((x >> r) & 1) * ((y >> c) & 1)
                                    for r in range(3) for c in range(3)))
    require(len(family) == 28 and len(set(family)) == 28,
            "the rank-one idempotent alphabet must contain 28 distinct matrices")
    for N in family:
        for r in range(3):
            for c in range(3):
                value = 0
                for k in range(3):
                    value ^= N[3 * r + k] & N[3 * k + c]
                require(value == N[3 * r + c], "enumerated matrix is not idempotent")
    return family


def replay() -> dict:
    family = idempotent_family()
    target = tuple(frozenset((1,)) if (r, c) == (0, 0) else
                   frozenset((2,)) if (r, c) == (1, 1) else
                   frozenset((3,)) if (r, c) == (2, 2) else frozenset()
                   for r in range(3) for c in range(3))
    histogram: Counter[int] = Counter()
    digest = hashlib.sha256()
    hits = 0
    for left_index, N in enumerate(family):
        for g in range(1, 8):
            A = reference_factor(N, g)
            for right_index, M in enumerate(family):
                for h in range(1, 8):
                    output = reference_product(A, reference_factor(M, h))
                    output_masks = masks(output)
                    target_masks = masks(target)
                    distance = sum((a ^ b).bit_count()
                                   for a, b in zip(output_masks, target_masks))
                    histogram[distance] += 1
                    hits += distance == 0
                    digest.update(bytes((left_index, g, right_index, h)))
                    digest.update(bytes(output_masks))
    return {
        "alphabet_words": sum(histogram.values()),
        "idempotents": len(family),
        "nonidentity_group_labels": 7,
        "target_hits": hits,
        "minimum_coefficient_hamming_distance": min(histogram),
        "distance_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "ordered_word_output_sha256": digest.hexdigest(),
    }


def replay_one_call() -> dict:
    family = idempotent_family()
    target = tuple(frozenset((1,)) if (r, c) == (0, 0) else
                   frozenset((2,)) if (r, c) == (1, 1) else
                   frozenset((3,)) if (r, c) == (2, 2) else frozenset()
                   for r in range(3) for c in range(3))
    histogram: Counter[int] = Counter()
    digest = hashlib.sha256()
    hits = 0
    for index, N in enumerate(family):
        for g in range(1, 8):
            output_masks = masks(reference_factor(N, g))
            distance = sum((a ^ b).bit_count()
                           for a, b in zip(output_masks, masks(target)))
            histogram[distance] += 1
            hits += distance == 0
            digest.update(bytes((index, g)))
            digest.update(bytes(output_masks))
    return {
        "alphabet_words": sum(histogram.values()),
        "idempotents": len(family),
        "nonidentity_group_labels": 7,
        "target_hits": hits,
        "minimum_coefficient_hamming_distance": min(histogram),
        "distance_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "ordered_word_output_sha256": digest.hexdigest(),
    }


def main() -> None:
    CORE.load_pins()
    # Cross-check all 64 entries and the defining quaternion relations.
    for a in range(8):
        for b in range(8):
            require(CORE.qmul(a, b) == Q8[a][b], "Q8 multiplication table mismatch")
    require(Q8[1][1] == Q8[2][2] == Q8[3][3] == 4,
            "i^2=j^2=k^2=-1 control failed")
    require(Q8[1][2] == Q8[3][0] and Q8[2][1] == Q8[7][0],
            "ij=k and ji=-k controls failed")
    for a in range(8):
        for b in range(8):
            for c in range(8):
                require(Q8[Q8[a][b]][c] == Q8[a][Q8[b][c]],
                        "literal Q8 table is not associative")

    family = idempotent_family()
    direct = reference_product(
        reference_product(reference_factor(tuple(int(i == 0) for i in range(9)), 1),
                          reference_factor(tuple(int(i == 4) for i in range(9)), 2)),
        reference_factor(tuple(int(i == 8) for i in range(9)), 3))
    expected_target = tuple(frozenset((1,)) if (r, c) == (0, 0) else
                            frozenset((2,)) if (r, c) == (1, 1) else
                            frozenset((3,)) if (r, c) == (2, 2) else frozenset()
                            for r in range(3) for c in range(3))
    require(direct == expected_target, "three-call diagonal positive control failed")
    require(masks(direct) == CORE.target(), "reference and packaged target encodings differ")

    receipt = replay()
    result = json.loads((PACKAGE / "RESULT.json").read_text())
    one_call = replay_one_call()
    require(one_call == result["one_call_domain"], "independent one-call receipt mismatch")
    require(one_call["alphabet_words"] == 196 and one_call["target_hits"] == 0,
            "one-call alphabet exclusion failed")
    require(receipt == result["two_call_domain"], "independent exhaustive receipt mismatch")
    require(receipt["alphabet_words"] == 38_416, "two-call alphabet not fully covered")
    require(receipt["target_hits"] == 0, "two-call target word found")
    require(receipt["minimum_coefficient_hamming_distance"] == 2,
            "reported nearest-output control changed")
    require(result["direct_positive_control_calls"] == 3,
            "positive-control call count changed")

    # A non-idempotent rank-one matrix is outside the paid alphabet.
    try:
        CORE.validate_idempotent((0, 1, 0, 0, 0, 0, 0, 0, 0))
    except ValueError:
        pass
    else:
        raise ValueError("non-idempotent control was accepted")
    print("PASS_Q8_TWO_CALL_EXCLUSION",
          f"words={receipt['alphabet_words']}",
          f"hits={receipt['target_hits']}",
          f"min_hamming={receipt['minimum_coefficient_hamming_distance']}",
          f"one_call_hits={one_call['target_hits']}",
          "Q8_table=64 associative_triples=512 direct_calls=3",
          f"sha256={receipt['ordered_word_output_sha256']}")


if __name__ == "__main__":
    main()
