#!/usr/bin/env python3
"""Opt-in complete PR1097 replay with an authenticated signed-epoch checker."""
import argparse
import contextlib
import hashlib
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # Also support python -I and unrelated cwd.
import candidate


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def load(source=None):
    source = (source or ROOT.parent / "p111-minrank-proof-reconciliation").resolve()
    pins = json.loads((ROOT / "SOURCES.json").read_text())
    authenticated = {}
    for name, digest in pins["files_sha256"].items():
        raw = (source / name).read_bytes()
        # Source containers stay pinned; proof equivalence uses decoded bytes.
        if name.endswith(".lrat.gz"):
            import gzip
            raw = gzip.decompress(raw)
        need(hashlib.sha256(raw).hexdigest() == digest, "predecessor pin: " + name)
        authenticated[name] = raw
    names = ("encoding", "lrat", "controls", "compare_original", "p111_original_verify")
    need(not any(name in sys.modules for name in names), "preloaded predecessor module")
    # Execute precisely the authenticated source bytes, never cached .pyc files.
    # Explicit dependency order also prevents reuse of an unrelated bare import.
    try:
        for name in names:
            filename = "verify.py" if name == "p111_original_verify" else name + ".py"
            module = types.ModuleType(name)
            module.__file__ = str(source / filename)
            sys.modules[name] = module
            exec(compile(authenticated[filename], module.__file__, "exec"), module.__dict__)
    except BaseException:
        for name in names:
            sys.modules.pop(name, None)
        raise
    module.sources()  # Retain predecessor's own exact inventory/source checks.
    return module


@contextlib.contextmanager
def checker(module, function):
    original = module.lrat.check
    module.lrat.check = function
    try:
        yield
    finally:
        module.lrat.check = original


def run(module, engine):
    function = module.lrat.check if engine == "baseline" else candidate.check
    with checker(module, function):
        result = module.compute()
    need(canonical(result) == canonical(module.read_json(module.ROOT / "EXPECTED.json")),
         "complete predecessor receipt differs")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("baseline", "epochs"), default="epochs")
    parser.add_argument("--source", type=Path, help="Relocated original PR1097 package")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    module = load(args.source)
    result = run(module, args.engine)
    if args.receipt:
        args.receipt.write_bytes(canonical(result) + b"\n")
    print(json.dumps({"status": "PASS", "engine": args.engine,
                      "proof_additions": sum(v["proof"]["additions"] for v in result["certificates"].values()),
                      "hints_checked": sum(v["proof"]["hints_checked"] for v in result["certificates"].values()),
                      "receipt_sha256": hashlib.sha256(canonical(result)).hexdigest(),
                      "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
