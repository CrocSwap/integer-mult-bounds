"""Optional actual native replay with the checked cpp_int stand-in, not Boost.

The two unchanged C++ checkers compile with their selected dimensions. The
explicit stand-in uses checked 128-bit arithmetic and refuses overflow. This
is a finite cross-stage control, not a fresh system-Boost or supplier replay.
All compiler inputs are authenticated by the primary verifier before work.

Power-of-Ten deviation: Python allocates bounded fixture/receipt objects and
dispatches authenticated external programs. Two builds and twelve fixed child
calls have explicit deadlines; three streams contain at most 30,000 records.
Frozen compiler code and its existing diagnostics remain unchanged. Reassess
those bounds before adding fixtures, targets, compiler flags or input files.
Nick Petalas. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import verify

BIT = "research/e8-bit-carrier-skeleton/code/bit/"
CHECKERS = BIT + "checkers/"
STAGE = BIT + "regression/stage_cohort.py"
PORTABLE = "research/e8-bit-carrier-skeleton/portable-include/"
STANDIN = "research/bit589-checked-cpp-int-seed92/include/"
NATIVE_INPUTS = (
    CHECKERS + "columns_h.cpp",
    CHECKERS + "legality_h.cpp",
    CHECKERS + "json.hpp",
    STAGE,
    PORTABLE + "bits/stdc++.h",
    STANDIN + "boost/multiprecision/cpp_int.hpp",
)
LEGALITY_STATUS = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
COLUMNS_STATUS = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
REJECTION = "local defining-decoder full formal column"
BASE_SHA = "ea44aa047a2a9cf034de8b56b2166c49cf2dbdf9cd9ed6a20299a4f2b05ef09a"
MUTANT_SHA = "5629b522bb0381127e3514396f034f308e0aa797f134f833e4d8feb678dce744"


def command(arguments, *, timeout=30):
    """Return a completed process; callers check its actual output contract."""
    verify.require(0 < len(arguments) <= 24, "bounded native command")
    return subprocess.run(
        arguments, check=False, capture_output=True, text=True, timeout=timeout
    )


def compile_checkers(data, directory):
    verify.require(set(NATIVE_INPUTS) <= set(data), "complete native source pins")
    for name in NATIVE_INPUTS:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data[name])
    compiler = os.environ.get("CXX", "c++")
    verify.require(bool(compiler) and len(compiler) <= 4096, "compiler executable")
    flags = [
        compiler,
        "-O2",
        "-std=c++17",
        "-DHDIM=8",
        "-DNCOPY=9",
        "-DVPORTS=111",
        "-DRHELP=439",
    ]
    flags += ["-I" + str(directory / name) for name in (PORTABLE, CHECKERS, STANDIN)]
    binaries = {}
    for name in ("legality_h", "columns_h"):
        output = directory / name
        result = command(
            flags + ["-o", str(output), str(directory / CHECKERS / (name + ".cpp"))],
            timeout=60,
        )
        verify.require(
            result.returncode == 0 and output.is_file(),
            "native compile failed: " + result.stderr,
        )
        binaries[name] = output
    return binaries


def legality(binary, cin, cout, receipt, count):
    result = command([str(binary), str(cin), str(cout), str(receipt)])
    verify.require(
        result.returncode == 0 and receipt.is_file(),
        "native legality failed: " + result.stderr,
    )
    value = json.loads(receipt.read_bytes())
    verify.require(value["status"] == LEGALITY_STATUS, "native legality status")
    verify.require(
        value["records"] == count and value["rank_mass"] == 5129,
        "native legality records and mass",
    )
    verify.require(
        value["copies"] == value["erasures"] == 9, "native copy/erase inventory"
    )
    verify.require(value["common_frame_ADDs"] == count - 2929, "native ADD recount")
    return value


def columns(binary, stream, receipt, honest):
    result = command([str(binary), str(stream), str(receipt)])
    if not honest:
        verify.require(
            result.returncode == 2 and result.stderr.strip() == REJECTION,
            "native mutant rejection site",
        )
        verify.require(
            not result.stdout and not receipt.exists(),
            "native rejection produces no success receipt",
        )
        return {"exit_code": 2, "rejection": REJECTION}
    verify.require(
        result.returncode == 0 and receipt.is_file(),
        "native baseline columns failed: " + result.stderr,
    )
    value = json.loads(receipt.read_bytes())
    verify.require(value["status"] == COLUMNS_STATUS, "native column status")
    verify.require(
        value["formal_columns_checked"] == 883,
        "complete native global column inventory",
    )
    verify.require(value["local_scalar_stream"] == str(stream), "native stream link")
    value["local_scalar_stream"] = "COHORT249-RECORDS.bin"
    seconds = value.pop("seconds")
    verify.require(
        type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
        "native elapsed-time metadata",
    )
    lines = result.stderr.splitlines()
    verify.require(len(lines) == 5, "five native stages")
    for stage, line in enumerate(lines):
        prefix = "stage " + str(stage) + " PASS elapsed "
        verify.require(
            line.startswith(prefix) and line.endswith("s"), "native stage diagnostic"
        )
        elapsed = float(line[len(prefix) : -1])
        verify.require(math.isfinite(elapsed) and elapsed >= 0, "native stage timing")
    return value


def fixture(data, word, directory, binaries, honest):
    raw = verify.export(data[verify.EXPORTER], word, directory)
    expected_sha = BASE_SHA if honest else MUTANT_SHA
    verify.require(
        hashlib.sha256(raw).hexdigest() == expected_sha,
        "native fixture record identity",
    )
    values, differences = verify.replay(raw, word)
    if honest:
        verify.require(not differences, "native positive scalar oracle")
    else:
        verify.require(
            verify.witness(values, differences, word)["actual_bit"] == 1,
            "native dirty-input scalar oracle",
        )
    records, cin, cout = directory / "records", directory / "cin", directory / "cout"
    result = command(
        [
            sys.executable,
            "-I",
            "-B",
            str(directory.parent / STAGE),
            str(records),
            str(records),
            str(cin),
            str(cout),
        ]
    )
    verify.require(result.returncode == 0, "original cohort staging: " + result.stderr)
    stream = cout / "COHORT249-RECORDS.bin"
    verify.require(stream.read_bytes() == raw, "original cohort stream identity")
    legal = legality(
        binaries["legality_h"], cin, cout, directory / "legality.json", len(raw) // 24
    )
    scalar = columns(binaries["columns_h"], stream, directory / "columns.json", honest)
    return raw, {"records_sha256": expected_sha, "legality": legal, "columns": scalar}


def audit(data, directory):
    binaries = compile_checkers(data, directory)
    word = json.loads(gzip.decompress(data[verify.WORD]))
    verify.validate_scatter(word)
    verify.require(
        word["scatter"][0] == [4, 5, 6, 7, 8] and word["ret"][0] == 472,
        "native exact mutation site",
    )
    results, mutants = {}, []
    for name, added in (
        ("baseline", []),
        ("paired_duplicate", [0, 0]),
        ("single_occurrence", [0]),
    ):
        value = copy.deepcopy(word)
        value["scatter"][0].extend(added)
        raw, results[name] = fixture(
            data, value, directory / name, binaries, name == "baseline"
        )
        if added:
            mutants.append(raw)
    verify.require(mutants[0] == mutants[1], "paired and single native stream identity")
    return {
        "status": "PASS_SCATTER_EXPORT_NATIVE_PARITY_CONTROL",
        "arithmetic_backend": "checked_cpp_int_128_standin",
        "fixtures": results,
        "paired_and_single_records_equal": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    data = verify.sources(verify.ROOT)
    with tempfile.TemporaryDirectory(prefix="scatter-native-") as temporary:
        result = audit(data, Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        expected = json.loads((PACKAGE / "NATIVE.json").read_bytes())
        verify.require(
            json.dumps(result, sort_keys=True, allow_nan=False)
            == json.dumps(expected, sort_keys=True, allow_nan=False),
            "typed native deterministic receipt",
        )
        print(result["status"], "native_legality_accepts=3 scalar_rejects=2")


if __name__ == "__main__":
    main()
