#!/usr/bin/env python3
"""Authentication and native counter-component failure controls."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('counter_verify', ROOT/'verify.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class Controls(unittest.TestCase):
    def test_altered_stream_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(ROOT/'SOURCES.json', root/'SOURCES.json')
            shutil.copytree(ROOT/'sources', root/'sources')
            (root/'sources/stream.py').chmod(0o600)
            with (root/'sources/stream.py').open('a') as stream:
                stream.write('\n# Deliberate source mutation.\n')
            with self.assertRaisesRegex(ValueError, 'source digest'):
                v.authenticate(root)

    def test_altered_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'SOURCES.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'manifest digest'):
                v.authenticate(root)

    def test_typed_receipt_rejected(self):
        expected = json.loads((ROOT/'RESULT.json').read_text())
        actual = json.loads(json.dumps(expected))
        actual['records'][0]['parameters'][0] = True
        with self.assertRaisesRegex(ValueError, 'typed deterministic receipt'):
            v.check_receipt(expected, actual)

    def test_receipt_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'receipt.json'
            target.write_text('keep these bytes')
            completed = subprocess.run(
                [sys.executable,'-I','-Werror','-B',str(ROOT/'verify.py'),'--write',str(target)],
                capture_output=True,text=True,timeout=120)
            self.assertNotEqual(completed.returncode,0)
            self.assertIn('FileExistsError',completed.stderr)
            self.assertEqual(target.read_text(),'keep these bytes')

    def test_written_formula_branches(self):
        # Literal source-derived maxima for two genuinely different lifetime cuts.
        self.assertEqual(v.bound(1,1,1,3,3)['intrinsic'], 18)
        self.assertEqual(v.bound(1,1,2,3,3)['intrinsic'], 28)
        self.assertEqual(v.bound(1,4096,2,2,3)['intrinsic'], 41)


if __name__ == '__main__':
    unittest.main()
