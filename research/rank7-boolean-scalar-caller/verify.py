# SPDX-License-Identifier: Apache-2.0
"""Cold native/capacity replay, Boolean caller and exact tariff comparison."""

import argparse
import json
import tempfile
from pathlib import Path

import caller
import check_bits
import replay

PACKAGE = Path(__file__).resolve().parent


def run(work):
    result = replay.run(work)
    result["bit_checks"] = check_bits.run()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        caller.require(
            not work.exists() and not work.is_relative_to(PACKAGE.parents[1]),
            "fresh external output directory",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="boolean-scalar-caller-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        caller.require(
            result == json.loads(expected.read_text()), "deterministic result"
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
