"""Authenticate and load the unchanged comparison and its semantic backend.

No archive Python is used by direct.py. This loader supplies the credited
compiler/backend and the differential reference only. Apache-2.0.
"""
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_loaded = None
_temporary = None


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_members(archive=None):
    metadata = json.loads((HERE / "PREDECESSOR.json").read_text())
    archive = HERE / "inputs/pr3131.tar" if archive is None else Path(archive)
    need(sha256(archive.read_bytes()).hexdigest() == metadata["archive_sha256"], "frozen PR3131 archive")
    expected = {row["name"]: row for row in metadata["members"]}
    result = {}
    with tarfile.open(archive, "r:") as contents:
        for member in contents.getmembers():
            if member.isdir():
                continue
            need(member.isfile() and member.name in expected and member.name not in result, "archive member inventory")
            data = contents.extractfile(member).read()
            row = expected[member.name]
            need(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"], "archive member hash")
            need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"], "archive Git blob")
            result[member.name] = data
    need(set(result) == set(expected), "complete archive inventory")
    return result


def load():
    global _loaded, _temporary
    if _loaded is not None:
        return _loaded
    raw = authenticated_members()
    # Compile authenticated bytes directly. No cached .pyc or archive extraction.
    _temporary = tempfile.TemporaryDirectory(prefix="guarded-wrapper-")
    folder = Path(_temporary.name)
    (folder / "inputs").mkdir()
    (folder / "inputs/pr3109.tar").write_bytes(raw["inputs/pr3109.tar"])
    source = ModuleType("sources")
    source.__file__ = str(folder / "sources.py")
    exec(compile(raw["sources.py"], source.__file__, "exec"), source.__dict__)
    source.ROOT = ROOT  # Only relocate the frozen loader's repository root.
    previous = sys.modules.get("sources")
    sys.modules["sources"] = source
    try:
        model = ModuleType("credited_dense_collector")
        model.__file__ = str(folder / "model.py")
        exec(compile(raw["model.py"], model.__file__, "exec"), model.__dict__)
    finally:
        if previous is None:
            del sys.modules["sources"]
        else:
            sys.modules["sources"] = previous
    _loaded = model
    return model
