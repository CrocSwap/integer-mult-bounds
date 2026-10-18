#!/usr/bin/env python3
"""Independent exact replay of the fixed two-target circuit.

No imports from the producer, primary checker, or predecessor executables.
Logical rows use dense integer vectors and a common power-of-two denominator;
frames use binary Gaussian elimination. This is an exact finite check, not a
native Clifford compiler or a proof of the full multiplication theorem.
"""

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUTS = HERE.parent / "p104-native-channel" / "inputs"
WITNESS_SHA = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
FIXTURE_SHA = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"


class AuditError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise AuditError(message)


def read_pinned(path, expected):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected, "frozen input hash: " + path.name)
    return json.loads(raw)


def binary_basis(vectors):
    """Canonical reduced basis; do not enumerate a frame's elements."""
    pivots = {}
    for original in vectors:
        need(type(original) is int and 0 < original < 512, "invalid binary vector")
        v = original
        for bit in sorted(pivots, reverse=True):
            if v & (1 << bit):
                v ^= pivots[bit]
        if not v:
            continue
        bit = v.bit_length() - 1
        for old_bit in list(pivots):
            if pivots[old_bit] & (1 << bit):
                pivots[old_bit] ^= v
        pivots[bit] = v
    return tuple(pivots[b] for b in sorted(pivots, reverse=True))


def frame(vectors):
    need(isinstance(vectors, list), "frame is not a basis list")
    result = binary_basis(vectors)
    need(len(result) == len(vectors), "dependent frame basis")
    return result


def in_frame(vector, basis):
    for pivot in basis:
        if vector & (1 << (pivot.bit_length() - 1)):
            vector ^= pivot
    return vector == 0


def subset(small, large):
    return all(in_frame(v, large) for v in small)


FULL = binary_basis([1 << i for i in range(9)])


def root_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            roots.add(tuple(v))
    for tail in product((-1, 1), repeat=7):
        v = (1,) + tail
        if sum(a < 0 for a in v) % 2 == 0:
            roots.add(v)
    section = fixture["section4_explicit_P104"]
    removed = {tuple(v) for v in section["F0"] + section["C"]}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots,
         "root reconstruction")
    ports = sorted(roots - removed)
    need(len(ports) == 104, "P104 port count")
    return ports


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def dyadic(value):
    need(type(value) in (int, str), "scalar coefficient must be exact")
    parts = str(value).split("/")
    need(len(parts) <= 2, "scalar coefficient syntax")
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    need(denominator > 0 and denominator & (denominator - 1) == 0,
         "non-dyadic scalar coefficient")
    exponent = denominator.bit_length() - 1
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    return numerator, exponent


def normalize(numerators, exponent):
    nonzero = [abs(n) for n in numerators if n]
    if not nonzero:
        return [0] * len(numerators), 0
    shift = min(exponent, min((n & -n).bit_length() - 1 for n in nonzero))
    return [n >> shift for n in numerators], exponent - shift


def add_rows(target, source, coefficient):
    a, ea = target
    b, eb = source
    n, en = dyadic(coefficient)
    exponent = max(ea, eb + en)
    return normalize([(x << (exponent - ea)) + n * (y << (exponent - eb - en))
                      for x, y in zip(a, b)], exponent)


