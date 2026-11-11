#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the inherited exact checks on a private source-bound candidate copy."""

import argparse
from pathlib import Path
from shutil import copyfile
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay_sources import parent_archive, read, need

STAGES = {"early": "verify_early.py", "native": "verify_native.py", "caller": "verify.py"}
REPLAY_MODULES = (
    "verify_early.py", "verify_native.py", "verify.py", "price.py", "adapt.py",
    "construct.py", "certificate.py", "derive_grid.py", "support.py",
    "split.py", "temporal_construct.py",
)
INPUTS = ("INPUTS.json", "WITNESS.json", "PATHS.json", "WORD.json.gz",
          "EARLY-RESULT.json", "NATIVE-RESULT.json", "RESULT.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--out", type=Path, help="Generate a new receipt at a path that does not exist")
    args = parser.parse_args()
    need(__debug__, "Run without optimized Python")
    output = args.out.resolve() if args.out else None
    if output:
        need(not output.exists(), "Receipt destination already exists")
    from replay_adapters import adapt_replay

    with parent_archive() as parent, TemporaryDirectory(prefix="p104-stationary-stage-") as tmp:
        work = Path(tmp)
        for name in REPLAY_MODULES:
            copyfile(parent / name, work / name)
        for name in INPUTS:
            if (HERE / name).is_file():
                copyfile(HERE / name, work / name)
        copyfile(HERE / "replay_sources.py", work / "source.py")
        copyfile(HERE / "replay_checks.py", work / "replay_checks.py")
        (work / "PARENT-DIRECTORY.txt").write_text(str(parent) + "\n")
        adapt_replay(work, read(HERE / "PROFILE.json"), read(HERE / "WITNESS.json"))
        argv = [sys.executable, "-I", "-B", str(work / STAGES[args.stage])]
        if output:
            argv.extend(("--out", str(output)))
        subprocess.run(argv, cwd=work, check=True)


if __name__ == "__main__":
    main()
