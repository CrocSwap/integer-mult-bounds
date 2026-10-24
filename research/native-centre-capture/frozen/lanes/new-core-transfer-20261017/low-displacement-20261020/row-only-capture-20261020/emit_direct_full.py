#!/usr/bin/env python3
"""Remove the two identity-composite wrappers of the direct FULL child."""

import argparse
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


need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "Frozen full-capture checker")
spec = importlib.util.spec_from_file_location("frozen_productive_capture", HELPER)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Exact complete capture source")
    source = json.loads(raw)
    identity = {"linear_Z4": [0] * 9, "matrix_rows": [1 << j for j in range(9)],
                "offset": 0, "phase": 0, "quadratic_rows": [0] * 9}
    recipe = {"left": identity, "rank": 9, "right": identity}
    base.n.phase.equal(base.n.phase.recipe(recipe), base.n.phase.fourier(9),
                       "The native FULL kernel has identity wrappers")
    code = base.n.rows(source["code"])
    response = base.n.rows(source["response"])
    captured = base.n.rows(source["captured_response"])
    selected = set(source["selected_ports"])
    reports = {}
    for provider, word in source["providers"].items():
        old = word["native_recipes"]["capture-full"]
        base.n.phase.equal(base.n.phase.recipe(recipe), base.n.phase.recipe(old),
                           "The exact old and direct FULL operators")
        word["native_recipes"]["capture-full"] = recipe
        report = base.verify(word, code, response, captured, selected)
        count = sum(event[0] == "native" and event[5] == "capture-full" for event in word["events"])
        need(count == 16, "All sixteen direct FULL calls")
        report["native_side_map_upper_bound"] -= 2 * count
        report["direct_full_nontrivial_side_maps"] = 0
        need(report["native_side_map_upper_bound"] == 3008, "The complete refined side-map bound")
        reports[provider] = report
    source["schema"] = "productive-sixteen-direct-full-capture-v1"
    source["refinement_source_decompressed_sha256"] = SOURCE_PIN
    data = (json.dumps(source, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "DIRECT-FULL-CAPTURE.json.gz").write_bytes(gzip.compress(data, mtime=0))
    receipt = {
        "status": "PASS_DIRECT_FULL_REFINEMENT",
        "source_decompressed_sha256": SOURCE_PIN,
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(data).hexdigest(),
        "reports": reports,
        "scope": "Only the sixteen FULL recipe wrappers change. All exact source, target and arbitrary-baseline contracts are unchanged.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
