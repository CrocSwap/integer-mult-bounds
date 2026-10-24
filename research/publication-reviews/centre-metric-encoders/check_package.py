"""Check package bytes, retained sources, and replay failure controls."""

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
PACKAGE = BASE / "packages/centre-metric-encoders"
CAMPAIGN = BASE.parent


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((PACKAGE / "PACKAGE-MANIFEST.json").read_text())
    for item in manifest["files"]:
        path = PACKAGE / item["path"]
        need(path.stat().st_size == item["bytes"] and digest(path) == item["sha256"],
             "Package manifest: " + item["path"])
    source_manifest = json.loads((PACKAGE / "SOURCE-MANIFEST.json").read_text())
    for item in source_manifest["immutable_inputs"]:
        source = CAMPAIGN / item["source_campaign_path"]
        target = PACKAGE / item["path"]
        need(source.read_bytes() == target.read_bytes(), "Original source: " + item["path"])
    cold = HERE / "cold/package"
    for relative in ("replay.py", "portable/check_signed_clean.py", "SOURCE-MANIFEST.json"):
        need((cold / relative).read_bytes() == (PACKAGE / relative).read_bytes(),
             "Cold checked code is final: " + relative)
    read_paths = set()
    for path in (HERE / "cold/replay").glob("*/*/FILE-ACCESS.json"):
        read_paths.update(json.loads(path.read_text()))
    assertions = {}
    for relative in sorted(read_paths):
        if relative.endswith(".py"):
            tree = ast.parse((cold / relative).read_text())
            assertions[relative] = sum(isinstance(node, ast.Assert) for node in ast.walk(tree))
    need(not any(assertions.values()), "No checked Python file loses assertions under optimization")

    source_checks = []
    for item in json.loads((PACKAGE / "evidence/SOURCE-LICENSE-CHECK.json").read_text())["checks"]:
        raw = subprocess.check_output(["git", "show", item["source_commit"] + ":" + item["source_path"]], cwd=CAMPAIGN)
        need(raw == (PACKAGE / item["retained_path"]).read_bytes(), "Pinned Git source: " + item["source_path"])
        source_checks.append({"source_path": item["source_path"], "sha256": hashlib.sha256(raw).hexdigest(), "equal": True})
    native_sources = json.loads((PACKAGE / "evidence/NATIVE-SOURCE-VERIFICATION.json").read_text())
    native_credit_checks = []
    for label in ("PR3133-README", "PR3148-README", "PR2588-README"):
        item = next(record for record in native_sources["files"] if record["label"] == label)
        path = BASE / "refresh" / (label + ".md")
        need(digest(path) == item["sha256"], "Refreshed credit source: " + label)
        native_credit_checks.append({"label": label, "sha256": digest(path), "url": item["url"]})
    for name, expected in (("PR3133-NOTICE", "c9731c9cca25ede32c2a1b3aef6d5b249973cb2ed5fb2494407bdca598763661"),
                           ("PR3133-CREDITS.md", "1d9d8f56d8899f55878e4cb2c4e052b22506444016a51c2e678773505f5189e6"),
                           ("PR2588-NOTICE", "a91b93a731f116ae55b3644c88232b4d996e58bb810e2559dec013f9788f5e4b")):
        need(digest(PACKAGE / "notices" / name) == expected, "Retained native notice: " + name)

    context = json.loads((PACKAGE / "evidence/SELECTED-CONTEXT.json").read_text())
    selected = BASE / "refresh/main/certificates/selected-result.json"
    need(digest(selected) == context["selected_record_sha256"], "Current selected record pin")
    need(json.loads(selected.read_text()) == context["selected_record"], "Current selected record bytes")

    controls = []
    directory = HERE / "failure-controls"
    directory.mkdir(exist_ok=True)
    forbidden = directory / "outside.txt"
    forbidden.write_text("This file is outside each worker output directory.\n")
    for mode in ("normal", "optimized"):
        for control in ("false_requirement", "outside_read"):
            target = directory / (mode + "-" + control)
            target.mkdir(exist_ok=True)
            probe = target / "probe.py"
            if control == "false_requirement":
                probe.write_text("import runpy\nmodule = runpy.run_path(" + repr(str(cold / "replay.py")) + ")\nmodule['require'](False, 'EXPECTED_FALSE_REQUIREMENT_REJECTION')\n")
                expected = "EXPECTED_FALSE_REQUIREMENT_REJECTION"
            else:
                probe.write_text("from pathlib import Path\nPath(" + repr(str(forbidden)) + ").read_bytes()\n")
                expected = "File access outside the package, output, or Python runtime: " + str(forbidden)
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command += [str(cold / "replay.py"), "--worker", str(probe), str(target)]
            result = subprocess.run(command, capture_output=True, text=True)
            (target / "output.log").write_text(result.stdout + result.stderr)
            need(result.returncode != 0 and expected in result.stderr, "Failure control: " + control + "/" + mode)
            controls.append({"mode": mode, "control": control, "exit_code": result.returncode, "rejected_at_expected_check": True})

    report = {"status": "PASS_ENCODER_PACKAGE_CHECKS", "package_manifest_sha256": digest(PACKAGE / "PACKAGE-MANIFEST.json"),
              "package_files": len(manifest["files"]), "immutable_sources_equal_original": len(source_manifest["immutable_inputs"]),
              "cold_code_equal_final": True, "retained_git_sources": source_checks,
              "native_credit_source_checks": native_credit_checks,
              "current_selected_record_equal": True, "python_files_read_assertion_counts": assertions,
              "failure_controls": controls,
              "scope": "The file list includes hash reads, not only executed imports. The file-access hook is a reproducibility check, not a security sandbox."}
    (HERE / "PACKAGE-CHECKS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
