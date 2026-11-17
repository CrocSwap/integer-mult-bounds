"""Exact finite certificate for one rank-five-flat mode shadow."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PROJECTION = (
    (-2, 0, 1, 1, 1, 1, 0, 0),
    (-2, 1, 0, 1, 1, 0, 1, 0),
    (1, 0, 0, -1, -1, 0, 0, 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def rank(rows):
    matrix = [list(map(Fraction, row)) for row in rows]
    pivot = 0
    for column in range(len(matrix[0])):
        found = next((i for i in range(pivot, len(matrix))
                      if matrix[i][column]), None)
        if found is None:
            continue
        matrix[pivot], matrix[found] = matrix[found], matrix[pivot]
        scale = matrix[pivot][column]
        matrix[pivot] = [x / scale for x in matrix[pivot]]
        for i in range(pivot + 1, len(matrix)):
            scale = matrix[i][column]
            matrix[i] = [x - scale * y
                         for x, y in zip(matrix[i], matrix[pivot], strict=True)]
        pivot += 1
        if pivot == len(matrix):
            break
    return pivot


def load_rows():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    source = next(row for row in sources["files"] if row["usage"] == "input")
    source_path = ROOT / source["path"]
    require(source_path.stat().st_size < 2_000_000, "source exceeds input bound")
    payload = source_path.read_bytes()
    require(sha256(payload).hexdigest() == source["sha256"], "source hash")
    columns = json.loads(payload)["mode_columns"]
    require(len(columns) == 8, "eight modes required")
    require(all(len(c) == 112 for c in columns), "112 ports required")
    require(all(type(x) is int and x in (-1, 0, 1)
                for c in columns for x in c), "mode entry")
    return tuple(zip(*columns, strict=True))


def project(rows):
    require(rank(PROJECTION) == 3, "projection rank")
    require(rank(rows[:5]) == 5, "flat basis rank")
    raw = [tuple(dot(n, row) for n in PROJECTION) for row in rows]
    require(all(x % 2 == 0 for p in raw for x in p), "even projection")
    require(all(not any(p) for p in raw[:5]), "flat annihilation")
    flat = [i for i, p in enumerate(raw) if not any(p)]
    require(len(flat) == 15 and rank([rows[i] for i in flat]) == 5,
            "closed flat rank and cardinality")
    points, translation = [], [0, 0, 0]
    for p in raw:
        q = tuple(x // 2 for x in p)
        if next((x for x in q if x), 0) < 0:
            translation = [a + b for a, b in zip(translation, q, strict=True)]
            q = tuple(-x for x in q)
        points.append(q)
    require(all(tuple(int(i == j) for i in range(3)) in points
                for j in range(3)), "quotient lattice is Z^3")
    return points, flat, translation


def product_size(sizes):
    return sizes[0] * sizes[1] * sizes[2]


def geometry(points):
    require(3 <= len(points) <= 112, "generator bound")
    require(all(len(p) == 3 and all(type(x) is int and abs(x) <= 8 for x in p)
                for p in points), "bounded integer generators")
    lo = tuple(sum(min(0, p[i]) for p in points) for i in range(3))
    hi = tuple(sum(max(0, p[i]) for p in points) for i in range(3))
    sizes = tuple(b - a + 1 for a, b in zip(lo, hi, strict=True))
    require(product_size(sizes) <= 500_000, "box capacity")
    strides = (1, sizes[0], sizes[0] * sizes[1])
    normals = set()
    for a, b in combinations(sorted(set(points)), 2):
        n = (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2],
             a[0]*b[1] - a[1]*b[0])
        divisor = gcd(*n)
        if divisor:
            n = tuple(x // divisor for x in n)
            if next(x for x in n if x) < 0:
                n = tuple(-x for x in n)
            normals.add(n)
    require(rank(sorted(normals)) == 3, "full-dimensional zonotope")
    facets = []
    for n in sorted(normals):
        values = [dot(n, p) for p in points]
        facets.append((n, sum(min(0, x) for x in values),
                       sum(max(0, x) for x in values)))
    return lo, hi, sizes, strides, facets


def encode(point, lo, strides):
    return sum((x - a) * s for x, a, s in zip(point, lo, strides, strict=True))


def subset_bits(points, geo):
    lo, _, sizes, strides, _ = geo
    bits = 1 << encode((0, 0, 0), lo, strides)
    for point in points:
        shift = dot(point, strides)
        bits |= bits << shift if shift >= 0 else bits >> -shift
    require(bits.bit_length() <= product_size(sizes), "subset box overflow")
    return bits


def subset_set(points):
    reached = {(0, 0, 0)}
    for a, b, c in points:
        shifted = {(x+a, y+b, z+c) for x, y, z in reached}
        reached.update(shifted)
        require(len(reached) <= 500_000, "subset set capacity")
    return reached


def scan(geo, bits, strict):
    lo, hi, _, strides, facets = geo
    count = holes = 0
    first = None
    for z in range(lo[2], hi[2] + 1):
        for y in range(lo[1], hi[1] + 1):
            left, right = lo[0], hi[0]
            for (a, b, c), low, high in facets:
                low, high = low + strict, high - strict
                offset = b*y + c*z
                if a == 0:
                    if not low <= offset <= high:
                        left, right = 1, 0
                        break
                else:
                    if a < 0:
                        a, low, high, offset = -a, -high, -low, -offset
                    left = max(left, -((offset-low) // a))
                    right = min(right, (high-offset) // a)
            if left <= right:
                width = right - left + 1
                mask = (1 << width) - 1
                position = encode((left, y, z), lo, strides)
                count += width
                holes += (mask ^ ((bits >> position) & mask)).bit_count()
                if first is None:
                    first = position
    return count, holes, first


def direct_scan(geo, reached):
    lo, hi, _, _, facets = geo
    closed = interior = 0
    for p in product(*(range(a, b+1) for a, b in zip(lo, hi, strict=True))):
        values = [(dot(n, p), low, high) for n, low, high in facets]
        inside = all(low <= v <= high for v, low, high in values)
        require(inside == (p in reached), "direct point membership")
        closed += inside
        interior += all(low < v < high for v, low, high in values)
    return closed, interior


def controls(geo, bits, interior):
    position = interior[2]
    require(position is not None and (bits >> position) & 1, "interior fixture")
    damaged = bits ^ (1 << position)
    require(scan(geo, damaged, 0)[1] == 1, "deleted subset, closed control")
    require(scan(geo, damaged, 1)[1] == 1, "deleted subset, interior control")
    toy = [(1, -3, 0), (1, -2, 0), (1, 0, 0), (0, 0, 1), (0, 0, 1)]
    toy_geo = geometry(toy)
    toy_bits = subset_bits(toy, toy_geo)
    require(scan(toy_geo, toy_bits, 0)[:2] == (30, 6), "closed holes control")
    require(scan(toy_geo, toy_bits, 1)[:2] == (4, 2), "interior holes control")
    reached = subset_set(toy)
    lo, _, _, strides, _ = toy_geo
    require(sum(1 << encode(p, lo, strides) for p in reached) == toy_bits,
            "signed shifts control")
    return 5


def main():
    rows = load_rows()
    points, flat, translation = project(rows)
    geo = geometry(points)
    require(geo[:3] == ((0, -1, -49), (86, 85, 5), (87, 87, 55)), "box")
    require(len(geo[4]) == 25, "facet-normal count")
    bits = subset_bits(points, geo)
    reached = subset_set(points)
    lo, _, _, strides, _ = geo
    independent_bits = sum(1 << encode(p, lo, strides) for p in reached)
    require(bits == independent_bits, "independent subset enumeration")
    closed, interior = scan(geo, bits, 0), scan(geo, bits, 1)
    require(closed[:2] == (103333, 0), "closed filling certificate")
    require(interior[:2] == (94599, 0), "interior filling certificate")
    require(direct_scan(geo, reached) == (103333, 94599), "independent scan")
    control_count = controls(geo, bits, interior)
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    receipt = {
        "status": "PASS_MODE_RANK_FIVE_SHADOW", "flat_indices": flat,
        "translation": translation, "closed_points": closed[0],
        "interior_points": interior[0], "subset_sums": len(reached),
        "box_points": product_size(geo[2]), "facet_normal_pairs": len(geo[4]),
        "controls": control_count,
        "generator_histogram": [[list(p), n] for p, n in sorted(Counter(points).items())],
        "subset_sha256": sha256(bits.to_bytes((bits.bit_length()+7)//8, "little")).hexdigest(),
        "package_sha256": {name: sha256((PACKAGE/name).read_bytes()).hexdigest()
                           for name in files},
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
