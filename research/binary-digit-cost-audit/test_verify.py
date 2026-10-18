"""Failure-sensitive scientific export checks; standard library only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


def digests(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class Export(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='digit-audit-export-')
        self.root=Path(self.temp.name)/'package'
        shutil.copytree(HERE,self.root)

    def tearDown(self):
        self.temp.cleanup()

    def run_export(self,*args):
        return subprocess.run([sys.executable,'-I','-B','-O',str(self.root/'verify.py'),*args],
                              cwd=self.root.parent,text=True,encoding='utf-8',capture_output=True,timeout=60)

    def test_readonly_git_free_export(self):
        before=digests(self.root)
        result=self.run_export()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS_BINARY_DIGIT_COST_AUDIT',result.stdout)
        self.assertEqual(before,digests(self.root))

    def test_source_rejected_before_execution(self):
        path=self.root/'vendor/pr2501/bitstream.py'
        path.write_bytes(b'raise RuntimeError("UNAUTHENTICATED_EXECUTION")\n'+path.read_bytes())
        result=self.run_export()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('source SHA256',result.stderr)
        self.assertNotIn('UNAUTHENTICATED_EXECUTION',result.stderr)

    def test_semantic_and_type_receipt_corruption(self):
        path=self.root/'RESULT.json'
        original=json.loads(path.read_text())
        for field in ('count','type'):
            changed=json.loads(json.dumps(original))
            if field=='count':
                changed['digit_cases'][0]['meter'][2]+=1
            else:
                changed['preparation']['cardinality_cases'][0]['bits']=True
            path.write_text(json.dumps(changed),encoding='utf-8')
            result=self.run_export()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('complete typed committed receipt mismatch',result.stderr)

    def test_missing_duplicate_and_overwrite(self):
        path=self.root/'RESULT.json'
        result=self.run_export('--write')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('refusing to overwrite',result.stderr)
        path.write_text('{"status":1,"status":2}',encoding='utf-8')
        result=self.run_export()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('duplicate JSON key',result.stderr)
        path.unlink()
        result=self.run_export()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('FileNotFoundError',result.stderr)


if __name__=='__main__':
    unittest.main()
