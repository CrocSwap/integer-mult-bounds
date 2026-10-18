#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Exact first-copy-drop replay; full arbitrary-erasure argument is in PROOF.md."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("primary_engine", HERE / "engine.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def check_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for source in manifest["archives"]:
        path = Path(source["local_path"])
        engine.need(not path.is_absolute() and ".." not in path.parts, "invalid source path")
        actual = hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        engine.need(actual == source["sha256"], "source pin mismatch: " + str(path))
    return json.loads((HERE / "inputs/PR1226-RESULTS.json").read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-directory", type=Path, help="write new artifacts; refuse existing directory")
    args = parser.parse_args()
    try:
        if args.write_directory:
            engine.need(not args.write_directory.exists(), "receipt directory already exists")
        predecessor = check_sources()
        data = engine.model()
        histogram, table = engine.census(data)
        engine.need(histogram == predecessor["census"]["beta_histogram"], "parent rank census changed")
        engine.need(len(table) == predecessor["census"]["beta7_atom_count"] == 7616, "rank-seven coverage changed")
        summary = engine.summarize(data, histogram, table)
        summary = json.loads(json.dumps(summary))
        if args.write_directory:
            args.write_directory.mkdir()
            (args.write_directory / "MODEL.json").write_text(json.dumps(data, indent=2)+"\n")
            (args.write_directory / "CERTIFICATE.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
            (args.write_directory / "THRESHOLDS.jsonl").write_bytes(engine.table_bytes(table))
        else:
            expected = HERE / "generated"
            engine.need(data == json.loads((expected / "MODEL.json").read_text()), "model receipt changed")
            recorded = [json.loads(line) for line in (expected / "THRESHOLDS.jsonl").read_text().splitlines()]
            engine.need(table == recorded, "threshold table changed")
            engine.need(summary == json.loads((expected / "CERTIFICATE.json").read_text()), "summary certificate changed")
        print("PASS_P112_STAR_FIRST_COST_DROP atoms=7616 codewords=967232 copy_drop=20 frame_change=4 even_loss=560")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_P112_STAR_FIRST_COST_DROP: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
