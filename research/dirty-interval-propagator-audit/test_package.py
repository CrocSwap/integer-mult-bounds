#!/usr/bin/env python3
"""Independent prefix controls and real package-failure tests; Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("interval_audit", PACKAGE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def right_inverse_step(matrix, operation):
    """P^-1 E^-1: update a column, appending letters on the right."""
    src, dst, factor, sign = operation
    for row in matrix:
        for word, coefficient in list(row[dst].items()):
            new = word + (factor,)
            row[src][new] = row[src].get(new, 0) - sign * coefficient
            if row[src][new] == 0:
                del row[src][new]


def copy_minimal(root):
    target = root / "research" / PACKAGE.name
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(audit.ROOT / row["path"], path)
    return target


def run(target, *arguments):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py"),
                           *map(str, arguments)], cwd=target, text=True,
                          capture_output=True, timeout=60)


class PackageTests(unittest.TestCase):
    def test_prefix_and_inverse_prefix_positive_contract(self):
        """The obstruction must not manufacture a failure of the prefix lemma."""
        boundaries = 0
        for n in range(1, 9):
            size = (n - 1).bit_length() + 2
            bound = 2 * 3 ** ((n - 1).bit_length())
            for sign in (1, -1):
                forward = audit.symbolic_identity(size)
                backward = audit.symbolic_identity(size)
                for operation in [None, *audit.emit(n, sign)]:
                    if operation is not None:
                        audit.symbolic_step(forward, operation)
                        right_inverse_step(backward, operation)
                    for matrix in (forward, backward):
                        for row in matrix:
                            self.assertLessEqual(sum(abs(c) for p in row for c in p.values()), bound)
                            for poly in row:
                                self.assertTrue(all(audit.ordered(word) for word in poly))
                    boundaries += 1
        self.assertEqual(boundaries, 446)

    def test_dispatcher_change_detected(self):
        source = (audit.ROOT / audit.DISPATCHER).read_text()
        changed = source.replace("(x,z,B,-1)", "(x,z,B,1)")
        self.assertNotEqual(changed, source)
        actual = audit.source_emitter(changed)
        self.assertNotEqual(actual(7, 1), audit.emit(7, 1))

    def test_wrong_order_loses_quadratic_block(self):
        factors = audit.family(7, 64)
        correct = audit.multiply(factors[1], factors[4])
        wrong = audit.multiply(factors[4], factors[1])
        self.assertEqual(audit.norm(correct), 4096)
        self.assertEqual(audit.norm(wrong), 1)
        self.assertNotEqual(correct, wrong)

    def test_source_tamper_rejected_before_execution(self):
        with tempfile.TemporaryDirectory(prefix="interval source fault ") as folder:
            root = Path(folder)
            target = copy_minimal(root)
            path = root / audit.DISPATCHER
            path.write_text(path.read_text().replace("(x,z,B,-1)", "(x,z,B,1)"))
            result = run(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256 drift", result.stderr)
            self.assertNotIn(audit.MARKER, result.stdout)

    def test_certificate_tamper_rejected(self):
        with tempfile.TemporaryDirectory(prefix="interval receipt fault ") as folder:
            target = copy_minimal(Path(folder))
            path = target / "CERTIFICATE.json"
            data = json.loads(path.read_text())
            data["parametric_examples"][1]["block_norm"] = "65"
            path.write_text(json.dumps(data))
            result = run(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate mismatch", result.stderr)
            self.assertNotIn(audit.MARKER, result.stdout)

    def test_write_refuses_occupied_path(self):
        with tempfile.TemporaryDirectory(prefix="interval output fault ") as folder:
            target = copy_minimal(Path(folder))
            output = Path(folder) / "occupied.json"
            output.write_bytes(b"preserve this file\n")
            result = run(target, "--write", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("File exists", result.stderr)
            self.assertEqual(output.read_bytes(), b"preserve this file\n")

    def test_readonly_relocated_exact_receipt(self):
        with tempfile.TemporaryDirectory(prefix="interval readonly relocation ") as folder:
            root = Path(folder)
            target = copy_minimal(root)
            paths = list(root.rglob("*"))
            before = {str(p.relative_to(root)): p.read_bytes() for p in paths if p.is_file()}
            try:
                for path in paths:
                    path.chmod(0o555 if path.is_dir() else 0o444)
                root.chmod(0o555)
                result = run(target)
                self.assertEqual(result.returncode, 0, result.stderr)
                expected = json.loads((target / "CERTIFICATE.json").read_text())
                self.assertIn("receipt_sha256=" + audit.digest(expected), result.stdout)
                after = {str(p.relative_to(root)): p.read_bytes()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                root.chmod(0o755)
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
