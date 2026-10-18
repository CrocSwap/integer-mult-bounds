#!/usr/bin/env python3
"""Fresh unchanged C++ legality and 5/9/11-stage replay of both R439 words.

Ryan Haines, substantial OpenAI Codex assistance. Apache-2.0.
Requires Python 3.11+, a C++17 compiler and Boost headers.
"""
import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(argv, log):
    with log.open("w", encoding="utf-8") as handle:
        subprocess.run([str(arg) for arg in argv], stdout=handle, stderr=subprocess.STDOUT, check=True)


def replay(work):
    spec = importlib.util.spec_from_file_location("interleaved_verifier", HERE / "verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    receipt = verifier.verify(work)
    verifier.need(receipt == json.loads((HERE / "EXPECTED.json").read_text()), "local receipt changed")
    pkg = ROOT / "research/e8-bit-carrier-skeleton"
    checkers = pkg / "code/bit/checkers"
    binaries = work / "bin"
    binaries.mkdir()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(checkers), "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
    # The portable bits header is not needed on Linux; pin it when explicitly used.
    for name, source, more in [("legality", "legality_h.cpp", []),
                               ("columns_h", "columns_h.cpp", []),
                               ("columns_k4", "columns_k.cpp", ["-DKPAIRS=4"]),
                               ("columns_k5", "columns_k.cpp", ["-DKPAIRS=5"])]:
        print("Compiling " + name, flush=True)
        run([*compiler, *flags, *more, "-o", binaries / name, checkers / source],
            binaries / (name + ".log"))
    result = {}
    for version in ("before", "after"):
        folder = work / version
        records = folder / "records"
        run([sys.executable, "-I", "-B", pkg / "code/bit/regression/stage_cohort.py",
             records, records, folder / "cin", folder / "cout"], folder / "stage.log")
        run([binaries / "legality", folder / "cin", folder / "cout", folder / "legality.json"],
            folder / "legality.log")
        legality = json.loads((folder / "legality.json").read_text())
        verifier.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
                      "native legality failed")
        verifier.need(legality["rank_mass"] == 5129 and legality["copies"] == legality["erasures"] == 9,
                      "native paid obligations changed")
        verifier.need(legality["common_frame_ADDs"] == receipt[version]["adds"], "native ADD bill differs")
        result[version] = {"legality": legality, "columns": {}}
        for name, stages, columns, controls in [("columns_h", 5, 883, 6),
                                                ("columns_k4", 9, 1327, 18),
                                                ("columns_k5", 11, 1549, 24)]:
            run([binaries / name, folder / "cout/COHORT249-RECORDS.bin", folder / (name + ".json")],
                folder / (name + ".log"))
            raw = json.loads((folder / (name + ".json")).read_text())
            verifier.need(raw["status"].startswith("PASS_NEW_COHORT249_ALL_"), "native column check failed")
            verifier.need(raw["formal_columns_checked"] == columns and len(raw["stages"]) == stages,
                          "native formal-column coverage changed")
            verifier.need(len(raw["negative_controls"]) == controls
                          and all(row["rejected"] for row in raw["negative_controls"]),
                          "native bridge omission control failed")
            verifier.need(raw["local_scalar_additions"] == receipt[version]["adds"], "scalar count differs")
            verifier.need([int(row["cancellation_free_signed_row_l1_upper"]) for row in raw["signed_lift_prefix"]]
                          == [receipt[version]["forward_positive_bound"], receipt[version]["reverse_positive_bound"]],
                          "independent native positive bounds differ")
            verifier.need(raw["payload_prefix_upper"] == receipt[version]["payload_upper"], "payload bound differs")
            raw.pop("seconds")
            raw["local_scalar_stream"] = version + "/cout/COHORT249-RECORDS.bin"
            result[version]["columns"][str(stages)] = raw
        print("Native " + version + ": legality and 5/9/11-stage columns PASS", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new output directory; must not exist")
    parser.add_argument("--record-expected", type=Path, help="write a NEW native expected receipt")
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = replay(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="p111-interleaved-native-") as directory:
            result = replay(Path(directory))
    if args.record_expected:
        with args.record_expected.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    elif result != json.loads((HERE / "NATIVE.json").read_text()):
        raise SystemExit("REJECT: deterministic native receipts differ")
    if args.out:
        (args.out / "native-receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_P111_INTERLEAVED_NATIVE both_words=2 stages=5,9,11 bridge_controls=96 ADDs=24305->24273")


if __name__ == "__main__":
    main()
