"""Bounded source authentication and binary linear algebra. Apache-2.0."""

import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MANIFEST_HASH = "99c07244428f1ec7449ab8466f5b43e8c0fef15564300ce81876328e219f10f7"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(not path.is_symlink() and path.is_file(), "regular input")
    require(path.stat().st_size <= 100_000, "input size bound")
    return json.loads(path.read_bytes())


def authenticate(package=PACKAGE, root=ROOT):
    manifest = read_json(package / "SOURCES.json")
    canonical = json.dumps(manifest, sort_keys=True).encode()
    require(
        hashlib.sha256(canonical).hexdigest() == MANIFEST_HASH,
        "fixed source inventory, schema types and usage",
    )
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    for row in rows + manifest["retained_files"]:
        path = root / row["path"] if "path" in row else package / row["local_path"]
        require(not path.is_symlink() and path.is_file(), "regular source")
        raw = path.read_bytes()
        require(len(raw) <= 100_000, "source size bound")
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw)
        require(blob.hexdigest() == row["git_blob"], "source Git blob")
    return manifest


def geometry():
    authenticate()
    path = ROOT / "research/p112-root-simplex-exclusion/geometry.py"
    spec = importlib.util.spec_from_file_location("pinned_geometry", path)
    require(spec is not None and spec.loader is not None, "geometry loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def basis(values, bits=9):
    require(len(values) <= 120 and bits in (9, 18), "basis input bound")
    pivots = [0] * bits
    for value in values:
        require(type(value) is int and 0 <= value < 1 << bits, "binary value")
        for bit in range(bits - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return tuple(x for x in pivots if x)


def span(values):
    generators = basis(values)
    require(len(generators) <= 8, "span dimension bound")
    result = [0]
    for value in generators:
        result += [x ^ value for x in result]
    return result
