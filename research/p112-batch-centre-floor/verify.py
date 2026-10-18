#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact P112 batch-floor premises. Standard library; default read-only; -O safe.

Predecessor code is hash-bound as provenance but never imported or executed.
--write regenerates only this package's complete deterministic RESULT.json.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def source_pins():
    manifest = read_json(HERE / "SOURCES.json")
    require(manifest.get("schema_version") == 1, "source schema")
    rows, seen = [], set()
    for item in manifest["files"]:
        name = item["path"]
        require(name not in seen, "duplicate source")
        seen.add(name)
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT.resolve()), "external source")
        if item["usage"] == "provenance":
            command = ["git", "-C", str(ROOT), "show", manifest["base_commit"] + ":" + name]
            process = subprocess.run(command, capture_output=True, check=False)
            require(process.returncode == 0, "cannot read pinned historical provenance: " + name)
            payload = process.stdout
            binding = "historical Git blob at pinned base; current working file is not read"
        else:
            require(item["usage"] == "input" and path.is_file(), "missing/invalid input")
            payload = path.read_bytes()
            binding = "current immutable input bytes"
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        require(blob == item["git_blob"], "Git blob mismatch: " + name)
        sha = hashlib.sha256(payload).hexdigest()
        require(sha == item["sha256"], "source hash: " + name)
        rows.append({"path": name, "sha256": sha, "git_blob": blob, "binding": binding})
    require(len(rows) >= 3, "empty source coverage")
    return {"base_commit": manifest["base_commit"], "files": rows,
            "hash_domain": "SHA256 of exact bytes; historical provenance also bound to its Git blob"}


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def binary_basis(rows):
    basis, selected = {}, []
    for index, value in enumerate(rows):
        v = value
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis:
                v ^= basis[pivot]
            else:
                basis[pivot] = v
                selected.append(index)
                break
    return selected


def binary_rank(rows):
    return len(binary_basis(rows))


def rational_basis(rows):
    """Fraction elimination, returning indices of original witness rows."""
    pivots, selected = {}, []
    for index, row in enumerate(rows):
        v = list(map(Fraction, row))
        for column, basis in sorted(pivots.items()):
            if v[column]:
                q = v[column]
                v = [x - q * y for x, y in zip(v, basis)]
        column = next((j for j, x in enumerate(v) if x), None)
        if column is not None:
            q = v[column]
            pivots[column] = [x / q for x in v]
            selected.append(index)
    return selected, sorted(pivots)


