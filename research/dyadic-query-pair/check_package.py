"""Offline relocation and evidence/source corruption checks in temporary copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(root, success, marker):
    completed = subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py")],
                               cwd=root.parent, text=True, capture_output=True)
    combined = completed.stdout + completed.stderr
    if success:
        if completed.returncode != 0 or marker not in combined:
            raise RuntimeError("relocated replay failed: " + combined[-2000:])
    elif completed.returncode == 0 or marker not in combined:
        raise RuntimeError("fault was not rejected at the required predicate: " + combined[-2000:])


def change_json(root, name, mutate):
    path = root / name
    value = json.loads(path.read_text())
    mutate(value)
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def main():
    with tempfile.TemporaryDirectory(prefix="dyadic query pair offline ") as scratch:
        root = Path(scratch) / "standalone package with spaces"
        shutil.copytree(ROOT, root)
        run(root, True, "PASS_DYADIC_QUERY_PAIR")
        cases = []

        def mutate_source(root):
            path = root / "vendor/pr521-PROOF.md"
            path.write_bytes(path.read_bytes() + b"\nsource drift\n")

        cases.append(("immutable source drift", mutate_source, "source SHA256"))

        def missing_inventory(root):
            change_json(root, "SOURCES.json", lambda v: v["immutable_inputs"].pop())

        cases.append(("source inventory omission", missing_inventory, "complete immutable source inventory"))

        def boolean_count(root):
            change_json(root, "CERTIFICATE.json",
                        lambda v: v["fixture"].__setitem__("private_rows_added", False))

        cases.append(("integer zero changed to Boolean", boolean_count, "complete CERTIFICATE mismatch"))

        def invoice_count(root):
            change_json(root, "CERTIFICATE.json", lambda v: v["fixture"]["fused_invoice"].__setitem__(
                "ordinary_children", 2))

        cases.append(("unpaid child in receipt", invoice_count, "complete CERTIFICATE mismatch"))

        def query_power(root):
            change_json(root, "PROGRAM.json", lambda v: v["fused_chronological_events"][2].__setitem__(
                2, 1 << 54))

        cases.append(("literal central-power corruption", query_power, "literal PROGRAM mismatch"))

        def code_drift(root):
            path = root / "program.py"
            path.write_bytes(path.read_bytes() + b"\n# implementation drift\n")

        cases.append(("implementation/source binding drift", code_drift, "complete CERTIFICATE mismatch"))
        for name, mutate, marker in cases:
            pristine = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            mutate(root)
            run(root, False, marker)
            for path, data in pristine.items():
                (root / path).write_bytes(data)
            print("rejected:", name)
    print("PASS_DYADIC_PACKAGE_CONTROLS: relocated offline replay and 6 deliberate faults")


if __name__ == "__main__":
    main()
