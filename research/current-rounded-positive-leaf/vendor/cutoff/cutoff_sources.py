"""Authenticate the exact public positive-child package before source reuse.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
_state = None


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=HERE):
    seen = set()
    for row in json.loads((root/"DEPENDENCIES.json").read_text())["files"]:
        name = PurePosixPath(row["path"])
        need(not name.is_absolute() and ".." not in name.parts and name.parts[0] == "vendor",
             "relative retained source")
        file = root/str(name)
        need(str(name) not in seen and file.is_file() and not file.is_symlink(), "unique regular retained source")
        seen.add(str(name)); data=file.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"]
             and sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"],
             "unchanged public cutoff dependency: "+str(name))
    return len(seen)


def load(name, path):
    need(name not in sys.modules, "cold cutoff source namespace: "+name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),"exec"),module.__dict__)
    return module


def activate():
    global _state
    if _state is None:
        authenticate(); root=HERE/"vendor/leaf"
        sys.path.insert(0,str(root))
        discovery=load("all_leaf_sources",root/"all_leaf_sources.py")
        inherited=discovery.activate()
        view=load("leaf_view",root/"leaf_view.py")
        catalog=load("source_catalog",root/"source_catalog.py")
        selected=load("selected_leaf",root/"selected_leaf.py")
        _state=SimpleNamespace(old=inherited,rows=inherited.rows,common=inherited.common,
                               view=view,catalog=catalog,selected=selected,root=root)
    return _state
