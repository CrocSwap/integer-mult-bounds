"""Materialize and verify the parity-rounded Gaussian construction."""
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
    mode = parser.parse_args().mode
    prepare = runpy.run_path(str(HERE / "prepare.py"))
    with TemporaryDirectory(prefix="p104-rounded-partitions-") as temporary:
        work = Path(temporary) / "native"
        prepare["materialize"](HERE / "peer8054", HERE / "round370", work)
        (work / "RESULT.json").write_bytes((HERE / "RESULT.json").read_bytes())
        subprocess.run([sys.executable, "-IB", str(work / "verify.py"), mode], check=True)
        print("PASS_GAUSSIAN_ROUNDED_PARTITIONS", mode, flush=True)


if __name__ == "__main__":
    main()
