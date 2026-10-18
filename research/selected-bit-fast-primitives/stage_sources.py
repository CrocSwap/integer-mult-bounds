"""Authenticate B1 and factor words without shadowing its bootstrap module."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = {
    "pr2899": "fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531",
    "pr2157": "db202c7b91b5b8b9340f96f870d54e275854f0b73839451c7c15bd7895ac3639",
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
    if any(name in sys.modules for name in ("source", "loader", "words", "route_catalog", "qadic_streams")):
        raise ValueError("cold shared stage namespace")
    _temporary = tempfile.TemporaryDirectory(prefix="fast-bit-primitives-")
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
    module("qadic_streams", paths["pr2157"] / "qadic_streams.py")
    catalog = module("route_catalog", paths["pr2157"] / "route_catalog.py")
    data = {}
    manifest = json.loads((paths["pr2157"] / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        body = (ROOT / row["path"]).read_bytes()
        if sha256(body).hexdigest() != row["sha256"]:
            raise ValueError("retained factor input changed: " + row["path"])
        data[row["path"]] = body
    _loaded = source, catalog, data
    return _loaded
