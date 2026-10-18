#!/usr/bin/env python3
"""Exact premises for the P112 two-product compensation proof.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Geometry: DreamingOfClouds PR717; exact snapshot: Mihir Srivastava PR845.
The three-product survivor premise is credited to Cinna Davis PR1373.
No predecessor code is imported; no floating-point arithmetic is used.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p112-single-lift/reference-geometry.json"
PAIR = (4, 6)
NORMALS = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def basis(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return [pivots[p] for p in sorted(pivots)]


def rank(rows):
    return len(basis(rows))


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def support(values):
    return sum(1 << i for i, value in enumerate(values) if value)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def root_key(row):
    row = tuple(row)
    return row if next(x for x in row if x) > 0 else tuple(-x for x in row)


def load_source():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        raw = (ROOT / entry["path"]).read_bytes()
        require(digest(raw) == entry["sha256"], "source SHA256 drift: " + entry["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == entry["git_blob"], "source Git blob drift: " + entry["path"])
    return json.loads((ROOT / SOURCE).read_text())


def geometry(source):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    for tail in product((-1, 1), repeat=7):
        r = (1, *tail)
        if r.count(-1) % 2 == 0:
            roots.add(r)
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [0] * 8
            r[i], r[i + 1] = 2, 2 * sign
            frame.append(r)
    require(len(roots) == 120, "E8 line coverage")
    roots = sorted(roots - {tuple(r) for r in frame})
    require(frame == source["frame"], "frame order")
    require(set(roots) == {root_key(r) for r in source["roots"]}, "root source binding")
    require(len(roots) == 112, "P112 coverage")
    require(all(dot(r, f) % 4 == 0 for r in roots for f in frame), "integral frame coordinates")
    x = [[dot(r, f) // 4 for f in frame] for r in roots]
    require(all(sum(row[i] * row[j] for row in x) == 56 * (i == j)
                for i in range(8) for j in range(8)), "X^T X = 56I")
    source_index = {root_key(r): i for i, r in enumerate(source["roots"])}
    for r, row in zip(roots, x):
        i = source_index[r]
        sign = 1 if tuple(source["roots"][i]) == r else -1
        require(row == [sign * z for z in source["X"][i]], "X source binding")
        require(set(row) <= {-1, 0, 1} and dot(row, row) == 4, "coordinate alphabet")
    b = []
    for i, r in enumerate(roots):
        row = 0
        for j, s in enumerate(roots):
            require(dot(r, s) % 4 == 0, "integral Gram")
            gram = dot(r, s) // 4
            require(dot(x[i], x[j]) == 2 * gram, "XX^T = 2G")
            row |= ((1 + gram) % 2) << j
        b.append(row)
    require(rank(b) == 9 and len(set(b)) == 112 and all(b), "distinct nonzero rank-nine rows")
    require(all(b[i] >> i & 1 for i in range(112)), "affine diagonal")
    return roots, x, b


def finite_premises(x, b):
    coordinate_masks = [support(row[j] for row in x) for j in range(8)]
    coordinate_ranks = [rank(b[i] & mask for i in indices(mask)) for mask in coordinate_masks]
    require(coordinate_ranks == [8] * 8, "all eight baseline coordinate charges")
    masks = [support(a * row[PAIR[0]] + c * row[PAIR[1]] for row in x)
             for a, c in NORMALS]
    words = [0]
    for row in basis(b):
        words += [w ^ row for w in words]
    require(len(set(words)) == 512, "complete binary character space")
    strata = []
    for n, mask in zip(NORMALS, masks):
        hist = Counter((word & mask).bit_count() for word in words if word)
        distance = min(k for k in hist if k)
        dimension = rank(b[i] for i in indices(mask))
        require(dimension >= 8 and distance > 3, "small-erasure premise")
        strata.append({"normal": list(n), "support_size": mask.bit_count(),
                       "span_dimension": dimension, "erasure_distance": distance,
                       "character_weight_histogram": dict(sorted(hist.items()))})
    require([r["span_dimension"] for r in strata] == [8, 8, 9, 9, 9], "stratum dimensions")
    require([r["erasure_distance"] for r in strata] == [24, 24, 12, 12, 24], "stratum distances")
    slices = [[mask & b[j] for j in range(112)] for mask in masks]
    free_pairs = [(i, j) for i in range(112) for j in range(112) if not (b[i] >> j & 1)]
    require(len(free_pairs) == 5824, "all free port pairs")
    records, one_trace, two_trace = [], bytearray(), bytearray()
    for a, left in enumerate(masks):
        for c, right in enumerate(masks):
            original = rank(b[i] & right for i in indices(left))
            require(original >= 8, "unperturbed term floor")
            one = [rank(b[i] & right for i in indices(slices[a][j])) for j in range(112)]
            require(min(one) >= 7, "one-sided survivor floor")
            # Projection of any row basis spans the restricted matrix.
            row_bases = [basis(b[i] for i in indices(slices[a][j])) for j in range(112)]
            two = [rank(row & slices[c][i] for row in row_bases[j]) for i, j in free_pairs]
            expected = 4 + sum(t != 0 for t in NORMALS[a]) + sum(t != 0 for t in NORMALS[c])
            require(min(two) == expected, "PR1373 two-sided survivor premise")
            one_trace.extend(one)
            two_trace.extend(two)
            records.append({"left": a, "right": c, "original_rank": original,
                            "one_sided_histogram": dict(sorted(Counter(one).items())),
                            "one_sided_minimum": min(one), "one_sided_witness": one.index(min(one)),
                            "two_sided_histogram": dict(sorted(Counter(two).items())),
                            "two_sided_minimum": min(two),
                            "two_sided_witness": list(free_pairs[two.index(min(two))])})
    require(len(one_trace) == 2800 and len(two_trace) == 145600, "full survivor coverage")
    return {"coordinate_pair": list(PAIR), "ports": 112, "pairing_rank": rank(b),
            "baseline_coordinate_ranks": coordinate_ranks,
            "pairing_sha256": digest(canonical(b)), "strata": strata,
            "character_evaluations": 2555, "free_port_pairs": len(free_pairs),
            "one_sided_records": len(one_trace), "one_sided_sha256": digest(one_trace),
            "two_sided_records": len(two_trace), "two_sided_sha256": digest(two_trace),
            "pairs": records}


@dataclass(frozen=True)
class QI:
    real: Fraction
    imag: Fraction = Fraction(0)

    def __add__(self, other):
        other = qi(other)
        return QI(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return QI(-self.real, -self.imag)

    def __sub__(self, other):
        return self + -qi(other)

    def __mul__(self, other):
        other = qi(other)
        return QI(self.real * other.real - self.imag * other.imag,
                  self.real * other.imag + self.imag * other.real)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = qi(other)
        den = other.real * other.real + other.imag * other.imag
        require(bool(den), "division by zero")
        return self * QI(other.real / den, -other.imag / den)

    def __bool__(self):
        return bool(self.real or self.imag)


def qi(value):
    return value if isinstance(value, QI) else QI(Fraction(value))


def inverse(matrix):
    n = len(matrix)
    rows = [[qi(t) for t in row] + [qi(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        z = rows[j][j]
        rows[j] = [t / z for t in rows[j]]
        for i in range(n):
            if i != j:
                z = rows[i][j]
                rows[i] = [a - z * c for a, c in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def multiply(a, c):
    return [[sum((qi(u) * v for u, v in zip(row, col)), qi(0)) for col in zip(*c)] for row in a]


def factors(x, u, v, matrix):
    invt = transpose(inverse(matrix))
    left = multiply([[row[4], row[6], z] for row, z in zip(x, u)], matrix)
    right = multiply([[row[4], row[6], z] for row, z in zip(x, v)], invt)
    active = sum(any(matrix[i][j] for i in (0, 1)) and any(invt[i][j] for i in (0, 1))
                 for j in range(3))
    require(active in (2, 3), "projected rank-two identity")
    return left, right, active


def free_rectangle(u, v, b):
    um, vm = support(u), support(v)
    require(um and vm, "rectangle factors must be nonzero")
    require(all(not (b[i] & vm) for i in indices(um)), "rectangle is not free")


def check_identity(left, right, x, u, v):
    for i in range(112):
        for j in range(112):
            expected = qi(x[i][4] * x[j][4] + x[i][6] * x[j][6]) + qi(u[i]) * v[j]
            actual = sum((a * c for a, c in zip(left[i], right[j])), qi(0))
            require(actual == expected, "ordinary-transpose factor identity")


def costs(left, right, b):
    return [rank(b[i] & support(c) for i in indices(support(a)))
            for a, c in zip(transpose(left), transpose(right))]


def reject(fn, message):
    try:
        fn()
    except (ValueError, ZeroDivisionError):
        return message
    raise ValueError("negative control unexpectedly accepted: " + message)


def fixtures(x, b):
    z, e = [0] * 112, [int(i == 46) for i in range(112)]
    partner = next(i for i in range(112) if not (b[i] >> 46 & 1))
    u = [int(i == partner) for i in range(112)]
    large = [-row[4] if not (b[i] >> 46 & 1) else 0 for i, row in enumerate(x)]
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    imag = QI(Fraction(0), Fraction(1))
    cases = [
        ("sharp-free-singleton", u, e, identity),
        ("dense-triangular", u, e, [[1, 1, 0], [1, -1, 0], [2, 3, 1]]),
        ("large-rectangle", large, e, [[1, 1, 0], [0, 1, 0], [1, 2, 1]]),
        ("compensation-is-required", large, e, [[1, 0, 0], [0, 1, 0], [1, 0, 1]]),
        ("transpose-branch", e, large, [[1, 0, 1], [0, 1, -1], [0, 0, 1]]),
        ("three-products", u, e, [[1, 0, 1], [0, 1, 1], [1, 1, 3]]),
        ("nonreal-rescaling", u, e, [[imag, 0, 0], [0, 1, 0], [0, 0, 1]]),
    ]
    results, saved = [], {}
    for name, a, c, matrix in cases:
        free_rectangle(a, c, b)
        left, right, active = factors(x, a, c, matrix)
        check_identity(left, right, x, a, c)
        ranks = costs(left, right, b)
        require(sum(ranks) >= 16, "fixture COPY floor")
        if active == 3:
            require(min(ranks) >= 6, "three-product fixture floor")
        results.append({"name": name, "rectangle_size": [support(a).bit_count(), support(c).bit_count()],
                        "projected_products": active, "copy_ranks": ranks, "matrix_entries": 12544})
        saved[name] = (left, right, a, c)
    require(results[0]["copy_ranks"] == [8, 8, 0], "sharp attainment")
    omission = next(r for r in results if r["name"] == "compensation-is-required")
    require(omission["copy_ranks"] == [7, 8, 7], "compensation omission witness")
    controls = []
    controls.append(reject(lambda: free_rectangle(e, e, b), "nonfree-diagonal"))
    controls.append(reject(lambda: free_rectangle(z, e, b), "zero-rectangle-factor"))
    controls.append(reject(lambda: inverse([[1, 0, 1], [0, 1, 0], [1, 0, 1]]), "singular-factor-change"))
    left, right, a, c = saved["compensation-is-required"]
    omitted = [[row[0], row[1], qi(0)] for row in left]
    controls.append(reject(lambda: check_identity(omitted, right, x, a, c), "omitted-compensation-identity"))
    controls.append(reject(lambda: require(48 + sum(omission["copy_ranks"]) == 63, "complete bill is 70"),
                           "omitted-compensation-invoice-63-versus-70"))
    left, right, a, c = saved["nonreal-rescaling"]
    conjugated = [[QI(t.real, -t.imag) for t in row] for row in right]
    controls.append(reject(lambda: check_identity(left, conjugated, x, a, c), "conjugate-instead-of-ordinary-transpose"))
    boundary_m = [[1, 0, 1], [0, 1, 1], [1, 0, 2]]
    boundary_v = [row[4] for row in x]
    left, right, active = factors(x, z, boundary_v, boundary_m)
    check_identity(left, right, x, z, boundary_v)
    boundary_costs = costs(left, right, b)
    require(active == 3 and boundary_costs == [8, 8, 0], "zero-factor boundary")
    controls.append(reject(lambda: require(min(boundary_costs) >= 6, "zero-factor boundary has rank zero"),
                           "three-products-without-nonzero-rectangle"))
    require([Fraction(3, 4) * a + Fraction(1, 8) * c + Fraction(1, 8) * d
             for a, c, d in zip((8, 8, 0), (8, 0, 8), (0, 8, 8))] == [7, 7, 2],
            "concavity witness")
    require(2 * 7 ** 2 + 2 ** 2 < 2 * 8 ** 2, "out-of-range power boundary")
    controls.append(reject(lambda: require(2 * 7 ** 2 + 2 ** 2 >= 2 * 8 ** 2, "q=2 outside theorem"),
                           "power-exponent-outside-zero-one"))
    return {"cases": results, "entry_checks": 8 * 12544,
            "zero_factor_boundary": {"projected_products": active, "copy_ranks": boundary_costs},
            "omission_invoice": {"six_unchanged": 48, "falsely_omitting_compensation": 63, "complete": 70},
            "concavity_combination": {"weights": ["3/4", "1/8", "1/8"], "result": [7, 7, 2]},
            "negative_controls": controls}


def build():
    source = load_source()
    roots, x, b = geometry(source)
    result = {"schema_version": 1, "status": "scoped-copy-obstruction-no-new-kappa",
              "base_commit": json.loads((HERE / "SOURCES.json").read_text())["base_commit"],
              "geometry_source_sha256": digest((ROOT / SOURCE).read_bytes()),
              "root_order": "lexicographic, first nonzero coordinate positive, twice-E8 roots",
              "root_order_sha256": digest(canonical(roots)),
              "finite": finite_premises(x, b), "fixtures": fixtures(x, b)}
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new certificate; refuse overwrites")
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2)
            output.write("\n")
    else:
        require(result == json.loads(args.check.read_text()), "complete certificate mismatch")
    print("PASS_P112_TWO_PRODUCT_COMPENSATION strata=5 characters=2555 one_sided=2800 "
          "three_product_records=145600 fixtures=8 controls=8 copy_floor=64 no_new_kappa")


if __name__ == "__main__":
    main()
