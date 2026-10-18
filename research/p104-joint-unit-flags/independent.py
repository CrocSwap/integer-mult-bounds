# SPDX-License-Identifier: Apache-2.0
"""Check the static flag witness without importing its producer or geometry."""

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
GEOMETRY = "research/p104-endpoint-geometric-budget/geometry.py"


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


def sources():
    rows = read_json(PACKAGE / "SOURCES.json")["files"]
    require(len(rows) <= 8, "source record bound")
    authenticated = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        name = row["path"]
        require(
            name in {WORD, FIXTURE, GEOMETRY} and name not in authenticated,
            "exact input inventory",
        )
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, "input size bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        authenticated[name] = raw
    require(set(authenticated) == {WORD, FIXTURE, GEOMETRY}, "three pinned inputs")
    return [
        json.loads(authenticated[name], object_pairs_hook=unique)
        for name in (WORD, FIXTURE)
    ]


def binary_span(basis):
    require(type(basis) is list and len(basis) <= 9, "binary basis shape")
    mask = 1
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector domain")
        require(not (mask >> vector & 1), "independent flag vectors")
        mask |= sum(1 << (point ^ vector) for point in range(512) if mask >> point & 1)
    require(mask.bit_count() == 2 ** len(basis), "span dimension")
    return mask


