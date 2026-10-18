"""Offline/optimized replay plus proof-relevant package-corruption controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(path, success):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(path / "verify.py")],
                            cwd=path.parent, capture_output=True, text=True)
    if (result.returncode == 0) != success:
        raise ValueError("unexpected package result\n" + result.stdout + result.stderr)
    if success and "PASS_BALANCED_CYCLIC_LIFT" not in result.stdout:
        raise ValueError("missing success evidence")
    return (result.stdout + result.stderr).splitlines()[-1]


def main():
    with tempfile.TemporaryDirectory(prefix="balanced cyclic offline ") as root:
        path = Path(root) / "standalone research package"
        shutil.copytree(HERE, path, ignore=shutil.ignore_patterns("__pycache__"))
        results = {"offline_optimized": run(path, True)}
        source = path / "vendor/pr628-DIRTY-PROOF.md"
        original = source.read_bytes()
        source.write_bytes(original + b"\nchanged immutable input\n")
        results["source_drift"] = run(path, False)
        source.write_bytes(original)
        certificate = path / "CERTIFICATE.json"
        original = certificate.read_bytes()
        obj = json.loads(original)
        obj["product_checks"]["seed55_fixture"]["stats"]["borrowed_scalar_words"] = True
        certificate.write_text(json.dumps(obj))
        results["certificate_boolean"] = run(path, False)
        certificate.write_bytes(original)
        program = path / "lift.py"
        original = program.read_text()
        changed = original.replace("(helper, pivot, Fraction(1))", "(helper, pivot, Fraction(-1))")
        if changed == original:
            raise ValueError("ineffective instruction mutation")
        program.write_text(changed)
        results["instruction_sign"] = run(path, False)
        program.write_text(original)
        print(json.dumps(results, indent=2))
    print("PASS_BALANCED_CYCLIC_PACKAGE: offline optimized replay; 3 rejected corruptions")


if __name__ == "__main__":
    main()
