"""Behavioral controls for the finite images, mutable boundary and cleanup."""

import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def load(path, name="reviewed_module"):
    import types
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


MODEL = load(ROOT / "model.py")
VERIFY = load(ROOT / "verify.py")


class DefectControls(unittest.TestCase):
    def test_complete_images_and_transversal_indices(self):
        for rank, count, bits in ((1, 3, 2), (2, 25, 6), (3, 10225, 15)):
            row = MODEL.census(rank)
            self.assertEqual(row["defect_values"], count)
            self.assertEqual(row["coset_bits"], bits)
            self.assertEqual(sum(int(k) * v for k, v in row["fiber_histogram"].items()), 1 << bits)
        with self.assertRaisesRegex(ValueError, "complete census rank"):
            MODEL.census(4)
        basis, generators, _ = MODEL.transversal(2)
        self.assertEqual(abs(VERIFY.determinant(basis)), 64)
        missing = list(MODEL.representatives(generators[:-1], 8))
        self.assertEqual(len(missing), 32)
        self.assertNotEqual(len({MODEL.defect(x, 2) for x in missing}), 25)

    def test_period_and_noncongruence_are_different(self):
        x, y, t = (0, 0, 0, 0), (0, 0, 1, 1), (1, 0, 0, 0)
        self.assertEqual(MODEL.defect(x, 1), MODEL.defect(y, 1))
        shifted_y = tuple(a + b for a, b in zip(y, t, strict=True))
        self.assertNotEqual(MODEL.defect(t, 1), MODEL.defect(shifted_y, 1))
        # Any one output for the shared zero label fails at one of the sources.
        code_only_update = MODEL.defect(t, 1)
        self.assertNotEqual(code_only_update, MODEL.defect(shifted_y, 1))
        self.assertNotEqual(MODEL.defect(t, 1), MODEL.defect(x, 1))  # q=1 is invalid.
        for shift in (-10, -2, 2, 14):
            self.assertEqual(MODEL.defect((shift, 0, 0, 0), 1), MODEL.defect(x, 1))

    def test_dirty_and_missing_cleanup_are_rejected_by_behavior(self):
        source = [1, 0, 0, 0]
        clean = source + [0, 0] + [0] * 8
        expected = MODEL.signed_encode(MODEL.defect(source, 1), 2)
        dirty = source + [1, 0] + [0] * 8
        result = MODEL.run_gates(dirty, MODEL.pair_gates())
        actual = sum(v << i for i, v in enumerate(result[6:14]))
        self.assertNotEqual(actual, expected)
        self.assertEqual(result[:6], dirty[:6])  # Restoring dirty work alone is insufficient.
        omitted = MODEL.run_gates(clean, MODEL.pair_gates()[:-1])
        self.assertNotEqual(omitted[4:6], [0, 0])
        correct = MODEL.run_gates(clean, MODEL.pair_gates())
        self.assertEqual(correct[4:6], [0, 0])
        # Literal gate reversal restores every bit even for arbitrary initial work.
        self.assertEqual(MODEL.run_gates(result, reversed(MODEL.pair_gates())), dirty)

    def test_floor_and_encoding_boundaries(self):
        self.assertEqual((-1 + 2) // 2 - (-1) // 2, 1)
        self.assertNotEqual(int((-1 + 2) / 2) - int((-1) / 2), 1)
        with self.assertRaisesRegex(ValueError, "overflow"):
            MODEL.signed_encode([4], 3)
        with self.assertRaisesRegex(ValueError, "aliases"):
            MODEL.run_gates([0], [("cnot", 0, 0)])
        with self.assertRaisesRegex(ValueError, "integer coordinates"):
            MODEL.lift([True, 0, 0, 0], 1)

    def test_lookup_charge_includes_cleanup_and_output(self):
        images = MODEL.full_box(1)
        invoice = MODEL.table_invoice(4, images, 2)
        self.assertEqual((invoice["toffoli"], invoice["cnot"], invoice["x"]), (96, 48, 64))
        self.assertEqual(invoice["clean_equality_work_bits"], 3)
        with self.assertRaisesRegex(ValueError, "full address table"):
            MODEL.table_invoice(3, images, 2)
        self.assertEqual(2 * (32 - 1) * (1 << 32), 266287972352)

    def test_typed_receipt_and_source_mutants(self):
        with tempfile.TemporaryDirectory(prefix="p104-defect-controls-") as temporary:
            target = Path(temporary) / "export"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            verification = load(target / "verify.py")
            data = json.loads((target / "RESULT.json").read_text())
            data["censuses"][0]["rank"] = True
            (target / "RESULT.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "typed mathematical receipt"):
                verification.main()
            source = target / "vendor/lattice.py"
            source.write_bytes(source.read_bytes() + b"\n# corrupted source\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                verification.authenticate()

    def test_literal_word_mutant_changes_covered_operator(self):
        code = (ROOT / "model.py").read_text()
        changed = code.replace("br, bi = sr - (-di) // 2, si - dr // 2",
                               "br, bi = sr - (-di) // 2, si + dr // 2")
        self.assertNotEqual(code, changed)
        import types
        mutant = types.ModuleType("wrong_floor_sign")
        exec(compile(changed, "wrong_floor_sign.py", "exec"), mutant.__dict__)
        value = [2, 0, 0, 0]
        self.assertNotEqual(mutant.lift(value, 1), MODEL.lift(value, 1))

    def test_bytecode_and_optimized_independent_asserts(self):
        with tempfile.TemporaryDirectory(prefix="p104-defect-loader-") as temporary:
            target = Path(temporary) / "export"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            source = target / "vendor/lattice.py"
            cache = Path(importlib.util.cache_from_source(str(source)))
            cache.parent.mkdir(parents=True)
            poison = compile("raise RuntimeError('cached poison executed')", str(source), "exec")
            stat = source.stat()
            cache.write_bytes(importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(stat.st_mtime), stat.st_size)
                              + marshal.dumps(poison))
            verification = load(target / "verify.py")
            self.assertEqual(verification.authenticate().index_counts(1), [2])
            assertion = target / "assertion.py"
            assertion.write_text("assert False, 'assertion stays active'\n")
            with self.assertRaisesRegex(AssertionError, "stays active"):
                verification.source_module(assertion, "assertion")

    def test_readonly_gitfree_optimized_replay(self):
        with tempfile.TemporaryDirectory(prefix="p104-defect-readonly-") as temporary:
            target = Path(temporary) / "export"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            paths = [target, *target.rglob("*")]
            before = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in paths if p.is_file()}
            try:
                for path in paths:
                    path.chmod(0o555 if path.is_dir() else 0o444)
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                                        cwd=temporary, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_P104_POINTWISE_DEFECT", result.stdout)
                after = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in target.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
