#!/usr/bin/env python3
"""Replay two R420 words with unchanged, pinned native cohort checkers.

Usage: BOOST_INCLUDE=/path/to/boost CXX=c++ python3 native.py BASE.gz CANDIDATE.gz FRESH_OUTPUT
Sagar Thakrar, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys


HUB = Path(__file__).resolve().parents[1] / "e8-bit-carrier-skeleton"
PINS = {
    "code/bit/export_records.py": "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3",
    "code/bit/regression/stage_cohort.py": "6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a",
    "code/bit/checkers/legality_h.cpp": "6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3",
    "code/bit/checkers/columns_k.cpp": "1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2",
    "code/bit/checkers/json.hpp": "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
    "portable-include/bits/stdc++.h": "420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99",
}


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(base_word, candidate_word, output_path):
    certificate = json.loads((Path(__file__).parent / "CERTIFICATE.json").read_text())
    for name, path in (("baseline", base_word), ("candidate", candidate_word)):
        word = json.loads(gzip.decompress(Path(path).read_bytes()))
        content = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
        need(hashlib.sha256(content).hexdigest() == certificate[name + "_canonical_sha256"],
             name + ": word does not match the local certificate")
    for name, digest in PINS.items():
        need(hashlib.sha256((HUB / name).read_bytes()).hexdigest() == digest,
             "native dependency changed: " + name)
    output = Path(output_path).resolve()
    output.mkdir(parents=True, exist_ok=False)
    checker = HUB / "code/bit/checkers"
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    includes = ["-I" + str(HUB / "portable-include"), "-I" + str(checker),
                "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
    commands = []

    def execute(args, log):
        args = [str(x) for x in args]
        commands.append(args)
        with log.open("w") as stream:
            subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, check=True)

    common = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9"] + includes
    execute(common + ["-o", output / "legality", checker / "legality_h.cpp"],
            output / "compile-legality.log")
    execute(common + ["-DVPORTS=120", "-DRHELP=420", "-DKPAIRS=4", "-o",
                      output / "columns", checker / "columns_k.cpp"],
            output / "compile-columns.log")
    result = {"source_sha256": PINS, "python": platform.python_version(),
              "platform": platform.platform(), "compiler": subprocess.check_output(
                  compiler + ["--version"], text=True).splitlines()[0], "words": {}}
    python = [sys.executable, "-I", "-B"]
    for label, word in (("baseline", base_word), ("candidate", candidate_word)):
        folder = output / label
        folder.mkdir()
        records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
        execute(python + [HUB / "code/bit/export_records.py", Path(word).resolve(), records],
                folder / "export.log")
        execute(python + [HUB / "code/bit/regression/stage_cohort.py", records, records,
                          cin, cout], folder / "stage.log")
        execute([output / "legality", cin, cout, cout / "legality.json"],
                folder / "legality.log")
        execute([output / "columns", cout / "COHORT249-RECORDS.bin", cout / "columns.json"],
                folder / "columns.log")
        legality = json.loads((cout / "legality.json").read_text())
        columns = json.loads((cout / "columns.json").read_text())
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
             label + ": legality failed")
        need(legality["copies"] == legality["erasures"] == 9, label + ": copy lifecycle changed")
        need(columns["status"] == "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL",
             label + ": columns failed")
        need(columns["formal_columns_checked"] == 1380 and len(columns["stages"]) == 9,
             label + ": incorrect native coverage")
        need(columns["bridge_additions"] == 2160 and columns["fresh_center_copies"] == 81,
             label + ": stage accounting changed")
        need(columns["payload_prefix_bits"] < 104, label + ": exceeds inherited payload budget")
        controls = columns["negative_controls"]
        need(len(controls) == 18 and all(item["rejected"] for item in controls),
             label + ": omitted bridge control did not reject")
        need(legality["common_frame_ADDs"] == columns["local_scalar_additions"],
             label + ": inconsistent exported addition counts")
        result["words"][label] = {"word_sha256": hashlib.sha256(Path(word).read_bytes()).hexdigest(),
            "canonical_sha256": certificate[label + "_canonical_sha256"],
            "records": legality["records"], "native_ADDs": legality["common_frame_ADDs"],
            "rank_mass": legality["rank_mass"], "paid_histogram": legality["paid_histogram"],
            "local_raw_H": columns["local_raw_H"], "payload_prefix_bits": columns["payload_prefix_bits"],
            "payload_prefix_upper": columns["payload_prefix_upper"],
            "signed_lift_prefix": columns["signed_lift_prefix"],
            "formal_columns_checked": columns["formal_columns_checked"],
            "omitted_bridge_controls_rejected": len(controls)}
    before, after = (result["words"][label] for label in ("baseline", "candidate"))
    need(before["native_ADDs"] == 26916 and after["native_ADDs"] == 26802,
         "expected 114 exported ADD savings")
    need(before["records"] - after["records"] == 114, "unexpected record change")
    for key in ("rank_mass", "paid_histogram", "local_raw_H"):
        need(before[key] == after[key], "paid ranks changed: " + key)
    result["status"] = "PASS_R420_DECODER_SHARING_NATIVE_NINE_STAGE"
    result["commands"] = commands
    (output / "native-report.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    report = run(*sys.argv[1:])
    print(report["status"], "ADDs=26916->26802 columns=1380 controls=18/18 for both words")
