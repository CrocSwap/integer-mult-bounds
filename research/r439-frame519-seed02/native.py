#!/usr/bin/env python3
"""Compile unchanged owning checkers once and replay both finite words.

Run with BOOST_INCLUDE pointing to Boost headers if they are not installed.
Ross Richardson, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import json
import os
import platform
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUPPLIER = ROOT / "research/e8-bit-carrier-skeleton"
CHECKERS = SUPPLIER / "code/bit/checkers"
STAGER = SUPPLIER / "code/bit/regression/stage_cohort.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(command, **kwargs):
    result = subprocess.run(list(map(str, command)), text=True, capture_output=True, **kwargs)
    need(result.returncode == 0, "command failed: " + " ".join(map(str, command)) + "\n" + result.stderr)
    return result.stdout


def stable_receipt(path):
    receipt = json.loads(path.read_text())
    # All proof-relevant fields are retained; only elapsed time and temp path vary.
    receipt.pop("seconds", None)
    receipt.pop("local_scalar_stream", None)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    compiler = os.environ.get("CXX", "c++")
    boost = os.environ.get("BOOST_INCLUDE", "/usr/include")
    need((Path(boost) / "boost/multiprecision/cpp_int.hpp").is_file(),
         "Set BOOST_INCLUDE to a directory containing boost/multiprecision/cpp_int.hpp")
    with tempfile.TemporaryDirectory(prefix="r439-frame519-native-") as temporary:
        work = args.work or Path(temporary)
        work.mkdir(parents=True, exist_ok=True)
        print(run([sys.executable, "-I", "-B", HERE / "verify.py", "--work", work]).strip(), flush=True)
        bins = work / "bin"
        bins.mkdir(exist_ok=True)
        common = [compiler, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
                  "-I" + str(CHECKERS), "-I" + str(SUPPLIER / "portable-include"), "-I" + boost]
        for name, source, macros in [
            ("legality", "legality_h.cpp", []),
            ("columns_h", "columns_h.cpp", []),
            ("columns_k2", "columns_k.cpp", ["-DKPAIRS=2"]),
            ("columns_k4", "columns_k.cpp", ["-DKPAIRS=4"]),
            ("columns_k5", "columns_k.cpp", ["-DKPAIRS=5"]),
        ]:
            run([*common, *macros, CHECKERS / source, "-o", bins / name])
        proof = {}
        for name in ("base", "candidate"):
            folder = work / name
            records = folder / "records"
            cin, cout = folder / "cin", folder / "cout"
            run([sys.executable, "-I", "-B", STAGER, records, records, cin, cout])
            run([bins / "legality", cin, cout, folder / "legality.json"])
            result = {"legality": stable_receipt(folder / "legality.json")}
            for checker in ("columns_h", "columns_k2", "columns_k4", "columns_k5"):
                run([bins / checker, cout / "COHORT249-RECORDS.bin", folder / (checker + ".json")])
                result[checker] = stable_receipt(folder / (checker + ".json"))
            need(result["columns_h"] == result["columns_k2"], "independent five-stage routes disagree")
            need(result["legality"]["copies"] == result["legality"]["erasures"] == 9, "copy invoice")
            need(result["legality"]["rank_mass"] == 5129, "rank invoice")
            for checker, columns, controls in (("columns_h", 883, 6), ("columns_k4", 1327, 18),
                                               ("columns_k5", 1549, 24)):
                r = result[checker]
                need(r["formal_columns_checked"] == columns, "column coverage")
                need(len(r["negative_controls"]) == controls and all(c["rejected"] for c in r["negative_controls"]),
                     "omitted-bridge coverage")
                need(r["payload_prefix_bits"] == 93, "native payload")
                need(dict(r["local_raw_H"]) == dict(result["legality"]["paid_histogram"]),
                     "native profile discrepancy")
            proof[name] = result

        # Native failure controls against the candidate's actual record stream.
        raw = work / "candidate/cout/COHORT249-RECORDS.bin"
        original = list(struct.iter_unpack("<6i", raw.read_bytes()))
        receipts = []
        for name, mutation, checker, expected_reason in (
            ("even_coefficient", "even", "columns_h", "local defining-decoder full formal column"),
            ("self_add", "self", "columns_h", "source distinct"),
            ("copy_rank", "rank", "legality", "COPY rank"),
        ):
            records = [list(r) for r in original]
            if mutation in ("even", "self"):
                index = next(i for i, r in enumerate(records) if r[0] == 1 and r[4] == 519 and r[5] == 4)
                if mutation == "even":
                    records[index][3] = 2
                else:
                    records[index][2] = records[index][1]
            else:
                index = next(i for i, r in enumerate(records) if r[0] == 2)
                records[index][5] = 6
            mutated = b"".join(struct.pack("<6i", *r) for r in records)
            if checker == "legality":
                raw.write_bytes(mutated)
                command = [bins / checker, work / "candidate/cin", work / "candidate/cout", work / "bad.json"]
            else:
                path = work / (name + ".bin")
                path.write_bytes(mutated)
                command = [bins / checker, path, work / "bad.json"]
            completed = subprocess.run(list(map(str, command)), text=True, capture_output=True)
            raw.write_bytes(b"".join(struct.pack("<6i", *r) for r in original))
            need(completed.returncode != 0 and expected_reason in completed.stderr,
                 "native mutation not detected as expected: " + name)
            receipts.append(dict(name=name, rejected=True, reason=expected_reason))
        proof["native_mutations"] = receipts
        proof["normalization"] = "removed only seconds and local_scalar_stream; all other checker fields retained"
        proof["schema"] = "r439-frame519-native/1"
        output = HERE / "NATIVE-CERTIFICATE.json"
        if args.write_certificate:
            output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
        else:
            need(proof == json.loads(output.read_text()), "native certificate mismatch")
        print("PASS_R439_FRAME519_NATIVE words=2 columns=883/1327/1549 "
              "bridge_controls=96 record_controls=3 local_ADDs=24305->24285 payload_bits=93")
        if args.work:
            (work / "ENVIRONMENT.json").write_text(json.dumps(dict(python=sys.version,
                    platform=platform.platform(), compiler=run([compiler, "--version"]).splitlines()[0],
                    boost_include=boost), indent=2) + "\n")


if __name__ == "__main__":
    main()
