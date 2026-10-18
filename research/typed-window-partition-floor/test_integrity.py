"""Git-free, read-only replay and corrupted dependency/output checks."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


class Integrity(unittest.TestCase):
    def test_export_and_rejections(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / REL
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for item in json.loads((HERE / 'SOURCES.json').read_text())['files']:
                if item['usage'] == 'input':
                    target = root / item['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / item['path'], target)
            def hashes():
                return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob('*') if p.is_file()}
            def run(*args):
                return subprocess.run([sys.executable, '-I', '-B', str(package / 'verify.py'), *args],
                                      cwd=root, capture_output=True, text=True, timeout=120)
            before = hashes()
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(hashes(), before)
            self.assertNotEqual(run('--write').returncode, 0)
            self.assertEqual(hashes(), before)
            for name in ('vendor/pr2626/verify.py', 'POTENTIAL.json', 'RESULT.json'):
                path = package / name
                original = path.read_bytes()
                if name.endswith('verify.py'):
                    path.write_bytes(original + b'\nraise RuntimeError("MUST_NOT_IMPORT")\n')
                else:
                    value = json.loads(original)
                    if type(value) is list:
                        value[1]['potential'] += 1000
                    else:
                        value['states'] = True
                    path.write_text(json.dumps(value), encoding='utf-8')
                broken = run()
                self.assertNotEqual(broken.returncode, 0, name)
                self.assertNotIn('MUST_NOT_IMPORT', broken.stderr)
                path.write_bytes(original)
            self.assertEqual(hashes(), before)


if __name__ == '__main__':
    unittest.main()
