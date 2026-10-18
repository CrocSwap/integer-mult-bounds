"""Source/receipt failure boundaries for the registered exact verifier."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def invoke(root, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B',
        str(root/'research/hpe-energy-packed-radix/verify.py'), *map(str, args)],
        cwd=root, text=True, capture_output=True, timeout=90)


def export(root):
    package = root/'research/hpe-energy-packed-radix'
    package.mkdir(parents=True)
    for name in ('verify.py', 'SOURCES.json', 'RESULT.json'):
        shutil.copy2(HERE/name, package/name)
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage'] == 'input':
            dest = root/row['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/row['path'], dest)
    return package


class VerifierBoundaryTests(unittest.TestCase):
    def test_optimized_relocation_read_only_and_deterministic_rebuild(self):
        with tempfile.TemporaryDirectory(prefix='hpe-energy-test-') as directory:
            root = Path(directory)
            package = export(root)
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.rglob('*') if p.is_file()}
            result = invoke(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            generated = root/'rebuilt.json'
            result = invoke(root, '--write', generated)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(generated.read_bytes(), (package/'RESULT.json').read_bytes())

    def test_source_drift_rejected_before_math(self):
        with tempfile.TemporaryDirectory(prefix='hpe-energy-test-') as directory:
            root = Path(directory)
            export(root)
            source = root/'research/hyperplane-end-lean/HyperplaneEnd/Clifford.lean'
            source.write_bytes(source.read_bytes()+b'\n-- corrupted source\n')
            result = invoke(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source drift:', result.stderr)

    def test_receipt_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix='hpe-energy-test-') as directory:
            root = Path(directory)
            package = export(root)
            receipt = json.loads((package/'RESULT.json').read_text(encoding='utf-8'))
            receipt['source']['pairs'][0]['radix_bits'] += 1
            (package/'RESULT.json').write_text(json.dumps(receipt), encoding='utf-8')
            result = invoke(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('receipt mismatch', result.stderr)

    def test_duplicate_receipt_keys_rejected(self):
        with tempfile.TemporaryDirectory(prefix='hpe-energy-test-') as directory:
            root = Path(directory)
            package = export(root)
            receipt = (package/'RESULT.json').read_text(encoding='utf-8')
            (package/'RESULT.json').write_text('{"status":"duplicate",'+receipt[1:], encoding='utf-8')
            result = invoke(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('duplicate JSON key:', result.stderr)


if __name__ == '__main__':
    unittest.main()
