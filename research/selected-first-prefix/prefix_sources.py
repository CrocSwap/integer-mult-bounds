"""Authenticate the frozen scalar engine and its transitive live inputs."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE_SHA = "e91ff34b0ed26de045d67463456d90a4e213321663b6c24c14842fdda983f2a8"
_temporary = _source = None


def activate():
    global _temporary, _source
    if _source is not None:
        return _source
    archive = HERE/"inputs/pr3098.tar"
    if sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError("immutable PR3098 scalar archive")
    _temporary = tempfile.TemporaryDirectory(prefix="selected-first-prefix-")
    _source = Path(_temporary.name)
    with tarfile.open(archive, "r:") as contents:
        seen = set()
        for entry in contents.getmembers():
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts or entry.name in seen or not (entry.isfile() or entry.isdir()):
                raise ValueError("regular relative scalar archive")
            seen.add(entry.name)
        contents.extractall(_source, filter="data")
    sources = json.loads((_source/"SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input" and sha256((ROOT/row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed scalar tape input: "+row["path"])
    if "scalar_sources" in sys.modules:
        raise ValueError("cold selected-prefix namespace")
    spec = importlib.util.spec_from_file_location("scalar_sources", _source/"scalar_sources.py")
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    spec.loader.exec_module(source)
    source.ROOT = ROOT
    source.activate()
    sys.path.insert(0, str(_source))
    return _source
