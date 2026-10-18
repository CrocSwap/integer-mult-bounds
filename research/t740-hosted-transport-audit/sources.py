"""Fixed source closure, strict manifest authentication and bounded decoding."""

import gzip
import hashlib
import io
import json
import stat
from pathlib import Path

from audit import require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LIMIT = 32_000_000
SOURCE_HASH = "594eeeb31c4e96f0a35af52c014c94c1529662fc7f52e3b6efafb5e111cec9de"
PREDECESSOR_HASH = "6d50f1b01f04c2d2aa62ba58ace619eb690bbd63f2285129c0dd5931122617a3"
PATHS = {
    "base": "research/idle-star-paired-axis-census/vendor/BASE-FILL.json.gz",
    "journal": "research/idle-star-paired-axis-census/vendor/EXCHANGE.json",
    "providers": "research/idle-star-paired-axis-census/vendor/PROVIDERS.json",
    "order": "research/rank7-joint-endframes/allocation/ORDER.json",
    "dispatch": "research/rank7-joint-endframes/allocation/DISPATCH.json",
    "plan": "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz",
    "template": "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz",
    "phases": "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
}


def regular_bytes(path):
    info = path.lstat()
    require(
        stat.S_ISREG(info.st_mode) and info.st_size <= LIMIT, "regular bounded source"
    )
    return path.read_bytes()


def pinned_bytes(path, pin):
    raw = regular_bytes(path)
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(
        hashlib.sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob",
    )
    return raw


def manifest(path, digest):
    raw = regular_bytes(path)
    require(hashlib.sha256(raw).hexdigest() == digest, "fixed manifest bytes")
    result = json.loads(raw)
    require(
        type(result["schema_version"]) is int and result["schema_version"] == 1,
        "strict manifest version",
    )
    return result


def decode(raw):
    if raw[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "decoded source bound")
    return json.loads(raw)


def load(root=ROOT, package=PACKAGE):
    pins = manifest(package / "SOURCES.json", SOURCE_HASH)["files"]
    require(type(pins) is list and len(pins) == 10, "exact source inventory")
    active = {r["path"]: r for r in pins if r["usage"] == "input"}
    require(set(active) == set(PATHS.values()), "exact live closure")
    data = {
        name: decode(pinned_bytes(root / path, active[path]))
        for name, path in PATHS.items()
    }
    predecessors = manifest(package / "PREDECESSORS.json", PREDECESSOR_HASH)["sources"]
    require(
        type(predecessors) is list and len(predecessors) == 2, "two retained sources"
    )
    for pin in predecessors:
        pinned_bytes(package / pin["local_path"], pin)
    data["reference"] = json.loads(
        (package / "reference/PR3309-RESULT.json").read_bytes()
    )
    return data
