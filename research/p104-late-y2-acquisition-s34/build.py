#!/usr/bin/env python3
"""Replace one PR2460 correction group by source-acquisition paths.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged six groups are ywz65's PR2460 construction, following Ross
Richardson / PR2445 and the credited P104 channel lineage. No checker imports
this producer.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / "p104-native-channel" / "inputs"
PINS = {
    "word": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "ancestor": "ce1b033ae8b826eec87d70246a13a6034e177ef4863bf7f7c24631c79e5202c9",
}
# The two interior cuts count completed ORIGINAL events, not new insertions.
SHARED_ROUTE = [(6, 0), (1, 669), (0, 842)]


def read(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError("source pin: " + str(path))
    return json.loads(raw)


def span(basis):
    values = {0}
    for v in basis:
        values |= {x ^ v for x in tuple(values)}
    return values


def frame_at(word, source, cut):
    name = f"X{source}"
    result = word["initial_frames"][name]
    for event in word["program"][:cut]:
        if event[:2] == ["transport", name]:
            result = event[3]
    return result


def build(mode="late"):
    word = read(NATIVE / "LOWRANK-WITNESS.json", PINS["word"])
    ancestor = read(HERE / "inputs" / "PR2460-CIRCUIT.json", PINS["ancestor"])
    exclusive = next(g for g in ancestor["groups"] if g["targets"] == [2])
    sources = exclusive["sources"]
    removed = {f"N{s}" for s in sources}
    coefficients = {}
    for insertion in ancestor["insertions"]:
        if insertion["completed_cut"] == 0:
            for event in insertion["events"]:
                if event[0] == "add" and event[1] in removed and event[2].startswith("X"):
                    coefficients[int(event[2][1:])] = Fraction(event[3])
    if set(coefficients) != set(sources):
        raise ValueError("ancestor capture coverage")
    if mode == "late":
        routes = [SHARED_ROUTE] + [[(s, 0)] for s in sources if s not in (6, 1, 0)]
    elif mode == "initial-line":
        routes = [[(s, 0)] for s in sources]
    else:
        raise ValueError("unknown mode")

    circuit = deepcopy(ancestor)
    circuit["groups"] = [g for g in circuit["groups"] if g["targets"] != [2]]
    circuit["initial_frames"] = {r: f for r, f in circuit["initial_frames"].items() if r not in removed}
    circuit["final_frames"] = {r: f for r, f in circuit["final_frames"].items() if r not in removed}
    inserted = defaultdict(list)
    for insertion in ancestor["insertions"]:
        for event in insertion["events"]:
            # Every omitted operation belongs solely to the exclusive group.
            touches = event[1] in removed or (event[0] == "add" and event[2] in removed)
            if not touches:
                inserted[insertion["completed_cut"]].append(event)

    full = [1 << j for j in range(9)]
    endpoint = word["final_frames"]["Y2"]
    route_records = []
    for number, route in enumerate(routes):
        helper = f"LATE{number}"
        circuit["initial_frames"][helper] = []
        circuit["final_frames"][helper] = full
        # Cancel arbitrary initial dirt while Y2 and the new helper are ZERO.
        inserted[0].append(["add", "Y2", helper, "-1", []])
        current = []
        captures = []
        for source, cut in route:
            frame = frame_at(word, source, cut)
            if not span(current) <= span(frame) <= span(endpoint):
                raise ValueError("invalid acquisition path")
            if span(current) != span(frame):
                inserted[cut].append(["transport", helper, current, frame, len(frame)-len(current)])
            inserted[cut].append(["add", helper, f"X{source}", str(coefficients[source]), frame])
            captures.append({"source": source, "cut": cut, "frame": frame,
                             "coefficient": str(coefficients[source])})
            current = frame
        tail = inserted[len(word["program"])]
        if span(current) != span(endpoint):
            tail.append(["transport", helper, current, endpoint, len(endpoint)-len(current)])
        tail.extend([
            ["add", "Y2", helper, "1", endpoint],
            ["transport", helper, endpoint, full, 1],
        ])
        for source, _ in route:
            tail.append(["add", helper, f"X{source}", str(-coefficients[source]), full])
        route_records.append({"helper": helper, "captures": captures})
    circuit["late_acquisition"] = {"target": 2, "sources": sources, "mode": mode,
                                   "routes": route_records}
    circuit["insertions"] = [{"completed_cut": cut, "events": events}
                              for cut, events in sorted(inserted.items())]
    return circuit


def render(value, level=0):
    """Keep each literal event on one line for review."""
    indent = "  " * (level + 1)
    if isinstance(value, dict):
        return "{\n" + ",\n".join(indent + json.dumps(k) + ": " + render(v, level+1)
                                  for k, v in value.items()) + "\n" + "  "*level + "}"
    if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
        return "[\n" + ",\n".join(indent + render(v, level+1) for v in value) + "\n" + "  "*level + "]"
    return json.dumps(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new output file; never overwrite")
    parser.add_argument("--mode", choices=("late", "initial-line"), default="late")
    args = parser.parse_args()
    result = build(args.mode)
    with args.out.open("x", encoding="utf-8", newline="\n") as output:
        output.write(render(result) + "\n")


if __name__ == "__main__":
    main()
