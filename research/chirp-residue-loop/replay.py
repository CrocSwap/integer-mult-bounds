"""Authenticate and run the complete retained command with one substitution."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from loop import one_axis


def load_source(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (root / row["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("source hash mismatch: " + row["path"])
    source = root / "research/chirp-residue-step/verify.py"
    spec = importlib.util.spec_from_file_location("retained_chirp_residue", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("retained source loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(mode, *, census=None):
    source = load_source()
    implementation = source.one_axis if mode == "baseline" else one_axis
    if census is None:
        source.one_axis = implementation
    else:
        def record(radius, length, slope):
            result = implementation(radius, length, slope)
            census.append((radius, length, slope, result))
            return result
        source.one_axis = record
    source.main()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "fast"), default="fast")
    args = parser.parse_args()
    execute(args.mode)


if __name__ == "__main__":
    main()
