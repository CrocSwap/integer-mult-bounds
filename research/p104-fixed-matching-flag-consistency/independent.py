# SPDX-License-Identifier: Apache-2.0
"""Independent literal-frame certificate for the helper-91 monotone cut.

No predecessor verifier, interval-contact formula, or primary checker is loaded.
The mathematical model and endpoint matching are credited in README.md.
"""

import hashlib
import json
import sys
from copy import deepcopy
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
PREDECESSOR = "44d12bdeb8ade4066645bd968bebd4756b06200a"
FROZEN_INPUT_HASHES = (
    "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
)
WITNESS_HASH = "dfac6b19e589ca220e64bb0e0af2b28fae96e2398f7a0e9f558d10f72f261755"
LIMIT = 2_000_000
LOCAL = (17, 83, 91)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path, expected_hash=None):
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "bounded input")
    if expected_hash is not None:
        require(hashlib.sha256(raw).hexdigest() == expected_hash, "source hash")
    return json.loads(raw, object_pairs_hook=unique)


def load_inputs():
    sources = read_json(PACKAGE / "SOURCES.json")
    pins = {r["path"]: r["sha256"] for r in sources["files"] if r["usage"] == "input"}
    require(pins == dict(zip(INPUTS, FROZEN_INPUT_HASHES, strict=True)), "frozen input pins")
    values = [read_json(ROOT / name, pins[name]) for name in INPUTS]
    predecessor = [r for r in sources["exports"] if r["source_pr"] == 3019]
    require(len(predecessor) == 1, "one PR3019 record")
    record = predecessor[0]
    require(record["source_commit"] == PREDECESSOR, "exact PR3019 source pin")
    require(record["local_copy"] == "WITNESS3019.json", "fixed witness path")
    require(
        record["source_path"] == "research/p104-coherent-support-witness/WITNESS.json",
        "fixed PR3019 source path",
    )
    require(record["sha256"] == WITNESS_HASH, "fixed PR3019 witness hash")
    witness = read_json(PACKAGE / record["local_copy"], record["sha256"])
    return (*values, witness)


def span(rows):
    points = {0}
    for row in rows:
        require(type(row) is int and 0 < row < 512, "binary row")
        require(row not in points, "independent rows")
        points |= {p ^ row for p in points}
    return frozenset(points)


def dimension(points):
    count = len(points)
    require(count > 0 and count & (count - 1) == 0, "power-of-two frame size")
    return count.bit_length() - 1


def data_paths(word):
    names = [f"{kind}{i}" for kind in "XY" for i in range(104)]
    paths = {name: [span(word["initial_frames"][name])] for name in names}
    require(len(word["program"]) == 4058, "frozen data word length")
    for event in word["program"]:
        operation, name = event[:2]
        if operation != "transport":
            require(operation in {"add", "copy", "zero", "erase"}, "known opcode")
            require(not name.startswith("X"), "immutable frozen X")
            if operation in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread frozen Y")
            continue
        if name not in paths:
            continue
        before, after = span(event[2]), span(event[3])
        require(paths[name][-1] == before and before < after, "monotone data path")
        require(event[4] == dimension(after) - dimension(before), "transport rank")
        paths[name].append(after)
    for name in names:
        chain = paths[name]
        require(chain[-1] == span(word["final_frames"][name]), "data endpoint")
        endpoints = (1, 9) if name.startswith("X") else (0, 8)
        require(
            (dimension(chain[0]), dimension(chain[-1])) == endpoints,
            "data dimensions",
        )
    return paths


def endpoint_frames(certificate, paths, witness):
    pairing = witness["pairing"]
    require(type(pairing) is list and len(pairing) == 208, "208 helper assignments")
    require(all(type(b) is int and 0 <= b < 208 for b in pairing), "arrival slots")
    require(len(set(pairing)) == 208, "perfect matching")
    lines = [paths[f"X{i}"][0] for i in range(104)]
    caps = [paths[f"Y{i}"][-1] for i in range(104)]
    require(len(set(lines)) == len(set(caps)) == 104, "distinct endpoints")
    departures, arrivals = [], []
    for index in range(104):
        line_vector = next(p for p in lines[index] if p)
        for form in certificate["forms"]["departure"][index]:
            departures.append(span([line_vector, form]))
        for form in certificate["forms"]["arrival"][index]:
            require(type(form) is int and 0 < form < 512, "arrival functional")
            points = frozenset(
                p for p in caps[index] if (p & form).bit_count() % 2 == 0
            )
            require(dimension(points) == 7, "arrival plane dimension")
            arrivals.append(points)
    for helper, arrival in enumerate(pairing):
        require(departures[helper] <= arrivals[arrival], "compatible endpoint matching")
    return lines, departures, arrivals, caps, pairing


