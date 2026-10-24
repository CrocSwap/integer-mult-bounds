"""Open the corrected normalized product and its single physical cohort."""
from contextlib import contextmanager
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = "research/physical-ring-product"
HEAD = "62264289adb01f3ba4930cd0154c75887f96203c"
DIGEST = "c03d4b056ccd3db860c93579f6525e0bb1baea31cff879eb07135c99432ef159"
MANIFEST = "39c6eb4f1c2d38fdf8e44ae5c6b16bfe5315ff796ac60f1f6e48161ad3e2bab4"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(path=None):
    path = HERE / "inputs/ring-export.tar" if path is None else Path(path)
    require(path.is_file() and not path.is_symlink(), "regular FFT-word source export")
    require(sha256(path.read_bytes()).hexdigest() == DIGEST, "pinned FFT-word source bytes")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [item.name for item in members]
        require(len(names) == 27 and len(set(names)) == 27, "complete unique FFT-word source export")
        for item in members:
            part = PurePosixPath(item.name)
            require(item.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in item.name and part.as_posix() == item.name
                    and item.size <= 2**27, "bounded regular FFT-word source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == MANIFEST, "pinned FFT-word source receipt")
        receipt = json.loads(raw)
        require((receipt["commit"], receipt["package"], len(receipt["files"]))
                == (HEAD, PACKAGE, 26), "FFT-word source identity")
        require(set(names) == {row["path"] for row in receipt["files"]} | {".research-export.json"},
                "exact FFT-word source member set")
        for row in receipt["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "FFT-word source member: " + row["path"])
    return path


def active():
    require(_active is not None, "authenticated FFT-word cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "ring_sources" not in sys.modules, "cold FFT-word namespace")
    path = authenticate()
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="fft-word-source-") as directory:
        with tarfile.open(path, "r:") as archive:
            archive.extractall(directory, filter="data")
        package = Path(directory) / PACKAGE
        spec = importlib.util.spec_from_file_location("ring_sources", package / "ring_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["ring_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.ring_package = package
                state.ring = importlib.import_module("ring_engine")
                require(Path(state.ring.__file__).resolve() == (package / "ring_engine.py").resolve(),
                        "actual authenticated normalized-product code")
                yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("ring_sources") is source:
                del sys.modules["ring_sources"]
