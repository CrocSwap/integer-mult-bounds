#!/usr/bin/env python3
"""Replay both R439 words through the unchanged native cohort checkers.

anudeepadi, with substantial OpenAI Codex assistance. Apache-2.0.
Adapted from Ali Romman's research/r420-two-block-composition/native.py
and hosted.py (also prepared with substantial OpenAI Codex assistance).
The native exporters/checkers are by Dylan Crow and DaysSky; the optional
nine-stage chain follows the unchanged PR589 tune/verify.sh recipe.
"""
import argparse
import gzip
import hashlib
import importlib.metadata
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def command_runner(out):
    def call(name, command):
        print("RUN", name, flush=True)
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)
    return call


def validate_inputs(root, out):
    """Bind every replay to the package certificate and immutable sources."""
    here = root / "research/p111-dirty-block509"
    sources = json.loads((here / "SOURCES.json").read_text())
    certificate = json.loads((here / "CERTIFICATE.json").read_text())
    require(certificate["base_commit"] == sources["base_commit"], "Base commit pins differ")
    require("research/e8-bit-p111-tuned/tune/EXPECTED.json" in sources["files"],
            "The tuned historical invoice needs its own explicit source pin")
    for relative, expected in sources["files"].items():
        require(hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected,
                "Pinned source differs: " + relative)
    payloads = 0
    for relative, expected in sources["manifests"].items():
        manifest = root / relative
        require(hashlib.sha256(manifest.read_bytes()).hexdigest() == expected,
                "Pinned manifest differs: " + relative)
        for line in manifest.read_text().splitlines():
            digest, filename = line.split("  ", 1)
            source = manifest.parent / filename
            require(hashlib.sha256(source.read_bytes()).hexdigest() == digest,
                    "Manifest payload differs: " + str(source.relative_to(root)))
            payloads += 1
    hashes = {}
    for name in ("baseline", "candidate"):
        word = json.loads(gzip.decompress((out / (name + ".json.gz")).read_bytes()))
        hashes[name] = hashlib.sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        require(hashes[name] == certificate[name + "_word_sha256"], "Canonical input differs: " + name)
    return {"base_commit": sources["base_commit"], "word_content_sha256": hashes,
            "source_manifests_sha256": sources["manifests"], "manifest_payloads_checked": payloads,
            "source_files_sha256": sources["files"]}


