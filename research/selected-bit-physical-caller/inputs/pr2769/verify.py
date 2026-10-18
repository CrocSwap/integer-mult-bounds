#!/usr/bin/env python3
"""Check fixed-tape bank parking against its pinned source contracts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    expected = set()
    for entry in manifest["snapshots"]:
        name = entry["path"]
        if name in expected or not name.startswith("vendor/"):
            raise ValueError("unique scoped source inventory")
        expected.add(name)
        if sha256((HERE / name).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("pinned predecessor source changed: " + name)
    observed = {path.relative_to(HERE).as_posix() for path in (HERE / "vendor").glob("*.py")}
    if observed != expected:
        raise ValueError("complete predecessor source inventory")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    authenticate()
    sys.path[:0] = [str(HERE), str(HERE / "vendor")]
    from checks import run
    result = run()
    receipt = {"sha256": sha256(canonical(result).encode()).hexdigest(), "result": result}
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_text())
        if canonical(expected) != canonical(receipt):
            print(json.dumps(receipt, indent=2, sort_keys=True))
            raise ValueError("complete numerical-bank parking receipt differs")
        print("PASS_SELECTED_BIT_REGISTER_PARKING")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
