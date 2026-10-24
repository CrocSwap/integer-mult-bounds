#!/usr/bin/env python3
"""Form clean centre rows by a late exchange with productive fields."""

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
SOURCE = HERE.parent / "row-only-capture-20261020"
LANES = HERE.parents[2]
PINS = {
    "helper": (SOURCE / "emit_capture.py",
               "1557c9f38b1d89f6d38e920d8db604607519a99cf37366b4c15414aed489cf1f"),
    "formation": (SOURCE / "direct-normal/DIRECT-FULL-CAPTURE.json.gz",
                  "fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c"),
    "capture": (LANES / "controller-followthrough-20261017/row-capture-20261020/run-normal/ROW-CAPTURE.json",
                "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7"),
    "phase_review": (LANES / "new-native-recipes-20261017/row-capture-native-review-20261020/FREEZE.json",
                     "488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532"),
    "line_prefix": (HERE.parent / "fixed-reader-reuse-20261020/prefix-normal/CARRIER-PREFIX.json.gz",
                    "54c561cfc49ad3fe1258ba5a8760eeadaa11784272cf458e2a6e54403a0e655e"),
    "line_phase_review": (LANES / "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
                          "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c"),
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
spec = importlib.util.spec_from_file_location("clean_exchange_base", PINS["helper"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
n = base.n


def expected_map(code, response, selected):
    result = n.r.identity(640)
    for p in range(112):
        if p in selected:
            result[p] = {112 + p: F(-1)}
            result[112 + p] = dict(code[p])
        else:
            n.r.add(result[112 + p], response[p])
    return result


def inverse_content(code, response, selected):
    x = n.r.identity(224)[:112]
    for p in selected:
        x[p] = {112 + p: F(1)}
        for j, value in code[p].items():
            if j != p:
                n.r.add(x[p], {j: -value})
    result = [dict(row) for row in x] + [{} for _ in range(112)]
    for p in range(112):
        if p in selected:
            result[112 + p] = {p: F(-1)}
        else:
            result[112 + p] = {112 + p: F(1)}
            for j, value in response[p].items():
                n.r.add(result[112 + p], x[j], -value)
    return result


def verify(word, expected):
    current = list(word["start"])
    state = n.r.identity(640)
    maximum, height = F(1), 0
    for event in word["events"]:
        if event[0] == "native":
            _, field, old, new, rank, key = event
            need(current[field] == old, "The exact native input frame")
            need(len(n.basis(word["frames"][old] + word["frames"][new]))
                 == len(word["frames"][new]), "The native frame is nested")
            need(rank == len(word["frames"][new]) - len(word["frames"][old])
                 == word["native_recipes"][key]["rank"], "The exact native rank")
            current[field] = new
        else:
            need(event[0] == "scalar", "The complete event grammar")
            gate, frame = event[1:]
            op, target, source, raw = gate
            coefficient = F(raw)
            need(current[target] == frame, "The exact scalar target frame")
            if op == "add":
                need(source != target and current[source] == frame, "The exact source frame")
                n.r.add(state[target], state[source], coefficient)
            else:
                need(op == "scale", "Only ADD and SCALE instructions")
                state[target] = {j: coefficient * value for j, value in state[target].items()
                                 if coefficient * value}
            maximum = max(maximum, sum(abs(value) for value in state[target].values()))
            for value in state[target].values():
                d = value.denominator
                need(d & (d - 1) == 0, "All content is dyadic")
                height = max(height, d.bit_length() - 1)
    need(state == expected, "All640 independent arbitrary input fields")
    need(current == word["final"], "All640 complete final frames")
    need(state[224:] == n.r.identity(640)[224:], "All416 arbitrary helpers are restored")
    profile = Counter(event[4] for event in word["events"] if event[0] == "native")
    direct_full = sum(event[0] == "native" and event[5] == "capture-full"
                      for event in word["events"])
    return {
        "all_independent_input_fields": 640, "unchanged_arbitrary_helpers": 416,
        "native_profile": dict(sorted(profile.items())), "native_children": sum(profile.values()),
        "native_mass": sum(k * v for k, v in profile.items()),
        "native_side_map_upper_bound": 2 * (sum(profile.values()) - direct_full),
        "direct_full_identity_wrapper_children": direct_full,
        "explicit_input_monomial_views": len(word["input_views"]),
        "explicit_output_monomial_views": len(word["output_views"]),
        "scalar_stage_prices": {stage: base.price(word["events"][start:end])
                               for stage, (start, end) in word["stage_ranges"].items()},
        "real_scalar_primitives": base.price(word["events"]),
        "maximum_content_prefix_row_one_norm": str(maximum),
        "additional_content_binary_height": height,
        "owned_fields": 0, "private_fields": 0, "odd_divisions": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("formation"))
    line_prefix = json.loads(read("line_prefix"))
    capture = json.loads(read("capture"))
    read("phase_review")
    read("line_phase_review")
    pivots = capture["pivots"]
    selected = set(pivots)
    code, response = n.rows(capture["code"]), n.rows(capture["response"])
    need(pivots == source["selected_ports"] and code == n.rows(source["code"])
         and response == n.rows(source["response"]), "The exact formation and row code")
    for p in selected:
        need(code[p].get(p) == 1 and set(code[p]) & selected == {p},
             "Each normalized reader has its own pivot")
    expected = expected_map(code, response, selected)
    inverse = inverse_content(code, response, selected)
    need(n.r.product(expected[:224], inverse) == n.r.product(inverse, expected[:224])
         == n.r.identity(224), "Both exact content inverse orders")
    providers, reports = {}, {}
    for provider in source["providers"]:
        providers[provider], reports[provider] = {}, {}
        for entry, original in (
                ("I", source["providers"][provider]), ("Q", line_prefix["providers"][provider])):
            word = deepcopy(original)
            core_start, core_end = original["stage_ranges"]["retained_core"]
            progress = "selected_full_progress" if entry == "I" else "selected_line_progress"
            full_start, full_end = original["stage_ranges"][progress]
            word["events"] = deepcopy(original["events"][core_start:core_end]
                                      + original["events"][full_start:full_end])
            ranges = {"retained_core": [0, core_end - core_start],
                      "selected_progress": [core_end - core_start, len(word["events"])]}
            start = len(word["events"])
            for op, target, source_index, coefficient in capture["scalar_word"]:
                word["events"].append(["scalar", [op, target, source_index, coefficient], 1])
            ranges["source_row_code"] = [start, len(word["events"])]
            start = len(word["events"])
            for p in pivots:
                word["events"].extend([
                    ["scalar", ["add", 112 + p, p, "1"], 1],
                    ["scalar", ["add", p, 112 + p, "-1"], 1],
                    ["scalar", ["add", 112 + p, p, "1"], 1],
                ])
            ranges["signed_selected_exchanges"] = [start, len(word["events"])]
            word["stage_ranges"] = ranges
            report = verify(word, expected)
            rank = 9 if entry == "I" else 8
            need(report["native_profile"] == {1: 1392, 2: 64, 3: 48, rank: 16}
                 and report["native_mass"] == 1664 + 16 * rank, "The exact complete native profile")
            need(report["scalar_stage_prices"] == {
                "retained_core": 6456, "selected_progress": 0,
                "source_row_code": 1760, "signed_selected_exchanges": 384},
                "All code and exchange costs are explicit")
            need(report["real_scalar_primitives"] == 8600, "The exact complete scalar invoice")
            for stage in ("source_row_code", "signed_selected_exchanges"):
                bad = deepcopy(word)
                index = next(i for i in range(*ranges[stage]) if bad["events"][i][1][0] == "add")
                del bad["events"][index]
                try:
                    verify(bad, expected)
                except ValueError:
                    pass
                else:
                    raise ValueError("An omitted " + stage + " ADD was accepted")
            providers[provider][entry], reports[provider][entry] = word, report
    payload = {
        "schema": "clean-late-sixteen-centre-exchange-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin}
                        for name, (path, pin) in PINS.items()},
        "ports": source["ports"], "selected_ports": pivots, "code": capture["code"],
        "response": capture["response"], "content_map": n.r.encoded(expected[:224]),
        "inverse_content_map": n.r.encoded(inverse), "providers": providers,
        "physical_contract": {
            "input_I": "X=Qx; Y=y, with all640 fields independent and arbitrary.",
            "input_Q": "X=Qx; Y_P=Q_P z; Y_U=y_U, with independent arbitrary z.",
            "source_output_I": "X_P=-F9 y_P; X_U=F9 x_U.",
            "source_output_Q": "X_P=-F9 z; X_U=F9 x_U.",
            "target_output": "Y_P=F9 Lx; Y_U=F9 q_U (y+Ex)_U.",
            "centre_baseline": "The selected centre rows contain no borrowed-Y contribution. The old selectedY baseline is retained with a minus sign on selectedX.",
            "scope": "Complete local native formation by productive exchange. The actual routed next-entry and a complete caller are separate.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    for provider, entries in json.loads(raw)["providers"].items():
        for entry, word in entries.items():
            need(verify(word, expected) == reports[provider][entry], "The full serialized clean exchange")
    (args.out / "CLEAN-LATE-EXCHANGE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_EXACT_CLEAN_LATE_CENTRE_EXCHANGE",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(),
               "reports": reports, "content_inverse_both_orders": True,
               "negative_controls": "Omitted source-code or signed-exchange ADD fails in all four complete words.",
               "native_phase_scope": "Every native recipe, frame, and endpoint adapter is byte-exact inherited from the reviewed direct-FULL formation or line-entry prefix.",
               "scope": payload["physical_contract"]["scope"]}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