def environment():
    versions = {}
    for package in ("numpy", "scipy", "sympy", "mpmath"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed; only needed by optional hosted replay"
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    boost_include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    boost_version = next((line.split(maxsplit=2)[2] for line in
                          (Path(boost_include) / "boost/version.hpp").read_text().splitlines()
                          if line.startswith("#define BOOST_LIB_VERSION ")), "unknown")
    return {"python": sys.version, "compiler": subprocess.check_output(
                compiler + ["--version"], text=True).splitlines()[0],
            "boost_include": boost_include, "boost_version": boost_version.strip('"'),
            "python_packages": versions}


def scalar_additions(word):
    return (sum(len(sources) for phase in "DABC" for _, _, sources in word[phase])
            + sum(map(len, word["scatter"])))


def run(root, out):
    """Check fresh exports of out/{baseline,candidate}.json.gz; return receipts."""
    provenance = validate_inputs(root, out)
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    python = [sys.executable, "-I", "-B"]
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    words = {name: json.loads(gzip.decompress((out / (name + ".json.gz")).read_bytes()))
             for name in ("baseline", "candidate")}
    require(all((w["v"], w["R"], w["h"]) == (111, 439, 8) for w in words.values()),
            "Expected the pinned punctured R439 words")
    saving = scalar_additions(words["baseline"]) - scalar_additions(words["candidate"])
    require(saving > 0, "No scalar ADD saving")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir(exist_ok=True)
    call = command_runner(out)
    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])
    results = {"provenance": provenance, "environment": environment()}
    for name in ("baseline", "candidate"):
        base = out / name
        records, cin, cout = (base / item for item in ("records", "cin", "cout"))
        call(name + "-export", python + [bit / "export_records.py", out / (name + ".json.gz"), records])
        call(name + "-cohort", python + [bit / "regression/stage_cohort.py", records, records, cin, cout])
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        require(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
                "Legality did not pass")
        require(legality["copies"] == legality["erasures"] == 9 and legality["rank_mass"] == 5129,
                "Copy lifecycle or paid rank mass changed")
        require(legality["common_frame_ADDs"] == scalar_additions(words[name]),
                "Native export has a different scalar ADD bill")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns.json" if pairs == 2 else "columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            require(data["status"] == expected_status, "Formal columns did not pass")
            require(len(data["negative_controls"]) == 6 * (pairs - 1)
                    and all(c["rejected"] for c in data["negative_controls"]), "A bridge control failed")
            require(data["formal_columns_checked"] == 222 * pairs + 439, "Wrong formal column count")
            require(data["bridge_additions"] == 6 * (pairs - 1) * 111, "Wrong bridge bill")
            require(len(data["stages"]) == 2 * pairs + 1, "Incomplete stage replay")
            require(data["local_scalar_additions"] == legality["common_frame_ADDs"], "ADD bills differ")
            results[name]["stages"][str(2 * pairs + 1)] = {
                key: data[key] for key in ("status", "formal_columns_checked", "local_scalar_additions",
                                          "local_raw_H", "payload_prefix_bits", "payload_prefix_upper",
                                          "signed_lift_prefix", "negative_controls", "bridge_additions")}
    old_legality, new_legality = (results[name]["legality"] for name in ("baseline", "candidate"))
    require(old_legality["paid_histogram"] == new_legality["paid_histogram"], "Paid profile changed")
    require(old_legality["records"] - new_legality["records"] == saving, "Record saving differs")
    require(old_legality["nested_MOVEs"] == new_legality["nested_MOVEs"], "MOVE bill changed")
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("baseline", "candidate"))
        require(old["local_raw_H"] == new["local_raw_H"], "Paid recursive profile changed")
        require(old["local_scalar_additions"] - new["local_scalar_additions"] == saving,
                "Scalar saving differs between native stages")
        require(int(new["payload_prefix_upper"]) <= int(old["payload_prefix_upper"]), "Payload bound increased")
        require(len(old["signed_lift_prefix"]) == len(new["signed_lift_prefix"]) == 2,
                "Missing signed prefix direction")
        for a, b in zip(old["signed_lift_prefix"], new["signed_lift_prefix"]):
            require(a["reverse"] == b["reverse"] and int(b["cancellation_free_signed_row_l1_upper"])
                    <= int(a["cancellation_free_signed_row_l1_upper"]), "Signed bound increased")
    return results


