#!/usr/bin/env python3
"""Exact screen for a six-call word after one rational address extension."""

from fractions import Fraction
from functools import lru_cache
from itertools import permutations
import json
from pathlib import Path


IDENTITY = 0x8421
SEED = "0d9888a62e4721895567ab6fd3af5262"
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
CATALOG_SHA256 = "d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def add2(a, b):
    return [[a[i][j] + b[i][j] for j in range(2)] for i in range(2)]


def scale2(k, a):
    return [[k * a[i][j] for j in range(2)] for i in range(2)]


def det2(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def outer2(left, right):
    return [[left[i] * right[j] for j in range(2)] for i in range(2)]


def det3(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def rank2_mod2(a):
    entries = [[int(a[i][j]) & 1 for j in range(2)] for i in range(2)]
    if not any(value for row in entries for value in row):
        return 0
    determinant = (entries[0][0] * entries[1][1] -
                   entries[0][1] * entries[1][0]) & 1
    return 1 if determinant == 0 else 2


def linear_combo(coefficients, matrices):
    return [[sum((coefficients[k] * matrices[k][i][j] for k in range(len(matrices))),
                 Fraction(0)) for j in range(2)] for i in range(2)]


def rational_model():
    half = Fraction(1, 2)
    quarter = Fraction(1, 4)
    frames = {
        "A": [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]],
        "B": [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]],
        "P": [[half, half], [half, half]],
        "Q": [[half, -half], [-half, half]],
        "R": [[Fraction(1), half], [half, quarter]],
    }
    factorizations = {
        "A": ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0))),
        "B": ((Fraction(0), Fraction(1)), (Fraction(0), Fraction(1))),
        "P": ((half, half), (Fraction(1), Fraction(1))),
        "Q": ((half, -half), (Fraction(1), Fraction(-1))),
        "R": ((Fraction(1), half), (Fraction(1), half)),
    }
    for label, (left, right) in factorizations.items():
        need(frames[label] == outer2(left, right), "rank-one product: " + label)
        need(det2(frames[label]) == 0 and any(map(any, frames[label])),
             "nonzero rank-one address: " + label)
    need(frames["Q"] == add2(add2(frames["A"], frames["B"]),
                              scale2(Fraction(-1), frames["P"])),
         "Q=A+B-P")
    need(scale2(Fraction(4), frames["R"]) ==
         add2(add2(scale2(Fraction(2), frames["A"]),
                   scale2(Fraction(-1), frames["B"])),
              scale2(Fraction(4), frames["P"])),
         "4R=2A-B+4P")

    # Coordinates use the integral basis (A,B,P) for the old lattice.
    old_coordinates = {
        "A": (Fraction(1), Fraction(0), Fraction(0)),
        "B": (Fraction(0), Fraction(1), Fraction(0)),
        "P": (Fraction(0), Fraction(0), Fraction(1)),
        "R": (half, -quarter, Fraction(1)),
        "Q": (Fraction(1), Fraction(1), Fraction(-1)),
    }
    old_basis = (frames["A"], frames["B"], frames["P"])
    for label, coordinates in old_coordinates.items():
        need(linear_combo(coordinates, old_basis) == frames[label],
             "old-lattice coordinates: " + label)
    coordinate_matrix = [
        [old_coordinates[label][i] for label in ("A", "P", "R")]
        for i in range(3)
    ]
    need(det3(coordinate_matrix) == Fraction(1, 4),
         "index-four over-lattice determinant")
    need(all(not all((k * value).denominator == 1
                     for value in old_coordinates["R"])
             for k in (1, 2, 3)),
         "R must not enter the old lattice at multipliers 1, 2, or 3")
    need(all((4 * value).denominator == 1 for value in old_coordinates["R"]),
         "4R must belong to the old lattice")

    # Coordinates now use the integral basis (A,P,R) of the extended lattice.
    coordinates = {
        "A": (1, 0, 0),
        "P": (0, 1, 0),
        "R": (0, 0, 1),
        "B": (2, 4, -4),
        "Q": (3, 3, -4),
    }
    need(linear_combo((Fraction(2), Fraction(4), Fraction(-4)),
                      (frames["A"], frames["P"], frames["R"])) == frames["B"],
         "B coordinates in extended lattice")
    need(linear_combo((Fraction(3), Fraction(3), Fraction(-4)),
                      (frames["A"], frames["P"], frames["R"])) == frames["Q"],
         "Q coordinates in extended lattice")

    target_coordinates = ((1, 1, 0), (4, 3, -4), (2, 5, -4), (5, 7, -8))
    target_pairs = (("A", "P"), ("A", "Q"), ("B", "P"), ("B", "Q"))
    targets = []
    basis = (frames["A"], frames["P"], frames["R"])
    for coefficients, pair in zip(target_coordinates, target_pairs):
        target = linear_combo(tuple(Fraction(x) for x in coefficients), basis)
        need(target == add2(frames[pair[0]], frames[pair[1]]),
             "target coordinate and legal direct pair")
        need(det2(target) == half, "rank-two target determinant")
        targets.append(target)
    need(all((4 * value).denominator == 1
             for frame in frames.values() for row in frame for value in row),
         "frame denominator-four clearing")
    need(any((2 * value).denominator != 1 for row in frames["R"] for value in row),
         "R requires an even frame-clearing denominator")
    need(any((value).denominator != 1 for target in targets
             for row in target for value in row),
         "target clear denominator is not one")
    cleared_target_ranks = []
    for target in targets:
        cleared = scale2(Fraction(2), target)
        need(all(value.denominator == 1 for row in cleared for value in row),
             "target denominator-two clearing")
        need(det2(cleared) == 2 and rank2_mod2(cleared) == 1,
             "target clearing is singular of rank one modulo two")
        cleared_target_ranks.append(rank2_mod2(cleared))
    return frames, coordinates, target_coordinates, targets, tuple(cleared_target_ranks)


