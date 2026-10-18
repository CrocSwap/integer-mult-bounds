"""Public CLI checks in a minimal Git-free export."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dihedral-couplings-")
        self.root = Path(self.tmp.name)
        self.package = self.root / HERE.relative_to(ROOT)
        shutil.copytree(HERE, self.package)
        for item in json.loads((HERE/"SOURCES.json").read_bytes())["files"]:
            if item["usage"] == "input":
                dest = self.root/item["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/item["path"], dest)
        self.addCleanup(self.tmp.cleanup)

    def call(self):
        return subprocess.run([sys.executable,"-I","-O","-B",str(self.package/"verify.py")],
                              cwd=self.root, capture_output=True, text=True, timeout=60)

    def inventory(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_read_only_export(self):
        before=self.inventory()
        result=self.call()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS_DIHEDRAL_ARBITRARY_COUPLINGS",result.stdout)
        self.assertEqual(self.inventory(),before)

    def test_source_corruption(self):
        source=self.root/"research/infinite-dihedral-register-bound/README.md"
        source.write_bytes(source.read_bytes()+b"\nchanged\n")
        result=self.call()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("source SHA mismatch",result.stderr)

    def test_typed_receipt(self):
        path=self.package/"RESULT.json"
        original=json.loads(path.read_bytes())
        for value in (True,float(original["binary_matrices"])):
            altered=dict(original,binary_matrices=value)
            path.write_text(json.dumps(altered),encoding="utf-8")
            result=self.call()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("receipt mismatch",result.stderr)

    def test_material_implementation_mutations(self):
        path=self.package/"verify.py"
        original=path.read_text(encoding="utf-8")
        for old,new in [
            ('("xor", 0, 1), ("g", 1, 0), ("xor", 0, 1), ("g", 1, 0)]',
             '("xor", 0, 1), ("g", 1, 0), ("xor", 0, 1)]'),
            ('best = max(best, value.bit_length()-1-k)',
             'best = max(best, value.bit_length()-1)')]:
            self.assertIn(old,original)
            path.write_text(original.replace(old,new,1),encoding="utf-8")
            result=self.call()
            self.assertNotEqual(result.returncode,0)

if __name__=="__main__":
    unittest.main()