def acquisition_premises(witness, ports):
    paths = {name: [frame(basis)] for name, basis in witness["initial_frames"].items()}
    for event in witness["program"]:
        if event[0] == "transport" and event[1] in paths:
            paths[event[1]].append(frame(event[3]))
        if event[0] in ("add", "copy"):
            need(not event[1].startswith("X"), "original source is written")
            need(not event[2].startswith("Y"), "original target is read")
    correction = [{s: 8 * (s == t) - dot(ports[t], ports[s]) for s in range(104)}
                  for t in (0, 1)]
    correction = [{s: c for s, c in row.items() if c} for row in correction]
    endpoints = [frame(witness["final_frames"]["Y" + str(t)]) for t in (0, 1)]
    escapes = []
    for t in (0, 1):
        need(len(correction[t]) == 48 and set(correction[t].values()) == {-4, 4},
             "correction support or coefficient")
        h = endpoints[t]
        need(len(h) == 8, "target endpoint dimension")
        need(all(subset(b, h) for b in paths["Y" + str(t)]), "target path leaves endpoint")
        for s in sorted(correction[t]):
            source_path = paths["X" + str(s)]
            need(len(source_path) > 1 and len(source_path[0]) == 1,
                 "source initial line")
            need(all(subset(a, b) for a, b in zip(source_path, source_path[1:])),
                 "source path is not monotone")
            need(subset(source_path[0], h), "required initial line outside endpoint")
            escape = next((v for v in source_path[1] if not in_frame(v, h)), None)
            need(escape is not None, "first expansion does not escape endpoint")
            need([i for i, b in enumerate(source_path) if subset(b, h)] == [0],
                 "a later source frame remains inside endpoint")
            need(all(a != b for a in source_path for b in paths["Y" + str(t)]),
                 "direct source-target contact")
            escapes.append([t, s, escape])
    union = set(correction[0]) | set(correction[1])
    shared = set(correction[0]) & set(correction[1])
    exclusive = [set(correction[t]) - shared for t in (0, 1)]
    need(len(union) == 78 and len(shared) == 18, "two-target support union")
    need(len({paths["X" + str(s)][0] for s in union}) == 78, "distinct acquisition lines")
    intersection = binary_basis([v for v in range(1, 512)
                                 if in_frame(v, endpoints[0]) and in_frame(v, endpoints[1])])
    need(len(intersection) == 7, "intersection dimension")
    need(all(subset(paths["X" + str(s)][0], intersection) for s in shared),
         "shared source outside intersection")
    ratios = {s: correction[1][s] // correction[0][s] for s in shared}
    need(Counter(ratios.values()) == {-1: 9, 1: 9}, "shared coefficient ratios")
    return dict(correction=correction, endpoints=endpoints, union=union,
                shared=shared, exclusive=exclusive, intersection=intersection,
                ratios=ratios, escapes=escapes)


def check_metadata(circuit, premises):
    need(circuit["schema_version"] == 1 and circuit["targets"] == [0, 1], "circuit schema/targets")
    need(circuit["source_witness_sha256"] == WITNESS_SHA, "circuit source pin")
    need(circuit["shared"] == sorted(premises["shared"]), "shared metadata")
    need(circuit["exclusive"] == [sorted(s) for s in premises["exclusive"]], "exclusive metadata")
    need(frame(circuit["shared_frame"]) == premises["intersection"], "shared frame metadata")
    a, b = circuit["shared_pivots"]
    need(a in premises["shared"] and b in premises["shared"] and a != b,
         "shared pivot membership")
    need(premises["ratios"][a] == -1 and premises["ratios"][b] == 1,
         "shared pivot ratios")
    expected = {}
    for s in premises["union"]:
        t = 0 if s in premises["correction"][0] else 1
        expected[str(s)] = dyadic(str(premises["correction"][t][s]) + "/8")
    need({s: dyadic(c) for s, c in circuit["capture_coefficients"].items()} == expected,
         "capture coefficient metadata")
    names = {"N" + str(s) for s in premises["union"]}
    need(set(circuit["initial_frames"]) == set(circuit["final_frames"]) == names,
         "new helper inventory")
    need(all(frame(b) == () for b in circuit["initial_frames"].values()), "helper not initially ZERO")
    need(all(frame(b) == FULL for b in circuit["final_frames"].values()), "helper not finally FULL")


def replay(witness, ports, circuit=None, premises=None):
    if circuit is not None:
        check_metadata(circuit, premises)
    initial = dict(witness["initial_frames"])
    final = dict(witness["final_frames"])
    if circuit is not None:
        initial.update(circuit["initial_frames"])
        final.update(circuit["final_frames"])
    names = sorted(initial)
    index = {name: j for j, name in enumerate(names)}
    size = len(names)
    rows = {name: ([int(j == index[name]) for j in range(size)], 0) for name in names}
    frames = {name: frame(b) for name, b in initial.items()}
    new_names = set(circuit["initial_frames"]) if circuit else set()
    insertion_map = {}
    if circuit is not None:
        cuts = [block["completed_cut"] for block in circuit["insertions"]]
        need(cuts == [0, len(witness["program"])], "insertion cuts")
        insertion_map = {block["completed_cut"]: block["events"] for block in circuit["insertions"]}
    word = []
    for cut in range(len(witness["program"]) + 1):
        word.extend((True, event) for event in insertion_map.get(cut, []))
        if cut < len(witness["program"]):
            word.append((False, witness["program"][cut]))
    profile, added_profile = Counter(), Counter()
    added_ops = Counter()
    added_source_reads = 0
    deliveries = Counter()
    max_denominator_exp = 0
    max_reduced_numerator = 1
    for position, (added, event) in enumerate(word):
        op = event[0]
        label = "event " + str(position) + ": "
        if added:
            need(op in ("add", "transport"), label + "forbidden added operation")
            added_ops[op] += 1
        if op == "transport":
            need(len(event) == 5, label + "transport shape")
            _, name, before, after, charge = event
            a, b = frame(before), frame(after)
            need(name in frames and frames[name] == a, label + "transport entry frame")
            need(subset(a, b) or subset(b, a), label + "nonnested transport")
            rank = abs(len(a) - len(b))
            need(type(charge) is int and charge == rank and rank > 0,
                 label + "transport charge")
            if added:
                need(name in new_names and subset(a, b), label + "added monotone ownership")
                added_profile[rank] += 1
            profile[rank] += 1
            frames[name] = b
            continue
        if op == "add":
            need(len(event) == 5, label + "ADD shape")
            _, destination, source, coefficient, basis = event
            common = frame(basis)
            need(destination in rows and source in rows and destination != source, label + "ADD operands")
            need(frames[destination] == frames[source] == common, label + "ADD frame")
            if added:
                need(destination in new_names or destination in ("Y0", "Y1"), label + "added write ownership")
                need(source in new_names or (source.startswith("X") and source in witness["initial_frames"]),
                     label + "forbidden added read")
                if source.startswith("X"):
                    need(destination in new_names, label + "direct source-target ADD")
                    added_source_reads += 1
                if destination in ("Y0", "Y1"):
                    need(source in new_names, label + "target source ownership")
                    if common == frame(witness["final_frames"][destination]):
                        deliveries[destination] += 1
            rows[destination] = add_rows(rows[destination], rows[source], coefficient)
            numerators, exponent = rows[destination]
            max_denominator_exp = max(max_denominator_exp, exponent)
            for n in numerators:
                if n:
                    shift = min(exponent, (abs(n) & -abs(n)).bit_length() - 1)
                    max_reduced_numerator = max(max_reduced_numerator, abs(n) >> shift)
        elif op == "zero":
            need(len(event) == 3 and event[1] == "C" and "C" not in rows, label + "private allocation")
            rows["C"] = ([0] * size, 0)
            frames["C"] = frame(event[2])
        elif op == "copy":
            need(len(event) == 4 and event[1] == "C", label + "private COPY ownership")
            _, destination, source, basis = event
            need(destination in rows and source in rows and not any(rows[destination][0]),
                 label + "COPY destination not zero")
            need(frames[destination] == frames[source] == frame(basis), label + "COPY frame")
            rows[destination] = (rows[source][0][:], rows[source][1])
        elif op == "erase":
            need(len(event) == 3 and event[1] == "C" and "C" in rows, label + "private discard ownership")
            need(frames["C"] == frame(event[2]), label + "private discard frame")
            del rows["C"]
            del frames["C"]
        else:
            raise AuditError(label + "unknown operation")
    need(set(rows) == set(names), "final live registers")
    for name in names:
        need(frames[name] == frame(final[name]), "endpoint frame " + name)
        expected = [0] * size
        expected[index[name]] = 8
        if name.startswith("Y"):
            t = int(name[1:])
            for s in range(104):
                expected[index["X" + str(s)]] = (8 * (s == t) if circuit is not None and t in (0, 1)
                                                else dot(ports[t], ports[s]))
        need(rows[name] == normalize(expected, 3), "endpoint operator " + name)
    expected_base = Counter({1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8})
    need(profile - added_profile == expected_base, "baseline transport invoice")
    if circuit is not None:
        need(added_profile == {1: 142, 2: 16, 6: 18, 7: 60}, "added transport invoice")
        need(added_ops == {"transport": 236, "add": 440}, "added operation invoice")
        need(added_source_reads == 156, "added source-read count")
        need(deliveries == {"Y0": 2, "Y1": 2}, "final target deliveries")
    payload = {"columns": names, "rows": [[name, rows[name][1], rows[name][0]] for name in names]}
    digest = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
    return dict(columns=size, operator_coefficients=size * size, events=len(word),
                endpoint_integer_dyadic_sha256=digest,
                added_rank_profile=dict(sorted(added_profile.items())),
                added_rank_mass=sum(k * v for k, v in added_profile.items()),
                added_operations=dict(added_ops), added_source_reads=added_source_reads,
                final_deliveries=dict(deliveries),
                maximum_logical_denominator_exponent=max_denominator_exp,
                maximum_reduced_logical_numerator=max_reduced_numerator)


def run_controls(witness, ports, circuit, premises):
    rejected = []
    for name in ("dirty_compensation", "capture", "half_mix", "unmerge", "cleanup", "charge", "source_frame"):
        changed = deepcopy(circuit)
        early, late = [block["events"] for block in changed["insertions"]]
        if name == "dirty_compensation":
            del early[0]
            reason = "endpoint operator"
        elif name == "capture":
            del early[next(i for i, e in enumerate(early) if e[0] == "add" and e[2].startswith("X"))]
            reason = "endpoint operator"
        elif name == "half_mix":
            event = next(e for e in early if e[0] == "add" and e[1].startswith("N")
                         and e[2].startswith("N") and str(e[3]) == "-1/2")
            event[3] = "1/2"
            reason = "endpoint operator"
        elif name == "unmerge":
            del late[next(i for i, e in enumerate(late) if e[0] == "add"
                          and e[1].startswith("N") and e[2].startswith("N"))]
            reason = "endpoint operator"
        elif name == "cleanup":
            del late[-1]
            reason = "endpoint operator"
        elif name == "charge":
            event = next(e for e in early if e[0] == "transport")
            event[4] += 1
            reason = "transport charge"
        else:
            event = next(e for e in early if e[0] == "add" and e[2].startswith("X"))
            event[2] = "X1"
            reason = "ADD frame"
        try:
            replay(witness, ports, changed, premises)
        except AuditError as error:
            need(reason in str(error), name + " rejected for an unintended reason: " + str(error))
        else:
            raise AuditError("control unexpectedly accepted: " + name)
        rejected.append(name)
    equivalent = deepcopy(circuit)
    for key in ("initial_frames", "final_frames"):
        for basis in equivalent[key].values():
            basis.reverse()
    equivalent["shared_frame"].reverse()
    for block in equivalent["insertions"]:
        for event in block["events"]:
            if event[0] == "add":
                event[4].reverse()
            else:
                event[2].reverse()
                event[3].reverse()
    need(replay(witness, ports, equivalent, premises) == replay(witness, ports, circuit, premises),
         "equivalent frame-basis presentation rejected")
    return {"rejected": rejected, "accepted": ["reordered_frame_bases"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--circuit", type=Path, default=HERE / "CIRCUIT.json")
    parser.add_argument("--skip-controls", action="store_true")
    args = parser.parse_args()
    witness = read_pinned(INPUTS / "LOWRANK-WITNESS.json", WITNESS_SHA)
    fixture = read_pinned(INPUTS / "P104-FIXTURE.json", FIXTURE_SHA)
    ports = root_ports(fixture)
    circuit = json.loads(args.circuit.read_text())
    premises = acquisition_premises(witness, ports)
    baseline = replay(witness, ports)
    result = replay(witness, ports, circuit, premises)
    result["baseline"] = baseline
    result["acquisition_lifetimes_lower_bound"] = len(premises["union"])
    result["all_required_source_target_pairs_checked"] = len(premises["escapes"])
    result["source_escape_witness_sha256"] = hashlib.sha256(
        json.dumps(premises["escapes"], separators=(",", ":")).encode()).hexdigest()
    if not args.skip_controls:
        result["controls"] = run_controls(witness, ports, circuit, premises)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_P104_TWO_TARGET_INDEPENDENT columns=358 lifetimes=78 rank_mass=702 no_new_kappa")


if __name__ == "__main__":
    main()
