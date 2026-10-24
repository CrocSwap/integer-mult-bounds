#!/usr/bin/env python3
"""Merge native advances across cuts with no use of their field."""

import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PINS = {
    "producer": ("emit_native.py", "b6db27a1a7e990ac297972f0306efa624bfa317d70bcb18615a38a4b8d2aac03"),
    "source": ("native-normal/NATIVE.json.gz", "f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e"),
    "freeze": ("NATIVE-FREEZE.json", "ced70c0c6fe961b1a840819ee5e8cce2756a229d4eee7ec3b5a6f8e4bac6c6eb"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    relative, pin = PINS[name]
    raw = (HERE / relative).read_bytes()
    if relative.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Coalescing source pin " + name)
    return raw


read("producer")
spec = importlib.util.spec_from_file_location("signed_native_coalescing_source", HERE / PINS["producer"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
n, r = base.n, base.r


def merge(original):
    word = deepcopy(original)
    pending, events, chains, index_map = {}, [], [], {}

    def flush(field):
        if field not in pending:
            return
        old_indices = pending.pop(field)
        first, last = (original["events"][i] for i in (old_indices[0], old_indices[-1]))
        old, new = first[2], last[3]
        rank = len(word["frames"][new]) - len(word["frames"][old])
        need(rank == sum(original["events"][i][4] for i in old_indices),
             "The complete merged advance has the same mass")
        event = ["native", field, old, new, rank, str(old) + ":" + str(new)]
        chains.append({"event": len(events), "field": field, "source_events": old_indices,
                       "old": old, "new": new, "rank": rank})
        events.append(event)

    for i, event in enumerate(original["events"]):
        if event[0] == "native":
            field = event[1]
            if field in pending:
                need(original["events"][pending[field][-1]][3] == event[2],
                     "Exact per-field native chain")
            pending.setdefault(field, []).append(i)
        else:
            need(event[0] == "scalar", "The exact event grammar")
            flush(event[1][1])
            if event[1][2] is not None:
                flush(event[1][2])
            index_map[i] = len(events)
            events.append(deepcopy(event))
    for field in sorted(pending):
        flush(field)
    word["events"] = events
    for record in word["transfer_records"]:
        record["event"] = index_map[record["event"]]
    word["coalesced_native_chains"] = chains
    need([event for event in events if event[0] == "scalar"]
         == [event for event in original["events"] if event[0] == "scalar"],
         "Every scalar event and its order are unchanged")
    covered = sorted(i for chain in chains for i in chain["source_events"])
    need(covered == [i for i, event in enumerate(original["events"]) if event[0] == "native"],
         "Each original native event occurs in one merged chain")
    return word


def verify(word, response, direction, original, source_forward):
    report = n.verify_word(word, response, direction)
    expected = merge(original)
    need(word["events"] == expected["events"]
         and word["coalesced_native_chains"] == expected["coalesced_native_chains"],
         "The exact legal coalescing transformation")
    for key in ("frames", "start", "final", "endpoint_adapters"):
        need(word[key] == original[key], "The complete endpoint and frame binding " + key)
    report["binary_height"] = base.verify(original, response, direction,
                                          source_forward)["binary_height"]
    report["scalar_events_byte_equal"] = True
    report["explicit_endpoint_monomials"] = 224
    report["merged_chain_count"] = len(word["coalesced_native_chains"])
    need(report["native_profile"] == {1: 971, 2: 237, 3: 46, 4: 12, 5: 5, 6: 11, 7: 10},
         "The complete coalesced profile")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    read("freeze")
    source = json.loads(read("source"))
    source_forward = source["providers"]["base"]["forward_E"]
    providers = {provider: {name: merge(word) for name, word in words.items()}
                 for provider, words in source["providers"].items()}
    first = providers["base"]["forward_E"]
    frames = first["frames"]
    inherited = source_forward["native_recipes"]
    edge_pairs = sorted({(event[2], event[3]) for words in providers.values()
                         for word in words.values() for event in word["events"] if event[0] == "native"})
    recipes, fresh = {}, {}
    for old, new in edge_pairs:
        key = str(old) + ":" + str(new)
        if key in inherited:
            record = inherited[key]
        else:
            operation = n.compiler.canonical_frame(9, tuple(frames[old])).adjoint().then(
                n.compiler.canonical_frame(9, tuple(frames[new])))
            record, _ = n.compiler.lower_child(operation)
            need(record["rank"] == len(frames[new]) - len(frames[old]),
                 "The exact merged native rank")
            n.phase.equal(n.phase.recipe(record), n.phase.adjoint(n.phase.frame(frames[old], 9))
                          + n.phase.frame(frames[new], 9), "Merged native phase " + key)
            fresh[key] = record
            if len(fresh) % 25 == 0:
                print("Fresh exact phase checks", len(fresh), flush=True)
        recipes[key] = record
    need(len(fresh) == 206, "The fresh phase recipe census")
    model = source["model"]
    E, dual = n.rows(model["physical"]["E"]), n.rows(model["physical"]["inverse_adjoint_E"])
    reports = {}
    for provider, words in providers.items():
        reports[provider] = {}
        for name, word in words.items():
            word["native_recipes"] = recipes
            direction = "forward" if name.startswith("forward") else "backward"
            response = E if name in ("forward_E", "backward_transpose_E") else dual
            reports[provider][name] = verify(word, response, direction, source["providers"][provider][name],
                                             source["providers"][provider]["forward_E"])
    payload = dict(source, schema="signed-metric-coalesced-native-v1", providers=providers,
                   coalescing_source_pins=PINS)
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, words in saved["providers"].items():
        for name, word in words.items():
            direction = "forward" if name.startswith("forward") else "backward"
            response = E if name in ("forward_E", "backward_transpose_E") else dual
            need(verify(word, response, direction, source["providers"][provider][name],
                        source["providers"][provider]["forward_E"])
                 == reports[provider][name], "All serialized640-column maps")
    (args.out / "NATIVE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    checks = {
        "status": "PASS_COALESCED_SIGNED_METRIC_NATIVE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "source_pins": PINS, "fresh_exact_native_phase_checks": len(fresh),
        "inherited_native_records": len(recipes) - len(fresh),
        "unchanged_endpoint_phase_records": 224, "reports": reports,
        "phase_method": "Exact18 Pauli images and the exact reference column fix the full Clifford operator and global phase.",
        "scope": "Complete local data words. All scalar events and endpoints are unchanged. The caller, terminal, helper progress and recursive host remain separate.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, sort_keys=True, indent=2) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
