"""Frozen unchanged current monomial and literal descriptor tables.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import sys

HERE = Path(__file__).resolve().parent
_loaded = None


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=HERE):
    rows = json.loads((root / "DEPENDENCIES.json").read_text())["files"]
    seen = set()
    for row in rows:
        path = PurePosixPath(row["path"])
        need(not path.is_absolute() and ".." not in path.parts
             and path.parts[0] == "vendor" and str(path) not in seen,
             "unique relative frozen source")
        seen.add(str(path))
        target = root / str(path)
        need(target.is_file() and not target.is_symlink(), "regular frozen source")
        raw = target.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"]
             and sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "authenticated source " + str(path))
    return len(rows)


def load(name, path):
    need(name not in sys.modules, "cold source namespace " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def activate():
    global _loaded
    if _loaded is not None:
        return _loaded
    authenticate()
    phase = HERE / "vendor/monomial"
    sys.path.insert(0, str(phase))
    binding = load("phase_binding", phase / "phase_binding.py")
    state = binding.activate()
    adapter = load("phase_adapter", phase / "phase_adapter.py")
    selected = load("selected_service", phase / "selected_service.py")
    dispatch = phase / "vendor/binding/vendor/dispatch"
    rows = load("serial_monomial_retained_rows", dispatch / "row_programs.py")
    _loaded = SimpleNamespace(binding=binding, state=state, adapter=adapter,
                              selected=selected, rows=rows, phase=phase,
                              abi=state.abi, codec=state.codec)
    return _loaded
