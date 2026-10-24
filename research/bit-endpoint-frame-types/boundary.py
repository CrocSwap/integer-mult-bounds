#!/usr/bin/env python3
"""Typed endpoint IDs before the retained integer-label/XOR checked exporter.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Snapshot/delegation follows Pierre's integer-xor-scatter boundary, which retains
Nick Petalas's XOR and josecarlosgonzalezroque-design's label contracts.
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
SCHEMA = "typed-endpoints-integer-xor-v1"
MAX_BYTES = 5 * 1024 * 1024
PREDECESSOR = "research/integer-xor-scatter-boundary/boundary.py"
DEPENDENCIES = (
    PREDECESSOR,
    "research/integer-xor-scatter-boundary/SOURCES.json",
    "research/label-coordinate-boundary-audit/boundary.py",
    "research/xor-scatter-boundary/boundary.py",
    "research/xor-scatter-boundary/SOURCES.json",
    "research/e8-bit-p111-tuned/code/xcheck_p.py",
    "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, compressed=False):
    require(path.stat().st_size <= MAX_BYTES, "input exceeds 5 MiB")
    with (gzip.open if compressed else open)(path, "rb") as stream:
        body = stream.read(MAX_BYTES + 1)
    require(len(body) <= MAX_BYTES, "input exceeds 5 MiB")
    return body


def validate_endpoints(word):
    """Require one exact in-range integer frame ID per actual role at each end.

    Do not coerce bool, float or string IDs. Geometry, endpoint action and all
    other word conditions remain the unchanged symbolic checker's obligations.
    """
    require(type(word) is dict, "word must be an object")
    v, helpers = word.get("v"), word.get("R")
    require(type(v) is int and 1 <= v <= 256, "v outside 1..256")
    require(type(helpers) is int and 0 <= helpers <= 4096, "R outside 0..4096")
    frames = word.get("frames")
    require(type(frames) is list and bool(frames), "frames must be a nonempty list")
    roles = 2 * v + helpers
    for name in ("start", "final"):
        endpoints = word.get(name)
        require(type(endpoints) is list and len(endpoints) == roles,
                name + " must have exactly one entry per role")
        for role, frame in enumerate(endpoints):
            require(type(frame) is int and 0 <= frame < len(frames),
                    f"{name}[{role}] must be an exact in-range integer frame ID")
    return roles


def sources(root):
    rows = json.loads(read_bounded(PACKAGE / "SOURCES.json"))["files"]
    require(type(rows) is list and len(rows) <= 32, "bounded source inventory")
    bodies = {}
    for path in DEPENDENCIES:
        pins = [row for row in rows if row["path"] == path and row["usage"] == "input"]
        require(len(pins) == 1, "unique source pin: " + path)
        body = read_bounded(root / path)
        require(hashlib.sha256(body).hexdigest() == pins[0]["sha256"],
                "source pin mismatch: " + path)
        bodies[path] = body
    return bodies


def module(body, path):
    namespace = {"__name__": "authenticated_boundary", "__file__": str(path)}
    exec(compile(body, str(path), "exec", optimize=0), namespace)
    return namespace


def execute(mode, input_path, output=None, root=ROOT, scratch=None):
    require(mode in ("check", "export"), "unknown mode")
    require((mode == "export") == (output is not None), "export needs output; check takes none")
    if output is not None:
        require(not output.exists() and not output.is_symlink(), "output already exists")
    word = json.loads(read_bounded(input_path, input_path.suffix == ".gz"))
    roles = validate_endpoints(word)
    bodies = sources(root)
    with tempfile.TemporaryDirectory(prefix="typed-endpoints-", dir=scratch) as temporary:
        directory = Path(temporary)
        private_root = directory / "sources"
        for path, body in bodies.items():
            target = private_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        snapshot = directory / "word.json.gz"
        snapshot.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        predecessor = module(bodies[PREDECESSOR], private_root / PREDECESSOR)
        result = predecessor["execute"](mode, snapshot, output, root=private_root, scratch=directory)
    require(result["schema"] == "integer-xor-scatter-v1", "delegate schema")
    return {**result, "schema": SCHEMA, "endpoint_roles": roles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "export"))
    parser.add_argument("word", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--scratch", type=Path)
    args = parser.parse_args()
    try:
        result = execute(args.mode, args.word, args.output, scratch=args.scratch)
    except (ValueError, OSError, EOFError, RecursionError, subprocess.TimeoutExpired) as error:
        print(f"REJECT {SCHEMA}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
