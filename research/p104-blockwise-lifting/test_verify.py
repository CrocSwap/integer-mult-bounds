"""Source and exported evidence controls, beyond the mathematical mutations."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class ExportControls(unittest.TestCase):
    def replay(self, package, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *args],
                              cwd=package.parent, capture_output=True, text=True, timeout=90)

    def test_optimized_git_free_read_only_and_no_source_cache(self):
        with tempfile.TemporaryDirectory(prefix='p104-block-export-') as d:
            p = Path(d)/'package'
            shutil.copytree(ROOT, p, ignore=shutil.ignore_patterns('__pycache__'))
            for q in p.rglob('*'):
                if q.is_file():
                    q.chmod(0o444)
            result = self.replay(p)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_P104_BLOCKWISE_LIFTING', result.stdout)
            self.assertFalse(list(p.rglob('*.pyc')))

    def test_source_corruption_precedes_execution(self):
        with tempfile.TemporaryDirectory(prefix='p104-block-source-') as d:
            p = Path(d)/'package'
            shutil.copytree(ROOT, p, ignore=shutil.ignore_patterns('__pycache__'))
            (p/'vendor/lifting.py').write_text('raise RuntimeError("EXECUTED_BAD_SOURCE")\n')
            result = self.replay(p)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256', result.stderr)
            self.assertNotIn('RuntimeError: EXECUTED_BAD_SOURCE', result.stderr)

    def test_typed_receipt_and_occupied_output(self):
        with tempfile.TemporaryDirectory(prefix='p104-block-receipt-') as d:
            p = Path(d)/'package'
            shutil.copytree(ROOT, p, ignore=shutil.ignore_patterns('__pycache__'))
            data = json.loads((p/'RESULT.json').read_text())
            data['no_new_kappa'] = 1
            (p/'RESULT.json').write_text(json.dumps(data))
            result = self.replay(p)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('typed receipt mismatch', result.stderr)
            occupied = Path(d)/'existing.json'
            occupied.write_text('KEEP\n')
            result = self.replay(p, '--out', str(occupied))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(occupied.read_text(), 'KEEP\n')


if __name__ == '__main__':
    unittest.main()
