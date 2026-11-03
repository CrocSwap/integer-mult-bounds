"""Authenticate the unchanged PR1523 compatibility consumer before loading it."""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/observable-connector-repair"


def check_digest(raw, expected, path):
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("source drift: " + path)


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            check_digest(raw, row["sha256"], row["path"])


def module(name, filename):
    value = types.ModuleType(name)
    value.__file__ = str(filename)
    # Only source-authenticated, repository-owned code is compiled here.
    exec(compile(filename.read_bytes(), str(filename), "exec"), value.__dict__)
    return value


def load_model():
    authenticate()
    return module("observable_original_model", SOURCE / "model.py")


def load_consumer():
    authenticate()
    model = module("observable_original_model", SOURCE / "model.py")
    oracle = module("observable_original_oracle", SOURCE / "oracle.py")
    saved = {name: sys.modules.get(name) for name in ("model", "oracle")}
    previous_path = list(sys.path)
    try:
        sys.modules.update(model=model, oracle=oracle)
        consumer = module("observable_original_verify", SOURCE / "verify.py")
    finally:
        sys.path[:] = previous_path
        for name, previous in saved.items():
            if previous is None:
                del sys.modules[name]
            else:
                sys.modules[name] = previous
    return consumer
