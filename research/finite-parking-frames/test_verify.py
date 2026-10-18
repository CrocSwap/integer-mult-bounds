"""Package boundary tests; stdlib only, Apache-2.0; ywz65 with Codex."""
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

def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

class Boundaries(unittest.TestCase):
    def test_git_free_read_only_and_faults(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'export'
            shutil.copytree(HERE,out,ignore=shutil.ignore_patterns('__pycache__'))
            def run():
                return subprocess.run([sys.executable,'-I','-O','-B',str(out/'verify.py')],
                                      cwd=tmp,capture_output=True,text=True,timeout=120)
            before=hashes(out);r=run()
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual(before,hashes(out))
            cases = [
                ('inputs/frame.py',lambda raw:raw+b'\nraise RuntimeError("PREDECESSOR_EXECUTED")\n'),
                ('TABLE.json',lambda raw:json.dumps(json.loads(raw)[:-1]).encode()),
                ('RESULT.json',lambda raw:raw.replace(b'"exhaustive_packets": 2047',b'"exhaustive_packets": 2047.0')),
                ('SNAPSHOTS.json',lambda raw:json.dumps({'files':json.loads(raw)['files'][:-1]}).encode()),
            ]
            for name,mutate in cases:
                path=out/name;raw=path.read_bytes();changed=mutate(raw)
                self.assertNotEqual(raw,changed)
                path.write_bytes(changed);r=run()
                self.assertNotEqual(r.returncode,0,name)
                self.assertNotIn('RuntimeError: PREDECESSOR_EXECUTED',r.stderr)
                path.write_bytes(raw)
            raw=(out/'TABLE.json').read_bytes();(out/'TABLE.json').unlink();r=run()
            self.assertNotEqual(r.returncode,0)
            (out/'TABLE.json').write_bytes(raw)
            self.assertEqual(before,hashes(out))

    def test_output_is_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'existing.json';target.write_bytes(b'keep')
            r=subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'verify.py'),'--out',str(target)],
                             capture_output=True,text=True,timeout=10)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('output must be new',r.stderr)
            self.assertEqual(target.read_bytes(),b'keep')

if __name__ == '__main__':
    unittest.main(verbosity=2)
