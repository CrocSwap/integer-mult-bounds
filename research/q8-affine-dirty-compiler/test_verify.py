#!/usr/bin/env python3
"""Semantic compiler mutations and read-only CLI failure tests. Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('q8_compiler', HERE / 'verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class CompilerTests(unittest.TestCase):
    def test_dirty_spectator_and_noncoordinate_positive(self):
        actual, _ = verifier.check_fixture(4, 3, 5, 1, payload=3)
        original = verifier.symbolic_data(4, 3)
        self.assertEqual(actual[2:], original[2:])
        self.assertNotEqual(actual[0], original[0])
        self.assertEqual(verifier.failure_controls(), 7)
        row = [0] * 8
        with self.assertRaisesRegex(ValueError, 'aliased role arrays'):
            verifier.run_program([row, row], [])

    def test_actual_compiler_mutations_are_detected(self):
        original = verifier.compile_coupling
        try:
            for mutation in (
                lambda r, u, v, g: original(r, u, v, g)[:-1],
                lambda r, u, v, g: original(r, u, v, g ^ 4),
                lambda r, u, v, g: [],
            ):
                verifier.compile_coupling = mutation
                with self.assertRaisesRegex(ValueError, 'dirty operator mismatch'):
                    verifier.check_fixture(3, 3, 5, 1)
        finally:
            verifier.compile_coupling = original

    def test_readonly_export_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix='q8-compiler-') as temp:
            root = Path(temp)
            package = root / 'research' / HERE.name
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'RESULT.json'):
                (package / name).write_bytes((HERE / name).read_bytes())
            sources = json.loads((HERE / 'SOURCES.json').read_text())
            for source in sources['files']:
                if source['usage'] == 'input':
                    target = root / source['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / source['path']).read_bytes())
            def snapshot():
                return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                      cwd=root, capture_output=True, text=True, timeout=60)
            before = snapshot()
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_Q8_AFFINE_DIRTY_COMPILER', result.stdout)
            self.assertEqual(snapshot(), before)
            receipt = package / 'RESULT.json'
            good = receipt.read_bytes()
            # JSON booleans and floats must not compare equal to integer counts.
            receipt.write_bytes(good.replace(b'"source_inputs": 3', b'"source_inputs": 3.0'))
            self.assertNotEqual(run().returncode, 0)
            receipt.unlink()
            self.assertNotEqual(run().returncode, 0)
            self.assertFalse(receipt.exists(), 'verification regenerated missing evidence')
            receipt.write_bytes(good)
            target = root / next(s['path'] for s in sources['files'] if s['usage'] == 'input')
            target.write_bytes(target.read_bytes() + b'corrupted source')
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256 mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
