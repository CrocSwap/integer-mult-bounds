#!/usr/bin/env python3
"""Independent endpoint-span checks; no optimizer or predecessor imports.

Prepared by kumagi with substantial OpenAI Codex assistance. Apache-2.0.
The source fixture and old constraints are credited in README.md. This uses
binary row reduction, rather than the predecessor's enumeration of subspaces.
The network implication is a written theorem in PROOF.md, not proved by this run.
"""

from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFIX = "research/p104-native-channel/inputs/"
PINS = {
    "LOWRANK-WITNESS.json":
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "P104-FIXTURE.json":
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
}
EXPECTED_CUTS = [4656, 4656, 4672, 4680, 4672, 4656, 4656]
EXPECTED_BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    raw = (ROOT / PREFIX / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[name], "source digest: " + name)
    return json.loads(raw)


def reduce_vector(vector, basis):
    for row in basis:
        if vector & (1 << (row.bit_length() - 1)):
            vector ^= row
    return vector


def rref(vectors):
    """Canonical rows with highest-set-bit pivots, over F_2^9."""
    rows = []
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, "binary vector")
        vector = reduce_vector(vector, rows)
        if vector:
            pivot = 1 << (vector.bit_length() - 1)
            rows = [row ^ vector if row & pivot else row for row in rows]
            rows.append(vector)
            rows.sort(reverse=True)
    return tuple(rows)


def frame(vectors):
    basis = rref(vectors)
    require(len(basis) == len(vectors), "independent supplied frame basis")
    return basis


def contained(smaller, larger):
    return all(reduce_vector(row, larger) == 0 for row in smaller)


def orthogonal(basis):
    """Solve the homogeneous system using its free coordinates."""
    pivots = {row.bit_length() - 1 for row in basis}
    result = []
    for free in set(range(9)) - pivots:
        vector = 1 << free
        for row in basis:
            if (row & vector).bit_count() % 2:
                vector ^= 1 << (row.bit_length() - 1)
        result.append(vector)
    return rref(result)


