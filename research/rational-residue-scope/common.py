"""Strict source-bound artifact I/O, adapted from PR1159; Apache-2.0."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def invalid(value):
    raise ValueError("nonfinite JSON: " + value)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def load(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def write(path, value):
    path = Path(path)
    with path.open("xb") as stream:
        stream.write(gzip.compress(canonical(value), mtime=0) if path.suffix == ".gz" else
                     (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def pins():
    manifest = load(HERE / "SOURCE-PINS.json")
    for name, pin in manifest["files"].items():
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == pin["sha256"],
             "source hash mismatch: " + name)
    return manifest
