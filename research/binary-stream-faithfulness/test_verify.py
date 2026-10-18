"""Export and source/receipt failures for the independent replay boundary."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root/'research/binary-stream-faithfulness'
        shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        self.sources = json.loads((HERE/'SOURCES.json').read_text())
        for row in self.sources['files']:
            if row['usage'] == 'input':
                destination = self.root/row['path']
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],destination)

    def run_check(self,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*args],
                              cwd=self.root,text=True,capture_output=True,timeout=60)

    def test_git_free_read_only(self):
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=self.run_check()
        self.assertEqual(result.returncode,0,result.stderr)
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_source_drift_and_absence(self):
        for row in self.sources['files']:
            if row['usage'] != 'input':
                continue
            path=self.root/row['path']
            original=path.read_bytes()
            path.write_bytes(original+b' changed')
            result=self.run_check()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source binding',result.stderr)
            path.unlink()
            self.assertNotEqual(self.run_check().returncode,0)
            path.write_bytes(original)

    def test_typed_receipt_and_missing(self):
        path=self.package/'RESULT.json'
        result=json.loads(path.read_text())
        result['legal_word']['affine_same_translation_control']=1
        path.write_text(json.dumps(result))
        rejected=self.run_check()
        self.assertNotEqual(rejected.returncode,0)
        self.assertIn('typed exact receipt',rejected.stderr)
        path.unlink()
        self.assertNotEqual(self.run_check().returncode,0)

    def test_regenerate_is_exclusive(self):
        output=self.root/'new.json'
        first=self.run_check('--write-result',str(output))
        self.assertEqual(first.returncode,0,first.stderr)
        self.assertEqual(json.loads(output.read_text()),json.loads((HERE/'RESULT.json').read_text()))
        before=output.read_bytes()
        self.assertNotEqual(self.run_check('--write-result',str(output)).returncode,0)
        self.assertEqual(output.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
