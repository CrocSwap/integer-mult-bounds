"""CLI checks of the evidence boundary. Arham Tahir / Codex. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class ArtifactChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'export'
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))

    def invoke(self, *args):
        return subprocess.run([sys.executable, '-Werror', '-I', '-O', '-B',
                               str(self.package / 'verify.py'), *args],
                              cwd=self.root, text=True, capture_output=True, timeout=60)

    def rejected(self, phrase, *args):
        result = self.invoke(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(phrase, result.stdout + result.stderr)

    def test_git_free_read_only(self):
        def hashes():
            return {str(p.relative_to(self.package)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.package.rglob('*') if p.is_file()}
        before = hashes()
        for path in self.package.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS_QQ16_BLOCK_SCALE_SCAN', result.stdout)
        self.assertEqual(hashes(), before)

    def test_source_authenticated_before_execution(self):
        path = self.package / 'vendor/pair.py'
        with path.open('a') as stream:
            stream.write('\nraise SystemExit("UNAUTHENTICATED_CODE_EXECUTED")\n')
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source SHA256 mismatch', result.stdout + result.stderr)
        self.assertNotIn('UNAUTHENTICATED_CODE_EXECUTED', result.stdout + result.stderr)

    def test_typed_or_missing_receipt(self):
        path = self.package / 'RESULT.json'
        receipt = json.loads(path.read_text())
        receipt['schema_version'] = True
        path.write_text(json.dumps(receipt))
        self.rejected('receipt mismatch')
        path.unlink()
        self.rejected('RESULT.json')

    def test_duplicate_receipt_key(self):
        path = self.package / 'RESULT.json'
        text = path.read_text()
        path.write_text('{"schema_version":1,' + text[1:])
        self.rejected('duplicate JSON key')

    def test_exclusive_deterministic_regeneration(self):
        path = self.package / 'RESULT.json'
        expected = path.read_bytes()
        self.rejected('refuse receipt overwrite', '--write')
        path.unlink()
        result = self.invoke('--write')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_bytes(), expected)


if __name__ == '__main__':
    unittest.main()
