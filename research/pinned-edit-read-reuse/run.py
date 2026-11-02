#!/usr/bin/env python3
"""Select one retained scanner; produced by Nick Petalas. Apache-2.0."""
import argparse
import importlib.util
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load(implementation):
    if implementation not in ("predecessor", "optimized"):
        raise ValueError("unknown implementation")
    # Both retained scripts import the same authenticated, stdlib-only helper.
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location(
            "pinned_edit_" + implementation, PACKAGE / (implementation + ".py"))
        if spec is None or spec.loader is None:
            raise ValueError("scanner module unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    module.ROOT = ROOT
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("implementation", choices=("predecessor", "optimized"))
    args, rest = parser.parse_known_args()
    return load(args.implementation).main(rest)


if __name__ == "__main__":
    sys.exit(main())
