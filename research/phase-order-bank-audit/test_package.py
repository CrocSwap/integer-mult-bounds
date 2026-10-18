#!/usr/bin/env python3
"""Meaningful export/read-only and corruption controls. Apache-2.0."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def fingerprint(path):
    return {f.name:hashlib.sha256(f.read_bytes()).hexdigest()
            for f in path.iterdir() if f.is_file()}


class PackageControls(unittest.TestCase):
    def test_relocated_readonly_replay(self):
        with tempfile.TemporaryDirectory(prefix='phase-bank-export-') as temp:
            target = Path(temp)/'no git export'
            target.mkdir()
            for name in ('audit.py','physical.py','RESULT.json','SOURCES.json'):
                shutil.copyfile(HERE/name,target/name)
            before = fingerprint(target)
            env = os.environ.copy()
            env['PATH'] = ''
            command = [sys.executable,'-I','-O','-B',str(target/'audit.py')]
            run = subprocess.run(command,cwd=temp,env=env,capture_output=True,text=True,timeout=120)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertIn('PASS_PHASE_ORDER_BANK_AUDIT',run.stdout)
            self.assertEqual(before,fingerprint(target))
            self.assertEqual({x.name for x in target.iterdir()},set(before))

    def test_evidence_and_reference_corruption(self):
        with tempfile.TemporaryDirectory(prefix='phase-bank-corrupt-') as temp:
            target = Path(temp)
            for name in ('audit.py','physical.py','RESULT.json','SOURCES.json'):
                shutil.copyfile(HERE/name,target/name)
            original = (target/'RESULT.json').read_bytes()
            receipt = json.loads(original)
            receipt['symbolic']['permutations'] -= 1
            (target/'RESULT.json').write_text(json.dumps(receipt),encoding='utf-8')
            run = subprocess.run([sys.executable,'-I','-O','-B',str(target/'audit.py')],
                                 cwd=temp,capture_output=True,text=True,timeout=120)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('typed result receipt mismatch',run.stderr)
            (target/'RESULT.json').write_bytes(original)
            source = json.loads((target/'SOURCES.json').read_text())
            source['predecessor']['files'][0]['sha256'] = '0'*64
            (target/'SOURCES.json').write_text(json.dumps(source),encoding='utf-8')
            run = subprocess.run([sys.executable,'-I','-O','-B',str(target/'audit.py')],
                                 cwd=temp,capture_output=True,text=True,timeout=120)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('predecessor reference pin drift',run.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
