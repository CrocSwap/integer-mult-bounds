"""Authenticated shared physical vocabulary for source-complete leaf joins.

Retained computational bodies are unchanged. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
_state = None


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=HERE):
    seen = set()
    for row in json.loads((root/"DEPENDENCIES.json").read_text())["files"]:
        name = PurePosixPath(row["path"])
        need(not name.is_absolute() and ".." not in name.parts and name.parts[0] == "vendor",
             "frozen relative dependency")
        path = root/str(name)
        need(str(name) not in seen and path.is_file() and not path.is_symlink(), "unique regular source")
        seen.add(str(name))
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"] and
             sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
             "authenticated public dependency: "+str(name))
    return len(seen)


def load(name, path):
    need(name not in sys.modules, "cold source namespace: "+name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def activate():
    global _state
    if _state is None:
        authenticate()
        root = HERE/"vendor/atomic"
        discovery = load("move_sources", root/"move_sources.py")
        core = load("public_atomic_move", root/"atomic_move.py")
        common = core.S
        old = root/"vendor/monomial/vendor"
        rows = load("ranked_leaf_retained_rows", old/"binding/vendor/dispatch/row_programs.py")
        ir = load("ranked_leaf_source_ir", old/"binding/vendor/lifecycle/source_ir.py")
        clifford = load("ranked_leaf_clifford", old/"selected/clifford_exact.py")
        need(tuple(name for name, _ in rows.SCHEMA) == common.leaf_provider.SCHEMA,
             "one exact current 23-field order")
        _state = SimpleNamespace(core=core, common=common, rows=rows, ir=ir,
                                 clifford=clifford, selected=old/"selected")
    return _state
