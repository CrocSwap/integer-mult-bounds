"""Replay the separate geodesic annex without changing the primary package."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time


ANNEX = Path(__file__).resolve().parent
PACKAGE = ANNEX.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check_files(root, files):
    for name, expected in files.items():
        require(digest(root / name) == expected, "File pin: " + name)


def same_json(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(sys.version_info >= (3, 10), "Python 3.10 or later is required")
    output = args.out.resolve()
    require(output != PACKAGE and PACKAGE not in output.parents,
            "Use an output directory outside the full package")
    require(not output.exists(), "Use a new output directory")
    manifest = json.loads((ANNEX / "ANNEX-MANIFEST.json").read_text())
    check_files(ANNEX, manifest["files"])
    parent = json.loads((ANNEX / "PARENT-SNAPSHOT.json").read_text())
    check_files(PACKAGE, parent["files"])
    sources = json.loads((ANNEX / "SOURCES.json").read_text())
    check_files(ANNEX, {item["path"]: item["sha256"] for item in sources["files"]})
    check_files(PACKAGE, sources["parent_inputs"])
    adaptations = json.loads((ANNEX / "PORTABILITY.json").read_text())
    for item in adaptations:
        original, portable = ANNEX / item["source"], ANNEX / item["portable"]
        require(digest(original) == item["source_sha256"], "Original checker hash")
        require(digest(portable) == item["portable_sha256"], "Portable checker hash")
        functions = []
        for path in (original, portable):
            functions.append({node.name: ast.dump(node, include_attributes=False)
                              for node in ast.parse(path.read_text()).body
                              if isinstance(node, ast.FunctionDef)
                              and node.name in item["unchanged_function_names"]})
        require(functions[0] == functions[1], "Mathematical function changed")
    output.mkdir(parents=True)
    checks = []
    jobs = [
        ("producer", "verify_geodesic.py", [], "GEODESIC-CHECKS.json"),
        ("independent", "check_geodesic_review.py",
         ["--producer-receipt", str(output / "GEODESIC-CHECKS.json")], "GEODESIC-REVIEW.json"),
    ]
    for name, script, options, destination in jobs:
        command = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            command.append("-O")
        command += [str(ANNEX / "portable" / script), *options,
                    "--out", str(output / destination)]
        started = time.monotonic()
        run = subprocess.run(command, cwd=output, capture_output=True, text=True)
        (output / (name + ".stdout.txt")).write_text(run.stdout)
        (output / (name + ".stderr.txt")).write_text(run.stderr)
        require(run.returncode == 0, name + " failed; inspect its output logs")
        actual = json.loads((output / destination).read_text())
        if name == "producer":
            expected = json.loads((ANNEX / "frozen/lanes/source-domain/GEODESIC-CHECKS.json").read_text())
            require(actual["reader_sha256"] == digest(PACKAGE / "checkers/review_wire_gauge.py"),
                    "Actual parent reader hash")
            expected["reader_sha256"] = actual["reader_sha256"]
            require(same_json(actual, expected), "Producer mathematical receipt differs")
            require(len(actual["negative_controls"]) == 3, "Geodesic damage-control inventory")
            changes = ["reader_sha256: pinned portable parent reader"]
        else:
            expected = json.loads((ANNEX / "frozen/lanes/encoded-controller/review/GEODESIC-REVIEW.json").read_text())
            reviewed = [ANNEX / "frozen/lanes/source-domain/GEODESIC-BOUNDARY.md",
                        ANNEX / "portable/verify_geodesic.py", output / "GEODESIC-CHECKS.json",
                        PACKAGE / "checkers/review_wire_gauge.py", ANNEX / "portable/check_geodesic_review.py"]
            require(actual["reviewed_files_sha256"] == {str(path): digest(path) for path in reviewed},
                    "Fresh review file hashes")
            require(isinstance(actual["maximum_resident_bytes"], int)
                    and actual["maximum_resident_bytes"] >= 0, "Runtime memory metadata")
            for field in ("reviewed_files_sha256", "maximum_resident_bytes"):
                expected.pop(field)
                actual.pop(field)
            expected.pop("review_update")
            require(same_json(actual, expected), "Independent mathematical receipt differs")
            changes = ["reviewed_files_sha256: actual paths and executed checker hashes",
                       "maximum_resident_bytes: runtime metadata",
                       "review_update: retained only in the frozen historical review"]
        checks.append({"check": name, "status": actual["status"],
                       "receipt": destination, "receipt_sha256": digest(output / destination),
                       "seconds": round(time.monotonic() - started, 6),
                       "declared_metadata_changes": changes,
                       "all_other_typed_json_fields_equal": True})
        print(actual["status"], flush=True)
    check_files(PACKAGE, parent["files"])
    check_files(ANNEX, manifest["files"])
    result = {
        "status": "PASS_GEODESIC_BOUNDARY_ANNEX",
        "python": sys.version,
        "optimized": bool(sys.flags.optimize),
        "parallel_workers": 1,
        "checks": checks,
        "historical_source": sources["historical_revision"],
        "parent_files_unchanged": len(parent["files"]),
        "parent_manifest_sha256": sources["parent_manifest_sha256"],
        "annex_manifest_sha256": digest(ANNEX / "ANNEX-MANIFEST.json"),
        "frozen_source_files": len(sources["files"]),
        "application_scope": "Retained productive paths and scalar access, common I/full-F productive endpoints, identity joint content; inherited one-shot mode and whole-owner invoice",
        "complete_kappa_improvement": False,
        "not_rerun": ["Primary fixed-word package's mathematical checks", "Global native emitter",
                      "One-shot mode native admission", "Whole-owner hosting review",
                      "Current selected PR4470 replay", "Scalar/address or recursive repricing"],
    }
    (output / "REPLAY.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
