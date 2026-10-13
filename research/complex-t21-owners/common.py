# SPDX-License-Identifier: Apache-2.0
"""Portable JSON identities and explicit checks for the T21 witness."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def dump(path, value):
    Path(path).write_bytes((json.dumps(value, indent=2)+'\n').encode())


def write_gzip(path, value):
    raw = bytearray(gzip.compress(canonical(value), mtime=0))
    raw[9] = 255
    Path(path).write_bytes(raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
