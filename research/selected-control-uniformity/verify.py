#!/usr/bin/env python3
"""Read-only control-interface replay; no full selected supplier execution."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from control import need


def run():
    source = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = []
    for item in source["files"]:
        if item["usage"] == "input":
            need(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                 "source hash: " + item["path"])
            inputs.append(item["path"])
    need(set(inputs) == set(json.loads((PACKAGE / "VERIFY.json").read_text())["inputs"]),
         "declared source closure")
    import checks
    result = checks.run()
    result["authenticated_inputs"] = inputs
    result["scope"] = "Control/metadata evidence for the written uniform-charge proof under retained complete-stream payload primitives; not full supplier realization or a new formal recurrence proof."
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if not args.emit:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text()), "complete retained receipt")
        print("PASS_SELECTED_CONTROL_UNIFORMITY")
    print(json.dumps(result, sort_keys=True, indent=2))
