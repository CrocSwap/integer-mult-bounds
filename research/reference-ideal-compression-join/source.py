"""Exact canonical Reference/for_cap cohort, with no projected source bodies.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    for row in rows:
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular canonical source input")
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"] and
             sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "unchanged ideal-compression source: " + row["path"])
    retained = json.loads((HERE / "DEPENDENCIES.json").read_text())["files"]
    for row in retained:
        raw = (ROOT / row["path"]).read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"] and
             sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
             "unchanged public dependency: " + row["path"])
    return len(rows), len(retained)


@contextmanager
def opened():
    authenticate()
    names = ("exact", "engine", "triangular", "generator", "full", "gaussian", "gaussian_reference")
    need(not any(name in sys.modules for name in names), "cold actual Gaussian source cohort")
    modules = {}
    try:
        for name in names:
            spec = importlib.util.spec_from_file_location(name,
                ROOT / "research/rational-unitary-fft" / (name + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = modules[name] = module
            spec.loader.exec_module(module)
        raw = {path: (ROOT / path).read_bytes() for path in
               (modules["gaussian"].INTERVALS, modules["gaussian"].EVALUATOR)}
        yield modules["gaussian_reference"], raw
    finally:
        for name, module in modules.items():
            if sys.modules.get(name) is module:
                del sys.modules[name]
