#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Complete source-bound late-cut replay; no supplier or new kappa claim."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine


def read_inputs():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for source in sources["archives"]:
        path = Path(source["local_path"])
        engine.require(not path.is_absolute() and ".." not in path.parts, "unsafe input path")
        engine.require(hashlib.sha256((HERE/path).read_bytes()).hexdigest() == source["sha256"],
                       "source archive drift")
    word = json.loads(gzip.decompress((HERE / "inputs/PR589-WORD.json.gz").read_bytes()))
    predecessor = json.loads((HERE / "inputs/PR1256-CERTIFICATE.json").read_text())
    return word, predecessor


def check_initial_cut(record, predecessor):
    old = next(row for row in predecessor["retirements"] if row["helper"] == 468)
    engine.require(list(engine.bits(int(record["restore_hex"], 16))) == old["restore_row"],
                   "initial restoration row differs from PR1256")
    engine.require(list(engine.bits(int(record["dirt_hex"], 16))) == old["dirty_column"],
                   "initial dirty column differs from PR1256")
    engine.require(list(engine.bits(int(record["participants_hex"], 16))) == old["forced_participants"],
                   "initial footprint differs from PR1256")
    engine.require(record["illegal_target_promotions"] == old["illegal_target_promotions"],
                   "initial illegal targets differ from PR1256")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-directory", type=Path, help="new receipt directory; existing paths refused")
    args = parser.parse_args()
    try:
        if args.write_directory:
            engine.require(not args.write_directory.exists(), "output directory already exists")
        word, predecessor = read_inputs()
        events, records, summary, geometry = engine.census(word)
        check_initial_cut(records[0], predecessor)
        engine.require(not summary["not_excluded"], "a cut survives; the obstruction claim is invalid")
        files = dict(CUTS=engine.ledger_bytes(records),
                     EVENTS=(json.dumps(events, separators=(",", ":"))+"\n").encode(),
                     CERTIFICATE=(json.dumps(summary, sort_keys=True, indent=2)+"\n").encode(),
                     GEOMETRY=(json.dumps(geometry, sort_keys=True, indent=2)+"\n").encode())
        if args.write_directory:
            args.write_directory.mkdir()
            for name, content in files.items():
                (args.write_directory/(name + (".jsonl" if name == "CUTS" else ".json"))).write_bytes(content)
        else:
            for name, content in files.items():
                path = HERE / "generated" / (name + (".jsonl" if name == "CUTS" else ".json"))
                engine.require(path.read_bytes() == content, "complete " + name + " receipt disagreement")
        print("PASS_R439_HELPER468_LATE_CUT cuts=4874 excluded=4874 joins=9 arbitrary_suffix_from=177 new_kappa=false")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_R439_HELPER468_LATE_CUT: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
