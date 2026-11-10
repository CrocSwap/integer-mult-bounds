"""Authenticate unchanged source archives and load one shared tape vocabulary."""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import importlib.util
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = {
    "pr2809": "ee1d4ec05e3c872d264be3b38f71a8c153acf37427f5d3ba87f8e15440c9ccf0",
    "pr2808": "2ab59c6d0ad00c001ecbe44090b66871ec3d2c1fdc51daa503109e56f3285cab",
}
_temporary = None
_loaded = None
PROOF_INPUTS = {
    "research/bit2234-stock-threshold/README.md":
        "1e050c9f963421d751d9208092f9a15321ed77810e03912df8eb5eb56bbb06e7",
}


def extract(name, destination):
    archive = HERE / "inputs" / (name + ".tar")
    if sha256(archive.read_bytes()).hexdigest() != ARCHIVES[name]:
        raise ValueError("unchanged source archive: " + name)
    with tarfile.open(archive, "r:") as source:
        names = set()
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or member.name in names
                    or not (member.isfile() or member.isdir())):
                raise ValueError("regular relative source inventory")
            names.add(member.name)
        source.extractall(destination, filter="data")


def activate():
    global _temporary, _loaded
    if _loaded is not None:
        return _loaded
    names = ("loader", "words", "records", "catalogue", "controller", "numeric",
             "macro_machine", "macro_code", "scheduler", "cardinal_counts", "padding", "outer")
    if any(name in sys.modules for name in names):
        raise ValueError("cold shared predecessor namespace")
    for name, digest in PROOF_INPUTS.items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError("pinned stock proof changed: " + name)
    _temporary = tempfile.TemporaryDirectory(prefix="ordinary-physical-")
    root = Path(_temporary.name)
    for name in ARCHIVES:
        extract(name, root / name)
    specification = importlib.util.spec_from_file_location("loader", root / "pr2809/loader.py")
    loader = importlib.util.module_from_spec(specification)
    sys.modules["loader"] = loader
    specification.loader.exec_module(loader)
    loader.REPOSITORY = ROOT
    loader.activate()
    padding = loader.module("padding", root / "pr2808/vendor/pr2786/padding.py")
    outer = loader.module("outer", root / "pr2808/outer.py")
    _loaded = loader, padding, outer
    return _loaded
