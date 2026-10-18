"""Authenticate physical tape primitives and inherited scalar recipe sources."""
from hashlib import sha256
import importlib.util
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = {
    "pr3091":"745e3dcf93e44d0f6972b50326d6be907fb7dbf80b93dc71bad26df8c40f4fb0",
    "pr3090":"b76cd97a4dbc07aa0662b38b6dda726e0dfe8a231dd103f569559fb962768c20",
}
_temporary = None
_exports = None
_loaded = None


def exports():
    global _temporary,_exports
    if _exports is not None:
        return _exports
    _temporary = tempfile.TemporaryDirectory(prefix="physical-scalar-stream-")
    result = {}
    for name,digest in ARCHIVES.items():
        archive = HERE/"inputs"/(name+".tar")
        if sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError("immutable scalar source archive: "+name)
        destination = Path(_temporary.name)/name
        destination.mkdir()
        with tarfile.open(archive,"r:") as contents:
            seen = set()
            for entry in contents.getmembers():
                path = PurePosixPath(entry.name)
                if path.is_absolute() or ".." in path.parts or entry.name in seen or not (entry.isfile() or entry.isdir()):
                    raise ValueError("regular relative scalar source archive")
                seen.add(entry.name)
            contents.extractall(destination,filter="data")
        result[name] = destination
    _exports = result
    return result


def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def activate():
    global _loaded
    if _loaded is not None:
        return _loaded
    if any(name in sys.modules for name in ("leaf_sources","phase_sources","native_sources","source","words","signed_linear")):
        raise ValueError("cold physical scalar namespace")
    paths = exports()
    leaf = module("leaf_sources",paths["pr3091"]/"leaf_sources.py")
    leaf.ROOT = ROOT
    leaf.activate()
    sys.path.insert(0,str(paths["pr3091"]))
    lower = module("scalar_lower",paths["pr3090"]/"vendor/lowering/lower.py")
    _loaded = lower
    return lower
