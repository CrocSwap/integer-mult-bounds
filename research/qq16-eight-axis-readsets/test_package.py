"""Entry-point failure controls. Gareth Davidson / OpenAI Codex, Apache-2.0."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


def exported(path):
    root = Path(path) / 'repo'
    package = root / 'research' / HERE.name
    shutil.copytree(HERE, package, copy_function=shutil.copyfile)
    for item in verify.read(HERE / 'SOURCES.json')['files']:
        if item['usage'] == 'input':
            dest = root / item['path'];dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / item['path'], dest)
    for p in root.rglob('*'):
        if p.is_dir():p.chmod(0o755)
    return root, package


class Controls(unittest.TestCase):
    def test_receipt_corruption_at_both_entrypoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            data = verify.read(package / 'RESULT.json');data['sharp_family_read_threshold'] = 87
            (package / 'RESULT.json').write_text(json.dumps(data))
            for command in ['verify.py', 'check_certificate.py']:
                p = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / command)],
                                   cwd=tmp, capture_output=True, text=True, timeout=120)
                self.assertNotEqual(p.returncode, 0)
                self.assertNotIn('PASS_', p.stdout)

    def test_live_input_and_predecessor_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            path = root / 'research/joint-query/evidence/JOINT-QUERY-TRANSFER.md'
            path.write_bytes(path.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'live source hash'):
                verify.sources(root)
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            path = package / 'predecessor/verify.py';path.write_bytes(path.read_bytes() + b'\n')
            p = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                               capture_output=True, text=True, timeout=30)
            self.assertNotEqual(p.returncode, 0);self.assertIn('predecessor source hash', p.stderr)

    def test_owner_word_fails_independent_checker_after_rebound_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            path = package / 'CERTIFICATE.json';data = verify.read(path)
            data['owner_words_by_prefix']['0'] = [];path.write_text(json.dumps(data))
            receipt = verify.read(package / 'RESULT.json');receipt['certificate_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            p = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'check_certificate.py')],
                               capture_output=True, text=True, timeout=30)
            self.assertNotEqual(p.returncode, 0);self.assertIn('actual owner evaluation', p.stderr)

    def test_strict_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            for raw in ['{"n":1,"n":1}', '{"n":NaN}', '{"n":Infinity}']:
                path.write_text(raw)
                with self.assertRaises(ValueError):verify.read(path)
        self.assertNotEqual(verify.canonical({'n': 88}), verify.canonical({'n': 88.0}))

    def test_output_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'keep.json';path.write_bytes(b'keep evidence\n')
            p = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'),
                                '--emit-result', str(path)], capture_output=True, text=True, timeout=20)
            self.assertNotEqual(p.returncode, 0);self.assertIn('output already exists', p.stderr)
            self.assertEqual(path.read_bytes(), b'keep evidence\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