def rank4(matrix):
    rows = [(matrix >> (4 * i)) & 15 for i in range(4)]
    rank = 0
    for col in range(4):
        pivot = next((i for i in range(rank, 4) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(4):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def trace4(matrix):
    return sum((matrix >> (5 * i)) & 1 for i in range(4)) & 1


def floor4(matrix):
    rank = rank4(matrix)
    return rank + ((rank - trace4(matrix)) & 1)


def diagonal_mask(bits_by_role):
    return sum(1 << (5 * i) for i, bit in enumerate(bits_by_role) if bit & 1)


def first_order_screen(target_coordinates):
    masks = tuple(diagonal_mask([row[j] for row in target_coordinates])
                  for j in range(3))
    need(masks == (0x8001, 0x8421, 0), "extended-lattice target masks")
    visible = [floor4(s) + floor4(s ^ masks[0]) + floor4(s ^ masks[1])
               for s in range(1 << 16)]
    visible_floor = min(visible)
    visible_minimizers = tuple(i for i, value in enumerate(visible)
                               if value == visible_floor)
    need((visible_floor, visible_minimizers) == (4, (0x8001,)),
         "unique minimum visible aggregate mask")

    # When no R call occurs, the generated subgroup is the old basis (A,B,P).
    # Recompute its first-order rank/trace floor instead of assuming the extension.
    old_masks = (0x8001, 0x0420, 0x8421)
    old_values = [floor4(s) + floor4(s ^ old_masks[0]) +
                  floor4(s ^ old_masks[1]) + floor4(s ^ old_masks[2])
                  for s in range(1 << 16)]
    need(min(old_values) == 8, "no-R first-order floor")
    return masks, visible_floor, visible_minimizers, min(old_values)


@lru_cache(maxsize=500_000)
def mmul(a, b):
    out = 0
    cols = [sum(((b >> (4 * k + j)) & 1) << k for k in range(4))
            for j in range(4)]
    for i in range(4):
        row = (a >> (4 * i)) & 15
        for j in range(4):
            if (row & cols[j]).bit_count() & 1:
                out |= 1 << (4 * i + j)
    return out


def projectors():
    result = []
    for u in range(1, 16):
        for v in range(1, 16):
            if (u & v).bit_count() & 1:
                matrix = sum((((u >> i) & 1) * ((v >> j) & 1)) << (4 * i + j)
                             for i in range(4) for j in range(4))
                need(rank4(matrix) == 1 and trace4(matrix) == 1 and
                     mmul(matrix, matrix) == matrix,
                     "generated rank-one idempotent")
                result.append(matrix)
    need(len(result) == 120 and len(set(result)) == 120,
         "complete rank-one idempotent alphabet")
    return tuple(result)


LABEL_EXPONENT = {
    "A": (1, 0, 0),
    "P": (0, 1, 0),
    "R": (0, 0, 1),
    "B": (2, 4, -4),
    "Q": (3, 3, -4),
}


def plus3(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def factor_poly(label, projector):
    # Over F2, I+([F]-1)N = (I+N) + [F]N.
    constant = IDENTITY ^ projector
    result = {}
    if constant:
        result[(0, 0, 0)] = constant
    result[LABEL_EXPONENT[label]] = projector
    return result


def multiply_factor(poly, factor):
    result = {}
    for exponent, left in poly.items():
        for increment, right in factor.items():
            key = plus3(exponent, increment)
            product = mmul(left, right)
            if product:
                result[key] = result.get(key, 0) ^ product
                if not result[key]:
                    del result[key]
    return result


def word_poly(word):
    result = {(0, 0, 0): IDENTITY}
    for label, projector in word:
        result = multiply_factor(result, factor_poly(label, projector))
    return result


def target_poly(target_coordinates):
    return {tuple(exponent): 1 << (5 * role)
            for role, exponent in enumerate(target_coordinates)}


def pair_decompositions(projector_list, total):
    return tuple((i, j) for i in range(len(projector_list))
                 for j in range(i, len(projector_list))
                 if projector_list[i] ^ projector_list[j] == total)


def exact_six_search(projector_list, target):
    pa = 0x8001
    pp = 0x8421
    q_pairs = pair_decompositions(projector_list, pa)
    p_pairs = pair_decompositions(projector_list, pa ^ pp)
    r_pairs = pair_decompositions(projector_list, 0)
    need((len(q_pairs), len(p_pairs), len(r_pairs)) == (3, 3, 120),
         "complete projector-pair decomposition counts")

    checked = 0
    found = None
    for qi, qj in q_pairs:
        for pi, pj in p_pairs:
            for ri, rj in r_pairs:
                factors = (("Q", projector_list[qi]), ("Q", projector_list[qj]),
                           ("P", projector_list[pi]), ("P", projector_list[pj]),
                           ("R", projector_list[ri]), ("R", projector_list[rj]))
                for word in sorted(set(permutations(factors))):
                    checked += 1
                    if word_poly(word) == target:
                        found = word
                        break
                if found is not None:
                    break
            if found is not None:
                break
        if found is not None:
            break
    expected = len(q_pairs) * len(p_pairs) * len(r_pairs) * 360
    need(checked == expected == 388800, "complete six-call candidate coverage")
    need(found is None, "a six-call word exists")
    return q_pairs, p_pairs, r_pairs, checked


def main():
    frames, coordinates, target_coordinates, targets, target_clear_ranks = rational_model()
    masks, visible_floor, minimizers, no_r_floor = first_order_screen(target_coordinates)
    ps = projectors()
    target = target_poly(target_coordinates)

    # The direct legal eight-call word is a positive control.
    diagonal_projectors = (0x0001, 0x0020, 0x0400, 0x8000)
    direct = []
    for role, pair in enumerate((("A", "P"), ("A", "Q"),
                                 ("B", "P"), ("B", "Q"))):
        direct.extend((label, diagonal_projectors[role]) for label in pair)
    need(len(direct) == 8 and word_poly(tuple(direct)) == target,
         "direct eight-call positive control")

    # Dropping one output monomial must be detected by exact group-algebra equality.
    mutant = dict(target)
    mutant.pop(target_coordinates[3])
    need(word_poly(tuple(direct)) != mutant,
         "dropped-output negative control")

    q_pairs, p_pairs, r_pairs, checked = exact_six_search(ps, target)
    computed = {
        "schema_version": 1,
        "selection": {
            "seed": SEED,
            "track": "bit-mechanisms",
            "task_id": "bit-new-register-model",
            "scope_key": "7f5f4426ef796683c485",
            "priority_revision": 4,
            "catalogue_sha256": CATALOG_SHA256,
            "base_commit": BASE,
            "selected_record_sha256": SELECTED_SHA256,
        },
        "model": {
            "coefficient_field": "F2",
            "group_algebra": "F2[Z A + Z P + Z R]",
            "registers": 4,
            "free_binary_role_mixing": True,
            "labels": ["A", "B", "P", "Q", "R"],
            "extended_lattice_basis": ["A", "P", "R"],
            "label_coordinates": {key: list(value) for key, value in coordinates.items()},
            "address_relation": "4R=2A-B+4P; B=2A+4P-4R; Q=3A+3P-4R",
            "frame_clear_denominator": 4,
            "minimal_target_clear_denominator": 2,
            "target_clear_mod2_ranks": list(target_clear_ranks),
            "rank_one_idempotents": len(ps),
            "paid_factor": "I+([F]-1)N for a label F and any rank-one idempotent N in M4(F2)",
            "target": "diag([A+P],[A+Q],[B+P],[B+Q])",
            "target_coordinates": [list(row) for row in target_coordinates],
            "target_matrices": [[[str(x) for x in row] for row in matrix]
                                for matrix in targets],
        },
        "cost": {
            "direct_calls": 8,
            "six_call_saving_if_constructed": 2,
            "first_order_global_floor": 6,
            "after_six_call_obstruction_floor": 7,
            "exact_minimum_claimed": False,
            "frame_addition_precision_and_supplier_costs": "not included; no supplier or kappa transfer",
        },
        "first_order": {
            "target_masks_hex_A_P_R": [f"{mask:04x}" for mask in masks],
            "visible_A_P_Q_floor": visible_floor,
            "visible_minimizer_S_Q_hex": [f"{value:04x}" for value in minimizers],
            "no_R_old_alphabet_floor": no_r_floor,
            "mask_states": 65536,
        },
        "six_call_search": {
            "Q_pair_decompositions": len(q_pairs),
            "P_pair_decompositions": len(p_pairs),
            "R_equal_pair_choices": len(r_pairs),
            "orderings_per_projector_choice": 360,
            "candidate_words": checked,
            "words_checked": checked,
            "target_word_found": False,
            "scope": "all six-call words admitted by the unique first-order minimum; not a search of seven-call words",
        },
        "controls": {
            "direct_eight_call_word": "PASS",
            "dropped_output_mutation_detected": "PASS",
            "even_denominator_target_clear_mod2_singular": "PASS",
        },
        "selected_supplier_or_kappa_claimed": False,
    }
    certificate_path = Path(__file__).with_name("CERTIFICATE.json")
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    need(certificate == computed, "static certificate differs from exact replay")
    print("PASS_FIFTH_RATIONAL_FRAME_NO_SIX_CALL_WORD "
          "visible_floor=4 global_floor=6 no_R_floor=8 "
          "projectors=120 candidates=388800 checked=388800 "
          "direct_calls=8 no_six=>calls_at_least_7")


if __name__ == "__main__":
    main()
