"""Authenticate and open exact, unmodified source cohorts at their own paths.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Mirrors contain hard links to authenticated read-only inputs, never patched code.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    need(name not in sys.modules, "cold remaining-diagonal source alias: " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def authenticate():
    files = json.loads((HERE / "SOURCES.json").read_text())["files"]
    retained = json.loads((HERE / "DEPENDENCIES.json").read_text())["files"]
    checked = {}
    for row in files + retained:
        key = row.get("retained_path", row.get("path"))
        path = HERE / key if "retained_path" in row else ROOT / key
        need(path.is_file() and not path.is_symlink(), "regular authenticated input: " + key)
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"] and
             sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "exact remaining-diagonal input: " + key)
        checked[key] = row["sha256"]
    return checked


@contextmanager
def references():
    authenticate()
    names = ("exact", "engine", "triangular", "generator", "full", "gaussian", "gaussian_reference")
    modules = {}
    try:
        for name in names:
            modules[name] = load(name, ROOT / "research/rational-unitary-fft" / (name + ".py"))
        yield modules["gaussian_reference"], {
            "research/certified-gaussian-recovery/intervals.py":
            (ROOT / "research/certified-gaussian-recovery/intervals.py").read_bytes()
        }
    finally:
        for name, module in modules.items():
            if sys.modules.get(name) is module:
                del sys.modules[name]


@contextmanager
def native():
    """Preserve original relative paths and original authentication/ROOT logic."""
    authenticate()
    with tempfile.TemporaryDirectory(prefix="remaining-diagonal-sources-") as directory:
        mirror = Path(directory)
        for row in json.loads((HERE / "retained/fft/SOURCES.json").read_text())["files"]:
            if row["usage"] == "input":
                destination = mirror / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.link(ROOT / row["path"], destination)
        package = mirror / "research/full-fft-scalar-join"
        for path in sorted((HERE / "retained/fft").rglob("*")):
            if path.is_file():
                destination = package / path.relative_to(HERE / "retained/fft")
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.link(path, destination)
        name = "remaining_exact_fft_sources"
        module = load(name, package / "join_sources.py")
        try:
            yield module
        finally:
            sys.modules.pop(name, None)


def bridge():
    return (load("remaining_external_tapes", HERE / "retained/bridge/tapes.py"),
            load("remaining_exact_codec", HERE / "retained/bridge/boundary_codec.py"))