def run_hosted(root, out):
    """Replay the frozen PR589 nine-stage hosted plan and full finite invoice.

    The cited PR548 complex supplier is an inherited arithmetic input only;
    this command neither replays nor changes its construction.
    """
    validate_inputs(root, out)
    package = root / "research/e8-bit-p111-tuned"
    predecessor = root / "research/e8-bit-carrier-skeleton"
    price = package / "vendor/pr510/e8-r480-nine-stage"
    code = price / "vendor/e8-r715-eleven-stage-whole/code"
    python = [sys.executable, "-E", "-s", "-B"]
    call = command_runner(out)
    call("hosted-pr545-adapter", python + [package / "vendor/pr545/code/adapt.py", predecessor,
         out / "baseline.json.gz", out / "adapt545"])
    call("hosted-pr510-adapter", python + [price / "code/adapt.py", code, out / "adapt510"])
    adapted = out / "adapt9p"
    call("hosted-p111-adapter", python + [package / "code/adapt9p.py", code, price / "code",
         out / "adapt510/audit_parent_k.py", adapted])
    assembly_root = out / "assembly-root"
    (assembly_root / "data").mkdir(parents=True, exist_ok=True)
    if not (assembly_root / "code").exists():
        (assembly_root / "code").symlink_to(predecessor / "code", target_is_directory=True)
    shutil.copy2(package / "data/complex-b.json", assembly_root / "data/complex-b.json")
    results = {}
    for name in ("baseline", "candidate"):
        base = out / name
        parent = base / "nine"
        parent.mkdir(exist_ok=True)
        word = out / (name + ".json.gz")
        call(name + "-geometry", python + [out / "adapt545/nine_geometry.py", "--source", predecessor,
             "--out", parent, "--word", word])
        call(name + "-parent", python + [adapted / "global_k.py", "--word", word,
             "--local-check", base, "--out", parent, "--isometries",
             predecessor / "data/eleven/residual-isometries.json"])
        call(name + "-parent-audit", python + [adapted / "audit_parent_k.py", "--word", word,
             "--local-check", base, "--out", parent])
        hosted = base / "hosted"
        call(name + "-hosted", python + [adapted / "emit_k.py", parent, base, hosted,
             "--selection", package / "data/selection9-p111.json", "--key", "bit"])
        call(name + "-hosted-audit", python + [adapted / "audit_hosted_k.py", base, hosted,
             hosted / "AUDIT.json"])
        call(name + "-invoice", python + [adapted / "assemble9.py", base, hosted, hosted / "AUDIT.json",
             assembly_root, base / "PRICE.json", "pr548"])
        pg = json.loads((parent / "GLOBAL.json").read_text())
        parent_audit = json.loads((parent / "AUDIT.json").read_text())
        audit = json.loads((hosted / "AUDIT.json").read_text())
        invoice = json.loads((base / "PRICE.json").read_text())
        require(parent_audit["status"] == "PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT"
                and audit["status"] == "PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT"
                and invoice["status"] == "PASS_NINE_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY",
                "Hosted verification did not pass")
        require(audit["hosted_residuals"] == 126432 and audit["bank_assignments"] == 0,
                "Whole-owner inventory changed")
        require(len(parent_audit["mutations_rejected"]) == 17 and len(audit["mutations_rejected"]) == 16,
                "Incomplete inherited mutation coverage")
        results[name] = {"parent_mutations": parent_audit["mutations_rejected"], "hosted_audit": audit,
                         "bit_lower": invoice["bit_lower"], "bit_lower_decimal": invoice["bit_lower_decimal"],
                         "invoice": invoice["bit"], "global_prefix_bound": pg["global_prefix_bound"],
                         "bit_profile": invoice["bit_profile"], "local_additions": pg["local_additions"]}
    old, new = results["baseline"], results["candidate"]
    expected = json.loads((package / "tune/EXPECTED.json").read_text())["nine"]
    require(old["bit_lower"] == expected["bit_lower"] and old["invoice"] == expected["bit"]
            and old["bit_profile"] == expected["profile"], "The original R439 invoice was not reproduced")
    require(old["bit_profile"] == new["bit_profile"] and old["bit_lower"] == new["bit_lower"],
            "The recursive profile or bit exponent changed")
    require(old["hosted_audit"]["emitted_events"] - new["hosted_audit"]["emitted_events"]
            == 288 * (old["local_additions"] - new["local_additions"]), "Wrong physical instruction saving")
    require(int(new["global_prefix_bound"]) <= int(old["global_prefix_bound"]), "Global prefix bound increased")
    raw_bounds = {"prefix_bits", "coefficient_bits", "two_level_coefficient_bits"}
    require(all(new["invoice"][key] <= old["invoice"][key] for key in raw_bounds), "A finite bound increased")
    require({k: v for k, v in old["invoice"].items() if k not in raw_bounds}
            == {k: v for k, v in new["invoice"].items() if k not in raw_bounds}, "Charged invoice changed")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path, help="directory containing baseline.json.gz and candidate.json.gz")
    parser.add_argument("--hosted", action="store_true", help="also replay the full frozen nine-stage hosting plan")
    args = parser.parse_args()
    out = args.out.resolve()
    root = Path(__file__).resolve().parents[2]
    receipt = {"native": run(root, out)}
    if args.hosted:
        receipt["hosted"] = run_hosted(root, out)
    (out / "NATIVE.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS R439 native legality and all 5/9/11-stage formal columns for both words")


if __name__ == "__main__":
    main()
