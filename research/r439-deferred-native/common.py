"""Strict source binding and JSON I/O. Gareth Davidson / OpenAI Codex; Apache-2.0."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HUB = "research/e8-bit-carrier-skeleton"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def same(left, right, message):
    need(canonical(left) == canonical(right), message)


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def invalid(value):
    raise ValueError("nonfinite JSON: " + value)


def load(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def write(path, value):
    path = Path(path)
    raw = canonical(value)
    if path.suffix == ".gz":
        raw = gzip.compress(raw, mtime=0)
    else:
        raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)


def pins(root=ROOT):
    checked = {}
    for row in load(HERE / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            raw = (Path(root) / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
            checked[row["path"]] = row["sha256"]
    predecessor = load(HERE / "PREDECESSOR.json")
    need(predecessor["head"] == "b56dceffad83c88e8ad39ffd82a1bdd55c4130da", "predecessor head")
    for path, row in predecessor["files"].items():
        raw = (HERE / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "vendor source hash: " + path)
        checked[path] = row["sha256"]
    return checked
