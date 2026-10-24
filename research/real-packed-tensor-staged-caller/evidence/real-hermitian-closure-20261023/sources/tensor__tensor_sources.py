"""Authenticate the complete expansion cohort and adjacent headroom proof."""
from contextlib import contextmanager
import gzip
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
EXPANSION_PACKAGE = "research/physical-gaussian-expansion"
EXPANSION_HEAD = "1a86a8fb73bb7a0982fff99852a031832c191902"
COMPRESSED_DIGEST = "05146ca4feabe3dde0ab57aaea3eff9f218933562ba5b5c80bb256a247c144c7"
EXPANSION_DIGEST = "898dd6c8c1e53df8a1040918797b63128fc1d744f234d1f1e623b5acc85f198c"
EXPANSION_RECEIPT = "07ab9b5eec58f812793495ad76b6cede6a7e9912aeb3b53df3b82ec8bd08827d"
HEADROOM_HEAD = "5e7bdfa3c53bbb5a8d6e81f0efe7005c89184e6a"
HEADROOM_DIGEST = "49fd9c1d28809795d109003b4af8d667e22bbc950a75820cf7fb9986d8ac74c6"
CHIRP_PACKAGE = "research/physical-chirp-middle"
CHIRP_HEAD = "6bb7dfdae182a69f7c8836a9ec1be0b2b747e124"
CHIRP_COMPRESSED_DIGEST = "931ed8c764ea6cc592cb59ae93f8284184139a4d174752fb80f7a42762b2c0ad"
CHIRP_DIGEST = "e769b750eb650c4b2f7822a6e4780aa1b360c207ff9a724caa6dd2555ab3f54f"
CHIRP_RECEIPT = "dca075b93c723087c167f01c1074031eeeed2d09d9eeb877481b735a0cecb495"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    value = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def regular(item):
    path = PurePosixPath(item.name)
    require((item.isfile() or item.isdir()) and not path.is_absolute()
            and ".." not in path.parts and "\\" not in item.name
            and path.as_posix() == item.name and item.size <= 2**27,
            "bounded regular tensor source member")


