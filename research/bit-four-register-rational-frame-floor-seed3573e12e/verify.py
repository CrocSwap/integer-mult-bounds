#!/usr/bin/env python3
"""Exact rank/trace first-order floor for one four-register rational target."""

from fractions import Fraction
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CERTIFICATE = json.loads((ROOT / "CERTIFICATE.json").read_text(encoding="utf-8"))
TASK = json.loads((ROOT / "TASK.json").read_text(encoding="utf-8"))


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_RATIONAL_FRAME_FLOOR " + message)


def outer2(x, y):
    return [[x[i] * y[j] for j in range(2)] for i in range(2)]


def add2(left, right):
    return [[left[i][j] + right[i][j] for j in range(2)] for i in range(2)]


def det2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def eq2(left, right):
    return all(left[i][j] == right[i][j] for i in range(2) for j in range(2))


def bit_matrix(u, v, width=4):
    value = 0
    for i in range(width):
        for j in range(width):
            if (u >> i) & 1 and (v >> j) & 1:
                value |= 1 << (width * i + j)
    return value


def rank4(value):
    rows = [(value >> (4 * i)) & 15 for i in range(4)]
    rank = 0
    for column in range(4):
        pivot = next((r for r in range(rank, 4) if (rows[r] >> column) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(4):
            if r != rank and ((rows[r] >> column) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def multiply4(left, right):
    value = 0
    for i in range(4):
        for j in range(4):
            parity = 0
            for k in range(4):
                parity ^= ((left >> (4 * i + k)) & 1) & ((right >> (4 * k + j)) & 1)
            if parity:
                value |= 1 << (4 * i + j)
    return value


def trace4(value):
    return sum((value >> (5 * i)) & 1 for i in range(4)) & 1


def diagonal4(roles):
    value = 0
    for i in range(4):
        if (roles >> i) & 1:
            value |= 1 << (5 * i)
    return value


def rank_trace_floor(value):
    rank = rank4(value)
    return rank + ((rank ^ trace4(value)) & 1)


def relaxation(pa, pb, pp):
    best = 99
    minimizers = []
    for s_q in range(1 << 16):
        cost = (rank_trace_floor(s_q) + rank_trace_floor(s_q ^ pa)
                + rank_trace_floor(s_q ^ pb) + rank_trace_floor(s_q ^ pp))
        if cost < best:
            best = cost
            minimizers = [s_q]
        elif cost == best:
            minimizers.append(s_q)
    return best, minimizers


def main():
    selection = {
        "seed": "3573e12e06106f693177ed189d2a8b8e",
        "track": "bit-mechanisms",
        "task_id": "bit-new-register-model",
        "scope_key": "7084092dd726e7ba1f2f",
        "priority_revision": 4,
        "catalog_sha256": "d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7",
        "base_commit": "7c1e7811c730b17fe0eeef6c82ef011318b0465e",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    }
    need(TASK["selection"] == selection and CERTIFICATE["selection"] == selection,
         "seed or selected-source pins")
    need(TASK["base_commit"] == selection["base_commit"]
         and TASK["task_id"] == selection["task_id"]
         and TASK["priority_revision"] == selection["priority_revision"],
         "task selection metadata")
    refreshed = TASK.get("upstream_refresh", {})
    need(refreshed.get("canonical_main_commit") ==
         "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
         and refreshed.get("priority_revision") == 4
         and refreshed.get("catalog_sha256") == selection["catalog_sha256"]
         and refreshed.get("selected_record_sha256") == selection["selected_record_sha256"],
         "pre-submission canonical-main freshness record")
    half = Fraction(1, 2)
    frames = {
        "A": [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]],
        "B": [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]],
        "P": [[half, half], [half, half]],
        "Q": [[half, -half], [-half, half]],
    }
    factorizations = {
        "A": ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(0))),
        "B": ((Fraction(0), Fraction(1)), (Fraction(0), Fraction(1))),
        "P": ((half, half), (Fraction(1), Fraction(1))),
        "Q": ((half, -half), (Fraction(1), Fraction(-1))),
    }
    for label, (left, right) in factorizations.items():
        need(eq2(frames[label], outer2(left, right)),
             "rank-one product representation: " + label)
    need(eq2(frames["Q"], add2(add2(frames["A"], frames["B"]),
                                    [[-x for x in row] for row in frames["P"]])),
         "Q != A+B-P over Q")
    for label, matrix in frames.items():
        need(det2(matrix) == 0, "address is not rank one: " + label)
        need(any(matrix[i][j] for i in range(2) for j in range(2)),
             "zero address: " + label)
    frame_repr = {name: [[str(value) for value in row] for row in matrix]
                  for name, matrix in frames.items()}
    need(frame_repr == CERTIFICATE["model"]["addresses"], "address matrices differ from certificate")
    need(CERTIFICATE["model"]["independent_address_rank"] == 3,
         "certificate independent address rank")

    coefficients = ((1, 0, 1), (2, 1, -1), (0, 1, 1), (1, 2, -1))
    basis = (frames["A"], frames["B"], frames["P"])
    targets = []
    for row in coefficients:
        matrix = [[sum((row[k] * basis[k][i][j] for k in range(3)), Fraction(0))
                   for j in range(2)] for i in range(2)]
        need(det2(matrix) != 0, "target is not rank two")
        targets.append(matrix)
    target_repr = [[[str(value) for value in row] for row in matrix] for matrix in targets]
    need(target_repr == CERTIFICATE["targets"]["matrices"], "target matrices differ from certificate")
    need([str(det2(matrix)) for matrix in targets] == CERTIFICATE["targets"]["determinants"],
         "target determinants differ from certificate")

    # The target is built directly from two labels in the paid address alphabet.
    direct_labels = (("A", "P"), ("A", "Q"), ("B", "P"), ("B", "Q"))
    direct_roles = []
    for role, pair in enumerate(direct_labels):
        need(eq2(add2(frames[pair[0]], frames[pair[1]]), targets[role]),
             "direct frame pair does not give target role " + str(role))
        direct_roles.extend(((role, pair[0]), (role, pair[1])))
    need(len(direct_roles) == 8, "direct bill is not eight calls")

    # The complete rank-one idempotent alphabet has 120 elements.
    projectors = set()
    for u in range(1, 16):
        for v in range(1, 16):
            if (u & v).bit_count() & 1:
                projector = bit_matrix(u, v)
                projectors.add(projector)
                need(rank4(projector) == 1, "projector rank")
                need(trace4(projector) == 1, "rank-one idempotent trace")
                need(multiply4(projector, projector) == projector,
                     "generated rank-one matrix is not idempotent")
    need(len(projectors) == 120, "rank-one idempotent alphabet cardinality")

    # First-order exponents of A,B,P,Q are (1,0,0),(0,1,0),(0,0,1),(1,1,1).
    # The target coefficient masks follow from the exact integer coordinates above.
    pa = diagonal4(0b1001)
    pb = diagonal4(0b0110)
    pp = diagonal4(0b1111)
    need((f"{pa:04x}", f"{pb:04x}", f"{pp:04x}") ==
         tuple(CERTIFICATE["first_order"]["target_masks_hex"]),
         "target parity masks")

    # Check that the direct word supplies a first-order upper control.
    sums = {name: 0 for name in frames}
    for role, label in direct_roles:
        sums[label] ^= 1 << (5 * role)
    need((sums["A"] ^ sums["Q"]) == pa, "direct A derivative")
    need((sums["B"] ^ sums["Q"]) == pb, "direct B derivative")
    need((sums["P"] ^ sums["Q"]) == pp, "direct P derivative")
    need(sum(rank_trace_floor(sums[name]) for name in frames) == 8,
         "direct first-order witness does not attain the floor")

    minimum, minimizers = relaxation(pa, pb, pp)
    masks_hex = [f"{value:04x}" for value in minimizers]
    need(minimum == 8, "relaxation minimum changed")
    need(masks_hex == CERTIFICATE["first_order"]["minimizer_s_q_masks_hex"],
         "relaxation minimizer list")

    # A mask-edit control catches the tempting but incorrect omission of role 3's P bit.
    mutant_minimum, _ = relaxation(pa, pb, diagonal4(0b0011))
    need(mutant_minimum == 6, "parity-mask mutation control")

    expected = {
        "schema_version": 1,
        "model": {
            "coefficient_field": "F2",
            "registers": 4,
            "independent_address_rank": 3,
            "address_labels": ["A", "B", "P", "Q"],
            "rank_one_idempotents": 120,
            "paid_factor_types": 480,
            "paid_factor": "I + ([F]-1)N; F in {A,B,P,Q}; N rank-one idempotent",
            "target": "diag([A+P],[A+Q],[B+P],[B+Q])",
            "addresses": {
                "A": [["1", "0"], ["0", "0"]],
                "B": [["0", "0"], ["0", "1"]],
                "P": [["1/2", "1/2"], ["1/2", "1/2"]],
                "Q": [["1/2", "-1/2"], ["-1/2", "1/2"]],
            },
            "address_relation": "Q=A+B-P",
        },
        "targets": {
            "matrices": [
                [["3/2", "1/2"], ["1/2", "1/2"]],
                [["3/2", "-1/2"], ["-1/2", "1/2"]],
                [["1/2", "1/2"], ["1/2", "3/2"]],
                [["1/2", "-1/2"], ["-1/2", "3/2"]],
            ],
            "determinants": ["1/2", "1/2", "1/2", "1/2"],
            "direct_label_pairs_by_role": [["A", "P"], ["A", "Q"], ["B", "P"], ["B", "Q"]],
        },
        "cost": {
            "direct_calls": 8,
            "exact_minimum_calls": 8,
            "candidate_saving_ruled_out": 1,
            "other_costs": "free binary role mixing in the formal model; no supplier or kappa transfer",
        },
        "first_order": {
            "target_masks_hex": ["8001", "0420", "8421"],
            "minimum_rank_trace_floor": 8,
            "minimizer_count": 64,
            "minimizer_s_q_masks_hex": masks_hex,
            "states_exhausted": 65536,
            "mutated_pp_mask_hex": "0021",
            "mutated_floor": 6,
        },
        "selection": selection,
        "selected_supplier_or_kappa_claimed": False,
    }
    need(CERTIFICATE == expected, "static certificate differs from exact replay")
    print("PASS_FOUR_REGISTER_RATIONAL_FRAME_EXACT_MINIMUM_8 "
          "projectors=120 paid_factors=480 relaxation_states=65536 "
          "min_floor=8 minimizers=64 direct_calls=8 mutated_floor=6")


if __name__ == "__main__":
    main()
