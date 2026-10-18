"""Load the completed ordinary backend and immutable compact reference."""
from hashlib import sha256
import importlib.util
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = {
    "pr2899": "fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531",
    "pr2250": "f7c4412bed944228e911c370d847d057a68d27b7d80aac86964b396df6a31756",
}
_temporary = None
_loaded = None


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def activate():
    global _temporary, _loaded
    if _loaded is not None:
        return _loaded
    if any(name in sys.modules for name in ("source", "loader", "words", "streams")):
        raise ValueError("cold compact/ordinary namespace")
    _temporary = tempfile.TemporaryDirectory(prefix="physical-compact-")
    paths = {}
    for name, digest in ARCHIVES.items():
        archive = HERE / "inputs" / (name + ".tar")
        if sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError("immutable source archive: " + name)
        destination = Path(_temporary.name) / name
        with tarfile.open(archive, "r:") as contents:
            seen = set()
            for entry in contents.getmembers():
                path = PurePosixPath(entry.name)
                if path.is_absolute() or ".." in path.parts or entry.name in seen or not (entry.isfile() or entry.isdir()):
                    raise ValueError("regular relative source archive")
                seen.add(entry.name)
            contents.extractall(destination, filter="data")
        paths[name] = destination
    source = module("source", paths["pr2899"] / "source.py")
    source.ROOT = ROOT
    source.activate()
    sys.path.insert(0, str(paths["pr2899"]))
    module("streams", paths["pr2250"] / "streams.py")
    reference = module("compact_reference", paths["pr2250"] / "compact.py")
    _loaded = source, reference
    return _loaded
