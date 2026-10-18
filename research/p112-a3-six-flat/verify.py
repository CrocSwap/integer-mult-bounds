"""Check the P112 A3 six-flat equality obstruction. Apache-2.0."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from geometry import (
    SIMPLE,
    chamber_receipt,
    dot,
    require,
    root_data,
    root_plane_receipt,
)

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked JSON")
    require(path.stat().st_size <= 100_000, "JSON capacity")
    return json.loads(path.read_bytes())


def archived_source_check(sources):
    rows = sources["archived_sources"]
    require(len(rows) == 2 and {r["local_path"] for r in rows}
            == {"original-bk1b.py", "caller-data.json"}, "archive inventory")
    head = sources["predecessors"][0]["head"]
    for row in rows:
        require(row["pin"] == "head:" + head + ":" + row["path"], "archive origin pin")
        path = PACKAGE / row["local_path"]
        require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 20_000,
                "archive source capacity")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "archive SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "archive Git blob")


def source_check():
    sources = read_json(PACKAGE / "SOURCES.json")
    origin = sources["retained_geometry"]
    rows = [r for r in sources["files"] if r["path"] == origin["origin_path"]]
    require(len(rows) == 1 and rows[0]["usage"] == "provenance", "geometry pin")
    path = PACKAGE / "geometry.py"
    require(path.is_file() and not path.is_symlink(), "missing or linked geometry")
    require(path.stat().st_size <= 20_000, "geometry capacity")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == origin["sha256"] == rows[0]["sha256"],
            "geometry hash")
    archived_source_check(sources)
    caller = sources["retained_caller"]
    rows = [r for r in sources["archived_sources"] if r["path"] == caller["origin_path"]]
    require(len(rows) == 1 and rows[0]["usage"] == "provenance", "caller pin")
    path = PACKAGE / "caller-data.json"
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 20_000,
            "caller source capacity")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == caller["sha256"]
            == rows[0]["sha256"], "caller source hash")


def binary_span(values):
    require(len(values) <= 120 and all(0 < x < 512 for x in values), "label domain")
    basis = [0] * 9
    for value in values:
        for pivot in range(8, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    generators = tuple(x for x in basis if x)
    span = {0}
    for value in generators:
        span.update(tuple(x ^ value for x in span))
    require(len(span) == 1 << len(generators), "span capacity")
    return len(generators), span


def caller_bridge(roots, points, labels):
    raw = read_json(PACKAGE / "caller-data.json")
    require(len(raw["L"]) == len(raw["LAB"]) == 112, "caller inventory")
    original = {}
    for row, label in zip(raw["L"], raw["LAB"], strict=True):
        require(len(row) == 8 and all(type(x) in (int, float) and x in (-1, -.5, 0, .5, 1)
                                     for x in row), "caller root coordinates")
        require(type(label) is int and 0 < label < 512, "caller label domain")
        doubled = tuple(int(2 * x) for x in row)
        canonical = max(doubled, tuple(-x for x in doubled))
        require(canonical not in original, "duplicate caller root")
        original[canonical] = label
    require(set(original) == set(points), "caller root-line correspondence")
    columns = (1, 116, 320, 90, 136, 458, 350, 38, 440)
    require(binary_span(columns)[0] == 9, "invertible caller label map")
    for root, label in zip(roots, labels, strict=True):
        if root not in original:
            continue
        image = 0
        for j in range(9):
            if label >> j & 1:
                image ^= columns[j]
        require(image == original[root], "original caller label bridge")
    return {"coordinates_checked": 112, "binary_map_columns": columns, "map_rank": 9}


def a3_orbit(roots):
    """Pointwise stabilizer reflections cover every ordered A3 star."""
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    prefix, counts = (), []
    for expected in (240, 56, 27):
        candidates = {r for r in signed if all(dot(r, a) == 4 for a in prefix)}
        normals = tuple(r for r in roots if all(dot(r, a) == 0 for a in prefix))
        first = min(candidates)
        queue, seen = [first], {first}
        for index in range(240):
            if index >= len(queue):
                break
            for normal in normals:
                pairing = dot(queue[index], normal)
                require(pairing % 4 == 0, "reflection integrality")
                image = tuple(x - pairing // 4 * y
                              for x, y in zip(queue[index], normal, strict=True))
                require(image in candidates, "stabilizer image")
                if image not in seen:
                    queue.append(image)
                    seen.add(image)
            require(len(queue) <= 240, "orbit capacity")
        require(seen == candidates and len(seen) == expected, "A3 extension orbit")
        prefix += (first,)
        counts.append(expected)
    return counts


def labelled_geometry():
    roots, points, _, coordinates = root_data()
    labels = tuple(1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c))
                   for c in coordinates)
    require(len(set(labels)) == 120, "full root-label injectivity")
    require(all(sum(r[i] * r[j] for r in roots) == 120 * (i == j)
                for i in range(8) for j in range(8)), "full-root Gram matrix")
    require(all(sum(dot(r, s) != 0 for s in roots) == 57 for r in roots),
            "uniform full-root direction support")
    by_root = dict(zip(roots, labels, strict=True))
    for j, simple in enumerate(SIMPLE):
        cartan = tuple(dot(a, simple) // 4 for a in SIMPLE)
        for root, label in zip(roots, labels, strict=True):
            reflected = tuple(x - dot(root, simple) // 4 * y
                              for x, y in zip(root, simple, strict=True))
            canonical = max(reflected, tuple(-x for x in reflected))
            parity = sum(((label >> (i + 1)) & 1) * cartan[i] for i in range(8)) % 2
            require(by_root[canonical] == label ^ (parity << (j + 1)),
                    "Weyl action on binary labels")
    star = tuple(tuple(2 * int(i in (0, j)) for i in range(8)) for j in range(1, 4))
    values = tuple((0, *(dot(r, h) // 4 for h in star)) for r in roots)
    require(all(dot(r, h) % 4 == 0 for r in roots for h in star), "integral values")
    costs = tuple(4 - max(Counter(v).values()) for v in values)
    require(Counter(costs) == {0: 20, 1: 64, 2: 36}, "A3 spectrum")
    return roots, points, coordinates, labels, values, costs


def six_flats(labels, costs):
    """Enumerate annihilator RREF three-spaces, exactly once per six-space."""
    require(len(labels) == len(costs) == 120, "flat input shape")
    zero = tuple(sum(1 << i for i, x in enumerate(labels)
                     if (normal & x).bit_count() % 2 == 0) for normal in range(512))
    masks = tuple(sum(1 << i for i, c in enumerate(costs) if c == k) for k in (1, 2))
    histogram, capacity, maximal = Counter(), 0, []
    for pivots in combinations(range(9), 3):
        free = tuple((r, j) for r, p in enumerate(pivots)
                     for j in range(p + 1, 9) if j not in pivots)
        require(len(free) <= 18, "RREF free-bit bound")
        for bits in range(1 << len(free)):
            rows = [1 << j for j in pivots]
            for k, (r, j) in enumerate(free):
                rows[r] |= ((bits >> k) & 1) << j
            mask = zero[rows[0]] & zero[rows[1]] & zero[rows[2]]
            capacity = max(capacity, mask.bit_count())
            weight = (mask & masks[0]).bit_count() + 2 * (mask & masks[1]).bit_count()
            histogram[weight] += 1
            if weight == 36:
                maximal.append((tuple(rows), mask))
                require(len(maximal) <= 20, "maximal flat capacity")
    require(sum(histogram.values()) == 788035 and capacity == 20, "six-flat census")
    require(max(histogram) == 36 and len(maximal) == 20, "weighted six-flat maximum")
    require(max(w for w in histogram if w < 36) == 32, "nonmaximal flat bound")
    return histogram, maximal


def orthogonal_frames(roots, costs):
    adjacent = tuple(sum(1 << j for j in range(i + 1, 120) if dot(r, roots[j]) == 0)
                     for i, r in enumerate(roots))
    stack, frames, states = [((), (1 << 120) - 1)], [], 0
    for _ in range(400_000):
        if not stack:
            break
        prefix, candidates = stack.pop()
        states += 1
        if len(prefix) == 8:
            frames.append(prefix)
        else:
            for j in range(120):
                if candidates >> j & 1:
                    stack.append((prefix + (j,), candidates & adjacent[j]))
        require(len(stack) <= 1000 and len(frames) <= 2025, "frame memory capacity")
    require(not stack and states == 352876 and len(frames) == 2025, "frame coverage")
    histogram = Counter(sum(costs[i] for i in f) for f in frames)
    require(histogram == {8: 1005, 10: 960, 12: 60}, "frame cost spectrum")
    return frames, histogram


def equality_singletons(labels, values, costs, flat, frame):
    removed = flat | sum(1 << i for i in frame)
    singleton = [[] for _ in range(4)]
    for i, value in enumerate(values):
        if costs[i] != 1 or removed >> i & 1:
            continue
        mode = next(x for x in value if value.count(x) == 3)
        for j, x in enumerate(value):
            if x != mode:
                singleton[j].append(i)
    for indices in singleton:
        rank, span = binary_span(tuple(labels[i] for i in indices))
        closure = [i for i, x in enumerate(labels) if i not in frame and x in span]
        require(len(indices) == 16 and rank == 6 and closure == indices,
                "equality singleton closure")
    return singleton


def equality_pairs(labels, values, costs, maximal, frames):
    require(len(maximal) == 20 and len(frames) == 2025, "pair input capacity")
    histogram, witnesses = Counter(), []
    masks = tuple(sum(1 << i for i, c in enumerate(costs) if c == k) for k in (1, 2))
    for normals, flat in maximal:
        for frame in frames:
            union = flat | sum(1 << i for i in frame)
            weight = (union & masks[0]).bit_count() + 2 * (union & masks[1]).bit_count()
            histogram[weight] += 1
            require(weight <= 48, "flat-frame union cost")
            if weight == 48:
                singleton = equality_singletons(labels, values, costs, flat, frame)
                witnesses.append({"normals": normals, "frame": frame,
                                  "singletons": singleton})
                require(len(witnesses) <= 60, "equality witness capacity")
    require(sum(histogram.values()) == 40500 and len(witnesses) == 60,
            "equality pair coverage")
    return histogram, witnesses


def original_profile():
    weights = (2, 2, 6, 6, 6, 6, 6, 7, 7, 7)
    cap = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
    distances = (0, 53, 78, 92, 100, 106, 109)
    levels = []
    for level in range(1, 7):
        retained = weights[:len(weights) - (6 - level)]
        global_cap = sum(cap[w] for w in retained)
        target_cap = sum((32 if w == 7 else cap[w]) for w in retained)
        require((target_cap >= 53 or global_cap >= 73) if level == 1 else
                (target_cap >= 78 or global_cap >= 82) if level == 2 else
                global_cap >= distances[level], "not an original size survivor")
        levels.append((global_cap, target_cap))
    basis = weights[:4]
    require(sum(w - 2 for w in weights) == 35 < 36, "original deficit")
    require(sum(cap[w] for w in basis) == 44 < 53 and sum(basis) > 7, "BK7 gate")
    require(not any(all(sum(w for w, a in zip(basis, assignment, strict=True) if a == k)
                        <= 6 for k in (0, 1)) for assignment in product((0, 1), repeat=4)),
            "already excluded by BK packing")
    require(6 - 3 == 3 and 24 + 20 < 53 and 24 + 40 < 70, "shortening thresholds")
    return {"weights": weights, "cell": (6, 4), "original_levels": levels,
            "retained_code_dimension": 3, "common_support_cap": 24,
            "endpoints": 4, "endpoint_allowance": 80, "support_only_bound": 76,
            "flat_frame_bound": 80, "singleton_closed_support_cap": 64}


def build():
    source_check()
    roots, points, coordinates, labels, values, costs = labelled_geometry()
    flat_hist, maximal = six_flats(labels, costs)
    frames, frame_hist = orthogonal_frames(roots, costs)
    pair_hist, witnesses = equality_pairs(labels, values, costs, maximal, frames)
    result = {"schema": "p112-a3-six-flat/v1", "errors": 0,
              "field": "every characteristic-zero field", "profile": original_profile(),
              "chamber": chamber_receipt(roots, points, coordinates),
              "original_caller_bridge": caller_bridge(roots, points, labels),
              "root_planes": root_plane_receipt(roots), "a3_orbit": a3_orbit(roots),
              "spectrum": Counter(costs), "total_cost": sum(costs),
              "flat_histogram": flat_hist, "maximal_flat_normals": [r for r, _ in maximal],
              "frame_histogram": frame_hist, "pair_histogram": pair_hist,
              "equality_witnesses": witnesses, "new_profile_exclusions": 1}
    return json.loads(json.dumps(result))


def check_receipt(actual, expected):
    require(actual == expected, "committed receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a new external receipt")
    args = parser.parse_args()
    result = build()
    if args.output:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(REPO), "external output only")
        with output.open("x", encoding="utf-8") as stream:
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            require(stream.write(encoded) == len(encoded), "incomplete receipt write")
    else:
        check_receipt(result, read_json(PACKAGE / "RESULT.json"))
    print("PASS_P112_A3_SIX_FLAT profile=2^2,6^5,7^3 flats=788035 frames=2025 "
          "equality_pairs=60 errors=0 no_new_kappa")


if __name__ == "__main__":
    main()
