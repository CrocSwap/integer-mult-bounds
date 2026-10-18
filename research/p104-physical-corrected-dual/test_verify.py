"""Export and corruption controls for this finite physical certificate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest

P=Path(__file__).resolve().parent
ROOT=P.parents[1]

class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='p104-physical-export-')
        cls.root=Path(cls.tmp.name)
        cls.pkg=cls.root/'research'/P.name
        shutil.copytree(P,cls.pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for r in json.loads((P/'SOURCES.json').read_text())['files']:
            if r['usage']=='input':
                dst=cls.root/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],dst)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def run_verify(self,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.pkg/'verify.py'),*args],cwd=self.root,capture_output=True,text=True,timeout=280)
    def test_export_read_only(self):
        before={str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        result=self.run_verify();self.assertEqual(result.returncode,0,result.stderr)
        after={str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_executable_pin_precedes_execution(self):
        path=self.root/'research/p104-native-channel/vendor/native_verify.py';raw=path.read_bytes()
        marker=self.root/'EXECUTED'
        try:
            path.write_text("from pathlib import Path\nPath('EXECUTED').write_text('bad')\n",encoding='utf-8')
            result=self.run_verify();self.assertNotEqual(result.returncode,0);self.assertIn('source SHA256',result.stderr);self.assertFalse(marker.exists())
        finally:path.write_bytes(raw)
    def test_retained_source_pin(self):
        path=self.pkg/'inputs/CLEAN-DUAL.json';raw=path.read_bytes()
        try:
            path.write_bytes(raw+b' ');result=self.run_verify();self.assertNotEqual(result.returncode,0);self.assertIn('predecessor SHA256',result.stderr)
        finally:path.write_bytes(raw)
    def test_whole_receipt(self):
        path=self.pkg/'RESULT.json';raw=path.read_bytes()
        try:
            for field in ('witness','type'):
                x=json.loads(raw)
                if field=='witness':x['boundary']['physical_witness_X0_at_Y2_delta0']=['0','0']
                else:x['no_new_kappa']=1
                path.write_text(json.dumps(x),encoding='utf-8')
                result=self.run_verify();self.assertNotEqual(result.returncode,0);self.assertIn('complete typed receipt equality',result.stderr)
        finally:path.write_bytes(raw)
    def test_existing_output_refused(self):
        p=self.pkg/'RESULT.json';raw=p.read_bytes();result=self.run_verify('--out',str(p))
        self.assertNotEqual(result.returncode,0);self.assertIn('exclusive new receipt output',result.stderr);self.assertEqual(raw,p.read_bytes())
    def test_native_evidence_required(self):
        p=self.pkg/'NATIVE.json.gz';raw=p.read_bytes()
        try:
            p.unlink();result=self.run_verify();self.assertNotEqual(result.returncode,0);self.assertIn('NATIVE.json.gz',result.stderr)
        finally:p.write_bytes(raw)

if __name__=='__main__':unittest.main()
