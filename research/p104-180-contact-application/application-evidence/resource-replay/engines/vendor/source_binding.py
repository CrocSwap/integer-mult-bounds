"""Authenticate the frozen source capsule; no network or Git is required.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check_dependencies():
    items = json.loads((ROOT / "DEPENDENCIES.json").read_bytes())["files"]
    need(len(items) == 11, "exact eleven-file immutable capsule")
    seen = set()
    for row in items:
        name = row["local_path"]
        path = ROOT / name
        need(name not in seen and path.resolve().is_relative_to(ROOT), "capsule path")
        seen.add(name)
        data = path.read_bytes()
        need(len(data) == row["bytes"], "source length: " + name)
        need(digest(data) == row["sha256"], "source SHA-256: " + name)
        need(blob(data) == row["git_blob"], "source Git blob: " + name)
    return len(items)


def sources():
    check_dependencies()
    caller = json.loads((ROOT / "data/caller.json").read_bytes())
    word = json.loads(gzip.decompress((ROOT / "data/word.json.gz").read_bytes()))
    need(len(caller["events"]) == 3095 and caller["roles"] == 76, "frozen caller shape")
    need(len(word["program"]) == 71144 and word["public"] == 1461, "frozen local word")
    return caller, word


def load_vendor(name, relative):
    """Compile authenticated bytes directly, never a cached .pyc."""
    check_dependencies()
    path = ROOT / relative
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def fraction_string(x):
    return str(Fraction(x))


def strict_power(x):
    """Smallest nonnegative k for which the exact nonnegative x is < 2**k."""
    x = Fraction(x)
    need(x >= 0, "positive majorant")
    k = max(0, x.numerator.bit_length() - x.denominator.bit_length())
    while x >= 1 << k:
        k += 1
    while k and x < 1 << (k - 1):
        k -= 1
    return k


def oddpart(n):
    need(n > 0, "positive denominator")
    while n % 2 == 0:
        n //= 2
    return n
