"""Entry-point controls in an isolated Git-free export."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
REL = PKG.relative_to(ROOT)


def run(root, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(root / REL / 'verify.py'), *args],
                          cwd=root, capture_output=True, text=True, timeout=45)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(PKG, self.root / REL, ignore=shutil.ignore_patterns('__pycache__'))
        manifest = json.loads((PKG / 'SOURCES.json').read_text())
        for row in manifest['files']:
            path = self.root / row['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['path'], path)
        self.pkg = self.root / REL

    def tearDown(self):
        self.temp.cleanup()

    def test_export_and_no_writes(self):
        def snapshot():
            return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        completed = run(self.root)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(before, snapshot())

    def test_source_corruption(self):
        path = self.root / 'research/joint-query/certificate.json.gz'
        path.write_bytes(path.read_bytes() + b'corrupt')
        completed = run(self.root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('source SHA256', completed.stderr)

    def test_typed_receipt_and_semantics(self):
        path = self.pkg / 'RESULT.json'
        original = path.read_bytes()
        for mutation in ('type', 'witness', 'gate'):
            value = json.loads(original)
            if mutation == 'type':
                value['schema_version'] = True
            elif mutation == 'witness':
                value['witness']['required_original_x_port1'] = '0'
            else:
                value['gate_controls']['prefixes'][0][1][1] = '0'
            path.write_text(json.dumps(value))
            completed = run(self.root)
            self.assertNotEqual(completed.returncode, 0, mutation)
            self.assertIn('exact typed receipt', completed.stderr)

    def test_missing_receipt_and_explicit_emit(self):
        (self.pkg / 'RESULT.json').unlink()
        self.assertNotEqual(run(self.root).returncode, 0)
        emitted = run(self.root, '--emit')
        self.assertEqual(emitted.returncode, 0, emitted.stderr)
        self.assertEqual(json.loads(emitted.stdout), json.loads((PKG / 'RESULT.json').read_text()))
        self.assertFalse((self.pkg / 'RESULT.json').exists())


if __name__ == '__main__':
    unittest.main()
