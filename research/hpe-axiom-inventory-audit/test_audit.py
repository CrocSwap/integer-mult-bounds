"""Adversarial checks of the audit, its proposed repair and its evidence boundary."""
import contextlib
import difflib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hpe_inventory_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


@contextlib.contextmanager
def isolated():
    with tempfile.TemporaryDirectory(prefix="hpe-audit-control-") as temporary:
        root = Path(temporary).resolve()
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name, data in audit.pinned_inputs().items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        previous = audit.HERE, audit.ROOT
        audit.HERE, audit.ROOT = package, root
        try:
            yield root, package
        finally:
            audit.HERE, audit.ROOT = previous


class AuditControls(unittest.TestCase):
    def test_source_mutation_rejected(self):
        with isolated() as (root, _):
            path = root / audit.TARGET
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                audit.audit()

    def test_lean_transcript_mutation_rejected(self):
        with isolated() as (_, package):
            path = package / "fixtures/lean421.txt"
            path.write_text(path.read_text().replace("HPEInventoryFixture.extra", "propext"))
            with self.assertRaisesRegex(ValueError, "Lean transcript drift"):
                audit.audit()

    def test_materially_weakened_repairs_detected(self):
        original = (audit.ROOT / audit.TARGET).read_text()
        # Apply the submitted patch once; every mutant starts from that source.
        with isolated() as (root, package):
            subprocess.run(["git", "apply", str(package / "repair.patch")],
                           cwd=root, capture_output=True, check=True, timeout=30)
            fixed = (root / audit.TARGET).read_text()
        mutations = {
            "no_query_inventory": (
                "if len(wanted) != len(EXPECTED_RESULTS) or set(wanted) != set(EXPECTED_RESULTS):",
                "if False:"),
            "duplicate_reports_overwrite": ("if name in seen:", "if False:"),
            "extra_reports_ignored": ("if set(seen) != set(wanted):",
                                      "if set(wanted) - set(seen):"),
            "forbidden_axioms_accepted": ("        if extra:\n", "        if False:\n"),
        }
        for label, (before, after) in mutations.items():
            with self.subTest(mutation=label), isolated() as (_, package):
                self.assertEqual(fixed.count(before), 1)
                mutant = fixed.replace(before, after)
                patch = "".join(difflib.unified_diff(original.splitlines(True), mutant.splitlines(True),
                    fromfile="a/" + audit.TARGET, tofile="b/" + audit.TARGET))
                (package / "repair.patch").write_text(patch)
                with self.assertRaisesRegex(ValueError, "repair behavior differs"):
                    audit.audit()

    def test_receipt_mutation_rejected(self):
        with isolated() as (_, package):
            path = package / "RESULT.json"
            receipt = json.loads(path.read_text())
            receipt["omitted_queries_rejected_before_build"] = 0
            path.write_text(json.dumps(receipt))
            process = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py")],
                                     capture_output=True, text=True, timeout=120)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("committed receipt differs", process.stderr)

    def test_receipt_overwrite_refused(self):
        with isolated() as (_, package):
            path = package / "RESULT.json"
            before = path.read_bytes()
            process = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"),
                                      "--write-receipt", str(path)],
                                     capture_output=True, text=True, timeout=120)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("FileExistsError", process.stderr)
            self.assertEqual(before, path.read_bytes())

    def test_read_only_optimized_relocation(self):
        with isolated() as (root, package):
            files = [path for path in root.rglob("*") if path.is_file()]
            before = {path.relative_to(root): path.read_bytes() for path in files}
            for path in files:
                path.chmod(0o444)
            try:
                process = subprocess.run([sys.executable, "-I", "-B", "-O", str(package / "verify.py")],
                                         cwd=root, capture_output=True, text=True, timeout=120)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn("driver_cases=100", process.stdout)
                self.assertEqual(before, {path.relative_to(root): path.read_bytes() for path in files})
                self.assertEqual(set(before), {p.relative_to(root) for p in root.rglob("*") if p.is_file()})
            finally:
                for path in files:
                    path.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
