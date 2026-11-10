"""Offline source authentication and unchanged-source imports.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    records = json.loads((ROOT / "DEPENDENCIES.json").read_text())["files"]
    for record in records:
        data = (ROOT / record["path"]).read_bytes()
        need(len(data) == record["bytes"], "retained length: " + record["path"])
        need(hashlib.sha256(data).hexdigest() == record["sha256"],
             "retained SHA256: " + record["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == record["git_blob"],
             "retained Git blob: " + record["path"])
    return records


def vendor(name, path):
    # The unchanged rounded-table source requests its original relative path.
    aliases = {"vendor/exact_scalar_tables.py": "retained/exact_scalar_tables.py"}
    path = aliases.get(path, path)
    records = authenticate()
    need(path in {r["path"] for r in records}, "declared import only")
    name = "context_primitive_" + name
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    data = (ROOT / path).read_bytes()
    record = next(r for r in records if r["path"] == path)
    need(hashlib.sha256(data).hexdigest() == record["sha256"], "executed source bytes")
    # -B prevents writes but does not itself prevent cached-bytecode reads.
    # Compile the bytes that were authenticated, bypassing every .pyc loader.
    exec(compile(data, str(ROOT / path), "exec"), module.__dict__)
    return module
