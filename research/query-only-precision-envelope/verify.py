#!/usr/bin/env python3
"""Replay only the explicitly requested bounded source/countermodel certificate.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from source_binding import check_dependencies, need
import envelopes
import guards
import boundary
import controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("envelopes", "guards", "boundary", "controls", "all"), default="all")
    parser.add_argument("--write", action="store_true", help="write the deterministic local receipt before freeze")
    args = parser.parse_args()
    files = check_dependencies()
    modules = dict(envelopes=envelopes, guards=guards, boundary=boundary, controls=controls)
    for name, module in modules.items():
        if args.suite not in (name, "all"):
            continue
        result = module.run()
        path = ROOT / (name.upper() + ".json")
        if args.write:
            path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            need(result == json.loads(path.read_bytes()), "frozen receipt agrees: " + name)
        print("PASS_QUERY_ONLY_PRECISION_" + name.upper(), flush=True)
    print("AUTHENTICATED_SOURCE_FILES", files)


if __name__ == "__main__":
    main()
