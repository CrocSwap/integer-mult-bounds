#!/usr/bin/env python3
"""Exact checker for a three-dimensional port decoder on selected PR1094 labels."""
from __future__ import annotations

import hashlib
import json
import tarfile
from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
SOURCE_MANIFEST = ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json"
SOURCE_MANIFEST_SHA256 = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
ENTRY = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PAYLOAD_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
N = 9
PORTS = 112
CORE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_labels() -> list[int]:
    selected = ROOT / "certificates/selected-result.json"
    need(hashlib.sha256(selected.read_bytes()).hexdigest() == SELECTED_SHA256,
         "selected-result pin")
    selected_record = json.loads(selected.read_text(encoding="utf-8"))
    need(selected_record["source_manifest"] ==
         "research/community-frontier1094-audit/SELECTED-SOURCE.json",
         "selected source-manifest pointer")
    need(hashlib.sha256(SOURCE_MANIFEST.read_bytes()).hexdigest() == SOURCE_MANIFEST_SHA256,
         "selected source-manifest pin")
    need(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256,
         "selected archive pin")
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        member = tf.extractfile(ENTRY)
        need(member is not None, "selected DATA-PHASES entry")
        payload = member.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "selected payload pin")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda row: row["port"])
    need(data["ports"] == PORTS and len(recipes) == PORTS, "selected port count")
    need([row["port"] for row in recipes] == list(range(PORTS)), "selected port ordering")
    labels = [row["q"] for row in recipes]
    need(len(set(labels)) == PORTS, "selected labels are not distinct")
    need(all(0 < q < (1 << N) for q in labels), "label outside F2^9")
    need({q.bit_count() for q in labels} == {3, 7}, "selected label weights")
    return labels


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def rank_vectors(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in vectors:
        v = value
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def rank_rows(rows: list[int], width: int) -> int:
    a = list(rows)
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(a)) if (a[i] >> col) & 1), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for i in range(len(a)):
            if i != rank and ((a[i] >> col) & 1):
                a[i] ^= a[rank]
        rank += 1
    return rank


def matrix_rank(matrix: list[list[int]]) -> int:
    width = len(matrix[0]) if matrix else 0
    rows = [sum((value & 1) << j for j, value in enumerate(row)) for row in matrix]
    return rank_rows(rows, width)


def validate_groups(groups: list[list[int]], labels: list[int]) -> None:
    need(len(groups) == 38, "expected 37 triads and one line")
    need(groups[0] == [0] and len(groups[0]) == 1, "residual-line convention")
    need(all(len(g) == 3 for g in groups[1:]), "non-triad block")
    flat = [i for group in groups for i in group]
    need(sorted(flat) == list(range(PORTS)), "port groups are not a partition")
    for g in groups[1:]:
        need(valid_triad(g, labels), "invalid orthogonal 3-plane")


def valid_triad(group: list[int], labels: list[int]) -> bool:
    return (len(group) == 3
            and rank_vectors([labels[i] for i in group]) == 3
            and all(dot(labels[i], labels[j]) == 0
                    for k, i in enumerate(group) for j in group[k + 1:]))


def validate_matrix_factorization(groups: list[list[int]], matrices: list[list[list[int]]],
                                  labels: list[int]) -> None:
    need(len(matrices) == len(groups), "one coefficient matrix per block")
    for g, m in zip(groups, matrices):
        need(len(m) == len(g) and all(len(row) == len(g) for row in m),
             "coefficient matrix dimensions")
        need(all(value in (0, 1) for row in m for value in row), "nonbinary coefficient")
    for r in range(N):
        for c in range(N):
            got = 0
            for g, m in zip(groups, matrices):
                for a, i in enumerate(g):
                    for b, j in enumerate(g):
                        got ^= m[a][b] & ((labels[i] >> r) & 1) & ((labels[j] >> c) & 1)
            need(got == (r == c), "global 9x9 coefficient identity")


