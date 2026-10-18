#!/usr/bin/env python3
"""Reproduce source, receipt and predicate mutation controls in a private copy.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = Path("research/connector-covering-code/cycle_search.cpp")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def execute(argv, *, data=None, timeout=120):
    return subprocess.run(argv, input=data, text=True, capture_output=True,
                          check=False, timeout=timeout)


def failure(result, diagnostic):
    require(result.returncode != 0 and diagnostic in result.stderr + result.stdout,
            "failure control did not reject as expected: " + diagnostic)


def main():
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    require(compiler is not None, "C++17 compiler required")
    manifest = json.loads((HERE / "VERIFY.json").read_text())
    with tempfile.TemporaryDirectory(prefix="capacity-controls-") as temp:
        root = Path(temp)
        package = root / HERE.relative_to(ROOT)
        shutil.copytree(HERE, package)
        for name in manifest["inputs"]:
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        source = root / NATIVE
        original = source.read_text()
        command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
        # A source change must reject before compilation, regardless of mode.
        source.write_text(original + "\n// mutation control\n")
        failure(execute(command, timeout=15), "source digest mismatch")
        source.write_text(original)

        # Compile the actual altered predicate, not merely a changed oracle.
        mutations = [
            ("reset", "high_parity ^= gaps[i] & 1;", "high_parity = 0;",
             "0001021323 0101202222\n", "0\n"),
            ("fiber_cap", "if (sizes[point] > 8) return false;",
             "if (sizes[point] > 9) return false;", "0012131213 7700000000\n", "1\n"),
        ]
        for name, old, new, data, expected in mutations:
            require(original.count(old) == 1, "ambiguous source mutation: " + name)
            source.write_text(original.replace(old, new))
            binary = root / name
            built = execute([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                             str(package / "audit.cpp"), "-o", str(binary)], timeout=60)
            require(built.returncode == 0, "mutant compilation failed: " + built.stderr)
            result = execute([str(binary), "--query"], data=data, timeout=20)
            require(result.returncode == 0 and result.stdout == expected and not result.stderr,
                    "actual native mutation did not discriminate: " + name)
            failure(execute([str(binary), "--query"], data="01021323\n", timeout=20),
                    "missing gap vector")
        source.write_text(original)

        # A valid source replay must reject a plausible but altered receipt.
        receipt_path = package / "RESULT.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["native_domains"][0]["accepted"] += 1
        receipt_path.write_text(json.dumps(receipt))
        failure(execute(command, timeout=180), "receipt differs from fresh checks")
    print("PASS_CAPACITY_FAILURE_CONTROLS source_pin=1 native_mutants=2 malformed_query=2 receipt=1")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        raise SystemExit("FAIL_CAPACITY_FAILURE_CONTROLS " + str(error)) from error
