"""End-to-end export and evidence controls; only temporary copies mutate."""
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


class Integrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='surcharged-dyadic-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.package=self.root/'research'/HERE.name
        shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row.get('usage')!='input':continue
            target=self.root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],target)

    def run_copy(self,*args):
        env=os.environ.copy();env['PYTHONOPTIMIZE']='2'
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*args],
                              cwd=self.root,env=env,text=True,capture_output=True,timeout=120)

    def rejected(self,result,reason):
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertIn(reason,result.stderr)
        self.assertNotIn('PASS_SURCHARGED_DYADIC_COMPARATOR',result.stdout)

    def test_export_and_assertion_enabled_source_subprocess(self):
        self.assertFalse((self.root/'.git').exists())
        result=self.run_copy()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_SURCHARGED_DYADIC_COMPARATOR pairs 9669 controls 16',result.stdout)

    def test_vendored_source_rejects_before_execution(self):
        source=self.package/'vendor/pr1392/research/pr1048-certified-repair/pricing.py'
        source.write_bytes(source.read_bytes()+b'\nraise RuntimeError("MUST_NOT_EXECUTE")\n')
        result=self.run_copy();self.rejected(result,'source SHA256')
        self.assertNotIn('MUST_NOT_EXECUTE',result.stderr)

    def test_main_input_rejects_before_execution(self):
        source=self.root/'research/pr1048-algebraic-order/oracle.py'
        source.write_bytes(source.read_bytes()+b'\nraise RuntimeError("MUST_NOT_EXECUTE")\n')
        result=self.run_copy();self.rejected(result,'source SHA256')
        self.assertNotIn('MUST_NOT_EXECUTE',result.stderr)

    def test_forged_typed_receipt(self):
        path=self.package/'RESULT.json';data=json.loads(path.read_text())
        data['cases'][0]['certificate']['order']=False # False == 0 in Python.
        path.write_text(json.dumps(data),encoding='utf-8')
        self.rejected(self.run_copy(),'typed receipt mismatch')

    def test_missing_coverage(self):
        path=self.package/'RESULT.json';data=json.loads(path.read_text())
        data['small_census']['pairs']-=1
        path.write_text(json.dumps(data),encoding='utf-8')
        self.rejected(self.run_copy(),'typed receipt mismatch')

    def test_writer_refuses_existing_receipt(self):
        path=self.package/'RESULT.json';before=path.read_bytes()
        self.rejected(self.run_copy('--write'),'refuse to overwrite committed receipt')
        self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