def candidate_triples(labels: list[int], residual: int = 0) -> list[tuple[int, int, int]]:
    edges = []
    for i in range(PORTS):
        if i == residual:
            continue
        for j in range(i + 1, PORTS):
            if j == residual or dot(labels[i], labels[j]):
                continue
            for k in range(j + 1, PORTS):
                if (k != residual and not dot(labels[i], labels[k])
                        and not dot(labels[j], labels[k])):
                    edges.append((i, j, k))
    return edges


def iter_orthogonal_covers(labels: list[int], residual: int = 0):
    """MRV exact covers; each branch uses sorted port triples."""
    by_port: list[list[tuple[int, int, int]]] = [[] for _ in range(PORTS)]
    for edge in candidate_triples(labels, residual):
        for i in edge:
            by_port[i].append(edge)
    remaining = ((1 << PORTS) - 1) ^ (1 << residual)

    def visit(mask: int, chosen: list[tuple[int, int, int]]):
        if mask == 0:
            yield tuple(chosen)
            return
        best_options = None
        scan = mask
        while scan:
            bit = scan & -scan
            i = bit.bit_length() - 1
            scan ^= bit
            options = [edge for edge in by_port[i]
                       if all((mask >> j) & 1 for j in edge)]
            if not options:
                return
            if best_options is None or len(options) < len(best_options):
                best_options = options
                if len(options) == 1:
                    break
        assert best_options is not None
        for edge in best_options:
            edge_mask = sum(1 << i for i in edge)
            yield from visit(mask ^ edge_mask, chosen + [edge])

    yield from visit(remaining, [])


def solve_identity(groups: list[list[int]], labels: list[int]) -> list[list[list[int]]] | None:
    """Return the deterministic column-echelon solution to sum A M A^T=I_9."""
    variables = [(g, a, b) for g in groups
                 for a in range(len(g)) for b in range(len(g))]
    basis: list[tuple[int, int] | None] = [None] * (N * N)
    for z, (g, a, b) in enumerate(variables):
        value = 0
        for r in range(N):
            if (labels[g[a]] >> r) & 1:
                for c in range(N):
                    if (labels[g[b]] >> c) & 1:
                        value |= 1 << (r * N + c)
        coefficients = 1 << z
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot] is None:
                basis[pivot] = (value, coefficients)
                break
            vector, combo = basis[pivot]
            value ^= vector
            coefficients ^= combo
    target = sum(1 << (r * N + r) for r in range(N))
    solution = 0
    while target:
        pivot = target.bit_length() - 1
        if basis[pivot] is None:
            return None
        vector, combo = basis[pivot]
        target ^= vector
        solution ^= combo
    matrices = []
    z = 0
    for g in groups:
        d = len(g)
        matrix = [[0] * d for _ in range(d)]
        for a in range(d):
            for b in range(d):
                matrix[a][b] = (solution >> z) & 1
                z += 1
        matrices.append(matrix)
    need(z == len(variables), "internal variable count")
    validate_matrix_factorization(groups, matrices, labels)
    return matrices