def roots(fixture):
    rows = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            rows.append(tuple(row))
    rows += [(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0]
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    result = sorted(set(rows) - removed)
    require(len(rows) == 120 and len(result) == 104, "ordered root inventory")
    return result


def data_paths(word):
    names = [f"{kind}{i}" for kind in "XY" for i in range(104)]
    paths = {name: [binary_span(word["initial_frames"][name])] for name in names}
    require(len(word["program"]) == 4058, "4058 original events")
    for event in word["program"]:
        if event[0] != "transport" or event[1] not in paths:
            continue
        _, name, before, after, rank = event
        old, new = binary_span(before), binary_span(after)
        require(
            paths[name][-1] == old and old != new and old & new == old,
            "strict data path inclusion",
        )
        require(rank == len(after) - len(before), "data transport rank")
        paths[name].append(new)
    for name, chain in paths.items():
        require(
            len(chain) <= 10 and chain[-1] == binary_span(word["final_frames"][name]),
            "complete data path",
        )
    return paths


def residuals(word, fixture):
    paths, ports = data_paths(word), roots(fixture)
    xs, ys = [paths[f"X{s}"] for s in range(104)], [paths[f"Y{t}"] for t in range(104)]
    require(
        all(p[0].bit_count() == 2 and p[-1].bit_count() == 512 for p in xs),
        "source endpoints",
    )
    require(all(p[0] == 1 and p[-1].bit_count() == 256 for p in ys), "target endpoints")
    labels = [p[0].bit_length() - 1 for p in xs]
    normals = []
    for chain in ys:
        dual = [
            n
            for n in range(1, 512)
            if all(
                (n & v).bit_count() % 2 == 0 for v in range(512) if chain[-1] >> v & 1
            )
        ]
        require(len(dual) == 1, "unique target normal")
        normals.append(dual[0])
    require(len(set(labels)) == len(set(normals)) == 104, "distinct endpoints")
    arrival, departure, count = (
        [set() for _ in range(104)],
        [set() for _ in range(104)],
        0,
    )
    for t in range(104):
        for s in range(104):
            gram = sum(a * b for a, b in zip(ports[t], ports[s], strict=True))
            require(bool(ys[t][-1] >> labels[s] & 1) == (gram % 8 == 4), "Gram binding")
            if gram == 8 * int(t == s):
                continue
            count += 1
            require(
                ys[t][-1] not in xs[s] and xs[s][0] not in ys[t], "no direct bypass"
            )
            if not any(frame >> labels[s] & 1 for frame in ys[t][:-1]):
                arrival[t].add(labels[s])
            if not any(
                frame.bit_count() > 2 and frame & ys[t][-1] == frame for frame in xs[s]
            ):
                departure[s].add(normals[t])
    require(
        count == 4992 and sum(map(len, arrival)) == sum(map(len, departure)) == 4656,
        "original correction and residual counts",
    )
    return labels, normals, arrival, departure


def check_covers(forms, endpoint_normals, demands):
    require(type(forms) is list and len(forms) == 104, "104 cover pairs")
    spaces = []
    for pair, normal, points in zip(forms, endpoint_normals, demands, strict=True):
        require(type(pair) is list and len(pair) == 2, "two forms per endpoint")
        require(
            all(type(f) is int and 0 < f < 512 and f != normal for f in pair),
            "proper form domain",
        )
        masks = [
            sum(
                1 << v
                for v in range(512)
                if (v & normal).bit_count() % 2 == (v & f).bit_count() % 2 == 0
            )
            for f in pair
        ]
        require(all(mask.bit_count() == 128 for mask in masks), "dimension-seven cover")
        covered = [{v for v in points if mask >> v & 1} for mask in masks]
        require(
            not covered[0] & covered[1] and covered[0] | covered[1] == points,
            "disjoint exact residual cover",
        )
        best = max(
            sum((v & f).bit_count() % 2 == 0 for v in points)
            for f in range(1, 512)
            if f != normal
        )
        require(len(covered[0]) == best, "first cover attains maximum capacity")
        spaces.extend(masks)
    return spaces


def check_helpers(helpers, labels, normals, departure_forms, arrivals):
    require(type(helpers) is list and len(helpers) == 208, "208 helper flags")
    source_slots, target_slots = set(), set()
    for row in helpers:
        require(
            set(row)
            == {"source", "departure_choice", "target", "arrival_choice", "basis"},
            "helper schema",
        )
        s, d, t, a = [
            row[key]
            for key in ("source", "departure_choice", "target", "arrival_choice")
        ]
        require(
            all(type(v) is int for v in (s, d, t, a))
            and 0 <= s < 104
            and 0 <= t < 104
            and d in (0, 1)
            and a in (0, 1),
            "endpoint slot domain",
        )
        require(
            (s, d) not in source_slots and (t, a) not in target_slots,
            "unique endpoint slots",
        )
        source_slots.add((s, d))
        target_slots.add((t, a))
        basis = row["basis"]
        require(type(basis) is list and len(basis) == 9, "nine unit steps")
        require(binary_span(basis[:1]) == binary_span([labels[s]]), "source line")
        require(
            binary_span(basis[:2]) == binary_span([labels[s], departure_forms[s][d]]),
            "designated departure plane",
        )
        require(
            binary_span(basis[:7]) == arrivals[2 * t + a], "designated arrival plane"
        )
        require(
            binary_span(basis[:8])
            == sum(1 << v for v in range(512) if (v & normals[t]).bit_count() % 2 == 0),
            "target hyperplane",
        )
        require(binary_span(basis).bit_count() == 512, "FULL final frame")
    require(len(source_slots) == len(target_slots) == 208, "complete slot bijections")


def check(certificate, original):
    require(
        set(certificate) == {"schema_version", "forms", "helpers", "graph", "scope"},
        "certificate schema",
    )
    require(
        type(certificate["schema_version"]) is int
        and certificate["schema_version"] == 1,
        "schema version",
    )
    labels, normals, arrival, departure = original
    forms = certificate["forms"]
    require(set(forms) == {"arrival", "departure"}, "two orientations")
    arrivals = check_covers(forms["arrival"], normals, arrival)
    check_covers(forms["departure"], labels, departure)
    departures = [
        binary_span([labels[s], f]) for s in range(104) for f in forms["departure"][s]
    ]
    graph = [[j for j, b in enumerate(arrivals) if a & b == a] for a in departures]
    actual = {
        "edges": sum(map(len, graph)),
        "left_degrees": list(map(len, graph)),
        "right_degrees": [sum(j in row for row in graph) for j in range(208)],
    }
    require(
        json.dumps(actual, sort_keys=True)
        == json.dumps(certificate["graph"], sort_keys=True)
        and actual["edges"] == 2309,
        "full graph census",
    )
    check_helpers(certificate["helpers"], labels, normals, forms["departure"], arrivals)


def main():
    original = residuals(*sources())
    check(read_json(PACKAGE / "CERTIFICATE.json"), original)
    print("PASS_P104_JOINT_UNIT_FLAGS_INDEPENDENT demands=9312 helpers=208")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_JOINT_UNIT_FLAGS_INDEPENDENT: {error}") from error