def source_geometry():
    witness, fixture = (load(name) for name in PINS)
    roots = set()
    for left, right in combinations(range(8), 2):
        for sign in (-1, 1):
            vector = [0] * 8
            vector[left], vector[right] = 2, sign * 2
            roots.add(tuple(vector))
    for tail in product((-1, 1), repeat=7):
        if sum(value == -1 for value in tail) % 2 == 0:
            roots.add((1, *tail))
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    require(len(roots) == 120 and len(removed) == 16 and removed <= roots,
            "E8 roots and puncture")
    ports = sorted(roots - removed)
    require(len(ports) == 104, "104 ports")

    names = [f"{kind}{index}" for kind in "XY" for index in range(104)]
    paths = {name: [frame(witness["initial_frames"][name])] for name in names}
    paid = Counter()
    require(len(witness["program"]) == 4058, "word length")
    for event in witness["program"]:
        require(event[0] in {"add", "copy", "zero", "erase", "transport"},
                "known frozen instruction kind")
        if event[0] in {"add", "copy"}:
            require(not event[1].startswith("X") and not event[2].startswith("Y"),
                    "immutable sources and unread targets")
        elif event[0] in {"zero", "erase"}:
            require(not event[1].startswith(("X", "Y")),
                    "no data-field initialization or erasure")
        elif event[0] == "transport":
            _, name, before, after, rank = event
            paid[rank] += 1
            if name in paths:
                before, after = frame(before), frame(after)
                require(before == paths[name][-1] and contained(before, after)
                        and len(after) - len(before) == rank > 0,
                        "frozen monotone data path")
                paths[name].append(after)
    require(dict(paid) == EXPECTED_BASE, "frozen paid profile")
    for name in names:
        require(paths[name][-1] == frame(witness["final_frames"][name]),
                "frozen final frame")
    lines = [paths[f"X{s}"][0] for s in range(104)]
    targets = [paths[f"Y{t}"][-1] for t in range(104)]
    require(len(set(lines)) == len(set(targets)) == 104, "distinct endpoints")
    require(all(len(line) == 1 for line in lines)
            and all(len(target) == 8 for target in targets), "endpoint dimensions")
    labels = [line[0] for line in lines]
    require(all(len(paths[f"X{s}"][-1]) == 9 for s in range(104))
            and all(paths[f"Y{t}"][0] == () for t in range(104)),
            "FULL source ends and ZERO target starts")
    duals = [orthogonal(target) for target in targets]
    require(all(len(dual) == 1 for dual in duals), "one-dimensional target duals")
    normals = [dual[0] for dual in duals]
    for target, normal in zip(targets, normals, strict=True):
        require(orthogonal((normal,)) == target, "double annihilator")
        require(all((reduce_vector(v, target) == 0)
                    == ((v & normal).bit_count() % 2 == 0) for v in range(512)),
                "membership against independent parity equation")
    odd_functionals = []
    for alphabet in (labels, normals):
        possible = [v for v in range(1, 512)
                    if all((v & q).bit_count() % 2 == 1 for q in alphabet)]
        require(possible, "affine odd functional used by old cut capacities")
        odd_functionals.append(possible[0])

    demands = set()
    for t, left in enumerate(ports):
        for s, right in enumerate(ports):
            gram4 = sum(a * b for a, b in zip(left, right, strict=True))
            require(gram4 % 4 == 0, "integral Gram entry")
            if 8 * (t == s) != gram4:
                demands.add((t, s))
            require((reduce_vector(labels[s], targets[t]) == 0)
                    == (gram4 % 8 == 4), "root/label incidence binding")
    require(len(demands) == 4992, "4992 correction demands")
    require(all(sum((t, s) in demands for s in range(104)) == 48
                for t in range(104)), "48 demands per target")

    residual_sizes, forced_sizes = Counter(), Counter()
    direct_bypasses = later_reads = 0
    for t, target in enumerate(targets):
        residual = []
        for s, label in enumerate(labels):
            if (t, s) not in demands:
                continue
            direct = target in paths[f"X{s}"]
            direct_bypasses += direct
            earlier = any(len(v) < 8 and reduce_vector(label, v) == 0
                          for v in paths[f"Y{t}"])
            if not direct and not earlier:
                residual.append(label)
        require(rref(residual) == target, "rank-eight residual target span")
        residual_sizes[len(residual)] += 1
    require(direct_bypasses == 0, "no direct source hyperplane bypass")
    for s, line in enumerate(lines):
        forced_normals = []
        for t, target in enumerate(targets):
            require(line not in paths[f"Y{t}"], "no target source-line bypass")
            if (t, s) in demands:
                later = any(len(v) > 1 and contained(v, target)
                            for v in paths[f"X{s}"])
                later_reads += later
                if not later:
                    forced_normals.append(normals[t])
        require(rref(forced_normals) == orthogonal(line),
                "rank-eight forced target-normal span")
        forced_sizes[len(forced_normals)] += 1
    require(later_reads == 336, "later-readable correction entries")

    cut_counts = []
    for cut in range(1, 8):
        forced = 0
        for t, s in demands:
            source_bypass = any(len(v) > cut and contained(v, targets[t])
                                for v in paths[f"X{s}"])
            target_bypass = any(len(v) <= cut and reduce_vector(labels[s], v) == 0
                                for v in paths[f"Y{t}"])
            forced += not source_bypass and not target_bypass
        cut_counts.append(forced)
    require(cut_counts == EXPECTED_CUTS, "seven old cut constraints")
    return {
        "demands": len(demands), "rank_eight_arrival_spans": len(targets),
        "rank_eight_departure_spans": len(lines), "direct_bypasses": direct_bypasses,
        "later_reads": later_reads, "arrival_sizes": dict(sorted(residual_sizes.items())),
        "departure_sizes": dict(sorted(forced_sizes.items())),
        "odd_functionals": odd_functionals, "cut_requirements": cut_counts,
        "endpoint_span_requirement": 8 * len(targets),
    }


def histories():
    # Positive compositions enumerate histories independently of stop-bit masks.
    by_mass = [[()]]
    for mass in range(1, 10):
        by_mass.append([(first, *tail) for first in range(1, mass + 1)
                        for tail in by_mass[mass - first]])
    rows = {}
    for jumps in by_mass[9]:
        stops = [0]
        for jump in jumps:
            stops.append(stops[-1] + jump)
        edges = list(zip(stops[:-1], stops[1:], strict=True))
        capacities = []
        for cut in range(1, 8):
            crossing = [(a, b) for a, b in edges if a <= cut < b]
            require(len(crossing) == 1, "unique crossing of every cut")
            a, b = crossing[0]
            capacities.append(0 if a == 0 or b == 9 else 1 << (7 - b + a))
        arrival = next((a for a, b in edges if b == 8), 0)
        departure = next((9 - b for a, b in edges if a == 1), 0)
        rows[jumps] = {
            "cuts": capacities, "visits_one": int(1 in stops),
            "visits_eight": int(8 in stops), "arrival": arrival,
            "departure": departure,
        }
        require(0 <= arrival <= 7 * (8 in stops)
                and 0 <= departure <= 7 * (1 in stops), "endpoint weights")
    require(len(rows) == 256, "all 256 complete increasing histories")
    expected_weights = {0: 129, **{weight: 2 ** (weight - 1) for weight in range(1, 8)}}
    for key in ("arrival", "departure"):
        require(dict(Counter(row[key] for row in rows.values())) == expected_weights,
                "complete endpoint-weight distribution")
    require(sum(row["visits_one"] for row in rows.values()) == 128
            and sum(row["visits_eight"] for row in rows.values()) == 128,
            "old endpoint-visit distribution")
    return rows


