#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Freeze the exact inputs and run receipts consumed by the low signed replay."""

import argparse
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path


def load(path):
    return json.loads(path.read_bytes())


def require(test, message):
    if not test:
        raise ValueError(message)


def freeze(core, native, independent, resources, out):
    pair = native / "pair"
    build_path = pair / "BINDING.json"
    build = load(build_path)
    prior = load(independent)
    launch_path = native / "native-logs" / "launch.json"
    mark = load(launch_path)
    native_result = native / "replay" / "RESULT.json"
    require(mark["exit"] == 0 and mark["status"] == "PASS_7636_LOWERED_C_NATIVE"
            and mark["native_result_sha256"] == sha256(native_result.read_bytes()).hexdigest(), "actual native pass")
    require(prior["result"] == "PASS_PAIRED_EXACT_REPLAY_AND_CONDITIONAL_PRICE", "actual independent pass")
    source, candidate = (pair / role / "WORD.json.gz" for role in ("source", "candidate"))
    refs = {
        "clear_result": build_path, "source_word": source, "word": candidate,
        "source_clear": pair / "source" / "CLEAR-CERTIFICATES.json",
        "candidate_clear": pair / "candidate" / "CLEAR-CERTIFICATES.json",
        "source_invoice": core / "retained" / "pr7636" / "data" / "invoice-new.json",
        "public_b_invoice": core / "evidence" / "pr7636" / "mutation" / "INVOICE.json",
        "independent_pair": independent, "native_result": native_result, "native_receipt": launch_path,
        "native_start": native / "native-logs" / "START.json", "native_stdout": native / "native-logs" / "stdout.txt",
        "native_stderr": native / "native-logs" / "stderr.txt", "native_time": native / "native-logs" / "time.txt",
        "native_adapter": native / "verify_low_native.py", "native_launcher": native / "run_guarded_low.py",
        "native_physical": native / "engines" / "physical.py", "native_walsh": native / "engines" / "walsh.py",
        "native_authorization": native / "native-authorization.json",
    }
    for role, prefix in (("source", "source_"), ("candidate", "")):
        folder = resources / ("resource-" + role)
        refs[role + "_resource_result"] = folder / "RESULT.json"
        refs[role + "_resource_exit"] = folder / "EXIT.json"
        for name, suffix in (("GRID", "grid"), ("LITERALS", "literals"), ("ORDINARY", "ordinary"),
                             ("TAPE-SCALAR", "tape_scalar"), ("TARIFF", "tariff")):
            refs[prefix + suffix] = folder / (name + ".json")
    inputs = {name: {"path": os.path.relpath(path.resolve(), out.resolve().parent),
                     "sha256": sha256(path.read_bytes()).hexdigest()} for name, path in refs.items()}
    word = json.loads(gzip.decompress(candidate.read_bytes()))
    mains = set(word["live"]) | {r + 112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helpers = set(range(word["public"])) - mains
    catalogue = {(e[2], e[3]) for e in word["program"] if e[0] == "MOVE"}
    catalogue.update((word["initial"][r], word["final"][r]) for r in helpers)
    result = {
        "source_pr": 7636, "source_head": build["source_head"], "source_canonical_sha256": build["source"]["canonical_sha256"],
        "candidate_canonical_sha256": build["candidate"]["canonical_sha256"], "candidate_raw_sha256": build["candidate"]["raw_sha256"],
        "paid_positions": 109618, "catalogue_size": len(catalogue), "bit_pin": ".00376669",
        "source_bracket": prior["matched_lowered_7636"]["price"]["kappa"], "public_b_bracket": prior["source"]["price"]["kappa"],
        "bracket": prior["candidate"]["price"]["kappa"], "claim": "0.0036813560186", "probe": "0.00368135601867",
        "inputs": inputs, "native_launch": {k: mark[k] for k in ("adapter_sha256", "launcher_sha256", "run_id", "status")},
    }
    with out.open("x") as output:
        json.dump(result, output, sort_keys=True, indent=2)
        output.write("\n")
    print("Frozen signed inputs", len(inputs), "catalogue", len(catalogue), "spec SHA-256", sha256(out.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("core", "native", "independent", "resources", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    freeze(args.core, args.native, args.independent, args.resources, args.out)


if __name__ == "__main__":
    main()
