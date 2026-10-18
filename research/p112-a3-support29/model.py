"""Exact finite premises for robust A3 shortening. Apache-2.0.

Root/label conventions and simplex normalization follow Nick Petalas's
PR3221/3227 and the retained E8/P112 lineage. The defect budget is new here.
"""

import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry():
    """Authenticate the one explicit source before loading its definitions."""
    sources = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    path = REPO / "research/p112-ten-piece-simplex/geometry.py"
    rows = [r for r in sources["files"] if r["path"] == str(path.relative_to(REPO))]
    require(len(rows) == 1, "geometry source pin")
    require(path.is_file() and not path.is_symlink(), "geometry source file")
    require(path.stat().st_size <= 20_000, "geometry source capacity")
    require(
        hashlib.sha256(path.read_bytes()).hexdigest() == rows[0]["sha256"],
        "geometry source hash",
    )
    spec = importlib.util.spec_from_file_location("p112_support29_geometry", path)
    require(spec is not None and spec.loader is not None, "geometry loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def span(labels):
    require(
        len(labels) <= 120 and all(type(x) is int and 0 < x < 512 for x in labels),
        "binary label domain",
    )
    result = {0}
    for label in labels:
        result.update(tuple(x ^ label for x in result))
    require(len(result) <= 512, "binary span capacity")
    return result


def star_data(g):
    roots, _, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    star = tuple(tuple(2 * int(i in (0, j)) for i in range(8)) for j in range(1, 4))
    require(all(g.dot(r, h) % 4 == 0 for r in roots for h in star), "star divisibility")
    values = tuple((0, *(g.dot(r, h) // 4 for h in star)) for r in roots)
    costs = tuple(4 - max(Counter(v).values()) for v in values)
    require(Counter(costs) == {0: 20, 1: 64, 2: 36}, "A3 cost spectrum")
    groups = [[] for _ in range(4)]
    for i, value in enumerate(values):
        if costs[i] == 1:
            common = next(x for x in value if value.count(x) == 3)
            groups[next(j for j, x in enumerate(value) if x != common)].append(i)
    require(
        len(set(labels)) == 120 and all(len(x) == 16 for x in groups),
        "singleton partition",
    )
    return roots, labels, star, values, costs, groups


def star_orbits(g, roots):
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    prefix, counts = (), []
    for expected in (240, 56, 27):
        candidates = {r for r in signed if all(g.dot(r, a) == 4 for a in prefix)}
        normals = tuple(r for r in roots if all(g.dot(r, a) == 0 for a in prefix))
        first = min(candidates)
        queue, seen = [first], {first}
        for index in range(240):
            if index >= len(queue):
                break
            for normal in normals:
                d = g.dot(queue[index], normal)
                require(d % 4 == 0, "integral reflection")
                image = tuple(
                    x - d // 4 * y for x, y in zip(queue[index], normal, strict=True)
                )
                require(image in candidates, "pointwise stabilizer image")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 240, "orbit capacity")
        require(seen == candidates and len(seen) == expected, "A3 orbit coverage")
        prefix += (first,)
        counts.append(expected)
    return counts


def label_actions(g, roots, labels):
    by_root = dict(zip(roots, labels, strict=True))
    for j, normal in enumerate(g.SIMPLE):
        cartan = tuple(g.dot(a, normal) // 4 for a in g.SIMPLE)
        for root, label in zip(roots, labels, strict=True):
            d = g.dot(root, normal)
            require(d % 4 == 0, "root reflection divisibility")
            image = g.canonical(
                tuple(x - d // 4 * y for x, y in zip(root, normal, strict=True))
            )
            parity = sum(((label >> (i + 1)) & 1) * cartan[i] for i in range(8)) % 2
            require(by_root[image] == label ^ (parity << (j + 1)), "binary Weyl action")
    return 960


def six_flat_capacity(labels):
    """All RREF three-dimensional annihilators in nine binary dimensions."""
    require(len(labels) == len(set(labels)) == 120, "flat inventory")
    zero = tuple(
        sum(1 << i for i, x in enumerate(labels) if (normal & x).bit_count() % 2 == 0)
        for normal in range(512)
    )
    histogram = Counter()
    for pivots in combinations(range(9), 3):
        free = tuple(
            (r, j)
            for r, p in enumerate(pivots)
            for j in range(p + 1, 9)
            if j not in pivots
        )
        require(len(free) <= 18, "RREF capacity")
        for bits in range(1 << len(free)):
            rows = [1 << j for j in pivots]
            for k, (r, j) in enumerate(free):
                rows[r] |= ((bits >> k) & 1) << j
            histogram[(zero[rows[0]] & zero[rows[1]] & zero[rows[2]]).bit_count()] += 1
    require(
        sum(histogram.values()) == 788035 and max(histogram) == 20,
        "complete six-flat capacity",
    )
    return dict(sorted(histogram.items()))


def frames(g, roots):
    adjacency = tuple(
        sum(1 << j for j in range(i + 1, 120) if g.dot(r, roots[j]) == 0)
        for i, r in enumerate(roots)
    )
    stack, result = [((), (1 << 120) - 1)], []
    for visited in range(400_000):
        if not stack:
            require(visited == 352876 and len(result) == 2025, "frame coverage")
            return result
        prefix, candidates = stack.pop()
        if len(prefix) == 8:
            result.append(prefix)
        else:
            for j in range(120):
                if candidates >> j & 1:
                    stack.append((prefix + (j,), candidates & adjacency[j]))
        require(len(stack) <= 1000 and len(result) <= 2025, "frame capacity")
    raise ValueError("frame iteration budget exhausted")


def singleton_facts(labels, groups):
    rows = []
    for group in groups:
        binary = span(tuple(labels[i] for i in group))
        closure = tuple(i for i, x in enumerate(labels) if x in binary)
        require(len(binary) == 64 and closure == tuple(group), "full singleton closure")
        restrictions = {
            sum(
                1 << j
                for j, i in enumerate(group)
                if (normal & labels[i]).bit_count() % 2 == 0
            )
            for normal in range(512)
        }
        restrictions.discard((1 << 16) - 1)
        histogram = Counter(mask.bit_count() for mask in restrictions)
        require(
            len(restrictions) == 63 and max(histogram) == 10, "proper-hyperplane bound"
        )
        rows.append(
            {
                "indices": group,
                "rank": 6,
                "closure": closure,
                "hyperplane_histogram": dict(sorted(histogram.items())),
            }
        )
    return rows


def puncture_facts(frame_list, costs, groups):
    singleton = {i for group in groups for i in group}
    histogram = Counter(
        (sum(costs[i] for i in frame), len(singleton.intersection(frame)))
        for frame in frame_list
    )
    require(
        set(histogram) == {(8, 0), (8, 4), (8, 8), (10, 4), (12, 0)},
        "puncture cost/singleton pairs",
    )
    require(sum(histogram.values()) == 2025, "puncture histogram coverage")
    return [
        {"cost": f, "singletons": t, "count": n}
        for (f, t), n in sorted(histogram.items())
    ]


def defect_bounds(support, frame_cost, frame_singletons, unpinned):
    require(type(support) is int and 0 <= support <= 30, "common support domain")
    require(
        (frame_cost, frame_singletons) in {(8, 0), (8, 4), (8, 8), (10, 4), (12, 0)},
        "puncture domain",
    )
    require(type(unpinned) is int and 0 <= unpinned <= 4, "unpinned endpoint domain")
    baseline = 136 - frame_cost - 2 * support
    lower = baseline + max(0, 6 * unpinned - frame_singletons)
    upper = 64 + 4 * unpinned
    return lower, upper


def budget_table(support, punctures):
    return [
        {
            "frame_cost": row["cost"],
            "frame_singletons": row["singletons"],
            "unpinned": u,
            "lower": defect_bounds(support, row["cost"], row["singletons"], u)[0],
            "upper": defect_bounds(support, row["cost"], row["singletons"], u)[1],
        }
        for row in punctures
        for u in range(5)
    ]


def rational_rank(matrix):
    require(len(matrix) <= 42 and all(len(r) == 112 for r in matrix), "rank capacity")
    rows, rank = [[Fraction(x) for x in r] for r in matrix], 0
    for column in range(112):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            if scale:
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[rank], strict=True)
                ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def boundary_witness(roots, labels, values, costs, frame_list):
    frame = min(f for f in frame_list if sum(costs[i] for i in f) == 12)
    live = tuple(i for i in range(120) if i not in frame)
    common = tuple(i for i in live if costs[i] == 2)
    endpoints = [[0] * 112 for _ in range(4)]
    for column, i in enumerate(live):
        if i in common:
            continue
        value = values[i]
        mode = max(set(value), key=value.count)
        for j in range(4):
            endpoints[j][column] = value[j] - mode
    small = [[int(i == selected) for i in live] for selected in common]
    code = [[roots[i][j] for i in live] for j in range(8)]
    supports = [tuple(live[j] for j, x in enumerate(q) if x) for q in endpoints]
    require(
        len(common) == 30 and all(len(s) == 16 for s in supports), "witness support"
    )
    require(
        all(len(span(tuple(labels[i] for i in s))) == 64 for s in supports),
        "witness binary rank",
    )
    for j in range(1, 4):
        require(
            all(
                endpoints[j][k] - endpoints[0][k] == values[i][j]
                for k, i in enumerate(live)
                if i not in common
            ),
            "witness code identity",
        )
    piece_rank = rational_rank(small + endpoints)
    code_rank = rational_rank(code)
    union_rank = rational_rank(small + endpoints + code)
    intersection = piece_rank + code_rank - union_rank
    require(
        (piece_rank, code_rank, union_rank, intersection) == (34, 8, 39, 3),
        "witness intersection rank",
    )
    return {
        "frame": frame,
        "live": live,
        "common": common,
        "endpoints": endpoints,
        "endpoint_supports": supports,
        "piece_rank": piece_rank,
        "code_rank": code_rank,
        "union_rank": union_rank,
        "intersection_dimension": intersection,
    }
