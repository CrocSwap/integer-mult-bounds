"""Authenticate every declared executable/archive before predecessor imports."""
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate(root=ROOT, package=HERE):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (root / row["path"]).read_bytes()
            if sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("source changed: " + row["path"])
    for row in manifest.get("external_proofs", []):
        if sha256((package/row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("inherited proof changed: " + row["path"])


def activate():
    authenticate()
    path = ROOT / "research/selected-bit-fast-primitives"
    sys.path.insert(0, str(path))
    # This module is deliberately not named 'source' when imported: the
    # unchanged archive loader reserves that name for its own predecessor.
    import stage_sources
    return stage_sources.activate()
