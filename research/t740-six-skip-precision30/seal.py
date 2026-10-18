#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Derive privacy-preserving evidence only from completed authenticated replays.

Terminal projections omit machine timing; original receipts remain unchanged
in the external workspace and are committed to by their exact SHA256 digests.
Substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import shutil
import sys

import verify as v


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-work", type=v.Path, required=True)
    parser.add_argument("--work", type=v.Path, required=True)
    a = parser.parse_args()
    baseline, work = a.baseline_work.resolve(), a.work.resolve()
    v.authenticate()
    sys.path.insert(0, str(v.ROOT / "research/rank7-t740-carrier-skips"))
    original = v.load(
        v.ROOT / "research/rank7-t740-carrier-skips/reproduce.py",
        "credited_baseline_seal",
    )
    result = v.read(baseline / "RESULT.json")
    stages = v.read(baseline / "STAGES.json")
    for stage in stages:
        v.need(
            stage["exit_code"] == 0
            and v.sha(baseline / (stage["stage"] + ".log")) == stage["log_sha256"],
            "authentic completed baseline stage",
        )
    v.need(
        original.check_release(
            baseline, baseline / "pr3042", result["fill_sha256"], stages
        )
        == result,
        "completed baseline fully rederived",
    )
    checked = v.read(work / "RESULT.json")
    v.completion(checked)
    v.need(
        v.sha(work / "candidate/RESULT.json") == checked["admission_sha256"]
        and v.sha(work / "candidate/release/RELEASE-RECEIPT.json")
        == checked["release_sha256"],
        "completed refinement result authenticates actual admission and terminal receipt",
    )
    derivation = v.read(work / "DERIVATION.json")
    v.need(
        derivation["replacements"] == v.read(v.P / "PRECISION-EDITS.json")
        and derivation["reference_sha256"]
        == v.sha(baseline / "run/adapters/admit_extension.py")
        and derivation["candidate_sha256"] == v.sha(work / "admit_precision30.py"),
        "exact declared source derivation",
    )
    arithmetic = v.calculate()
    for key in ("kappa", "previous", "gain"):
        v.need(v.Q(checked[key]) == v.Q(arithmetic[key]), "exact completed refinement")
    evidence = dict(checked)
    for key, directory in (
        ("baseline", baseline / "run/candidate"),
        ("candidate", work / "candidate"),
    ):
        admission = v.read(directory / "RESULT.json")
        receipt_path = directory / "release/RELEASE-RECEIPT.json"
        receipt = v.read(receipt_path)
        v.need(
            admission["status"]
            == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
            "actual complete admission",
        )
        v.need(
            admission["release_receipt_sha256"] == v.sha(receipt_path)
            and admission["package_manifest_sha256"] == receipt["manifest_sha256"],
            "actual terminal receipt and admitted manifest",
        )
        for stage in admission["stages"]:
            v.need(
                stage["exit_code"] == 0
                and v.sha(directory / (stage["name"] + ".log")) == stage["log_sha256"],
                "all actual admission stages and logs",
            )
        evidence[key + "_release_projection"] = {
            field: receipt[field]
            for field in ("status", "kappa_decimal", "manifest_sha256")
        }
        evidence[key + "_terminal_receipt_sha256"] = v.sha(receipt_path)
        evidence[key + "_admission_sha256"] = v.sha(directory / "RESULT.json")
        evidence[key + "_package_manifest_sha256"] = admission[
            "package_manifest_sha256"
        ]
        evidence[key + "_native_receipt_sha256"] = admission["native_receipt_sha256"]
        if "checkpoint_scope" in admission:
            evidence[key + "_checkpoint_scope"] = admission["checkpoint_scope"]
    controls = v.read(work / "candidate/release/verify/RESULT.json")
    audit = v.read(
        work / "candidate/release/verify/strict/global/audit/ASYNC-AUDIT.json"
    )
    v.need(
        audit["status"]
        == "PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS"
        and audit["mutation_controls_run"] is True,
        "actual complete controller mutation audit",
    )
    names = audit["mutations_rejected"]
    v.need(len(names) == len(set(names)) == 25, "all25 actual controller controls")
    baseline_audit = v.read(
        baseline / "run/candidate/release/verify/strict/global/audit/ASYNC-AUDIT.json"
    )
    expected_names = v.read(
        v.ROOT / "research/rank7-t740-carrier-skips/evidence/ASYNC-AUDIT.json"
    )["mutations_rejected"]
    v.need(
        baseline_audit["mutations_rejected"] == names == expected_names,
        "both completed releases retain every named original controller control",
    )
    evidence["inherited_supplier_summary_controls"] = controls["controls"]
    evidence["controller_controls"] = names
    evidence["controls"] = dict(controls["controls"], controller=len(names))
    evidence["controller_summary_note"] = (
        "The unchanged supplier summary retains the historical controller=15 field; "
        "the actual completed ASYNC-AUDIT lists25 distinct rejected controls. "
        "Original source and receipts are unchanged; this evidence reports the actual list."
    )
    evidence["projection_scope"] = (
        "Terminal status, exact point and manifest projected from authentic completed receipts; "
        "machine timing omitted. Original bytes remain unchanged privately and are SHA256-bound. "
        "Registered replay checks finite evidence; reproduce.py performs the full changed release."
    )
    out = v.P / "evidence"
    v.need(not out.exists(), "fresh evidence output")
    out.mkdir()
    for source, name in (
        (work / "candidate/package/outer/LEDGER.json", "OUTER-LEDGER.json"),
        (work / "DERIVATION.json", "DERIVATION.json"),
    ):
        shutil.copyfile(source, out / name)
    evidence["files"] = {p.name: v.sha(p) for p in out.iterdir()}
    (out / "VALIDATION.json").write_text(
        v.json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    )
    v.run()
    print("PASS_SEALED_COMPLETE_REFINEMENT")


if __name__ == "__main__":
    main()
