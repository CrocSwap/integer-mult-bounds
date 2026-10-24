"""Authenticate the word runtime and the branch-free Gaussian reference."""
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
PACKAGE = "research/physical-fft-word"
HEAD = "9b5474f47b0ea9a3c76bb5b1b577fb36704815e0"
DIGEST = "d428e8b6aef4d348fa2e922ca64c4cfd634bbb2f0c150033273e65fcf4600b49"
MANIFEST = "237ccd34aadda692f73b85277816b76168acaecfe06a12996cce37a7f0925cbc"
REFERENCE_HEAD = "8922e3b3f0fd7772b0fb42028eb2532984c3ab42"
REFERENCE_DIGEST = "e6cdacd59a067189a99bfe03f4448913bb8d518ed4a9b1d981a68c5c666529c7"
REFERENCE_PACKAGE = "research/branchfree-gaussian-inverse"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_member(item):
    part = PurePosixPath(item.name)
    require((item.isfile() or item.isdir()) and not part.is_absolute()
            and ".." not in part.parts and "\\" not in item.name
            and part.as_posix() == item.name and item.size <= 2**27,
            "bounded regular Gaussian source member")


def authenticate():
    path = HERE / "inputs/word-export.tar"
    require(path.is_file() and not path.is_symlink(), "regular Gaussian word source")
    require(sha256(path.read_bytes()).hexdigest() == DIGEST, "pinned Gaussian word source")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [item.name for item in members]
        require(len(names) == len(set(names)) == 22, "complete Gaussian word export")
        for item in members:
            safe_member(item)
            require(item.isfile(), "regular Gaussian word export file")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == MANIFEST, "pinned Gaussian word receipt")
        receipt = json.loads(raw)
        require((receipt["commit"], receipt["package"], len(receipt["files"]))
                == (HEAD, PACKAGE, 21), "Gaussian word source identity")
        require(set(names) == {row["path"] for row in receipt["files"]} | {".research-export.json"},
                "exact Gaussian word source inventory")
        for row in receipt["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "Gaussian word source member: " + row["path"])
    reference = HERE / "inputs/branchfree-source.tar"
    require(reference.is_file() and not reference.is_symlink()
            and sha256(reference.read_bytes()).hexdigest() == REFERENCE_DIGEST,
            "pinned Chafik branch-free source")
    with tarfile.open(reference, "r:") as archive:
        require(archive.pax_headers.get("comment") == REFERENCE_HEAD, "exact branch-free reference commit")
        members = archive.getmembers()
        require(len({item.name for item in members}) == len(members), "unique Gaussian reference members")
        expected = {REFERENCE_PACKAGE + "/" + name for name in (
            "EXPECTED.json", "MANIFEST.json", "PROOF.md", "README.md", "SOURCE.json",
            "code/branchfree.py", "code/check.py", "code/precision_guard.py", "verify.py")}
        require({item.name for item in members if item.isfile()} == expected,
                "complete Chafik branch-free package")
        for item in members:
            safe_member(item)
            require(item.name == "research" or item.name == REFERENCE_PACKAGE
                    or item.name.startswith(REFERENCE_PACKAGE + "/"), "Gaussian reference root")
    return path, reference


def active():
    require(_active is not None, "authenticated Gaussian physical cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "fft_word_sources" not in sys.modules
            and "fft_word_engine" not in sys.modules and "cardinal_counts" not in sys.modules,
            "cold Gaussian namespace")
    path, reference = authenticate()
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="gaussian-core-source-") as directory:
        for source_path in (path, reference):
            with tarfile.open(source_path, "r:") as archive:
                archive.extractall(directory, filter="data")
        package = Path(directory) / PACKAGE
        spec = importlib.util.spec_from_file_location("fft_word_sources", package / "fft_word_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["fft_word_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.word_package = package
                state.word = importlib.import_module("fft_word_engine")
                state.branchfree_package = Path(directory) / REFERENCE_PACKAGE
                require(Path(state.word.__file__).resolve() == (package / "fft_word_engine.py").resolve(),
                        "actual authenticated FFT-word implementation")
                yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("fft_word_sources") is source:
                del sys.modules["fft_word_sources"]
