#!/usr/bin/env python3
"""Read-only exact caller-boundary checks for the conservative outer proof."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from packing import need


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = []
    for item in sources["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == item["sha256"], "source hash: " + item["path"])
            inputs.append(item["path"])
    manifest = json.loads((PACKAGE / "VERIFY.json").read_text())
    need(set(inputs) == set(manifest["inputs"]), "declared complete source closure")
    return inputs


def run():
    inputs = authenticate()
    import checks
    return {"schema_version": 1, "authenticated_inputs": inputs,
            "parameters": checks.parameters(), "compressed_domains": checks.compressed_domains(),
            "packing": checks.packing_checks(), "rounded_convolution": checks.convolution_checks(ROOT),
            "crt": checks.crt_checks(ROOT), "recovery": checks.recovery_checks(),
            "scope": "Exact finite caller-boundary evidence for a written transfer conditional on the named completed callees. No full Gaussian multiplier, selected supplier execution, formal proof or frontier change."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if not args.emit:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(result == expected, "complete retained receipt")
        print("PASS_SELECTED_CONSERVATIVE_OUTER_INTERFACES")
    print(json.dumps(result, sort_keys=True, indent=2))
