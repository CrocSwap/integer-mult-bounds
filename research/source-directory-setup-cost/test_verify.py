"""Evidence integrity and unchanged Git-free package replays."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Integrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='source-setup-export-')
        self.package = Path(self.temp.name)/'research/source-directory-setup-cost'
        shutil.copytree(HERE, self.package)

    def tearDown(self):
        self.temp.cleanup()

    def run_verify(self, *args):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*args],
            cwd=self.temp.name, env=env, capture_output=True, text=True, encoding='utf-8', timeout=100)

    def inventory(self):
        return {str(p.relative_to(self.package)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.package.rglob('*') if p.is_file()}

    def test_git_free_read_only(self):
        before = self.inventory()
        result = self.run_verify()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_SOURCE_DIRECTORY_SETUP_COST',result.stdout)
        self.assertEqual(self.inventory(),before)

    def test_source_rejected_before_execution(self):
        path = self.package/'source/pr2569/words.py'
        path.write_bytes(b"raise RuntimeError('SOURCE_EXECUTED')\n"+path.read_bytes())
        result = self.run_verify()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('source SHA256',result.stderr)
        self.assertNotIn('SOURCE_EXECUTED',result.stderr)

    def test_exact_typed_receipt(self):
        path = self.package/'RESULT.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['setup_cases'][0]['w'] = True
        path.write_text(json.dumps(data),encoding='utf-8')
        result = self.run_verify()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('complete typed receipt mismatch',result.stderr)

    def test_missing_duplicate_and_exclusive_receipt(self):
        path = self.package/'RESULT.json'
        original = path.read_bytes()
        overwrite = self.run_verify('--write-result')
        self.assertNotEqual(overwrite.returncode,0)
        self.assertIn('refusing to overwrite receipt',overwrite.stderr)
        self.assertEqual(path.read_bytes(),original)
        path.write_text('{"status":0,"status":1}',encoding='utf-8')
        duplicate = self.run_verify()
        self.assertIn('duplicate JSON key',duplicate.stderr)
        path.unlink()
        missing = self.run_verify()
        self.assertNotEqual(missing.returncode,0)
        self.assertIn('FileNotFoundError',missing.stderr)
        regenerated = self.run_verify('--write-result')
        self.assertEqual(regenerated.returncode,0,regenerated.stderr)
        self.assertEqual(path.read_bytes(),original)


if __name__ == '__main__':
    unittest.main()
