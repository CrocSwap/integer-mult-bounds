#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Gaussian whole-hyperplane reciprocity boundary; no supplier or kappa claim.

Adam Gall, with substantial OpenAI Codex assistance. Geometry is imported from
Charles Bethin's source-pinned PR767; the binary certificate is implemented here.
All acceptance checks remain active under Python -O.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
N = 60
ALL = (1 << N) - 1
IDENTITY = tuple(1 << i for i in range(N))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_hash(data, expected):
    require(hashlib.sha256(data).hexdigest() == expected, "source SHA256 drift")


def load_geometry():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            check_hash(data, row["sha256"])
            pins[row["path"]] = row["sha256"]
    path = ROOT / "research/gaussian-e8-asymmetric-copy/geometry/core.py"
    spec = importlib.util.spec_from_file_location("pinned_gaussian_geometry", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.Geometry(), pins


def bits(value):
    while value:
        bit = value & -value
        value ^= bit
        yield bit.bit_length() - 1


def multiply(left, right):
    result = []
    for row in left:
        value = 0
        for j in bits(row):
            value ^= right[j]
        result.append(value)
    return tuple(result)


def transpose(matrix):
    result = [0] * N
    for i, row in enumerate(matrix):
        for j in bits(row):
            result[j] |= 1 << i
    return tuple(result)


def diagonal(matrix):
    return sum(((row >> i) & 1) << i for i, row in enumerate(matrix))


def xor(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def outer(left, right):
    return tuple(right if (left >> i) & 1 else 0 for i in range(N))


def inverse(matrix):
    rows = [row | (1 << (N + i)) for i, row in enumerate(matrix)]
    for i in range(N):
        pivot = next((j for j in range(i, N) if (rows[j] >> i) & 1), None)
        require(pivot is not None, "singular incidence matrix")
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(N):
            if j != i and (rows[j] >> i) & 1:
                rows[j] ^= rows[i]
    require(tuple(row & ALL for row in rows) == IDENTITY, "inverse elimination")
    return tuple(row >> N for row in rows)


def image_basis(columns):
    """Return pivot rows with explicit combinations of input columns."""
    basis = {}
    selected = []
    for index, column in enumerate(columns):
        value, combination = column, 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (value, combination)
                selected.append(index)
                break
            prior, prior_combination = basis[pivot]
            value ^= prior
            combination ^= prior_combination
    return basis, selected


def solve(basis, target):
    value, combination = target, 0
    while value:
        pivot = value.bit_length() - 1
        require(pivot in basis, "target outside diagonal image")
        row, coefficient = basis[pivot]
        value ^= row
        combination ^= coefficient
    return combination


def rational_rank(matrix):
    """Independent rational elimination, used on realified Gaussian matrices."""
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][col]
            if scale:
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def realify(matrix):
    result = []
    for row in matrix:
        result.append([entry for a, b in row for entry in (a, -b)])
        result.append([entry for a, b in row for entry in (b, a)])
    return result


def fitting(matrix, incidence):
    require(len(matrix) == N and all(0 <= row <= ALL for row in matrix), "matrix shape")
    require(diagonal(matrix) == ALL, "missing fitting diagonal")
    for i, row in enumerate(matrix):
        require(not (row & ~(incidence[i] | (1 << i))), "forbidden nonorthogonal entry")


def reciprocal(matrix):
    require(matrix == transpose(matrix), "fitted matrix is not reciprocal")


def literal_rectangles(coefficients, incidence):
    """Independent sum of the actual H_u x H_v support rectangles, over F2."""
    result = [0] * N
    for u, row in enumerate(coefficients):
        for v in bits(row):
            for reader in bits(incidence[u]):
                result[reader] ^= incidence[v]
    return tuple(result)


def bill(coefficients, ranks):
    return sum(ranks[u][v] for u, row in enumerate(coefficients) for v in bits(row))


def rank_contract(ranks, incidence):
    require(len(ranks) == N and all(len(row) == N for row in ranks), "rank table shape")
    for u in range(N):
        for v in range(N):
            require(ranks[u][v] == (2 if (incidence[u] >> v) & 1 else 3),
                    "wrong Gaussian pairing-rank charge")


def expect_rejection(callback):
    try:
        callback()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def build():
    core, geometry, pins = load_geometry()
    require(len(core.e8_roots()) == 240, "root count")
    require(len(set(geometry.lines)) == N, "line count")
    require(all(sum(x * x for x in root) == 8 for root in geometry.lines), "root normalization")
    incidence = tuple(sum(1 << j for j, entry in enumerate(row) if entry == (0, 0))
                      for row in geometry.gram)
    require(incidence == transpose(incidence), "Hermitian orthogonality symmetry")
    require(diagonal(incidence) == 0, "no self-orthogonal lines")
    require(all(row.bit_count() == 15 for row in incidence), "whole hyperplane size")
    inv = inverse(incidence)
    require(multiply(incidence, inv) == IDENTITY == multiply(inv, incidence), "two-sided inverse")
    require(inv == transpose(inv), "inverse symmetry")
    require(all(row.bit_count() % 2 == 1 for row in inv), "inverse fixes all-ones vector")

    supports = [tuple(bits(row)) for row in incidence]
    require(all(geometry.rank(support) == 3 for support in supports), "hyperplane dimension")
    ranks = tuple(tuple(geometry.pairing_rank(a, b) for b in supports) for a in supports)
    rank_contract(ranks, incidence)
    rank_census = Counter(entry for row in ranks for entry in row)
    require(rank_census == {2: 900, 3: 2700}, "all3600 pairing ranks")
    # Independent realified checks cover every compulsory diagonal type and both
    # off-diagonal rank classes; these do not call the predecessor's rank kernel.
    rank_controls = [(i, i) for i in range(N)] + [(0, 45), (0, 1)]
    for u, v in rank_controls:
        a, b = geometry.basis(supports[u]), geometry.basis(supports[v])
        matrix = [[core.hermitian(x, y) for y in b] for x in a]
        require(rational_rank(realify(matrix)) == 2 * ranks[u][v], "realification rank mismatch")

    edges = [(i, j) for i in range(N) for j in range(i + 1, N) if (incidence[i] >> j) & 1]
    require(len(edges) == 450, "orthogonal unordered edges")
    columns = [inv[i] & inv[j] for i, j in edges]
    require(Counter(value.bit_count() for value in columns) == {34: 360, 38: 90},
            "asymmetry-column weight census")
    require(all(value.bit_count() % 2 == 0 for value in columns), "even image")
    basis, selected = image_basis(columns)
    require(len(basis) == 59, "complete even diagonal image")

    origin = multiply(inv, inv)
    fitting(literal_rectangles(origin, incidence), incidence)
    require(literal_rectangles(origin, incidence) == IDENTITY, "identity completion")
    reciprocal(origin)
    require(diagonal(origin) == ALL, "symmetric compulsory diagonal")
    require(bill(origin, ranks) == 5940, "identity-completion bill")
    new_types = sum((row & ~(incidence[u] | (1 << u))).bit_count() for u, row in enumerate(origin))
    require(new_types == 1920, "positive completion must leave predecessor960 dictionary")

    # Basis-complete checks, not samples from 2^900 completions. Every fitting B
    # is I plus any subset of the 900 directed orthogonal entries. Each directed
    # generator conjugates to outer(Q_i,Q_j); its diagonal is column i,j below.
    for (i, j), column in zip(edges, columns):
        delta = outer(inv[i], inv[j])
        expected = [0] * N
        expected[i] = 1 << j
        require(multiply(multiply(incidence, delta), incidence) == tuple(expected), "directed generator")
        require(diagonal(delta) == column, "directed diagonal formula")
        reverse = transpose(delta)
        expected_reverse = transpose(tuple(expected))
        require(multiply(multiply(incidence, reverse), incidence) == expected_reverse, "reverse generator")
        symmetric_delta = xor(delta, reverse)
        require(diagonal(symmetric_delta) == 0, "reciprocal generator diagonal")
        reciprocal(symmetric_delta)

    # Exact arbitrary-asymmetry boundary: solve for diagonal(origin) so the
    # resulting fitting coefficient matrix has no diagonal types at all.
    combination = solve(basis, ALL)
    zero_edges = [edges[k] for k in bits(combination)]
    zero_fitting = list(IDENTITY)
    for i, j in zero_edges:
        zero_fitting[i] ^= 1 << j
    zero_fitting = tuple(zero_fitting)
    zero_coefficients = multiply(multiply(inv, zero_fitting), inv)
    fitting(zero_fitting, incidence)
    require(diagonal(zero_coefficients) == 0, "zero-diagonal boundary")
    require(literal_rectangles(zero_coefficients, incidence) == zero_fitting, "boundary rectangle replay")
    require(len(zero_edges) == 34 and bill(zero_coefficients, ranks) == 4736, "boundary invoice")
    require(zero_fitting != transpose(zero_fitting), "boundary must be nonreciprocal")

    i, j = edges[0]
    single_fitting = list(IDENTITY)
    single_fitting[i] ^= 1 << j
    single_coefficients = multiply(multiply(inv, tuple(single_fitting)), inv)
    require(diagonal(single_coefficients).bit_count() == 22, "single-asymmetry boundary")
    min_forced = min(N - value.bit_count() for value in columns)
    require(3 * min_forced == 66, "single-asymmetry Gaussian cost floor")

    controls = []
    core_path = "research/gaussian-e8-asymmetric-copy/geometry/core.py"
    expect_rejection(lambda: check_hash((ROOT / core_path).read_bytes() + b"\n", pins[core_path]))
    controls.append("source-drift")
    singular = list(incidence)
    singular[1] = singular[0]
    expect_rejection(lambda: inverse(singular))
    controls.append("singular-incidence")
    wrong_ranks = [list(row) for row in ranks]
    wrong_ranks[0][0] = 1  # Binary rectangle rank is one, physical Gaussian rank is three.
    expect_rejection(lambda: rank_contract(wrong_ranks, incidence))
    controls.append("binary-rank-is-not-copy-rank")
    missing = list(origin)
    missing[0] ^= 1
    expect_rejection(lambda: fitting(literal_rectangles(tuple(missing), incidence), incidence))
    controls.append("omitted-compulsory-diagonal-type")
    expect_rejection(lambda: require(literal_rectangles(transpose(zero_coefficients), incidence)
                                     == zero_fitting, "reader-source direction"))
    controls.append("reader-source-direction")
    invalid = list(IDENTITY)
    invalid[0] ^= 1 << 1
    expect_rejection(lambda: fitting(tuple(invalid), incidence))
    controls.append("nonorthogonal-entry-not-free")
    expect_rejection(lambda: reciprocal(zero_fitting))
    controls.append("nonsymmetric-fitting-outside-reciprocity-theorem")
    expect_rejection(lambda: require(diagonal(zero_coefficients) == ALL, "false unrestricted diagonal claim"))
    controls.append("unrestricted-forced-diagonal-generalization")
    expect_rejection(lambda: solve(basis, ALL ^ 1))
    controls.append("odd-diagonal-image-target")
    damaged = [columns[index] for index in selected[:-1]]
    expect_rejection(lambda: require(len(image_basis(damaged)[0]) == 59, "incomplete image certificate"))
    controls.append("missing-image-basis-vector")
    # Two duplicate occurrences cancel algebraically but remain two paid calls.
    duplicate_bill = bill(origin, ranks) + 2 * ranks[0][1]
    require(duplicate_bill == 5946 and duplicate_bill >= 180, "multiplicity charged before parity")
    controls.append("duplicate-cancellation-retains-physical-charge")

    return {
        "schema_version": 1,
        "status": "PASS_GAUSSIAN_HYPERPLANE_RECIPROCITY",
        "source_inputs_sha256": pins,
        "gaussian_lines": N,
        "dictionary_ordered_pairs": N * N,
        "incidence_rank_F2": N,
        "incidence_rows_hex": [hex(row) for row in incidence],
        "inverse_rows_hex": [hex(row) for row in inv],
        "Gaussian_pairing_rank_counts": {str(k): v for k, v in sorted(rank_census.items())},
        "independent_realification_checks": len(rank_controls),
        "directed_fitting_generators_checked": 2 * len(edges),
        "reciprocal_affine_dimension": len(edges),
        "reciprocal_forced_diagonal_terms": N,
        "reciprocal_Gaussian_cost_lower_bound": 180,
        "reciprocal_rational_cost_lower_bound": 360,
        "reciprocal_Dfc_deficit_upper": {"constant": -120, "stage_coefficient": -240},
        "identity_completion": {"Gaussian_cost": bill(origin, ranks), "new_nonorthogonal_normal_types": new_types},
        "asymmetry_image": {
            "domain_edges": len(edges), "rank_F2": len(basis), "image": "all even-weight vectors in F2^60",
            "column_weight_counts": {"34": 360, "38": 90},
            "independent_edge_indices": selected,
            "basis_diagonal_columns_hex": [hex(columns[index]) for index in selected],
        },
        "single_asymmetric_pair": {
            "minimum_compulsory_diagonal_terms": min_forced,
            "Gaussian_cost_lower_bound": 66,
            "Dfc_deficit_upper": {"constant": -120, "stage_coefficient": -12},
        },
        "zero_diagonal_boundary": {
            "asymmetric_directed_entries": [list(edge) for edge in zero_edges],
            "fitting_rows_hex": [hex(row) for row in zero_fitting],
            "coefficient_rows_hex": [hex(row) for row in zero_coefficients],
            "diagonal_terms": 0,
            "Gaussian_cost": bill(zero_coefficients, ranks),
            "purpose": "Boundary witness only, not an improvement or a physical supplier",
        },
        "controls": controls,
        "limitations": "No optimal allpairs bill, no general nonsymmetric exclusion, no sharpness at180, no supplier or kappa claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the canonical JSON evidence")
    args = parser.parse_args()
    result = build()
    target = PACKAGE / "RESULT.json"
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(target.read_text()) == result, "committed evidence differs from exact replay")
    print("PASS_GAUSSIAN_HYPERPLANE_RECIPROCITY pairs=3600 symmetric_floor=180 "
          "single_asymmetry_floor=66 diagonal_image_rank=59 zero_diagonal_bill=4736 "
          f"controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
