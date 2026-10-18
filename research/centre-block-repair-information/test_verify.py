#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral integrity controls for the exact information certificate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
primary = types.ModuleType('primary_under_test')
primary.__file__ = str(HERE / 'verify.py')
exec(compile((HERE / 'verify.py').read_bytes(), primary.__file__, 'exec'), primary.__dict__)


class IntegrityControls(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'), *args],
                              text=True, capture_output=True, timeout=120, cwd=ROOT)

    def test_changed_executable_input_is_rejected_before_execution(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        with tempfile.TemporaryDirectory(prefix='centre-block-source-') as tmp:
            root = Path(tmp)
            for row in manifest['files']:
                if row['usage'] == 'input':
                    dst = root / row['path']
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row['path'], dst)
            changed = root / primary.PREDECESSOR
            changed.write_bytes(b"raise RuntimeError('changed bytes executed')\n" + changed.read_bytes())
            with self.assertRaisesRegex(ValueError, '^source pin: ' + primary.PREDECESSOR + '$'):
                primary.load(root)

    def test_receipt_cannot_extend_coverage_to_seven(self):
        with tempfile.TemporaryDirectory(prefix='centre-block-receipt-') as tmp:
            path = Path(tmp) / 'overclaimed.json'
            receipt = json.loads((HERE / 'RESULT.json').read_text())
            receipt['all_blocks_proved']['maximum_size'] = 7
            path.write_text(json.dumps(receipt))
            completed = self.run_cli('--receipt', str(path))
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('receipt mismatch', completed.stderr)

    def test_write_does_not_replace_occupied_output(self):
        with tempfile.TemporaryDirectory(prefix='centre-block-output-') as tmp:
            path = Path(tmp) / 'retained.json'
            original = b'preserve earlier evidence\n'
            path.write_bytes(original)
            completed = self.run_cli('--write', str(path))
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('FileExistsError', completed.stderr)
            self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main(verbosity=1)