def quotient_subspaces():
    """Extend literal subspaces; no RREF/free-entry census is used."""
    layers = [{frozenset({0})}]
    for _ in range(5):
        following = set()
        for subspace in layers[-1]:
            for vector in range(1, 32):
                if vector not in subspace:
                    following.add(
                        frozenset(subspace | {p ^ vector for p in subspace})
                    )
        layers.append(following)
    require(list(map(len, layers)) == [1, 31, 155, 155, 31, 1], "literal quotient census")
    return layers


def quotient_lifts(low, high):
    """Find five coset generators by extending low inside high."""
    current, generators = set(low), []
    require(len(low) == 4 and len(high) == 128 and low <= high, "endpoint sizes")
    for point in sorted(high):
        if point not in current:
            generators.append(point)
            current |= {p ^ point for p in current}
    require(current == set(high) and len(generators) == 5, "five quotient generators")
    result = []
    for coordinate in range(32):
        lift = 0
        for i, generator in enumerate(generators):
            if coordinate >> i & 1:
                lift ^= generator
        result.append(frozenset(p ^ lift for p in low))
    require(len(set(result)) == 32, "distinct quotient cosets")
    return result


def allowed_frames(endpoints, helper, quotients):
    lines, departures, arrivals, caps, pairing = endpoints
    low, high = departures[helper], arrivals[pairing[helper]]
    cosets = quotient_lifts(low, high)
    frames = {1: {lines[helper // 2]}, 8: {caps[pairing[helper] // 2]}}
    for quotient_dimension, subspaces in enumerate(quotients):
        layer = set()
        for subspace in subspaces:
            points = set()
            for coordinate in subspace:
                points.update(cosets[coordinate])
            layer.add(frozenset(points))
        frames[quotient_dimension + 2] = layer
    require(
        [len(frames[d]) for d in range(1, 9)]
        == [1, 1, 31, 155, 155, 31, 1, 1],
        "complete helper layers",
    )
    return frames


def local_incidence(endpoints, paths):
    quotients = quotient_subspaces()
    local = {h: allowed_frames(endpoints, h, quotients) for h in LOCAL}
    contacts = {str(h): [[] for _ in range(8)] for h in LOCAL}
    target_frames = set(paths["Y40"])
    target_writers = []
    for helper in range(208):
        frames = allowed_frames(endpoints, helper, quotients)
        for d in range(1, 9):
            for h in LOCAL:
                if local[h][d] & frames[d]:
                    contacts[str(h)][d - 1].append(helper)
            if frames[d] & target_frames:
                target_writers.append([d, helper])
    reads, writes = {}, {}
    for h in LOCAL:
        reads[str(h)], writes[str(h)] = [], []
        for d in range(1, 9):
            reads[str(h)].append(
                [s for s in range(104) if local[h][d] & set(paths[f"X{s}"])]
            )
            writes[str(h)].append(
                [t for t in range(104) if local[h][d] & set(paths[f"Y{t}"])]
            )
    direct = [s for s in range(104) if set(paths[f"X{s}"]) & target_frames]
    return contacts, reads, writes, target_writers, direct


def gram_row(fixture):
    doubled_roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            doubled_roots.append(tuple(row))
    doubled_roots += [
        (1, *signs)
        for signs in product((-1, 1), repeat=7)
        if signs.count(-1) % 2 == 0
    ]
    removed = fixture["section4_explicit_P104"]
    removed_roots = {tuple(r) for r in removed["F0"] + removed["C"]}
    ports = sorted(set(doubled_roots) - removed_roots)
    require(
        len(doubled_roots) == 120 and len(removed_roots) == 16 and len(ports) == 104,
        "ordered roots",
    )
    row = [
        Fraction(
            8 * int(s == 40)
            - sum(a * b for a, b in zip(ports[40], root, strict=True)),
            8,
        )
        for s, root in enumerate(ports)
    ]
    return ports, row


def derive(certificate, word, fixture, witness):
    paths = data_paths(word)
    endpoints = endpoint_frames(certificate, paths, witness)
    contacts, reads, writes, target_writers, direct = local_incidence(endpoints, paths)
    _, departures, arrivals, caps, pairing = endpoints
    ports, correction = gram_row(fixture)
    source_lines = [next(p for p in paths[f"X{s}"][0] if p) for s in range(104)]
    require(
        all(bool(correction[s]) == (source_lines[s] in caps[40]) for s in range(104)),
        "row Gram/frame support binding",
    )
    forbidden = sorted(departures[139] - arrivals[pairing[83]])
    required = [s for s, coefficient in enumerate(correction) if coefficient]
    missing = sorted(set(required) - {8, 41, 45})
    return {
        "schema_version": 1,
        "predecessor_commit": PREDECESSOR,
        "literal_contact_helpers": list(LOCAL),
        "contacts_by_dimension": contacts,
        "source_reads_by_dimension": reads,
        "target_writes_by_dimension": writes,
        "Y40_helper_writers": target_writers,
        "Y40_direct_sources": direct,
        "A139_points": sorted(departures[139]),
        "helper83_arrival_slot": pairing[83],
        "A139_outside_B80": forbidden,
        "monotone_helper": 91,
        "Y40_source_support_upper_bound": [8, 41, 45],
        "Y40_required_sources": required,
        "Y40_forced_missing_sources": missing,
        "Y40_forced_missing_count": len(missing),
        "first_counterexample": {
            "target": 40,
            "source": missing[0],
            "coefficient": str(correction[missing[0]]),
            "doubled_target_root": list(ports[40]),
            "doubled_source_root": list(ports[missing[0]]),
        },
        "coverage": (
            "finite literal incidence plus written arbitrary-program monotone-cut "
            "proof; no formal-kernel proof; no_new_kappa"
        ),
    }


def verify_cut(record):
    expected_contacts = {
        "17": [[16, 17], [17], [17], [17], [17], [17], [17], [17, 83]],
        "83": [
            [82, 83], [83], [83], [83, 91], [83, 91], [83, 91], [83], [17, 83]
        ],
        "91": [
            [90, 91], [91], [91], [83, 91, 139], [83, 91, 139],
            [83, 91], [91], [91, 183]
        ],
    }
    require(
        record["contacts_by_dimension"] == expected_contacts,
        "complete local contacts",
    )
    expected_reads = {
        str(h): [[source]] + [[] for _ in range(7)]
        for h, source in ((17, 8), (83, 41), (91, 45))
    }
    require(
        record["source_reads_by_dimension"] == expected_reads,
        "complete local source injections",
    )
    expected_writes = {
        str(h): [[] for _ in range(7)] + [[target]]
        for h, target in ((17, 40), (83, 40), (91, 4))
    }
    require(
        record["target_writes_by_dimension"] == expected_writes,
        "complete local writes",
    )
    require(record["Y40_helper_writers"] == [[8, 17], [8, 83]], "only Y40 writers")
    require(record["Y40_direct_sources"] == [], "no direct Y40 source")
    require(record["A139_points"] == [0, 113, 288, 337], "departure plane A139")
    require(record["helper83_arrival_slot"] == 80, "arrival B80")
    require(record["A139_outside_B80"] == [113, 337], "incompatible relay containment")
    require(record["Y40_source_support_upper_bound"] == [8, 41, 45], "support cut")
    require(len(record["Y40_required_sources"]) == 48, "48 required row coefficients")
    require(record["Y40_forced_missing_count"] == 45, "45 forced missing coefficients")
    require(
        record["Y40_forced_missing_sources"]
        == sorted(set(record["Y40_required_sources"]) - {8, 41, 45}),
        "missing support subtraction",
    )
    first = record["first_counterexample"]
    require(
        (first["target"], first["source"], first["coefficient"]) == (40, 1, "1/2"),
        "nonzero first counterexample",
    )


def rejection_controls(record):
    variants = []
    changed = deepcopy(record)
    changed["contacts_by_dimension"]["91"][3].append(0)
    variants.append(changed)
    changed = deepcopy(record)
    changed["source_reads_by_dimension"]["83"][4] = [1]
    variants.append(changed)
    changed = deepcopy(record)
    changed["A139_outside_B80"] = []
    variants.append(changed)
    changed = deepcopy(record)
    changed["Y40_helper_writers"].append([8, 0])
    variants.append(changed)
    changed = deepcopy(record)
    changed["first_counterexample"]["coefficient"] = "0"
    variants.append(changed)
    for changed in variants:
        try:
            verify_cut(changed)
        except ValueError:
            continue
        raise ValueError("cut-premise mutation accepted")
    return len(variants)


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: independent.py [--emit]")
    record = derive(*load_inputs())
    verify_cut(record)
    record["rejected_premise_mutations"] = rejection_controls(record)
    if "--emit" in sys.argv:
        print(json.dumps(record, indent=2, sort_keys=True))
        return
    expected = read_json(PACKAGE / "INDEPENDENT.json")
    require(
        json.dumps(record, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "exact independent receipt",
    )
    print(
        "PASS_P104_INDEPENDENT_MONOTONE_CUT "
        "helper=91 target=40 forced_missing=45 no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_INDEPENDENT_MONOTONE_CUT: {error}") from error
