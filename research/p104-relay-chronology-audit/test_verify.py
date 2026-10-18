"""Behavioral export/provenance checks, plus independent scientific faults."""
from pathlib import Path
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Controls(unittest.TestCase):
    def test_independent_rejects_actual_endpoint_fault(self):
        a=load('audit_test',HERE/'audit.py')
        independent=load('independent_test',HERE/'independent.py')
        base,fixture,word=a.load()
        altered=copy.deepcopy(word)
        changed=next(op for op in altered['ops'] if op[0]=='read')
        changed[3]=str(-a.Q(changed[3]))
        with self.assertRaisesRegex(ValueError,'adjoint endpoint'):
            independent.check(base,altered)
        # Equivalent binary bases must be accepted, not confused with source
        # bytes: this is a semantic positive on the already authenticated input.
        equivalent=copy.deepcopy(word)
        for op in equivalent['ops']:
            if op[0]=='move':op[2]=list(reversed(op[2]))
        self.assertEqual(a.replay(base,equivalent,a.correction(fixture)),
                         a.replay(base,word,a.correction(fixture)))

    def test_git_free_export_and_boundaries(self):
        with tempfile.TemporaryDirectory(prefix='p104-relay-audit-') as directory:
            root=Path(directory);package=root/'research'/HERE.name
            shutil.copytree(HERE,package)
            for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
                if row['usage']=='input':
                    target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(ROOT/row['path'],target)
            cmd=[sys.executable,'-I','-O','-B',str(package/'verify.py')]
            def run():return subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=90)
            hashes={str(f.relative_to(root)):f.read_bytes() for f in root.rglob('*') if f.is_file()}
            positive=run()
            self.assertEqual(positive.returncode,0,positive.stderr)
            self.assertFalse((root/'.git').exists())
            self.assertEqual(hashes,{str(f.relative_to(root)):f.read_bytes() for f in root.rglob('*') if f.is_file()})
            executable=package/'inputs/check_p104_relay_construction.py'
            old=executable.read_bytes()
            executable.write_bytes(b'raise RuntimeError("EXECUTED_UNTRUSTED_PREDECESSOR")\n'+old)
            failed=run()
            self.assertNotEqual(failed.returncode,0)
            self.assertIn('retained source drift',failed.stderr)
            self.assertNotIn('EXECUTED_UNTRUSTED_PREDECESSOR',failed.stderr)
            executable.write_bytes(old)
            receipt=package/'RESULT.json';old_receipt=receipt.read_bytes()
            changed=json.loads(old_receipt);changed['endpoint_coefficients']=float(changed['endpoint_coefficients'])
            receipt.write_text(json.dumps(changed),encoding='utf-8')
            failed=run();self.assertNotEqual(failed.returncode,0);self.assertIn('typed receipt mismatch',failed.stderr)
            receipt.write_bytes(old_receipt)
            witness=package/'LINE-WITNESS.json';old_witness=witness.read_bytes()
            rows=json.loads(old_witness);rows.pop()
            witness.write_text(json.dumps(rows),encoding='utf-8')
            failed=run();self.assertNotEqual(failed.returncode,0);self.assertIn('complete line witness',failed.stderr)
            witness.write_bytes(old_witness)
            (package/'inputs/WORD-v2.json').unlink()
            self.assertNotEqual(run().returncode,0)

    def test_exclusive_output(self):
        with tempfile.TemporaryDirectory(prefix='p104-relay-output-') as directory:
            occupied=Path(directory)/'result.json';occupied.write_bytes(b'preserve')
            out=subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'verify.py'),'--out',str(occupied)],
                               capture_output=True,text=True,timeout=30)
            self.assertNotEqual(out.returncode,0)
            self.assertIn('output already exists',out.stderr)
            self.assertEqual(occupied.read_bytes(),b'preserve')


if __name__=='__main__':unittest.main(verbosity=2)
