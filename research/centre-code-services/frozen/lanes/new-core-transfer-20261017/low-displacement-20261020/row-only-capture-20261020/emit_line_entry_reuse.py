#!/usr/bin/env python3
"""Emit the local line-entry interface for arbitrary centre records."""

import argparse
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "run-normal/PRODUCTIVE-CAPTURE.json.gz"
SOURCE_PIN = "7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2"
HELPER = HERE / "emit_capture.py"
HELPER_PIN = "1557c9f38b1d89f6d38e920d8db604607519a99cf37366b4c15414aed489cf1f"


def need(test, message):
    if not test:
        raise ValueError(message)


need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "The pinned formation checker")
spec = importlib.util.spec_from_file_location("line_entry_base", HELPER)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Exact complete formation source")
    source = json.loads(raw)
    selected = set(source["selected_ports"])
    response = base.n.rows(source["response"])
    captured = base.n.rows(source["captured_response"])
    identity = base.n.r.identity(112)
    reports, words = {}, {}
    fresh = 0
    for provider, original in source["providers"].items():
        word = deepcopy(original)
        start_core, end_core = original["stage_ranges"]["retained_core"]
        start_query, end_query = original["stage_ranges"]["late_query"]
        kept = deepcopy(original["events"][start_core:end_core])
        query = deepcopy(original["events"][start_query:end_query])
        events = list(kept)
        word["native_recipes"].pop("capture-full")
        source_views = {view["port"]: view for view in original["input_views"]}
        input_views = [{**view, "field": view["port"]} for view in original["input_views"]]
        for p in source["selected_ports"]:
            line = original["start"][p]
            word["start"][112 + p] = line
            old = base.n.compiler.canonical_frame(9, tuple(word["frames"][line]))
            full = base.n.compiler.canonical_frame(9, tuple(word["frames"][1]))
            operation = old.adjoint().then(full)
            recipe, _ = base.n.compiler.lower_child(operation)
            need(recipe["rank"] == 8, "The exact line-to-FULL rank")
            circuit = base.n.phase.adjoint(base.n.phase.frame(word["frames"][line], 9)) \
                + base.n.phase.frame(word["frames"][1], 9)
            base.n.phase.equal(base.n.phase.recipe(recipe), circuit,
                               "Exact selected line-entry advance")
            fresh += 1
            key = "capture-line:" + str(p)
            word["native_recipes"][key] = recipe
            events.append(["native", 112 + p, line, 1, 8, key])
            input_views.append({**source_views[p], "role": "selected_target",
                                "field": 112 + p, "source_entry_port": p})
        query_start = len(events)
        events.extend(query)
        word["events"] = events
        word["input_views"] = input_views
        word.pop("new_full_recipe_circuit")
        word["stage_ranges"] = {"precode": [0, 0], "retained_core": [0, len(kept)],
                                "selected_line_progress": [len(kept), query_start],
                                "late_query": [query_start, len(events)]}
        report = base.verify(word, identity, response, captured, selected)
        need(report["native_profile"] == {1: 1392, 2: 64, 3: 48, 8: 16},
             "The complete reuse profile")
        need(report["native_mass"] == 1792 and report["real_scalar_primitives"] == 9880,
             "The complete current-reader local invoice")
        need(len(input_views) == 128 and len(word["output_views"]) == 96,
             "All source and selected target input views are charged")
        reports[provider], words[provider] = report, word
        bad = deepcopy(word)
        bad["start"][112 + source["selected_ports"][0]] = 0
        try:
            base.verify(bad, identity, response, captured, selected)
        except ValueError:
            pass
        else:
            raise ValueError("The wrong selected I-frame input was accepted")
    payload = {
        "schema": "productive-sixteen-line-entry-reuse-v1",
        "source_decompressed_sha256": SOURCE_PIN,
        "ports": source["ports"], "selected_ports": source["selected_ports"],
        "ordinary_ports": source["ordinary_ports"], "response": source["response"],
        "selected_query_response": source["captured_response"], "providers": words,
        "physical_contract": {
            "input": "X_p=Q_p x_p; Y_p=y_p outside P; Y_p=Q_p z_p on P",
            "source_output": "X_p=F9 x_p for every p",
            "ordinary_target_output": "Y_p=F9 q_p (y+E x)_p outside P",
            "selected_target_output": "Y_p=F9 [z_p+(C E x)_p] on P",
            "baseline": "All16 records z and all other data/helper fields are independent and arbitrary.",
            "reader_scope": "The late query uses the same local reader C_P. A routed past-reader query is a separate word and invoice.",
        },
    }
    data = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(data)
    for provider, word in saved["providers"].items():
        need(base.verify(word, identity, response, captured, selected) == reports[provider],
             "The complete serialized line-entry replay")
    (args.out / "LINE-ENTRY-REUSE.json.gz").write_bytes(gzip.compress(data, mtime=0))
    receipt = {"status": "PASS_EXACT_LOCAL_LINE_ENTRY_REUSE",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "source_decompressed_sha256": SOURCE_PIN,
               "payload_decompressed_sha256": sha256(data).hexdigest(),
               "reports": reports, "fresh_phase_checks": fresh,
               "negative_control": "A selected I-frame input is rejected.",
               "scope": "Exact arbitrary-record local interface only. The actual past/current routed reader product, its access maps, and the complete supplier remain separate."}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
