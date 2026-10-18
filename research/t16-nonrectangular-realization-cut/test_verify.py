"""Behavioral source-export and source-schema CLI checks."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

P=Path(__file__).resolve().parent
R=P.parents[1]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='nr-')
        self.root=Path(self.temp.name)
        self.package=self.root/'research'/P.name
        shutil.copytree(P,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        manifest=json.loads((P/'SOURCES.json').read_bytes())
        for row in manifest['files']:
            if row.get('usage')=='input':
                target=self.root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(R/row['path'],target)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self,args,ok,text):
        p=subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*map(str,args)],cwd=self.root,capture_output=True,text=True,timeout=45)
        self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr)
        self.assertIn(text,p.stdout+p.stderr)
        return p

    def fixture(self,positive=False):
        ns=runpy.run_path(str(self.package/'verify.py'))
        old,_,_=ns['sources']();classes,_=old.geometry()
        ps=[Counter({(0,)*5:len(c['bins'])}) for c in classes]
        fs=[{t:[0]*5 for t in c['calls']} for c in classes]
        patterns,bad,good=ns['witness'](classes)
        ps[9],fs[9]=patterns,good if positive else bad
        path=self.root/'candidate.json'
        path.write_text(json.dumps(old.export_stage1(ps,fs)),encoding='utf-8')
        return path

    def test_git_free_read_only(self):
        snapshot=lambda:{str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        before=snapshot()
        self.invoke([],True,'PASS_T16_NONRECTANGULAR_CUT')
        self.assertEqual(before,snapshot())
        self.assertFalse((self.root/'.git').exists())

    def test_retained_executable_before_execution(self):
        path=self.package/'source/pr2535/cuts.py'
        path.write_bytes(b"raise RuntimeError('MUST_NOT_EXECUTE')\n"+path.read_bytes())
        self.invoke([],False,'source SHA256')

    def test_main_input_tampering(self):
        path=self.root/'research/complex-t16-rare-pattern-exchanges/data/PLAN.json'
        path.write_bytes(path.read_bytes()+b'\n')
        self.invoke([],False,'source SHA256')

    def test_typed_receipt_and_missing_evidence(self):
        path=self.package/'RESULT.json'
        result=json.loads(path.read_bytes())
        result['realization_census']['bad_realizations']=False
        path.write_text(json.dumps(result),encoding='utf-8')
        self.invoke([],False,'complete typed RESULT equality')
        path.unlink()
        self.invoke([],False,'FileNotFoundError')

    def test_actual_stage1_cli_and_positive(self):
        path=self.fixture()
        out=self.root/'cut.json'
        args=['--stage1',path,'--class-index','9','--cells',self.package/'CELLS.json','--output',out]
        self.invoke(args,True,'deficit=1')
        result=json.loads(out.read_bytes())
        self.assertEqual((result['lhs'],result['rhs'],len(result['pattern_coefficients'])),(5,4,27))
        self.assertIn([4,0,0,0,0],[r['pattern'] for r in result['pattern_coefficients']])
        before=out.read_bytes()
        self.invoke(args,False,'FileExistsError')
        self.assertEqual(before,out.read_bytes())
        self.fixture(positive=True)
        args[-1]=self.root/'positive.json'
        self.invoke(args,True,'deficit=0')
        good=json.loads(args[-1].read_bytes())
        self.assertEqual((good['lhs'],good['rhs'],good['violated']),(4,4,False))

    def test_cli_rejects_bad_cell_without_output(self):
        candidate=self.fixture()
        cells=self.root/'bad-cells.json';cells.write_text('[[1,5],[1,5]]')
        out=self.root/'must-not-exist.json'
        self.invoke(['--stage1',candidate,'--class-index','9','--cells',cells,'--output',out],False,'duplicate cell')
        self.assertFalse(out.exists())


if __name__=='__main__':
    unittest.main()
