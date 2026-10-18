# SPDX-License-Identifier: Apache-2.0
"""Authenticate all predecessor bytes before importing their implementation."""

import hashlib
import json
import sys
from pathlib import Path

from scalars import require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PARENT = ROOT / "research/rank7-boolean-scalar-caller"


def load():
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    require(1 <= len(records) <= 64, "bounded complete dependency inventory")
    for record in records:
        if record["usage"] != "input":
            continue
        path = ROOT / record["path"]
        require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000, "regular input"
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "source hash",
        )
    sys.path.insert(0, str(PARENT))
    import bitadder
    import caller
    import replay
    from source.vendor.lowering import lower

    return bitadder, caller, replay, lower
