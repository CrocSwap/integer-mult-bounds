#!/usr/bin/env python3
"""Optional unchanged C++ replay. @ellipsi2 with OpenAI Codex; Apache-2.0."""
import argparse
import gzip
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("target_star", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
CK = v.ROOT / "research/e8-bit-carrier-skeleton/code/bit/checkers"
STAGE = v.ROOT / "research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py"
PORTABLE = v.ROOT / "research/e8-bit-carrier-skeleton/portable-include"


def execute(args, log, reject=False):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr)
    v.need((result.returncode != 0) if reject else (result.returncode == 0),
           "unexpected command result; see " + str(log))
    if reject:
        v.need("local defining-decoder full formal column" in result.stderr,
               "control failed for an unrelated reason; see " + str(log))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boost-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new output directory")
    parser.add_argument("--check", type=Path, help="compare proof-relevant receipts, ignoring environment")
    args = parser.parse_args()
    sources = v.check_pins()
    v.need((args.boost_include / "boost/multiprecision/cpp_int.hpp").is_file(), "Boost headers missing")
    args.output.mkdir()  # never overwrite an earlier replay
    out = args.output.resolve()
    compiler = os.environ.get("CXX", "c++")
    flags = [compiler, "-O2", "-std=c++17", "-include", "algorithm", "-DHDIM=8", "-DNCOPY=9",
             "-DVPORTS=120", "-DRHELP=420", "-I" + str(CK), "-I" + str(PORTABLE),
             "-I" + str(args.boost_include.resolve())]
    binaries = {}
    for name, source, extra in [("legality", "legality_h.cpp", [])] + [
            ("columns%d" % k, "columns_k.cpp", ["-DKPAIRS=%d" % k]) for k in (2, 4, 5)]:
        binary = out / name
        execute(flags + extra + [CK / source, "-o", binary], out / (name + "-compile.log"))
        binaries[name] = binary
    original = json.loads(gzip.decompress((v.ROOT / v.WORD).read_bytes()))
    candidate, _, _, _ = v.synthesize(original)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    v.need(v.digest(sources) == certificate["source_manifest_sha256"], "source manifest binding")
    v.need(v.digest(candidate) == certificate["candidate_content_sha256"], "candidate hash")
    receipts = {}
    for label, word, pricekey in [("baseline", original, "original"), ("candidate", candidate, "candidate")]:
        work = out / label
        work.mkdir()
        records = work / "records"
        records.mkdir()
        v.export(word, records)
        cin, cout = work / "cin", work / "cout"
        execute([sys.executable, "-I", "-B", STAGE, records, records, cin, cout], work / "stage.log")
        execute([binaries["legality"], cin, cout, work / "legality.json"], work / "legality.log")
        legality = json.loads((work / "legality.json").read_text())
        expected = certificate[pricekey]
        v.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
               "native legality status")
        for key, price in [("records", "records"), ("common_frame_ADDs", "scalar_additions"),
                           ("nested_MOVEs", "moves"), ("copies", "copies"), ("rank_mass", "rank_mass")]:
            v.need(legality[key] == expected[price], "native legality price: " + key)
        columns = []
        stream = cout / "COHORT249-RECORDS.bin"
        for k in (2, 4, 5):
            receipt = work / ("columns%d.json" % k)
            execute([binaries["columns%d" % k], stream, receipt], work / ("columns%d.log" % k))
            result = json.loads(receipt.read_text())
            v.need(result["formal_columns_checked"] == 2*k*120+420, "native column count")
            v.need(result["local_scalar_additions"] == expected["scalar_additions"], "native ADD count")
            v.need(result["payload_prefix_bits"] == expected["payload_bits"]
                   and int(result["payload_prefix_upper"]) == expected["payload_upper"], "native prefix")
            bounds = [int(x["cancellation_free_signed_row_l1_upper"]) for x in result["signed_lift_prefix"]]
            v.need(bounds == [expected["forward_positive_bound"], expected["inverse_positive_bound"]],
                   "native directional bounds")
            v.need(dict(result["local_raw_H"]) == {int(a): b for a, b in expected["local_histogram"].items()},
                   "native histogram")
            v.need(len(result["negative_controls"]) == 6*(k-1)
                   and all(x["rejected"] for x in result["negative_controls"]), "native bridge controls")
            result.pop("seconds")
            result.pop("local_scalar_stream")
            columns.append(result)
        receipts[label] = dict(legality=legality, columns=columns)
        if label == "candidate":
            raw = stream.read_bytes()
            records6 = [raw[i:i+24] for i in range(0, len(raw), 24)]
            first = next(i for i, r in enumerate(v.struct.iter_unpack("<6i", raw)) if r[0] == 1)
            damaged = work / "missing-preparation.bin"
            damaged.write_bytes(b"".join(records6[:first] + records6[first+1:]))
            for k in (2, 4, 5):
                execute([binaries["columns%d" % k], damaged, work / ("must-not-pass%d.json" % k)],
                        work / ("missing-preparation%d.log" % k), reject=True)
            receipts[label]["missing_preparation_rejected_at_stages"] = [5, 9, 11]
    report = dict(status="PASS_R420_TARGET_STAR_NATIVE", receipts=receipts,
                  environment=dict(python=sys.version, platform=platform.platform(),
                      compiler=subprocess.check_output([compiler, "--version"], text=True).strip(),
                      boost_version_header_sha256=v.hashlib.sha256(
                          (args.boost_include / "boost/version.hpp").read_bytes()).hexdigest()))
    if args.check:
        expected = json.loads(args.check.read_text())
        v.need(report["status"] == expected["status"] and report["receipts"] == expected["receipts"],
               "native certificate mismatch")
    v.write_json(out / "NATIVE.json", report)
    print("PASS_R420_TARGET_STAR_NATIVE both_words=5/9/11 columns=900/1380/1620 missing_preparation=rejected")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("REJECT_R420_TARGET_STAR_NATIVE:", error, file=sys.stderr)
        sys.exit(1)
