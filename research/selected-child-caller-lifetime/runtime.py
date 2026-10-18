"""Authenticated source loader; adapted from credited PR2821 (Apache-2.0)."""
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
from contextlib import contextmanager
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
SNAPSHOT = "69ee10977b78aacd151042b8be962363e2690a6a019e8e93bedd4b130daa853a"
DEPENDENCIES = "2aece61fca00a10df61b6cb243408d76aca30e0019c8a3720a8d3e05481af0fe"


def need(test, message):
    if not test:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: need(False, "nonfinite JSON"))


def authenticate():
    path = ROOT / "evidence/PR2801-SNAPSHOT.json"
    need(hashlib.sha256(path.read_bytes()).hexdigest() == SNAPSHOT, "snapshot pin")
    snapshot = read_json(path)
    need(snapshot["head"] == "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1", "runtime head")
    need({row["path"] for row in snapshot["files"]} ==
         {str(p.relative_to(ROOT)) for p in (ROOT / "vendor").iterdir()
          if p.is_file() and p.suffix in (".py", ".md")}, "source inventory")
    sources = {}
    for row in snapshot["files"]:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "source Git blob")
        if row["path"].endswith(".py"):
            sources[Path(row["path"]).stem] = data
    return sources


def authenticate_dependencies():
    path = ROOT / "evidence/DEPENDENCIES.json"
    need(hashlib.sha256(path.read_bytes()).hexdigest() == DEPENDENCIES, "dependency manifest pin")
    for row in read_json(path):
        data = (ROOT / row["export"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "dependency source SHA256")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "dependency source Git blob")


class Loader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, sources):
        self.sources = sources

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.sources:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = str(ROOT / "vendor" / (module.__name__ + ".py"))
        exec(compile(self.sources[module.__name__], module.__file__, "exec"), module.__dict__)


@contextmanager
def runtime():
    sources = authenticate()
    saved = {name: sys.modules.pop(name) for name in sources if name in sys.modules}
    loader = Loader(sources)
    sys.meta_path.insert(0, loader)
    try:
        yield SimpleNamespace(**{name: importlib.import_module(name) for name in sources})
    finally:
        sys.meta_path.remove(loader)
        for name in sources:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
