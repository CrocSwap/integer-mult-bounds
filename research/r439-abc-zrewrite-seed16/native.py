#!/usr/bin/env python3
"""Fresh native baseline/candidate checks; adapted from PR1122, Apache-2.0.

Gareth Davidson's PR1122 harness follows PR980/926, Sagar Thakrar PR837,
and Sricharan Vagvala PR967. Adaptation with substantial OpenAI Codex help.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verification():
    spec = importlib.util.spec_from_file_location("seed16_verify", HERE / "verify.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def run(output):
    V = verification()
    V.same(V.run(), V.load(HERE / "CERTIFICATE.json"), "finite certificate")
    paths = {"baseline": HERE / "vendor/pr1122/candidate.json.gz",
             "candidate": HERE / "CANDIDATE-WORD.json"}
    words = {name: V.load(path) for name, path in paths.items()}
    prices = {name: V.price(word) for name, word in words.items()}
    for name, price in prices.items():
        V.need(int(price["local_upper"]) < 1 << 104, name + " local precision")
        V.need(int(price["nine_upper"]) < 1 << 192, name + " nine-stage precision")
    V.need(prices["baseline"]["ADDs"] == 10652, "frozen complete baseline invoice")
    for key in words["baseline"]:
        if key not in ("A", "B", "C"):
            V.same(words["baseline"][key], words["candidate"][key], "unchanged field " + key)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    hub = ROOT / "research/e8-bit-carrier-skeleton"
    checker = hub / "code/bit/checkers"
    flags = shlex.split(os.environ.get("CXX", "c++")) + [
        "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
        "-I" + str(hub / "portable-include"), "-I" + str(checker),
        "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
    commands = []

    def execute(args, log):
        args = [str(x) for x in args]
        commands.append(args)
        with Path(log).open("x") as stream:
            subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, check=True)

    execute(flags + ["-o", output / "legality", checker / "legality_h.cpp"],
            output / "compile-legality.log")
    for k in (2, 4, 5):
        execute(flags + ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=" + str(k),
                         "-o", output / ("columns-" + str(k)), checker / "columns_k.cpp"],
                output / ("compile-columns-" + str(k) + ".log"))
    # Inherited exporters use assertions: never propagate -O to them.
    python = [sys.executable, "-I", "-B"]
    reports, nonadd = {}, {}
    inherited = V.load(HERE / "vendor/pr1122/EXPECTED.json")["native"]["7"]
    for label in ("baseline", "candidate"):
        print("native word " + label, flush=True)
        folder = output / label
        folder.mkdir()
        records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
        execute(python + [hub / "code/bit/export_records.py", paths[label], records],
                folder / "export.log")
        execute(python + [hub / "code/bit/regression/stage_cohort.py", records, records, cin, cout],
                folder / "stage.log")
        execute([output / "legality", cin, cout, cout / "legality.json"], folder / "legality.log")
        legality = V.load(cout / "legality.json")
        V.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
               "native legality status")
        V.need(legality["copies"] == legality["erasures"] == 9, "native COPY lifetime")
        V.need(legality["rank_mass"] == 5129, "true E8 paid rank mass")
        V.same(legality["paid_histogram"], inherited["paid_histogram"], "inherited true paid histogram")
        V.need(legality["common_frame_ADDs"] == prices[label]["ADDs"], "native local ADD invoice")
        rows = list(struct.iter_unpack("<6i", (records / "249-records.bin").read_bytes()))
        movements = {}
        for row in rows:
            if row[0] == 0:
                movements.setdefault(str(row[1]), []).append(list(row))
        nonadd[label] = {"moves": movements, "copy_erase": [list(row) for row in rows if row[0] in (2, 3)]}
        stages = {}
        for k in (2, 4, 5):
            name = "columns-" + str(k)
            execute([output / name, cout / "COHORT249-RECORDS.bin", cout / (name + ".json")],
                    folder / (name + ".log"))
            col = V.load(cout / (name + ".json"))
            expected = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2
                        else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            V.need(col["status"] == expected, "native columns status")
            V.need(col["formal_columns_checked"] == 2 * k * 111 + 439, "native column coverage")
            V.need(len(col["stages"]) == 2 * k + 1, "native stage coverage")
            V.need(col["bridge_additions"] == 6 * (k - 1) * 111, "native bridge invoice")
            V.need(col["fresh_center_copies"] == 9 * (2 * k + 1)
                   and col["reverse_fresh_center_copies"] == 9 * k, "native staged COPY invoice")
            addition_key = "five_stage_additions" if k == 2 else "stage_additions"
            V.need(col[addition_key] == (2 * k + 1) * prices[label]["ADDs"], "all scalar stages billed")
            V.need(col["local_scalar_additions"] == prices[label]["ADDs"], "native local ADD agreement")
            V.need(col["payload_prefix_bits"] == prices[label]["local_bits"] <= 104, "native local precision")
            V.need(int(col["payload_prefix_upper"]) == int(prices[label]["local_upper"]), "exact local precision invoice")
            V.same([int(x["cancellation_free_signed_row_l1_upper"]) for x in col["signed_lift_prefix"]],
                   [prices[label]["F"], prices[label]["B"]], "native literal F/B agreement")
            controls = col["negative_controls"]
            V.need(len(controls) == 6 * (k - 1) and all(x["rejected"] is True for x in controls),
                   "native omitted-bridge controls")
            stages[str(2 * k + 1)] = {key: col[key] for key in (
                "formal_columns_checked", "bridge_additions", "fresh_center_copies",
                "reverse_fresh_center_copies", "payload_prefix_bits", "payload_prefix_upper", "local_raw_H")}
            stages[str(2 * k + 1)].update(scalar_ADDs=col[addition_key],
                total_ADDs=col[addition_key] + col["bridge_additions"], controls_rejected=len(controls))
        reports[label] = {key: legality[key] for key in (
            "records", "common_frame_ADDs", "rank_mass", "paid_histogram", "copies", "erasures")}
        reports[label].update(staged=stages, literal_price=prices[label],
            canonical_word_sha256=hashlib.sha256(canonical(words[label])).hexdigest(),
            nonadd_record_sha256=hashlib.sha256(canonical(nonadd[label])).hexdigest())
    V.same(nonadd["baseline"], nonadd["candidate"], "every register MOVE path and COPY/ERASE record")
    V.need(reports["baseline"]["records"] - reports["candidate"]["records"] ==
           prices["baseline"]["ADDs"] - prices["candidate"]["ADDs"], "unexpected non-ADD record saving")
    for stage in ("5", "9", "11"):
        V.same(reports["baseline"]["staged"][stage]["local_raw_H"],
               reports["candidate"]["staged"][stage]["local_raw_H"], "true local raw ranks unchanged")
    write(output / "commands.json", commands)
    write(output / "native-report.json", reports)
    return {"status": "PASS_R439_ABC_ZREWRITE_NATIVE", "words": reports,
            "complete_frame_paths_identical": True, "copy_erase_records_identical": True,
            "controls_rejected": 96, "no_new_kappa": True,
            "scope": "Finite physical/native 5/9/11-stage coverage; local104/nine192 admission only."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="seed16-native-") as temporary:
        report = run(args.output or Path(temporary) / "run")
        if args.write_certificate:
            write(HERE / "NATIVE.json", report)
        else:
            verification().same(report, verification().load(HERE / "NATIVE.json"), "native certificate")
    print("PASS_R439_ABC_ZREWRITE_NATIVE: 2 words; 5/9/11 stages; 96 bridge controls; rank_mass5129; no_new_kappa")


if __name__ == "__main__":
    main()
