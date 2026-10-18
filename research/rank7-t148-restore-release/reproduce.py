#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh PR3015 source/native chain with the T148 order, fill and dispatch.

Uses PR3021's authenticated exporter, process cleanup and source-chain checks.
No scientific source or retained validator is patched by this wrapper.
"""

import argparse
import gzip
import hashlib
import os
import sys
from fractions import Fraction
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent


def prepare(repo, work):
    verify.authenticate()
    verify.need(not work.exists(), "refusing an existing replay workspace")
    verify.need(not work.is_relative_to(PACKAGE) and not PACKAGE.is_relative_to(work),
                "external replay workspace")
    verify.need(sys.flags.optimize == 0 and os.name == "posix", "POSIX with assertions enabled")
    driver = verify.retained("release_driver")
    driver.PACKAGE = PACKAGE
    work.mkdir(parents=True)
    source, run = work / "pr3015", work / "run"
    driver.export(repo, source)
    _, _, _, order, _, fill, dispatch = verify.allocation()
    paths = {}
    for name, value in [("fill", fill), ("order", order), ("dispatch", dispatch)]:
        path = work / (name.upper() + (".json.gz" if name == "fill" else ".json"))
        raw = verify.canonical(value)
        path.write_bytes(gzip.compress(raw, compresslevel=1, mtime=0) if name == "fill" else raw)
        paths[name] = path
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(work / "bytecode"),
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONINTMAXSTRDIGITS="0")
    for key in ("PYTHONPATH", "PYTHONOPTIMIZE", "WITNESS_SPEC", "WITNESS_RECORD", "WITNESS_DISCOVER"):
        env.pop(key, None)
    stages = []
    driver.run_stage("source-preflight", [sys.executable, "-B", source / "reproduce.py",
        "--repo", repo, "--work", run, "--jobs", "1", "--dry-run"], work, env, stages, 120)
    recipe = verify.read(run / "PREFLIGHT.json")["commands"]
    verify.need([name for name, _ in recipe] == driver.RECIPE_NAMES, "complete source recipe")
    changes = []
    for name, command in recipe:
        if name != "complete-admission":
            continue
        for argument, path in paths.items():
            index = command.index("--" + argument) + 1
            expected = source / "allocation" / path.name
            verify.need(command[index] == str(expected), "recipe preimage: " + argument)
            changes.append(dict(stage=name, argument="--" + argument,
                                old=command[index], new=str(path)))
            command[index] = str(path)
    verify.need(len(changes) == 3, "only fill/order/dispatch arguments change")
    driver.save(work / "RECIPE.json", dict(commands=recipe, changes=changes))
    return driver, source, recipe, paths, env, stages


def check_release(driver, work, source, paths, stages, finite):
    candidate = work / "run/candidate"
    admission = verify.read(candidate / "RESULT.json")
    release_path = candidate / "release/RELEASE-RECEIPT.json"
    release = verify.read(release_path)
    verify.need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
                "complete admission")
    verify.need(release["status"] == "PASS_RELEASE", "complete outer release")
    verify.need(admission["replicas"] == 148, "actual T148 admission")
    verify.need({int(k): n for k, n in admission["profile"].items()} == verify.EXPECTED,
                "actual complete profile")
    for name, path in paths.items():
        verify.need(admission[name + "_sha256"] == verify.digest(path), "admitted " + name)
    payload = hashlib.sha256(verify.canonical(verify.read(paths["fill"]))).hexdigest()
    verify.need(payload == finite["fill_payload_sha256"], "actual admitted canonical fill")
    for name in ("order", "dispatch"):
        verify.need(verify.digest(paths[name]) == finite[name + "_sha256"], "literal " + name)
    verify.need(admission["release_receipt_sha256"] == verify.digest(release_path), "release binding")
    verify.need(admission["package_manifest_sha256"] == release["manifest_sha256"], "package binding")
    verify.need(admission["source_manifest_sha256"] == verify.read(source / "CLAIM.json")[
        "source_manifest_sha256"], "unchanged edited source")
    endpoint = Fraction(admission["kappa"])
    previous = Fraction(finite["comparison_kappa"])
    verify.need(previous < endpoint < Fraction(finite["new_root"][0]), "strict valid gain over PR3021")
    verify.need(endpoint == Fraction(release["kappa_decimal"]), "same released endpoint")
    driver.check_source_chain(work, source, admission, stages)
    driver.authenticate_tree(candidate / "package")
    invoice = candidate / "release/verify/strict/global/audit/PREFIX-AND-INVOICE.json"
    verify.check_invoice(verify.read(invoice), finite)
    return dict(status="PASS_T148_R1_COMPLETE_RELEASE", kappa=str(endpoint),
                invoice_payload_sha256=verify.digest(invoice),
                comparison_kappa=str(previous), gain=str(endpoint - previous),
                fresh_retained_bootstrap=True, replicas=148, profile=verify.EXPECTED,
                stock=finite["stock148"], fill_payload_sha256=finite["fill_payload_sha256"],
                fill_sha256=verify.digest(paths["fill"]),
                order_sha256=verify.digest(paths["order"]),
                dispatch_sha256=verify.digest(paths["dispatch"]),
                admission_result_sha256=verify.digest(candidate / "RESULT.json"),
                release_receipt_sha256=verify.digest(release_path),
                native_receipt_sha256=verify.digest(work / "run/native/NATIVE-RECEIPT.json"),
                stages=stages,
                scope="Conditional finite release; universal inherited hypotheses remain.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    finite = verify.run()
    work = args.work.resolve()
    driver, source, recipe, paths, env, stages = prepare(args.repo.resolve(), work)
    driver.save(work / "FINITE.json", finite)
    if args.dry_run:
        print("PASS_T148_PREFLIGHT_ONLY_NOT_A_RELEASE")
        return
    for name, command in recipe:
        driver.run_stage(name, command, work, env, stages, 1800)
    result = check_release(driver, work, source, paths, stages, finite)
    driver.save(work / "RESULT.json", result)
    print(result["status"], result["kappa"], flush=True)


if __name__ == "__main__":
    main()
