"""Strict artifact I/O, adapted from Gareth Davidson's PR980; Apache-2.0."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "ba82555c64e1879e4b7decce28186f208fcb8262"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
A_WORD = "research/r439-global-prefix-admission/candidate.json.gz"
BD_WORD = "vendor/pr1062/candidate.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
HUB = "research/e8-bit-carrier-skeleton"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


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
    with path.open("xb") as stream:
        if path.suffix == ".gz":
            stream.write(gzip.compress(canonical(value), mtime=0))
        else:
            stream.write((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def pins(root):
    manifest = load(HERE / "SOURCES.json")
    need(manifest["base_commit"] == BASE, "base context")
    for scope, directory in (("files", Path(root)), ("vendor_files", HERE)):
        for name, row in manifest[scope].items():
            need(hashlib.sha256((directory / name).read_bytes()).hexdigest() == row["sha256"],
                 "source hash mismatch: " + name)
    return manifest


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
