#!/usr/bin/env python3
"""Independent complete cache graph, all-D certificate and physical route oracle.

Credit Ali Romman6530/6527/6513/6511, Nick Petalas6608 and retained scalar,
native and tape authors. Source template prices and arithmetic premises are
credited inputs, not newly audited results. Substantial OpenAI Codex assistance.
Apache-2.0. No predecessor or primary implementation is imported or executed.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PIN_SHA = "d9c3cedebf70439e9491e27ab21c9f3ab1638dd3be450217370f96217760d99d"
CASE_SHA = "6643eab23335c5aab85edf2599262d9020c5ce5e646d876e63c275747d8b16b8"
SCHEMA_SHA = "50ae780b73aff908bddb70d99438e7d2ec45d037b07fcccb63fc038948701e26"
START = (-1, -1, -1)
POLICY_KEYS = {"total", "layers", "total_states", "total_edges", "max_layer_states", "states_sha256", "edges_sha256", "potentials_sha256"}
COMMON = {"schema_version", "source_manifest_sha256", "case_manifest_sha256", "policies", "physical"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha((canonical(value) + "\n").encode())


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def bad_number(value):
    raise ValueError("noninteger JSON number: " + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad_number, parse_constant=bad_number)


def compressed(path, limit):
    with gzip.open(path, "rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "compressed input exceeds bounded decoded capacity")
    return parse(raw)


def authenticate():
    for name, expected in (("SOURCE-PINS.json", PIN_SHA), ("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA)):
        need(sha((ROOT / name).read_bytes()) == expected, "source/case/schema digest changed")
    source = parse((ROOT / "SOURCE-PINS.json").read_bytes())
    need(len(source["files"]) == 15, "fifteen pinned source objects required")
    for row in source["files"]:
        raw = (ROOT / row["local_path"]).read_bytes()
        need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "source bytes changed")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob changed")
    parse((ROOT / "SCHEMA.json").read_bytes())
    return parse((ROOT / "CASES.json").read_bytes())


def inputs():
    word = compressed(ROOT / "inputs/WORD.json.gz", 33554432)
    rows = compressed(ROOT / "inputs/CIRCUITS64.json.gz", 33554432)
    certificates = compressed(ROOT / "inputs/CERTIFICATES.json.gz", 33554432)
    need(type(rows) is list and len(rows) == 43 == len(certificates), "43 template price premises required")
    costs, gates = {}, {}
    for row, certificate in zip(rows, certificates):
        need(type(row) is list and len(row) == 3, "template row shape invalid")
        key = (row[0], str(Fraction(row[1])))
        need(key not in costs and type(certificate["total"]) is int and certificate["total"] >= 0, "template price invalid")
        costs[key], gates[key] = certificate["total"], row[2]
    return word, word["program"] + [["EXIT"]], costs, gates


def seek(head, field):
    if head == -1:
        return 128 * field, 0
    delta = field - head - 1
    return 128 * abs(delta), 1 if delta >= 0 else -1


def schedules(held, pending, prefix=()):
    if not pending:
        yield held, prefix
    for index, (load, bank, field) in enumerate(pending):
        if (load and (held[bank] != -1 or field in held)) or (not load and held[bank] != field):
            continue
        after = list(held)
        after[bank] = field if load else -1
        remaining = pending[:index] + pending[index + 1:]
        yield from schedules(tuple(after), remaining, prefix + ((load, bank, field),))


def transfer_plans(slots, required):
    goals = itertools.permutations(required) if required is not None else [(-1, -1)]
    for goal in goals:
        if required is not None and any(old in required and old != new for old, new in zip(slots, goal)):
            continue
        pending = []
        for bank, (old, new) in enumerate(zip(slots, goal)):
            if old == new:
                continue
            if old >= 0:
                pending.append((0, bank, old))
            if new >= 0:
                pending.append((1, bank, new))
        for held, actions in schedules(tuple(slots), tuple(pending)):
            need(held == tuple(goal), "transfer goal not reached")
            yield held, actions


def edges(state, event, costs, resident):
    op, head = event[0], state[2]
    required = tuple(event[1:3]) if op in ("ADD", "COPY") else None
    if required is not None:
        need(len(set(required)) == 2, "distinct scalar operands required")
    for held, actions in transfer_plans(state[:2], required):
        a, b, end = 0, 0, head
        for unused, bank, field in actions:
            ca, cb = seek(end, field)
            a, b, end = a + ca + 1152, b + cb - 3, field
        if required is not None:
            a += 512 + 2 * costs[(op, str(Fraction(event[3])))]
            b -= 256
        elif op == "SCALE":
            ca, cb = seek(end, event[1])
            a += ca + 2688 + costs[(op, str(Fraction(event[2])))]
            b, end = b + cb - 267, event[1]
        else:
            need(op in ("MOVE", "INIT", "CLEAR", "EXIT"), "event opcode invalid")
            if end >= 0:
                a, b = a + 128 * (end + 1), b - 1
            end = -1
        action = {"kind": "old", "transfers": [list(row) for row in actions]}
        yield (*held, end), (a, b), action
    if resident and op == "SCALE" and Fraction(event[2]) == 2 and event[1] in state[:2]:
        yield state, (3284, -2), {"kind": "resident", "transfers": []}


def proposals(events, costs, resident, budget):
    values, layers, parents = {START: (0, 0)}, [[[*START, 0, 0]]], []
    total_states, total_edges = 1, 0
    budget["states"] += 1
    for event in events:
        following, parent = {}, {}
        for state, (one, two) in sorted(values.items()):
            for after, (a, b), action in edges(state, event, costs, resident):
                total_edges += 1
                budget["edges"] += 1
                need(budget["edges"] <= 3000000, "combined complete edge capacity exceeded")
                first, second = one + a + b, two + 2 * a + b
                if after not in following:
                    following[after], parent[after] = (first, second), (state, action)
                else:
                    old_one, old_two = following[after]
                    if second < old_two:
                        parent[after] = state, action
                    following[after] = min(first, old_one), min(second, old_two)
        need(following, "unreachable event layer")
        total_states += len(following)
        budget["states"] += len(following)
        need(budget["states"] <= 500000, "combined complete state capacity exceeded")
        layers.append([[*state, two - one, 2 * one - two] for state, (one, two) in sorted(following.items())])
        parents.append(parent)
        values = following
    need(set(values) == {START}, "complete final origin return missing")
    current, actions = START, []
    for parent in reversed(parents):
        current, action = parent[current]
        actions.append(action)
    need(current == START, "attaining path has wrong initial state")
    return {"total": layers[-1][0][3:], "layers": layers, "actions": list(reversed(actions))}


def typed_action(value):
    need(type(value) is dict and set(value) == {"kind", "transfers"}, "policy action keys invalid")
    need(value["kind"] in ("old", "resident") and type(value["kind"]) is str, "policy action kind invalid")
    need(type(value["transfers"]) is list, "policy transfers must be list")
    for row in value["transfers"]:
        need(type(row) is list and len(row) == 3 and all(type(v) is int for v in row), "transfer requires three integers")
        need(row[0] in (0, 1) and row[1] in (0, 1) and row[2] >= 0, "transfer domain invalid")
    need(value["kind"] != "resident" or not value["transfers"], "resident edge may not transfer fields")


def certificate_layers(certificate, count):
    need(type(certificate) is dict and set(certificate) == {"total", "layers", "actions"}, "certificate keys invalid")
    total = certificate["total"]
    need(type(total) is list and len(total) == 2 and all(type(v) is int for v in total), "affine total needs two integers")
    need(type(certificate["layers"]) is list and len(certificate["layers"]) == count + 1, "certificate layer count invalid")
    need(type(certificate["actions"]) is list and len(certificate["actions"]) == count, "certificate action count invalid")
    result = []
    for rows in certificate["layers"]:
        need(type(rows) is list and rows, "empty certificate layer")
        layer = {}
        for row in rows:
            need(type(row) is list and len(row) == 5 and all(type(v) is int for v in row), "potential row needs five integers")
            state = tuple(row[:3])
            need(all(v >= -1 for v in state) and state not in layer, "potential state invalid/duplicate")
            need(len({v for v in state[:2] if v >= 0}) == sum(v >= 0 for v in state[:2]), "aliased banks")
            layer[state] = tuple(row[3:])
        need(rows == sorted(rows), "potential rows must be sorted")
        result.append(layer)
    need(result[0] == {START: (0, 0)} and set(result[-1]) == {START}, "certificate potential boundary invalid")
    return result


def check_graph(certificate, events, costs, resident):
    layers = certificate_layers(certificate, len(events))
    edge_hash, edge_count = hashlib.sha256(), 0
    for index, event in enumerate(events):
        reachable, frame = set(), []
        for before, potential in sorted(layers[index].items()):
            for after, cost, action in edges(before, event, costs, resident):
                reachable.add(after)
                need(after in layers[index + 1], "missing reachable potential state")
                following = layers[index + 1][after]
                a, b = potential[0] + cost[0] - following[0], potential[1] + cost[1] - following[1]
                all_d_residual(a, b)
                frame.append([list(before), list(after), list(cost), action["kind"], action["transfers"]])
        need(reachable == set(layers[index + 1]), "extra/missing reachable layer state")
        frame.sort()
        edge_hash.update((canonical(frame) + "\n").encode())
        edge_count += len(frame)
    states = [[list(state) for state in sorted(layer)] for layer in layers]
    return {"total": certificate["total"], "layers": len(layers), "total_states": sum(map(len, layers)),
            "total_edges": edge_count, "max_layer_states": max(map(len, layers)),
            "states_sha256": digest(states), "edges_sha256": edge_hash.hexdigest(),
            "potentials_sha256": digest(certificate["layers"])}


def all_d_residual(a, b):
    need(a >= 0 and a + b >= 0, "all-D edge inequality failed")


def ownership_step(alive, owner, slots, event, action, public):
    for load, bank, field in action["transfers"]:
        need(field in alive, "transfer references nonlive field")
        if load:
            need(slots[bank] == -1 and field in owner, "acquisition lacks clean exclusive destination")
            owner.remove(field)
            slots[bank] = field
        else:
            need(slots[bank] == field and field not in owner, "eviction lacks exclusive authority")
            owner.add(field)
            slots[bank] = -1
    op = event[0]
    if action["kind"] == "resident":
        need(op == "SCALE" and Fraction(event[2]) == 2 and event[1] in slots, "illegal resident edge")
    elif op in ("ADD", "COPY"):
        need(event[1] != event[2] and all(field in slots for field in event[1:3]), "scalar operands not resident")
    else:
        need(slots == [-1, -1] and owner == alive, "boundary does not restore complete owner layout")
        if op == "INIT":
            need(event[1] not in alive, "INIT requires fresh field")
            alive.add(event[1]); owner.add(event[1])
        elif op == "CLEAR":
            need(event[1] in alive and event[1] >= public, "CLEAR requires live owned field")
            alive.remove(event[1]); owner.remove(event[1])
        elif op in ("MOVE", "SCALE"):
            need(event[1] in alive, "external operation references nonlive field")
    held = {field for field in slots if field >= 0}
    need(not (held & owner) and held | owner == alive, "exclusive owner partition failed")


def check_path(certificate, events, costs, resident, public):
    state, a, b = START, 0, 0
    alive, owner, slots = set(range(public)), set(range(public)), [-1, -1]
    counts = Counter()
    for event, action in zip(events, certificate["actions"]):
        typed_action(action)
        matches = [(end, cost) for end, cost, candidate in edges(state, event, costs, resident) if candidate == action]
        need(len(matches) == 1, "attaining action is not uniquely legal")
        ownership_step(alive, owner, slots, event, action, public)
        state, cost = matches[0]
        need(state[:2] == tuple(slots), "policy endpoint bank tags differ")
        if event[0] in ("MOVE", "INIT", "CLEAR", "EXIT"):
            need(state == START, "external boundary owner head not at origin")
        a, b = a + cost[0], b + cost[1]
        counts[action["kind"]] += 1
    need(state == START and (a, b) == tuple(certificate["total"]), "attaining affine path total differs")
    need(certificate["layers"][-1] == [[*START, a, b]], "final potential not attained")
    need(alive == owner == set(range(public)) and slots == [-1, -1], "final ownership failed")
    return dict(counts)


def resident_gates(dimension):
    result = []
    for base in range(0, 128 * dimension, 64):
        for offset in range(62, -1, -1):
            first, second = base + offset, base + offset + 1
            result.extend(((first, second), (second, first), (first, second)))
        result.append((base + 63, base))
    return result


def resident_route(dimension):
    cursor, result = 0, []
    for control, target in resident_gates(dimension):
        for address, opcode, operand in ((control, "xor", 0), (target, "flipmask", 1), (control, "xor", 0)):
            while cursor != address:
                direction = 1 if address > cursor else -1
                result.append(["move", 0, direction])
                cursor += direction
            result.append([opcode, 0, operand])
    while cursor:
        result.append(["move", 0, -1])
        cursor -= 1
    return result


def validate_route(route):
    need(type(route) is list and len(route) <= 220000, "resident route size invalid")
    for row in route:
        need(type(row) is list and len(row) == 3 and type(row[0]) is str
             and type(row[1]) is int and type(row[2]) is int, "physical instruction types invalid")
        op, first, second = row
        need(first == 0 and ((op == "move" and second in (-1, 1)) or (op == "xor" and second == 0)
             or (op == "flipmask" and second == 1)), "resident primitive outside active ribbon/control0")


def physical_execute(route, bits, carry, inverse=False, active_bank=0):
    active, other, owner = list(bits), [i % 2 for i in range(len(bits))], [1] * (3 * len(bits))
    other_before, owner_before = other[:], owner[:]
    ribbons = [active, other] if active_bank == 0 else [other, active]
    need(ribbons[active_bank] is active and ribbons[1 - active_bank] is other, "actual active bank binding failed")
    head, owner_head, scratch, reads, writes, moves = 0, len(bits) + 1, 0, 0, 0, 0
    for op, unused, operand in reversed(route) if inverse else route:
        if op == "move":
            head += -operand if inverse else operand
            need(0 <= head < len(active), "physical head leaves active ribbon")
            moves += 1
        elif op == "xor":
            scratch ^= active[head]
            reads += 1
        else:
            active[head] ^= scratch
            reads += 1
            writes += 1
    need(head == 0 and scratch == 0, "resident head/control not restored")
    need(other == other_before and owner == owner_before and owner_head == len(bits) + 1, "unrelated owner/ribbon/head changed")
    return active, carry, (reads, writes, moves)


def expected_bits(bits):
    result = []
    for base in range(0, len(bits), 64):
        record = bits[base:base + 64]
        result.extend([record[63] ^ record[62]] + record[:63])
    return result


def source_basis(gates):
    source = gates[("SCALE", "2")]
    need(all(type(gate) is list and len(gate) == 2 for gate in source), "SCALE2 dependency must be linear CNOT circuit")
    for column in range(129):
        initial = [int(index == column) for index in range(129)]
        result = initial[:]
        for control, target in source:
            need(type(control) is int and type(target) is int and 0 <= control < 129 and 0 <= target < 129 and control != target,
                 "source SCALE2 CNOT domain invalid")
            result[target] ^= result[control]
        need(result == expected_bits(initial[:128]) + initial[128:], "resident map differs from pinned SCALE2 basis column")
    return 129


def physical_record(dimension, route):
    need(type(dimension) is int and dimension in (1, 2), "frozen physical dimensions are1,2")
    validate_route(route)
    traffic = None
    length = 128 * dimension
    for column in range(length + 1):
        bits, carry = [int(index == column) for index in range(length)], int(column == length)
        for bank in (0, 1):
            result, end_carry, counts = physical_execute(route, bits, carry, active_bank=bank)
            need(result == expected_bits(bits) and end_carry == carry, "actual resident route basis endpoint differs")
            restored, restored_carry, inverse_counts = physical_execute(route, result, carry, True, bank)
            need(restored == bits and restored_carry == carry and inverse_counts == counts, "literal physical inverse differs")
            traffic = counts
    reads, writes, moves = traffic
    need((reads, writes, moves) == (1140 * dimension, 380 * dimension, 1764 * dimension - 2), "physical unit traffic differs")
    return {"D": dimension, "reads": reads, "writes": writes, "moves": moves,
            "total": reads + writes + moves, "basis_columns": length + 1}


def signed_fixtures(cases, dimension, route):
    fixtures = cases["signed_values"][str(dimension)]
    need(len(fixtures) == (25 if dimension == 1 else 18), "signed fixture schedule changed")
    for values in fixtures:
        need(type(values) is list and len(values) == 2 * dimension
             and all(type(v) is int and -(1 << 62) <= v < (1 << 62) for v in values), "signed entrance guard failed")
        bits = [(value >> bit) & 1 for value in values for bit in range(64)]
        for bank in (0, 1):
            after, carry, unused = physical_execute(route, bits, 0, active_bank=bank)
            outputs = [sum(after[64 * i + bit] << bit for bit in range(64)) for i in range(2 * dimension)]
            outputs = [value - (1 << 64) if value >> 63 else value for value in outputs]
            need(outputs == [2 * value for value in values] and carry == 0, "signed physical doubling failed")
            restored, carry, unused = physical_execute(route, after, 0, True, bank)
            need(restored == bits and carry == 0, "signed literal inverse failed")
    return len(fixtures)


def validate_common(value):
    need(type(value) is dict and set(value) == COMMON, "receipt top keys invalid")
    need(type(value["schema_version"]) is int and value["schema_version"] == 1, "receipt version must be integer1")
    need(value["source_manifest_sha256"] == PIN_SHA and value["case_manifest_sha256"] == CASE_SHA, "receipt source/case binding differs")
    need(type(value["policies"]) is dict and set(value["policies"]) == {"baseline", "candidate"}, "policy profile keys invalid")
    for row in value["policies"].values():
        need(type(row) is dict and set(row) == POLICY_KEYS, "policy profile shape invalid")
        need(type(row["total"]) is list and len(row["total"]) == 2 and all(type(v) is int for v in row["total"]), "policy affine total invalid")
        for key in ("layers", "total_states", "total_edges", "max_layer_states"):
            need(type(row[key]) is int and row[key] > 0, "policy count must be positive integer")
        for key in ("states_sha256", "edges_sha256", "potentials_sha256"):
            need(type(row[key]) is str and len(row[key]) == 64 and all(c in "0123456789abcdef" for c in row[key]), "policy digest invalid")
    physical = value["physical"]
    need(type(physical) is dict and set(physical) == {"source_basis_columns", "records"}, "physical profile keys invalid")
    need(type(physical["source_basis_columns"]) is int and physical["source_basis_columns"] == 129, "source basis count invalid")
    need(type(physical["records"]) is list and len(physical["records"]) == 2, "physical record count invalid")
    for row, dimension in zip(physical["records"], (1, 2)):
        need(type(row) is dict and set(row) == {"D", "reads", "writes", "moves", "total", "basis_columns"}, "physical record keys invalid")
        need(all(type(v) is int and v > 0 for v in row.values()) and row["D"] == dimension, "physical counts/order invalid")


def actual_artifact(path, events, costs, public, expected, cases):
    value = compressed(path, 67108864)
    need(type(value) is dict and set(value) == {"schema_version", "width", "baseline", "candidate", "routes"}, "POLICY artifact keys invalid")
    need(type(value["schema_version"]) is int and value["schema_version"] == 1 and type(value["width"]) is int and value["width"] == 64,
         "POLICY artifact version/width invalid")
    result, path_counts = {}, {}
    for name, resident in (("baseline", False), ("candidate", True)):
        result[name] = check_graph(value[name], events, costs, resident)
        need(result[name] == expected["policies"][name], "actual submitted graph/potentials differ")
        path_counts[name] = check_path(value[name], events, costs, resident, public)
    need(type(value["routes"]) is list and len(value["routes"]) == 2, "actual route record count invalid")
    records = []
    for row, dimension in zip(value["routes"], (1, 2)):
        need(type(row) is dict and set(row) == {"D", "word"} and type(row["D"]) is int and row["D"] == dimension, "actual route record invalid")
        records.append(physical_record(dimension, row["word"]))
        signed_fixtures(cases, dimension, row["word"])
    need(records == expected["physical"]["records"], "actual submitted physical profile differs")
    return {"actual_all_edges_and_attaining_paths_checked": True, "path_kinds": path_counts,
            "actual_policy_canonical_sha256": digest(value)}


def rejected(function, value):
    try:
        function(value)
    except ValueError:
        return True
    return False


def controls(value):
    invalid = parse(canonical(value)); invalid["schema_version"] = True
    result = {"duplicate_json_rejected": rejected(parse, '{"x":1,"x":2}'),
              "nonfinite_json_rejected": rejected(parse, '{"x":NaN}'),
              "float_json_rejected": rejected(parse, '{"x":1.0}'),
              "boolean_schema_rejected": rejected(validate_common, invalid),
              "resident_transfer_rejected": rejected(typed_action, {"kind": "resident", "transfers": [[0, 0, 1]]}),
              "boolean_transfer_rejected": rejected(typed_action, {"kind": "old", "transfers": [[True, 0, 1]]}),
              "other_bank_route_rejected": rejected(validate_route, [["move", 1, 1]]),
              "boolean_route_rejected": rejected(validate_route, [["xor", False, 0]]),
              "unsupported_dimension_rejected": rejected(lambda d: physical_record(d, []), 3)}
    need(all(result.values()), "oracle negative control failed")
    return result


def rejects_reason(function, value, phrase):
    try:
        function(value)
    except ValueError as error:
        need(phrase in str(error), "negative control failed at unintended guard: " + str(error))
        return True
    return False


def semantic_controls(costs):
    events = [["ADD", 0, 1, "1"], ["EXIT"]]
    cert = proposals(events, costs, True, {"states": 0, "edges": 0})
    missing = parse(canonical(cert)); missing["layers"][1].pop()
    drift = parse(canonical(cert)); drift["layers"][1][0][2] = 999; drift["layers"][1].sort()
    coefficient = parse(canonical(cert)); coefficient["layers"][1][0][3] += 1; coefficient["layers"][1][0][4] -= 3
    absent = {"total": [0, 0], "actions": [{"kind": "resident", "transfers": []}], "layers": []}
    route = resident_route(1)
    first_move = next(i for i, row in enumerate(route) if row[0] == "move")
    no_move = route[:first_move] + route[first_move + 1:]
    resident_events = [["ADD", 0, 1, "1"], ["SCALE", 0, "2"], ["EXIT"]]
    resident_drift = proposals(resident_events, costs, True, {"states": 0, "edges": 0})
    next(row for row in resident_drift["layers"][2] if row[0] >= 0)[2] = 999
    resident_drift["layers"][2].sort()
    result = {"missing_reachable_state_rejected": rejects_reason(lambda c: check_graph(c, events, costs, True), missing, "reachable"),
              "owner_head_drift_rejected": rejects_reason(lambda c: check_graph(c, events, costs, True), drift, "reachable"),
              "resident_self_state_drift_rejected": rejects_reason(lambda c: check_graph(c, resident_events, costs, True), resident_drift, "reachable"),
              "all_D_coefficient_rejected": rejects_reason(lambda c: check_graph(c, events, costs, True), coefficient, "all-D"),
              "D1_D2_positive_bad_residual_rejected": rejects_reason(lambda x: all_d_residual(*x), (-1, 3), "all-D"),
              "absent_resident_target_rejected": rejects_reason(lambda c: check_path(c, [["SCALE", 0, "2"]], costs, True, 2), absent, "uniquely legal"),
              "occupied_load_rejected": rejects_reason(lambda a: ownership_step({0, 1, 2}, {2}, [0, 1], ["ADD", 0, 1, "1"], a, 3),
                                                        {"kind": "old", "transfers": [[1, 0, 2]]}, "clean exclusive"),
              "unflushed_owner_rejected": rejects_reason(lambda a: ownership_step({0, 1}, {1}, [0, -1], ["MOVE", 0, 1], a, 2),
                                                          {"kind": "old", "transfers": []}, "complete owner"),
              "missing_unit_move_rejected": rejects_reason(lambda r: physical_record(1, r), no_move, "physical head")}
    need(all(result.values()), "semantic artifact control failed")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--first-evidence", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.check_primary), "blind emission cannot read primary data")
    cases = authenticate()
    word, events, costs, gates = inputs()
    budget = {"states": 0, "edges": 0}
    certificates = {name: proposals(events, costs, enabled, budget) for name, enabled in (("baseline", False), ("candidate", True))}
    if args.first_evidence:
        with args.first_evidence.open("xb") as stream:
            stream.write(gzip.compress((canonical(certificates) + "\n").encode(), mtime=0))
    policies = {name: check_graph(certificates[name], events, costs, enabled) for name, enabled in (("baseline", False), ("candidate", True))}
    need(policies["baseline"]["total"] == [800847760, -5118198], "credited old scalar policy total differs")
    paths = {name: check_path(certificates[name], events, costs, enabled, word["public"]) for name, enabled in (("baseline", False), ("candidate", True))}
    physical = {"source_basis_columns": source_basis(gates), "records": [physical_record(d, resident_route(d)) for d in (1, 2)]}
    signed = sum(signed_fixtures(cases, d, resident_route(d)) for d in (1, 2))
    value = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA, "policies": policies, "physical": physical}
    validate_common(value)
    diagnostic = {"controls": controls(value), "semantic_controls": semantic_controls(costs), "signed_fixtures": signed,
                  "own_attaining_path_kinds": paths, "code_sha256": sha(Path(__file__).read_bytes())}
    if args.emit:
        with args.emit.open("x") as stream:
            stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    else:
        retained = parse((ROOT / "ORACLE.json").read_bytes())
        validate_common(retained)
        need(canonical(retained) == canonical(value), "retained oracle receipt differs")
    if args.check_primary:
        peer = parse(args.check_primary.read_bytes())
        validate_common(peer)
        need(canonical(peer) == canonical(value), "actual complete primary receipt differs")
        diagnostic["actual_primary"] = actual_artifact(args.check_primary.parent / "POLICY.json.gz", events, costs, word["public"], value, cases)
    print("PASS_P104_RESIDENT_SCALE_POLICY_ORACLE " + canonical(diagnostic))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL_P104_RESIDENT_SCALE_POLICY_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
