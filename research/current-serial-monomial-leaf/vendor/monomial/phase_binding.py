"""Authenticate and bind unchanged #3087 to the current physical vocabulary.

Only source discovery is replaced. All phase, signed-pair, monomial, Compact,
Count and Tape computational source bodies remain their pinned bytes.
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
    rows = json.loads((root / "DEPENDENCIES.json").read_text())["files"]
    seen = set()
    for row in rows:
        name = PurePosixPath(row["path"])
        need(not name.is_absolute() and ".." not in name.parts and name.parts[0] == "vendor",
             "regular relative frozen source path")
        path = root / str(name)
        need(str(name) not in seen and path.is_file() and not path.is_symlink(),
             "unique regular frozen source")
        seen.add(str(name))
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"]
             and sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "unchanged source bytes: " + str(name))
    return len(rows)


def load(name, path):
    need(name not in sys.modules, "cold phase source module " + name)
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
    binding, monomial = HERE / "vendor/binding", HERE / "vendor/monomial"
    sys.path.insert(0, str(binding))
    base = load("binding_sources", binding / "binding_sources.py")
    state = base.activate()
    reference = sys.modules["compact_reference"]
    need("compact" not in sys.modules and "phase_sources" not in sys.modules,
         "cold shared monomial source namespace")
    sys.modules["compact"] = reference
    finite = load("monomial_reference", monomial / "reference.py")
    shim = ModuleType("phase_sources")
    shim.activate = lambda: (sys.modules["native_sources"], reference, finite)
    sys.modules["phase_sources"] = shim
    sys.path.insert(0, str(monomial))
    codec = load("codec", binding / "codec.py")
    provider = load("provider", binding / "provider.py")
    phase = load("signed_phase", monomial / "signed_phase.py")
    recipe = load("phase_recipe", monomial / "phase_recipe.py")
    pair = load("pair_dispatch", monomial / "pair_dispatch.py")
    engine = load("monomial_engine", monomial / "monomial_engine.py")
    need(engine.Count is state.counts.Count and engine.Tape is state.records.Tape
         and phase.Count is engine.Count and recipe.Count is engine.Count,
         "one actual Count/Tape vocabulary across the complete monomial")
    _state = SimpleNamespace(source=state, codec=codec, provider=provider,
                             phase=phase, recipe=recipe, engine=engine,
                             reference=finite, pair=pair, abi=state.abi)
    return _state
