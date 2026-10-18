# SPDX-License-Identifier: Apache-2.0
"""Bounded source loading for the mixed-entrance audit."""

import gzip
import hashlib
import io
import json
import sys
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/rank7-joint-endframes/"
ENGINE = "research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow/"
COMPILER = ENGINE + "vendor/clifford/clifford_exact.py"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
HELPERS = (331, 450, 451, 508, 509)
W = [256, 128, 64, 38, 20, 10, 1]
LIMIT = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def decode(raw, compressed=False):
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "decoded input capacity")
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def authenticate(root=ROOT):
    rows = decode((PACKAGE / "SOURCES.json").read_bytes())["files"]
    pins = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    declared = set(decode((PACKAGE / "VERIFY.json").read_bytes())["inputs"])
    require(set(pins) == declared and len(pins) <= 24, "exact live input inventory")
    blobs = {}
    for name, sha in pins.items():
        path = root / name
        require(path.stat().st_size <= LIMIT, "raw input capacity")
        raw = path.read_bytes()
        require(digest(raw) == sha, "source SHA256: " + name)
        blobs[name] = raw
    return blobs


def data(blobs, relative):
    return decode(blobs[SOURCE + relative], relative.endswith(".gz"))


def module(raw, name):
    """Compile authenticated bytes directly, without consulting a .pyc file."""
    result = types.ModuleType(name)
    sys.modules[name] = result
    exec(compile(raw, name, "exec"), result.__dict__)
    return result


def reject(action, reason):
    try:
        action()
    except (ValueError, AssertionError) as error:
        return str(error)
    raise ValueError("control accepted: " + reason)
