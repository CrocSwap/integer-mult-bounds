# SPDX-License-Identifier: Apache-2.0
"""Mathematical oracle, actual corruption and relocated CLI rejection tests."""
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V
import dense as D


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Prefer a sibling of the repo (historical layout); fall back to /tmp when
        # that parent is not writable (common in containerized checkouts).
        preferred = V.ROOT.parent / 'contribution1319-test-temp'
        try:
            preferred.mkdir(exist_ok=True)
            cls.scratch = preferred
        except OSError:
            cls.scratch = Path(tempfile.gettempdir()) / 'contribution1319-test-temp'
            cls.scratch.mkdir(exist_ok=True)

    def export(self, directory):
        root = Path(directory) / 'export'
        package = root / 'research' / V.PKG.name
        package.mkdir(parents=True)
        for name in ('verify.py','dense.py','SOURCES.json','CERTIFICATE.json','DENSE.json'):
            shutil.copy2(V.PKG / name, package / name)
        # Live inventory pins plus the demoted runtime oracle used by dense.py.
        for name in sorted(V.INPUTS | {V.KERNEL}):
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(V.ROOT / name, dest)
        self.assertTrue(root.resolve().is_relative_to(self.scratch.resolve()))
        return root, package

    def run_cli(self, root, script, *args, optimized=False):
        argv = [sys.executable,'-I','-B'] + (['-O'] if optimized else [])
        argv += [str(root / 'research' / V.PKG.name / script), *args]
        return subprocess.run(argv,cwd=root,capture_output=True,text=True,timeout=45)

    def test_fourier_multiplicities_against_gaussian_elimination(self):
        for f in range(1,4):
            for sign in (-1,1):
                self.assertEqual(D.eigenspace_counts(D.tensor(f,sign)), V.spectrum(f,sign))
        # The rank-defect bound is tested on two different diagonalizable maps,
        # without assuming they have a common eigenbasis.
        a = D.blocks([D.tensor(1),D.tensor(1)])
        b = D.tensor(2)
        self.assertGreaterEqual(D.rank(D.difference(a,b)),V.correction_floor(V.target(1,2),V.child(2,1)))

    def test_mixed_encoding_and_phase_mutations(self):
        row = V.read_json(V.PKG / 'DENSE.json')['mixed_full_space_witnesses'][0]
        e = [[(Q(x),Q(y)) for x,y in line] for line in row['encoding']]
        inverse = [[(Q(x),Q(y)) for x,y in line] for line in row['inverse_encoding']]
        a = D.scale(D.tensor(2), D.ROOTS[3])
        target = D.blocks([D.tensor(1),D.tensor(1,-1)])
        self.assertEqual(D.mm(D.mm(inverse,a),e),target)
        self.assertNotEqual(D.mm(D.mm(inverse,D.tensor(2)),e),target)
        e[0][0] = D.add(e[0][0],D.ONE)
        self.assertNotEqual(D.mm(inverse,e),D.eye(4))
        self.assertNotEqual(D.mm(a,e),D.mm(e,target))

    def test_invalid_integer_domains_and_duplicate_json(self):
        for f in (True,0,-1,1.0):
            with self.assertRaises(ValueError):
                V.spectrum(f)
        for q,d in ((True,0),(0,0),(1,-1),(1,True)):
            with self.assertRaises(ValueError):
                V.target(1,q,d)
        with self.assertRaises(ValueError):
            V.correction_floor([2,0,0,0],[1,0,0,0])
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}',object_pairs_hook=V.unique_object)

    def test_source_and_inventory_corruption_reject_both_engines(self):
        live = sorted(V.INPUTS)[0]
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            root, package = self.export(directory)
            source = root / live
            original = source.read_bytes()
            source.write_bytes(original+b'\n# source drift\n')
            for script in ('verify.py','dense.py'):
                result = self.run_cli(root,script,optimized=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('source SHA256 mismatch',result.stdout+result.stderr)
            source.write_bytes(original)
            manifest = V.read_json(package / 'SOURCES.json')
            manifest['files'] = [r for r in manifest['files'] if r['path'] != live]
            (package / 'SOURCES.json').write_text(json.dumps(manifest),encoding='utf-8')
            for script in ('verify.py','dense.py'):
                result = self.run_cli(root,script)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('input inventory',result.stdout+result.stderr)

    def test_receipt_corruption_and_json_types_reject(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            root, package = self.export(directory)
            path = package / 'CERTIFICATE.json'
            original = path.read_bytes()
            for value in (False,28033):
                cert = json.loads(original)
                cert['uniform']['cases'] = value
                path.write_text(json.dumps(cert),encoding='utf-8')
                result = self.run_cli(root,'verify.py',optimized=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('certificate mismatch',result.stdout+result.stderr)
            path.write_bytes(original)
            dense_path = package / 'DENSE.json'
            cert = V.read_json(dense_path)
            cert['mixed_full_space_witnesses'][0]['inverse_encoding'][0][0][0] = '1'
            dense_path.write_text(json.dumps(cert),encoding='utf-8')
            result = self.run_cli(root,'dense.py',optimized=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('dense certificate mismatch',result.stdout+result.stderr)

    def test_optimized_read_only_export_and_deterministic_regeneration(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as directory:
            root, package = self.export(directory)
            before = {p.name:p.read_bytes() for p in package.iterdir()}
            self.assertFalse((root / '.git').exists())
            for script in ('verify.py','dense.py'):
                result = self.run_cli(root,script,optimized=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(before,{p.name:p.read_bytes() for p in package.iterdir()})
            for script in ('verify.py','dense.py'):
                result = self.run_cli(root,script,'--write')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(before,{p.name:p.read_bytes() for p in package.iterdir()})


if __name__ == '__main__':
    unittest.main()
