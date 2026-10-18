#!/usr/bin/env python3
"""Complete generic preparation/control/child replay; selected GL64 is outside scope."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from algebra import need


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = []
    for item in sources["files"]:
        if item["usage"] == "input":
            need(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                 "source hash: " + item["path"])
            inputs.append(item["path"])
    need(set(inputs) == set(json.loads((PACKAGE / "VERIFY.json").read_text())["inputs"]),
         "declared source closure")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    authenticate()
    import checks
    result = checks.run(args.progress)
    if not args.emit:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text()), "complete retained receipt")
        print("PASS_SELECTED_JOINED_DISPATCH")
    print(json.dumps(result, sort_keys=True, indent=2))
