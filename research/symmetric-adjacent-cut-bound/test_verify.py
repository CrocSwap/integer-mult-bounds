#!/usr/bin/env python3
"""Failure-sensitive controls for the exact mathematical package. Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("symmetric_verify", HERE/"verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageTests(unittest.TestCase):
    def relocated(self, root):
        package = root/"research"/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for item in v.read_json(HERE/"SOURCES.json")["files"]:
            if item["usage"] == "input":
                dst = root/item["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT/item["path"], dst)
        return package

    def run_verifier(self, package, *flags):
        return subprocess.run([sys.executable,"-I","-O","-B",str(package/"verify.py"),*flags],
                              text=True,capture_output=True,timeout=30)

    def test_positive_receipt_and_semantic_controls(self):
        self.assertEqual(v.compute(), v.read_json(HERE/"EXPECTED.json"))

    def test_detectors_are_necessary(self):
        # Delete actual acceptance predicates in disposable in-memory variants.
        # The production reject helper must then expose unexpected acceptance.
        source = (HERE/"verify.py").read_text()
        cases = [
            ('need(actual == expected, "full formal endpoint")',
             lambda m: m.endpoint({(0,1):1},{(0,1):2}), "full formal endpoint"),
            ('need(rank(rows(projector, r)) == 1, "paid scalar rank")',
             lambda m: m.paid(3,2,0,m.eye(2)), "paid scalar rank"),
            ('need(mm(projector, projector, r) == projector, "paid scalar idempotence")',
             lambda m: m.paid(3,2,0,2), "paid scalar idempotence"),
            ('need(rank(rows(s, r)) == r, "singular scalar map")',
             lambda m: m.scalar(3,2,0), "singular scalar map"),
        ]
        for predicate, operation, reason in cases:
            with self.subTest(reason=reason):
                self.assertEqual(source.count(predicate),1)
                m = types.ModuleType("detector_removed")
                m.__file__ = str(HERE/"verify.py")
                exec(compile(source.replace(predicate,"pass"),m.__file__,"exec"),m.__dict__)
                with self.assertRaisesRegex(m.Failure,"control unexpectedly accepted"):
                    m.reject(lambda: operation(m),reason)

    def test_missing_receipt_is_not_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.relocated(Path(d))
            (p/"EXPECTED.json").unlink()
            result = self.run_verifier(p)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("EXPECTED.json",result.stderr)
            self.assertFalse((p/"EXPECTED.json").exists())

    def test_scientific_receipt_mutations(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.relocated(Path(d))
            original = v.read_json(p/"EXPECTED.json")
            for key in ("complete_projector_factor_checks", "no_new_kappa"):
                mutant = dict(original)
                mutant[key] = -1
                (p/"EXPECTED.json").write_text(json.dumps(mutant))
                result = self.run_verifier(p)
                self.assertNotEqual(result.returncode,0)
                self.assertIn("fixed receipt mismatch",result.stderr)
            (p/"EXPECTED.json").write_text('{"schema_version":1,"schema_version":2}')
            result = self.run_verifier(p)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("duplicate JSON key",result.stderr)

    def test_source_drift_rejected_before_replay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self.relocated(root)
            item = next(x for x in v.read_json(p/"SOURCES.json")["files"] if x["usage"] == "input")
            (root/item["path"]).write_text("changed source")
            result = self.run_verifier(p)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("source drift",result.stderr)

    def test_optimized_readonly_relocation_and_explicit_generation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self.relocated(root)
            before = (p/"EXPECTED.json").read_bytes()
            result = self.run_verifier(p,"--write")
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual((p/"EXPECTED.json").read_bytes(),before)
            files = [f for f in root.rglob("*") if f.is_file()]
            saved = {str(f.relative_to(root)): f.read_bytes() for f in files}
            try:
                for f in files:
                    f.chmod(0o444)
                result = self.run_verifier(p)
                self.assertEqual(result.returncode,0,result.stderr)
                now = {str(f.relative_to(root)): f.read_bytes() for f in root.rglob("*") if f.is_file()}
                self.assertEqual(saved,now)
            finally:
                for f in files:
                    f.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
