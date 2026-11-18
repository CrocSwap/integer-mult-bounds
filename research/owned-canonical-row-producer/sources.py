"""Load only named, byte-pinned predecessor modules. Apache-2.0."""

import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def load(name, relative):
    pins = {row["path"]: row for row in json.loads((PACKAGE / "SOURCE-PINS.json").read_text())}
    path = PACKAGE / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != pins[relative]["sha256"]:
        raise ValueError("retained module hash")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
