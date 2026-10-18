#!/usr/bin/env python3
"""Registered exact replay; host arithmetic remains a declared macro boundary."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input" and sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("pinned source bytes changed: " + item["path"])
    import checks
    result = checks.run()
    result = json.loads(json.dumps(result, sort_keys=True))
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_text())
        if json.dumps(result, sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ValueError("retained exact receipt differs from replay")
        print("PASS_SELECTED_PREFIX_COEFFICIENT_SITE")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
