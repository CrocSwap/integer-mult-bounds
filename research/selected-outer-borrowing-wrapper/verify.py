#!/usr/bin/env python3
"""Read-only replay. Receipts are compared by complete typed JSON encoding."""

import argparse
import json
from pathlib import Path

from predecessor import PACKAGE, installed, require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def run(core_only=False):
    with installed():
        from checks import run_cases
        from controls import run_controls

        result = {"cases": run_cases(), "controls": run_controls()}
        if not core_only:
            from integration import run_node

            result["integration"] = run_node()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-only", action="store_true")
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = run(args.core_only)
    if args.emit_to is not None:
        target = args.emit_to.resolve()
        require(not target.is_relative_to(PACKAGE), "receipt output must be external")
        with target.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        if args.core_only:
            expected = {
                key: value for key, value in expected.items() if key != "integration"
            }
        require(
            canonical(result) == canonical(expected), "complete typed receipt matches"
        )
    print(
        "PASS_OUTER_BORROWING_WRAPPER",
        "core" if args.core_only else "complete",
        "cases",
        len(result["cases"]),
        "controls",
        len(result["controls"]),
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
