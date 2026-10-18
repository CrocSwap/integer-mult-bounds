"""Mathematical boundary and source/receipt failure controls. Apache-2.0."""

from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search
import verify
import independent


class MathematicalControls(unittest.TestCase):
    def test_full_ball_inverse_and_no_depth_loss(self):
        words, layers = search.ball()
        self.assertEqual(layers, [1, 10, 69, 370, 1646, 6312, 22168])
        for matrix, word in words.items():
            with self.subTest(matrix=matrix):
                self.assertEqual(search.execute(word), matrix)
                self.assertEqual(search.multiply(matrix, search.inverse(matrix)), search.IDENTITY)
        self.assertEqual(independent.rational_ball(3)[1], layers[:4])

    def test_shortcut_arbitrary_dirt_and_prefix_contract(self):
        _, reference, _, _, _, _, _ = verify.sources()
        t, s, w = ("T", 0), ("S", 0), verify.WORK
        for q in map(Q, (-3, -2, 2, 3)):
            word = verify.shortcut(["add", list(t), list(s), q.numerator, 1], reference)
            verify.local_check(q, word)
            rows = {t: {0: Q(1)}, s: {1: Q(1)}, w: {2: Q(1)}}
            for primitive in word:
                verify.step(rows, primitive)
                self.assertEqual(rows[s], {1: 1})
                self.assertEqual(rows[t][0], 1)
                self.assertLessEqual(abs(rows[t].get(1, 0)), abs(q))
                self.assertIn(rows[w], ({2: 1}, {}))
                self.assertTrue(all(v.denominator == 1 for row in rows.values() for v in row.values()))

    def test_declared_adverse_cases(self):
        _, reference, _, _, _, _, _ = verify.sources()
        self.assertEqual(len(verify.controls(reference)), 10)
        entries = verify.read(HERE / "EXPECTED.json")["coefficients"]
        minima = {e["coefficient"]: e["two_register_minimum"] for e in entries}
        distances = {m: len(w) for m, w in search.ball()[0].items()}
        self.assertEqual(len(independent.independent_controls(entries, minima, distances)), 7)

    def test_negative_sign_is_gate_relabeling(self):
        for q in (Q(1, 2), Q(3, 4), Q(5, 2), Q(29, 8), Q(17)):
            row = search.metric([q], search.ball()[0])[0]
            self.assertIsNotNone(row["word"])
            verify.local_check(-q, verify.two_register_word(row["word"], negative=True))


class PackageControls(unittest.TestCase):
    def test_offline_relocation_recompression_corruption_and_preservation(self):
        pins = verify.read(HERE / "SOURCES.json")
        with tempfile.TemporaryDirectory(prefix="restored source 29 ") as temporary:
            root = Path(temporary) / "minimal checkout with spaces"
            package = root / "research/complex-restored-source29"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for name in pins["files"]:
                destination = root / name
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / name, destination)
            source = root / verify.PROVIDER / "LOCAL-PROGRAMS.json.gz"
            source.write_bytes(gzip.compress(gzip.decompress(source.read_bytes()), compresslevel=1, mtime=123))
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]

            def run(*extra):
                return subprocess.run(command + list(extra), cwd=temporary, text=True, capture_output=True, timeout=90)

            def snapshot():
                return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob("*") if p.is_file()}

            before = snapshot()
            completed = run()
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("PASS_RESTORED_SOURCE_CK", completed.stdout)
            self.assertEqual(before, snapshot(), "default replay wrote into the source tree")

            # Default and --write must both preserve an existing certificate.
            certificate = package / "EXPECTED.json"
            original_certificate = certificate.read_bytes()
            preserved = run("--write", str(certificate))
            self.assertNotEqual(preserved.returncode, 0)
            self.assertIn("refusing to overwrite", preserved.stderr)
            self.assertEqual(certificate.read_bytes(), original_certificate)

            # Float/int equality cannot conceal a changed deterministic receipt.
            receipt = json.loads(original_certificate)
            receipt["coefficient_count"] = 103.0
            certificate.write_text(json.dumps(receipt), encoding="utf-8")
            altered = run()
            self.assertNotEqual(altered.returncode, 0)
            self.assertIn("complete certificate mismatch", altered.stderr)
            self.assertEqual(json.loads(certificate.read_text())["coefficient_count"], 103.0)
            certificate.write_bytes(original_certificate)

            # Corrupt decompressed input, not a gzip header.
            source.write_bytes(gzip.compress(gzip.decompress(source.read_bytes()) + b" "))
            corrupted = run()
            self.assertNotEqual(corrupted.returncode, 0)
            self.assertIn("source pin:", corrupted.stderr)


if __name__ == "__main__":
    unittest.main()
