"""Run the pinned checks in sequence and compare their exact results."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mathematical_functions(path):
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef) and node.name != "main"
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    need(out != PACKAGE and PACKAGE not in out.parents,
         "Use an output directory outside the package")
    need(not out.exists(), "Use a new output directory")
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in sources["files"]:
        need(sha256(PACKAGE / item["path"]) == item["sha256"],
             "Source pin: " + item["path"])
    adaptations = json.loads((PACKAGE / "PORTABILITY.json").read_text())
    for item in adaptations:
        original, portable = PACKAGE / item["source"], PACKAGE / item["portable"]
        need(sha256(original) == item["source_sha256"], "Original checker pin")
        need(sha256(portable) == item["portable_sha256"], "Portable checker pin")
        need(mathematical_functions(original) == mathematical_functions(portable),
             "A mathematical function changed: " + item["portable"])
    out.mkdir(parents=True)
    reports = []
    for index, item in enumerate(adaptations, 1):
        script = PACKAGE / item["portable"]
        receipt = out / (str(index) + "-" + Path(item["expected"]).name)
        command = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            command.append("-O")
        command += [str(script), "--out", str(receipt)]
        start = time.monotonic()
        result = subprocess.run(command, cwd=out, text=True, capture_output=True)
        (out / (str(index) + "-stdout.txt")).write_text(result.stdout)
        (out / (str(index) + "-stderr.txt")).write_text(result.stderr)
        need(result.returncode == 0, item["portable"] + " failed: " + result.stderr)
        expected = json.loads((PACKAGE / item["expected"]).read_text())
        actual = json.loads(receipt.read_text())
        changed_fields = []
        if "checker_sha256" in expected:
            need(expected["checker_sha256"] == item["source_sha256"],
                 "The frozen receipt has a different checker pin")
            need(actual["checker_sha256"] == item["portable_sha256"],
                 "The fresh receipt has a different checker pin")
            expected.pop("checker_sha256")
            actual.pop("checker_sha256")
            changed_fields.append("checker_sha256")
        need(actual == expected, "The exact receipt differs: " + item["portable"])
        reports.append({
            "checker": item["portable"],
            "receipt": receipt.name,
            "receipt_sha256": sha256(receipt),
            "status": actual["status"],
            "matches_frozen_mathematical_result": True,
            "allowed_metadata_changes": changed_fields,
            "seconds": round(time.monotonic() - start, 6),
        })
        print(actual["status"], flush=True)
    report = {
        "status": "PASS_COMPLETED_PREFIX_OUTER_PACKAGE",
        "python": sys.version,
        "optimized": bool(sys.flags.optimize),
        "execution": "Sequential standard-library Python; no Git, network, or producer imports in review checkers",
        "historical_revision": sources["historical_revision"],
        "current_main_context": sources["current_main_context"],
        "checked_source_files": len(sources["files"]),
        "checks": reports,
        "fixed_past_supplier_verified": False,
        "fixed_past_distinct_prior_review": False,
        "current_selected_4470_compatibility_established": False,
        "complete_kappa_change": False,
    }
    (out / "REPLAY.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
