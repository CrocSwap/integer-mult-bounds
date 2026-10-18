#!/usr/bin/env python3
"""Separate dense quarter-integer/echelon audit. Imports no producer or checker."""
from collections import Counter
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


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    require(len(raw) <= 3_000_000, "bounded input")
    if path in PINS:
        require(sha256(raw).hexdigest() == PINS[path], "independent source pin")
    return json.loads(raw)


def echelon(frame):
    require(len(frame) <= 9 and all(type(v) is int and 0 < v < 512 for v in frame), "binary basis")
    rows = list(frame)
    used = 0
    for bit in range(8, -1, -1):
        pivot = next((i for i in range(used, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[used], rows[pivot] = rows[pivot], rows[used]
        for i in range(len(rows)):
            if i != used and (rows[i] >> bit) & 1:
                rows[i] ^= rows[used]
        used += 1
    require(used == len(frame), "basis independence")
    return tuple(rows)


def contained(left, right):
    for vector in left:
        for pivot in right:
            if vector ^ pivot < vector:
                vector ^= pivot
        if vector:
            return False
    return True


def roots(fixture):
    # Start with all 240 signed roots, then select the first-nonzero-positive lines.
    signed = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0]*8
            row[i], row[j] = a, b
            signed.append(tuple(row))
    signed += [s for s in product((-1, 1), repeat=8) if s.count(-1) % 2 == 0]
    require(len(signed) == 240, "240 signed roots")
    lines = sorted(r for r in signed if next(x for x in r if x) > 0)
    removed = set(map(tuple, fixture["F0"] + fixture["C"]))
    ports = [r for r in lines if r not in removed]
    require(len(ports) == 104, "104 independent ports")
    return ports


def scalar(value):
    parts = str(value).split("/")
    require(len(parts) <= 2 and len(str(value)) <= 16, "bounded scalar")
    return int(parts[0]), int(parts[1]) if len(parts) == 2 else 1


def execute(event, rows, frames, columns):
    op, register = event[:2]
    if op == "transport":
        old, new = echelon(event[2]), echelon(event[3])
        require(frames[register] == old, "independent transport entry")
        require(old != new and (contained(old, new) or contained(new, old)), "independent nesting")
        require(event[4] == abs(len(old)-len(new)), "independent rank")
        frames[register] = new
    elif op == "zero":
        require(register == "C" and register not in rows, "independent private allocation")
        rows[register], frames[register] = [0]*columns, echelon(event[2])
    elif op == "erase":
        require(register == "C" and frames[register] == echelon(event[2]), "independent private discard")
        del rows[register], frames[register]
    else:
        require(op in ("add", "copy"), "independent event type")
        source = event[2]
        require(register != source and frames[register] == frames[source] == echelon(event[-1]), "independent common chart")
        if op == "copy":
            require(not any(rows[register]), "independent private zero")
            rows[register] = rows[source].copy()
            return
        numerator, denominator = scalar(event[3])
        for i in range(columns):
            product_value = numerator*rows[source][i]
            require(product_value % denominator == 0, "exact quarter-integer arithmetic")
            rows[register][i] += product_value // denominator


def audit(circuit, word, ports):
    initial = dict(word["initial_frames"])
    require(not set(initial) & set(circuit["initial_frames"]), "independent disjoint helpers")
    initial.update(circuit["initial_frames"])
    names = list(initial)
    columns = len(names)
    require(columns <= 400, "bounded dense columns")
    indices = {name: i for i, name in enumerate(names)}
    rows = {name: [4*int(i == indices[name]) for i in range(columns)] for name in names}
    frames = {name: echelon(frame) for name, frame in initial.items()}
    insertions = {part["completed_cut"]: part["events"] for part in circuit["insertions"]}
    require(len(insertions) == len(circuit["insertions"]) <= 20, "independent unique cuts")
    require(sum(map(len, insertions.values())) <= 1500, "bounded added events")
    for cut in range(len(word["program"]) + 1):
        for event in insertions.get(cut, []):
            execute(event, rows, frames, columns)
        if cut < len(word["program"]):
            execute(word["program"][cut], rows, frames, columns)
    final = dict(word["final_frames"])
    final.update(circuit["final_frames"])
    require(set(rows) == set(names) == set(frames) == set(final), "independent closed lifetimes")
    for name in names:
        expected = [4*int(i == indices[name]) for i in range(columns)]
        if name.startswith("Y"):
            target = int(name[1:])
            if target < 3:
                expected[indices[f"X{target}"]] = 4
            else:
                for source in range(104):
                    dot = sum(ports[target][j]*ports[source][j] for j in range(8))
                    require(dot % 2 == 0, "independent Gram denominator")
                    expected[indices[f"X{source}"]] = dot // 2
        require(rows[name] == expected, "independent endpoint " + name)
        require(frames[name] == echelon(final[name]), "independent final chart " + name)
    return columns*columns


def main():
    word = read(NATIVE / "LOWRANK-WITNESS.json")
    fixture = read(NATIVE / "P104-FIXTURE.json")["section4_explicit_P104"]
    ancestor = read(HERE / "inputs/PR2504-CIRCUIT.json")
    candidate = read(HERE / "CIRCUIT.json")
    ports = roots(fixture)
    old_columns = audit(ancestor, word, ports)
    columns = audit(candidate, word, ports)
    profiles = []
    for circuit in (ancestor, candidate):
        profiles.append(Counter(e[4] for part in circuit["insertions"] for e in part["events"] if e[0] == "transport"))
    require(profiles[0] - profiles[1] == Counter({1: 1, 2: 1, 6: 1}) and not profiles[1]-profiles[0], "exact profile deletion")
    require(columns == 137641 and old_columns == 138384, "complete coefficient counts")
    # Separate semantic faults run through this dense interpreter, not a receipt comparison.
    for helper in ("POOL1", "POOL2"):
        faulty = json.loads(json.dumps(candidate))
        changed = False
        for part in faulty["insertions"]:
            for event in part["events"]:
                if not changed and event[:2] == ["add", helper]:
                    event[3], changed = "0", True
        require(changed, "fault site")
        try:
            audit(faulty, word, ports)
        except ValueError as error:
            require("independent endpoint" in str(error), "semantic endpoint rejection")
        else:
            raise ValueError("accepted independent fanout fault")
    print("PASS_P104_POOLED_INDEPENDENT columns=371 coefficients=137641 removed=H1+H2+H6 controls=2 no_new_kappa")


if __name__ == "__main__":
    main()
