#!/usr/bin/env python3
"""Authenticate and replay the unchanged numerical form constructors."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
NAMES = ("words", "matrices", "forms")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources(package=PACKAGE):
    manifest = json.loads((package / "SNAPSHOT.json").read_text())
    need(manifest["head"] == HEAD, "exact scientific dependency")
    need(manifest["repository"] == "https://github.com/CrocSwap/integer-mult-bounds",
         "canonical repository")
    names = {name + ".py" for name in NAMES} | {"NOTICE.md"}
    need(len(manifest["files"]) == len(names), "closed source inventory")
    exports = {}
    for item in manifest["files"]:
        name = Path(item["path"]).name
        need(name in names and name not in exports, "unique source name")
        need(item["path"] == "vendor/" + name, "canonical export path")
        original = "research/selected-bit-node/" + ("" if name == "NOTICE.md" else "vendor/") + name
        need(item["source_path"] == original, "exact original path")
        path = package / item["path"]
        need(not path.is_symlink(), "regular source export")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
        exports[name] = raw
    return exports


@contextmanager
def loaded(package=PACKAGE):
    exports = sources(package)
    need(not any(name in sys.modules for name in NAMES), "no preloaded scientific modules")
    try:
        for name in NAMES:
            module = ModuleType(name)
            path = package / "vendor" / (name + ".py")
            module.__file__ = str(path)
            sys.modules[name] = module
            # Compile the authenticated bytes, never a possibly stale .pyc.
            exec(compile(exports[name + ".py"], str(path), "exec", dont_inherit=True), module.__dict__)
        yield SimpleNamespace(**{name: sys.modules[name] for name in NAMES})
    finally:
        for name in NAMES:
            sys.modules.pop(name, None)


def receipt():
    from census import run_case

    small = [("good", m, r, modulus, 3) for m in (2, 3, 5)
             for r in sorted({1, m - 1}) for modulus in (3, 9)]
    small += [("fallback", m, 1, modulus, 3) for m in (1, 2, 3, 5) for modulus in (3, 9)]
    selected = [("good", 64, 1, 3, 3), ("good", 64, 42, 3, 3),
                ("good", 64, 42, 3, 7), ("fallback", 64, 1, 3, 3)]
    with loaded() as modules:
        records = [run_case(modules, *case) for case in small + selected]
    return {"schema_version": 1, "source_head": HEAD,
            "good_bound_at_rank42": 33574, "fallback_bound": 32645,
            "scope": "constructor excess above all entry residents; successful source contracts",
            "fixtures": records}


def check_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "fixed typed receipt")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a receipt without writing")
    arguments = parser.parse_args()
    actual = receipt()
    if arguments.emit:
        print(json.dumps(actual, indent=2))
    else:
        check_receipt(actual, json.loads((PACKAGE / "RESULT.json").read_text()))
        print("PASS_SELECTED_FORM_CONSTRUCTION_STORAGE "
              f"fixtures={len(actual['fixtures'])} good=33574 fallback=32645 no_new_kappa")


if __name__ == "__main__":
    main()
