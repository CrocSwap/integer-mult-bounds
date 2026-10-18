#!/usr/bin/env python3
"""Optional reproduction of producer artifacts; not an independent proof kernel.

Apache-2.0. Ross Richardson with substantial OpenAI Codex assistance.
Requires a read-only export of pinned PR2435 and numpy==2.4.2.
Writes only to a new explicit output directory; compares complete JSON payloads.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = "research/gmx-t74-borrow43-handoff/new"


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-tree", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source_tree.resolve(), args.output.resolve()
    manifest = read_json(HERE / "INPUTS.json")
    try:
        import numpy
        if numpy.__version__ != "2.4.2":
            raise ValueError("producer environment requires numpy==2.4.2")
        originals = [r for r in manifest["files"] if r["path"].startswith("inputs/") and "source_path" in r]
        for row in manifest["producers"] + originals:
            payload = (source / row["source_path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != row["sha256"]:
                raise ValueError("source pin mismatch: " + row["source_path"])
        output.mkdir(parents=True, exist_ok=False)
        code = source / SOURCE / "code/borrow"
        for variant in ("base", "extra"):
            dest = output / variant
            word = source / SOURCE / "borrow/words" / ("BORROW-WORD-43" + variant + ".json.gz")
            commands = [
                [code / "bw_transport.py", word, dest],
                [code / "bw_emit.py", dest],
                [code / "bw_adapters.py", dest / "CANONICAL-WORD.json.gz",
                 dest / "RESIDUAL-ADAPTERS.json", dest / "WRAPPER-CHECKS.json"],
            ]
            for command in commands:
                subprocess.run([sys.executable, "-B", *map(str, command)], check=True, timeout=120)
            for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "RESIDUAL-ADAPTERS.json"):
                if read_json(dest / name) != read_json(HERE / "inputs" / (variant + "-" + name)):
                    raise ValueError("complete generated payload mismatch: " + variant + "/" + name)
    except (OSError, ValueError, ImportError, subprocess.SubprocessError) as exc:
        print("FAIL_T74_PRODUCER_REPRODUCTION:", exc, file=sys.stderr)
        return 1
    print("PASS_T74_PRODUCER_REPRODUCTION six_complete_payloads no_independence_claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
