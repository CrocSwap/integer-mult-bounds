#!/usr/bin/env python3
"""Run the unchanged native supplier checkers. Apache-2.0.

Ross Richardson, substantial OpenAI Codex assistance. Checker/exporter authors
retain their source notices. No native checker code is modified or vendored.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("frame524_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ROOT = v.ROOT
SUPPLIER = ROOT / "research/e8-bit-carrier-skeleton"
CHECKERS = SUPPLIER / "code/bit/checkers"
STAGE = SUPPLIER / "code/bit/regression/stage_cohort.py"


def call(args):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    v.need(result.returncode == 0, "native command failed: " + str(args[0]) + "\n" + result.stderr[-4000:])
    return result


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(x) for k, x in value.items() if k not in ("seconds", "local_scalar_stream")}
    if isinstance(value, list):
        return [normalized(x) for x in value]
    return value


def run(write=False):
    pins = v.sources()
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    word = json.loads(gzip.decompress((ROOT / v.WORD).read_bytes()))
    recipe = json.loads((HERE / "CANDIDATE.json").read_text())
    proposed = v.candidate(word, recipe)
    v.need(v.digest(word) == certificate["source_word_canonical_sha256"] and
           v.digest(proposed) == certificate["candidate_word_canonical_sha256"], "native input certificate mismatch")
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    boost = Path(os.environ.get("BOOST_INCLUDE", "/usr/include"))
    v.need((boost / "boost/multiprecision/cpp_int.hpp").exists(), "Set BOOST_INCLUDE to a Boost header root")
    include = ["-I" + str(SUPPLIER / "portable-include"), "-I" + str(CHECKERS), "-I" + str(boost)]
    receipts = {}
    with tempfile.TemporaryDirectory(prefix="frame524-native-") as tmp:
        work = Path(tmp)
        binaries = {}
        jobs = []
        for name, source, defs in (
            ("legality", "legality_h.cpp", []),
            ("five", "columns_h.cpp", ["-DVPORTS=111", "-DRHELP=439"]),
            ("nine", "columns_k.cpp", ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=4"]),
            ("eleven", "columns_k.cpp", ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=5"]),
        ):
            binaries[name] = work / name
            jobs.append(compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9"] + defs + include +
                        [str(CHECKERS / source), "-o", str(binaries[name])])
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(call, jobs))
        for label, current, expected in (("baseline", word, certificate["baseline"]),
                                          ("candidate", proposed, certificate["candidate"])):
            folder = work / label
            folder.mkdir()
            path = folder / "word.json.gz"
            path.write_bytes(gzip.compress(v.canonical(current), mtime=0))
            records = folder / "records"
            call([sys.executable, "-I", "-B", ROOT / v.EXPORT, path, records])
            cin, cout = folder / "in", folder / "out"
            call([sys.executable, "-I", "-B", STAGE, records, records, cin, cout])
            result = {}
            call([binaries["legality"], cin, cout, cout / "legality.json"])
            result["legality"] = normalized(json.loads((cout / "legality.json").read_text()))
            for name, columns, controls in (("five", 883, 6), ("nine", 1327, 18), ("eleven", 1549, 24)):
                output = cout / (name + ".json")
                call([binaries[name], cout / "COHORT249-RECORDS.bin", output])
                receipt = normalized(json.loads(output.read_text()))
                v.need(receipt["status"].startswith("PASS_") and receipt["formal_columns_checked"] == columns,
                       "native columns failure")
                v.need(len(receipt["negative_controls"]) == controls and
                       all(c["rejected"] for c in receipt["negative_controls"]), "native bridge controls incomplete")
                v.need(receipt["local_scalar_additions"] == expected["invoice"]["ADDs"] and
                       receipt["payload_prefix_bits"] == expected["invoice"]["payload_bits"], "native invoice disagreement")
                v.need([int(x["cancellation_free_signed_row_l1_upper"]) for x in receipt["signed_lift_prefix"]] ==
                       [expected["invoice"]["forward_positive_bound"], expected["invoice"]["reverse_positive_bound"]],
                       "native prefix disagreement")
                result[name] = receipt
            legality = result["legality"]
            v.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE" and
                   legality["common_frame_ADDs"] == expected["invoice"]["ADDs"] and
                   legality["rank_mass"] == 5129 and legality["copies"] == legality["erasures"] == 9,
                   "native legality mismatch")
            receipts[label] = result
    receipt = {"status": "PASS_R439_FRAME524_NATIVE", "base_commit": pins["base_commit"],
               "candidate_word_canonical_sha256": certificate["candidate_word_canonical_sha256"],
               "bridge_omission_controls_rejected": 96, "receipts": receipts}
    path = HERE / "NATIVE-CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
        environment = {"python": sys.version, "platform": platform.platform(),
                       "compiler": call(compiler + ["--version"]).stdout,
                       "boost_version_header": (boost / "boost/version.hpp").read_text(),
                       "source_pins_sha256": v.digest(pins)}
        (HERE / "NATIVE-ENVIRONMENT.json").write_text(json.dumps(environment, indent=2) + "\n")
    else:
        v.need(receipt == json.loads(path.read_text()), "native certificate differs from fresh execution")
    print("PASS_R439_FRAME524_NATIVE baseline_and_candidate columns=883/1327/1549 bridge_controls=96")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    run(parser.parse_args().write_certificate)