def profile(rows, cheap, full):
    weights = [(cheap, rows[(1, 7, 1)]), (full, rows[(1,) * 9])]
    cuts = [sum(n * row["cuts"][k] for n, row in weights) for k in range(7)]
    totals = {key: sum(n * row[key] for n, row in weights)
              for key in ("visits_one", "visits_eight", "arrival", "departure")}
    old = (all(value >= required for value, required in zip(cuts, EXPECTED_CUTS, strict=True))
           and totals["visits_one"] >= 208 and totals["visits_eight"] >= 208
           and 9 * (cheap + full) <= 4344)
    new = old and totals["arrival"] >= 832 and totals["departure"] >= 832
    return {"cheap": cheap, "full": full, "cuts": cuts, **totals,
            "rank_mass": 9 * (cheap + full), "old_accepts": old, "new_accepts": new}


def calculate():
    finite = source_geometry()
    rows = histories()
    rejected = profile(rows, 329, 71)
    require(rejected["old_accepts"] and not rejected["new_accepts"],
            "400-lifetime profile separates the old and new necessary screens")
    require(rejected["arrival"] == rejected["departure"] == 826
            and rejected["cuts"] == [4873] * 7, "400-lifetime profile exact totals")
    # Only the reported numerical floors are compared here, not the mixer's
    # entire structural argument; 250 is its explicitly unadopted sketch.
    require(all(329 + 71 >= floor for floor in (216, 219, 234, 250)),
            "400 lifetimes exceeds credited numerical floors")
    surviving = profile(rows, 335, 71)
    require(surviving["new_accepts"] and surviving["arrival"] == surviving["departure"] == 832
            and surviving["cuts"] == [4879] * 7, "406-lifetime equality profile survives rows")
    historical = profile(rows, 137, 71)
    require(historical["old_accepts"] and not historical["new_accepts"]
            and historical["arrival"] == historical["departure"] == 634
            and historical["cuts"] == [4681] * 7, "historical published relaxation totals")
    # Controls isolate mistakes that endpoint counts alone or uniform weights miss.
    cheap = profile(rows, 208, 0)
    require(not cheap["old_accepts"] and cheap["arrival"] == cheap["departure"] == 208,
            "endpoint visitors alone do not supply cut or span capacity")
    require(rows[(9,)]["arrival"] == rows[(9,)]["departure"] == 0,
            "direct zero-to-full jump supplies no endpoint span")
    require(rows[(8, 1)]["visits_eight"] == 1 and rows[(8, 1)]["arrival"] == 0
            and rows[(1, 8)]["visits_one"] == 1 and rows[(1, 8)]["departure"] == 0,
            "endpoint visit is not a positive span contribution")
    require(rows[(1, 7, 1)]["arrival"] != rows[(1,) * 9]["arrival"],
            "equal endpoint counts do not justify equal span weights")
    require((rows[(1, 1, 6, 1)]["arrival"], rows[(1, 1, 6, 1)]["departure"]) == (2, 7)
            and (rows[(1, 6, 1, 1)]["arrival"], rows[(1, 6, 1, 1)]["departure"]) == (7, 2),
            "arrival and departure rows differ on asymmetric histories")
    serialized_rows = [{"jumps": jumps, **row} for jumps, row in sorted(rows.items())]
    digest = hashlib.sha256(json.dumps(serialized_rows, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    return {"finite": finite, "histories": len(rows), "history_sha256": digest,
            "rejected_400_profile": rejected, "span_deficit_each": 832 - 826,
            "surviving_406_relaxation": surviving,
            "historical_208_relaxation": historical, "negative_controls": 5}


if __name__ == "__main__":
    result = calculate()
    print("PASS_P104_ENDPOINT_SPAN_INDEPENDENT")
    print(json.dumps(result, sort_keys=True))
