#!/usr/bin/env python3
"""Exact, read-only scalar audit of one F0 cancellation fault.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable code is imported. Native cut semantics are unverified.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAULT = 24438  # zero-based in the expanded, unfiltered F_0 word
WIDTH = 712


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load(root):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"],
                 "source changed: " + item["path"])
    raw = (root / "research/joint-query/certificate.json.gz").read_bytes()
    need(len(raw) < 1024 * 1024, "compressed input cap")
    payload = gzip.decompress(raw)  # authenticated before decompression
    need(len(payload) < 16 * 1024 * 1024, "payload cap")
    return json.loads(payload)


def reg(token):
    need(isinstance(token, list) and len(token) == 2, "register token")
    kind, index = token
    need(type(index) is int and kind in ("L", "C"), "register kind")
    need(0 <= index < (704 if kind == "L" else 8), "register range")
    return index + (704 if kind == "C" else 0)


def expand(packet):
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "schema")
    word = []
    for event in packet["programs"]["F_0"]:
        op = event[0]
        if op == "retained_core":
            need(event[1:3] == ["forward", 0], "F0 core")
            word.extend(packet["core_words"]["forward"])
        elif op in ("cover_sweep", "private_sweep"):
            word.extend(event[2])
        else:
            word.append(event)
    need(len(word) == 26099, "expanded event count")
    need(Counter(event[0] for event in word) == {
        "scalar": 21025, "climb": 3486, "adapter": 1090,
        "residual_adapter": 480, "phase": 10, "native_line": 8},
        "F0 inventory; no cover map is specialized away")
    need(word[FAULT] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1],
         "fault event binding")
    tail = packet["core_words"]["forward"][FAULT + 1:]
    need(Counter(event[0] for event in tail) == {
        "scalar": 475, "residual_adapter": 240, "phase": 1}, "core suffix inventory")
    need(all(event[2] == 1 for event in tail if event[0] == "scalar"),
         "all remaining core scalar events have frame label 1")
    need(all(224 <= event[2] < 704 for event in tail if event[0] == "residual_adapter"),
         "remaining residual adapters act only on helpers")
    return word


def apply(state, gate):
    op, dst = gate[0], reg(gate[1])
    if op == "add":
        src = reg(gate[2])
        need(src != dst and len(gate) == 5, "ADD operands")
        state[dst] += Q(gate[3], gate[4]) * state[src]
    elif op == "scale":
        need(len(gate) == 4, "SCALE operands")
        state[dst] *= Q(gate[2], gate[3])
    elif op == "clear":
        need(dst >= 704 and len(gate) == 2, "only owned private CLEAR")
        state[dst] = Q(0)
    else:
        raise ValueError("unknown scalar operation")


def run(word, initial, injection=None, stop=None):
    need(len(initial) == WIDTH, "state width")
    state = list(initial)
    for index, event in enumerate(word):
        if index == stop:
            return state
        # Deliberate common-chart scalar projection, not physical child replay.
        if event[0] == "scalar":
            apply(state, event[1])
        if injection is not None and index == injection[0]:
            need(event[0] == "scalar" and event[1][0] == "add", "inject after ADD")
            state[reg(event[1][1])] += injection[1]
    return state


def unit(index):
    value = [Q(0)] * WIDTH
    value[index] = Q(1)
    return value


def sparse(state):
    return [[index, str(value)] for index, value in enumerate(state) if value]


def audit(word):
    dirty = unit(359)
    prefix = run(word, dirty, stop=FAULT)
    need((prefix[39], prefix[359]) == (Q(-4), Q(1)), "dirty cut coefficients")
    need(run(word, dirty) == dirty, "exact dirty restoration, no data leak")
    data = unit(112)  # original-data max norm exactly one
    need(run(word, data) == data, "Y0 positive fixture")
    data_cut = run(word, data, stop=FAULT)
    need(data_cut[39] == data_cut[359] == 0, "data contribution at cut")
    response = run(word[FAULT + 1:], unit(39))
    data_response = response[:224]
    need(sum(bool(value) for value in data_response) == 52, "52 affected fields")
    need({abs(value) for value in data_response if value} == {Q(1, 2)}, "response size")
    need(not any(response[224:]), "fault leaves all helper/private outputs exact")
    need(response[2] == Q(-1, 2), "X2 attaining coordinate")
    cases = []
    for exponent in (0, 8, 64, 256):
        magnitude, u = Q(2**exponent), Q(1, 2**80)
        initial = list(data)
        initial[359] = magnitude
        cut = run(word, initial, stop=FAULT)
        allowance = u * (abs(cut[39]) + 4 * abs(cut[359]))
        need(allowance == 8 * u * magnitude, "local relative defect allowance")
        ideal = run(word, initial)
        need(ideal == initial, "exact producer on witness family")
        faulty = run(word, initial, (FAULT, allowance))
        difference = [a - b for a, b in zip(faulty, ideal)]
        need(difference == [allowance * value for value in response], "linear response")
        need(faulty[224:] == initial[224:], "exact restoration with fault")
        need(max(abs(value) for value in difference[:224]) == 4 * u * magnitude,
             "completed data defect")
        absolute = run(word, initial, (FAULT, Q(1, 256)))
        need(max(abs(a - b) for a, b in zip(absolute[:224], ideal[:224])) == Q(1, 512),
             "absolute-error control independent of dirty magnitude")
        cases.append({"dirty_power_of_two": exponent, "u": str(u),
                      "local_defect": str(allowance),
                      "completed_data_defect": str(4 * u * magnitude)})
    need(run(word, data, (FAULT, Q(0))) == data, "zero-dirty control")
    earlier = run(word[24434 + 1:], unit(103))
    need(sum(bool(value) for value in earlier[224:704]) == 102,
         "earlier-fault restoration control")
    scalars = [event[1] for event in word if event[0] == "scalar"]
    return {"schema_version": 1, "scope": "common-chart F0 scalar projection",
            "expanded_events": len(word), "scalar_macros": len(scalars),
            "scalar_projection_sha256": hashlib.sha256(canonical(scalars)).hexdigest(),
            "fault_index_zero_based": FAULT, "fault_event": word[FAULT],
            "dirty_input": 359, "data_input": 112,
            "prefix_dirty_target_coefficient": str(prefix[39]),
            "prefix_dirty_source_coefficient": str(prefix[359]),
            "unit_fault_final_response": sparse(response),
            "all_480_helpers_exact_after_fault": True,
            "all_8_private_outputs_zero_after_fault": True,
            "completed_defect_formula": "4*u*T", "cases": cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true", help="create absent RESULT.json")
    args = parser.parse_args()
    result = audit(expand(load(args.root.resolve())))
    output = HERE / "RESULT.json"
    if args.write:
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(json.loads(output.read_text(encoding="utf-8"))) == canonical(result),
             "result receipt changed")
    print("PASS_QQ16_PRODUCER_DIRTY_FAULT")
    print("F0 scalar projection: 4*u*T data error from one ADD fault; helpers restore.")


if __name__ == "__main__":
    main()
