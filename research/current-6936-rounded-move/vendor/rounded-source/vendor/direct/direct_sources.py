"""One authenticated physical vocabulary for serial / positive-leaf composition.

Only source discovery is shared; all retained computational bytes are intact.
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
    for row in json.loads((root/"DEPENDENCIES.json").read_text())["files"]:
        path = PurePosixPath(row["path"])
        need(not path.is_absolute() and ".." not in path.parts and path.parts[0] == "vendor",
             "relative retained public source")
        target = root/str(path)
        need(str(path) not in seen and target.is_file() and not target.is_symlink(), "unique regular source")
        seen.add(str(path)); data = target.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"] and
             sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
             "exact public dependency: "+str(path))
    for row in json.loads((root/"SHARED-SOURCE-JOIN.json").read_text())["files"]:
        data = (root/row["shared_path"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"] and
             sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
             "identical shared serial dependency: "+row["serial_path"])
    return len(seen)


def load(name, path):
    need(name not in sys.modules, "cold source module: "+name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def activate():
    global _state
    if _state is None:
        authenticate()
        leaf_root = HERE/"vendor/leaf"
        sys.path.insert(0, str(leaf_root))
        discovery = load("all_leaf_sources", leaf_root/"all_leaf_sources.py")
        leaf = discovery.activate()
        leaf_view = load("leaf_view", leaf_root/"leaf_view.py")
        catalog = load("source_catalog", leaf_root/"source_catalog.py")
        # The serial dependency receipt proves every original runtime source
        # byte equals the one already activated above. A discovery-only shim
        # therefore supplies the same physical Count/Tape/codec/row objects.
        serial_state = SimpleNamespace(adapter=leaf.common.monomial,
            state=leaf.common.shared, rows=leaf.rows, abi=leaf.common.abi,
            codec=leaf.common.codec, selected=leaf.common.selected)
        shim = ModuleType("serial_sources")
        shim.activate = lambda: serial_state
        shim.need = need
        need("serial_sources" not in sys.modules, "cold serial discovery name")
        sys.modules["serial_sources"] = shim
        serial = load("direct_serial_column_view", HERE/"vendor/serial/column_view.py")
        need(serial.S.adapter is leaf.common.monomial and serial.S.rows is leaf.rows
             and serial.S.abi is leaf.common.abi,
             "one unchanged monomial, literal row and current coded vocabulary")
        _state = SimpleNamespace(leaf=leaf, child=leaf_view.PositiveChild,
            catalog=catalog, serial=serial.SerialProvider, abi=leaf.common.abi,
            common=leaf.common, atomic=leaf.core.AtomicMove)
    return _state
