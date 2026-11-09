"""Authenticated immutable source and exact current local SCALE registration.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types
from fractions import Fraction

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((ROOT / "DEPENDENCIES.json").read_bytes())["files"]
    need(len(rows) == 6, "six frozen dependencies")
    for row in rows:
        p = ROOT / row["local_path"]
        need(p.resolve().is_relative_to(ROOT), "local dependency")
        data = p.read_bytes()
        need(len(data) == row["bytes"], "source length")
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA-256")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "source Git blob")
    return len(rows)


def vendor(name, path):
    authenticate()
    p = ROOT / path
    mod = types.ModuleType(name); mod.__file__ = str(p); sys.modules[name] = mod
    exec(compile(p.read_bytes(), str(p), "exec"), mod.__dict__)
    return mod


def word():
    authenticate()
    w = json.loads(gzip.decompress((ROOT / "data/word.json.gz").read_bytes()))
    need(w["public"] == 1461 and len(w["program"]) == 71144, "exact source word")
    return w


def current_scales():
    w = word()
    return [(i, tuple(e), Fraction(e[2])) for i, e in enumerate(w["program"]) if e[0] == "SCALE"]


def bind_scales():
    """Actual unchanged local SERVICE token grammar, no invented opcode.

    This returns a finite token/table registry for the current local SCALE
    class. It does not install an entire current caller/recursive exporter.
    """
    from tables import compile_rounded
    cache, registry, rows = {}, {}, []
    for pc, raw, q in current_scales():
        if q not in cache:
            cache[q] = compile_rounded("SCALE", q)
        token = ("local", pc, raw)
        registry[token] = cache[q][0]
        rows.append(dict(pc=pc, raw=list(raw), coefficient=str(q), field=raw[1]))
    need(len(rows) == 3660 and len(cache) == 52, "current SCALE occurrence/coefficient census")
    need(("local",37480,("SCALE",697,"-2/3",591)) in registry, "actual exposed arithmetic seam")
    return registry, cache, rows
