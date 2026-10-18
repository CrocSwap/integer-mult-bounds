#!/usr/bin/env python3
"""Two words through unchanged native legality and 5/9/11-stage checkers.

Adapted from the PR980/926 harness by Gareth Davidson, following Sagar Thakrar's
PR837 harness, and from Sricharan Vagvala's PR967 harness. Apache-2.0.
Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
"""
import os
from pathlib import Path
import runpy
import shlex
import struct
import subprocess
import sys

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, same = C["need"], C["same"]


def run(root, words_dir, prices, output):
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

    flags = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9"] + includes
    execute(flags + ["-o", output / "legality", checker / "legality_h.cpp"], output / "compile-legality.log")
    for k in (2, 4, 5):
        execute(flags + ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=" + str(k),
                         "-o", output / ("columns-" + str(k)), checker / "columns_k.cpp"],
                output / ("compile-columns-" + str(k) + ".log"))
    # Original exporters contain assertions: keep them enabled even under -O.
    python = [sys.executable, "-I", "-B"]
    results, nonadd = {}, {}
    for label in ("0", "1"):
        print("native GL5 word", label, flush=True)
        folder = output / label
        folder.mkdir()
        records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
        execute(python + [hub / "code/bit/export_records.py", Path(words_dir) / (label + ".json.gz"), records],
                folder / "export.log")
        execute(python + [hub / "code/bit/regression/stage_cohort.py", records, records, cin, cout],
                folder / "stage.log")
        execute([output / "legality", cin, cout, cout / "legality.json"], folder / "legality.log")
        legality = C["load"](cout / "legality.json")
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             "native legality")
        need(legality["copies"] == legality["erasures"] == 9, "native COPY lifetime")
        record_rows = list(struct.iter_unpack("<6i", (records / "249-records.bin").read_bytes()))
        movements = {}
        for row in record_rows:
            if row[0] == 0:
                movements.setdefault(str(row[1]), []).append(list(row))
        nonadd[label] = {"moves": movements,
                         "copy_erase": [list(x) for x in record_rows if x[0] in (2, 3)]}
        stages = {}
        for k in (2, 4, 5):
            name = "columns-" + str(k)
            execute([output / name, cout / "COHORT249-RECORDS.bin", cout / (name + ".json")],
                    folder / (name + ".log"))
            col = C["load"](cout / (name + ".json"))
            expected = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2
                        else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            need(col["status"] == expected, "native columns")
            need(col["formal_columns_checked"] == 2 * k * 111 + 439, "native column coverage")
            need(len(col["stages"]) == 2 * k + 1, "native stage coverage")
            need(col["bridge_additions"] == 6 * (k - 1) * 111, "native bridge bill")
            need(col["fresh_center_copies"] == 9 * (2 * k + 1)
                 and col["reverse_fresh_center_copies"] == 9 * k,
                 "native staged COPY bill")
            addition_key = "five_stage_additions" if k == 2 else "stage_additions"
            need(col[addition_key] == (2 * k + 1) * prices[label]["ADDs"], "all scalar stages billed")
            need(col["local_scalar_additions"] == legality["common_frame_ADDs"] == prices[label]["ADDs"],
                 "native ADD agreement")
            need(col["payload_prefix_bits"] == prices[label]["local_bits"] <= 104, "native local precision")
            need(int(col["payload_prefix_upper"]) == int(prices[label]["local_upper"]), "native exact local bill")
            same([int(x["cancellation_free_signed_row_l1_upper"]) for x in col["signed_lift_prefix"]],
                 [prices[label]["F"], prices[label]["B"]], "native literal prefix agreement")
            controls = col["negative_controls"]
            need(len(controls) == 6 * (k - 1) and all(x["rejected"] is True for x in controls),
                 "native omitted-bridge controls")
            stages[str(2 * k + 1)] = {key: col[key] for key in (
                "formal_columns_checked", "bridge_additions", "fresh_center_copies", "reverse_fresh_center_copies",
                "signed_lift_prefix", "payload_prefix_bits", "payload_prefix_upper", "local_raw_H", "stages")}
            stages[str(2 * k + 1)].update(scalar_ADDs=col[addition_key], controls_rejected=len(controls))
        results[label] = {key: legality[key] for key in (
            "records", "common_frame_ADDs", "rank_mass", "paid_histogram", "copies", "erasures")}
        results[label]["staged"] = stages
        results[label]["nine_stage_admitted"] = prices[label]["admitted"]
    baseline = results["0"]
    for label, after in results.items():
        same(nonadd["0"], nonadd[label], "per-register frame path or copy lifetime changed")
        need(baseline["records"] - after["records"] == prices["0"]["ADDs"] - prices[label]["ADDs"], "unexpected record delta")
        for key in ("rank_mass", "paid_histogram", "copies", "erasures"):
            same(baseline[key], after[key], "paid resource changed: " + key)
        for stage in ("5", "9", "11"):
            same(baseline["staged"][stage]["local_raw_H"], after["staged"][stage]["local_raw_H"],
                 "local raw ranks changed")
    C["write"](output / "commands.json", commands)
    C["write"](output / "native-report.json", results)
    return results
