# SPDX-License-Identifier: Apache-2.0
"""Reject PR3019's fixed matching under one helper's nested-frame consistency.

Bitmap frames, prescribed paths, interval contacts and exact Gram reconstruction
adapted from Nick Petalas, PR3019 at 44d12bdeb8ade4066645bd968bebd4756b06200a
and its credited PR3013/2996 predecessors. Quotient enumeration is adapted from
PR3019's literal.py. New here: one-helper consistent layers, exhaustive full-flag
census, the small monotonicity cut receipt and their source-authenticated replay.
"""

import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LIMIT = 2_000_000
SOURCE_COMMIT = "44d12bdeb8ade4066645bd968bebd4756b06200a"
SOURCE_PATH = "research/p104-coherent-support-witness/WITNESS.json"
INPUT_PINS = {
    "research/p104-joint-unit-flags/CERTIFICATE.json":
        "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json":
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/inputs/P104-FIXTURE.json":
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
}
WITNESS_PIN = "dfac6b19e589ca220e64bb0e0af2b28fae96e2398f7a0e9f558d10f72f261755"
HELPER = 91
FULL = (1 << 104) - 1

def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "JSON size bound")
    return json.loads(raw, object_pairs_hook=unique)


def span(basis):
    require(type(basis) is list and len(basis) <= 9, "basis size")
    points = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector")
        require(vector not in points, "independent basis")
        points += [point ^ vector for point in points]
    return sum(1 << point for point in points)


def bits(mask, width):
    require(type(mask) is int and 0 <= mask < 1 << width, "mask domain")
    for _ in range(width):
        if not mask:
            break
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def dim(frame):
    count = frame.bit_count()
    require(count > 0 and count & (count - 1) == 0, "subspace size")
    return count.bit_length() - 1


def data_paths(word):
    paths = {
        f"{kind}{i}": [span(word["initial_frames"][f"{kind}{i}"])]
        for kind in "XY"
        for i in range(104)
    }
    require(type(word["program"]) is list and len(word["program"]) == 4058, "word size")
    for event in word["program"]:
        op, name = event[:2]
        if op != "transport":
            require(op in {"add", "copy", "zero", "erase"}, "opcode")
            require(not name.startswith("X"), "immutable X")
            if op in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread Y")
            continue
        if name not in paths:
            continue
        old, new = span(event[2]), span(event[3])
        require(paths[name][-1] == old and old != new and old & new == old, "path")
        rank = event[4]
        require(type(rank) is int and rank == dim(new) - dim(old), "transport rank")
        paths[name].append(new)
    for name, chain in paths.items():
        require(
            len(chain) <= 10 and chain[-1] == span(word["final_frames"][name]), "exit"
        )
        require(
            (dim(chain[0]), dim(chain[-1])) == ((1, 9) if name[0] == "X" else (0, 8)),
            "data endpoints",
        )
    return paths


def cover_frames(certificate, paths):
    forms = certificate["forms"]
    require(set(forms) == {"departure", "arrival"}, "cover orientations")
    lines = [paths[f"X{s}"][0] for s in range(104)]
    caps = [paths[f"Y{t}"][-1] for t in range(104)]
    require(len(set(lines)) == len(set(caps)) == 104, "distinct data endpoints")
    departures, arrivals = [], []
    for kind in ("departure", "arrival"):
        require(type(forms[kind]) is list and len(forms[kind]) == 104, "cover count")
        for index, pair in enumerate(forms[kind]):
            require(type(pair) is list and len(pair) == 2, "two cover slots")
            for form in pair:
                require(type(form) is int and 0 < form < 512, "cover functional")
                if kind == "departure":
                    basis = [lines[index].bit_length() - 1, form]
                    departures.append(span(basis))
                else:
                    frame = sum(
                        1 << p
                        for p in bits(caps[index], 512)
                        if (p & form).bit_count() % 2 == 0
                    )
                    require(dim(frame) == 7, "arrival dimension")
                    arrivals.append(frame)
    graph = [[j for j, b in enumerate(arrivals) if a & b == a] for a in departures]
    require(sum(map(len, graph)) == 2309, "compatibility edges")
    return lines, departures, arrivals, caps, graph


def check_pairing(pairing, graph):
    size = len(graph)
    require(type(pairing) is list and len(pairing) == size, "pairing size")
    require(all(type(j) is int and 0 <= j < size for j in pairing), "pairing integers")
    require(len(set(pairing)) == size, "pairing bijection")
    require(all(j in graph[i] for i, j in enumerate(pairing)), "compatible pairing")


