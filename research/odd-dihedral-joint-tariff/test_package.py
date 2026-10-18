#!/usr/bin/env python3
"""Fail-closed package and detector-sensitivity checks. Apache-2.0."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("odd_dihedral_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = v.compute()
        cls.expected = v.strict_json(HERE / "RECEIPT.json")

    def test_complete_receipt_and_semantic_controls(self):
        self.assertEqual(v.canonical(self.actual), v.canonical(self.expected))
        self.assertIn("joint deficit n=3", self.actual["semantic_controls"])
        self.assertIn("dirty spectator leaks into target", self.actual["semantic_controls"])

    def test_scientific_receipt_corruptions(self):
        mutants = []
        d = deepcopy(self.expected); d["counts"]["complete_single_targets"] -= 1; mutants.append(d)
        d = deepcopy(self.expected); d["counts"]["complete_short_words"] = True; mutants.append(d)
        d = deepcopy(self.expected); d["domains"]["odd_periods_all_targets"].append(33); mutants.append(d)
        d = deepcopy(self.expected); d["semantic_controls"].remove("joint deficit n=3"); mutants.append(d)
        d = deepcopy(self.expected); d["mathematical_digest_sha256"] = "0" * 64; mutants.append(d)
        d = deepcopy(self.expected); del d["counts"]["single_call_omissions"]; mutants.append(d)
        for mutant in mutants:
            with self.assertRaisesRegex(ValueError, "receipt differs"):
                v.verify_receipt(self.actual, mutant)

    def test_detector_removal_is_observed(self):
        source = (HERE / "verify.py").read_text()
        controls = [
            ('    require(nx + ny >= qjoint, "joint cut invoice")', '    pass  # removed joint invoice'),
            ('    require(nx >= qx, "x cut invoice")', '    pass  # removed x invoice'),
            ('    require(ny >= qy, "y cut invoice")', '    pass  # removed y invoice'),
            ('    require(state == target_matrix(targets, roles), "formal endpoint mismatch")',
             '    pass  # removed full endpoint'),
        ]
        for old, new in controls:
            self.assertEqual(source.count(old), 1)
            namespace = {"__file__": str(HERE / "verify.py"), "__name__": "mutated_verifier"}
            exec(compile(source.replace(old, new), "detector_removed.py", "exec"), namespace)
            with self.assertRaisesRegex(ValueError, "negative control accepted"):
                namespace["semantic_controls"]()

    def test_wrong_joint_formula_is_observed(self):
        source = (HERE / "verify.py").read_text()
        old = 'sum((k, e) == (m, 1) for k, e in pairs))'
        self.assertEqual(source.count(old), 1)
        namespace = {"__file__": str(HERE / "verify.py"), "__name__": "mutated_verifier"}
        exec(compile(source.replace(old, '0)'), "joint_formula_removed.py", "exec"), namespace)
        with self.assertRaisesRegex(ValueError, "joint cut / shortest distance"):
            namespace["compute"]()

    def test_independent_checker_refuses_disabled_assertions(self):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "independent_check.py")],
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent checker requires assertions", result.stderr)

    def test_receipt_source_and_relocated_cli(self):
        with tempfile.TemporaryDirectory(prefix="odd-dihedral-package-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for item in v.strict_json(HERE / "SOURCES.json")["files"]:
                if item["usage"] == "input":
                    dest = root / item["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(HERE.parents[1] / item["path"], dest)
            def run(*args):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *args],
                                      cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      timeout=60)
            def failure(message):
                result = run()
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(message, result.stderr)
            receipt = package / "RECEIPT.json"
            original = receipt.read_bytes()
            receipt.unlink()
            failure("RECEIPT.json")
            self.assertFalse(receipt.exists(), "missing evidence must not be regenerated")
            receipt.write_text('{"x":0,"x":1}')
            failure("duplicate JSON key")
            receipt.write_text('{}')
            failure("receipt differs from exact recomputation")
            receipt.write_bytes(original)
            item = next(x for x in v.strict_json(HERE / "SOURCES.json")["files"] if x["usage"] == "input")
            source = root / item["path"]
            saved = source.read_bytes()
            source.write_bytes(saved + b"\nsource drift\n")
            failure("source hash mismatch")
            source.write_bytes(saved)
            regenerated = run("--emit")
            self.assertEqual(regenerated.returncode, 0, regenerated.stderr)
            self.assertEqual(regenerated.stdout.encode(), original)
            files = [p for p in root.rglob("*") if p.is_file()]
            before = {str(p.relative_to(root)): p.read_bytes() for p in files}
            for p in files:
                p.chmod(0o444)
            directories = [root] + [p for p in root.rglob("*") if p.is_dir()]
            for p in directories:
                p.chmod(0o555)
            try:
                passed = run()
                self.assertEqual(passed.returncode, 0, passed.stderr)
                self.assertIn("PASS_ODD_DIHEDRAL_JOINT_TARIFF", passed.stdout)
                after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for p in directories:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
