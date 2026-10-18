#!/usr/bin/env python3
"""Authenticated PR2697 source loader. Reused from Ross Richardson PR2874 (08dd02bd); Apache-2.0."""
from __future__ import annotations
import ast
import hashlib
import importlib.abc
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
PIN = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
MANIFEST_SHA256 = "a9f623f4971232daccb39091b51294d9cd09fe07af054184edc4f3bd7a51008e"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def check_receipt(expected,actual):
    require(json.dumps(expected,sort_keys=True)==json.dumps(actual,sort_keys=True),
            "exact typed deterministic receipt")


def authenticate(root=ROOT, expected=MANIFEST_SHA256):
    raw = (root / "SNAPSHOTS.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected, "manifest digest")
    manifest = json.loads(raw)
    require(manifest["source_head"] == PIN, "source head")
    code = {}
    for item in manifest["files"]:
        path = Path(item["path"])
        require(not path.is_absolute() and ".." not in path.parts, "local source path")
        data = (root / path).read_bytes()
        require(item["commit"] == PIN, "source commit")
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source digest")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["blob"], "source Git blob")
        if path.suffix == ".py":
            require(path.stem not in code, "unique module")
            code[path.stem] = (str(root / path), data)
    return code


class Frozen(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, code):
        self.code = code

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.code:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        filename, data = self.code[module.__name__]
        module.__file__ = filename
        exec(compile(data, filename, "exec"), module.__dict__)


def load_runtime():
    code = authenticate()
    require(not (set(code) & set(sys.modules)), "source module already loaded")
    sys.meta_path.insert(0, Frozen(code))
    import directory, packet, records, words, counts
    return SimpleNamespace(directory=directory, packet=packet, records=records,
                           words=words, counts=counts, code=code)
