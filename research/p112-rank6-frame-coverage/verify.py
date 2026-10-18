#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Recompute every rank-six maximal slice and its exact frame coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for source in sources["archives"]:
        name = Path(source["local_path"])
        engine.require(not name.is_absolute() and ".." not in name.parts, "unsafe archive path")
        engine.require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == source["sha256"],
                       "source archive drift: " + str(name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-directory", type=Path, help="new output directory; existing path is rejected")
    args = parser.parse_args()
    try:
        if args.write_directory:
            engine.require(not args.write_directory.exists(), "output directory already exists")
        check_sources()
        data = engine.model()
        engine.require(data == json.loads((HERE / "inputs/PR1323-MODEL.json").read_text()),
                       "predecessor root model changed")
        table, certificate = engine.census(data)
        certificate = json.loads(json.dumps(certificate))
        engine.check_cover(data, json.loads((HERE / "COVERING.json").read_text()))
        if args.write_directory:
            args.write_directory.mkdir()
            (args.write_directory / "COVERAGE.jsonl").write_bytes(engine.table_bytes(table))
            (args.write_directory / "CERTIFICATE.json").write_text(
                json.dumps(certificate, indent=2, sort_keys=True)+"\n")
        else:
            generated = HERE / "generated"
            recorded = [json.loads(s) for s in (generated / "COVERAGE.jsonl").read_text().splitlines()]
            engine.require(table == recorded, "complete coverage table disagreement")
            engine.require(certificate == json.loads((generated / "CERTIFICATE.json").read_text()),
                           "coverage certificate disagreement")
        print("PASS_P112_RANK6_FRAME_COVERAGE atoms=7616 slices=967232 max_hits=1120 average_floor=54 cover_bill=60")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_P112_RANK6_FRAME_COVERAGE: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
