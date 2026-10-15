#!/usr/bin/env python3
"""Exact finite controls for the uniform Q8 central-minus-one call bound."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ONE = 0
MINUS_ONE = 4
I = 2
J = 1
K = 3


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def qmul(a: int, b: int) -> int:
    """Multiply Q8 elements encoded as (central sign, i-bit, j-bit)."""
    ca, aa, ba = (a >> 2) & 1, (a >> 1) & 1, a & 1
    cb, ab, bb = (b >> 2) & 1, (b >> 1) & 1, b & 1
    central = ca ^ cb ^ (aa & ab) ^ (ba & bb) ^ (ab & ba)
    return (central << 2) | ((aa ^ ab) << 1) | (ba ^ bb)


GROUP_MUL = tuple(tuple(qmul(a, b) for b in range(8)) for a in range(8))
GA_ONE = 1 << ONE
GA_MINUS_ONE = 1 << MINUS_ONE
GA_I = 1 << I
GA_J = 1 << J
X = GA_I ^ GA_ONE
Y = GA_J ^ GA_ONE
Z = GA_MINUS_ONE ^ GA_ONE


def ga_mul(a: int, b: int) -> int:
    """Multiply coefficient masks in F2[Q8]."""
    out = 0
    aa = a
    while aa:
        abit = aa & -aa
        ai = abit.bit_length() - 1
        bb = b
        while bb:
            bbit = bb & -bb
            bi = bbit.bit_length() - 1
            out ^= 1 << GROUP_MUL[ai][bi]
            bb ^= bbit
        aa ^= abit
    return out


def q8_axioms() -> str:
    need(all(GROUP_MUL[ONE][g] == g and GROUP_MUL[g][ONE] == g
             for g in range(8)), "Q8 identity")
    for g in range(8):
        need(any(GROUP_MUL[g][h] == ONE and GROUP_MUL[h][g] == ONE
                 for h in range(8)), f"Q8 inverse for {g}")
        need(GROUP_MUL[MINUS_ONE][g] == GROUP_MUL[g][MINUS_ONE],
             f"Q8 central minus-one at {g}")
    need(GROUP_MUL[I][I] == MINUS_ONE and GROUP_MUL[J][J] == MINUS_ONE,
         "Q8 square relations")
    need(GROUP_MUL[I][J] == K and GROUP_MUL[J][I] == (MINUS_ONE ^ K),
         "Q8 noncommuting generator relation")
    for a in range(8):
        for b in range(8):
            for c in range(8):
                need(GROUP_MUL[GROUP_MUL[a][b]][c]
                     == GROUP_MUL[a][GROUP_MUL[b][c]], "Q8 associativity")
    table = bytes(value for row in GROUP_MUL for value in row)
    return hashlib.sha256(table).hexdigest()


def add_basis(basis: dict[int, int], value: int) -> bool:
    """Insert one F2 vector into a highest-pivot basis."""
    x = value
    while x:
        pivot = x.bit_length() - 1
        if pivot in basis:
            x ^= basis[pivot]
        else:
            basis[pivot] = x
            return True
    return False


def in_span(basis: dict[int, int], value: int) -> bool:
    x = value
    while x:
        pivot = x.bit_length() - 1
        if pivot not in basis:
            return False
        x ^= basis[pivot]
    return True


def augmentation_quotient() -> dict[str, int]:
    J_elements = [value for value in range(256) if value.bit_count() % 2 == 0]
    need(len(J_elements) == 128, "augmentation ideal cardinality")
    square_basis: dict[int, int] = {}
    for a in J_elements:
        for b in J_elements:
            add_basis(square_basis, ga_mul(a, b))
    need(len(square_basis) == 5, "dim(J^2)=5")
    need(in_span(square_basis, Z), "z belongs to J^2")
    need(not in_span(square_basis, X), "x not in J^2")
    need(not in_span(square_basis, Y), "y not in J^2")
    need(not in_span(square_basis, X ^ Y), "x,y independent modulo J^2")
    need(ga_mul(X, X) == Z and ga_mul(Y, Y) == Z, "x^2=y^2=z")
    need(ga_mul(Z, Z) == 0, "z^2=0")
    return {"dim_J": 7, "dim_J2": len(square_basis), "dim_J_over_J2": 2}


def linear_coordinates(value: int) -> tuple[int, int]:
    """First-order coefficients in J/J^2, using Q8 -> C2 x C2."""
    a = 0
    b = 0
    for g in range(8):
        if value >> g & 1:
            a ^= (g >> 1) & 1
            b ^= g & 1
    return a, b


def matrix_add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def f2_matrix_mul(a: tuple[int, ...], b: tuple[int, ...], r: int) -> tuple[int, ...]:
    """Multiply binary matrices stored as row bitmasks."""
    out = []
    for row in a:
        value = 0
        for k in range(r):
            if (row >> k) & 1:
                value ^= b[k]
        out.append(value)
    return tuple(out)


def matrix_mul(a: tuple[int, ...], b: tuple[int, ...], r: int) -> tuple[int, ...]:
    out = [0] * (r * r)
    for i in range(r):
        for k in range(r):
            coefficient = a[i * r + k]
            if coefficient:
                for j in range(r):
                    if b[k * r + j]:
                        out[i * r + j] ^= ga_mul(coefficient, b[k * r + j])
    return tuple(out)


def matrix_rank(rows: tuple[int, ...]) -> int:
    work = list(rows)
    rank = 0
    for col in range(max((row.bit_length() for row in work), default=0)):
        pivot = next((i for i in range(rank, len(work)) if (work[i] >> col) & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(len(work)):
            if i != rank and ((work[i] >> col) & 1):
                work[i] ^= work[rank]
        rank += 1
        if rank == len(work):
            break
    return rank


def idempotents(r: int) -> tuple[tuple[int, ...], ...]:
    found = set()
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() % 2 != 1:
                continue
            found.add(tuple(v if (u >> row) & 1 else 0 for row in range(r)))
    return tuple(sorted(found))


def trace(rows: tuple[int, ...], r: int) -> int:
    return sum((rows[row] >> row) & 1 for row in range(r)) % 2


def coordinate_projection(r: int, slots: tuple[int, ...]) -> tuple[int, ...]:
    selected = set(slots)
    return tuple((1 << row) if row in selected else 0 for row in range(r))


def pair_projection_controls(r: int, Ns: tuple[tuple[int, ...], ...]) -> tuple[list[int], int]:
    rzero = (0,) * r
    decompositions = []
    checked = 0
    for p in range(r):
        for q in range(p + 1, r):
            projection = coordinate_projection(r, (p, q))
            hits = 0
            for a in Ns:
                for b in Ns:
                    if matrix_add(a, b) == projection:
                        hits += 1
                        checked += 1
                        need(f2_matrix_mul(a, b, r) == rzero, "ordered idempotent product AB must vanish")
                        need(f2_matrix_mul(b, a, r) == rzero, "ordered idempotent product BA must vanish")
            decompositions.append(hits)
            need(hits > 0, "positive pair-decomposition control")
    return decompositions, checked


def identity_matrix(r: int) -> tuple[int, ...]:
    return tuple(GA_ONE if row == col else 0 for row in range(r) for col in range(r))


def factor_matrix(label: int, n: tuple[int, ...], r: int) -> tuple[int, ...]:
    delta = (GA_I if label == "i" else GA_J) ^ GA_ONE
    return tuple((GA_ONE if row == col else 0) ^ (delta if n[row] >> col & 1 else 0)
                 for row in range(r) for col in range(r))


def target_matrix(target: tuple[int, ...], r: int) -> tuple[int, ...]:
    return tuple((1 << target[row]) if row == col else 0
                 for row in range(r) for col in range(r))


def direct_word(target: tuple[int, ...], r: int) -> list[tuple[str, tuple[int, ...]]]:
    word = []
    for slot, g in enumerate(target):
        projector = coordinate_projection(r, (slot,))
        if g == I:
            word.append(("i", projector))
        elif g == J:
            word.append(("j", projector))
        elif g == MINUS_ONE:
            word.extend((("i", projector), ("i", projector)))
        elif g == ONE:
            continue
        else:
            raise ValueError("target is outside the central-minus-one family")
    return word


def run_word(word: list[tuple[str, tuple[int, ...]]], r: int) -> tuple[int, ...]:
    value = identity_matrix(r)
    for label, n in word:
        value = matrix_mul(value, factor_matrix(label, n, r), r)
    return value


def central_targets() -> tuple[tuple[int, int, int], ...]:
    targets = set()
    for central_slot in range(3):
        other = [slot for slot in range(3) if slot != central_slot]
        for g in (I, J):
            for h in (I, J):
                value = [ONE] * 3
                value[central_slot] = MINUS_ONE
                value[other[0]] = g
                value[other[1]] = h
                targets.add(tuple(value))
    need(len(targets) == 12, "twelve distinct central-minus-one targets")
    return tuple(sorted(targets))


def target_linear_matrices(target: tuple[int, ...], r: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    arows = [0] * r
    brows = [0] * r
    for slot, g in enumerate(target):
        if g == I:
            arows[slot] = 1 << slot
        elif g == J:
            brows[slot] = 1 << slot
        else:
            need(g in (ONE, MINUS_ONE), "target group element")
    return tuple(arows), tuple(brows)


def matrix_linear_coefficients(matrix: tuple[int, ...], r: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    arows = [0] * r
    brows = [0] * r
    for row in range(r):
        for col in range(r):
            a, b = linear_coordinates(matrix[row * r + col])
            if a:
                arows[row] |= 1 << col
            if b:
                brows[row] |= 1 << col
    return tuple(arows), tuple(brows)


def source_pins() -> int:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    base = manifest["base_commit"]
    checked = 0
    for row in manifest["files"]:
        path = row["path"]
        blob = subprocess.run(["git", "rev-parse", f"{base}:{path}"], cwd=ROOT,
                              text=True, capture_output=True, check=True).stdout.strip()
        payload = subprocess.run(["git", "show", f"{base}:{path}"], cwd=ROOT,
                                 capture_output=True, check=True).stdout
        need(blob == row["git_blob"], f"source blob drift: {path}")
        need(hashlib.sha256(payload).hexdigest() == row["sha256"], f"source hash drift: {path}")
        checked += 1
    need(manifest["base_commit"] == "c676548106012571fefa1dce0ec16f1bcfe11dce", "exact base pin")
    return checked


def build_certificate() -> dict:
    group_table_sha256 = q8_axioms()
    quotient = augmentation_quotient()
    linear_checks = 0
    for g in range(8):
        c, a, b = (g >> 2) & 1, (g >> 1) & 1, g & 1
        element = (1 << g) ^ GA_ONE
        need(linear_coordinates(element) == (a, b), f"abelianized linear coordinates at group element {g}")
        need(c in (0, 1), "central bit")
        linear_checks += 1

    idempotent_counts = {}
    pair_candidates_per_projection = {}
    total_pair_candidates = 0
    pair_decompositions = {}
    for r, expected in ((3, 28), (4, 120)):
        Ns = idempotents(r)
        need(len(Ns) == expected, f"rank-one idempotent count at r={r}")
        for n in Ns:
            need(matrix_rank(n) == 1, f"rank-one gate at r={r}")
            need(f2_matrix_mul(n, n, r) == n, f"idempotent gate at r={r}")
            need(trace(n, r) == 1, f"trace-one gate at r={r}")
        decompositions, checked = pair_projection_controls(r, Ns)
        idempotent_counts[str(r)] = len(Ns)
        pair_candidates_per_projection[str(r)] = len(Ns) ** 2
        total_pair_candidates += len(Ns) ** 2 * (r * (r - 1) // 2)
        pair_decompositions[str(r)] = {"coordinate_projections": len(decompositions),
                                       "ordered_decompositions": checked,
                                       "per_projection": decompositions}

    direct_replays = 0
    for r in (3, 4):
        for triple in central_targets():
            target = triple + (ONE,) * (r - 3)
            word = direct_word(target, r)
            need(len(word) == 4, "direct four-call tariff")
            product = run_word(word, r)
            need(product == target_matrix(target, r), "direct exact group-algebra target")
            need(matrix_linear_coefficients(product, r) == target_linear_matrices(target, r),
                 "direct first-order target coefficients")
            direct_replays += 1

    # Every target has two first-order idempotent traces, so the call length is even.
    parity_targets = 0
    for triple in central_targets():
        a, b = target_linear_matrices(triple, 3)
        need((trace(a, 3) ^ trace(b, 3)) == 0, "even target first-order trace")
        parity_targets += 1

    # Three targeted negative controls: one missing central call, wrong endpoint,
    # and a rank-one-looking but non-idempotent shear E_01.
    canonical = (MINUS_ONE, I, J)
    canonical_word = direct_word(canonical, 3)
    omitted = canonical_word[:1] + canonical_word[2:]
    need(run_word(omitted, 3) != target_matrix(canonical, 3), "omitted central call control")
    wrong = (ONE, I, J)
    need(run_word(canonical_word, 3) != target_matrix(wrong, 3), "wrong central target control")
    bad = (2, 0, 0)
    need(f2_matrix_mul(bad, bad, 3) != bad, "non-idempotent E_01 control")

    return {
        "format": "q8-central-minus-one-any-r/1",
        "base_commit": "c676548106012571fefa1dce0ec16f1bcfe11dce",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "theorem": {
            "group": "Q8",
            "coefficient_field": "F2",
            "paid_labels": ["i", "j"],
            "target_tuples": 12,
            "finite_role_domain": "all r >= 3",
            "target": "one [-1] and two independently selected [i]/[j] entries; all remaining roles identity",
            "exact_minimum_calls": 4,
            "direct_call_profile": [2, 1, 1],
            "uniform_lower_bound": "odd lengths excluded by trace in J/J^2; length two excluded by exact central coefficient z and rank-one idempotent products"
        },
        "algebra": {
            "group_order": 8,
            "group_table_sha256": group_table_sha256,
            "dim_J": quotient["dim_J"],
            "dim_J2": quotient["dim_J2"],
            "dim_J_over_J2": quotient["dim_J_over_J2"],
            "x2_equals_y2_equals_z": ga_mul(X, X) == Z and ga_mul(Y, Y) == Z,
            "z2_zero": ga_mul(Z, Z) == 0,
            "z_in_J2": True,
            "linear_coordinate_checks": linear_checks
        },
        "finite_controls": {
            "rank_one_idempotents": idempotent_counts,
            "ordered_pair_candidates_per_projection": pair_candidates_per_projection,
            "total_ordered_pair_candidate_checks": total_pair_candidates,
            "rank_two_coordinate_projection_decompositions": pair_decompositions,
            "central_targets_each_width": 12,
            "direct_full_group_algebra_replays": direct_replays,
            "target_parity_checks": parity_targets,
            "negative_controls": {
                "omitted_central_call": "rejected",
                "wrong_central_endpoint": "rejected",
                "non_idempotent_gate": "rejected"
            }
        },
        "cost": {
            "direct_calls": 4,
            "threshold_for_saving": 3,
            "saving_percent_at_threshold": 25,
            "supplier_mapping": "not established",
            "new_kappa": False
        }
    }


def verify(write: bool = False) -> dict:
    pin_count = source_pins()
    receipt = build_certificate()
    certificate_path = PACKAGE / "CERTIFICATE.json"
    if write:
        certificate_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8")
    else:
        expected = json.loads(certificate_path.read_text(encoding="utf-8"))
        need(expected == receipt, "certificate differs from exact replay")
    need(pin_count == 10, "source pin inventory")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate after replay")
    args = parser.parse_args()
    receipt = verify(write=args.write)
    controls = receipt["finite_controls"]
    print("PASS_Q8_CENTRAL_MINUS_ONE_ANY_R "
          f"q8={receipt['algebra']['group_order']} "
          f"dim_J_over_J2={receipt['algebra']['dim_J_over_J2']} "
          f"idempotents={controls['rank_one_idempotents']['3']},{controls['rank_one_idempotents']['4']} "
          f"pair_checks={sum(controls['rank_two_coordinate_projection_decompositions'][r]['ordered_decompositions'] for r in ('3','4'))} "
          f"direct={controls['direct_full_group_algebra_replays']} controls=3 exact_min=4 no_new_kappa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
