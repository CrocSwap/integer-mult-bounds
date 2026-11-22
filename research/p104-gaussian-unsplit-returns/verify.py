"""Restore the two-return Gaussian variant and replay one registered mode."""

from argparse import ArgumentParser
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
MODES = ("binary", "cost", "schedule", "install", "physical", "receiver", "slabs", "product")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=MODES)
    args = parser.parse_args()
    prepare = runpy.run_path(str(HERE / "prepare.py"))
    with TemporaryDirectory(prefix="p104-unsplit-returns-") as temporary:
        work = Path(temporary) / "upstream"
        prepare["materialize"](HERE / "peer8053", work)
        (work / "RESULT.json").write_bytes((HERE / "RESULT.json").read_bytes())
        subprocess.run([sys.executable, "-IB", str(work / "verify.py"), args.mode], check=True)
        print("PASS_GAUSSIAN_UNSPLIT_RETURNS", args.mode, flush=True)


if __name__ == "__main__":
    main()
