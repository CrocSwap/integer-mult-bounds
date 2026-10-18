"""Mathematical and failure-boundary tests for the finite binding audit."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("hpe_binding_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (audit.ROOT / audit.EXACT).read_text(encoding="utf-8")
        cls.pairs, cls.circuits = audit.literal_data(cls.text)

    def test_semantic_C_square_and_inverse(self):
        """C(q)^2=X(q), C(q)^* C(q)=I, including non-coordinate q."""
        for q in (0, 1, 3, 128, 511):
            square = audit.compile_literal([["cg", q, True], ["cg", q, True]])
            inverse = audit.compile_literal([["cg", q, False], ["cg", q, True]])
            for x in range(audit.N):
                self.assertEqual(audit.run_literal(square, x), ({x ^ q: (1, 0)}, 0))
                self.assertEqual(audit.run_literal(inverse, x), ({x: (1, 0)}, 0))

    def test_semantic_zero_column_does_not_bind_input_character(self):
        """An actual Z0 mutation preserves column zero and changes 256 columns."""
        original = self.circuits["rhsLit1"]
        mutant = copy.deepcopy(original)
        mutant[0][2][0] = (mutant[0][2][0] + 2) % 4
        c0, c1 = map(audit.compile_literal, (original, mutant))
        changed = []
        for x in range(audit.N):
            v0, e0 = audit.run_literal(c0, x)
            v1, e1 = audit.run_literal(c1, x)
            self.assertEqual(e0, e1)
            sign = -1 if x & 1 else 1
            self.assertEqual(v1, {y: (sign*a, sign*b) for y, (a, b) in v0.items()})
            if v0 != v1:
                changed.append(x)
        self.assertEqual(changed, list(range(1, audit.N, 2)))

    def test_semantic_frame_literal_corruption(self):
        mutant = copy.deepcopy(self.circuits["fU1"])
        position = next(i for i, g in enumerate(mutant) if g[0] == "cg")
        mutant[position][2] = False
        compiled = audit.compile_literal(mutant)
        expected = audit.frame_kernel(self.pairs[0][1])
        with self.assertRaisesRegex(ValueError, "operator mismatch"):
            audit.assert_column(audit.run_literal(compiled, 0), expected(0), "changed frame C sign")

    def test_binding_source_drift(self):
        """Check the bytes actually loaded, before any producer execution."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in audit.check_sources():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / name, target)
            self.assertEqual(audit.check_sources(root), audit.check_sources())
            path = root / audit.CLIFFORD
            path.write_bytes(path.read_bytes().replace(b"a-sgn*b", b"a+sgn*b", 1))
            with self.assertRaisesRegex(ValueError, "source drift"):
                audit.check_sources(root)

    def test_binding_literal_grammar_and_inverse(self):
        pair = audit.declaration(self.text, "pair1", "Pair")
        with self.assertRaisesRegex(ValueError, "missing/duplicate"):
            audit.literal_data(self.text + "\ndef pair1 : Pair := " + pair + "\n\n")
        bad = self.text.replace(".cg 1 true,", ".cg 1 true ignored,", 1)
        with self.assertRaisesRegex(ValueError, "bad C gate"):
            audit.literal_data(bad)
        bad_gate = copy.deepcopy(next(g for g in self.circuits["wR1"] if g[0] == "pm"))
        bad_gate[2][0] ^= 1
        with self.assertRaisesRegex(ValueError, "bad permutation inverse"):
            audit.compile_literal([bad_gate])

    def test_receipt_corruption_typing_and_overwrite(self):
        result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            path.write_text(json.dumps(result), encoding="utf-8")
            audit.validate_receipt(path, result)
            bad = copy.deepcopy(result)
            bad["primitive_operator_checks"][0]["matrix_sha256"] = "0" * 64
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                audit.validate_receipt(path, result)
            bad = copy.deepcopy(result); bad["schema_version"] = True
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                audit.validate_receipt(path, result)
            path.write_text('{"pairs":3,"pairs":3}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate receipt key"):
                audit.validate_receipt(path, result)
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                audit.main(["--write-receipt", str(path)])
            self.assertEqual(path.read_bytes(), before)

    def test_readonly_relocation_optimized_replay(self):
        """A source export replays under -I -O -B with no writes or Git access."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for source in HERE.iterdir():
                if source.is_file():
                    shutil.copyfile(source, package / source.name)
            for name in audit.check_sources():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / name, target)
            files = sorted(p for p in root.rglob("*") if p.is_file())
            directories = sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True)
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            try:
                for p in files:
                    p.chmod(0o444)
                for p in directories:
                    p.chmod(0o555)
                process = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                         cwd=root, capture_output=True, text=True, timeout=180)
                self.assertEqual(process.returncode, 0, process.stderr[-2000:])
                self.assertIn("PASS_HPE_LEAN_SEMANTIC_BINDING", process.stdout)
                after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for p in directories:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
