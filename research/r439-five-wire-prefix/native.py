#!/usr/bin/env python3
"""Unmodified native legality and 5/9/11-stage column checks, both R439 words, extending PR904.

Harness adapted from Sagar Thakrar's research/r420-decoder-sharing/native.py.
Original harness: Gareth Davidson (@bitplane), OpenAI Codex assistance.
Adaptation: Ross Richardson, substantial OpenAI Codex assistance. Apache-2.0.
"""
import os
from pathlib import Path
import runpy
import shlex
import struct
import subprocess
import sys

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def run(root, baseline, candidate, output):
    C["pins"](root)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    hub = Path(root).resolve() / C["HUB"]
    checker = hub / "code/bit/checkers"
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    includes = ["-I" + str(hub / "portable-include"), "-I" + str(checker),
                "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
    commands = []

    def execute(args, log):
        args = [str(x) for x in args]
        commands.append(args)
        with log.open("x") as stream:
            subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, check=True)

    common = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9"] + includes
    execute(common + ["-o", output / "legality", checker / "legality_h.cpp"],
            output / "compile-legality.log")
    for k in (2, 4, 5):
        execute(common + ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=" + str(k),
                          "-o", output / ("columns-" + str(k)), checker / "columns_k.cpp"],
                output / ("compile-columns-" + str(k) + ".log"))
    python = [sys.executable, "-I", "-B"]
    result, nonadd = {}, {}
    for label, word in (("baseline", baseline), ("candidate", candidate)):
        print("native", label, flush=True)
        folder = output / label
        folder.mkdir()
        records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
        execute(python + [hub / "code/bit/export_records.py", Path(word).resolve(), records],
                folder / "export.log")
        execute(python + [hub / "code/bit/regression/stage_cohort.py", records, records, cin, cout],
                folder / "stage.log")
        execute([output / "legality", cin, cout, cout / "legality.json"], folder / "legality.log")
        legality = C["load"](cout / "legality.json")
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             "native legality")
        need(legality["copies"] == legality["erasures"] == 9, "native copy lifecycle")
        # Per-register MOVE sequences, including ranks, and unchanged COPY/ERASE blocks.
        record_rows = list(struct.iter_unpack("<6i", (records / "249-records.bin").read_bytes()))
        movements = {}
        for row in record_rows:
            if row[0] == 0:
                movements.setdefault(str(row[1]), []).append(list(row))
        nonadd[label] = {"moves": movements, "copy_erase": [list(x) for x in record_rows if x[0] in (2, 3)]}
        columns_receipts = {}
        for k in (2, 4, 5):
            name = "columns-" + str(k)
            execute([output / name, cout / "COHORT249-RECORDS.bin", cout / (name + ".json")],
                    folder / (name + ".log"))
            columns = C["load"](cout / (name + ".json"))
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            need(columns["status"] == expected_status, "native columns")
            need(columns["formal_columns_checked"] == 2 * k * 111 + 439, "column coverage")
            need(len(columns["stages"]) == 2 * k + 1, "stage coverage")
            need(columns["bridge_additions"] == 6 * (k - 1) * 111, "bridge cost")
            need(columns["fresh_center_copies"] == 9 * (2 * k + 1), "stage COPY cost")
            need(columns["payload_prefix_bits"] <= 104, "inherited prefix cap")
            controls = columns["negative_controls"]
            need(len(controls) == 6 * (k - 1) and all(x["rejected"] is True for x in controls),
                 "omitted bridge controls")
            need(legality["common_frame_ADDs"] == columns["local_scalar_additions"], "ADD agreement")
            columns_receipts[str(2 * k + 1)] = {key: columns[key] for key in (
                "formal_columns_checked", "bridge_additions", "fresh_center_copies", "reverse_fresh_center_copies",
                "signed_lift_prefix", "payload_prefix_bits", "payload_prefix_upper", "local_raw_H", "stages")}
            columns_receipts[str(2 * k + 1)]["controls_rejected"] = len(controls)
        result[label] = {key: legality[key] for key in ("records", "common_frame_ADDs", "rank_mass", "paid_histogram",
                                                       "copies", "erasures")}
        result[label]["staged"] = columns_receipts
    need(C["canonical"](nonadd["baseline"]) == C["canonical"](nonadd["candidate"]), "frame paths changed")
    before, after = result["baseline"], result["candidate"]
    need(before["common_frame_ADDs"] == 24051 and after["common_frame_ADDs"] == 23711, "340 native ADD savings")
    need(before["records"] - after["records"] == 340, "unexpected record changes")
    for key in ("rank_mass", "paid_histogram", "copies", "erasures"):
        need(before[key] == after[key], "paid resources changed: " + key)
    for stage in ("5", "9", "11"):
        old, new = before["staged"][stage], after["staged"][stage]
        need(old["local_raw_H"] == new["local_raw_H"], "local raw ranks changed")
        for a, b in zip(old["signed_lift_prefix"], new["signed_lift_prefix"]):
            need(int(b["cancellation_free_signed_row_l1_upper"]) <= int(a["cancellation_free_signed_row_l1_upper"]),
                 "positive prefix grew")
    C["write"](output / "commands.json", commands)
    C["write"](output / "native-report.json", result)
    return result