def authenticate_export(path, expected_digest, expected_head, expected_package, expected_receipt, total):
    require(digest(path) == expected_digest, "complete uncompressed tensor dependency export")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [item.name for item in members]
        require(len(names) == len(set(names)) == total, "complete unique tensor dependency inventory")
        for item in members:
            regular(item)
            require(item.isfile(), "regular expansion export member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == expected_receipt, "pinned complete tensor dependency receipt")
        receipt = json.loads(raw)
        require((receipt["commit"], receipt["package"], len(receipt["files"]))
                == (expected_head, expected_package, total-1), "tensor dependency source identity")
        require(set(names) == {row["path"] for row in receipt["files"]} | {".research-export.json"},
                "exact expansion source member set")
        for row in receipt["files"]:
            raw = archive.extractfile(row["path"]).read()
            require(len(raw) == row["size"] and sha256(raw).hexdigest() == row["sha256"],
                    "expansion source member: " + row["path"])


def authenticate_expansion(path):
    authenticate_export(path, EXPANSION_DIGEST, EXPANSION_HEAD, EXPANSION_PACKAGE, EXPANSION_RECEIPT, 37)


def authenticate_chirp(path):
    authenticate_export(path, CHIRP_DIGEST, CHIRP_HEAD, CHIRP_PACKAGE, CHIRP_RECEIPT, 30)


@contextmanager
def bind_chirp(package, state):
    """Bind unchanged chirp modules to their byte-identical, already open ring."""
    require("chirp_sources" not in sys.modules, "one tensor chirp loader")
    spec = importlib.util.spec_from_file_location("chirp_sources", package / "chirp_sources.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["chirp_sources"] = module
    try:
        spec.loader.exec_module(module)
        path = module.authenticate()
        # The two complete exports retain the same corrected ring. Compare
        # every ring-package byte before sharing its already loaded Tape types.
        with tarfile.open(path, "r:") as archive:
            prefix = module.PACKAGE + "/"
            for member in archive.getmembers():
                if member.name.startswith(prefix):
                    relative = member.name[len(prefix):]
                    require((state.ring_package / relative).read_bytes() == archive.extractfile(member).read(),
                            "identical shared ring dependency: " + relative)
        require(module._active is None, "unbound authenticated chirp loader")
        state.convolution = importlib.import_module("convolution_engine")
        require(Path(state.convolution.__file__).resolve() == (state.ring_package / "convolution_engine.py").resolve(),
                "actual shared ring convolution module")
        # This context adapter supplies the original loader's state token.
        # It changes no function, arithmetic owner, coefficient or code bytes.
        module._active = state
        state.chirp_package = package
        sys.path.insert(0, str(package))
        try:
            yield module
        finally:
            module._active = None
            sys.path.remove(str(package))
    finally:
        if sys.modules.get("chirp_sources") is module:
            del sys.modules["chirp_sources"]


def authenticate_headroom(path):
    require(path.is_file() and not path.is_symlink() and digest(path) == HEADROOM_DIGEST,
            "pinned Gaussian headroom source")
    with tarfile.open(path, "r:") as archive:
        require(archive.pax_headers.get("comment") == HEADROOM_HEAD, "exact headroom proof commit")
        members = archive.getmembers()
        require(len({item.name for item in members}) == len(members), "unique headroom source members")
        files = [item for item in members if item.isfile()]
        require(len(files) == 19 and {"LICENSE", "NOTICE"} <= {item.name for item in files},
                "complete headroom package and source notices")
        for item in members:
            regular(item)
            require(item.name in ("LICENSE", "NOTICE", "research", "research/gaussian-expansion-headroom")
                    or item.name.startswith("research/gaussian-expansion-headroom/"), "headroom source root")


def active():
    require(_active is not None, "authenticated tensor physical cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "expansion_sources" not in sys.modules
            and "cardinal_counts" not in sys.modules, "cold tensor namespace")
    compressed = HERE / "inputs/expansion-export.tar.gz"
    require(compressed.is_file() and not compressed.is_symlink()
            and digest(compressed) == COMPRESSED_DIGEST, "pinned compressed expansion source")
    headroom = HERE / "inputs/headroom-source.tar"
    authenticate_headroom(headroom)
    chirp_compressed = HERE / "inputs/chirp-export.tar.gz"
    require(chirp_compressed.is_file() and not chirp_compressed.is_symlink()
            and digest(chirp_compressed) == CHIRP_COMPRESSED_DIGEST, "pinned compressed chirp source")
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="gaussian-tensor-source-") as directory:
        root = Path(directory)
        source_tar = root / "expansion.tar"
        with gzip.open(compressed, "rb") as source, source_tar.open("xb") as target:
            shutil.copyfileobj(source, target, 65536)
        require(source_tar.stat().st_size <= 2**27, "bounded decompressed expansion source")
        authenticate_expansion(source_tar)
        chirp_tar = root / "chirp.tar"
        with gzip.open(chirp_compressed, "rb") as source, chirp_tar.open("xb") as target:
            shutil.copyfileobj(source, target, 65536)
        require(chirp_tar.stat().st_size <= 2**27, "bounded decompressed chirp source")
        authenticate_chirp(chirp_tar)
        expansion_root, headroom_root, chirp_root = root / "expansion", root / "headroom", root / "chirp"
        expansion_root.mkdir()
        headroom_root.mkdir()
        chirp_root.mkdir()
        for path, target in ((source_tar, expansion_root), (headroom, headroom_root), (chirp_tar, chirp_root)):
            with tarfile.open(path, "r:") as archive:
                archive.extractall(target, filter="data")
        package = expansion_root / EXPANSION_PACKAGE
        spec = importlib.util.spec_from_file_location("expansion_sources", package / "expansion_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["expansion_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.expansion_package = package
                state.headroom_package = headroom_root / "research/gaussian-expansion-headroom"
                with bind_chirp(chirp_root / CHIRP_PACKAGE, state):
                    yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("expansion_sources") is source:
                del sys.modules["expansion_sources"]
