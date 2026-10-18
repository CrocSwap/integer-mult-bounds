#!/usr/bin/env python3
"""Unchanged native legality and 5/9/11-stage checks of the quartet word.

Adapted from Gareth Davidson's PR941 harness, itself adapted from Sagar
Thakrar's r420-decoder-sharing/native.py. Substantial OpenAI Codex assistance;
Apache-2.0.
Usage: BOOST_INCLUDE=/path/to/boost python3 native.py NEW_OUTPUT_DIRECTORY
"""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shlex
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
Q = runpy.run_path(str(HERE / "verify.py"))
S, V, C, need = Q["S"], Q["V"], Q["C"], Q["need"]


def run(output):
    Q["source_pins"]()
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    original, parent, previous, target, pairs, columns = S["inputs"]()
    winner = C["load"](HERE / "CERTIFICATE.json")["winner"]
    operations = S["helper_operations"](pairs, winner["indices"], winner["word"])
    candidate = S["construct"](parent, target, columns, operations)
    V["check_bill"](candidate, winner["bill"])
    need(C["digest"](candidate) == "77868e11715b8c7714f0aa67256694ca44f1540e761c090f34897af97b8c525e",
         "candidate canonical digest")
    candidate_path = output / "candidate.json"
    C["write"](candidate_path, candidate)
    hub = S["ROOT"] / C["HUB"]
    checker = hub / "code/bit/checkers"
    boost = Path(os.environ.get("BOOST_INCLUDE", "/usr/include")).resolve()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    options = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
                          "-I" + str(hub / "portable-include"), "-I" + str(checker), "-I" + str(boost)]
    commands = []

    def execute(args, log):
        args = [str(x) for x in args]
        commands.append(args)
        with log.open("x") as stream:
            result = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(log.read_text()[-4000:])

    builds = [("legality", "legality_h.cpp", [])] + [
        ("columns-" + str(k), "columns_k.cpp", ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=" + str(k)])
        for k in (2, 4, 5)]
    for name, source, flags in builds:
        execute(options + flags + ["-MMD", "-MF", output / (name + ".d"),
                                    "-o", output / name, checker / source], output / (name + "-build.log"))
    result, nonadd = {}, {}
    python = [sys.executable, "-I", "-B"]
    for label, path, word in (("previous", S["PRE"] / "candidate.json.gz", previous),
                              ("candidate", candidate_path, candidate)):
        folder = output / label
        folder.mkdir()
        records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
        execute(python + [hub / "code/bit/export_records.py", path, records], folder / "export.log")
        execute(python + [hub / "code/bit/regression/stage_cohort.py", records, records, cin, cout],
                folder / "stage.log")
        execute([output / "legality", cin, cout, cout / "legality.json"], folder / "legality.log")
        legality = C["load"](cout / "legality.json")
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             "native legality status")
        rows = list(struct.iter_unpack("<6i", (records / "249-records.bin").read_bytes()))
        moves = {}
        for row in rows:
            if row[0] == 0:
                moves.setdefault(row[1], []).append(row)
        nonadd[label] = dict(moves=moves, copy_erase=[row for row in rows if row[0] in (2, 3)])
        bill = V["bill"](word)
        need(legality["common_frame_ADDs"] == bill["native_ADDs"], "native ADD cost")
        need(legality["copies"] == legality["erasures"] == 9, "native copy lifecycle")
        staged = {}
        for k in (2, 4, 5):
            name = "columns-" + str(k)
            execute([output / name, cout / "COHORT249-RECORDS.bin", cout / (name + ".json")],
                    folder / (name + ".log"))
            check = C["load"](cout / (name + ".json"))
            status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2 else
                      "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            need(check["status"] == status, "native column status")
            need(check["formal_columns_checked"] == 2 * k * 111 + 439, "formal column coverage")
            need(len(check["stages"]) == 2 * k + 1, "stage coverage")
            need(check["bridge_additions"] == 6 * (k - 1) * 111, "bridge cost")
            need(check["fresh_center_copies"] == 9 * (2 * k + 1), "stage copy cost")
            need(check["payload_prefix_bits"] <= 104, "local payload cap")
            controls = check["negative_controls"]
            need(len(controls) == 6 * (k - 1) and all(c["rejected"] for c in controls), "bridge controls")
            bounds = [int(c["cancellation_free_signed_row_l1_upper"]) for c in check["signed_lift_prefix"]]
            need(bounds == [bill["F"], bill["B"]], "native positive bounds")
            V["guards"](*bounds)
            need(check["local_scalar_additions"] == bill["native_ADDs"], "staged ADD cost")
            staged[str(2 * k + 1)] = {key: check[key] for key in
                ("formal_columns_checked", "bridge_additions", "fresh_center_copies",
                 "payload_prefix_bits", "payload_prefix_upper", "local_raw_H")}
            staged[str(2 * k + 1)]["controls_rejected"] = len(controls)
        result[label] = {key: legality[key] for key in
                         ("records", "common_frame_ADDs", "rank_mass", "paid_histogram", "copies", "erasures")}
        result[label].update(staged=staged, bill=bill, canonical_sha256=C["digest"](word))
    Q["same"](nonadd["previous"], nonadd["candidate"], "register paths or COPY/ERASE changed")
    before, after = result["previous"], result["candidate"]
    need(before["records"] - after["records"] == 3, "native record delta")
    for key in ("rank_mass", "paid_histogram", "copies", "erasures"):
        Q["same"](before[key], after[key], "paid resource change: " + key)
    for stage in ("5", "9", "11"):
        Q["same"](before["staged"][stage]["local_raw_H"], after["staged"][stage]["local_raw_H"],
                  "local raw rank change")
    dependencies = {}
    for name, _, _ in builds:
        text = (output / (name + ".d")).read_text().replace("\\\n", " ")
        for entry in shlex.split(text.split(": ", 1)[1]):
            path = Path(entry).resolve()
            if path.is_relative_to(boost):
                key = str(path.relative_to(boost))
            elif path.is_relative_to(S["ROOT"]):
                key = str(path.relative_to(S["ROOT"]))
            else:
                key = str(path)
            dependencies[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = dict(status="PASS_R439_HELPER_QUARTETS_NATIVE", words=result,
                   python=sys.version, compiler=subprocess.check_output(compiler + ["--version"], text=True),
                   dependencies=dict(sorted(dependencies.items())))
    C["write"](output / "commands.json", commands)
    C["write"](output / "native-report.json", receipt)
    return receipt


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    receipt = run(sys.argv[1])
    print(receipt["status"], "ADDs=11949->11946 columns=883/1327/1549 controls=96/96 no_new_kappa")
