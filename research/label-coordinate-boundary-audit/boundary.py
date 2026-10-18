#!/usr/bin/env python3
"""Opt-in integer-labels-v1 plus simple-scatter-v1 boundary. Apache-2.0.

Prepared with substantial OpenAI Codex assistance. Snapshot delegation adapts
Arham Tahir's PR2992; its validator and original supplier scripts stay pinned.
Export enforces schemas only; it does not replace symbolic/native checking.
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
SCHEMA = "integer-labels-v1"
PREDECESSOR = "research/simple-scatter-boundary/boundary.py"
SCRIPTS = {
    "check": "research/e8-bit-p111-tuned/code/xcheck_p.py",
    "export": "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_labels(word):
    """Require literal integer coordinates; do not round or coerce any value."""
    require(type(word) is dict, "word must be an object")
    v, h, lines = word.get("v"), word.get("h"), word.get("lines")
    require(type(v) is int and v > 0, "v must be a positive integer")
    require(type(h) is int and h == 8, "h must be the integer 8")
    require(type(lines) is list and len(lines) == v, "lines must have exactly v rows")
    for i, row in enumerate(lines):
        require(type(row) is list and len(row) == h, f"label {i} must have h coordinates")
        for j, value in enumerate(row):
            require(type(value) is int, f"label {i} coordinate {j} must be an exact integer")


def source_bytes(path, root=ROOT):
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    rows = [row for row in pins if row["path"] == path and row["usage"] == "input"]
    require(len(rows) == 1, "unique source pin: " + path)
    body = (root / path).read_bytes()
    require(hashlib.sha256(body).hexdigest() == rows[0]["sha256"], "source pin mismatch: " + path)
    return body


def execute(mode, input_path, output=None, root=ROOT):
    require(mode in SCRIPTS and ((mode == "export") == (output is not None)),
            "export requires output; check takes none")
    raw = input_path.read_bytes()
    word = json.loads(gzip.decompress(raw) if input_path.suffix == ".gz" else raw)
    validate_labels(word)
    scope = {"__name__": "pinned_scatter", "__file__": str(root / PREDECESSOR)}
    exec(compile(source_bytes(PREDECESSOR, root), PREDECESSOR, "exec", optimize=0), scope)
    scope["validate_scatter"](word)
    body = source_bytes(SCRIPTS[mode], root)
    with tempfile.TemporaryDirectory(prefix="integer-labels-") as temporary:
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
    except (ValueError, OSError, EOFError, subprocess.TimeoutExpired) as error:
        print(f"REJECT {SCHEMA}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
