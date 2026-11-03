#!/usr/bin/env python3
"""Bounded exact-product reuse for the unchanged PR5267 replay.

This implementation was produced by Nick Petalas. Apache-2.0.
The authenticated executable retains ssafwann's credit and every original check.
"""

from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import sys


SOURCE = "research/schur-nilpotent-extension/verify.py"
SOURCE_SHA256 = "acf0bb1b148b84ed81020eb002431726a6f12185dd051484bb9181ea79110ce6"
CAPACITY = 512
MAX_SOURCE_BYTES = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(path=None):
    """Execute precisely the bytes checked, without writing bytecode or files."""
    if path is None:
        path = Path(__file__).resolve().parents[2] / SOURCE
    with path.open("rb") as stream:
        source = stream.read(MAX_SOURCE_BYTES + 1)
    require(len(source) <= MAX_SOURCE_BYTES, "source capacity")
    require(sha256(source).hexdigest() == SOURCE_SHA256, "source digest")
    namespace = {"__name__": "retained_nilpotent_schur", "__file__": str(path)}
    code = compile(source, str(path), "exec", dont_inherit=True)
    exec(code, namespace)  # The digest fixes this single executable target.
    require(callable(namespace.get("mul")) and callable(namespace.get("main")),
            "retained entry points")
    return namespace


def run(cached=True):
    namespace = load_source()
    original = namespace["mul"]
    product = lru_cache(maxsize=CAPACITY)(original) if cached else original
    namespace["mul"] = product
    try:
        namespace["main"]()
    finally:
        if cached:
            product.cache_clear()


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--uncached"]), "usage: cached.py [--uncached]")
    run(cached=not sys.argv[1:])
