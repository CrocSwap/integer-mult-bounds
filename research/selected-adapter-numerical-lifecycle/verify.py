"""Replay the complete closed selected adapter coefficient lifecycle."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
NAMES = ("words", "records", "matrices", "controller", "forms", "numeric")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), "fixed typed receipt")


def authenticated_sources():
    manifest = json.loads((PACKAGE / "SNAPSHOT.json").read_text())
    need(manifest["head"] == HEAD, "exact scientific dependency")
    need(manifest["repository"] == "https://github.com/CrocSwap/integer-mult-bounds",
         "canonical scientific repository")
    expected = {name + ".py" for name in NAMES} | {"NOTICE.md"}
    need(len(manifest["files"]) == len(expected), "closed source inventory")
    exports = {}
    for item in manifest["files"]:
        name = Path(item["path"]).name
        need(name in expected and name not in exports, "unique source name")
        need(item["path"] == "vendor/" + name, "canonical local source path")
        original = "research/selected-bit-node/" + ("" if name == "NOTICE.md" else "vendor/") + name
        need(item["source_path"] == original, "exact original source path")
        path = PACKAGE / item["path"]
        need(not path.is_symlink(), "regular source export")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
        exports[name] = raw
    return exports


def load_sources():
    exports = authenticated_sources()
    need(not any(name in sys.modules for name in NAMES), "no preloaded scientific modules")
    try:
        for name in NAMES:
            module = ModuleType(name)
            path = PACKAGE / "vendor" / (name + ".py")
            module.__file__ = str(path)
            sys.modules[name] = module
            # Every byte authenticates before execution. Direct compilation
            # deliberately bypasses stale .pyc files in the source export.
            exec(compile(exports[name + ".py"], str(path), "exec", dont_inherit=True), module.__dict__)  # noqa: S102
    except Exception:
        for name in NAMES:
            sys.modules.pop(name, None)
        raise
    return SimpleNamespace(**{name: sys.modules[name] for name in NAMES})


def receipt():
    from census import run_case

    modules = load_sources()
    cases = [("good", 42, 3, 0, "head", False, 3),
             ("good", 1, 9, 0, "tail", False, 3),
             ("good", 1, 3, 1, "zero", False, 7),
             ("good", 42, 3, 4, "head", True, 3),
             ("fallback", 1, 3, 0, "shear", False, 3),
             ("fallback", 1, 9, 1, "shear", True, 7),
             ("fallback", 1, 3, 4, "zero", False, 3),
             ("fallback", 1, 3, 1, "shear", False, 3, "P")]
    records = [run_case(modules, *case) for case in cases]
    need(records[0]["extra"][0] == 37672, "whole-call residue bound attained")
    return {"schema_version": 1, "source_head": HEAD,
            "residue_excess_bound": 37672, "index_excess_bound": 22,
            "scope": "closed adapter branch above all entry residents; successful source contracts",
            "fixtures": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the receipt without writing")
    arguments = parser.parse_args()
    actual = receipt()
    if arguments.emit:
        print(json.dumps(actual, indent=2))
    else:
        check_receipt(actual, json.loads((PACKAGE / "RESULT.json").read_text()))
        print(f"PASS_SELECTED_ADAPTER_NUMERICAL_LIFECYCLE fixtures={len(actual['fixtures'])} "
              "residues=37672 indices=22 no_new_kappa")


if __name__ == "__main__":
    main()
