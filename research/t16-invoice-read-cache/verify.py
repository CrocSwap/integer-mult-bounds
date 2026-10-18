#!/usr/bin/env python3
"""Source-bound T16 replay with fresh-value JSON reuse.

thakrarsagar with substantial OpenAI Codex assistance. Apache-2.0.
Tairitsu-Aya's audit and Kumagi's compression improvement remain unchanged.
"""

import argparse
import gzip
import hashlib
import json
import marshal
from pathlib import Path
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / "research/t16-invoice-boundary-audit"


class JsonReader:
    """Reuse first-seen contents when fixtures return; always give fresh values."""

    def __init__(self):
        self.cache = {}
        self.hits = self.misses = 0

    def __call__(self, path):
        raw = path.read_bytes()
        previous = self.cache.get(path)
        if previous is not None and previous[0] == raw:
            self.hits += 1
            return marshal.loads(previous[1])
        value = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
        if previous is None:
            self.cache[path] = (raw, marshal.dumps(value))
        self.misses += 1
        return value


def authenticate(root=ROOT):
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] == "input":
            actual = hashlib.sha256((root / pin["path"]).read_bytes()).hexdigest()
            if actual != pin["sha256"]:
                raise ValueError("Input changed: " + pin["path"])


def load_source(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def replay(baseline=False):
    authenticate()
    sys.modules["cases"] = load_source("cases", PREDECESSOR / "cases.py")
    audit = load_source("t16_boundary", PREDECESSOR / "verify.py")
    reader = JsonReader()
    original_load = audit.load

    def load(name, path):
        module = original_load(name, path)
        if name == "frozen_invoice" and not baseline:
            module.read = reader
        return module

    audit.load = load
    with tempfile.TemporaryDirectory(prefix="t16-read-cache-") as directory:
        actual = audit.run(Path(directory))
    expected = json.loads((PREDECESSOR / "EXPECTED.json").read_bytes())
    if actual != expected:
        raise ValueError("Full T16 receipt differs from predecessor")
    return actual, reader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Use the original reader")
    parser.add_argument("--receipt", type=Path, help="Write the reconstructed full receipt")
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError("Assertions must remain enabled for the frozen checkers")
    # Direct invocations also ignore preexisting bytecode for frozen module imports.
    with tempfile.TemporaryDirectory(prefix="t16-read-pycache-") as directory:
        sys.pycache_prefix = directory
        actual, reader = replay(args.baseline)
    if args.receipt is not None:
        args.receipt.write_text(json.dumps(actual, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(actual["status"], json.dumps(actual["summary"], sort_keys=True))
    print("PASS_T16_READ_CACHE", json.dumps({"baseline": args.baseline,
          "hits": reader.hits, "misses": reader.misses, "paths": len(reader.cache),
          "retained_bytes": sum(len(raw) + len(value) for raw, value in reader.cache.values())},
          sort_keys=True))


if __name__ == "__main__":
    main()
