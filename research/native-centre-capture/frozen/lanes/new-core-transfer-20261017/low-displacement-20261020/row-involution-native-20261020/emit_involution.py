#!/usr/bin/env python3
"""Emit both native orientations of the sixteen-row involution."""

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
    "helper": (
        PARENT / "row-only-capture-20261020/emit_capture.py",
        "1557c9f38b1d89f6d38e920d8db604607519a99cf37366b4c15414aed489cf1f",
    ),
    "native": (
        PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
    "involution": (
        LANES / "controller-followthrough-20261017/row-involution-20261020/run-normal/ROW-INVOLUTION.json",
        "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b",
    ),
    "formation": (
        PARENT / "row-only-capture-20261020/direct-normal/DIRECT-FULL-CAPTURE.json.gz",
        "fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c",
    ),
    "formation_review": (
        LANES / "new-native-recipes-20261017/row-capture-native-review-20261020/FREEZE.json",
        "488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532",
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
spec = importlib.util.spec_from_file_location("involution_native_base", PINS["helper"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
n = base.n


def verify(word, response, direction, selected):
    current = list(word["start"])
    state = [{i: F(1)} for i in range(640)]
    maximum, height = F(1), 0
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "The exact native input frame")
            need(len(n.basis(word["frames"][old] + word["frames"][new]))
                 == len(word["frames"][new]), "A nested native edge")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "The exact native rank")
            current[field] = new
        else:
            need(event[0] == "scalar", "The literal event grammar")
            gate, frame = event[1:]
            op, target, source, raw = gate
            coefficient = F(raw)
            need(current[target] == frame, "The exact scalar target frame")
            if op == "add":
                need(target != source and current[source] == frame,
                     "The exact scalar source frame")
                n.r.add(state[target], state[source], coefficient)
            else:
                need(op == "scale", "Only ADD and SCALE instructions")
                state[target] = {i: coefficient * value
                                 for i, value in state[target].items() if coefficient * value}
            maximum = max(maximum, sum(abs(value) for value in state[target].values()))
            for value in state[target].values():
                d = value.denominator
                need(d & (d - 1) == 0, "Every content coefficient is dyadic")
                height = max(height, d.bit_length() - 1)
    expected = [{i: F(1)} for i in range(640)]
    for p, row in enumerate(response):
        if direction == "forward":
            n.r.add(expected[112 + p], row)
        else:
            for j, coefficient in row.items():
                n.r.add(expected[j], {112 + p: -coefficient})
    need(state == expected, "All640 independent input columns")
    need(current == word["final"], "All640 final frames")
    need(state[224:] == [{i: F(1)} for i in range(224, 640)],
         "All416 arbitrary helpers are unchanged")
    need(all(current[p] == 1 for p in range(112)), "All X outputs are FULL")
    need(all(current[112 + p] == 1 for p in selected), "All selected Y outputs are FULL")
    profile = Counter(event[4] for event in word["events"] if event[0] == "native")
    children = sum(profile.values())
    return {
        "arbitrary_input_columns": 640, "unchanged_arbitrary_helper_fields": 416,
        "native_profile": dict(sorted(profile.items())), "native_children": children,
        "native_mass": sum(k * v for k, v in profile.items()),
        "native_side_map_upper_bound": 2 * (children - len(selected)),
        "direct_full_identity_wrapper_children": len(selected),
        "explicit_input_monomial_views": len(word["input_views"]),
        "explicit_output_monomial_views": len(word["output_views"]),
        "real_scalar_primitives": base.price(word["events"]),
        "scalar_stage_prices": {stage: base.price(word["events"][start:stop])
                               for stage, (start, stop) in word["stage_ranges"].items()},
        "maximum_content_prefix_row_one_norm": str(maximum),
        "additional_content_binary_height": height,
        "owned_fields": 0, "private_fields": 0, "fixed_odd_scans": 0,
    }


def retune(original, old_mode, mode, cyclic):
    events = deepcopy(original["events"])
    parameters = {record["id"]: record for record in cyclic["parameters"]}
    changes = []
    for record in original["transfer_records"]:
        index = record["event"]
        if record["part"] == "large48":
            parameter = parameters[record["parameter"]]
            carriers = cyclic["cyclic_carriers"][parameter["vertex"]]
            row, column = carriers[parameter["row"]], carriers[parameter["column"]]
        else:
            need(record["part"] == "small64", "The actual transfer family")
            row, column = record["target_port"], record["source_port"]
        old = old_mode[row][column]
        new = mode[row][column]
        event = events[index]
        need(event[0] == "scalar" and event[1][0] == "add", "A literal transfer slot")
        sign = F(event[1][3]) / old
        need(sign in (1, -1), "The pinned transfer orientation")
        need(new and new.denominator == 1, "The new integer transfer has the old support")
        event[1][3] = str(sign * new)
        if new != old:
            changes.append({"original_event": index, "mode_row": row, "mode_column": column,
                            "old_coefficient": str(sign * old), "new_coefficient": str(sign * new)})
    return events, changes


def backward_query(forward_word):
    word = []
    for op, target, source, coefficient in forward_word:
        if op == "add":
            word.append(["scalar", ["add", source - 112, 112 + target, str(-F(coefficient))], 1])
        else:
            need(op == "scale", "Only ADD and SCALE instructions in the pinned query")
            word.append(["scalar", ["scale", 112 + target, None, str(1 / F(coefficient))], 1])
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("native"))
    involution = json.loads(read("involution"))
    formation = json.loads(read("formation"))
    cyclic = json.loads(read("cyclic"))
    read("formation_review")
    pivots = involution["pivots"]
    selected = set(pivots)
    selected_y = {112 + p for p in selected}
    need(pivots == formation["selected_ports"], "The exact physical selected set")
    old_mode = n.rows(source["model"]["mode_response"])
    old_response = n.rows(source["model"]["response"])
    for p in source["model"]["small_ports"]:
        need(old_mode[p] == {p: F(1)}, "The source stores the small clique map separately")
        old_mode[p] = old_response[p]
    responses = {name: n.rows(involution[key]) for name, key in
                 (("A", "response"), ("AT", "response_transpose"))}
    modes = {name: n.rows(involution[key]) for name, key in
             (("A", "mode_response"), ("AT", "mode_response_transpose"))}
    need(responses["AT"] == n.r.transpose(responses["A"], 112), "The physical transpose")
    need(all(n.r.product(response, response) == n.r.identity(112)
             for response in responses.values()), "Both response involutions")
    for pair in cyclic["pair_codes"]:
        ports = set(pair["ports"])
        need(not ports & selected or ports <= selected, "The selected pair closure")
    reports, providers, ledgers = {}, {}, {}
    for provider, directions in source["providers"].items():
        providers[provider], reports[provider], ledgers[provider] = {}, {}, {}
        reference = formation["providers"][provider]
        for name, response in responses.items():
            providers[provider][name], reports[provider][name], ledgers[provider][name] = {}, {}, {}
            for direction, original in directions.items():
                events, changed_weights = retune(original, old_mode, modes[name], cyclic)
                kept, deleted, indices = [], [], []
                for index, event in enumerate(events):
                    target = event[1] if event[0] == "native" else event[1][1]
                    reads_selected = (event[0] == "scalar" and event[1][0] == "add"
                                      and event[1][2] in selected_y)
                    if target in selected_y or (direction == "backward" and reads_selected):
                        deleted.append(event)
                    else:
                        need(not reads_selected, "No retained event reads a selected Y")
                        kept.append(event)
                        indices.append(index)
                events = list(kept)
                ranges = {"retained_core": [0, len(events)]}
                current = list(original["start"])
                for event in kept:
                    if event[0] == "native":
                        need(current[event[1]] == event[2], "The retained native path")
                        current[event[1]] = event[3]
                need(all(current[p] == 1 for p in range(112)), "The completed X query cut")
                need(all(current[field] == 0 for field in selected_y), "All selected Y are still in I")
                start_full = len(events)
                for p in pivots:
                    events.append(["native", 112 + p, 0, 1, 9, "capture-full"])
                ranges["selected_full_progress"] = [start_full, len(events)]
                start_query = len(events)
                if direction == "forward":
                    for op, target, origin, coefficient in involution["final_query_words"][name]:
                        need(target in selected and (op != "add" or 112 <= origin < 224),
                             "The pinned selected-row query")
                        events.append(["scalar", [op, 112 + target,
                                                  None if origin is None else origin - 112,
                                                  coefficient], 1])
                else:
                    events.extend(backward_query(involution["final_query_words"][name]))
                ranges["late_query"] = [start_query, len(events)]
                used = {event[5] for event in kept if event[0] == "native"}
                recipes = {key: original["native_recipes"][key] for key in sorted(used)}
                for key, recipe in recipes.items():
                    need(recipe == reference["native_recipes"][key],
                         "Every retained native recipe is in the reviewed formation word")
                recipes["capture-full"] = reference["native_recipes"]["capture-full"]
                need(original["frames"] == reference["frames"]
                     and original["start"] == reference["start"], "The exact inherited frame arrays")
                final = list(original["final"])
                for p in pivots:
                    final[112 + p] = 1
                need(final == reference["final"], "The exact inherited mixed output frames")
                word = {"events": events, "frames": original["frames"],
                        "start": original["start"], "final": final, "native_recipes": recipes,
                        "input_views": reference["input_views"], "output_views": reference["output_views"],
                        "stage_ranges": ranges, "retained_original_event_indices": indices}
                report = verify(word, response, direction, selected)
                need(report["native_profile"] == {1: 1392, 2: 64, 3: 48, 9: 16}
                     and report["native_mass"] == 1808, "The complete hybrid native profile")
                need(report["explicit_input_monomial_views"] == 112
                     and report["explicit_output_monomial_views"] == 96, "Every boundary view is charged")
                for stage in ("retained_core", "late_query"):
                    bad = deepcopy(word)
                    index = next(i for i in range(*ranges[stage])
                                 if bad["events"][i][0] == "scalar"
                                 and bad["events"][i][1][0] == "add")
                    del bad["events"][index]
                    try:
                        verify(bad, response, direction, selected)
                    except ValueError:
                        pass
                    else:
                        raise ValueError("An omitted " + stage + " ADD was accepted")
                providers[provider][name][direction] = word
                reports[provider][name][direction] = report
                ledgers[provider][name][direction] = {
                    "changed_original_transfer_weights": changed_weights,
                    "removed_events": len(deleted),
                    "removed_native_profile": dict(sorted(Counter(
                        event[4] for event in deleted if event[0] == "native").items())),
                    "removed_scalar_primitives_after_retuning": base.price(deleted),
                    "no_retained_selected_Y_read": True,
                }
    payload = {
        "schema": "sixteen-row-involution-mixed-native-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin}
                        for name, (path, pin) in PINS.items()},
        "ports": source["model"]["ports"], "selected_ports": pivots,
        "responses": {name: n.r.encoded(response) for name, response in responses.items()},
        "providers": providers, "transfer_ledgers": ledgers,
        "physical_contract": {
            "input": "X=Qx; Y=y; all640 input fields are independent and arbitrary.",
            "forward": "Xout=F9x; Yout_P=F9(y+Mx)_P; Yout_U=F9q_U(y+Mx)_U.",
            "backward": "Xout=F9(x-M^T y); Yout_P=F9y_P; Yout_U=F9q_U y_U.",
            "scope": "M is A or AT. These are mixed output contracts. A^2=I does not supply a routed caller or a raw all-hole interface.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, families in saved["providers"].items():
        for name, directions in families.items():
            for direction, word in directions.items():
                need(verify(word, responses[name], direction, selected) == reports[provider][name][direction],
                     "Every serialized complete word passes")
    (args.out / "ROW-INVOLUTION-NATIVE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_EXACT_EIGHT_MIXED_ROW_INVOLUTION_WORDS",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "reports": reports, "transfer_ledgers": ledgers,
        "native_phase_scope": "All complete native operators, exact ordered frame arrays, and physical endpoint views bind byte-for-byte to the independently reviewed formation packet.",
        "negative_controls": "One omitted retained ADD and one omitted late-query ADD fail in each of eight complete words.",
        "scope": "Complete local hybrid F/B family only. Raw endpoint conversion, routed caller composition, recursive hosting, and the full supplier cost remain separate.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "payload_decompressed_sha256": sha256(raw).hexdigest(),
                      "reports": reports}, sort_keys=True))


if __name__ == "__main__":
    main()
