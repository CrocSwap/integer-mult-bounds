#!/usr/bin/env python3
"""Exact sparse boundary and invoice check for the pooled P104 partial word."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / "p104-native-channel/inputs"
PINS = {
    NATIVE / "LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    NATIVE / "P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    HERE / "inputs/PR2504-CIRCUIT.json": "96459a07c79fd1b711af6343bc9c004d91e28cd0da3306c290cff657082b110d",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    raw = path.read_bytes()
    need(len(raw) <= 3_000_000, "bounded input")
    if path in PINS:
        need(sha256(raw).hexdigest() == PINS[path], "source pin " + str(path))
    return json.loads(raw)


def space(vectors):
    need(isinstance(vectors, list) and len(vectors) <= 9, "frame size")
    result = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "binary label")
        result |= {value ^ vector for value in tuple(result)}
    need(len(result) == 1 << len(vectors), "independent basis")
    return frozenset(result)


def root_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[i], row[j] = 2, 2*sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    need(len(roots) == 120, "E8 root lines")
    removed = set(map(tuple, fixture["F0"] + fixture["C"]))
    result = sorted(roots - removed)
    need(len(result) == 104, "104 frozen ports")
    return result


def events(word, circuit):
    insertions = circuit["insertions"]
    need(len(insertions) <= 20, "bounded insertion cuts")
    cuts = [part["completed_cut"] for part in insertions]
    need(cuts == sorted(set(cuts)), "unique ordered cuts")
    need(all(type(k) is int and 0 <= k <= len(word["program"]) for k in cuts), "cut range")
    by_cut = {part["completed_cut"]: part["events"] for part in insertions}
    need(sum(len(v) for v in by_cut.values()) <= 1500, "bounded added word")
    result = []
    for cut in range(len(word["program"]) + 1):
        result.extend(by_cut.get(cut, []))
        if cut < len(word["program"]):
            result.append(word["program"][cut])
    need(len(result) <= 6000, "bounded complete word")
    return result


def apply(event, rows, frames):
    op, register = event[:2]
    if op == "transport":
        _, register, old, new, rank = event
        a, b = space(old), space(new)
        need(register in frames and frames[register] == a, "transport entry")
        need((a < b or b < a) and rank == abs(len(new)-len(old)), "nested paid rank")
        frames[register] = b
    elif op == "zero":
        need(register == "C" and register not in rows, "owned initialization")
        rows[register], frames[register] = {}, space(event[2])
    elif op == "erase":
        need(register == "C" and frames[register] == space(event[2]), "owned discard")
        del rows[register], frames[register]
    elif op in ("add", "copy"):
        source = event[2]
        frame = space(event[-1])
        need(register != source and frames[register] == frames[source] == frame, "common-chart read")
        if op == "copy":
            need(not rows[register], "owned zero before COPY")
            rows[register] = dict(rows[source])
            return
        need(type(event[3]) in (str, int) and len(str(event[3])) <= 16, "bounded rational")
        value = Q(event[3])
        for name, coefficient in tuple(rows[source].items()):
            updated = rows[register].get(name, Q(0)) + value*coefficient
            if updated:
                rows[register][name] = updated
            else:
                rows[register].pop(name, None)
    else:
        raise ValueError("unknown event")


def replay(word, circuit, ports, corrected=True):
    initial = dict(word["initial_frames"])
    need(not set(initial) & set(circuit["initial_frames"]), "disjoint new dirty helpers")
    initial.update(circuit["initial_frames"])
    need(len(initial) <= 400, "bounded arbitrary inputs")
    rows = {r: {r: Q(1)} for r in initial}
    frames = {r: space(f) for r, f in initial.items()}
    program = events(word, circuit)
    for event in program:
        apply(event, rows, frames)
    final = dict(word["final_frames"])
    final.update(circuit["final_frames"])
    need(set(rows) == set(frames) == set(final) == set(initial), "all private lifetimes closed")
    for register in initial:
        expected = {register: Q(1)}
        if register.startswith("Y"):
            target = int(register[1:])
            if corrected and target < 3:
                expected[f"X{target}"] = Q(1)
            else:
                for source, root in enumerate(ports):
                    value = Q(sum(a*b for a, b in zip(ports[target], root)), 8)
                    if value:
                        expected[f"X{source}"] = value
        need(rows[register] == expected, "arbitrary-input endpoint " + register)
        need(frames[register] == space(final[register]), "final frame " + register)
    return program, len(initial)


def footprint(event, registers):
    return event[1] in registers or (event[0] in ("add", "copy") and event[2] in registers)


def preserved(ancestor, candidate):
    selected = [g for g in ancestor["groups"] if g["targets"] in ([0, 2], [0, 1, 2])]
    old = {f"N{s}" for g in selected for s in g["sources"]}
    old |= {r for g in selected for r in g["extra_helpers"]}
    new = old - {r for g in selected for r in g["extra_helpers"]}
    new |= {"POOL1", "POOL2"}
    def retained(circuit, removed):
        return [[part["completed_cut"], [e for e in part["events"] if not footprint(e, removed)]]
                for part in circuit["insertions"]]
    need(retained(ancestor, old) == retained(candidate, new), "literal preservation of all other groups")
    need(candidate["late_acquisition"] == ancestor["late_acquisition"], "unchanged late branch")
    need(candidate["groups"] == [g for g in ancestor["groups"] if g not in selected], "retained groups")
    for key in ("initial_frames", "final_frames"):
        need({r: f for r, f in ancestor[key].items() if r not in old}
             == {r: f for r, f in candidate[key].items() if r not in new}, "unchanged helper boundaries")
    return len(old), len(new)


def bill(word, circuit):
    added = [e for part in circuit["insertions"] for e in part["events"]]
    profile = Counter(e[4] for e in added if e[0] == "transport")
    return {"helpers": len(circuit["initial_frames"]), "added_events": len(added),
            "added_adds": sum(e[0] == "add" for e in added),
            "added_transports": sum(profile.values()),
            "added_source_reads": sum(e[0] == "add" and e[2].startswith("X") for e in added),
            "added_profile": {str(k): v for k, v in sorted(profile.items())},
            "added_rank_mass": sum(k*v for k, v in profile.items()),
            "complete_events": len(word["program"]) + len(added)}


def controls(word, circuit, ports):
    flat = [(p, i, e) for p, part in enumerate(circuit["insertions"]) for i, e in enumerate(part["events"])]
    tests = {
        "missing_root_fanout": next((p, i) for p, i, e in flat if e[:2] == ["add", "POOL1"]),
        "missing_secondary_fanout": next((p, i) for p, i, e in flat if e[:2] == ["add", "POOL2"]),
        "missing_dirty_compensation": next((p, i) for p, i, e in flat if e[:3] == ["add", "Y1", "POOL1"]),
        "missing_cleanup": next((p, i) for p, i, e in reversed(flat) if e[0] == "add" and e[1] == "POOL1"),
    }
    result = {}
    for name, (part, index) in tests.items():
        bad = deepcopy(circuit)
        bad["insertions"][part]["events"][index][3] = "0"
        try:
            replay(word, bad, ports)
        except ValueError as error:
            result[name] = str(error)
        else:
            raise ValueError("accepted semantic fault " + name)
    part, index = next((p, i) for p, i, e in flat if e[:2] == ["transport", "POOL1"])
    bad = deepcopy(circuit)
    bad["insertions"][part]["events"][index][4] += 1
    try:
        replay(word, bad, ports)
    except ValueError as error:
        result["wrong_paid_rank"] = str(error)
    else:
        raise ValueError("accepted wrong paid rank")
    return result


def check(circuit):
    word = load(NATIVE / "LOWRANK-WITNESS.json")
    fixture = load(NATIVE / "P104-FIXTURE.json")["section4_explicit_P104"]
    ancestor = load(HERE / "inputs/PR2504-CIRCUIT.json")
    ports = root_ports(fixture)
    need(not any(e[0] != "transport" and e[1].startswith("X") for e in word["program"]), "immutable original sources")
    need(not any(e[0] in ("add", "copy") and e[2].startswith("Y") for e in word["program"]), "original word never reads Y")
    for part in circuit["insertions"]:
        for event in part["events"]:
            if event[0] == "transport":
                need(event[1] in circuit["initial_frames"] and space(event[2]) < space(event[3]), "monotone new helper")
    replay(word, {"initial_frames": {}, "final_frames": {}, "insertions": []}, ports, False)
    replay(word, ancestor, ports)
    program, columns = replay(word, circuit, ports)
    old, new = preserved(ancestor, circuit)
    result = bill(word, circuit)
    need(result["helpers"] == 91 and result["added_rank_mass"] == 819, "declared local improvement")
    need(all(not f for f in circuit["initial_frames"].values()), "new dirty ZERO entrances")
    need(all(len(space(f)) == 512 for f in circuit["final_frames"].values()), "new FULL exits")
    result.update({"formal_columns": columns, "endpoint_coefficients": columns*columns,
                   "replaced_helpers": old, "pooled_helpers": new,
                   "ancestor_bill": bill(word, ancestor), "controls": controls(word, circuit, ports),
                   "status": "PASS_P104_POOLED_COLLECTORS", "complete_original_events": len(word["program"]),
                   "scope": "Exact finite three-target logical correction, dirty restoration and dimension-gap bill only. No native lowering, global hosting, precision, all-size supplier or new kappa."})
    need(len(program) == result["complete_events"], "complete event recount")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    circuit = load(HERE / "CIRCUIT.json")
    result = check(circuit)
    need(result == load(HERE / "RESULT.json"), "complete receipt equality")
    if args.out:
        with args.out.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
