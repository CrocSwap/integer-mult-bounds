# SPDX-License-Identifier: Apache-2.0
"""Strict I/O only. Gareth Davidson, with substantial OpenAI Codex assistance."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def invalid(value):
        raise ValueError("nonfinite JSON number: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=invalid)


def sources():
    data = read(HERE / "SOURCES.json")
    root = HERE.parents[1]
    records = [item for item in data["files"] if item["usage"] == "input"]
    require(len(records) == 3, "source inventory")
    for item in records:
        raw = (root / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256 mismatch")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == item["git_blob"], "source Git blob mismatch")


def finish(result, expected, write=None):
    sources()
    if write is not None:
        with Path(write).open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        require(canonical(result) == canonical(read(HERE / expected)), "receipt mismatch")
    print("receipt_sha256=" + digest(result))
