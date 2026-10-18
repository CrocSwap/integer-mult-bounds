#!/usr/bin/env python3
"""Read-only exact wrapper-contract replay; external receipt emission only."""
import argparse
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import algebra
import runtime_check


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run():
    inputs = runtime_check.authenticate()
    return dict(schema_version=1, source_inputs=inputs, algebra=algebra.run(),
                literal_source=runtime_check.run(), no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = run()
    if args.emit_to is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        algebra.need(canonical(result) == canonical(expected), "complete typed receipt")
    else:
        target = args.emit_to.resolve()
        algebra.need(not target.is_relative_to(PACKAGE), "emit outside package")
        with target.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_WEIGHTED_WRAPPER_CONTRACT no_new_kappa")


if __name__ == "__main__":
    main()
