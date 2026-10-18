"""Authenticate the physical Compact predecessor and its monomial source."""
from hashlib import sha256
import importlib.util
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE_SHA256 = "c76e11cce0696db643715a362631b60fb14f26ba66c1e3bb5b5b0389eb52e95d"
_temporary = None
_loaded = None


def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def activate():
    global _temporary,_loaded
    if _loaded is not None:
        return _loaded
    names = ("native_sources","source","loader","words","compact","compact_engine","streams")
    if any(name in sys.modules for name in names):
        raise ValueError("cold shared physical monomial namespace")
    archive = HERE/"inputs/pr3055.tar"
    if sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("immutable physical Compact source archive")
    _temporary = tempfile.TemporaryDirectory(prefix="physical-monomial-")
    destination = Path(_temporary.name)
    with tarfile.open(archive,"r:") as contents:
        seen = set()
        for entry in contents.getmembers():
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts or entry.name in seen or not (entry.isfile() or entry.isdir()):
                raise ValueError("regular relative source archive")
            seen.add(entry.name)
        contents.extractall(destination,filter="data")
    native = module("native_sources",destination/"native_sources.py")
    native.ROOT = ROOT
    _source,reference = native.activate()
    sys.path.insert(0,str(destination))
    if "compact" in sys.modules:
        raise ValueError("one authenticated compact reference")
    sys.modules["compact"] = reference
    monomial = module("monomial_reference",Path(reference.__file__).with_name("monomial.py"))
    _loaded = native,reference,monomial
    return _loaded
