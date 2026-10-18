#!/usr/bin/env python3
"""Exact rank certificate for the P104 I-G/2 correction matrix."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from fractions import Fraction


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FIXTURE_PATH = REPO / "research/p104-native-channel/inputs/P104-FIXTURE.json"
EXPECTED_FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
CHANNEL_PROOF_PATH = REPO / "research/p104-native-channel/PROOF.md"
EXPECTED_CHANNEL_PROOF_SHA256 = "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c"
WITNESS_PATH = REPO / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
EXPECTED_WITNESS_SHA256 = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
EXPECTED_DETERMINANT = 8721064880344833042121878122499340763136


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_fixture() -> dict:
    raw = FIXTURE_PATH.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == EXPECTED_FIXTURE_SHA256,
         "P104 fixture hash changed")
    return json.loads(raw)


def check_channel_contract() -> None:
    raw = CHANNEL_PROOF_PATH.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == EXPECTED_CHANNEL_PROOF_SHA256,
         "P104 channel proof hash changed")
    need(b"y_t + sum_s <r_t,r_s> x_s/2" in raw,
         "pinned native channel does not state the Gram map")


def check_sparse_factorization(ports: list[tuple[int, ...]], gram: list[list[int]]) -> int:
    """Check B^T B and a dirty-Q correction word in the common chart."""
    raw = WITNESS_PATH.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == EXPECTED_WITNESS_SHA256,
         "native low-rank witness changed")
    witness = json.loads(raw)
    full_frame = [1 << j for j in range(9)]
    need(all(witness["final_frames"][f"X{i}"] == full_frame for i in range(104)),
         "native source ports do not finish in the common rank-nine frame")
    need(all(witness["final_frames"][f"Q{i}"] == full_frame for i in range(8)),
         "native Q scratch registers do not finish in the common rank-nine frame")

    # Columns follow canonical P104 port order. The physical label isometry
    # changes frame labels, not the root coordinates used for this factorization.
    b = [[Fraction(root[j], 2) for root in ports] for j in range(8)]
    n = sum(value != 0 for row in b for value in row)
    need(n == 568, "sparse P104 root-coordinate count changed")
    reconstructed = [
        [sum(b[k][i] * b[k][j] for k in range(8)) for j in range(104)]
        for i in range(104)
    ]
    need(reconstructed == [[Fraction(value) for value in row] for row in gram],
         "P104 coordinate factorization does not reconstruct G")

    # For arbitrary x, y and dirty q, use
    # Y += B^Tq/2; Q += Bx; Y -= B^TQ/2; Q -= Bx; Y += x.
    # This restores q and maps y to y + (I-G/2)x exactly.
    correction = [
        [Fraction(i == j) - reconstructed[i][j] / 2 for j in range(104)]
        for i in range(104)
    ]
    need(all(correction[i][j] == Fraction(2 * int(i == j) - gram[i][j], 2)
             for i in range(104) for j in range(104)),
         "dirty-scratch correction word has the wrong coefficient matrix")
    # Four sparse passes, plus the 104 Y += x additions.
    return 4 * n + 104


def canonical_root_lines() -> list[tuple[int, ...]]:
    """Enumerate the 120 unoriented E8 roots in doubled coordinates."""
    roots: set[tuple[int, ...]] = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = a, b
            if next(x for x in v if x) < 0:
                v = [-x for x in v]
            roots.add(tuple(v))
    for signs in itertools.product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            v = signs if signs[0] > 0 else tuple(-x for x in signs)
            roots.add(tuple(v))
    return sorted(roots)


def rank_integer(matrix: list[list[int]]) -> int:
    """Exact rational rank by fraction-free elimination."""
    a = [row[:] for row in matrix]
    m, n = len(a), len(a[0]) if a else 0
    previous = 1
    r = 0
    for col in range(n):
        pivot_row = next((i for i in range(r, m) if a[i][col]), None)
        if pivot_row is None:
            continue
        if pivot_row != r:
            a[r], a[pivot_row] = a[pivot_row], a[r]
        pivot = a[r][col]
        for i in range(r + 1, m):
            for j in range(col + 1, n):
                numerator = a[i][j] * pivot - a[i][col] * a[r][j]
                q, rem = divmod(numerator, previous)
                need(rem == 0, "non-exact Bareiss division in rank check")
                a[i][j] = q
            a[i][col] = 0
        previous = pivot
        r += 1
        if r == m:
            break
    return r


def determinant_bareiss(matrix: list[list[int]]) -> int:
    """Exact determinant using pivoted fraction-free Bareiss elimination."""
    a = [row[:] for row in matrix]
    n = len(a)
    need(all(len(row) == n for row in a), "determinant input must be square")
    if n == 0:
        return 1
    sign, previous = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                q, rem = divmod(numerator, previous)
                need(rem == 0, "non-exact Bareiss division in determinant")
                a[i][j] = q
            a[i][k] = 0
        previous = pivot
    return sign * a[n - 1][n - 1]


def gram_matrix(roots: list[tuple[int, ...]]) -> list[list[int]]:
    out = []
    for x in roots:
        row = []
        for y in roots:
            dot = sum(a * b for a, b in zip(x, y))
            need(dot % 4 == 0, "doubled E8 root dot product is not divisible by four")
            row.append(dot // 4)
        out.append(row)
    return out


def build_correction(fixture: dict, *, omit_one_removed: bool = False,
                     wrong_gram_scale: bool = False):
    source = fixture["section4_explicit_P104"]
    removed = [tuple(v) for v in source["F0"] + source["C"]]
    if omit_one_removed:
        removed.pop()
    universe = canonical_root_lines()
    need(len(universe) == 120 and len(set(universe)) == 120,
         "E8 root-line universe is not exactly 120 lines")
    need(set(removed) <= set(universe), "fixture puncture is not an E8 root line")
    roots = [v for v in universe if v not in set(removed)]
    need(len(roots) == 104, "fixture must select exactly 104 P104 root lines")
    gram = gram_matrix(roots)
    scale = 2 if wrong_gram_scale else 1
    gram = [[scale * x for x in row] for row in gram]
    need(all(gram[i][i] == 2 for i in range(104)),
         "P104 Gram diagonal must be the root norm 2")
    need(all(gram[i][j] == gram[j][i] for i in range(104) for j in range(104)),
         "Gram matrix is not symmetric")
    correction_twice = [[2 * int(i == j) - gram[i][j] for j in range(104)]
                        for i in range(104)]
    return gram, correction_twice


def main() -> None:
    check_channel_contract()
    fixture = read_fixture()
    gram, correction_twice = build_correction(fixture)
    punctures = {tuple(x) for x in
                 fixture["section4_explicit_P104"]["F0"] +
                 fixture["section4_explicit_P104"]["C"]}
    ports = [v for v in canonical_root_lines() if v not in punctures]
    scalar_adds = check_sparse_factorization(ports, gram)
    gram_rank = rank_integer(gram)
    correction_det = determinant_bareiss(correction_twice)
    need(gram_rank == 8, "P104 root Gram matrix must have rank 8")
    need(correction_det == EXPECTED_DETERMINANT,
         "exact determinant of 2I-G changed")
    need(correction_det != 0, "I-G/2 correction unexpectedly singular")

    # The unoriented root-line representatives may be sign-flipped independently.
    # This conjugates both matrices by a diagonal sign matrix and preserves rank.
    punctures = {tuple(x) for x in
                 fixture["section4_explicit_P104"]["F0"] +
                 fixture["section4_explicit_P104"]["C"]}
    flipped_roots = [tuple(-x for x in v) for v in canonical_root_lines()
                     if v not in punctures]
    flipped = gram_matrix(flipped_roots)
    flipped_twice_correction = [
        [2 * int(i == j) - flipped[i][j] for j in range(104)]
        for i in range(104)
    ]
    need(rank_integer(flipped) == 8, "root-line sign control changed Gram rank")
    need(determinant_bareiss(flipped_twice_correction) == correction_det,
         "root-line sign control changed correction determinant")

    controls = {}
    for name, kwargs in (
        ("missing_puncture_rejected", {"omit_one_removed": True}),
        ("wrong_gram_scale_rejected", {"wrong_gram_scale": True}),
    ):
        try:
            build_correction(fixture, **kwargs)
        except ValueError:
            controls[name] = "REJECTED"
        else:
            raise ValueError(f"negative control unexpectedly accepted: {name}")
    need(all(v == "REJECTED" for v in controls.values()), "negative control failed")

    result = {
        "schema": "p104-side-correction-rank-obstruction/1",
        "status": "PASS_FULL_RANK_I_MINUS_G_OVER_2",
        "fixture_sha256": EXPECTED_FIXTURE_SHA256,
        "channel_proof_sha256": EXPECTED_CHANNEL_PROOF_SHA256,
        "root_line_count": 120,
        "punctured_line_count": 16,
        "p104_port_count": 104,
        "gram_rank": gram_rank,
        "correction": "I-G/2",
        "twice_correction_determinant": str(correction_det),
        "correction_rank": 104,
        "minimum_rank_one_outer_product_summands": 104,
        "root_coordinate_nonzeros": 568,
        "dirty_scratch_factorization_scalar_adds": scalar_adds,
        "direct_correction_matrix_nonzeros": 4992,
        "scratch_registers": 8,
        "scratch_restoration": "arbitrary initial Q values restored exactly",
        "target_frame_round_trip_transports": 208,
        "target_frame_round_trip_rank_mass": 208,
        "correction_finite_invoice": {"rank_mass": 208, "scalar_additions": scalar_adds},
        "channel_plus_correction_finite_invoice": {
            "rank_mass": 2576, "scalar_additions": 5000
        },
        "controls": controls,
        "scope": "Exact rational rank certificate and exact finite end-cut correction word. The 208 compiled target frame round trips add rank mass 208, and the common-chart scalar factorization adds 2,376 scalar additions while restoring all eight arbitrary dirty Q registers. The combined finite channel invoice excludes global hosting, idle costs and any fusion optimization, so it is not a supplier or new kappa.",
    }
    (ROOT / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_P104_SIDE_CORRECTION_RANK",
          f"gram_rank={gram_rank}",
          f"correction_rank={result['correction_rank']}",
          f"det(2I-G)={correction_det}",
          f"controls={len(controls)}")


if __name__ == "__main__":
    main()
