"""Behavioral boundaries for the source-bound certificate replay."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


class ReplayBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='p104-export-')
        self.root = Path(self.tmp.name)
        self.package = self.root/'research'/P.name
        shutil.copytree(P, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for name in json.loads((P/'VERIFY.json').read_text())['inputs']:
            dst = self.root/name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, dst)

    def tearDown(self):
        for directory, dirs, files in os.walk(self.root):
            Path(directory).chmod(0o755)
            for name in files:
                (Path(directory)/name).chmod(0o644)
        self.tmp.cleanup()

    def run_script(self, script='verify.py', *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package/script), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=180)

    def test_optimized_readonly_export(self):
        paths = [p for p in self.root.rglob('*') if p.is_file()]
        before = {p.relative_to(self.root):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        for p in paths:
            p.chmod(0o444)
        for p in self.root.rglob('*'):
            if p.is_dir():
                p.chmod(0o555)
        self.root.chmod(0o555)
        replay = self.run_script()
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertIn('matched=104', replay.stdout)
        after = {p.relative_to(self.root):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_source_digest_before_replay(self):
        name = json.loads((P/'VERIFY.json').read_text())['inputs'][0]
        with (self.root/name).open('ab') as out:
            out.write(b'\n')
        for script in ('verify.py', 'independent.py', 'build.py'):
            args = ('--out', str(self.root/'new.json')) if script == 'build.py' else ()
            result = self.run_script(script, *args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source', result.stderr)
        self.assertFalse((self.root/'new.json').exists())

    def test_typed_receipt_drift(self):
        path = self.package/'RESULT.json'
        receipt = json.loads(path.read_text())
        receipt['targets'][53]['added_rank_mass'] = 333.0
        path.write_text(json.dumps(receipt))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('typed complete result equality', result.stderr)

    def test_independent_chronology_control(self):
        path = self.package/'CERTIFICATE.json'
        cert = json.loads(path.read_text())
        late = next(v for p in cert['targets'][2]['paths'] for v in p if v[1] > 0)
        late[1] = 0
        path.write_text(json.dumps(cert))
        result = self.run_script('independent.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('chronological acquisition', result.stderr)

    def test_exclusive_literal_output(self):
        path = self.root/'word.json'
        result = self.run_script('verify.py', '--emit-target', '53', '--out', str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())['new_helpers'], 37)
        original = path.read_bytes()
        result = self.run_script('verify.py', '--emit-target', '53', '--out', str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
