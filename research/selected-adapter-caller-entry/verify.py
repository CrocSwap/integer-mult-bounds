"""Authenticate and probe numerical entry state in the selected BIT caller."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
NAMES = (
    "words",
    "matrices",
    "plan",
    "records",
    "stream",
    "trace",
    "cardinality",
    "controller",
    "counts",
    "directory",
    "forms",
    "numeric",
    "bitstream",
    "cardinal_counts",
    "layout",
    "stream_runner",
    "packet",
    "packet_engine",
    "consumer",
)
ROOT_NAMES = {"cardinal_counts", "consumer", "layout", "packet_engine"}
DEPENDENCY_HEAD = "9fdbd4b0429dbfcb4569f7768b66d318deacab6b"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    authenticate_dependency()
    manifest = json.loads((PACKAGE / "SNAPSHOT.json").read_text())
    need(manifest["head"] == HEAD, "exact dependency head")
    need(
        manifest["repository"] == "https://github.com/CrocSwap/integer-mult-bounds",
        "canonical repository",
    )
    expected = {name + ".py" for name in NAMES} | {"NOTICE.md"}
    need(len(manifest["files"]) == len(expected), "complete source inventory")
    exports = {}
    for item in manifest["files"]:
        name = Path(item["path"]).name
        need(name in expected and name not in exports, "unique source export")
        need(item["path"] == "vendor/" + name, "canonical export path")
        subdir = "" if name == "NOTICE.md" or name[:-3] in ROOT_NAMES else "vendor/"
        need(
            item["source_path"] == "research/selected-bit-node/" + subdir + name,
            "exact original source path",
        )
        path = PACKAGE / item["path"]
        need(not path.is_symlink(), "regular source export")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
        exports[name] = raw
    return exports


def authenticate_dependency():
    dependency = json.loads((PACKAGE / "DEPENDENCY.json").read_text())
    need(dependency["head"] == DEPENDENCY_HEAD, "exact adapter dependency head")
    need(
        dependency["path"] == "evidence/ADAPTER-LIFETIME.md"
        and dependency["source_path"]
        == "research/selected-adapter-numerical-lifecycle/README.md",
        "exact adapter proof paths",
    )
    need(
        dependency["repository"] == "https://github.com/CrocSwap/integer-mult-bounds",
        "canonical adapter repository",
    )
    path = PACKAGE / dependency["path"]
    need(not path.is_symlink(), "regular adapter proof export")
    raw = path.read_bytes()
    need(
        hashlib.sha256(raw).hexdigest() == dependency["sha256"], "adapter proof SHA256"
    )
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
    ).hexdigest()
    need(blob == dependency["git_blob"], "adapter proof Git blob")


def load_sources():
    exports = authenticate()
    need(not any(name in sys.modules for name in NAMES), "no preloaded source modules")
    try:
        for name in NAMES:
            module = ModuleType(name)
            path = PACKAGE / "vendor" / (name + ".py")
            module.__file__ = str(path)
            sys.modules[name] = module
            # All nineteen inputs authenticate before the first executes.
            exec(  # noqa: S102 - only the complete authenticated frozen inventory
                compile(exports[name + ".py"], str(path), "exec", dont_inherit=True),
                module.__dict__,
            )
    except Exception:
        for name in NAMES:
            sys.modules.pop(name, None)
        raise
    return SimpleNamespace(**{name: sys.modules[name] for name in NAMES})


def check_receipt(actual, expected):
    need(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "typed receipt",
    )


def receipt():
    from probe import run_case

    modules = load_sources()
    cases = [
        (True, 1, 64, 0, 3),
        (True, 42, 127, 0, 7),
        (False, 1, 64, 0, 3),
        (True, 1, 64, 4, 7),
    ]
    results = [run_case(modules, *case) for case in cases]
    return {
        "schema_version": 1,
        "source_head": HEAD,
        "adapter_entry_excess": [0, 12],
        "composed_adapter_excess": [37672, 34],
        "scope": (
            "adapter coefficient lifetimes above all Consumer.apply entry residents"
        ),
        "execution": (
            "exact caller/trace/extent state; payload and coefficient bodies abstracted"
        ),
        "fixtures": results,
    }


def main():
    sys.path.insert(0, str(PACKAGE))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print without writing")
    args = parser.parse_args()
    actual = receipt()
    if args.emit:
        print(json.dumps(actual, indent=2))
    else:
        check_receipt(actual, json.loads((PACKAGE / "RESULT.json").read_text()))
        print(
            "PASS_SELECTED_ADAPTER_CALLER_ENTRY fixtures=4 entry=0/12 "
            "composed=37672/34 no_new_kappa"
        )


if __name__ == "__main__":
    main()
