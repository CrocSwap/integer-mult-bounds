"""Mathematical and integrity regression controls. Apache-2.0."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import fixtures as F
import geometry as G
import independent as I


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        C.sources()
        cls.model = G.load_model()
        cls.receipt = C.strict_load(C.HERE/"EXPECTED.json")
        cls.gram = I.gram_model()
        cls.u = [F.ZERO]*112
        for i in cls.receipt["geometry"]["free_boundary"]["deleted"]:
            cls.u[i] = F.q(cls.model["x"][i][0])
        cls.v = [F.ZERO]*112
        cls.v[0] = F.ONE
        cls.shear = [[1, 0, 0], [0, 1, 0], [-1, 0, 1]]
        cls.nonreal = [[1, (1, 1), 1], [1, (2, 1), 1], [(0, 1), (1, 2), (1, 1)]]

    def test_boundary_and_the_missing_charge(self):
        result = F.evaluate(self.model, [0, 1], self.u, self.v, self.shear)
        self.assertEqual(result["replacement_ranks"], [7, 8, 7])
        self.assertFalse(result["at_least_two_rank_eight"])
        self.assertEqual(result["full_factor_ranks"], [9, 9])
        self.assertEqual(result["full_entries_checked"], 12544)
        with self.assertRaisesRegex(ValueError, "complete COPY power bill"):
            F.power_certificate([7, 8, 0])
        self.assertEqual(F.power_certificate([6, 6, 4])["replacement_floor"], "2*8^q")
        # The quantified comparison's exponent boundary is substantive:
        # the lower envelope would not imply it for q=2.
        self.assertLess(6**2+6**2+4**2, 2*8**2)

    def test_correction_scope_and_dirty_values(self):
        bad = list(self.u)
        bad[0] = F.ONE
        with self.assertRaisesRegex(ValueError, "free correction"):
            F.evaluate(self.model, [0, 1], bad, self.v, self.shear)
        two = list(self.v)
        two[1] = F.ONE
        with self.assertRaisesRegex(ValueError, "singleton"):
            F.evaluate(self.model, [0, 1], self.u, two, self.shear)
        with self.assertRaisesRegex(ValueError, "singleton"):
            F.evaluate(self.model, [0, 1], self.u, [F.ZERO]*112, self.shear)
        with self.assertRaisesRegex(ValueError, "distinct"):
            F.evaluate(self.model, [0, 0], self.u, self.v, self.shear)
        zero = F.evaluate(self.model, [0, 1], [F.ZERO]*112, self.v, self.nonreal)
        self.assertGreaterEqual(zero["whole_COPY_rank_sum"], 64)

    def test_coupled_ordinary_inverse_is_essential(self):
        for fault in ["ordinary_inverse", "conjugate_transpose"]:
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, "all-pairs decoder identity"):
                F.evaluate(self.model, [0, 1], self.u, self.v, self.nonreal, fault=fault)
        with self.assertRaisesRegex(ValueError, "singular"):
            F.evaluate(self.model, [0, 1], self.u, self.v, [[1, 0, 0], [1, 0, 0], [0, 0, 1]])

    def test_independent_finite_premise_mutations(self):
        original = self.receipt["geometry"]
        mutations = []
        value = deepcopy(original); value["strata"].pop(); mutations.append(value)
        value = deepcopy(original); value["strata"][0]["even_neighbor_spans"][0] += 1; mutations.append(value)
        value = deepcopy(original); value["pairings"][0]["costs"][0][0] = 7; mutations.append(value)
        value = deepcopy(original); value["strata"][0]["free_min"] = 25; mutations.append(value)
        value = deepcopy(original); value["free_boundary"]["deleted"][0] = value["free_boundary"]["deleted"][1]; mutations.append(value)
        value = deepcopy(original); value["summary"]["singleton_sites"] = 111; mutations.append(value)
        for i, value in enumerate(mutations):
            with self.subTest(mutation=i), self.assertRaises(ValueError):
                I.check(value, self.gram)

    def test_source_inventory_and_strict_typed_receipts(self):
        manifest = C.strict_load(C.HERE/"SOURCES.json")
        bad = deepcopy(manifest)
        bad["files"].pop()
        with self.assertRaisesRegex(ValueError, "source inventory"):
            C.sources(manifest=bad)
        bad = deepcopy(manifest)
        bad["files"].append(deepcopy(bad["files"][-1]))
        with self.assertRaisesRegex(ValueError, "source inventory"):
            C.sources(manifest=bad)
        for other in [True, 1.0]:
            with self.assertRaises(ValueError):
                C.same({"count": 1}, {"count": other}, "typed mismatch")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"invalid.json"
            for raw in ['{"x":1,"x":2}', '{"x":NaN}']:
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    C.strict_load(path)

    def test_readonly_optimized_export_and_real_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="column-floor-export-") as temp:
            base = Path(temp)
            export = base/"export"
            package = export/"research"/C.HERE.name
            package.mkdir(parents=True)
            for source in C.HERE.iterdir():
                if source.is_file() and source.suffix in {".py", ".json"}:
                    shutil.copyfile(source, package/source.name)
            for relative in C.INPUTS:
                target = export/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C.ROOT/relative, target)
            files = [p for p in export.rglob("*") if p.is_file()]
            directories = [export]+[p for p in export.rglob("*") if p.is_dir()]
            before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            argv = [sys.executable, "-I", "-O", "-B", str(package/"verify.py")]
            try:
                for p in files:
                    p.chmod(0o444)
                for p in directories:
                    p.chmod(0o555)
                result = subprocess.run(argv, cwd=base, text=True, capture_output=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertIn("receipt_sha256="+C.digest(self.receipt), result.stdout)
                self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
                fixture = export/"research/p112-single-lift/geometry.py"
                fixture.chmod(0o644)
                original = fixture.read_bytes()
                fixture.write_bytes(original+b"\n# intentional test corruption\n")
                bad = subprocess.run(argv, cwd=base, text=True, capture_output=True, timeout=20)
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn("source bytes", bad.stderr)
                fixture.write_bytes(original)
                receipt = package/"EXPECTED.json"
                receipt.chmod(0o644)
                altered = deepcopy(self.receipt)
                altered["summary"]["boundary_ranks"][-1] = 0
                receipt.write_text(json.dumps(altered))
                bad = subprocess.run(argv, cwd=base, text=True, capture_output=True, timeout=180)
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn("complete typed receipt mismatch", bad.stderr)
            finally:
                for p in directories:
                    p.chmod(0o755)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"existing.json"
            path.write_bytes(b"KEEP\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(C.HERE/"verify.py"),
                                     "--write", str(path)], text=True, capture_output=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing existing output", result.stderr)
            self.assertEqual(path.read_bytes(), b"KEEP\n")


if __name__ == "__main__":
    unittest.main()
