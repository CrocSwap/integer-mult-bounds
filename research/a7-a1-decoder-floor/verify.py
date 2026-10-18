#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact A7+A1 P120 support-deficiency evidence; no physical supplier claim."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/nine-term-decoder-normal-form-seed42/"
EXECUTABLE_PINS = {
    "e8lab.py": "772349edc9dff45fa3cac89fdbbe8bf1bab734e9776a245fcac8e8bd60d94634",
    "verify.py": "248763cf5ff85f073766aa8a85187a1d314fcf3a716b2586ca8fc1197d4c6c4e",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(vector):
    first = next(x for x in vector if x)
    return tuple(vector) if first > 0 else tuple(-x for x in vector)


def roots():
    values = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            values.add(canonical(row))
    for row in itertools.product((-1, 1), repeat=8):
        if sum(x < 0 for x in row) % 2 == 0:
            values.add(canonical(row))
    return sorted(values, reverse=True)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def binary_basis(rows):
    pivots = {}
    for value in rows:
        while value:
            column = value.bit_length() - 1
            if column in pivots:
                value ^= pivots[column]
            else:
                pivots[column] = value
                break
    return [pivots[k] for k in sorted(pivots)]


def rank(rows):
    return len(binary_basis(rows))


def model():
    rr = roots()
    require(len(rr) == 120 and all(dot(x, x) == 8 for x in rr), "E8 root model")
    pairing = [sum(((dot(x, y) // 4 + 1) % 2) << j
                   for j, y in enumerate(rr)) for x in rr]
    require(all(dot(x, y) % 4 == 0 for x in rr for y in rr), "integral root pairing")
    basis = binary_basis(pairing)
    require(len(basis) == 9, "pairing rank nine")
    labels = [sum(((b >> i) & 1) << k for k, b in enumerate(basis)) for i in range(120)]
    words = [sum(((dot_bits(w, label)) & 1) << i for i, label in enumerate(labels))
             for w in range(512)]
    require(len(set(labels)) == 120 and rank(labels) == 9, "faithful binary labels")
    require(set(words) == set(span(basis)), "all label characters")
    # T is stored multiplied by 16. Normals are b_k=e_k-1/8 and a=1/2.
    t16 = [[8 * row[k] - sum(row) for k in range(8)] + [4 * sum(row)] for row in rr]
    supports = [sum((t16[i][k] != 0) << i for i in range(120)) for k in range(9)]
    require([rank(labels[i] for i in bits(s)) for s in supports] == [9] * 9,
            "every reader support spans nine")
    # D first eight entries are x_k+t_i; last is sum(x)/4. This is the
    # complete row solution since the reader normals have rank eight.
    for i, x in enumerate(rr):
        d4 = [4 * a for a in x] + [sum(x)]
        for j, y in enumerate(rr):
            require(dot(d4, t16[j]) == 32 * dot(x, y), "constant all-pairs identity")
            require(sum(t16[j][:8]) == 0, "arbitrary complex shift cancels")
    return rr, pairing, labels, words, t16, supports


def dot_bits(a, b):
    return (a & b).bit_count()


def span(basis):
    values = [0]
    for row in basis:
        values += [x ^ row for x in values]
    return values


def source_binding(rr):
    """Authenticate executable bytes before import, then bind the actual PR1224 frame."""
    for name, expected in EXECUTABLE_PINS.items():
        require(hashlib.sha256((ROOT / SOURCE / name).read_bytes()).hexdigest() == expected,
                "executable source drift: " + name)
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            require(hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                    "source drift: " + entry["path"])
    spec = importlib.util.spec_from_file_location("e8lab", ROOT / SOURCE / "e8lab.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["e8lab"] = module
    spec.loader.exec_module(module)
    spec = importlib.util.spec_from_file_location("a7_source_normal_form", ROOT / SOURCE / "verify.py")
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    frame = predecessor.build_frames()["A7 weights + A1 root"]
    require(frame.z == [-1] * 8 + [0], "source dependency")
    # In doubled coordinates Q e_k = b'_k/2 + a'/8. This maps our
    # b_k=2e_k-1/4 to the source's b'_k and our A1 vector 1 to a'.
    columns = [tuple(frame.F[k][j] / 2 + frame.F[8][j] / 8 for j in range(8))
               for k in range(8)]
    require(all(dot(columns[j], columns[k]) == (j == k)
                for j in range(8) for k in range(8)), "source isometry")
    mapping = []
    signs = []
    for row in rr:
        image = tuple(sum(row[k] * columns[k][j] for k in range(8)) for j in range(8))
        normalized = canonical(image)
        require(normalized in module.LINES, "root isometry image")
        mapping.append(module.LINES.index(normalized))
        signs.append(1 if image == normalized else -1)
    require(len(set(mapping)) == 120, "source root bijection")
    for k in range(8):
        image = tuple(2 * columns[k][j] - frame.F[8][j] / 4 for j in range(8))
        require(image == frame.F[k], "source A7 normal binding")
    require(tuple(sum(columns[k][j] for k in range(8)) for j in range(8)) == frame.F[8],
            "source A1 normal binding")
    return {"frame": [[str(x) for x in row] for row in frame.F],
            "root_permutation": mapping, "root_signs": signs,
            "isometry_columns": [[str(x) for x in row] for row in columns]}


def symmetry(rr, pairing):
    index = {r: i for i, r in enumerate(rr)}
    for k in range(7):
        permutation = []
        for row in rr:
            swapped = list(row)
            swapped[k], swapped[k + 1] = swapped[k + 1], swapped[k]
            permutation.append(index[canonical(swapped)])
        require(len(set(permutation)) == 120, "S8 generator root bijection")
        for i in range(120):
            for j in range(120):
                require(((pairing[i] >> j) & 1) ==
                        ((pairing[permutation[i]] >> permutation[j]) & 1),
                        "S8 generator pairing covariance")
    return 7 * 120 * 120


def compatibility_census(rr, labels, words, direct=False):
    """All 43,435 binary planes; optional second method computes H by row annihilation."""
    differences = [sum((r[0] != r[k]) << i for i, r in enumerate(rr)) for k in range(1, 8)]
    require([d.bit_count() for d in differences] == [57] * 7, "difference supports")
    expected_q = []
    for k in range(1, 8):
        row = [0] * 8
        row[0], row[k] = 2, -2
        expected_q.append(labels[rr.index(tuple(row))])
    require(rank(expected_q) == 7, "seven independent pair-root labels")
    table = [[sum((words[a] & words[b] & d == 0) << b for b in range(512))
              for a in range(512)] for d in differences]
    forced = []
    for d in differences:
        forced.append([binary_basis(labels[i] for i in bits(words[z] & d)) for z in range(512)])
    planes = 0
    partners = Counter()
    ranks = Counter()
    digest = hashlib.sha256()
    direct_checks = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b >= (a ^ b):
                continue
            planes += 1
            nonzero = 0
            for k in range(7):
                h = table[k][a] & table[k][b]
                size = h.bit_count()
                require(size in (1, 2), "plane-compatible deficiency dimension exceeds one")
                digest.update(h.to_bytes(64, "little"))
                if direct:
                    cut = (words[a] | words[b]) & differences[k]
                    cut_basis = binary_basis(labels[i] for i in bits(cut))
                    require(9 - len(cut_basis) == size.bit_length() - 1, "direct H dimension")
                    if size == 2:
                        z = h.bit_length() - 1
                        require(all(dot_bits(v, z) % 2 == 0 for v in cut_basis), "direct H vector")
                    direct_checks += 1
                if size == 2:
                    nonzero += 1
                    z = h.bit_length() - 1
                    f = forced[k][z]
                    require(len(f) in (1, 7), "forced-space dimension is not one or seven")
                    ranks[len(f)] += 1
                    if len(f) == 1:
                        require(f[0] == expected_q[k], "rank-one forced space uses wrong pair root")
            partners[nonzero] += 1
    require(planes == 43435, "complete binary plane census")
    return {"planes": planes, "plane_partner_histogram": dict(sorted(partners.items())),
            "forced_rank_histogram": dict(sorted(ranks.items())),
            "q_labels": expected_q, "q_rank": 7, "plane_H_sha256": digest.hexdigest(),
            "direct_annihilator_checks": direct_checks}


def invoice(d4, t16, pairing, labels):
    row_supports = [sum((d4[i][k] != 0) << i for i in range(120)) for k in range(9)]
    col_supports = [sum((t16[i][k] != 0) << i for i in range(120)) for k in range(9)]
    costs = [rank(pairing[i] & col_supports[k] for i in bits(row_supports[k])) for k in range(9)]
    require(costs == [rank(labels[i] for i in bits(s)) for s in row_supports],
            "pairing rank versus label-span invoice")
    return costs


def identity(d4, t16, rr):
    return all(dot(d4[i], t16[j]) == 32 * dot(rr[i], rr[j])
               for i in range(120) for j in range(120))


def witnesses(rr, pairing, labels, t16):
    shifts = [-row[0] for row in rr]
    base = [[4 * (row[k] + shifts[i]) for k in range(8)] + [sum(row)] for i, row in enumerate(rr)]
    require(identity(base, t16, rr), "eight-active attainment identity")
    base_cost = invoice(base, t16, pairing, labels)
    require(base_cost == [0] + [9] * 8, "eight-active attainment invoice")
    chosen = rr.index((2, -2, 0, 0, 0, 0, 0, 0))
    shifts[chosen] = -rr[chosen][1]
    active = [[4 * (row[k] + shifts[i]) for k in range(8)] + [sum(row)] for i, row in enumerate(rr)]
    require(identity(active, t16, rr), "nine-active attainment identity")
    active_cost = invoice(active, t16, pairing, labels)
    require(active_cost == [1, 8] + [9] * 7, "nine-active sharp invoice")
    # A changed coefficient, omitted term, and wrong reader each destroy exactness.
    bad = [row[:] for row in active]
    bad[chosen][0] += 4
    require(not identity(bad, t16, rr), "coefficient mutation escaped")
    omitted = [row[:] for row in active]
    for row in omitted:
        row[8] = 0
    require(not identity(omitted, t16, rr), "omitted A1 term escaped")
    swapped = [row[:] for row in t16]
    for row in swapped:
        row[0], row[1] = row[1], row[0]
    require(not identity(active, swapped, rr), "wrong reader mutation escaped")
    # The standard eight-coordinate decoder supplies the comparator on this same P120.
    standard = [[4 * x for x in row] for row in rr]
    ordinary = [rank(pairing[i] & sum((row[k] != 0) << j for j, row in enumerate(rr))
                     for i, row in enumerate(rr) if row[k] != 0) for k in range(8)]
    require(ordinary == [9] * 8, "P120 coordinate comparator")
    require(all(dot(standard[i], standard[j]) == 16 * dot(rr[i], rr[j])
                for i in range(120) for j in range(120)), "coordinate scalar comparator")
    return {"changed_root_index": chosen, "changed_root": list(rr[chosen]),
            "row_shifts": shifts, "eight_active_costs": base_cost,
            "nine_active_costs": active_cost, "coordinate_costs": ordinary,
            "identity_entries": 28800, "semantic_controls": 3}


def result(direct=False):
    rr, pairing, labels, words, t16, supports = model()
    binding = source_binding(rr)
    census = compatibility_census(rr, labels, words, direct)
    # The direct route is a replay mode, not a difference in mathematical evidence.
    census.pop("direct_annihilator_checks")
    return {"schema_version": 1, "scope": "fixed A7+A1 P120; arbitrary complex row shifts",
            "minimum_copy": 72, "root_lines": 120, "reader_label_ranks": [9] * 9,
            "forced_A1_cost": 9, "source_binding": binding, "census": census,
            "symmetry_pairing_entries": symmetry(rr, pairing),
            "witness": witnesses(rr, pairing, labels, t16),
            "power_bill": {"q_domain": "0<q<=1", "zero_terms_allowed": "8*9^q",
                           "all_nine_active": "1+8^q+7*9^q"},
            "scope_limits": "No physical circuit, recursive supplier profile, new kappa or formal-kernel claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate RESULT.json")
    parser.add_argument("--direct", action="store_true", help="also recompute every H by direct annihilation")
    args = parser.parse_args()
    evidence = result(args.direct)
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(json.loads(path.read_text()) == json.loads(json.dumps(evidence)), "stored certificate mismatch")
    print("PASS_A7_A1_DECODER_FLOOR roots=120 planes=43435 COPY=72 active=1,8,9,9,9,9,9,9,9"
          + (" direct_H_checks=304045" if args.direct else "") + " no_new_kappa")


if __name__ == "__main__":
    main()
