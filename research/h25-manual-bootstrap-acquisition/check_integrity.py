"""Passive package inventory/checksum validation; imports no candidate source."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
inventory = json.loads((root / "INVENTORY.json").read_text())
excluded = {"INVENTORY.json", "SHA256SUMS"}
expected = {item["path"]: item for item in inventory["files"]}
actual = set()
for path in root.rglob("*"):
    if path.is_symlink():
        raise SystemExit("symlink forbidden")
    if path.is_file():
        actual.add(path.relative_to(root).as_posix())
if actual != set(expected) | excluded:
    raise SystemExit("inventory path-set mismatch")
for name, item in expected.items():
    if Path(name).is_absolute() or ".." in Path(name).parts:
        raise SystemExit("unsafe inventory path")
    data = (root / name).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"] or blob != item["git_blob"]:
        raise SystemExit("inventory digest mismatch: " + name)
checks = {}
for line in (root / "SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    if name in checks or Path(name).is_absolute() or ".." in Path(name).parts:
        raise SystemExit("unsafe/duplicate checksum path")
    checks[name] = digest
if set(checks) != actual - {"SHA256SUMS"}:
    raise SystemExit("checksum path-set mismatch")
for name, digest in checks.items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
        raise SystemExit("checksum mismatch: " + name)
print("PASS passive byte inventory;", len(actual), "files; no source imported or qualification performed")
