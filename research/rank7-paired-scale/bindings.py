# SPDX-License-Identifier: Apache-2.0
"""Authenticate external inputs and the exact PR3152 comparator before import."""

import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PARENT = ROOT / "research/rank7-boolean-scalar-caller"


def authenticate(package=PACKAGE, root=ROOT):
    records = json.loads((package / "SOURCES.json").read_text())["files"]
    if not 1 <= len(records) <= 64:
        raise ValueError("bounded source inventory")
    upstream = json.loads((package / "UPSTREAM.json").read_text())["files"]
    if len(upstream) != 2:
        raise ValueError("complete PR3152 comparator inventory")
    paths = [(root / r["path"], r["sha256"]) for r in records if r["usage"] == "input"]
    paths += [(package / r["path"], r["sha256"]) for r in upstream]
    for path, digest in paths:
        if path.is_symlink() or path.stat().st_size > 8_000_000:
            raise ValueError("bounded regular source")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"source hash: {path}")
    return len(paths)


def load():
    count = authenticate()
    sys.path.insert(0, str(PARENT))
    import bitadder
    import caller
    import replay
    from source.vendor.lowering import lower

    return bitadder, caller, replay, lower, count


def load_scalar():
    authenticate()
    from vendor import scalars

    return scalars
