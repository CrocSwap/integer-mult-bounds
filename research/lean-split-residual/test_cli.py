"""Read-only minimal-export checks for the public finite verifier."""
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parent.parent

class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="split-residual-export-")
        self.root=Path(self.tmp.name);self.package=self.root/P.relative_to(R)
        shutil.copytree(P,self.package)
        for item in json.loads((P/"SOURCES.json").read_bytes())["files"]:
            if item["usage"]=="input":
                dest=self.root/item["path"];dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(R/item["path"],dest)
        self.addCleanup(self.tmp.cleanup)
    def call(self):
        return subprocess.run([sys.executable,"-I","-O","-B",str(self.package/"verify.py")],
                              cwd=self.root,text=True,capture_output=True,timeout=60)
    def inventory(self):
        return {str(x.relative_to(self.root)):hashlib.sha256(x.read_bytes()).hexdigest()
                for x in self.root.rglob("*") if x.is_file()}
    def test_readonly_export(self):
        before=self.inventory();result=self.call()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.inventory(),before)
        self.assertIn("PASS_SPLIT_RESIDUAL_CONTROLS",result.stdout)
    def test_changed_source(self):
        source=self.root/"research/selected-bit-local-ring-sweeps/PROOF.md"
        source.write_bytes(source.read_bytes()+b"\nchanged\n")
        result=self.call()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("source hash mismatch",result.stderr)
    def test_typed_receipt(self):
        path=self.package/"RESULT.json";original=json.loads(path.read_bytes())
        for bad in (True,float(original["ring_cases"])):
            path.write_text(json.dumps(dict(original,ring_cases=bad)),encoding="utf-8")
            result=self.call()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("receipt mismatch",result.stderr)
    def test_changed_formal_bytes(self):
        source=self.package/"SplitResidual.lean"
        source.write_bytes(source.read_bytes()+b"\n-- changed\n")
        result=self.call()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("receipt mismatch",result.stderr)

if __name__=="__main__":unittest.main()
