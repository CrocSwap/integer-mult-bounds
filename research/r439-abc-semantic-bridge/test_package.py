"""Subprocess relocation and corruption tests. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageTests(unittest.TestCase):
    def test_relocated_and_corrupted_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            manifest = json.loads((HERE / 'SOURCES.json').read_text())
            sources = [f['path'] for f in manifest['files'] if f['usage'] == 'input']
            for name in sources:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                      cwd=tmp, text=True, capture_output=True, timeout=120)
            positive = run()
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertIn('PASS_R439_ABC_SEMANTIC_BRIDGE', positive.stdout)
            cases = [(package / 'inputs/candidate.json.gz', 'candidate pin'),
                     (root / sources[0], 'source pin'),
                     (package / 'RESULT.json', 'receipt mismatch')]
            for path, message in cases:
                with self.subTest(message=message):
                    original = path.read_bytes()
                    if path.name == 'RESULT.json':
                        receipt = json.loads(original)
                        receipt['bills']['candidate']['ADDs'] -= 1
                        path.write_text(json.dumps(receipt))
                    else:
                        path.write_bytes(original + b'corruption')
                    result = run()
                    path.write_bytes(original)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)


if __name__ == '__main__':
    unittest.main()
