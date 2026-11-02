"""Exact finite corroboration of the multiple-entrance carrier tariff.

Produced by Nick Petalas. Apache-2.0.
The uniform theorem is in PROOF.md; this file checks bounded metric models.
"""
import argparse
import hashlib
import heapq
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def vector_add(a, b, prime, width):
    result, place = 0, 1
    for _ in range(width):
        result += ((a % prime + b % prime) % prime) * place
        a, b, place = a // prime, b // prime, place * prime
    return result


def span(generators, prime, width):
    vectors = {0}
    for generator in generators:
        old = tuple(vectors)
        multiple = 0
        for _ in range(prime):
            vectors.update(vector_add(v, multiple, prime, width) for v in old)
            multiple = vector_add(multiple, generator, prime, width)
    return sum(1 << v for v in vectors)


def matrix_rank(vectors, prime, width):
    rows = [[(v // prime**j) % prime for j in range(width)] for v in vectors]
    pivot = 0
    for column in range(width):
        candidates = [r for r in range(pivot, len(rows)) if rows[r][column]]
        if not candidates:
            continue
        r = candidates[0]
        rows[pivot], rows[r] = rows[r], rows[pivot]
        inverse = pow(rows[pivot][column], -1, prime)
        rows[pivot] = [(x * inverse) % prime for x in rows[pivot]]
        for r in range(len(rows)):
            if r != pivot:
                coefficient = rows[r][column]
                rows[r] = [(x - coefficient * y) % prime
                           for x, y in zip(rows[r], rows[pivot])]
        pivot += 1
    return pivot


def geometry(prime, width):
    need((prime, width) in ((2, 3), (3, 2)), "Fixed finite geometry domain")
    order = prime**width
    spaces = sorted({span(gens, prime, width)
                     for size in range(width + 1)
                     for gens in itertools.combinations(range(1, order), size)})
    sizes = {prime**d: d for d in range(width + 1)}
    dimensions = [sizes[s.bit_count()] for s in spaces]
    vectors = [[v for v in range(order) if s >> v & 1] for s in spaces]
    distances = []
    for i, a in enumerate(spaces):
        need(matrix_rank(vectors[i], prime, width) == dimensions[i], "Span rank")
        row = []
        for j, b in enumerate(spaces):
            distance = dimensions[i] + dimensions[j] - 2 * sizes[(a & b).bit_count()]
            join_rank = matrix_rank(vectors[i] + vectors[j], prime, width)
            need(distance == 2 * join_rank - dimensions[i] - dimensions[j],
                 "Independent join/intersection distance agreement")
            row.append(distance)
        distances.append(row)
    for i, j, k in itertools.product(range(len(spaces)), repeat=3):
        need(distances[i][k] <= distances[i][j] + distances[j][k], "Triangle")
        drop = dimensions[i] - sizes[(spaces[i] & spaces[j]).bit_count()]
        need(distances[i][j] == dimensions[j] - dimensions[i] + 2 * drop,
             "Exact rank-drop identity")
    return spaces, dimensions, distances


def shortest_visits(spaces, dimensions, distances, tariff):
    """Dijkstra on every frame/visited-lines state, then minima over supersets."""
    lines = [i for i, d in enumerate(dimensions) if d == 1]
    flags = {v: 1 << j for j, v in enumerate(lines)}
    masks, count = 1 << len(lines), len(spaces)
    infinity = 10**12
    costs = [[infinity] * count for _ in range(masks)]
    zero = spaces.index(1)
    costs[0][zero] = 0
    queue = [(0, 0, zero)]
    settled = 0
    for _ in range(masks * count * count + 1):
        if not queue:
            break
        cost, mask, vertex = heapq.heappop(queue)
        if cost != costs[mask][vertex]:
            continue
        settled += 1
        need(settled <= masks * count, "Finite Dijkstra state bound")
        for target in range(count):
            new_mask = mask | flags.get(target, 0)
            candidate = cost + tariff[distances[vertex][target]]
            if candidate < costs[new_mask][target]:
                costs[new_mask][target] = candidate
                heapq.heappush(queue, (candidate, new_mask, target))
    else:
        raise ValueError("Finite Dijkstra edge bound exhausted")
    need(not queue, "Shortest-path run completed")
    for bit in range(len(lines)):
        for mask in range(masks):
            if not mask >> bit & 1:
                superset = costs[mask | (1 << bit)]
                costs[mask] = [min(x, y) for x, y in zip(costs[mask], superset)]
    need(all(x < infinity for row in costs for x in row), "Every requirement reachable")
    return lines, costs, settled


def predicted(spaces, dimensions, lines, mask, endpoint, tariff):
    if not mask:
        return tariff[dimensions[endpoint]]
    required = [v for bit, v in enumerate(lines) if mask >> bit & 1]
    inside = [v for v in required if spaces[v] & spaces[endpoint] == spaces[v]]
    final = dimensions[endpoint] - 1 if inside else dimensions[endpoint] + 1
    return tariff[1] + (len(required) - 1) * tariff[2] + tariff[final]


def tariffs(width):
    maximum = 2 * width
    rows = {
        "linear": tuple(range(maximum + 1)),
        "cap_one": tuple(min(r, 1) for r in range(maximum + 1)),
        "cap_two": tuple(min(r, 2) for r in range(maximum + 1)),
        "ceil_half": tuple((r + 1) // 2 for r in range(maximum + 1)),
        "zero": (0,) * (maximum + 1),
        "harmonic_scaled": tuple(420 * r // (r + 1) for r in range(maximum + 1)),
    }
    for name, row in rows.items():
        need(row[0] == 0 and all(row[r] <= row[r + 1] for r in range(maximum)),
             "Nonnegative nondecreasing tariff: " + name)
        for a in range(maximum + 1):
            for b in range(maximum + 1 - a):
                need(row[a + b] <= row[a] + row[b], "Subadditive tariff: " + name)
    return rows


def check_geometry(prime, width):
    spaces, dimensions, distances = geometry(prime, width)
    counts, transcript, linear_costs = {}, hashlib.sha256(), None
    for name, tariff in tariffs(width).items():
        lines, costs, settled = shortest_visits(spaces, dimensions, distances, tariff)
        checked = 0
        for mask in range(1 << len(lines)):
            for endpoint in range(len(spaces)):
                expected = predicted(spaces, dimensions, lines, mask, endpoint, tariff)
                need(costs[mask][endpoint] == expected, "Exact route tariff")
                transcript.update(f"{name}:{mask}:{endpoint}:{expected}\n".encode())
                checked += 1
        counts[name] = {"instances": checked, "settled_states": settled}
        if name == "linear":
            linear_costs = costs
    need(linear_costs is not None, "Linear witness checked")
    controls = check_controls(spaces, dimensions, distances, lines, linear_costs, width)
    return {"prime": prime, "width": width, "subspaces": len(spaces),
            "lines": len(lines), "tariffs": counts, "controls": controls,
            "transcript_sha256": transcript.hexdigest()}


def check_controls(spaces, dimensions, distances, lines, linear_costs, width):
    full = dimensions.index(width)
    first, second = lines[:2]
    pair = 3
    need(linear_costs[pair][full] == width + 2, "Two distinct entrances cost two extra")
    need(linear_costs[pair][full] != width, "Reject free sharing of distinct lines")
    need(linear_costs[1][second] == 3, "Outside line costs three")
    need(linear_costs[1][second] != 1, "Reject false containment discount")
    need(linear_costs[1][full] == width, "Single contained entrance is free")
    need(linear_costs[0][full] == width, "Empty requirements retain endpoint")
    superlinear = tuple(r * r for r in range(2 * width + 1))
    _, costs, _ = shortest_visits(spaces, dimensions, distances, superlinear)
    need(costs[0][full] < superlinear[width], "Reject omitted subadditivity premise")
    if width == 3:
        nonmonotone = (0, 1) + (0,) * (2 * width - 1)
        _, costs, _ = shortest_visits(spaces, dimensions, distances, nonmonotone)
        need(costs[1][first] == 0 < nonmonotone[1], "Reject omitted monotonicity premise")
    return {"false_free_sharing": 1, "false_containment": 1,
            "endpoint_omission": 1, "non_subadditive": 1,
            "nonmonotone": int(width == 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="Print generated hash-bound receipt")
    args = parser.parse_args()
    results = [check_geometry(2, 3), check_geometry(3, 2)]
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "VALIDATION.md", "verify.py")
    hashes = {}
    for name in names:
        with (package / name).open("rb") as source:
            data = source.read(1024 * 1024 + 1)
        need(len(data) <= 1024 * 1024, "Bounded package input")
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {"claim_type": "scoped proof with finite corroboration",
               "results": results, "sha256": hashes}
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        cases = sum(row["instances"] for result in results for row in result["tariffs"].values())
        print(f"PASS_MULTIPLE_ENTRANCE_CARRIER_TARIFF instances={cases} no_new_kappa")


if __name__ == "__main__":
    main()
