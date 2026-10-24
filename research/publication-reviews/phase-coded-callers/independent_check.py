"""Check source matrices and actual D25 views without package imports."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


PREFIX = "work/centre-encoding-campaign-20261014/"
PINS = {
    "interface": (
        PREFIX + "lanes/new-core-transfer-20261017/INTERFACE.json",
        "c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746",
    ),
    "ledger": (
        PREFIX + "upstream-refresh-20261017/pr3251/research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    ),
    "views": (
        PREFIX + "lanes/bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
}
def need(value, label):
    if not value:
        raise ValueError(label)


def rank_and_det(matrix):
    """Use rational row elimination, independent of spectral formulas."""
    rows = [[F(x) for x in row] for row in matrix]
    n = len(rows)
    pivot_row, determinant = 0, F(1)
    for column in range(n):
        pivot = next((i for i in range(pivot_row, n) if rows[i][column]), None)
        if pivot is None:
            continue
        if pivot != pivot_row:
            rows[pivot], rows[pivot_row] = rows[pivot_row], rows[pivot]
            determinant = -determinant
        value = rows[pivot_row][column]
        determinant *= value
        rows[pivot_row] = [x / value for x in rows[pivot_row]]
        for i in range(pivot_row + 1, n):
            scale = rows[i][column]
            if scale:
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return pivot_row, determinant if pivot_row == n else F(0)


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def pull(columns, vector):
    return sum(((column & vector).bit_count() % 2) << j for j, column in enumerate(columns))


def phase(lines, dimension=25):
    linear = [sum(weight for vector, weight in lines if vector >> i & 1) % 4
              for i in range(dimension)]
    quadratic = [sum(-2 * weight for vector, weight in lines
                     if vector >> i & 1 and vector >> j & 1) % 4
                 for i in range(dimension) for j in range(i)]
    return linear, quadratic


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    data = {}
    for name, (relative, expected) in PINS.items():
        raw = (args.source_root / relative).read_bytes()
        need(sha256(raw).hexdigest() == expected, name + " source pin")
        data[name] = json.loads(raw)

    selected = [0, 7, 20, 27, 36, 46, 57, 111]
    ordinary = [p for p in range(112) if p not in selected]
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in data["interface"]["R"]]
    b = [[sum(r[j][a] * r[j][p] for j in range(8)) / 4 for p in ordinary]
         for a in selected]
    q = {row["port"]: row["q"] for row in data["ledger"]["recipes"]}
    need(set(q) == set(range(112)) and len(set(q.values())) == 112, "Distinct actual root lines")
    need(all(sum(b[i][k] * b[j][k] for k in range(104)) == 13 * (i == j)
             for i in range(8) for j in range(8)), "BB*=13I")
    roots = [-13, -11, -5, -3, -1, 1, 3, 5, 11, 13]
    eigenvalue_counts = Counter()
    multiplicity_profiles = Counter()
    for mode in range(512):
        signs = [(-1) ** ((mode & q[p]).bit_count() % 2) for p in ordinary]
        matrix = [[sum(b[i][k] * b[j][k] * signs[k] for k in range(104))
                   for j in range(8)] for i in range(8)]
        need(all(x.denominator == 1 for row in matrix for x in row), "Integral T mode")
        multiplicities = []
        for root in roots:
            shifted = [[matrix[i][j] - root * (i == j) for j in range(8)] for i in range(8)]
            nullity = 8 - rank_and_det(shifted)[0]
            multiplicities.append(nullity)
            eigenvalue_counts[root] += nullity
        need(sum(multiplicities) == 8, "Eight independent eigenspaces span each mode")
        multiplicity_profiles[tuple(multiplicities)] += 1
    need(all(eigenvalue_counts[root] for root in roots), "Every spectral value occurs")

    characters = (1, 2, 3, 6, 6)
    exponents = [sum((q[p] & chi).bit_count() % 2 for chi in characters) % 4 for p in ordinary]
    need(set(exponents) <= {0, 2}, "Real odd-power witness")
    odd = [[sum(b[i][k] * b[j][k] * (1 if exponents[k] == 0 else -1)
                for k in range(104)) for j in range(8)] for i in range(8)]
    vector = [0, 0, 1, 0, -1, 1, 0, 1]
    need(all(sum(x * y for x, y in zip(row, vector)) == 0 for row in odd), "Odd-power null vector")
    odd_rank = rank_and_det(odd)[0]
    minor = rank_and_det([row[:7] for row in odd[:7]])[1]
    need(odd_rank == 7 and minor == -73, "Exact odd-power rank and minor")
    d_image = [sum(b[i][k] * vector[i] for i in range(8)) for k in range(104)]
    need(sum(x * x for x in d_image) == 52, "Nonzero ordinary image")

    views = {(row["stage"], row["port"]): row for row in data["views"]["entries"]}
    need(set(views) == {(s, p) for s in range(3) for p in range(112)}, "All D25 views")
    phase_checks, omission_controls = 0, 0
    for (stage, port), row in views.items():
        rho = row["route_columns"]
        need(row["q"] == q[port], "Same root line in the view")
        need(all(pull(rho, rho[j]) == 1 << j for j in range(25)), "Orthogonal route")
        need(all(act(rho, rho[j]) == 1 << j for j in range(25)), "Involutive route")
        need(act(rho, q[port]) == q[port], "Own line is fixed")
        if stage == 0:
            continue
        alignment = row["literal_stage_alignment"]
        entry_delta = act(rho, alignment["entry_X"])
        previous = [(1 << j, 1) for j in range(9 + 8 * (stage - 1))]
        left = previous + [(pull(rho, entry_delta), 2)]
        right = [(pull(rho, 1 << j), 1) for j in range(9, 9 + 8 * stage)]
        right.append((pull(rho, q[port]), 1))
        need(phase(left) == phase(right), "Exact entry Z4 polynomial")
        need(phase(previous) != phase(right), "Missing entry translation is rejected")
        omission_controls += 1
        complete = [(1 << j, 1) for j in range(9 + 8 * stage)]
        exit_left = complete + [(pull(rho, alignment["exit_X"]), 2)]
        exit_right = [(pull(rho, 1 << j), 1) for j in range(9 + 8 * stage)]
        need(phase(exit_left) == phase(exit_right), "Exact exit Z4 polynomial")
        phase_checks += 2

    e1 = sum(1 << j for j in range(9, 17))
    e2 = sum(1 << j for j in range(17, 25))
    signatures = set()
    for j in range(112):
        for k in range(112):
            sequence = [views[1, k], views[1, j], views[2, j], views[2, 0]]
            outputs = []
            for value in (0, e2, e1):
                for row in sequence:
                    value = act(row["route_columns"], value) ^ row["literal_stage_alignment"]["exit_X"]
                outputs.append(value)
            signatures.add(tuple(outputs))
    need(len(signatures) == 112**2, "All literal affine paths separate one common input")

    profiles = {
        "D25_Q": (25, {1: 4400, 2: 192, 3: 144, 8: 48}),
        "D25_I": (25, {1: 4384, 2: 192, 3: 144, 8: 32, 9: 16}),
        "D73_Q": (73, {1: 12752, 2: 576, 3: 432, 8: 144}),
    }
    masses = {}
    for name, (dimension, profile) in profiles.items():
        mass = sum(rank * count for rank, count in profile.items())
        need(mass == 224 * dimension and all(0 < rank < dimension for rank in profile), "Strict moment premise")
        masses[name] = mass
    result = {
        "status": "PASS_INDEPENDENT_PHASE_CALLER_INPUTS",
        "imports_package_code": False,
        "source_pins": {name: expected for name, (_, expected) in PINS.items()},
        "symmetric_modes": 512,
        "exact_eigenspace_rank_checks": 5120,
        "eigenvalue_multiplicities_across_modes": dict(sorted(eigenvalue_counts.items())),
        "distinct_multiplicity_profiles": len(multiplicity_profiles),
        "odd_power_characters": characters,
        "odd_power_rank": odd_rank,
        "odd_power_leading_minor": str(minor),
        "odd_power_ordinary_image_norm_squared": "52",
        "independent_D25_phase_identities": phase_checks,
        "missing_entry_translation_controls": omission_controls,
        "physical_common_input_path_signatures": len(signatures),
        "complete_native_masses": masses,
        "scope": "Exact finite source checks support the separately read all-width proofs. They do not supply a recursive host, complete map price, numerical grid, or kappa result.",
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
