"""Compare the original and replacement words with the pinned cohort checkers.

Adapted from Ali Romman / PR688 by Alluri with substantial OpenAI Codex assistance.
Apache-2.0. The underlying C++ checkers are unchanged.
"""
import json
import os
import shlex
import subprocess
import sys


def run(root, out):
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    python = [sys.executable, "-B"]
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir()

    def call(name, command):
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)

    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])
    results = {}
    local = json.loads((out / "LOCAL.json").read_text())
    saving = local["saved_additions"]
    for name in ("baseline", "replacement"):
        base = out / name
        records, cin, cout = (base / item for item in ("records", "cin", "cout"))
        call(name + "-export", python + [bit / "export_records.py", out / (name + ".json.gz"), records])
        call(name + "-cohort", python + [bit / "regression/stage_cohort.py", records, records, cin, cout])
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        if legality["status"] != "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE":
            raise ValueError("Legality did not pass")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns.json" if pairs == 2 else "columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            if data["status"] != expected_status:
                raise ValueError("Formal columns did not pass")
            expected = 6 * (pairs - 1)
            if (len(data["negative_controls"]) != expected
                    or not all(c["rejected"] for c in data["negative_controls"])):
                raise ValueError("A bridge control failed")
            if data["formal_columns_checked"] != 240 * pairs + 420:
                raise ValueError("Wrong formal column count")
            results[name]["stages"][str(2 * pairs + 1)] = {
                "bridge_controls_rejected": expected,
                "receipt": {
                key: data[key] for key in ("formal_columns_checked", "local_scalar_additions", "local_raw_H",
                                          "payload_prefix_bits", "payload_prefix_upper", "signed_lift_prefix")}}
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages]["receipt"] for name in ("baseline", "replacement"))
        if old["local_raw_H"] != new["local_raw_H"] or old["local_scalar_additions"] - new["local_scalar_additions"] != saving:
            raise ValueError("Paid profile or XOR saving differs")
        for name, receipt in (("baseline", old), ("replacement", new)):
            expected = local[name]
            if (int(receipt["payload_prefix_upper"]) != int(expected["payload_prefix_upper"])
                    or receipt["payload_prefix_bits"] != expected["payload_prefix_bits"]
                    or int(receipt["payload_prefix_upper"]) >= 2**104):
                raise ValueError("Independent native precision bill differs or exceeds the retained cap")
            actual = [int(x["cancellation_free_signed_row_l1_upper"]) for x in receipt["signed_lift_prefix"]]
            if actual != [expected["forward_prefix"], expected["reverse_prefix"]]:
                raise ValueError("Independent signed prefix bounds differ")
    return results
