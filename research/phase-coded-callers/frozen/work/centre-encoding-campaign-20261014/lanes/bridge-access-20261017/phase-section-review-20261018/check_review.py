"""Check the exact spectral inputs to the phase-section geometry."""

from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "geometry": ("native-escape-20261017/PHASE-SECTION-GEOMETRY.md", "a3d970f070e6aaf67b79bd80d564cd7d653580f1f7fc1daadc3170dbdb9249ff"),
    "source_qualification": ("native-escape-20261017/PHASE-SECTION-GEOMETRY-SOURCES.md", "ae8ec52c10c77658190b996a529a405736e377ebc76e9804eaf73e7ff965cc97"),
    "map_correction": ("native-escape-20261017/inplace-service-review/MAP-COST-CORRECTION.md", "fbf9ef6d0069ab6b5d4ac8ad5daa480a88fdc8bc363cfacb309d47010e3f3c7f"),
    "interface": ("new-core-transfer-20261017/INTERFACE.json", "c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746"),
    "phase": ("bridge-access-20261017/cycle-cover-response-20261018/check_cycle_cover.py", "cf39b15752fcb96cc22b9013dce38e13a4399d99b30dc9f53eef788d5ded2bf4"),
}
ROOTS = [-13, -11, -5, -3, -1, 1, 3, 5, 11, 13]
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]


def need(value, label):
    if not value:
        raise ValueError(label)


def det(a):
    a = [row[:] for row in a]
    n = len(a)
    sign, prior = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * a[k][k] - a[i][k] * a[k][j]
                need(numerator % prior == 0, "Exact Bareiss division")
                a[i][j] = numerator // prior
        prior = a[k][k]
        for i in range(k + 1, n):
            a[i][k] = 0
    return sign * a[-1][-1]


def mm(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def main():
    for rel, pin in PINS.values():
        need(sha256((LANES / rel).read_bytes()).hexdigest() == pin, rel + " pin")
    phase_path = LANES / PINS["phase"][0]
    spec = importlib.util.spec_from_file_location("section_review_phase", phase_path)
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    _, ports = phase.load()
    q = [p["q"] for p in ports]
    source = json.loads((LANES / PINS["interface"][0]).read_text())
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in source["R"]]
    b2 = [[sum(r[j][a] * r[j][p] for j in range(8)) / 2 for p in U] for a in A]
    need(all(x.denominator == 1 for row in b2 for x in row), "Twice B is integer")
    b2 = [[int(x) for x in row] for row in b2]
    need(all(sum(b2[i][k] * b2[j][k] for k in range(104)) == 52 * (i == j)
             for i in range(8) for j in range(8)), "BD equals 13I")
    seen = {}
    for chi in range(512):
        signs = [1 - 2 * ((chi & q[p]).bit_count() & 1) for p in U]
        t4 = [[sum(b2[i][k] * b2[j][k] * signs[k] for k in range(104))
               for j in range(8)] for i in range(8)]
        value = [[int(i == j) for j in range(8)] for i in range(8)]
        for root in ROOTS:
            factor = [[t4[i][j] - 4 * root * (i == j) for j in range(8)] for i in range(8)]
            value = mm(value, factor)
            if root not in seen and det(factor) == 0:
                seen[root] = chi
        need(not any(x for row in value for x in row), "Exact ten-root annihilator")
    need(set(seen) == set(ROOTS), "Every claimed spectral value occurs")
    copy_characters = (1, 2, 3, 6, 6)
    powers = [sum((q[p] & chi).bit_count() & 1 for chi in copy_characters) % 4 for p in U]
    need(set(powers) <= {0, 2}, "The odd-power witness is real")
    s4 = [[sum(b2[i][k] * b2[j][k] * (1 if powers[k] == 0 else -1)
               for k in range(104)) for j in range(8)] for i in range(8)]
    null = [0, 0, 1, 0, -1, 1, 0, 1]
    need(all(sum(x * y for x, y in zip(row, null)) == 0 for row in s4), "Odd-power null vector")
    minor = det([row[:7] for row in s4[:7]])
    need(minor == -73 * 4**7, "Odd-power rank is exactly seven")
    singular_squared = sorted({F(13, root * root) for root in ROOTS})
    cosines_squared = sorted({F(root * root, 169) for root in ROOTS})
    need(singular_squared[0] == F(1, 13) and singular_squared[-1] == 13, "Sharp section norm bounds")
    result = {
        "status": "PASS_INDEPENDENT_PHASE_SECTION_GEOMETRY",
        "source_pins": {k: pin for k, (_, pin) in PINS.items()},
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "exact_symmetric_mode_matrices": 512,
        "spectral_occurrence_modes": seen,
        "positive_section_singular_values_squared": [str(x) for x in singular_squared],
        "principal_angle_cosines_squared": [str(x) for x in cosines_squared],
        "positive_section_norm_squared": "13", "condition_number_squared": "169",
        "oblique_projector_norm_squared": "169", "odd_power_rank": 7,
        "odd_power_leading_minor": str(F(minor, 4**7)),
        "scope": "Exact spectral inputs and independent algebra review. No new native service, stream-map cost, or supplier claim.",
    }
    (HERE / "CHECKS.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
