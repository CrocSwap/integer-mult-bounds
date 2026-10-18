"""Sharp outside-span A2 joint capacity. Standard library; Apache-2.0."""

import json
import runpy
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
MANIFEST_HASH = "b077ee52590c8cf361546b049fa625f82ffde8e88a10e94f52d6c144a8893714"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_regular(path):
    require(not path.is_symlink() and path.is_file(), "regular input required")
    require(path.stat().st_size <= 100_000, "input byte bound")
    return path.read_bytes()


def authenticate(root=ROOT, package=PACKAGE, manifest=None):
    if manifest is None:
        manifest = json.loads(read_regular(package / "SOURCES.json"))
    canonical = json.dumps(manifest, sort_keys=True).encode()
    require(sha256(canonical).hexdigest() == MANIFEST_HASH, "source inventory")
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = read_regular(root / row["path"])
            require(sha256(raw).hexdigest() == row["sha256"], "live source hash")
    for row in manifest["retained_files"]:
        raw = read_regular(package / row["local_path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(sha256(raw).hexdigest() == row["sha256"], "retained source hash")
        require(sha1(blob).hexdigest() == row["git_blob"], "retained Git blob")


def basis(values):
    require(len(values) <= 512, "binary collection bound")
    rows = []
    for value in values:
        require(type(value) is int and 0 <= value < 512, "nine-bit integer")
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted(rows + [value], reverse=True)
    return tuple(rows)


def span(rows):
    require(len(rows) <= 9 and len(basis(rows)) == len(rows), "bounded basis")
    result = [0]
    for row in rows:
        result += [x ^ row for x in result]
    require(len(set(result)) == 1 << len(rows), "span cardinality")
    return tuple(result)


def model():
    authenticate()
    g = runpy.run_path(str(ROOT / GEOMETRY))
    roots, _, live, coordinates = g["root_data"]()
    labels = tuple(1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c))
                   for c in coordinates)
    prior = json.loads(read_regular(PACKAGE / "vendor/pr3288-RESULT.json"))
    fiber = frozenset(prior["canonical_fiber"])
    require(len(fiber) == 27 and fiber <= set(labels), "canonical fiber labels")
    found = False
    for a, b in combinations(roots, 2):
        if abs(g["dot"](a, b)) != 4:
            continue
        group = {label for root, label in zip(roots, labels, strict=True)
                 if g["dot"](a, root) == 0 and g["dot"](b, root) != 0}
        if group == fiber:
            found = True
            break
    require(found, "fixture is not an A2 projective fiber")
    return frozenset(labels), frozenset(live), fiber, g["SIMPLE"]


def quadratic(simple):
    edges = tuple((i, j) for i, j in combinations(range(8), 2)
                  if sum(x * y for x, y in zip(simple[i], simple[j], strict=True))
                  // 4 % 2)
    return tuple((x.bit_count() + sum((x >> i & 1) * (x >> j & 1)
                                    for i, j in edges)) % 2 for x in range(256))


def affine_data(space, q):
    affine = tuple(x >> 1 for x in sorted(space) if x & 1)
    require(bool(affine), "empty affine section")
    origin = affine[0]
    direction = basis(tuple(x ^ origin for x in affine))
    polar = tuple(sum((q[x ^ y] ^ q[x] ^ q[y]) << i
                      for i, y in enumerate(direction)) for x in direction)
    return len(direction), len(basis(polar)), sum(1 - 2 * q[x] for x in affine)


def codimension_two():
    """All 2667 two-equation kernels in seven coordinates, RREF dual rows."""
    count = 0
    for pivots in combinations(range(7), 2):
        choices = []
        for pivot in pivots:
            free = tuple(i for i in range(pivot) if i not in pivots)
            choices.append(tuple((1 << pivot) | sum((code >> i & 1) << j
                                 for i, j in enumerate(free))
                                 for code in range(1 << len(free))))
        for a, b in product(*choices):
            count += 1
            yield tuple(x for x in range(128)
                        if not (x & a).bit_count() % 2
                        and not (x & b).bit_count() % 2)
    require(count == 2667, "dual RREF coverage")


def extensions(u, w):
    seen = set()
    count = 0
    for t in range(512):
        if t in w or t in seen:
            continue
        coset = frozenset(x ^ t for x in u)
        seen.update(coset)
        count += 1
        yield u | coset
    require(count == 12, "outside extension count")


def census(roots, live, fiber, q):
    w_order = span(basis(tuple(fiber)))
    w = frozenset(w_order)
    missing = (roots & w) - fiber
    require(len(w) == 128 and len(missing) == 1, "A2 seven-space model")
    require(affine_data(w, q) == (6, 6, 8), "positive affine six-space")
    histogram, u_hist = Counter(), Counter()
    equality, live_equality, witness = 0, 0, None
    for coordinates in codimension_two():
        u = frozenset(w_order[x] for x in coordinates)
        j = len(u & fiber)
        u_hist[j] += 1
        eligible = j == 10
        if eligible:
            require(affine_data(u, q) == (4, 4, -4), "equality four-section")
            require(not u & missing, "missing root in equality section")
        local_equality = 0
        for v in extensions(u, w):
            m = len(v & roots)
            score = m + j
            require(score <= 30, "outside joint upper bound")
            histogram[score] += 1
            if score == 30:
                require(eligible and m == 20, "equality classification")
                equality += 1
                local_equality += 1
                if v & roots <= live:
                    live_equality += 1
                    if witness is None:
                        witness = {"basis": list(basis(tuple(sorted(v)))),
                                   "support": sorted(v & roots),
                                   "fiber_support": sorted(v & fiber)}
        require(local_equality == (5 if eligible else 0), "five extensions")
    require(sum(histogram.values()) == 32004 and equality == 1080, "census totals")
    require(live_equality == 144 and witness is not None, "actual P112 attainment")
    return {"outside_intersection5_spaces": 32004, "full_equality": equality,
            "canonical_P112_equality": live_equality,
            "joint_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "fiber_intersection_histogram": {str(k): v for k, v in sorted(u_hist.items())},
            "witness": witness}


def verify():
    roots, live, fiber, simple = model()
    q = quadratic(simple)
    require(roots == frozenset(1 | x << 1 for x in range(256) if q[x]),
            "quadratic root binding")
    require(sum(1 - 2 * x for x in q) == 16, "ambient Gauss sign")
    result = census(roots, live, fiber, q)
    result.update(schema_version=1, canonical_fiber=sorted(fiber), sharp_bound=30)
    expected = json.loads(read_regular(PACKAGE / "RESULT.json"))
    require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "result receipt changed")
    print("PASS_E8_A2_OUTSIDE_RANK6 full=1080 canonical_P112=144 sharp=30")
    return result


if __name__ == "__main__":
    verify()
