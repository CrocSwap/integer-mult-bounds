#!/usr/bin/env python3
"""Opt-in simple-scatter-v1 entry points. Arham Tahir; Apache-2.0.

Substantial OpenAI Codex assistance. The original checker/exporter and their
notices remain unchanged. Export mode adds schema validation, not a symbolic
or native endpoint check.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCHEMA = "simple-scatter-v1"
SCRIPTS = {
    "check": "research/e8-bit-p111-tuned/code/xcheck_p.py",
    "export": "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
}


def validate_scatter(word):
    """Rows are simple supports; multiplicities are rejected, never normalized."""
    if type(word) is not dict:
        raise ValueError("word must be an object")
    v, retained, rows = word.get("v"), word.get("ret"), word.get("scatter")
    if type(v) is not int or v <= 0:
        raise ValueError("v must be a positive integer")
    if type(retained) is not list:
        raise ValueError("ret must be a list")
    if type(rows) is not list or len(rows) != v:
        raise ValueError("scatter must have exactly v rows")
    for t, row in enumerate(rows):
        if type(row) is not list:
            raise ValueError(f"scatter row {t} must be a list")
        seen = set()
        for k in row:
            if type(k) is not int or not 0 <= k < len(retained):
                raise ValueError(f"scatter row {t}: index must be an integer in range")
            if k in seen:
                raise ValueError(f"scatter row {t}: duplicate index {k}")
            seen.add(k)


def script_bytes(root, mode):
    path = SCRIPTS[mode]
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    pin = next(row for row in pins if row["path"] == path and row["usage"] == "input")
    body = (root / path).read_bytes()
    if hashlib.sha256(body).hexdigest() != pin["sha256"]:
        raise ValueError("source pin mismatch: " + path)
    return body


def execute(mode, input_path, output=None, root=ROOT):
    """Validate once, then delegate using private snapshots of word and script."""
    if mode not in SCRIPTS or (mode == "export") != (output is not None):
        raise ValueError("export requires an output directory; check takes none")
    raw = input_path.read_bytes()
    word = json.loads(gzip.decompress(raw) if input_path.suffix == ".gz" else raw)
    validate_scatter(word)
    body = script_bytes(root, mode)
    with tempfile.TemporaryDirectory(prefix="simple-scatter-") as temporary:
        directory = Path(temporary)
        script, snapshot = directory / "delegate.py", directory / "word.json.gz"
        script.write_bytes(body)
        snapshot.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        command = [sys.executable, "-I", "-B", str(script), str(snapshot)]
        if output is not None:
            command.append(str(output))
        return subprocess.run(command, check=False, timeout=60).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=SCRIPTS)
    parser.add_argument("word", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        return execute(args.mode, args.word, args.output)
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f"REJECT {SCHEMA}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
