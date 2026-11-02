# SPDX-License-Identifier: GPL-3.0-or-later
"""Cold fixture replay of only the new ordering component."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / "ARTIFACTS.json").read_text())
actual = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "ARTIFACTS.json")
expected = sorted(row["path"] for row in manifest["files"])
if actual != expected:
    raise RuntimeError("archive file set changed")
for row in manifest["files"]:
    raw = (root / row["path"]).read_bytes()
    if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise RuntimeError("archive byte identity changed: " + row["path"])
sys.argv = [str(root / "test_prefix_visits_v1.py")]
runpy.run_path(sys.argv[0], run_name="__main__")
