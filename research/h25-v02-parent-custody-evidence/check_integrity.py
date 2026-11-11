#!/usr/bin/env python3
"""Validate archive bytes and Python syntax only; never import archived candidates."""
import ast
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
def require(ok, reason):
    if not ok:
        raise SystemExit(reason)

manifest_path = root / "MANIFEST.json"
require(not manifest_path.is_symlink(), "manifest must be a regular local file")
manifest = json.loads(manifest_path.read_text())
require(manifest.get("schema") == "v02-parent-archive-integrity-v1", "manifest schema mismatch")
entries = manifest["files"]
names = [row["path"] for row in entries]
require(len(names) == len(set(names)), "duplicate manifest path")
actual = set()
for path in root.rglob("*"):
    require(not path.is_symlink(), "symlink prohibited")
    if path.is_file():
        actual.add(path.relative_to(root).as_posix())
require(actual == set(names) | {"MANIFEST.json"}, "archive inventory mismatch")
for row in entries:
    name = row["path"]
    require(not Path(name).is_absolute() and ".." not in Path(name).parts, "nonlocal manifest path")
    raw = (root / name).read_bytes()
    require(len(raw) == row["bytes"], "byte count mismatch: " + name)
    require(hashlib.sha256(raw).hexdigest() == row["sha256"], "digest mismatch: " + name)
source_map = json.loads((root / "SOURCE-MAP.json").read_text())
indexed = {row["path"]: row for row in entries}
parsed = 0
for row in source_map["retained"]:
    name = row["archive_relative_path"]
    require(name in indexed, "source mapping missing from manifest")
    require(all(row[key] == indexed[name][key] for key in ("bytes", "sha256")), "source map mismatch")
    if row["kind"] == "final_source" and name.endswith(".py.txt"):
        ast.parse((root / name).read_text(), filename=name)
        parsed += 1
print(json.dumps({"status": "PASS_STATIC_ARCHIVE_INTEGRITY", "manifest_entries": len(entries),
    "retained_snapshots": len(source_map["retained"]), "python_snapshots_ast_parsed": parsed,
    "candidate_imports": 0, "historical_replays": 0, "original_v02_cases": 0}, sort_keys=True))
