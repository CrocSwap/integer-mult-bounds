"""Authenticate the exact padding source and its complete caller export."""

import importlib
import json
import sys
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
NAMES = (
    "PREDECESSOR.json",
    "README.md",
    "padding.py",
    "predecessor.tar.gz",
    "source.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(package=PACKAGE):
    manifest = json.loads((package / "VENDOR.json").read_text())
    require(set(manifest["files"]) == set(NAMES), "exact five-file export")
    root = package / "vendor" / "pr2786"
    require(
        {path.name for path in root.iterdir()} == set(NAMES),
        "no undeclared source or bytecode cache",
    )
    for name in NAMES:
        path, pin = root / name, manifest["files"][name]
        require(path.stat().st_size == pin["size"] <= 200_000, "bounded source file")
        data = path.read_bytes()
        require(sha256(data).hexdigest() == pin["sha256"], "predecessor SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(
            sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
            "predecessor Git blob",
        )
    return root


@contextmanager
def installed(package=PACKAGE):
    root = authenticate(package)
    require(
        not {"source", "padding"}.intersection(sys.modules),
        "no preloaded padding source",
    )
    old_path = list(sys.path)
    old_modules = set(sys.modules)
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    exported = root
    try:
        source = importlib.import_module("source")
        with source.installed() as (_manifest, exported):
            yield exported
    finally:
        sys.path[:] = old_path
        sys.dont_write_bytecode = old_bytecode
        for name in set(sys.modules) - old_modules:
            module_path = Path(
                getattr(sys.modules[name], "__file__", "") or "."
            ).resolve()
            if module_path.is_relative_to(
                package.resolve()
            ) or module_path.is_relative_to(exported):
                sys.modules.pop(name, None)
