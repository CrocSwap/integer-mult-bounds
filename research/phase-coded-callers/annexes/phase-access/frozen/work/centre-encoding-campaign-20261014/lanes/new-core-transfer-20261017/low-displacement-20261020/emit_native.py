#!/usr/bin/env python3
"""Emit and check the native rank-thirty response on the actual ports."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        ("plain", "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"),
    "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json":
        ("plain", "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c"),
    "new-core-transfer-20261017/low-displacement-20261020/check_response.py":
        ("plain", "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8"),
    "new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz":
        ("decompressed", "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"),
    "new-native-recipes-20261017/sources/vendor/clifford/clifford_exact.py":
        ("plain", "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"),
    "interface-proof/verify_native_lift.py":
        ("plain", "087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(relative):
    mode, pin = PINS[relative]
    raw = (LANES / relative).read_bytes()
    if mode == "decompressed":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source pin " + relative)
    return raw


def load_module(name, relative):
    read(relative)
    spec = importlib.util.spec_from_file_location(name, LANES / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


r = load_module("low_response", "new-core-transfer-20261017/low-displacement-20261020/check_response.py")
compiler = load_module("low_compiler", "new-native-recipes-20261017/sources/vendor/clifford/clifford_exact.py")
phase = load_module("low_phase", "interface-proof/verify_native_lift.py")


def basis(vectors):
    rows = list(dict.fromkeys(vectors))
    count = 0
    for bit in range(8, -1, -1):
        found = next((i for i in range(count, len(rows)) if rows[i] >> bit & 1), None)
        if found is None:
            continue
        rows[count], rows[found] = rows[found], rows[count]
        for i in range(len(rows)):
            if i != count and rows[i] >> bit & 1:
                rows[i] ^= rows[count]
        count += 1
    return tuple(rows[:count])


def rows(value):
    return [{int(p): F(c) for p, c in row.items()} for row in value]


def verify_word(word, response, direction):
    current = list(word["start"])
    state = [{i: F(1)} for i in range(len(current))]
    maximum = F(1)
    scalar_word = []
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "Literal native entry frame")
            need(len(basis(word["frames"][old] + word["frames"][new])) == len(word["frames"][new]),
                 "Literal nested native edge")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "Literal native rank")
            current[field] = new
        else:
            need(event[0] == "scalar", "Literal event grammar")
            gate, frame = event[1:]
            op, target, origin, coefficient = gate
            c = F(coefficient)
            need(current[target] == frame, "Literal scalar target frame")
            if op == "scale":
                state[target] = {p: c * v for p, v in state[target].items() if c * v}
            else:
                need(op == "add" and target != origin and current[origin] == frame,
                     "Literal scalar source frame")
                r.add(state[target], state[origin], c)
            maximum = max(maximum, sum(abs(v) for v in state[target].values()))
            scalar_word.append(gate)
    expected = [{i: F(1)} for i in range(len(current))]
    for target, row in enumerate(response):
        if direction == "forward":
            r.add(expected[112 + target], row)
        else:
            for origin, coefficient in row.items():
                r.add(expected[origin], {112 + target: -coefficient})
    need(state == expected and current == word["final"], "All640 columns and final frames")
    profile = Counter(event[4] for event in word["events"] if event[0] == "native")
    return {"all_input_columns": len(current), "untouched_arbitrary_fields": len(current) - 224,
            "owned_fields": 0, "private_fields": 0, "native_profile": dict(sorted(profile.items())),
            "native_mass": sum(k * v for k, v in profile.items()), "native_children": sum(profile.values()),
            "real_scalar_primitives": r.price(scalar_word), "prefix_row_l1_bound": str(maximum),
            "native_side_map_bound": 2 * sum(profile.values()), "endpoint_maps": 224}


def make_word(cyclic, model, direction):
    frames = deepcopy(cyclic["frames"])
    indices = {tuple(frame): i for i, frame in enumerate(frames)}
    small = set(model["small_ports"])
    current = list(cyclic["start"])
    events = []
    mode = rows(model["mode_response"])
    by_parameter = {record["id"]: record for record in cyclic["parameters"]}
    transfer_records = []
    for event in cyclic["programs"][direction]:
        kind = event[0]
        if kind == "native":
            _, field, old, new, rank = event
            if field % 112 in small:
                need(field < 224, "Only data fields receive native progress")
                continue
            need(current[field] == old, "Pinned cyclic native frame")
            current[field] = new
            events.append(["native", field, old, new, rank, str(old) + ":" + str(new)])
        elif kind == "parameter_add":
            _, target, origin, parameter, sign, frame = event
            record = by_parameter[parameter]
            carriers = cyclic["cyclic_carriers"][record["vertex"]]
            c = sign * mode[carriers[record["row"]]].get(carriers[record["column"]], F(0))
            if c:
                transfer_records.append({"part": "large48", "event": len(events),
                                         "coefficient": str(c), "parameter": parameter})
                events.append(["scalar", ["add", target, origin, str(c)], frame])
        else:
            need(kind in ("add", "scale"), "Pinned cyclic scalar grammar")
            _, target, origin, coefficient, frame = event
            events.append(["scalar", [kind, target, origin, coefficient], frame])

    def frame(vectors):
        vectors = basis(vectors)
        if vectors not in indices:
            indices[vectors] = len(frames)
            frames.append(list(vectors))
        return indices[vectors]

    def native(field, new):
        old = current[field]
        if old == new:
            return
        need(len(basis(frames[old] + frames[new])) == len(frames[new]), "Clique nested edge")
        events.append(["native", field, old, new, len(frames[new]) - len(frames[old]),
                       str(old) + ":" + str(new)])
        current[field] = new

    q = cyclic["ports"]
    for group in model["small_cliques"]:
        k = len(group)
        for depth in range(1, k):
            for i, p in enumerate(group):
                native(p, frame(q[group[(i + j) % k]] for j in range(depth)))
                native(112 + p, frame(q[group[(i - j) % k]] for j in range(1, depth + 1)))
            for i, p in enumerate(group):
                target_port = group[(i + depth) % k]
                need(current[p] == current[112 + target_port], "Every clique transfer has equal frames")
                target, origin, coefficient = ((112 + target_port, p, "-1") if direction == "forward"
                                               else (p, 112 + target_port, "1"))
                transfer_records.append({"part": "small64", "event": len(events),
                                         "source_port": p, "target_port": target_port,
                                         "coefficient": coefficient})
                events.append(["scalar", ["add", target, origin, coefficient], current[p]])
        for p in group:
            native(p, cyclic["final"][p])
            native(112 + p, cyclic["final"][112 + p])
    need(current == cyclic["final"], "Full native frame completion")
    return {"frames": frames, "start": cyclic["start"], "final": cyclic["final"],
            "events": events, "transfer_records": transfer_records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cyclic = json.loads(read("independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"))
    model = json.loads(read("new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json"))
    core = json.loads(read("new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"))
    for provider, data in core["providers"].items():
        need(data["canonical"]["ports"] == cyclic["ports"], "Pinned provider directions " + provider)
        need(len(data["canonical"]["start"]) == 632, "Pinned live-field count " + provider)
    words = {direction: make_word(cyclic, model, direction) for direction in ("forward", "backward")}
    need(words["forward"]["frames"] == words["backward"]["frames"], "Both directions use the same actual frames")
    frames = words["forward"]["frames"]
    edge_pairs = sorted({(event[2], event[3]) for word in words.values()
                         for event in word["events"] if event[0] == "native"})
    recipes = {}
    for i, (old, new) in enumerate(edge_pairs):
        operation = compiler.canonical_frame(9, tuple(frames[old])).adjoint().then(
            compiler.canonical_frame(9, tuple(frames[new])))
        record, _ = compiler.lower_child(operation)
        need(record["rank"] == len(frames[new]) - len(frames[old]), "Fresh native rank")
        phase.equal(phase.recipe(record), phase.adjoint(phase.frame(frames[old], 9))
                    + phase.frame(frames[new], 9), "Fresh native phase " + str((old, new)))
        recipes[str(old) + ":" + str(new)] = record
        if (i + 1) % 100 == 0:
            print("Native phases", i + 1, "/", len(edge_pairs), flush=True)
    endpoints = []
    for p, q in enumerate(cyclic["ports"]):
        for role in ("source", "target"):
            conventional = (compiler.cgate(9, q) if role == "source"
                            else compiler.cgate(9, q, -1).then(compiler.fourier(9)))
            circuit = (("C", q, 1),) if role == "source" else (("C", q, -1),) + phase.fourier(9)
            frame = cyclic["start"][p] if role == "source" else cyclic["final"][112 + p]
            operation = conventional.adjoint().then(compiler.canonical_frame(9, tuple(frames[frame])))
            record, _ = compiler.lower_child(operation)
            need(record["rank"] == 0, "Endpoint adapter is monomial")
            phase.equal(phase.recipe(record), phase.adjoint(circuit) + phase.frame(frames[frame], 9),
                        "Fresh conventional endpoint " + str((role, p)))
            endpoints.append({"port": p, "role": role, "frame": frame, **record})
    reports = {}
    for direction, word in words.items():
        word["native_recipes"] = recipes
        word["endpoint_adapters"] = endpoints
        reports[direction] = verify_word(word, rows(model["response"]), direction)
    need(reports["forward"]["native_profile"] == {1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9},
         "Complete profile")
    need(reports["forward"]["native_mass"] == 1792 and reports["forward"]["real_scalar_primitives"] == 5288,
         "Complete local invoice")
    # Deletion of one nonzero transfer must change the complete content map.
    bad = deepcopy(words["forward"])
    del bad["events"][bad["transfer_records"][0]["event"]]
    try:
        verify_word(bad, rows(model["response"]), "forward")
    except ValueError:
        pass
    else:
        raise ValueError("The missing transfer control was accepted")
    payload = {"schema": "low-displacement-native-v1", "source_pins": PINS,
               "response": model["response"], "common_frame_words": model["common_frame_words"],
               "selected_ports": model["selected_ports"], "small_cliques": model["small_cliques"],
               "providers": {provider: words for provider in core["providers"]}}
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, directions in saved["providers"].items():
        for direction, word in directions.items():
            need(verify_word(word, rows(saved["response"]), direction) == reports[direction],
                 "Serialized provider replay " + provider + " " + direction)
    (args.out / "NATIVE-PROGRAM.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_LOW_DISPLACEMENT_NATIVE", "source_pins": PINS,
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(),
               "fresh_native_phase_checks": len(recipes), "fresh_endpoint_phase_checks": len(endpoints),
               "reports": reports, "same_geometry_both_providers_checked": True,
               "negative_control": "one nonzero transfer omitted and rejected",
               "scope": "Complete local data shears and exact phases. Helpers are unchanged; their progress, recursive hosting, routed codes and terminal remain open."}
    (args.out / "NATIVE-CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