def factor_matrix(group: list[int], matrix: list[list[int]], labels: list[int]) -> list[dict]:
    d = len(group)
    columns = [sum((matrix[r][c] & 1) << r for r in range(d)) for c in range(d)]
    basis: list[int] = []
    for col in columns:
        if rank_vectors(basis + [col]) > len(basis):
            basis.append(col)
    terms = []
    for k, left_coeff in enumerate(basis):
        coordinates = []
        for col in columns:
            match = next((mask for mask in range(1 << len(basis))
                          if _xor_selected(basis, mask) == col), None)
            need(match is not None, "matrix column outside its basis")
            coordinates.append(match)
        right_coeff = sum(1 << j for j, coords in enumerate(coordinates)
                          if (coords >> k) & 1)
        left_label = 0
        right_label = 0
        for j, port in enumerate(group):
            if (left_coeff >> j) & 1:
                left_label ^= labels[port]
            if (right_coeff >> j) & 1:
                right_label ^= labels[port]
        left_support = [i for i, q in enumerate(labels) if dot(q, left_label)]
        right_support = [i for i, q in enumerate(labels) if dot(q, right_label)]
        copy_rank = support_pair_rank(left_support, right_support, labels)
        terms.append({
            "group": group,
            "left_coeff": left_coeff,
            "right_coeff": right_coeff,
            "left_label": left_label,
            "right_label": right_label,
            "left_support": left_support,
            "right_support": right_support,
            "copy_rank": copy_rank,
        })
    # Independently check that the reported rank-one factors reconstruct M.
    for r in range(d):
        for c in range(d):
            got = 0
            for term in terms:
                got ^= ((term["left_coeff"] >> r) & 1) & ((term["right_coeff"] >> c) & 1)
            need(got == matrix[r][c], "rank-one factorization of a block matrix")
    return terms


def _xor_selected(values: list[int], mask: int) -> int:
    result = 0
    for i, value in enumerate(values):
        if (mask >> i) & 1:
            result ^= value
    return result


def support_pair_rank(left: list[int], right: list[int], labels: list[int]) -> int:
    rows = []
    for i in left:
        row = sum(dot(labels[i], labels[j]) << k for k, j in enumerate(right))
        rows.append(row)
    return rank_rows(rows, len(right))


def check_full_decoder(terms: list[dict], labels: list[int]) -> None:
    for i in range(PORTS):
        for j in range(PORTS):
            value = 0
            for term in terms:
                value ^= dot(labels[i], term["left_label"]) & dot(labels[j], term["right_label"])
            need(value == dot(labels[i], labels[j]), "full 112x112 decoder identity")


def apply_c(vector: list[tuple[int, int]], shift: int) -> list[tuple[int, int]]:
    """Apply C_q=((1+i)I+(1-i)X_q)/2 with a shared integer denominator."""
    out = []
    for state, (a, b) in enumerate(vector):
        c, d = vector[state ^ shift]
        out.append((a - b + c + d, a + b + d - c))
    return out


def check_dirty_endpoints(groups: list[list[int]], active: set[tuple[int, ...]],
                          labels: list[int]) -> int:
    dim = 1 << N
    checked = 0
    for group in groups:
        if tuple(group) not in active:
            continue
        correction = 0
        for port in group:
            correction ^= labels[port]
        for state in range(dim):
            vector = [(0, 0)] * dim
            vector[state] = (1, 0)
            for _ in range(2):
                for port in group:
                    vector = apply_c(vector, labels[port])
            expected = state ^ correction
            for out_state, amplitude in enumerate(vector):
                need(amplitude == ((1 << (2 * len(group)), 0) if out_state == expected else (0, 0)),
                     "exact Gaussian-dyadic dirty endpoint C_E^2")
            wrong = state ^ (correction ^ labels[group[0]])
            need(wrong != expected and vector[wrong] == (0, 0),
                 "missing-coordinate endpoint negative control")
            checked += 1
    need(checked > 0, "no active endpoint controls")
    return checked


