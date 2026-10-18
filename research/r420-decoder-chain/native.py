#!/usr/bin/env python3
"""Native nine-stage replay, adapted from Sagar Thakrar's PR708 native.py.
Adam Gall (@adamgall), substantial OpenAI Codex assistance; Apache-2.0.
Unchanged predecessor exporter, legality checker, and full formal-column checker.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys

from verify import HERE, ROOT, canonical, need

HUB = ROOT / "research/e8-bit-carrier-skeleton"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("words", type=Path)
    parser.add_argument("output", type=Path, help="fresh output directory")
    args = parser.parse_args()
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    pins = json.loads((HERE / "SOURCES.json").read_text())["files_sha256"]
    for path, digest in pins.items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "source pin: " + path)
    words = {name: (args.words / (name + ".json.gz")).resolve() for name in ("baseline", "candidate")}
    for name, path in words.items():
        word = json.loads(gzip.decompress(path.read_bytes()))
        need(hashlib.sha256(canonical(word)).hexdigest() == certificate[name + "_canonical_sha256"],
             "native input mismatch: " + name)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    checker = HUB / "code/bit/checkers"
    common = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
                         "-I" + str(HUB / "portable-include"), "-I" + str(checker),
                         "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]

    def run(command, log):
        with log.open("w") as stream:
            subprocess.run(list(map(str, command)), stdout=stream, stderr=subprocess.STDOUT, check=True)

    run(common + ["-o", output / "legality", checker / "legality_h.cpp"], output / "compile-legality.log")
    run(common + ["-DVPORTS=120", "-DRHELP=420", "-DKPAIRS=4", "-o", output / "columns",
                  checker / "columns_k.cpp"], output / "compile-columns.log")
    result = {"python": platform.python_version(), "platform": platform.platform(),
              "compiler": subprocess.check_output(compiler + ["--version"], text=True).splitlines()[0],
              "words": {}}
    python = [sys.executable, "-I", "-B"]
    for name, word in words.items():
        folder = output / name
        folder.mkdir()
        records, cin, cout = [folder / x for x in ("records", "cin", "cout")]
        run(python + [HUB / "code/bit/export_records.py", word, records], folder / "export.log")
        run(python + [HUB / "code/bit/regression/stage_cohort.py", records, records, cin, cout], folder / "stage.log")
        run([output / "legality", cin, cout, cout / "legality.json"], folder / "legality.log")
        run([output / "columns", cout / "COHORT249-RECORDS.bin", cout / "columns.json"], folder / "columns.log")
        legality = json.loads((cout / "legality.json").read_text())
        columns = json.loads((cout / "columns.json").read_text())
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE", "legality")
        need(columns["status"] == "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL", "columns")
        need(legality["copies"] == legality["erasures"] == 9, "COPY/ERASE lifecycle")
        need(columns["formal_columns_checked"] == 1380 and len(columns["stages"]) == 9, "formal coverage")
        need(columns["bridge_additions"] == 2160 and columns["fresh_center_copies"] == 81, "stage charges")
        need(len(columns["negative_controls"]) == 18 and all(c["rejected"] for c in columns["negative_controls"]),
             "omitted bridge controls")
        need(legality["common_frame_ADDs"] == columns["local_scalar_additions"] ==
             certificate["native_additions_" + ("before" if name == "baseline" else "after")], "ADD count")
        need(columns["payload_prefix_bits"] < 104, "native payload budget exceeded")
        result["words"][name] = {
            "canonical_sha256": certificate[name + "_canonical_sha256"],
            "native_ADDs": legality["common_frame_ADDs"], "records": legality["records"],
            "rank_mass": legality["rank_mass"], "paid_histogram": legality["paid_histogram"],
            "local_raw_H": columns["local_raw_H"], "payload_prefix_bits": columns["payload_prefix_bits"],
            "payload_prefix_upper": columns["payload_prefix_upper"],
            "signed_lift_prefix": columns["signed_lift_prefix"],
            "formal_columns_checked": columns["formal_columns_checked"],
            "omitted_bridge_controls_rejected": 18}
    for key in ("rank_mass", "paid_histogram", "local_raw_H"):
        need(result["words"]["baseline"][key] == result["words"]["candidate"][key], "paid profile changed")
    result["status"] = "PASS_R420_DECODER_CHAIN_NATIVE"
    (output / "NATIVE.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_R420_DECODER_CHAIN_NATIVE words=2 stages=9 columns=1380 controls=18/18 "
          "payload_bits=" + "/".join(str(result["words"][x]["payload_prefix_bits"]) for x in words))


if __name__ == "__main__":
    main()
