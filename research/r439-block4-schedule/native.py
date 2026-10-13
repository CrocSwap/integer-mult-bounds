"""Optional unchanged native legality and five/nine/eleven-stage replay.

Needs C++17 and Boost headers. For MSVC run in an x64 developer shell.
Gautam Gupta, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT / "research/e8-bit-carrier-skeleton/code/bit"


def run(command, log):
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run([str(x) for x in command], cwd=log.parent, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--cxx", default=os.environ.get("CXX", "c++"))
    parser.add_argument("--boost-include", type=Path, default=os.environ.get("BOOST_INCLUDE", "/usr/include"))
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    need(not work.exists(), "native work directory must be fresh")
    work.mkdir(parents=True)
    run([sys.executable, "-B", HERE / "verify.py", "--out", work / "python"], work / "python.log")
    py = json.loads((work / "python/result.json").read_text())
    includes = [BIT / "checkers", BIT.parents[1] / "portable-include", args.boost_include.resolve()]
    msvc = Path(args.cxx).stem.lower() == "cl"
    binaries = {}
    for name, source, extra in (("legality", "legality_h.cpp", []),
                                ("five", "columns_h.cpp", []),
                                ("nine", "columns_k.cpp", ["KPAIRS=4"]),
                                ("eleven", "columns_k.cpp", ["KPAIRS=5"])):
        definitions = ["HDIM=8", "NCOPY=9", "VPORTS=111", "RHELP=439"] + extra
        exe = work / (name + (".exe" if os.name == "nt" else ""))
        if msvc:
            flags = ["/nologo", "/std:c++17", "/O2", "/EHsc", "/bigobj", "/Fe:" + str(exe)]
            flags += ["/I" + str(p) for p in includes] + ["/D" + x for x in definitions]
        else:
            flags = ["-std=c++17", "-O2", "-o", str(exe)]
            flags += ["-I" + str(p) for p in includes] + ["-D" + x for x in definitions]
        run([args.cxx, *flags, BIT / "checkers" / source], work / ("compile-" + name + ".log"))
        binaries[name] = exe
    result = {}
    for label, word in (("before", ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"),
                         ("after", work / "python/candidate.json.gz")):
        directory = work / label
        directory.mkdir()
        records = directory / "records"
        run([sys.executable, "-B", BIT / "export_records.py", word, records], directory / "export.log")
        need((records / "249-records.bin").read_bytes() == (work / "python" / (label + ".bin")).read_bytes(),
             "independent exporter mismatch")
        cin, cout = directory / "cin", directory / "cout"
        run([sys.executable, "-B", BIT / "regression/stage_cohort.py", records, records, cin, cout], directory / "stage.log")
        run([binaries["legality"], cin, cout, directory / "legality.json"], directory / "legality.log")
        legality = json.loads((directory / "legality.json").read_text())
        need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE", "legality")
        need(legality["common_frame_ADDs"] == py[label]["additions"] and legality["rank_mass"] == 5129, "native cost")
        result[label] = {"legality": legality}
        for name, stages, controls in (("five", 5, 6), ("nine", 9, 18), ("eleven", 11, 24)):
            run([binaries[name], cout / "COHORT249-RECORDS.bin", directory / (name + ".json")], directory / (name + ".log"))
            receipt = json.loads((directory / (name + ".json")).read_text())
            need(receipt["status"].startswith("PASS_NEW_COHORT249_ALL_"), "columns status")
            need(receipt["formal_columns_checked"] == (stages-1)*111 + 439, "formal column count")
            need(len(receipt["stages"]) == stages and len(receipt["negative_controls"]) == controls
                 and all(c["rejected"] for c in receipt["negative_controls"]), "bridge controls")
            need(receipt["local_scalar_additions"] == py[label]["additions"]
                 and receipt["payload_prefix_upper"] == py[label]["payload_upper"], "prefix/scalar mismatch")
            need(dict(receipt["local_raw_H"]) == {int(k): v for k, v in py[label]["paid_profile"].items()}, "native profile")
            receipt.pop("seconds")
            receipt.pop("local_scalar_stream")
            result[label][name] = receipt
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    expected = HERE / "NATIVE-CERTIFICATE.json"
    if args.write_certificate:
        expected.write_bytes(encoded.encode("utf-8"))
    else:
        need(json.loads(expected.read_text()) == json.loads(encoded), "stored native certificate mismatch")
    (work / "result.json").write_bytes(encoded.encode("utf-8"))
    print("PASS_R439_BLOCK4_NATIVE before+after columns=883/1327/1549 bridge_controls=6/18/24 payload_bits=93")


if __name__ == "__main__":
    main()
