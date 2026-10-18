"""Supplementary unchanged C++ legality and 5/9/11-stage column replays.

Jeffrey Cox, with substantial OpenAI assistance; Apache-2.0.
Requires Python 3.11+, a C++17 compiler and Boost headers.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SKELETON = ROOT / "research/e8-bit-carrier-skeleton"


def command(arguments, log: Path) -> None:
    with log.open("w") as stream:
        subprocess.run([str(a) for a in arguments], stdout=stream, stderr=stream, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path, help="new output directory")
    parser.add_argument("--boost-include", type=Path, default=Path("/usr/include"))
    parser.add_argument("--cxx", default=os.environ.get("CXX", "c++"))
    parser.add_argument("--cxxflags", default=os.environ.get("CXXFLAGS", ""))
    args = parser.parse_args()
    out = args.out.resolve()
    subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"), "--out", str(out)], check=True)
    common = [*shlex.split(args.cxx), "-O2", "-std=c++17", *shlex.split(args.cxxflags),
              "-DHDIM=8", "-DNCOPY=9", f"-I{SKELETON / 'portable-include'}",
              f"-I{SKELETON / 'code/bit/checkers'}", f"-I{args.boost_include.resolve()}"]
    binaries = out / "bin"
    binaries.mkdir()
    command([*common, "-o", binaries / "legality", SKELETON / "code/bit/checkers/legality_h.cpp"],
            binaries / "legality.compile.log")
    for pairs in (2, 4, 5):
        command([*common, "-DVPORTS=120", "-DRHELP=420", f"-DKPAIRS={pairs}",
                 "-o", binaries / f"columns{pairs}", SKELETON / "code/bit/checkers/columns_k.cpp"],
                binaries / f"columns{pairs}.compile.log")

    reports = {}
    python_receipt = json.loads((out / "REPORT.json").read_text())
    for variant in ("original", "rewritten"):
        folder = out / variant
        command([sys.executable, "-I", "-B", SKELETON / "code/bit/regression/stage_cohort.py",
                 folder / "records", folder / "records", folder / "cin", folder / "cout"],
                folder / "stage.log")
        command([binaries / "legality", folder / "cin", folder / "cout", folder / "legality.json"],
                folder / "legality.log")
        legality = json.loads((folder / "legality.json").read_text())
        expected = python_receipt[variant]
        if (legality["common_frame_ADDs"] != expected["adds"] or
                legality["rank_mass"] != expected["rank_mass"] or
                legality["copies"] != 9 or legality["erasures"] != 9):
            raise ValueError("native legality disagrees with independent Python replay")
        columns = {}
        for pairs in (2, 4, 5):
            command([binaries / f"columns{pairs}", folder / "cout/COHORT249-RECORDS.bin",
                     folder / f"columns{pairs}.json"], folder / f"columns{pairs}.log")
            receipt = json.loads((folder / f"columns{pairs}.json").read_text())
            if (receipt["local_scalar_additions"] != expected["adds"] or
                    receipt["formal_columns_checked"] != 2 * pairs * 120 + 420 or
                    receipt["payload_prefix_upper"] != expected["payload_upper"] or
                    not all(control["rejected"] for control in receipt["negative_controls"])):
                raise ValueError("native column checker disagrees with expected circuit")
            receipt.pop("local_scalar_stream")
            receipt.pop("seconds")
            columns[str(2 * pairs + 1)] = receipt
        reports[variant] = {"legality": legality, "columns": columns}
    (out / "NATIVE-REPORT.json").write_text(json.dumps(reports, indent=2) + "\n")
    expected = json.loads((HERE / "NATIVE-EXPECTED.json").read_text())
    if reports != expected:
        raise ValueError("native receipts differ from NATIVE-EXPECTED.json")
    print("PASS_NATIVE_R420_FOUR_WIRE: legality and 900/1380/1620 columns for both words; all bridge controls rejected")


if __name__ == "__main__":
    main()