def determinant(matrix):
    """Independent integer Bareiss determinant, applied to original-row minors."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "nonsquare minor")
    if not n:
        return 1
    a, previous, sign = [row[:] for row in matrix], 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        value = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = value * a[i][j] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "Bareiss nonexact division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = value
    return sign * a[-1][-1]


def geometry():
    roots = [tuple(2 * (i == j) for i in range(8)) for j in range(8)]
    planes = [p for p in itertools.combinations(range(8), 4)
              if p[0] ^ p[1] ^ p[2] ^ p[3] == 0]
    require(len(planes) == 14, "affine plane count")
    for plane in planes:
        for tail in itertools.product((-1, 1), repeat=3):
            row = [0] * 8
            for j, sign in zip(plane, (1,) + tail):
                row[j] = sign
            roots.append(tuple(row))
    return roots, planes


def positive_line(row):
    return tuple(row if next(x for x in row if x) > 0 else [-x for x in row])


def check_geometry(roots):
    require(len(roots) == 120 and len(set(roots)) == 120, "120 distinct roots")
    require(all(len(row) == 8 and dot(row, row) == 4 for row in roots), "root norm")
    require(all(dot(a, b) % 2 == 0 for a in roots for b in roots), "Gram integrality")
    require({dot(a, b) // 2 for i, a in enumerate(roots) for j, b in enumerate(roots)
             if i != j} == {-1, 0, 1}, "off-diagonal Gram")
    nrows = [sum(((1 + dot(a, b) // 2) & 1) << j for j, b in enumerate(roots)) for a in roots]
    require(binary_rank(nrows) == 9 and len(set(nrows)) == 120, "rank nine / distinct labels")
    require(all((nrows[i] >> i) & 1 for i in range(120)), "label diagonal")
    return nrows


def geometry_receipt(roots, planes, nrows):
    # Independent standard-coordinate signed-root generation and explicit map.
    signed = []
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            signed.append(tuple(row))
    signed.extend(row for row in itertools.product((-1, 1), repeat=8)
                  if sum(x == -1 for x in row) % 2 == 0)
    require(len(signed) == 240, "standard signed roots")
    standard = sorted({positive_line(row) for row in signed})
    frame = []
    for a in range(0, 8, 2):
        for sign in (1, -1):
            row = [0] * 8
            row[a], row[a + 1] = 2, 2 * sign
            frame.append(row)
    require(all(dot(a, b) == 8 * (i == j) for i, a in enumerate(frame)
                for j, b in enumerate(frame)), "standard frame")
    images, raw_images = [], []
    for row in standard:
        require(all(dot(row, f) % 4 == 0 for f in frame), "frame map integral")
        raw = [dot(row, f) // 4 for f in frame]
        raw_images.append(raw)
        images.append(positive_line(raw))
    require(set(images) == set(roots), "two root constructions disagree")
    for i, a in enumerate(standard):
        for j, b in enumerate(standard):
            require(2 * dot(raw_images[i], raw_images[j]) == dot(a, b), "exact scaled Gram identity")
            require(((1 + dot(a, b) // 4) & 1) == ((1 + dot(images[i], images[j]) // 2) & 1),
                    "pairing isometry")
    require(len(rational_basis(roots[8:])[0]) == 8, "live root rank")
    require(all(sum(row[i] * row[j] for row in roots[8:]) == 56 * (i == j)
                for i in range(8) for j in range(8)), "live Gram X^T X=56I")
    return {"hamming_roots": [list(r) for r in roots], "affine_planes": [list(p) for p in planes],
            "standard_roots_sha256": digest(standard), "standard_frame": frame,
            "standard_to_hamming": "h_j=(q dot f_j)/4; normalize line sign",
            "exact_scaled_Gram_identity": "2*(h(q) dot h(q')) = q dot q' before line-sign normalization",
            "exact_scaled_Gram_entries_checked": 14400,
            "label_pairing_entries_checked": 14400, "label_pairing_rank": 9,
            "label_pairing_sha256": digest(nrows), "live_ports": 112,
            "deleted_indices": list(range(8)), "live_root_rank": 8,
            "live_coordinate_Gram": [[56 * int(i == j) for j in range(8)] for i in range(8)]}


def source_geometry(roots, geom, sources):
    name = "research/p112-single-lift/reference-geometry.json"
    require(any(row["path"] == name for row in sources["files"]), "PR845 geometry must be pinned")
    data = read_json(ROOT / name)
    require(canonical(data["frame"]) == canonical(geom["standard_frame"]), "PR845 frame mismatch")
    require(len(data["roots"]) == len(data["X"]) == len(data["labels"]) == len(data["duals"]) == 112,
            "PR845 geometry lengths")
    require(all(type(x) is int for row in data["roots"] + data["X"] for x in row), "integer source roots")
    require(all(type(x) is int and 0 < x < 512 for x in data["labels"] + data["duals"]), "source labels")
    require(all(len(row) == 8 for row in data["roots"] + data["X"]), "source coordinate widths")
    images = []
    for row, expected in zip(data["roots"], data["X"]):
        require(all(dot(row, f) % 4 == 0 for f in data["frame"]), "source image integrality")
        image = [dot(row, f) // 4 for f in data["frame"]]
        require(image == expected, "PR845 X compatibility")
        images.append(positive_line(image))
    require(len(set(images)) == 112 and set(images) == set(roots[8:]), "PR845 live-set compatibility")
    for i, a in enumerate(data["roots"]):
        for j, b in enumerate(data["roots"]):
            inherited = (data["duals"][i] & data["labels"][j]).bit_count() & 1
            require(inherited == ((1 + dot(a, b) // 4) & 1), "PR845 labels/duals compatibility")
            require(inherited == ((1 + dot(images[i], images[j]) // 2) & 1), "PR845 pairing compatibility")
    return {"path": name, "live_roots_matched": 112, "X_entries_checked": 896,
            "label_dual_pairing_entries_checked": 12544,
            "imports_predecessor_code": False}


def pairing_rank(nrows, readers, sources):
    mask = sum(1 << j for j in set(sources))
    return binary_rank([nrows[i] & mask for i in set(readers)])


def check_minor(roots, indices, columns, expected):
    value = determinant([[roots[i][j] for j in columns] for i in indices])
    require(value != 0 and value == expected, "nonzero exact minor")


def census(roots, nrows):
    basis = binary_basis(nrows)
    require(len(basis) == 9, "label basis count")
    labels = [sum(((row >> index) & 1) << j for j, index in enumerate(basis)) for row in nrows]
    require(binary_rank(labels) == 9, "label coordinate map injective")
    records, exceptional = [], []
    for lam in range(1, 512):
        outside = [i for i in range(8, 120) if (labels[i] & lam).bit_count() & 1]
        selected, columns = rational_basis([roots[i] for i in outside])
        indices = [outside[j] for j in selected]
        rank = len(indices)
        require(rank in (7, 8), "complement rank")
        value = determinant([[roots[i][j] for j in columns] for i in indices])
        check_minor(roots, indices, columns, value)
        row = {"functional": lam, "outside_count": len(outside), "rank": rank,
               "minor_rows": indices, "minor_columns": columns, "minor_determinant": value}
        if rank == 7:
            normals = [j for j in range(8) if all(roots[i][j] == 0 for i in outside)]
            require(len(normals) == 1, "unique missing-coordinate normal")
            normal = normals[0]
            inside = [i for i in range(8, 120) if not ((labels[i] & lam).bit_count() & 1)]
            require(inside == [i for i in range(8, 120) if roots[i][normal]], "exceptional support equality")
            require(binary_rank([nrows[i] for i in inside]) == 8, "exceptional support dimension")
            row.update({"normal_coordinate": normal, "support": inside, "support_label_rank": 8})
            exceptional.append(row)
        records.append(row)
    require(Counter(r["rank"] for r in records) == {8: 503, 7: 8}, "rank histogram")
    require(sorted(r["normal_coordinate"] for r in exceptional) == list(range(8)), "missing normals")
    pairings = [[pairing_rank(nrows, a["support"], b["support"]) for b in exceptional] for a in exceptional]
    require(all(v == 8 for row in pairings for v in row), "64 exceptional pairings rank eight")
    return {"basis_root_indices": basis, "labels_in_dual_coordinates": labels,
            "hyperplanes": records, "exceptional_functionals": [r["functional"] for r in exceptional],
            "exceptional_pairing_ranks": pairings, "hyperplane_count": 511,
            "complement_rank_histogram": {"7": 8, "8": 503}, "checked_integer_minors": 511,
            "exceptional_pairings_checked": 64}


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def shear_pair(a, b, source, target, coefficient):
    for row in a:
        row[target] += coefficient * row[source]
    for row in b:
        row[source] -= coefficient * row[target]


def root_matrix(roots, k):
    return [[x if block == call else 0 for block in range(k) for x in root]
            for call in range(k) for root in roots[8:]]


def multiply(a, b):
    columns = list(zip(*b))
    return [[dot(row, col) for col in columns] for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def check_product(d, t, target):
    require(len(d) == len(target) and len(t) == len(target[0]), "factor dimensions")
    require(d and t and len(d[0]) == len(t[0]), "factor width")
    for i, row in enumerate(d):
        for j, other in enumerate(t):
            require(dot(row, other) == target[i][j], "full identity including cross-call entries")


def term_costs(d, t, nrows):
    result = []
    for column in range(len(d[0])):
        readers = {8 + i % 112 for i, row in enumerate(d) if row[column]}
        sources = {8 + i % 112 for i, row in enumerate(t) if row[column]}
        result.append(pairing_rank(nrows, readers, sources))
    return result


def aligned_columns(coefficients):
    """A block-root-code column is aligned iff all blocks use one root axis."""
    return [len({row % 8 for row in range(len(coefficients)) if coefficients[row][column]}) == 1
            for column in range(len(coefficients[0]))]


def check_exact_cost_law(a, b, costs):
    left, right = aligned_columns(a), aligned_columns(b)
    predicted = [8 if x or y else 9 for x, y in zip(left, right)]
    require(costs == predicted, "exact 8m plus two-sided mixing charge")
    return {"reader_aligned": left, "source_aligned": right,
            "two_sided_mixed_terms": sum(not (x or y) for x, y in zip(left, right))}


def fixture(roots, nrows, k, mode):
    n = 8 * k
    a, b, operations = identity(n), identity(n), []
    if mode.startswith("shared"):
        require(k >= 2, "shared fixture requires independent calls")
        for block in range(1, k):
            for j in range(8):
                for source, target, coefficient in ((j, 8 * block + j, 1), (8 * block + j, j, -1)):
                    shear_pair(a, b, source, target, coefficient)
                    operations.append([source, target, coefficient])
    if mode == "shared_cross_coordinate":
        shear_pair(a, b, 0, 9, 2)
        operations.append([0, 9, 2])
    if mode == "two_sided_coordinate_mixing":
        # Only column one has full label span on BOTH sides. The other
        # two changed columns each retain one aligned side: exact cost65.
        for i, row in enumerate(((1, 1, 0), (0, 1, 1), (0, 0, 1))):
            a[i][:3] = row
        for i, row in enumerate(((1, 0, 0), (-1, 1, 0), (1, -1, 1))):
            b[i][:3] = row
    if mode == "overcomplete":
        for i in range(n):
            a[i].append(a[i][0])
            b[i].append(-b[i][0])
            b[i][0] *= 2
    require(multiply(a, transpose(b)) == identity(n), "coefficient factorization")
    x = root_matrix(roots, k)
    d, t = multiply(x, a), multiply(x, b)
    target = multiply(x, transpose(x))
    check_product(d, t, target)
    costs = term_costs(d, t, nrows)
    exact_cost = check_exact_cost_law(a, b, costs)
    if mode == "two_sided_coordinate_mixing":
        require(sum(costs) == 64 * k + 1 and exact_cost["two_sided_mixed_terms"] == 1,
                "one-unit strict mixing charge")
    require(all(c >= 8 for c in costs) and sum(costs) >= 64 * k, "batch floor")
    if mode in ("canonical", "shared_same_coordinate"):
        require(costs == [8] * n, "attaining fixture")
    mixed = [c for c in range(len(a[0])) if
             len({i // 112 for i, row in enumerate(d) if row[c]}) > 1 or
             len({i // 112 for i, row in enumerate(t) if row[c]}) > 1]
    if mode.startswith("shared"):
        require(bool(mixed), "fixture must mix independent calls")
    return {"calls": k, "mode": mode, "terms": len(costs), "term_costs": costs,
            "cost": sum(costs), "lower_bound": 64 * k, "coefficient_A": a, "coefficient_B": b,
            "exact_cost_law": exact_cost,
            "paired_shears": operations, "mixed_call_columns": mixed,
            "matrix_entries_checked": len(d) * len(t),
            "off_diagonal_call_entries_checked": k * (k - 1) * 112 * 112,
            "factors_sha256": digest([d, t]), "target_sha256": digest(target)}


def rectangular_fixture(roots, nrows):
    # Three output blocks, two independent input blocks, rank(C)=2.
    # Compute the target directly from C and root dot products, independently
    # of the attaining coefficient factors used to generate D and T.
    coupling = [[1, 0], [0, 1], [1, -2]]
    a = [[coupling[block][term // 8] * int(axis == term % 8)
          for term in range(16)] for block in range(3) for axis in range(8)]
    b = identity(16)
    d = multiply(root_matrix(roots, 3), a)
    t = multiply(root_matrix(roots, 2), b)
    target = [[coupling[i // 112][j // 112] * dot(roots[8 + i % 112], roots[8 + j % 112])
               for j in range(224)] for i in range(336)]
    check_product(d, t, target)
    costs = term_costs(d, t, nrows)
    require(costs == [8] * 16, "rectangular coupling attainment")
    exact_cost = check_exact_cost_law(a, b, costs)
    return {"C": coupling, "rank_C": len(rational_basis(coupling)[0]),
            "input_blocks": 2, "output_blocks": 3, "terms": 16,
            "cost": sum(costs), "term_costs": costs, "exact_cost_law": exact_cost,
            "matrix_entries_checked": 336 * 224, "factors_sha256": digest([d, t])}


def expect_failure(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("control did not reject: " + label)


def controls(roots, nrows, counts):
    results = []
    corrupted = list(roots)
    corrupted[8] = tuple(2 * x for x in roots[8])
    results.append(expect_failure(lambda: check_geometry(corrupted), "root norm mutation"))
    bad_pairing = nrows[:]
    bad_pairing[0] ^= 1
    results.append(expect_failure(lambda: require(bad_pairing == check_geometry(roots), "pairing definition"),
                                  "binary pairing mutation"))
    results.append(expect_failure(lambda: require([r["functional"] for r in counts["hyperplanes"][:-1]] ==
                                                  list(range(1, 512)), "hyperplane coverage"), "omitted hyperplane"))
    first = counts["hyperplanes"][0]
    bad_indices = first["minor_rows"][:]
    bad_indices[-1] = bad_indices[0]
    results.append(expect_failure(lambda: check_minor(roots, bad_indices, first["minor_columns"],
                                                       first["minor_determinant"]), "duplicate minor row"))
    x = root_matrix(roots, 2)
    target = multiply(x, transpose(x))
    results.append(expect_failure(lambda: check_product([r[1:] for r in x], [r[1:] for r in x], target),
                                  "omitted rank-one summand"))
    leaked = [row[:] for row in x]
    for row in leaked:
        row[0] += row[8]
    results.append(expect_failure(lambda: check_product(leaked, x, target), "cross-call crosstalk"))
    wrong = multiply(leaked, transpose(x))
    require(all(wrong[i][j] == target[i][j] for i in range(224) for j in range(224)
                if i // 112 == j // 112), "crosstalk must pass diagonal-only check")
    # Exact factorization outside the root code. Its final term has cost one.
    d, t = [row[:] for row in x], [row[:] for row in x]
    for i in range(224):
        z = int(i == 0)
        d[i][0] += z
        d[i].append(-z)
        t[i].append(t[i][0])
    check_product(d, t, target)
    outside_costs = term_costs(d, t, nrows)
    require(outside_costs[-1] == 1, "outside-code cost-one counterexample")
    require(len(rational_basis(roots[9:])[0]) == 8, "singleton outside-code premise")
    results.append(expect_failure(lambda: require(all(c >= 8 for c in outside_costs), "root-code domain"),
                                  "outside-root-code exact factorization"))
    # Correlated two-input/two-output demand C=ones(2,2), rank(C)=1.
    single = root_matrix(roots, 1)
    repeated = single + single
    correlated_target = multiply(repeated, transpose(repeated))
    check_product(repeated, repeated, correlated_target)
    correlated_costs = term_costs(repeated, repeated, nrows)
    require(correlated_costs == [8] * 8, "rank-one demand attaining fixture")
    require(correlated_target != target, "correlated endpoint differs")
    results.append(expect_failure(lambda: check_product(repeated, repeated, target), "correlated demand substituted"))
    # Exact Z[i] unit rephasing: D_0*=i, T_0*=-i, with literal integer pairs.
    phase_d = [[(0, x) if c == 0 else (x, 0) for c, x in enumerate(row)] for row in single]
    phase_t = [[(0, -x) if c == 0 else (x, 0) for c, x in enumerate(row)] for row in single]
    phase_entries = 0
    for i, a in enumerate(phase_d):
        for j, b in enumerate(phase_t):
            real = sum(ar*br - ai*bi for (ar, ai), (br, bi) in zip(a, b))
            imaginary = sum(ar*bi + ai*br for (ar, ai), (br, bi) in zip(a, b))
            require((real, imaginary) == (dot(single[i], single[j]), 0), "Gaussian ordinary-transpose phase")
            phase_entries += 1
    results.append(expect_failure(lambda: require(all(dot(a, b) - 2*a[0]*b[0] == dot(a, b)
                                                    for a in single for b in single), "Hermitian mismatch"),
                                  "conjugate transpose substituted"))
    results.append(expect_failure(lambda: require(canonical({"count": True}) == canonical({"count": 1}),
                                                  "typed comparison"), "boolean replaces integer receipt"))
    return {"rejected": results, "count": len(results),
            "outside_code": {"entries_checked": 50176, "terms": len(outside_costs),
                             "term_costs": outside_costs, "cost": sum(outside_costs),
                             "new_term_cost": 1, "factors_sha256": digest([d, t]),
                             "not_a_cheaper_decoder_claim": True},
            "correlated_demand": {"C": [[1, 1], [1, 1]], "rank_C": 1,
                                  "input_blocks": 2, "output_blocks": 2, "cost": 64,
                                  "terms": 8, "entries_checked": 50176},
            "Gaussian_unit_phase_entries_checked": phase_entries,
            "crosstalk_passes_diagonal_only": True}


def generate():
    sources = source_pins()
    roots, planes = geometry()
    nrows = check_geometry(roots)
    geom = geometry_receipt(roots, planes, nrows)
    source_match = source_geometry(roots, geom, sources)
    counts = census(roots, nrows)
    fixtures = [fixture(roots, nrows, k, "canonical") for k in (1, 2, 3)]
    fixtures.extend(fixture(roots, nrows, k, "shared_same_coordinate") for k in (2, 3))
    fixtures.append(fixture(roots, nrows, 2, "shared_cross_coordinate"))
    fixtures.append(fixture(roots, nrows, 2, "overcomplete"))
    fixtures.append(fixture(roots, nrows, 1, "two_sided_coordinate_mixing"))
    return {"schema_version": 1, "claim": "Common-chart block-root-code copy optimum 64 rank(C); cost 8m+b; independent-call floor 64k",
            "scope": "all-pairs block-diagonal exactness; union support pricing; separate scalar totals",
            "sources": sources, "geometry": geom, "source_geometry_compatibility": source_match,
            "finite_premises": counts,
            "fixtures": fixtures, "controls": controls(roots, nrows, counts),
            "rectangular_coupling_fixture": rectangular_fixture(roots, nrows),
            "fixture_entries_checked": sum(f["matrix_entries_checked"] for f in fixtures),
            "fixture_off_diagonal_entries_checked": sum(f["off_diagonal_call_entries_checked"] for f in fixtures)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only RESULT.json")
    args = parser.parse_args()
    result = generate()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(canonical(result), encoding="utf-8", newline="\n")
    else:
        require(canonical(read_json(path)) == canonical(result), "complete typed RESULT.json mismatch")
    print("PASS_P112_BATCH_CENTRE_FLOOR: 511 exact hyperplanes; 64 exceptional pairings; "
          + str(result["fixture_entries_checked"]) + " fixture entries; "
          + str(result["controls"]["count"]) + " controls; charge >=64k")


if __name__ == "__main__":
    main()
