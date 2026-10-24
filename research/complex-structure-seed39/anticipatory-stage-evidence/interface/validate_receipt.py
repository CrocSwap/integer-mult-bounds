#!/usr/bin/env python3
"""Mutation-test retained receipt bindings without rerunning mathematical stages.

Apache-2.0; prepared with substantial OpenAI Codex assistance. All mutations
occur in temporary copies. A successful result is evidence about aggregation
failure detection, not a new cold replay or a proof of an all-size theorem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
STATUS = "PASS_PR2339_LOCAL_NATIVE_ADMISSION_WITHOUT_GLOBAL_BOUND"
LOCAL_FILES = (
    "CANONICAL-WORD.json.gz", "SCALAR-FRAME-AUDIT.json", "LOCAL-CHECKS.json",
    "INDEPENDENT-LOCAL-REPLAY.json", "WRAPPER-CHECKS.json", "CLIFFORD-REVIEW.json",
    "WARP-RECIPE-CHECKS.json", "ORIENTATION-CONTRACT.json",
    "ORIENTED-WARP-RECIPES.json.gz", "CLIFFORD-RECIPES.json", "LOCAL-PROGRAMS.json.gz",
)
STATUS_FILES = (
    "SCALAR-FRAME-AUDIT.json", "INDEPENDENT-LOCAL-REPLAY.json", "WRAPPER-CHECKS.json",
    "CLIFFORD-REVIEW.json", "WARP-RECIPE-CHECKS.json", "ORIENTATION-CONTRACT.json",
)


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic validation receipt")
    args = parser.parse_args()
    files = ["make_receipt.py", "replay.py", "LEMMAG-CHECKS.json"]
    files += [f"{variant}/{name}" for variant in ("base", "extra") for name in LOCAL_FILES]
    files += [f"{name}/TAMPER-RESULTS.json" for name in ("base-tamper", "extra-tamper", "extra-tamper-files")]
    pins = {name: digest(HERE / name) for name in files}
    expected_result = (HERE / "RESULT.json").read_bytes()
    controls = []
    with tempfile.TemporaryDirectory(prefix="pr2339-receipt-") as tmp:
        root = Path(tmp)
        fixture = root / "interface"
        fixture.mkdir()
        (root / "vendor").symlink_to(HERE.parent / "vendor", target_is_directory=True)
        (fixture / "pr2269").symlink_to(HERE / "pr2269", target_is_directory=True)
        for name in files:
            target = fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / name, target)

        def run():
            return subprocess.run([sys.executable, "-B", str(fixture / "make_receipt.py")],
                                  capture_output=True, text=True)

        def honest():
            result = run()
            need(result.returncode == 0 and result.stdout.strip() == STATUS,
                 "unmodified fixture rejected: " + result.stderr)
            need((fixture / "RESULT.json").read_bytes() == expected_result,
                 "unmodified result differs from retained result")

        honest()

        def mutate(variant, filename, key, value, reason, delete=False):
            path = fixture / variant / filename
            original = path.read_bytes()
            record = json.loads(original)
            if delete:
                del record[key]
            else:
                record[key] = value
            path.write_text(json.dumps(record, indent=2) + "\n")
            try:
                result = run()
                need(result.returncode != 0, f"accepted mutation: {variant}/{filename}:{key}")
                need("RuntimeError: " + reason in result.stderr,
                     f"wrong rejection for {variant}/{filename}:{key}: {result.stderr}")
                controls.append(dict(variant=variant, file=filename, field=key,
                                     mutation="delete" if delete else "replace", replacement=None if delete else value,
                                     rejected=True, reason=reason))
            finally:
                path.write_bytes(original)

        for variant in ("base", "extra"):
            for filename in STATUS_FILES:
                reason = "unsuccessful stage: " + filename
                mutate(variant, filename, "status", "FAIL_MUTATION", reason)
                mutate(variant, filename, "status", None, reason, delete=True)
            for key, value, reason in (
                ("canonical_content_sha256", "0" * 64, "unbound orientation canonical word"),
                ("paid_profile", {"1": 5264}, "orientation profile mismatch"),
            ):
                mutate(variant, "ORIENTATION-CONTRACT.json", key, value, reason)
                mutate(variant, "ORIENTATION-CONTRACT.json", key, None, reason, delete=True)
            for key, reason in (
                ("warp_recipes_rank_zero", "warp rank-zero proof missing"),
                ("warp_recipes_equal_exact_512_column_product", "warp exact-product proof missing"),
                ("all_child_equalities_include_global_phase", "global-phase proof missing"),
            ):
                for value in (False, 1):
                    mutate(variant, "CLIFFORD-REVIEW.json", key, value, reason)
                mutate(variant, "CLIFFORD-REVIEW.json", key, None, reason, delete=True)
            mutate(variant, "CLIFFORD-REVIEW.json", "warp_recipes", 223, "missing warp")

        # Timing and descriptive text are not mathematical acceptance conditions.
        for variant in ("base", "extra"):
            path = fixture / variant / "CLIFFORD-REVIEW.json"
            record = json.loads(path.read_bytes())
            record["seconds"] = 0
            record["scope"] = "non-proof metadata changed in isolated positive control"
            path.write_text(json.dumps(record, indent=2) + "\n")
        honest()

    need(all(digest(HERE / name) == sha for name, sha in pins.items()), "retained evidence changed")
    need((HERE / "RESULT.json").read_bytes() == expected_result, "retained result changed")
    receipt = dict(
        status="PASS_PR2339_RECEIPT_BINDINGS_52_MUTATIONS_REJECTED",
        base_commit="7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",
        construction_head="bf1742aee4d855efb8bbd44a8419eddb33a679e5",
        compiler_head="b479fc5567bc09ab9185bffe89b62594f36d74e5",
        method="Single-field mutations of isolated receipt copies; execute the real aggregator and require the intended failure message.",
        original_gap="The former aggregator accepted an all-zero orientation canonical digest and a false all_child_equalities_include_global_phase flag.",
        controls=controls, rejected_controls=len(controls), honest_baseline_passed=True,
        incidental_metadata_positive_control_passed=True, retained_outputs_unchanged=True,
        evidence_sha256=pins, result_sha256=hashlib.sha256(expected_result).hexdigest(),
        validator_sha256=digest(Path(__file__)),
        scope="Aggregation bindings only; original cold-stage history in VALIDATION.json is unchanged. No new mathematical replay, global construction, or kappa is certified.",
    )
    need(len(controls) == 52, "mutation coverage changed")
    if args.out:
        args.out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
