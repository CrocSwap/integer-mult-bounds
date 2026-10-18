#!/usr/bin/env python3
"""Small exhaustive algebra oracle and source/relocation controls. Apache-2.0."""
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


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


generator = module('span_generator', 'enumerate.py')
checker = module('span_checker', 'verify.py')


class MathematicalControls(unittest.TestCase):
    def test_complete_small_mask_oracle(self):
        """All 4096 triples of 4-bit rows, all 16 targets, literal 8 masks."""
        decisions = 0
        for rows in itertools.product(range(16), repeat=3):
            possible = set()
            for subset in itertools.product([False, True], repeat=3):
                total = 0
                for use, row in zip(subset, rows):
                    if use:
                        total ^= row
                possible.add(total)
            sets = [frozenset(i for i in range(4) if row >> i & 1) for row in rows]
            for target in range(16):
                solution, dual = generator.solve(list(enumerate(rows)), target)
                expected = target in possible
                self.assertEqual(solution is not None, expected)
                self.assertEqual(checker.spans(sets, {i for i in range(4) if target >> i & 1}),
                                 expected)
                if expected:
                    actual = 0
                    for source, row in enumerate(rows):
                        if solution >> source & 1:
                            actual ^= row
                    self.assertEqual(actual, target)
                    self.assertIsNone(dual)
                else:
                    self.assertEqual((target & dual).bit_count() % 2, 1)
                    self.assertTrue(all((row & dual).bit_count() % 2 == 0 for row in rows))
                decisions += 1
        self.assertEqual(decisions, 65536)

    def test_rational_geometry_against_determinants(self):
        # Exhaust all pairs of small integer 2-vectors, including dependence
        # modulo two with rational independence and negative coefficients.
        vectors = list(itertools.product(range(-2, 3), repeat=2))
        for a, b in itertools.product(vectors, repeat=2):
            determinant = a[0]*b[1]-a[1]*b[0]
            expected_rank = 2 if determinant else int(any(a) or any(b))
            self.assertEqual(len(generator.integer_basis([a, b])), expected_rank)
            normals = checker.normal_vectors([a, b], 2)
            self.assertEqual(len(normals), 2-expected_rank)
            self.assertTrue(all(sum(x*y for x, y in zip(v, normal)) == 0
                                for normal in normals for v in (a, b)))

    def test_normalized_source_cancellation(self):
        # q has clean response x0+x1; the original read also adds source x0.
        # The normalized replacement is x1, not x0+x1.
        mask, dual = generator.solve([(1, 2)], 3 ^ 1)
        self.assertEqual(mask, 2)
        self.assertIsNone(dual)
        self.assertFalse(checker.spans([{1}], {0, 1}))
        self.assertTrue(checker.spans([{1}], {0, 1} ^ {0}))

    def test_json_ambiguity_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            checker.strict_json('{"reads":2102,"reads":2101}')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            checker.strict_json('{"value":NaN}')


class RelocationControls(unittest.TestCase):
    def test_minimal_optimized_relocation_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='bit-source-span-') as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            source = root / checker.SOURCE
            source.parent.mkdir(parents=True)
            shutil.copyfile(checker.ROOT / checker.SOURCE, source)

            def run(script, *args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', package / script, *args],
                                      cwd=root, text=True, capture_output=True, timeout=60)

            positive = run('verify.py')
            self.assertEqual(positive.returncode, 0, positive.stdout + positive.stderr)
            self.assertIn('exclusion_witnesses=429 controls=11', positive.stdout)
            regenerated = run('enumerate.py')
            self.assertEqual(regenerated.returncode, 0, regenerated.stdout + regenerated.stderr)

            pins = package / 'SOURCES.json'
            original_pins = pins.read_bytes()
            payload = json.loads(original_pins)
            payload['files'] = [p for p in payload['files'] if p['usage'] != 'input']
            pins.write_text(json.dumps(payload))
            failed = run('verify.py')
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('input pin inventory', failed.stderr)
            pins.write_bytes(original_pins)

            original = source.read_bytes()
            source.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            failed = run('verify.py')
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source hash mismatch', failed.stderr)
            source.unlink()
            failed = run('verify.py')
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('FileNotFoundError', failed.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
