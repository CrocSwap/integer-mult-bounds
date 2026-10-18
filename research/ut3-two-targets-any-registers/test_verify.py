"""Mathematical and artifact failure controls, Apache-2.0; Codex assistance."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ut3_checker', HERE / 'verify.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class VerifyTests(unittest.TestCase):
    def test_noncommuting_mixed_coefficients(self):
        n, m = (1, 0), (1, 1)
        xy = checker.qword([(1, n), (2, m)], 2)
        yx = checker.qword([(2, m), (1, n)], 2)
        self.assertEqual(xy[3], checker.mm(n, m))
        self.assertEqual(yx[4], checker.mm(m, n))
        self.assertNotEqual(xy[3], yx[4])
        self.assertEqual(xy[4], checker.zero(2))
        self.assertEqual(yx[3], checker.zero(2))

    def test_all_two_factor_formal_images(self):
        generators = [(g, n) for g in (1, 2) for n in checker.rank_one_matrices(2)]
        for word in itertools.product(generators, repeat=2):
            formal = checker.formal_word(word, 2)
            self.assertEqual(checker.qword(word, 2), checker.quotient_formal(formal, 2))
            self.assertEqual(checker.regular_word(word, 2), checker.regular_formal(formal, 2))

    def test_proof_hypotheses_are_needed(self):
        # Without the zero linear boundary, the zero-product span inequality
        # would be false: one outer product has two active spans but one call.
        u, vt = (1, 0), (1,)
        self.assertNotEqual(checker.mm(u, vt), checker.zero(2))
        self.assertGreater(checker.rank(u) + checker.rank(vt), 1)
        # One central target has legal rank-one mixed coefficients at four calls.
        word = checker.direct(4, 1)
        self.assertEqual(checker.rank(checker.qword(word, 4)[3]), 1)
        self.assertEqual(checker.formal_word(word, 4), checker.target(4, 1))
        nilpotent = (2, 0)
        checker.validate_paid(nilpotent)
        self.assertEqual(checker.mm(nilpotent, nilpotent), checker.zero(2))
        self.assertEqual(checker.determinant_dual(nilpotent), 1)
        with self.assertRaisesRegex(ValueError, 'idempotent'):
            checker.validate_projector(nilpotent)

    def test_isolated_optimized_replay_and_real_corruptions(self):
        source_root = HERE.parents[1]
        source = 'research/bit-three-register-lower-bound/README.md'
        with tempfile.TemporaryDirectory(prefix='UT3 proof with spaces ') as directory:
            root = Path(directory)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            input_path = root / source
            input_path.parent.mkdir(parents=True)
            input_path.write_bytes((source_root / source).read_bytes())
            files = [p for p in root.rglob('*') if p.is_file()]
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

            def replay():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                    cwd=root, capture_output=True, text=True, timeout=30)

            result = replay()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('minimum=4w', result.stdout)
            after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            receipt_path = package / 'EXPECTED.json'
            original = receipt_path.read_bytes()
            for change in ('bool', 'omitted-fixture', 'underpriced'):
                receipt = json.loads(original)
                if change == 'bool':
                    receipt['schema_version'] = True
                elif change == 'omitted-fixture':
                    receipt['finite_evidence']['general_witnesses'].pop()
                else:
                    receipt['finite_evidence']['general_witnesses'][0][2] = 3
                receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
                broken = replay()
                self.assertNotEqual(broken.returncode, 0)
                self.assertIn('receipt mismatch', broken.stderr)
                self.assertEqual(json.loads(receipt_path.read_text()), receipt)
            receipt_path.write_bytes(original)
            input_path.write_bytes(input_path.read_bytes() + b'\ncorrupted input\n')
            broken = replay()
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn('source pin', broken.stderr)
            self.assertEqual(receipt_path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
