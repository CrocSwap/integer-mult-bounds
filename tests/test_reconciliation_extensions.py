"""Historical evidence survives reviewed appended build targets without weakening pins."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('extension_checker', ROOT/'scripts/verify_pr_reconciliation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class HistoricalMakefile(unittest.TestCase):
    def test_append_preserves_original_but_mutations_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old = b'old-target:\n\techo original\n'
            historical = root/'research/community-batch1099-audit/checkpoints/Makefile1047'
            historical.parent.mkdir(parents=True)
            historical.write_bytes(old)
            item = dict(integrated_path='Makefile', integrated_sha256=hashlib.sha256(old).hexdigest())
            current = root/'Makefile'
            with patch.object(checker, 'ROOT', root):
                current.write_bytes(old + b'\nnew-target:\n\techo added\n')
                checker.check_batch1047_file(item)
                current.write_bytes(old.replace(b'original', b'changed'))
                with self.assertRaisesRegex(ValueError, 'content changed'):
                    checker.check_batch1047_file(item)
                current.write_bytes(old + b'\nnew-target:\n')
                historical.write_bytes(old + b'altered')
                with self.assertRaisesRegex(ValueError, 'Changed historical'):
                    checker.check_batch1047_file(item)

    def test_other_source_remains_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'source.py').write_bytes(b'changed')
            with patch.object(checker, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Changed integrated file'):
                    checker.check_batch1047_file(dict(integrated_path='source.py', integrated_sha256='0'*64))
