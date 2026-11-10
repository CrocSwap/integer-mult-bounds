"""One authenticated source vocabulary for the published two service joins.

Only discovery is shared. Retained computational bodies are byte-identical.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from types import ModuleType, SimpleNamespace

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
             "regular relative retained source")
        file = root / str(name)
        need(str(name) not in seen and file.is_file() and not file.is_symlink(), "unique frozen source")
        seen.add(str(name))
        data = file.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"]
             and sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"],
             "authenticated published bytes: " + str(name))
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
    mono = HERE / "vendor/monomial"
    binding = load("phase_binding", mono / "phase_binding.py")
    shared = binding.activate()
    monomial = load("phase_adapter", mono / "phase_adapter.py")
    leaf = SimpleNamespace(base=shared.source, codec=shared.codec,
                           header=shared.provider, abi=shared.abi)
    shim = ModuleType("leaf_sources")
    shim.activate = lambda: leaf
    shim.need = need
    need("leaf_sources" not in sys.modules, "cold leaf discovery namespace")
    sys.modules["leaf_sources"] = shim
    kernels = HERE / "vendor/leaf/vendor/leaf"
    leaf.linear = load("signed_linear", kernels / "signed_linear.py")
    leaf.axis = load("axis_stream", kernels / "axis_stream.py")
    leaf.coefficient = load("coefficient_engine", kernels / "coefficient_engine.py")
    leaf_provider = load("leaf_provider", HERE / "vendor/leaf/leaf_provider.py")
    source = load("selected_service", mono / "selected_service.py")
    need(shared.engine.Count is leaf.coefficient.Count is shared.source.counts.Count
         and shared.engine.Tape is leaf.coefficient.Tape is shared.source.records.Tape
         and monomial.SCHEMA == leaf_provider.SCHEMA,
         "one unchanged Count/Tape/header vocabulary across all factors")
    _state = SimpleNamespace(shared=shared, monomial=monomial, leaf=leaf,
                             leaf_provider=leaf_provider, selected=source,
                             abi=shared.abi, codec=shared.codec)
    return _state
