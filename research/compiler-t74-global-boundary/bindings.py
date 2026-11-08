"""Authenticate source bytes before importing the retained compiler or runtime."""
from contextlib import contextmanager
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPILER = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_tensor_compiler.py"
BACKEND = "research/t74-support-composition"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE/"SOURCES.json").read_text())["files"]
    checked = {}
    for row in rows:
        if row["usage"] == "input":
            path = ROOT/row["path"]
            need(path.is_file() and not path.is_symlink(), "regular pinned source: "+row["path"])
            raw = path.read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "source bytes changed: "+row["path"])
            checked[row["path"]] = row["sha256"]
    return checked


def compiler():
    spec = importlib.util.spec_from_file_location("retained_global_boundary_compiler", ROOT/COMPILER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def runtime():
    """One cold authenticated #3627 cohort per process, as its source requires."""
    need("composed_sources" not in sys.modules, "one physical source cohort")
    old = sys.path[:]
    sys.path.insert(0, str(ROOT/BACKEND))
    try:
        import composed_sources
        with composed_sources.opened() as state:
            yield state
    finally:
        sys.path[:] = old
