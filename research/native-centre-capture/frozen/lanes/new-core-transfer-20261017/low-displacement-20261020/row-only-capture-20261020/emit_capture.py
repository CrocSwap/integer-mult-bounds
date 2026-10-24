#!/usr/bin/env python3
"""Emit sixteen productive centre rows at the exact full frame."""

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
PARENT = HERE.parent
LANES = PARENT.parents[1]
PINS = {
    "native": (
        PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
    "capture": (
        LANES / "controller-followthrough-20261017/row-capture-20261020/run-normal/ROW-CAPTURE.json",
        "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7",
    ),
    "helper": (
        PARENT / "emit_native.py",
        "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745",
    ),
    "cyclic": (
        LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source " + name)
    return raw


read("helper")
spec = importlib.util.spec_from_file_location("row_capture_native", PINS["helper"][0])
n = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = n
spec.loader.exec_module(n)


def price(events):
    return n.r.price([event[1] for event in events if event[0] == "scalar"])


def verify(word, code, response, captured_response, selected):
    current = list(word["start"])
    state = [{p: F(1)} for p in range(640)]
    maximum = F(1)
    height = 0
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "The exact native entry frame")
            need(len(n.basis(word["frames"][old] + word["frames"][new]))
                 == len(word["frames"][new]), "A nested native frame")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "The exact native rank")
            current[field] = new
        else:
            need(event[0] == "scalar", "The event grammar")
            gate, frame = event[1:]
            op, target, source, coefficient = gate
            coefficient = F(coefficient)
            need(current[target] == frame, "The exact scalar target frame")
            if op == "add":
                need(source != target and current[source] == frame, "The exact current source frame")
                n.r.add(state[target], state[source], coefficient)
            else:
                need(op == "scale", "Only dyadic scalar instructions")
                state[target] = {p: coefficient * value for p, value in state[target].items()}
            maximum = max(maximum, sum(abs(value) for value in state[target].values()))
            for value in state[target].values():
                denominator = value.denominator
                need(denominator & (denominator - 1) == 0, "No odd denominator")
                height = max(height, denominator.bit_length() - 1)
    expected = [{p: F(1)} for p in range(640)]
    for p in range(112):
        if p in selected:
            expected[112 + p] = {112 + j: value for j, value in code[p].items()}
            n.r.add(expected[112 + p], captured_response[p])
        else:
            n.r.add(expected[112 + p], response[p])
    need(state == expected, "All640 independent arbitrary input columns")
    need(current == word["final"], "All complete output frames")
    need(state[224:] == [{p: F(1)} for p in range(224, 640)], "All416 helpers are unchanged")
    profile = Counter(event[4] for event in word["events"] if event[0] == "native")
    return {
        "arbitrary_input_columns": 640, "unchanged_source_fields": 112,
        "unchanged_arbitrary_helper_fields": 416, "selected_full_targets": len(selected),
        "ordinary_hole_targets": 112 - len(selected), "native_profile": dict(sorted(profile.items())),
        "native_children": sum(profile.values()), "native_mass": sum(k * v for k, v in profile.items()),
        "native_side_map_upper_bound": 2 * sum(profile.values()),
        "explicit_input_monomial_views": len(word["input_views"]),
        "explicit_output_monomial_views": len(word["output_views"]),
        "real_scalar_primitives": price(word["events"]),
        "scalar_stage_prices": {stage: price(word["events"][start:stop])
                               for stage, (start, stop) in word["stage_ranges"].items()},
        "maximum_content_prefix_row_one_norm": str(maximum),
        "additional_content_binary_height": height,
        "owned_fields": 0, "private_fields": 0, "fixed_odd_scans": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("native"))
    capture = json.loads(read("capture"))
    cyclic = json.loads(read("cyclic"))
    selected_list = capture["pivots"]
    selected = set(selected_list)
    need(selected_list == [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23],
         "The fixed physical pivot set")
    code, inverse_code = n.rows(capture["code"]), n.rows(capture["code_inverse"])
    response, captured = n.rows(capture["response"]), n.rows(capture["selected_capture_response"])
    need(response == n.rows(source["model"]["response"]), "The exact native response")
    need(n.r.product(code, response) == captured, "The ordered captured response C E")
    need(n.r.product(code, inverse_code) == n.r.product(inverse_code, code) == n.r.identity(112),
         "Both row-code inverse orders")
    for p in range(112):
        if p in selected:
            need(code[p].get(p) == 1 and set(code[p]) & selected == {p}, "Normalized row shear")
            multiplier = F(-5 if selected_list.index(p) < 8 else -7)
            need(captured[p] == {j: multiplier * value for j, value in code[p].items()},
                 "The actual centre left eigenvector")
        else:
            need(code[p] == {p: F(1)} and captured[p] == response[p], "The ordinary rows stay unchanged")
    for pair in cyclic["pair_codes"]:
        ports = set(pair["ports"])
        need(not ports & selected or ports <= selected, "No selected physical pair is split")
    fresh_phases = 0
    words, reports, removals = {}, {}, {}
    for provider, directions in source["providers"].items():
        original = directions["forward"]
        frames = original["frames"]
        need(frames[0] == [] and len(frames[1]) == 9, "The exact I and FULL frames")
        full = n.compiler.canonical_frame(9, tuple(frames[1]))
        full_recipe, _ = n.compiler.lower_child(full)
        need(full_recipe["rank"] == 9, "An explicit full rank-nine child")
        n.phase.equal(n.phase.recipe(full_recipe), n.phase.frame(frames[1], 9),
                      "Exact new full-frame child " + provider)
        n.phase.equal(n.phase.frame(frames[1], 9), n.phase.fourier(9),
                      "The selected FULL exit has the exact F9 phase " + provider)
        fresh_phases += 2
        selected_fields = {112 + p for p in selected}
        kept, deleted, retained_indices = [], [], []
        for index, event in enumerate(original["events"]):
            target = event[1] if event[0] == "native" else event[1][1]
            if target in selected_fields:
                deleted.append(event)
            else:
                if event[0] == "scalar" and event[1][0] == "add":
                    need(event[1][2] not in selected_fields, "No retained read of a selected target")
                kept.append(event)
                retained_indices.append(index)
        pre = []
        for op, target, source_index, coefficient in capture["scalar_word"]:
            need(target in selected and (op != "add" or source_index not in selected),
                 "The precode uses only current ordinary Y sources")
            pre.append(["scalar", [op, 112 + target, None if source_index is None
                                   else 112 + source_index, coefficient], 0])
        events = pre + deepcopy(kept)
        ranges = {"precode": [0, len(pre)], "retained_core": [len(pre), len(events)]}
        current = list(original["start"])
        for event in kept:
            if event[0] == "native":
                need(current[event[1]] == event[2], "The retained frame path is continuous")
                current[event[1]] = event[3]
        need(all(current[p] == 1 for p in range(112)), "All112 sources are FULL at the query cut")
        need(all(current[112 + p] == 0 for p in selected), "The selected target baselines remain in I")
        start_full = len(events)
        for p in selected_list:
            events.append(["native", 112 + p, 0, 1, 9, "capture-full"])
        ranges["selected_full_progress"] = [start_full, len(events)]
        start_query = len(events)
        for op, target, source_index, coefficient in capture["final_query_word"]:
            need(op in ("add", "scale") and target in selected, "The fully dyadic final query")
            if op == "add":
                need(112 <= source_index < 224, "The final query reads a completed X source")
            events.append(["scalar", [op, 112 + target, None if source_index is None
                                      else source_index - 112, coefficient], 1])
        ranges["late_query"] = [start_query, len(events)]
        used = {event[5] for event in kept if event[0] == "native"}
        recipes = {key: original["native_recipes"][key] for key in sorted(used)}
        recipes["capture-full"] = full_recipe
        input_views, output_views = [], []
        for record in original["endpoint_adapters"]:
            p = record["port"]
            if record["role"] == "source":
                need(record["frame"] == original["start"][p] and record["rank"] == 0,
                     "The pinned physical input adapter")
                input_views.append(record)
            elif p not in selected:
                conventional = n.compiler.cgate(9, source["model"]["ports"][p], -1).then(
                    n.compiler.fourier(9))
                canonical = n.compiler.canonical_frame(9, tuple(frames[record["frame"]]))
                operation = canonical.adjoint().then(conventional)
                recipe, _ = n.compiler.lower_child(operation)
                need(recipe["rank"] == 0, "An explicit ordinary physical output view")
                circuit = n.phase.adjoint(n.phase.frame(frames[record["frame"]], 9)) \
                    + (("C", source["model"]["ports"][p], -1),) + n.phase.fourier(9)
                n.phase.equal(n.phase.recipe(recipe), circuit, "Exact ordinary output view")
                fresh_phases += 1
                output_views.append({"port": p, "frame": record["frame"], "recipe": recipe,
                                     "circuit": circuit})
        final = list(original["final"])
        for p in selected:
            final[112 + p] = 1
        word = {"start": original["start"], "final": final, "frames": frames, "events": events,
                "native_recipes": recipes, "input_views": input_views, "output_views": output_views,
                "stage_ranges": ranges, "retained_original_event_indices": retained_indices,
                "new_full_recipe_circuit": n.phase.frame(frames[1], 9)}
        report = verify(word, code, response, captured, selected)
        need(report["native_profile"] == {1: 1392, 2: 64, 3: 48, 9: 16}, "The full native invoice")
        need(report["scalar_stage_prices"] == {"precode": 1760, "retained_core": 6456,
                                              "selected_full_progress": 0, "late_query": 3424},
             "The full literal scalar invoice")
        need(report["real_scalar_primitives"] == 11640 and report["native_mass"] == 1808,
             "The complete local prices")
        need(len(input_views) == 112 and len(output_views) == 96, "All actual boundary views")
        words[provider], reports[provider] = word, report
        removals[provider] = {"events": len(deleted), "native_profile": dict(Counter(
            event[4] for event in deleted if event[0] == "native")),
            "scalar_primitives": price(deleted), "no_retained_selected_target_read": True}
        for stage in ("precode", "late_query"):
            bad = deepcopy(word)
            index = next(i for i in range(*ranges[stage]) if bad["events"][i][0] == "scalar"
                         and bad["events"][i][1][0] == "add")
            del bad["events"][index]
            try:
                verify(bad, code, response, captured, selected)
            except ValueError:
                pass
            else:
                raise ValueError("An omitted " + stage + " term was accepted")
    payload = {
        "schema": "productive-sixteen-full-capture-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin} for name, (path, pin) in PINS.items()},
        "ports": source["model"]["ports"], "selected_ports": selected_list,
        "ordinary_ports": sorted(set(range(112)) - selected), "code": capture["code"],
        "inverse_code": capture["code_inverse"], "response": capture["response"],
        "captured_response": capture["selected_capture_response"], "providers": words,
        "physical_contract": {
            "input": "X_p=Q_p x_p; Y_p=y_p; all416 helpers arbitrary",
            "source_output": "X_p=F9 x_p for all112 ports",
            "ordinary_target_output": "Y_p=F9 q_p (y+E x)_p for p outside P",
            "selected_target_output": "Y_p=F9 [C(y+E x)]_p for p in P",
            "helpers": "All416 unchanged; no owned or private field",
        },
    }
    data = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(data)
    for provider, word in saved["providers"].items():
        need(verify(word, code, response, captured, selected) == reports[provider],
             "The complete serialized replay")
    (args.out / "PRODUCTIVE-CAPTURE.json.gz").write_bytes(gzip.compress(data, mtime=0))
    receipt = {
        "status": "PASS_COMPLETE_PRODUCTIVE_FULL_CAPTURE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(data).hexdigest(),
        "source_pins": payload["source_pins"], "reports": reports, "removed_events": removals,
        "fresh_phase_checks": fresh_phases, "negative_controls": ["omitted precode ADD", "omitted late-query ADD"],
        "scope": "Complete local arbitrary-baseline capture with exact changed output phases. No next-stage I-frame claim, recursive hosting or final supplier improvement.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
