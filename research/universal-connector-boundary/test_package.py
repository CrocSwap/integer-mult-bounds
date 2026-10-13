#!/usr/bin/env python3
"""Relocated replay, exact regeneration, and deliberate package corruptions."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(root, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / script), *args],
                          cwd=root.parent, text=True, capture_output=True, timeout=60)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix="universal connector ") as temp:
        copy = Path(temp) / "package with spaces"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        initial = run(copy, "verify.py")
        require(initial.returncode == 0, initial.stderr)
        certificate = copy / "CERTIFICATE.json"
        before = certificate.read_bytes()
        require(run(copy, "generate.py").returncode == 0, "generator failed")
        require(certificate.read_bytes() == before, "certificate regeneration differs")
        expected = copy / "EXPECTED.json"
        expected_before = expected.read_bytes()
        regenerated = run(copy, "verify.py", "--write-summary")
        require(regenerated.returncode == 0, regenerated.stderr)
        require(expected.read_bytes() == expected_before, "evidence regeneration differs")
        failures = []

        def corrupt_json(name, filename, edit, diagnostic):
            path = copy / filename
            saved = path.read_bytes()
            payload = json.loads(saved)
            edit(payload)
            path.write_text(json.dumps(payload) + "\n")
            result = run(copy, "verify.py")
            path.write_bytes(saved)
            require(result.returncode != 0 and diagnostic in result.stderr,
                    f"wrong corruption outcome for {name}: {result.stdout} {result.stderr}")
            failures.append(name)

        corrupt_json("fabricated_full_coverage", "CERTIFICATE.json",
                     lambda d: d["censuses"][1].__setitem__("max_coverage", 32),
                     "independent census mismatch")
        corrupt_json("omitted_census", "CERTIFICATE.json",
                     lambda d: d["censuses"].pop(), "missing census")
        corrupt_json("unrestored_connector", "CERTIFICATE.json",
                     lambda d: d["schedules"]["five_extra_source"]["word"].pop(),
                     "root free-algebra identity")
        corrupt_json("unpaid_child", "CERTIFICATE.json",
                     lambda d: d["lowered"]["five_extra_output"]["query_leaf_prices"].__setitem__("B4", 27),
                     "unpaid recursive child")
        corrupt_json("fabricated_evidence", "EXPECTED.json",
                     lambda d: d.__setitem__("unit_lower_bound", 72), "expected evidence differs")
        reference = copy / "references/PR934-README.md"
        saved = reference.read_bytes()
        reference.write_bytes(saved + b"\nChanged predecessor bytes.\n")
        result = run(copy, "verify.py")
        reference.write_bytes(saved)
        require(result.returncode != 0 and "reference SHA256 mismatch" in result.stderr,
                "corrupt reference accepted or wrong failure")
        failures.append("changed_predecessor")
        require(run(copy, "verify.py").returncode == 0, "restored package no longer passes")
    print("PASS_UNIVERSAL_CONNECTOR_PACKAGE relocation=1 regeneration=2 corruptions=" + str(len(failures)))


if __name__ == "__main__":
    main()
