#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce one provider's source-bound endpoint/native dependency audit."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent


def load_support():
    path = PACKAGE / "support.py"
    module = types.ModuleType("v45_closed_support")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def check_run(support, modules, blobs, tag, run, progress):
    data = support.artifacts(blobs, tag, run)
    controls = modules["controls"].run(modules, data)
    result = modules["audit"].provider(modules, **data, progress=progress)
    result.update(schema_version=1, provider=tag, controls=controls,
                  source_sha256={p: support.sha(raw) for p, raw in blobs.items()},
                  scientific_head="be191346391661f4d35fc0d1508d0a6029572576",
                  scientific_base="d8e0f83f00191df62174b641e9fff055c357f641",
                  source_artifacts_bound=True)
    return result


def compute(tag, supplied=None, progress=None):
    support = load_support()
    blobs = support.inputs()
    own = {p.name: support.sha(support.read_bytes(p)) for p in PACKAGE.glob("*.py")}
    modules = support.modules(blobs)
    if supplied is None:
        with tempfile.TemporaryDirectory(prefix="v45-closed-cone-") as name:
            run = support.generate(blobs, tag, Path(name), progress)
            result = check_run(support, modules, blobs, tag, run, progress)
    else:
        result = check_run(support, modules, blobs, tag, supplied, progress)
    support.require(support.inputs() == blobs, "retained source changed during audit")
    after = {p.name: support.sha(support.read_bytes(p)) for p in PACKAGE.glob("*.py")}
    support.require(after == own, "audit source changed during replay")
    result["audit_source_sha256"] = own
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("base", "extra"))
    parser.add_argument("--artifacts", type=Path, help="reuse supplied artifacts; all source bindings/native identities still checked")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    def progress(value):
        print(json.dumps(value, sort_keys=True), file=sys.stderr, flush=True)
    result = compute(args.provider, args.artifacts, progress if args.progress else None)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = load_support().read(PACKAGE / ("RESULT-" + args.provider + ".json"))
        if result != expected:
            raise ValueError("deterministic source/native audit receipt mismatch")
        print(result["status"] + " provider=" + args.provider + " native_identities=" + str(result["distinct_native_identities"]))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError, TimeoutError, subprocess.TimeoutExpired) as exc:
        raise SystemExit("FAIL: " + str(exc)) from None