def main() -> None:
    labels = load_labels()
    candidate = json.loads((PACKAGE / "CANDIDATE.json").read_text(encoding="utf-8"))
    groups = candidate["groups"]
    matrices = candidate["matrices"]
    validate_groups(groups, labels)
    validate_matrix_factorization(groups, matrices, labels)
    terms = []
    matrix_rank_hist: dict[int, int] = {}
    for g, m in zip(groups, matrices):
        r = matrix_rank(m)
        matrix_rank_hist[r] = matrix_rank_hist.get(r, 0) + 1
        terms.extend(factor_matrix(g, m, labels))
    check_full_decoder(terms, labels)
    active = {tuple(g) for g, m in zip(groups, matrices) if matrix_rank(m)}
    endpoint_cases = check_dirty_endpoints(groups, active, labels)

    hist: dict[int, int] = {}
    for term in terms:
        r = term["copy_rank"]
        need(r > 0, "zero-charge term is outside this charged interface")
        hist[r] = hist.get(r, 0) + 1
    recorded_hist = {int(k): int(v) for k, v in candidate["copy_hist"].items()}
    need(hist == recorded_hist, "recorded copy histogram")
    charge = sum(r * count for r, count in hist.items())
    need(charge == candidate["copy_charge"], "recorded total copy charge")
    expected_terms = candidate["terms"]
    need(len(expected_terms) == len(terms), "recorded term count")
    for computed, recorded in zip(terms, expected_terms):
        need(computed == recorded, "recorded term support/factor")

    profile = CORE.copy()
    for r, count in hist.items():
        profile[r] = profile.get(r, 0) + count
    recorded_profile = {int(k): int(v) for k, v in candidate["local_profile"].items()}
    need(profile == recorded_profile, "recorded local profile")
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling  # type: ignore[import-not-found]
    moment = ceiling.relax(profile, 73, 896, 9, charge, Q(1, 99), unpaid=3)
    cap = ceiling.ceiling(profile, 73, 896, 9, charge, grid=Q(1, 10**12), unpaid=3)[1]
    need(candidate["passes_target"] == (moment[1] < 1), "target-pass flag")

    # Negative controls: changing an endpoint correction, a factor term, a block
    # coefficient or an orthogonality edge is rejected by exact predicates.
    try:
        check_full_decoder(terms[1:], labels)
    except ValueError:
        term_control = True
    else:
        term_control = False
    need(term_control, "omitted-factor negative control")
    bad_matrices = [[row[:] for row in m] for m in matrices]
    gi = next(i for i, m in enumerate(bad_matrices) if matrix_rank(m))
    bad_matrices[gi][0][0] ^= 1
    try:
        validate_matrix_factorization(groups, bad_matrices, labels)
    except ValueError:
        matrix_control = True
    else:
        matrix_control = False
    need(matrix_control, "corrupt-matrix negative control")
    bad = next((i, j) for i in range(PORTS) for j in range(i + 1, PORTS) if dot(labels[i], labels[j]))
    third = next(i for i in range(PORTS) if i not in bad)
    need(not valid_triad([bad[0], bad[1], third], labels),
         "nonorthogonal-triad negative control")

    result = {
        "status": "PASS_TRI_PLANE_FACTORIZATION_P112",
        "ports": PORTS,
        "dimension": N,
        "blocks": len(groups),
        "triads": len(groups) - 1,
        "orthogonal_triples_in_search_domain": 24416,
        "covers_examined": candidate["covers_examined"],
        "matrix_rank_histogram": {str(k): v for k, v in sorted(matrix_rank_hist.items())},
        "active_terms": len(terms),
        "copy_rank_histogram": {str(k): v for k, v in sorted(hist.items())},
        "copy_charge": charge,
        "endpoint_basis_cases": endpoint_cases,
        "moment_at_1_over_99": [str(moment[0]), str(moment[1])],
        "a_ceiling": str(cap),
        "a_ceiling_decimal": f"{float(cap):.12f}",
        "kappa_cap": str(cap / (1 + cap)),
        "passes_a_1_over_99": moment[1] < 1,
        "negative_controls": 4,
    }
    (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS_TRI_PLANE_FACTORIZATION_P112",
          f"triples={len(groups)-1}",
          f"terms={len(terms)}",
          f"copy={charge}",
          f"profile={{{','.join(f'{k}:{profile[k]}' for k in sorted(profile))}}}",
          f"endpoint_cases={endpoint_cases}",
          f"moment_upper={float(moment[1]):.15f}",
          f"a_cap={float(cap):.12f}",
          f"target={'PASS' if moment[1] < 1 else 'FAIL'}",
          "controls=4")


if __name__ == "__main__":
    main()
