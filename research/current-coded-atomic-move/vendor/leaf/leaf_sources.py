"""Authenticate unchanged #3091 and the published current physical vocabulary.

Only host-side archive discovery changes. Computational source bytes are frozen.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
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
    for row in json.loads((root / "DEPENDENCIES.json").read_text())["files"]:
        name = PurePosixPath(row["path"])
        need(not name.is_absolute() and ".." not in name.parts and name.parts[0] == "vendor",
             "relative retained computational source")
        file = root / str(name)
        need(str(name) not in seen and file.is_file() and not file.is_symlink(), "unique regular source")
        seen.add(str(name))
        raw = file.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"]
             and sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "unchanged computational source: " + str(name))
    return len(seen)


def load(name, path):
    need(name not in sys.modules, "cold source module: " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), "exec"), module.__dict__)
    return module


def activate():
    global _state
    if _state is not None:
        return _state
    authenticate()
    binding = HERE / "vendor/binding"
    sys.path.insert(0, str(binding))
    base = load("binding_sources", binding / "binding_sources.py").activate()
    codec = load("codec", binding / "codec.py")
    provider = load("retained_current_header", binding / "provider.py")
    _state = SimpleNamespace(base=base, codec=codec, header=provider, abi=base.abi)
    sys.path.insert(0, str(HERE / "vendor/leaf"))
    # Retained imports of leaf_sources resolve here.  No retained arithmetic
    # body is changed and no ordinary supplier is constructed or invoked.
    _state.linear = load("signed_linear", HERE / "vendor/leaf/signed_linear.py")
    _state.axis = load("axis_stream", HERE / "vendor/leaf/axis_stream.py")
    _state.coefficient = load("coefficient_engine", HERE / "vendor/leaf/coefficient_engine.py")
    need(_state.coefficient.Count is base.counts.Count
         and _state.coefficient.Tape is base.records.Tape
         and _state.axis.Count is base.counts.Count,
         "one actual Count/Tape vocabulary")
    return _state
