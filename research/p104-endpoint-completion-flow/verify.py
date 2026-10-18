# SPDX-License-Identifier: Apache-2.0
"""Necessary dependency test for every completion of fixed P104 endpoint pairs."""

import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
)
FIXED = (0, 1, 2, 7, 8, 9)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    require(path.stat().st_size <= 2_000_000, "JSON size bound")
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def inputs():
    records = read_json(PACKAGE / "SOURCES.json")["files"]
    require(len(records) == 5, "source inventory size")
    pins = {r["path"]: r["sha256"] for r in records if r["usage"] == "input"}
    require(set(pins) == set(INPUTS), "exact input inventory")
    values = []
    for name in INPUTS:
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, "input size bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pins[name], "input SHA256")
        values.append(json.loads(raw, object_pairs_hook=unique))
    return values


def span(basis):
    require(type(basis) is list and len(basis) <= 9, "basis shape")
    result = frozenset({0})
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "vector domain")
        require(vector not in result, "independent basis")
        result |= frozenset(v ^ vector for v in result)
    require(len(result) == 1 << len(basis), "span cardinality")
    return result


def dimension(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, "subspace cardinality")
    return size.bit_length() - 1


def data_paths(word):
    names = [f"{kind}{i}" for kind in "XY" for i in range(104)]
    paths = {name: [span(word["initial_frames"][name])] for name in names}
    require(len(word["program"]) == 4058, "4058 original events")
    for event in word["program"]:
        if event[0] != "transport" or event[1] not in paths:
            continue
        _, name, before, after, rank = event
        old, new = span(before), span(after)
        require(paths[name][-1] == old and old < new, "increasing data path")
        require(type(rank) is int and rank == dimension(new) - dimension(old), "rank")
        paths[name].append(new)
    for name, chain in paths.items():
        require(len(chain) <= 10, "data path size")
        require(chain[-1] == span(word["final_frames"][name]), "data exit")
        expected = (1, 9) if name[0] == "X" else (0, 8)
        require((dimension(chain[0]), dimension(chain[-1])) == expected, "endpoints")
    return paths


def endpoint_planes(certificate, paths):
    helpers = certificate["helpers"]
    require(type(helpers) is list and len(helpers) == 208, "208 helpers")
    planes, departures, arrivals = [], set(), set()
    for row in helpers:
        s, t, a, b = [
            row[k] for k in ("source", "target", "departure_choice", "arrival_choice")
        ]
        require(all(type(v) is int for v in (s, t, a, b)), "integer slots")
        require(0 <= s < 104 and 0 <= t < 104 and a in (0, 1) and b in (0, 1), "slots")
        require((s, a) not in departures and (t, b) not in arrivals, "unique slots")
        departures.add((s, a))
        arrivals.add((t, b))
        basis = row["basis"]
        require(type(basis) is list and len(basis) == 9, "full flag basis")
        span(basis)
        fixed = {d: span(basis[:d]) for d in FIXED}
        require(fixed[1] == paths[f"X{s}"][0], "designated source line")
        require(fixed[8] == paths[f"Y{t}"][-1], "designated target hyperplane")
        planes.append(fixed)
    return planes


def interval(fixed, d):
    if d in fixed:
        return fixed[d], fixed[d]
    require(3 <= d <= 6, "intermediate dimension")
    return fixed[2], fixed[7]


def fits(bounds, d, frame):
    low, high = bounds
    return dimension(frame) == d and low <= frame <= high


def contact(left, right, d):
    a, b = left
    c, e = right
    if not (a <= e and c <= b):
        return False
    minimum = dimension(a) + dimension(c) - dimension(a & c)
    maximum = dimension(b & e)
    return minimum <= d <= maximum


def components(adjacency):
    count, seen, result = len(adjacency), set(), []
    require(count <= 208, "helper bound")
    for start in range(count):
        if start in seen:
            continue
        queue, seen = [start], seen | {start}
        for offset in range(count):
            if offset >= len(queue):
                break
            for nxt in sorted(adjacency[queue[offset]]):
                require(0 <= nxt < count, "contact endpoint")
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        require(len(queue) <= count, "component capacity")
        result.append(queue)
    require(len(seen) == count, "complete components")
    return result


def dependency_graph(planes, paths):
    count = len(planes)
    require(0 < count <= 208, "helper inventory bound")
    support, outputs, layers = [0] * count, [0] * 104, []
    xs = [paths[f"X{s}"] for s in range(104)]
    ys = [paths[f"Y{t}"] for t in range(104)]
    for t, target in enumerate(ys):
        outputs[t] = sum(
            1 << s for s, source in enumerate(xs) if set(source) & set(target)
        )
    for d in range(1, 9):
        bounds = [interval(fixed, d) for fixed in planes]
        adjacency = [set() for _ in planes]
        for i in range(count):
            support[i] |= sum(
                1 << s
                for s, chain in enumerate(xs)
                if any(fits(bounds[i], d, f) for f in chain)
            )
            for j in range(i):
                if contact(bounds[i], bounds[j], d):
                    adjacency[i].add(j)
                    adjacency[j].add(i)
        groups = components(adjacency)
        for group in groups:
            joined = 0
            for i in group:
                joined |= support[i]
            for i in group:
                support[i] = joined
        for t, chain in enumerate(ys):
            for i in range(count):
                if any(fits(bounds[i], d, frame) for frame in chain):
                    outputs[t] |= support[i]
        layers.append(
            {
                "dimension": d,
                "contacts": sum(map(len, adjacency)) // 2,
                "components": len(groups),
                "max_sources": max(v.bit_count() for v in support),
            }
        )
    return outputs, layers


def correction(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0]
    removed = fixture["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(v) for v in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "ordered P104 roots")
    return [
        [
            Fraction(
                8 * int(t == s)
                - sum(a * b for a, b in zip(ports[t], ports[s], strict=True)),
                8,
            )
            for s in range(104)
        ]
        for t in range(104)
    ]


def compute(certificate, word, fixture):
    paths = data_paths(word)
    planes = endpoint_planes(certificate, paths)
    outputs, layers = dependency_graph(planes, paths)
    matrix = correction(fixture)
    required = [(t, s) for t in range(104) for s in range(104) if matrix[t][s]]
    missing = [(t, s) for t, s in required if not outputs[t] >> s & 1]
    require(
        len(required) == 4992 and missing, "nonempty required-dependency obstruction"
    )
    t, s = missing[0]
    return {
        "schema_version": 1,
        "helpers": len(planes),
        "required_pairs": len(required),
        "reachable_required_pairs": len(required) - len(missing),
        "unreachable_required_pairs": len(missing),
        "layers": layers,
        "target_source_masks_hex": [hex(mask) for mask in outputs],
        "witness": {
            "source": s,
            "target": t,
            "required_coefficient": str(matrix[t][s]),
            "optimistic_coefficient": "0",
        },
        "scope": "All intermediate completions of fixed matched endpoint planes; optimistic untimed contacts, no restoration charge; no new kappa.",
    }


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = compute(*inputs())
    if sys.argv[1:]:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = read_json(PACKAGE / "RESULT.json")
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "exact receipt",
    )
    print(
        "PASS_P104_ENDPOINT_COMPLETION_FLOW",
        f"required={result['required_pairs']}",
        f"unreachable={result['unreachable_required_pairs']}",
        "all_intermediate_completions no_new_kappa",
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_ENDPOINT_COMPLETION_FLOW: {error}") from error
