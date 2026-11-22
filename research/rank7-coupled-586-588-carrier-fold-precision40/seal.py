#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind a successful complete precision-40 replay into the package evidence."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from fractions import Fraction as Q

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True, help="fresh completed reproduce.py work directory")
    ap.add_argument("--retained", type=Path, required=True, help="authenticated retained bootstrap directory used by the run")
    args = ap.parse_args()
    work, retained = args.work.resolve(), args.retained.resolve()
    if work == P or work.is_relative_to(P) or P.is_relative_to(work):
        raise SystemExit("replay work must be external to the package")
    claim = read(P / "CLAIM.json")
    result = read(work / "RESULT.json")
    admit = read(work / "candidate/RESULT.json")
    native = read(work / "native/NATIVE-RECEIPT.json")
    release = read(work / "candidate/release/RELEASE-RECEIPT.json")
    retained_receipt = read(retained / "NATIVE-RECEIPT.json")
    release_verify = read(work / "candidate/release/verify/RESULT.json")
    k = Q(claim["kappa"])

    def need(ok, msg):
        if not ok:
            raise SystemExit(msg)

    need(result["status"] == "PASS_RANK7_EDITS_COMPLETE_REPLAY", "complete replay did not pass")
    need(Q(result["kappa"]) == Q(admit["kappa"]) == Q(release["kappa_decimal"]) == k, "κ mismatch")
    need(admit["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "admission did not pass")
    need(release["status"] == "PASS_RELEASE", "strict outer release did not pass")
    need(release_verify["status"] == "PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION", "strict supplier admission did not pass")
    need(all(s["exit_code"] == 0 for s in release_verify["stages"]), "strict supplier stages")
    need(admit["release_receipt_sha256"] == sha(work / "candidate/release/RELEASE-RECEIPT.json"), "release receipt binding")
    need(admit["package_manifest_sha256"] == release["manifest_sha256"], "admitted package manifest binding")
    need(admit["source_manifest_sha256"] == result["source_manifest_sha256"], "final source binding")
    need(Q(admit["comparison_kappa"]) == Q(claim["baseline_kappa"]), "baseline comparison binding")
    need(retained_receipt["status"] == "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE", "retained bootstrap receipt")
    need(result["explicit_retained_reuse"] is True and result["fresh_retained_bootstrap"] is False, "replay cache-use declaration")
    need(Q(claim["precision_parent_gain"]) == k - Q(claim["precision_parent_kappa"]) > 0, "strict gain over PR3133")

    evidence = P / "evidence"
    copies = {
        "ADMISSION-RESULT.json": work / "candidate/RESULT.json",
        "ADMISSION-STAGES.json": work / "candidate/STAGES.json",
        "FULL-NATIVE-RECEIPT.json": work / "native/NATIVE-RECEIPT.json",
        "FULL-NATIVE-RESULT.json": work / "native/RESULT.json",
        "FULL-REPLAY-RESULT.json": work / "RESULT.json",
        "FULL-REPLAY-STAGES.json": work / "STAGES.json",
        "RELEASE-RECEIPT.json": work / "candidate/release/RELEASE-RECEIPT.json",
        "RELEASE-VERIFY-RESULT.json": work / "candidate/release/verify/RESULT.json",
        "GEOMETRY-CONTROLS.json": work / "candidate/release/verify/GEOMETRY-CONTROLS.json",
        "RUNTIME-PATCHES.json": work / "candidate/RUNTIME-PATCHES.json",
        "ADAPTER-DERIVATION.json": work / "adapters/ADAPTER-DERIVATION.json",
        "RETAINED-BOOTSTRAP-RECEIPT.json": retained / "NATIVE-RECEIPT.json",
        "ENVIRONMENT.json": work / "native/ENVIRONMENT.json",
    }
    for name, source in copies.items():
        need(source.is_file(), "missing evidence source: " + str(source))
        shutil.copyfile(source, evidence / name)

    claim["admitted_package_manifest_sha256"] = admit["package_manifest_sha256"]
    claim["release_receipt_sha256"] = sha(evidence / "RELEASE-RECEIPT.json")
    claim["native_receipt_sha256"] = sha(evidence / "FULL-NATIVE-RECEIPT.json")
    write(P / "CLAIM.json", claim)
    seal = {
        "status": "PASS_PRECISION40_EVIDENCE_SEALED",
        "kappa": str(k),
        "precision_parent_pr": 3133,
        "precision_parent_kappa": claim["precision_parent_kappa"],
        "precision_parent_gain": claim["precision_parent_gain"],
        "fresh_retained_bootstrap_receipt_sha256": sha(evidence / "RETAINED-BOOTSTRAP-RECEIPT.json"),
        "full_replay_result_sha256": sha(evidence / "FULL-REPLAY-RESULT.json"),
        "admission_result_sha256": sha(evidence / "ADMISSION-RESULT.json"),
        "native_receipt_sha256": sha(evidence / "FULL-NATIVE-RECEIPT.json"),
        "release_receipt_sha256": sha(evidence / "RELEASE-RECEIPT.json"),
        "explicit_retained_reuse": True,
        "fresh_retained_bootstrap": False,
    }
    write(evidence / "SEAL.json", seal)

    logs = evidence / "logs"
    logs.mkdir(exist_ok=True)
    for source in sorted(work.glob("*.log")):
        shutil.copyfile(source, logs / (source.name + ".txt"))
    for source in sorted((work / "candidate").glob("*.log")):
        shutil.copyfile(source, logs / ("admission-" + source.name + ".txt"))
    for source in sorted((work / "candidate/release").glob("*.log")):
        shutil.copyfile(source, logs / ("release-" + source.name + ".txt"))
    nested = logs / "release-verify"
    for source in sorted((work / "candidate/release/verify").rglob("*.log")):
        dest = nested / source.relative_to(work / "candidate/release/verify")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    (logs / "fresh-retained-bootstrap.log.txt").write_bytes(
        (retained.parent / "fresh-retained-bootstrap.log").read_bytes()
    )
    manifest = {
        path.relative_to(P).as_posix(): sha(path)
        for path in sorted(P.rglob("*"))
        if path.is_file() and path != P / "MANIFEST.json" and "__pycache__" not in path.parts
    }
    write(P / "MANIFEST.json", manifest)
    print("PASS_PRECISION40_EVIDENCE_SEALED", claim["kappa_decimal"], "gain over PR3133", claim["precision_parent_gain"])


if __name__ == "__main__":
    main()
