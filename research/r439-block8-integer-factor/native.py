"""Fresh native legality and 5/9/11-stage columns for both words.

Prepared for @zeusinsight with substantial OpenAI Codex assistance; Apache-2.0.
Uses the unchanged predecessor's export/staging/checkers with their notices.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = ROOT / "research/e8-bit-carrier-skeleton"
CHECKERS = PKG / "code/bit/checkers"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(work, write):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path in pins["native_inputs"]:
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() ==
             pins["files"][path]["sha256"], "native source mismatch: " + path)
    subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                    "--output", str(work / "local")], check=True)
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    compiler = os.environ.get("CXX", "c++")
    common = [compiler, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
              "-DVPORTS=111", "-DRHELP=439", "-I" + str(CHECKERS),
              "-I" + str(PKG / "portable-include")]
    if os.environ.get("BOOST_INCLUDE"):
        common.append("-I" + os.environ["BOOST_INCLUDE"])
    subprocess.run(common + [str(CHECKERS / "legality_h.cpp"),
                             "-o", str(work / "legality")], check=True)
    for pairs in (2, 4, 5):
        subprocess.run(common + ["-DKPAIRS=" + str(pairs), str(CHECKERS / "columns_k.cpp"),
                                 "-o", str(work / ("columns" + str(pairs)))], check=True)
    receipts = {}
    for name in ("original", "replacement"):
        records = work / "local" / name
        inp, out = work / (name + "-in"), work / (name + "-out")
        subprocess.run([sys.executable, "-I", "-B", str(PKG / "code/bit/regression/stage_cohort.py"),
                        str(records), str(records), str(inp), str(out)], check=True)
        subprocess.run([str(work / "legality"), str(inp), str(out), str(out / "legality.json")],
                       check=True, capture_output=True, text=True)
        legality = json.loads((out / "legality.json").read_text())
        expected = cert["native_records"][name]
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             "legality status")
        for field, value in (("rank_mass", 5129), ("copies", 9), ("erasures", 9),
                             ("common_frame_ADDs", expected["adds"]), ("nested_MOVEs", expected["moves"])):
            need(legality[field] == value, "legality mismatch: " + field)
        receipts[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            dest = out / ("columns" + str(pairs) + ".json")
            subprocess.run([str(work / ("columns" + str(pairs))),
                            str(out / "COHORT249-RECORDS.bin"), str(dest)],
                           check=True, capture_output=True, text=True)
            receipt = json.loads(dest.read_text())
            stages = 2 * pairs + 1
            need(receipt["formal_columns_checked"] == (stages - 1) * 111 + 439,
                 "formal column coverage")
            controls = receipt["negative_controls"]
            need(len(controls) == 6 * (pairs - 1) and all(c["rejected"] for c in controls),
                 "bridge control coverage")
            prefix = expected["prefix"]
            need(receipt["payload_prefix_upper"] == prefix["payload"] and
                 receipt["payload_prefix_bits"] == prefix["payload_bits"], "prefix disagreement")
            need([int(r["cancellation_free_signed_row_l1_upper"]) for r in receipt["signed_lift_prefix"]]
                 == [prefix["forward"], prefix["reverse"]], "forward/reverse bounds")
            need(receipt["local_scalar_additions"] == expected["adds"], "native ADD mismatch")
            need(dict(receipt["local_raw_H"]) == {int(k): v for k, v in expected["paid_histogram"].items()},
                 "paid histogram mismatch")
            receipt.pop("seconds")
            receipt.pop("local_scalar_stream")
            receipts[name]["stages"][str(stages)] = receipt
    dest = HERE / "NATIVE-CERTIFICATE.json"
    if write:
        dest.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    else:
        need(receipts == json.loads(dest.read_text()), "native certificate mismatch")
    print("PASS_R439_BLOCK8_NATIVE words=2 stages=5,9,11 columns=883,1327,1549 bridge_controls=96")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for retained build/replay")
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-block8-native-") as temp:
            run(Path(temp), args.write_certificate)


if __name__ == "__main__":
    main()
