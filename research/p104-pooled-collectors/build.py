#!/usr/bin/env python3
"""Pool two PR2504 incidence groups. Predecessors and limits are in README.md."""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / "p104-native-channel" / "inputs"
ANCESTOR_SHA = "96459a07c79fd1b711af6343bc9c004d91e28cd0da3306c290cff657082b110d"
WORD_SHA = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"


def read_pinned(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError("source pin: " + str(path))
    return json.loads(raw)


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {value ^ vector for value in tuple(result)}
    return result


def basis(values):
    result, covered = [], {0}
    for value in sorted(values):
        if value not in covered:
            result.append(value)
            covered |= {old ^ value for old in tuple(covered)}
    return result


def pooled_word(word, ancestor):
    """Build only the changed groups, preserving the other insertions literally."""
    groups = [g for g in ancestor["groups"] if g["targets"] in ([0, 2], [0, 1, 2])]
    if len(groups) != 2:
        raise ValueError("expected two pooled predecessor groups")
    by_targets = {tuple(g["targets"]): g for g in groups}
    removed = {f"N{s}" for g in groups for s in g["sources"]}
    removed |= {r for g in groups for r in g["extra_helpers"]}
    captures = {}
    for insertion in ancestor["insertions"]:
        if insertion["completed_cut"] == 0:
            for event in insertion["events"]:
                if event[0] == "add" and event[1] in removed and event[2].startswith("X"):
                    captures[event[1]] = (event[2], Fraction(event[3]))
    if len(captures) != 22:
        raise ValueError("22 original captures required")
    frames = {r: [] for r in captures}
    frames.update({"POOL1": [], "POOL2": []})
    ends = [basis(span(word["final_frames"][f"Y{t}"])) for t in range(3)]
    j012 = basis(set.intersection(*(span(f) for f in ends)))
    j02 = basis(span(ends[0]) & span(ends[2]))
    before, gather, deliveries = [], [], []

    def move(events, register, target):
        old = frames[register]
        if span(old) != span(target):
            if not span(old) < span(target):
                raise ValueError("nonmonotone pooled transport")
            events.append(["transport", register, old, target, len(target)-len(old)])
            frames[register] = target

    def mix(dst, src, value, frame):
        event = ["add", dst, src, str(value), frame]
        before.append(event)
        gather.append(event)

    def capture_group(key, frame):
        registers = [f"N{s}" for s in by_targets[key]["sources"]]
        for register in registers:
            source, value = captures[register]
            line = word["initial_frames"][source]
            move(before, register, line)
            before.append(["add", register, source, str(value), line])
            move(before, register, frame)
        return registers

    triple = capture_group((0, 1, 2), j012)
    collector = triple[0]
    for register in triple[1:]:
        mix(collector, register, 1, j012)
    move(before, "POOL1", j012)
    mix("POOL1", collector, 1, j012)
    move(before, collector, j02)
    pair = capture_group((0, 2), j02)
    for register in pair:
        mix(collector, register, 1, j02)
    move(before, "POOL2", j02)
    mix("POOL2", collector, 1, j02)
    deliveries.extend([(1, "POOL1"), (0, collector), (2, "POOL2")])
    return finish(word, ancestor, removed, frames, before, gather, captures, deliveries, j012, j02)


def finish(word, ancestor, removed, frames, before, gather, captures, deliveries, j012, j02):
    full = [1 << i for i in range(9)]
    dirty = {r: {r: Fraction(1)} for r in frames}
    for _, dst, src, value, _ in gather:
        for name, coefficient in dirty[src].items():
            dirty[dst][name] = dirty[dst].get(name, 0) + Fraction(value)*coefficient
    compensation = [["add", f"Y{t}", name, str(-value), []]
                    for t, register in deliveries
                    for name, value in sorted(dirty[register].items()) if value]
    before = compensation + before
    after = []
    collectors = {register for _, register in deliveries}
    for register, frame in frames.items():
        if register not in collectors:
            before.append(["transport", register, frame, full, 9-len(frame)])
    for target, register in deliveries:
        frame = frames[register]
        endpoint = basis(span(word["final_frames"][f"Y{target}"]))
        after.extend([["transport", register, frame, endpoint, 8-len(frame)],
                      ["add", f"Y{target}", register, "1", endpoint],
                      ["transport", register, endpoint, full, 1]])
    after.extend(["add", dst, src, str(-Fraction(value)), full]
                 for _, dst, src, value, _ in reversed(gather))
    after.extend(["add", register, source, str(-value), full]
                 for register, (source, value) in sorted(captures.items()))
    result = deepcopy(ancestor)
    for key in ("initial_frames", "final_frames"):
        result[key] = {r: f for r, f in result[key].items() if r not in removed}
        result[key].update({r: ([] if key == "initial_frames" else full) for r in frames})
    result["groups"] = [g for g in result["groups"] if g["targets"] not in ([0, 2], [0, 1, 2])]
    for insertion in result["insertions"]:
        insertion["events"] = [e for e in insertion["events"]
                               if e[1] not in removed and not (e[0] == "add" and e[2] in removed)]
        if insertion["completed_cut"] == 0:
            insertion["events"].extend(before)
        elif insertion["completed_cut"] == len(word["program"]):
            insertion["events"].extend(after)
    result["pooled_groups"] = {"targets": [[0, 2], [0, 1, 2]],
                               "common_triple": j012, "common_pair": j02,
                               "helpers": sorted(frames), "extra_helpers": ["POOL1", "POOL2"],
                               "collectors": [[t, r] for t, r in deliveries]}
    return result


def build():
    word = read_pinned(NATIVE / "LOWRANK-WITNESS.json", WORD_SHA)
    ancestor = read_pinned(HERE / "inputs/PR2504-CIRCUIT.json", ANCESTOR_SHA)
    return pooled_word(word, ancestor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = build()
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