def intervals(frames, edges, dimension):
    lines, departures, arrivals, caps, _ = frames
    if dimension == 1:
        return [(lines[a // 2],) * 2 for a, _ in edges]
    if dimension == 2:
        return [(departures[a],) * 2 for a, _ in edges]
    if dimension == 7:
        return [(arrivals[b],) * 2 for _, b in edges]
    if dimension == 8:
        return [(caps[b // 2],) * 2 for _, b in edges]
    require(3 <= dimension <= 6, "intermediate dimension")
    return [(departures[a], arrivals[b]) for a, b in edges]


def fits(bounds, dimension, frame):
    low, high = bounds
    return dim(frame) == dimension and low & frame == low and frame & high == frame


def contact(left, right, dimension):
    a, b = left
    c, e = right
    if a & e != a or c & b != c:
        return False
    minimum = a.bit_count() * c.bit_count() // (a & c).bit_count()
    return minimum <= 1 << dimension <= (b & e).bit_count()


def interval_layers(frames, edges, paths):
    require(len(edges) == 208, "208 matched helpers")
    layers = []
    for d in range(1, 9):
        bounds = intervals(frames, edges, d)
        adjacency = [1 << i for i in range(len(edges))]
        reads, writes = [], []
        for i, left in enumerate(bounds):
            reads.append(
                sum(
                    1 << s
                    for s in range(104)
                    if any(fits(left, d, f) for f in paths[f"X{s}"])
                )
            )
            writes.append(
                sum(
                    1 << t
                    for t in range(104)
                    if any(fits(left, d, f) for f in paths[f"Y{t}"])
                )
            )
            for j in range(i):
                if contact(left, bounds[j], d):
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
        layers.append((adjacency, reads, writes))
    return layers


def components(adjacency):
    count = len(adjacency)
    require(0 < count <= 208, "component capacity")
    unvisited, groups = (1 << count) - 1, []
    for start in range(count):
        if not unvisited >> start & 1:
            continue
        queue = [start]
        unvisited ^= 1 << start
        for cursor in range(count):
            if cursor == len(queue):
                break
            new = adjacency[queue[cursor]] & unvisited
            queue.extend(bits(new, count))
            unvisited ^= new
        require(len(queue) <= count, "bounded component")
        groups.append(queue)
    require(unvisited == 0, "complete components")
    return groups


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


def quotient_spaces():
    """Enumerate distinct RREF subspaces of F2^5 as literal point lists."""
    result = []
    for size in range(6):
        spaces = []
        for pivots in combinations(range(5), size):
            free = [
                (i, j)
                for i, p in enumerate(pivots)
                for j in range(p + 1, 5)
                if j not in pivots
            ]
            for entries in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for index, (i, j) in enumerate(free):
                    if entries >> index & 1:
                        rows[i] |= 1 << j
                points = [0]
                for row in rows:
                    points += [p ^ row for p in points]
                spaces.append(sorted(points))
        if len({tuple(s) for s in spaces}) != len(spaces):
            raise ValueError("duplicate quotient subspace")
        result.append(spaces)
    if list(map(len, result)) != [1, 31, 155, 155, 31, 1]:
        raise ValueError("quotient census")
    return result


def coset_masks(low, high):
    """Construct all 32 literal cosets of A inside B without interval tests."""
    points, basis = [0], []
    for frame, target in ((low, 2), (high, 7)):
        for vector in range(1, 512):
            if len(basis) == target:
                break
            if frame >> vector & 1 and vector not in points:
                basis.append(vector)
                points += [p ^ vector for p in points]
        if len(basis) != target:
            raise ValueError("endpoint basis dimension")
    a_points = [0, basis[0], basis[1], basis[0] ^ basis[1]]
    masks = []
    for q in range(32):
        lift = 0
        for j in range(5):
            if q >> j & 1:
                lift ^= basis[2 + j]
        masks.append(sum(1 << (a ^ lift) for a in a_points))
    if len(set(masks)) != 32:
        raise ValueError("distinct quotient cosets")
    return masks


def allowed_frames(frames, edge, dimension, cosets, quotients):
    lines, departures, arrivals, caps, _ = frames
    a, b = edge
    if dimension == 1:
        return [lines[a // 2]]
    if dimension == 2:
        return [departures[a]]
    if dimension == 7:
        return [arrivals[b]]
    if dimension == 8:
        return [caps[b // 2]]
    if not 3 <= dimension <= 6:
        raise ValueError("literal dimension")
    result = []
    for points in quotients[dimension - 2]:
        mask = 0
        for point in points:
            mask |= cosets[point]
        result.append(mask)
    return result


def authenticated_json(path, expected):
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "authenticated input size bound")
    require(hashlib.sha256(raw).hexdigest() == expected, "input SHA256")
    return json.loads(raw, object_pairs_hook=unique)


def load_inputs():
    sources = read_json(PACKAGE / "SOURCES.json")
    records = sources["files"]
    require(type(records) is list, "source records")
    require(sum(r["usage"] == "input" for r in records) == 3, "three input records")
    pins = {r["path"]: r["sha256"] for r in records if r["usage"] == "input"}
    require(pins == INPUT_PINS, "exact frozen input pins")
    exports = sources["exports"]
    require(type(exports) is list and len(exports) == 1, "one predecessor export")
    exported = exports[0]
    require(exported["local_copy"] == "WITNESS3019.json", "local witness path")
    require(exported["source_pr"] == 3019, "predecessor PR")
    require(exported["source_commit"] == SOURCE_COMMIT, "predecessor head")
    require(exported["source_path"] == SOURCE_PATH, "predecessor witness path")
    require(exported["sha256"] == WITNESS_PIN, "predecessor witness pin")
    values = [authenticated_json(ROOT / name, pins[name]) for name in INPUT_PINS]
    values.append(authenticated_json(PACKAGE / "WITNESS3019.json", WITNESS_PIN))
    return values


def layer_plan(layer):
    adjacency, reads, writes = layer
    return components(adjacency), reads, [list(bits(w, 104)) for w in writes]


def freeze_helper(layer, frames, edges, paths, dimension, chosen):
    """One actual frame; all other helpers retain per-dimension intervals."""
    adjacency, reads, writes = [part.copy() for part in layer]
    helper_bit = 1 << HELPER
    bounds = intervals(frames, edges, dimension)
    require(fits(bounds[HELPER], dimension, chosen), "fixed frame fits interval")
    adjacency[HELPER] = helper_bit
    for other in range(208):
        adjacency[other] &= ~helper_bit
        if fits(bounds[other], dimension, chosen):
            adjacency[other] |= helper_bit
            adjacency[HELPER] |= 1 << other
    reads[HELPER] = sum(1 << s for s in range(104) if chosen in paths[f"X{s}"])
    writes[HELPER] = sum(1 << t for t in range(104) if chosen in paths[f"Y{t}"])
    return adjacency, reads, writes


def propagate(plans, direct):
    support, outputs = [0] * 208, direct.copy()
    for groups, reads, write_targets in plans:
        for i, mask in enumerate(reads):
            support[i] |= mask
        for group in groups:
            joined = 0
            for i in group:
                joined |= support[i]
            for i in group:
                support[i] = joined
        for i, targets in enumerate(write_targets):
            for target in targets:
                outputs[target] |= support[i]
    return outputs


def full_flags(choices):
    """Full flags in B/A=F2^5, in the literal RREF subspace order."""
    for i3, f3 in enumerate(choices[3]):
        for i4, f4 in enumerate(choices[4]):
            if f3 & f4 != f3:
                continue
            for i5, f5 in enumerate(choices[5]):
                if f4 & f5 != f4:
                    continue
                for i6, f6 in enumerate(choices[6]):
                    if f5 & f6 == f5:
                        yield (i3, i4, i5, i6)


def cut_receipt(layers, frames, pairing, matrix, direct):
    """Exact graph inventory for the separate written monotonicity argument."""
    inventory = {}
    for helper in (17, 83, 91):
        inventory[str(helper)] = [
            {"dimension": d, "contacts": list(bits(a[helper] & ~(1 << helper), 208)),
             "reads": list(bits(r[helper], 104)), "writes": list(bits(w[helper], 104))}
            for d, (a, r, w) in enumerate(layers, 1)
        ]
    writers = [[d, h] for d, (_, _, w) in enumerate(layers, 1)
               for h in range(208) if w[h] >> 40 & 1]
    require(writers == [[8, 17], [8, 83]], "Y40 write cut")
    require(direct[40] == 0, "no direct Y40 source injection")
    require(pairing[83] == 80 and pairing[91] == 8, "named cut arrival slots")
    require(frames[1][139] >> 113 & 1, "113 in departure139")
    require(not frames[2][80] >> 113 & 1, "113 outside arrival80")
    require(matrix[40][1] == Fraction(1, 2), "nonzero cut coefficient")
    return {"inventory": inventory, "Y40_writers": writers,
            "Y40_direct_sources": [], "separating_vector": 113,
            "entry_helper": 139, "exit_helper": 83, "exit_arrival": 80,
            "unreachable_coefficient": {"target": 40, "source": 1, "value": "1/2"}}


def flag_census(paths, frames, edges, layers, required, direct):
    quotients = quotient_spaces()
    cosets = coset_masks(frames[1][HELPER], frames[2][edges[HELPER][1]])
    choices = {d: allowed_frames(frames, edges[HELPER], d, cosets, quotients)
               for d in range(3, 7)}
    require([len(choices[d]) for d in range(3, 7)] == [31, 155, 155, 31],
            "quotient dimension census")
    plans = [layer_plan(layer) for layer in layers]
    prepared = {
        d: [layer_plan(freeze_helper(layers[d - 1], frames, edges, paths, d, f))
            for f in choices[d]] for d in range(3, 7)
    }
    census, classes, total = Counter(), {}, 0
    allowed_sources = sum(1 << s for s in (8, 41, 45))
    for indices in full_flags(choices):
        trial = plans.copy()
        for d, i in zip(range(3, 7), indices, strict=True):
            trial[d - 1] = prepared[d][i]
        outputs = propagate(trial, direct)
        require(outputs[40] & ~allowed_sources == 0, "uniform Y40 support bound")
        missing = [r & ~o for r, o in zip(required, outputs, strict=True)]
        count = sum(mask.bit_count() for mask in missing)
        census[count] += 1
        total += 1
        key = (tuple(outputs), tuple(missing))
        if key not in classes:
            classes[key] = {"flags": 0, "missing_required_pairs": count,
                            "representative_indices_3_to_6": list(indices),
                            "representative_frame_bases": [frame_basis(choices[d][i])
                                for d, i in zip(range(3, 7), indices, strict=True)],
                            "target_source_masks_hex": [hex(mask) for mask in outputs],
                            "missing_source_masks_hex": [hex(mask) for mask in missing]}
        classes[key]["flags"] += 1
    require(total == 9765, "complete full-flag census")
    require(census == {45: 477, 46: 9288}, "exact rejecting histogram")
    require(len(classes) == 2, "two exact support classes")
    return {"full_flags": total, "dimension_counts": [31, 155, 155, 31],
            "missing_pair_census": [{"missing_required_pairs": k, "flags": census[k]}
                                   for k in sorted(census)],
            "minimum_missing_required_pairs": min(census), "passing_flags": 0,
            "uniform_Y40_source_bound": [8, 41, 45],
            "classes": sorted(classes.values(), key=lambda r: r["missing_required_pairs"])}


def frame_basis(frame):
    points, basis = [0], []
    for vector in range(1, 512):
        if frame >> vector & 1 and vector not in points:
            basis.append(vector)
            points += [p ^ vector for p in points]
    require(len(points) == frame.bit_count(), "complete frame basis")
    return basis


def compute(certificate, word, fixture, witness):
    require(set(witness) == {"schema_version", "cycle", "pairing"}, "witness schema")
    require(type(witness["schema_version"]) is int and witness["schema_version"] == 1,
            "witness schema version")
    require(witness["cycle"] == [139, 154, 182, 179], "PR3019 cycle")
    paths = data_paths(word)
    frames = cover_frames(certificate, paths)
    pairing = witness["pairing"]
    check_pairing(pairing, frames[-1])
    edges = list(enumerate(pairing))
    matrix = correction(fixture)
    required = [sum(1 << s for s in range(104) if matrix[t][s]) for t in range(104)]
    require(sum(mask.bit_count() for mask in required) == 4992, "required pairs")
    require(all(bool(matrix[t][s]) == bool(frames[3][t] >>
                (frames[0][s].bit_length() - 1) & 1)
                for t in range(104) for s in range(104)), "Gram/frame support binding")
    direct = [sum(1 << s for s in range(104) if
              set(paths[f"X{s}"]) & set(paths[f"Y{t}"])) for t in range(104)]
    layers = interval_layers(frames, edges, paths)
    baseline = propagate([layer_plan(layer) for layer in layers], direct)
    require(baseline == [FULL] * 104, "PR3019 fully relaxed calibration")
    cut = cut_receipt(layers, frames, pairing, matrix, direct)
    census = flag_census(paths, frames, edges, layers, required, direct)
    return {"schema_version": 1, "fixed_helper": HELPER,
            "fixed_matching_commit": SOURCE_COMMIT, "required_pairs": 4992,
            "optimistic_baseline_missing_pairs": 0,
            "cut": cut, "census": census, "no_new_kappa": True}


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = compute(*load_inputs())
    if "--emit" in sys.argv:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    expected = read_json(PACKAGE / "RESULT.json")
    require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "exact typed receipt")
    print("PASS_P104_FIXED_MATCHING_FLAG_CONSISTENCY",
          "helper=91 full_flags=9765 passing=0 minimum_missing=45 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_FIXED_MATCHING_FLAG_CONSISTENCY: {error}") from error
