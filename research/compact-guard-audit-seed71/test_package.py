#!/usr/bin/env python3
"""Relocated replay and real subprocess mutations; standard library only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(script, cwd, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(script), *args],
                          cwd=cwd, text=True, capture_output=True, timeout=180)


def main():
    with tempfile.TemporaryDirectory(prefix="compact guard seed71 ") as tmp:
        export = Path(tmp) / "minimal checkout with spaces"
        package = export / REL
        pins = json.loads((HERE / "SOURCES.json").read_text())
        paths = [Path(p) for p in pins["required_files"]]
        paths += [REL / name for name in ("verify.py", "SOURCES.json", "EXPECTED.json")]
        for rel in paths:
            dest = export / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
        script = package / "verify.py"
        result = run(script, tmp)
        require(result.returncode == 0 and "PASS_COMPACT_GUARD_AUDIT" in result.stdout,
                "relocated optimized replay failed: " + result.stderr)
        print(result.stdout.strip(), flush=True)

        failures = []
        source = export / "scripts/audit_compact_controls.py"
        original = source.read_bytes()
        source.write_bytes(original + b"\n# deliberate drift\n")
        rejected = run(script, tmp)
        require(rejected.returncode != 0 and "source SHA256 mismatch" in rejected.stderr,
                "changed predecessor was accepted")
        source.write_bytes(original)
        failures.append("source_drift")

        original_script = script.read_text()
        mutations = [
            ("nonstrict_guard", "* ds[i] < self.A", "* ds[i] <= self.A", "nonsaturated iff failed"),
            ("forbid_last_carry", "range(self.n - 1)", "range(self.n)", "nonsaturated iff failed"),
            ("target_only", "correct = (yy, tt) == (target, t)", "correct = yy == target", "nonsaturated iff failed"),
            ("omit_highest_xor", "return y + highest * (1 - 2 * ((y // place) & 1)) * place", "return y", "highest selected XOR composition failed"),
        ]
        for label, before, after, expected_error in mutations:
            require(original_script.count(before) == 1, "mutation not unique: " + label)
            script.write_text(original_script.replace(before, after))
            rejected = run(script, tmp)
            require(rejected.returncode != 0 and expected_error in rejected.stderr,
                    "mathematical mutant not rejected: " + label + rejected.stderr)
            failures.append(label)
        script.write_text(original_script)

        expected = package / "EXPECTED.json"
        original_receipt = expected.read_text()
        changed = json.loads(original_receipt)
        changed["status"] = "DELIBERATELY_WRONG"
        expected.write_text(json.dumps(changed))
        rejected = run(script, tmp)
        require(rejected.returncode != 0 and "deterministic receipt mismatch" in rejected.stderr,
                "changed receipt was accepted")
        expected.write_text(original_receipt)
        failures.append("receipt_drift")

        rejected = run(script, tmp, "--write", str(expected))
        require(rejected.returncode != 0 and "refusing to overwrite" in rejected.stderr,
                "occupied output accepted")
        require(expected.read_text() == original_receipt, "occupied output was modified")
        failures.append("occupied_output")

        for path in export.rglob("*"):
            if path.is_file():
                require(path.read_bytes() == (ROOT / path.relative_to(export)).read_bytes(),
                        "relocation left an unexpected file mutation")
        print("PASS_COMPACT_GUARD_PACKAGE relocated_isolated_optimized=PASS faults="
              + str(len(failures)) + " [" + ", ".join(failures) + "]")


if __name__ == "__main__":
    main()
