"""Fresh unchanged native legality and 5/9/11-stage checks for both words.

Adapted from Ali Romman / PR688's r420-two-block-composition/native.py,
originally prepared with substantial OpenAI Codex assistance.
Prepared for Krishnendu Purohit (@Deftsalt-debug) with substantial OpenAI Codex
assistance. Apache-2.0. Needs C++17 and Boost headers (BOOST_INCLUDE).
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("block_verifier", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def run(out, write):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    package = verify.ROOT / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    required = [str(p.relative_to(verify.ROOT)) for p in
                (bit / "regression/stage_cohort.py", checkers / "legality_h.cpp",
                 checkers / "columns_k.cpp", checkers / "json.hpp",
                 package / "portable-include/bits/stdc++.h")]
    verify.need(pins["native_inputs"] == required, "native input coverage mismatch")
    for path in required:
        verify.need(verify.sha((verify.ROOT / path).read_bytes()) == pins["files"][path]["sha256"],
                    "native source hash mismatch: " + path)
    local = out / "local"
    local.mkdir()
    verify.run(local, False)
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir()

    def call(name, command):
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)

    def receipt(path):
        data = json.loads(path.read_text())
        # Only execution time and the temporary absolute stream pathname vary.
        data.pop("seconds", None)
        data.pop("local_scalar_stream", None)
        return data

    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])
    results = {}
    for name in ("original", "replacement"):
        records = local / name
        base = out / name
        cin, cout = base / "cin", base / "cout"
        call(name + "-cohort", [sys.executable, "-I", "-B", bit / "regression/stage_cohort.py",
                                records, records, cin, cout])
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = receipt(cout / "legality.json")
        verify.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
                    "native legality did not pass")
        verify.need(legality["rank_mass"] == 5129 and legality["copies"] == legality["erasures"] == 9,
                    "native legality price mismatch")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            path = cout / ("columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", path])
            data = receipt(path)
            status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2 else
                      "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            verify.need(data["status"] == status, "native columns did not pass")
            verify.need(data["formal_columns_checked"] == 222 * pairs + 439, "column coverage mismatch")
            controls = data["negative_controls"]
            verify.need(len(controls) == 6 * (pairs - 1) and all(c["rejected"] for c in controls),
                        "native bridge control failed")
            expected = json.loads((HERE / "CERTIFICATE.json").read_text())["native_records"][name]
            verify.need(data["local_scalar_additions"] == expected["adds"] and
                        data["payload_prefix_upper"] == expected["payload_prefix_upper"] and
                        [int(x["cancellation_free_signed_row_l1_upper"]) for x in data["signed_lift_prefix"]]
                        == expected["positive_prefix"], "native/Python prefix or count mismatch")
            results[name]["stages"][str(2 * pairs + 1)] = data
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("original", "replacement"))
        verify.need(old["local_raw_H"] == new["local_raw_H"] and
                    old["local_scalar_additions"] - new["local_scalar_additions"] == 10,
                    "native paid profile or saving mismatch")
        verify.need(int(new["payload_prefix_upper"]) <= int(old["payload_prefix_upper"]),
                    "native prefix increased")
    path = HERE / "NATIVE.json"
    if write:
        path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    else:
        verify.need(results == json.loads(path.read_text()), "native receipt mismatch")
    print("PASS_R439_BLOCK1_NATIVE words=2 stages=5,9,11 columns=883,1327,1549 bridge_controls=96")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh directory for logs and execution artifacts")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_receipt)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-block1-native-") as temporary:
            run(Path(temporary), args.write_receipt)


if __name__ == "__main__":
    main()
