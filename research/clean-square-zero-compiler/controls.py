"""Actual relocated CLI and mutation controls. JoyboyBrian; Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class Controls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='clean-square-zero-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        original = Path(__file__).resolve().parent
        self.package = self.root / 'research' / original.name
        shutil.copytree(original, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        repository = original.parent.parent
        manifest = json.loads((original / 'VERIFY.json').read_text())
        for name in manifest['inputs']:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repository / name, destination)

    def run_script(self, script, optimize=False):
        command = [sys.executable, '-I'] + (['-O'] if optimize else [])
        command += ['-W', 'error', '-B', str(self.package / script)]
        return subprocess.run(command, cwd=self.root, capture_output=True,
                              text=True, timeout=20, check=False)

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def replace(self, old, new):
        path = self.package / 'verify.py'
        source = path.read_text()
        self.assertEqual(source.count(old), 1)
        path.write_text(source.replace(old, new))

    def assert_rejected(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr)

    def test_git_free_readonly_normal_and_optimized(self):
        before = self.snapshot()
        for optimize in (False, True):
            for script in ('verify.py', 'literal.py'):
                result = self.run_script(script, optimize)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS_CLEAN_SQUARE_ZERO_', result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_declared_source_corruption_rejects(self):
        path = self.root / 'research/square-zero-idempotent-compiler/PROOF.md'
        path.write_bytes(path.read_bytes() + b'\ncorrupted source\n')
        self.assert_rejected(self.run_script('verify.py', True), 'source SHA256')

    def test_boolean_receipt_rejects(self):
        path = self.package / 'RESULT.json'
        receipt = json.loads(path.read_text())
        receipt['boundary_controls'] = True
        path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
        self.assert_rejected(self.run_script('verify.py', True), 'typed scientific receipt mismatch')

    def test_wrong_reflection_role_needs_literal_oracle(self):
        self.replace("gates.extend(b + a + [('reflect', pivot)]", 
                     "gates.extend(b + a + [('reflect', (pivot + 1) % width)]")
        primary = self.run_script('verify.py', True)
        self.assertEqual(primary.returncode, 0, primary.stderr)
        self.assert_rejected(self.run_script('literal.py', True), 'literal full-input endpoint')

    def test_omitted_even_clean_projector_rejects(self):
        self.replace('result.append((((1 << q) - 1) | h, sources | h, n))',
                     'pass  # actual omitted clean projector control')
        self.assert_rejected(self.run_script('verify.py', True), 'full canonical formal endpoint')

    def test_missing_scalar_inverse_rejects(self):
        self.replace("+ list(reversed(a)) + list(reversed(b)))", 
                     "+ list(reversed(b)))")
        self.assert_rejected(self.run_script('verify.py', True), 'clean scalar tariff')
        self.assert_rejected(self.run_script('literal.py', True), 'literal full-input endpoint')


if __name__ == '__main__':
    unittest.main(verbosity=2)
