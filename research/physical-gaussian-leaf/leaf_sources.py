"""Authenticate the completed Gaussian monomial and its physical tape sources."""
from hashlib import sha256
import importlib.util
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE_SHA256 = "d7e9c04a5e6d3f76158555d84080786c7cd8028ca31a61c9399de2b2c67bfd53"
_temporary = None
_loaded = None


def activate():
    global _temporary,_loaded
    if _loaded is not None:
        return _loaded
    if any(name in sys.modules for name in ("phase_sources","native_sources","source","words","monomial_engine")):
        raise ValueError("cold physical Gaussian coefficient namespace")
    archive = HERE/"inputs/pr3087.tar"
    if sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("immutable Gaussian monomial source archive")
    _temporary = tempfile.TemporaryDirectory(prefix="physical-gaussian-leaf-")
    destination = Path(_temporary.name)
    with tarfile.open(archive,"r:") as contents:
        seen = set()
        for entry in contents.getmembers():
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts or entry.name in seen or not (entry.isfile() or entry.isdir()):
                raise ValueError("regular relative coefficient source archive")
            seen.add(entry.name)
        contents.extractall(destination,filter="data")
    spec = importlib.util.spec_from_file_location("phase_sources",destination/"phase_sources.py")
    phase = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = phase
    spec.loader.exec_module(phase)
    phase.ROOT = ROOT
    phase.activate()
    sys.path.insert(0,str(destination))
    _loaded = phase
    return phase
