#!/usr/bin/env python3
"""Replay frame281's two words with unchanged native legality/column checkers.

Adapted from Ross Richardson's research/r439-frame267-seed01/native.py,
itself adapted from Ali Romman PR688, with substantial OpenAI Codex assistance.
The underlying exporter/cohort/checker authors retain their source attribution.
This frame281 adaptation was prepared with OpenAI Codex assistance. Apache-2.0.

Requires a GCC/Clang-compatible C++17 compiler (CXX, default c++) and Boost
headers (BOOST_INCLUDE, default /usr/include). No dependency is installed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile


def compiler_command():
    value = os.environ.get("CXX", "c++")
    # An unquoted Windows executable path may contain spaces. Shell-style
    # commands such as "ccache c++" continue to work on other platforms.
    return [value] if Path(value).is_file() else shlex.split(value)


def prefix_price(data):
    """Price the pinned local and nine-stage expressions from native F/B bounds."""
    prefix = data["signed_lift_prefix"]
    if len(prefix) != 2 or [row["reverse"] for row in prefix] != [False, True]:
        raise ValueError("Signed prefix directions missing or reordered")
    forward, backward = (int(row["cancellation_free_signed_row_l1_upper"]) for row in prefix)
    if forward < 1 or backward < 1:
        raise ValueError("Invalid signed prefix bound")
    local = 64 * forward ** 3 * backward ** 2
    nine = (1 << 18) * forward ** 5 * backward ** 4
    if int(data["payload_prefix_upper"]) != local or data["payload_prefix_bits"] != local.bit_length():
        raise ValueError("Native payload receipt disagrees with its F/B bounds")
    if local >= 1 << 104 or nine >= 1 << 192:
        raise ValueError("Local 104-bit or nine-stage 192-bit precision charge exceeded")
    return {"forward": str(forward), "backward": str(backward),
            "local_payload_upper": str(local), "local_payload_bits": local.bit_length(),
            "nine_stage_upper": str(nine), "nine_stage_bits": nine.bit_length()}


def run(root, out):
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    python = [sys.executable, "-I", "-B"]
    compiler = compiler_command()
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir()
    suffix = ".exe" if os.name == "nt" else ""
    commands = []

    def binary(name):
        return bindir / (name + suffix)

    def call(name, command):
        command = list(map(str, command))
        commands.append(command)
        (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        with (out / (name + ".log")).open("x", encoding="utf-8") as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)

    call("compile-legality", compiler + flags + ["-o", binary("legality"), checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             binary("columns" + str(pairs)), checkers / "columns_k.cpp"])
    results, counts, nonadd = {}, {}, {}
    for name in ("original", "replacement"):
        base = out / name
        records, cin, cout = (base / item for item in ("records", "cin", "cout"))
        call(name + "-export", python + [bit / "export_records.py", out / (name + ".json.gz"), records])
        rows = list(struct.iter_unpack("<6i", (records / "249-records.bin").read_bytes()))
        counts[name] = sum(row[0] == 1 for row in rows)
        moves = {}
        for row in rows:
            if row[0] == 0:
                moves.setdefault(row[1], []).append(row)
        nonadd[name] = {"moves": moves, "copy_erase": [row for row in rows if row[0] in (2, 3)]}
        call(name + "-cohort", python + [bit / "regression/stage_cohort.py", records, records, cin, cout])
        call(name + "-legality", [binary("legality"), cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        if legality["status"] != "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE":
            raise ValueError("Legality did not pass")
        if legality["common_frame_ADDs"] != counts[name] or legality["copies"] != 9 or legality["erasures"] != 9:
            raise ValueError("Native legality ADD count or lifecycle differs")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [binary("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            if data["status"] != expected_status:
                raise ValueError("Formal columns did not pass")
            if (len(data["negative_controls"]) != 6 * (pairs - 1)
                    or not all(c["rejected"] is True for c in data["negative_controls"])):
                raise ValueError("A bridge control failed")
            if data["formal_columns_checked"] != 222 * pairs + 439 or len(data["stages"]) != 2 * pairs + 1:
                raise ValueError("Wrong formal column or stage count")
            if (data["local_scalar_additions"] != counts[name]
                    or data["bridge_additions"] != 6 * (pairs - 1) * 111
                    or data["fresh_center_copies"] != 9 * (2 * pairs + 1)):
                raise ValueError("Native stage cost differs from exported records")
            price = prefix_price(data)
            if "prefix_price" in results[name] and results[name]["prefix_price"] != price:
                raise ValueError("Native local prefix bounds disagree across stage counts")
            results[name]["prefix_price"] = price
            data.pop("seconds", None)
            data.pop("local_scalar_stream", None)
            results[name]["stages"][str(2 * pairs + 1)] = data
    if counts["original"] <= counts["replacement"]:
        raise ValueError("Frame281 did not save exported ADDs")
    if nonadd["original"] != nonadd["replacement"]:
        raise ValueError("Per-register MOVE paths or COPY/ERASE events changed")
    old_legal, new_legal = (results[name]["legality"] for name in ("original", "replacement"))
    for key in ("rank_mass", "paid_histogram", "copies", "erasures"):
        if old_legal[key] != new_legal[key]:
            raise ValueError("Paid legality resource changed: " + key)
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("original", "replacement"))
        if old["local_raw_H"] != new["local_raw_H"]:
            raise ValueError("Paid profile differs")
    return results


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--output", type=Path, help="new output directory; preserve all native logs")
    args = parser.parse_args()
    compiler = compiler_command()
    if not compiler or not shutil.which(compiler[0]):
        raise ValueError("Set CXX to an available GCC/Clang-compatible C++17 compiler")
    include = Path(os.environ.get("BOOST_INCLUDE", "/usr/include"))
    if not (include / "boost/multiprecision/cpp_int.hpp").is_file():
        raise ValueError("Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp")
    pins = json.loads((here / "SOURCES.json").read_text())
    for path, digest in pins["files"].items():
        content = (root / path).read_bytes()
        if not path.endswith(".gz"):
            content = content.replace(b"\r\n", b"\n")
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("source hash mismatch: " + path)
    with tempfile.TemporaryDirectory(prefix="r439-frame281-native-") as temporary:
        work = args.output.resolve() if args.output else Path(temporary) / "work"
        # The verifier refuses an existing path and emits both bound words.
        subprocess.run([sys.executable, "-I", "-B", str(here / "verify.py"), "--output", str(work)], check=True)
        (work / "ENVIRONMENT.json").write_text(json.dumps({"python": sys.version, "platform": platform.platform(),
            "compiler": subprocess.check_output(compiler + ["--version"], text=True),
            "boost_include": str(include)}, indent=2) + "\n", encoding="utf-8")
        result = run(root, work)
        old_price, new_price = (result[name]["prefix_price"] for name in ("original", "replacement"))
        growth = {key: int(new_price[key]) > int(old_price[key])
                  for key in ("forward", "backward", "local_payload_upper", "nine_stage_upper")}
        receipt = {"schema": "r439-frame281-native/1", "words": result,
                   "prefix_growth": growth,
                   "normalization": "Only seconds and local_scalar_stream removed; all other native fields retained. Derived prefix prices and growth flags are separate."}
        path = here / "NATIVE-CERTIFICATE.json"
        if args.write_certificate:
            path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        elif not path.is_file():
            raise ValueError("Native replay passed; use --write-certificate to record the first native receipt")
        elif receipt != json.loads(path.read_text()):
            raise ValueError("native certificate mismatch")
        before, after = (result[name]["legality"]["common_frame_ADDs"] for name in ("original", "replacement"))
        print(f"PASS_R439_FRAME281_NATIVE words=2 columns=883/1327/1549 bridge_controls=96 ADDs={before}->{after}")
        print("prefix_growth=" + json.dumps(growth, sort_keys=True))
        print(f"prefix_bits local={old_price['local_payload_bits']}->{new_price['local_payload_bits']}/104 "
              f"nine={old_price['nine_stage_bits']}->{new_price['nine_stage_bits']}/192")


if __name__ == "__main__":
    main()
